#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""whydump analyze.py 单元测试（unittest，零第三方依赖）。

运行：
  python -m unittest discover -s tests -p "test_*.py"
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

# 让测试能找到 analyze.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import analyze  # noqa: E402

LEAK_HISTO = """\
 num     #instances         #bytes  class name (module)
-------------------------------------------------------
   1:          1200       1258291200  [B
   2:          3000         24000000  com.example.User
   3:           800          4800000  java.lang.String
Total    :        5000       1287091200
"""

SMALL_HISTO = """\
 num     #instances         #bytes  class name (module)
-------------------------------------------------------
   1:          1500         12000000  [C
   2:          1200          9600000  java.lang.String
   3:           900          7200000  com.example.Task
Total    :        3600         28800000
"""

COMMA_HISTO = """\
     1:          1,200      1,258,291,200  [B
     2:          3,000         24,000,000  com.example.User
Total    :        4,200      1,282,291,200
"""

# 小类写在前面：jmap 默认按字节降序，但 jhsdb / 手工拼文件不保证顺序
UNSORTED_HISTO = """\
   1:          10          1000  java.lang.String
   2:        1200    1258291200  [B
"""

FLAGS_TEXT = """\
 -XX:CICompilerCount=2 {default}
 -XX:InitialHeapSize=268435456 {product}
 -XX:MaxHeapSize=1073741824 {product}
 -XX:MaxMetaspaceSize=2147483648 {product}
"""

# 真实 `jcmd <pid> VM.flags` 是**单行**输出，所有 flag 空格分隔（实测 JDK 17）
SINGLE_LINE_FLAGS = (
    " -XX:CICompilerCount=2 -XX:InitialHeapSize=268435456"
    " -XX:MaxHeapSize=1073741824 -XX:MaxMetaspaceSize=2147483648 \n"
)

# 模拟 `jmap -histo:live | head` 截断：行合计 1000，Total 行却是 1000000
TRUNCATED_HISTO = """\
   1:           6            600  [B
   2:           4            400  java.lang.String
Total         10000         1000000
"""


class TestParseHisto(unittest.TestCase):
    def test_parses_standard_rows(self):
        entries = analyze.parse_histo(LEAK_HISTO)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].name, "[B")
        self.assertEqual(entries[0].instances, 1200)
        self.assertEqual(entries[0].bytes, 1258291200)

    def test_strips_module_suffix(self):
        rows = "   1:   1   4  com.example.MyClass (mymodule)\n"
        entries = analyze.parse_histo(rows)
        self.assertEqual(entries[0].name, "com.example.MyClass")

    def test_handles_thousand_separators(self):
        entries = analyze.parse_histo(COMMA_HISTO)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].instances, 1200)
        self.assertEqual(entries[0].bytes, 1258291200)

    def test_ignores_unparseable_lines(self):
        text = "header\n  not-a-row\nTotal : 0 0\n   1:  1  8  Foo\n"
        entries = analyze.parse_histo(text)
        self.assertEqual(len(entries), 1)

    def test_empty_input_gives_empty_list(self):
        self.assertEqual(analyze.parse_histo(""), [])


class TestParseFlags(unittest.TestCase):
    def test_extracts_heap_flags(self):
        flags = analyze.parse_flags(FLAGS_TEXT)
        self.assertEqual(flags["InitialHeapSize"], 268435456)
        self.assertEqual(flags["MaxHeapSize"], 1073741824)
        self.assertEqual(flags["MaxMetaspaceSize"], 2147483648)

    def test_parses_single_line_jcmd_output(self):
        # 回归：真实 jcmd 输出是单行，逐行 search 只会拿到第一个 flag
        flags = analyze.parse_flags(SINGLE_LINE_FLAGS)
        self.assertEqual(flags["InitialHeapSize"], 268435456)
        self.assertEqual(flags["MaxHeapSize"], 1073741824)
        self.assertEqual(flags["MaxMetaspaceSize"], 2147483648)

    def test_ignores_non_heap_flags(self):
        flags = analyze.parse_flags("-XX:CICompilerCount=2 {default}\n")
        self.assertEqual(flags, {})


class TestParseTotal(unittest.TestCase):
    def test_parses_total_with_colon(self):
        self.assertEqual(analyze.parse_total(LEAK_HISTO), 1287091200)

    def test_parses_total_without_colon(self):
        self.assertEqual(analyze.parse_total(TRUNCATED_HISTO), 1000000)

    def test_returns_none_when_absent(self):
        self.assertIsNone(analyze.parse_total(UNSORTED_HISTO))


class TestClassify(unittest.TestCase):
    def test_leak_suspect_when_dominant(self):
        diag = analyze.classify(analyze.parse_histo(LEAK_HISTO), 0.5)
        self.assertEqual(diag["category"], "leak-suspect")
        self.assertEqual(diag["max_class"], "[B")
        self.assertGreater(diag["max_ratio"], 0.9)

    def test_no_dominant_when_spread(self):
        diag = analyze.classify(analyze.parse_histo(SMALL_HISTO), 0.5)
        self.assertEqual(diag["category"], "no-dominant-class")

    def test_threshold_respects_argument(self):
        # 最大类 31.2%，阈值 0.3 时应判泄漏，0.5 时应判堆小
        entries = analyze.parse_histo(SMALL_HISTO)
        self.assertEqual(analyze.classify(entries, 0.3)["category"], "leak-suspect")
        self.assertEqual(analyze.classify(entries, 0.5)["category"], "no-dominant-class")

    def test_no_data_on_empty(self):
        diag = analyze.classify([], 0.5)
        self.assertEqual(diag["category"], "no-data")
        self.assertEqual(diag["top3_ratio"], 0.0)

    def test_top3_ratio_sums_top_three(self):
        # 6 个等大类：top3_ratio 应为 3/6=0.5，且不改 category 判定
        rows = "".join(f"  {i}:  1  100  C{i}\n" for i in range(1, 7))
        entries = analyze.parse_histo(rows)
        diag = analyze.classify(entries, 0.5)
        self.assertEqual(diag["category"], "no-dominant-class")
        self.assertAlmostEqual(diag["max_ratio"], 1 / 6)
        self.assertAlmostEqual(diag["top3_ratio"], 0.5)

    def test_uses_largest_class_not_first_row(self):
        entries = analyze.parse_histo(UNSORTED_HISTO)
        self.assertEqual(entries[0].name, "java.lang.String")
        diag = analyze.classify(entries, 0.5)
        self.assertEqual(diag["category"], "leak-suspect")
        self.assertEqual(diag["max_class"], "[B")
        self.assertGreater(diag["max_ratio"], 0.9)


class TestCli(unittest.TestCase):
    """跑真实 CLI（含 stdin / json / 退出码）端到端验证。"""

    def _run(self, args, stdin=None):
        return subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "..", "scripts", "analyze.py")]
            + args,
            input=stdin, capture_output=True, text=True,
        )

    def test_stdin_json(self):
        r = self._run(["-", "--json"], stdin=COMMA_HISTO)
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertEqual(d["category"], "leak-suspect")
        self.assertEqual(d["max_class"], "[B")
        self.assertIn("top3_ratio", d)

    def test_bad_input_returns_1(self):
        r = self._run(["nonexistent-file.txt"])
        self.assertEqual(r.returncode, 1)

    def test_unparseable_input_returns_1(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("not a histo\n")
            path = f.name
        try:
            r = self._run([path])
            self.assertEqual(r.returncode, 1)
            self.assertIn("whydump", r.stderr)
        finally:
            os.unlink(path)

    def test_truncated_histo_flagged(self):
        # 行合计只占 Total 的 0.1% → 必须标记 truncated，两种输出模式都告警
        r = self._run(["-", "--json"], stdin=TRUNCATED_HISTO)
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertTrue(d["truncated"])
        self.assertLess(d["parsed_ratio"], 0.95)
        r2 = self._run(["-"], stdin=TRUNCATED_HISTO)
        self.assertIn("截断", r2.stdout)

    def test_complete_histo_not_flagged(self):
        r = self._run(["-", "--json"], stdin=COMMA_HISTO)
        d = json.loads(r.stdout)
        self.assertFalse(d["truncated"])
        self.assertAlmostEqual(d["parsed_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
