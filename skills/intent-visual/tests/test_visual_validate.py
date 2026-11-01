#!/usr/bin/env python3
"""visual_validate.py 结构校验测试。

Run:
  python -m pytest skills/intent-visual/tests/test_visual_validate.py -v
  python skills/intent-visual/tests/test_visual_validate.py
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
try:
    from visual_validate import validate
finally:
    sys.path.pop(0)

BASELINE_HTML = (FIXTURES_DIR / "valid-visual-baseline.html").read_text(encoding="utf-8")

VALID_DESIGN = (FIXTURES_DIR / "valid-visual-design.md").read_text(encoding="utf-8")


def _make_chain_dir() -> Path:
    root = Path(tempfile.mkdtemp())
    chain = root / "intent-chain" / "2026-08-31-001-测试链路"
    chain.mkdir(parents=True)
    return chain


def _write_valid(chain: Path) -> None:
    (chain / "visual-design.md").write_text(VALID_DESIGN, encoding="utf-8")
    (chain / "visual-baseline.html").write_text(BASELINE_HTML, encoding="utf-8")


def _validate(design_text: str, baseline_text: str | None, baseline_exists: bool):
    return validate(design_text, baseline_text, baseline_exists)


class TestVisualValidate(unittest.TestCase):
    def test_valid_design_all_pass(self):
        results = _validate(VALID_DESIGN, BASELINE_HTML, True)
        failures = [r for r in results if r[1] == "FAIL"]
        self.assertEqual([], failures, f"合法样例不应有 FAIL: {failures}")

    def test_missing_baseline_fails_v10(self):
        results = _validate(VALID_DESIGN, None, False)
        v10 = [r for r in results if r[0] == "V10"][0]
        self.assertEqual("FAIL", v10[1])

    def test_baseline_without_style_fails_v10(self):
        results = _validate(VALID_DESIGN, "<html><body>空</body></html>", True)
        v10 = [r for r in results if r[0] == "V10"][0]
        self.assertEqual("FAIL", v10[1])

    def test_missing_section_fails_v2(self):
        broken = VALID_DESIGN.replace("## 2. 色板", "## 2X. 色板")
        results = _validate(broken, BASELINE_HTML, True)
        v2 = [r for r in results if r[0] == "V2"][0]
        self.assertEqual("FAIL", v2[1])
        self.assertIn("色板", v2[2])

    def test_bad_hex_fails_v4(self):
        broken = VALID_DESIGN.replace("| 主文字 | #171717 | 近黑 |", "| 主文字 | 纯黑 | 近黑 |")
        results = _validate(broken, BASELINE_HTML, True)
        v4 = [r for r in results if r[0] == "V4"][0]
        self.assertEqual("FAIL", v4[1])

    def test_font_without_fallback_fails_v5(self):
        broken = VALID_DESIGN.replace(
            "| 大标题 | ui-sans-serif, system-ui, sans-serif | 48px/56px | 500 |",
            "| 大标题 | Söhne | 48px/56px | 500 |",
        )
        results = _validate(broken, BASELINE_HTML, True)
        v5 = [r for r in results if r[0] == "V5"][0]
        self.assertEqual("FAIL", v5[1])
        self.assertIn("fallback", v5[2])

    def test_empty_avoid_list_fails_v7(self):
        broken = VALID_DESIGN.replace("- 不用大面积彩色底色", "- 无").replace(
            "- 不用投影卡片，用 1px 边框代替\n", ""
        )
        results = _validate(broken, BASELINE_HTML, True)
        v7 = [r for r in results if r[0] == "V7"][0]
        self.assertEqual("FAIL", v7[1])

    def test_missing_source_date_fails_v8(self):
        broken = VALID_DESIGN.replace("参考，2026-08-31，", "参考，")
        results = _validate(broken, BASELINE_HTML, True)
        v8 = [r for r in results if r[0] == "V8"][0]
        self.assertEqual("FAIL", v8[1])
        self.assertIn("日期", v8[2])

    def test_placeholder_residue_fails_v9(self):
        broken = VALID_DESIGN.replace("黑白编辑感的个人技术博客", "黑白编辑感的{产品名称}")
        results = _validate(broken, BASELINE_HTML, True)
        v9 = [r for r in results if r[0] == "V9"][0]
        self.assertEqual("FAIL", v9[1])

    def test_empty_file_only_v1_fail(self):
        results = _validate("", None, False)
        self.assertEqual(1, len(results))
        self.assertEqual(("V1", "FAIL"), (results[0][0], results[0][1]))

    def test_main_end_to_end_exit_0(self):
        chain = _make_chain_dir()
        _write_valid(chain)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from visual_validate import main
            old_argv = sys.argv
            sys.argv = ["visual_validate.py", str(chain / "visual-design.md")]
            try:
                code = main()
            finally:
                sys.argv = old_argv
        self.assertEqual(0, code)
        self.assertIn("结论: 视觉规范结构完整", buf.getvalue())

    def test_main_end_to_end_missing_baseline_exit_1(self):
        chain = _make_chain_dir()
        (chain / "visual-design.md").write_text(VALID_DESIGN, encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from visual_validate import main
            old_argv = sys.argv
            sys.argv = ["visual_validate.py", str(chain / "visual-design.md")]
            try:
                code = main()
            finally:
                sys.argv = old_argv
        self.assertEqual(1, code)
        self.assertIn("V10", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
