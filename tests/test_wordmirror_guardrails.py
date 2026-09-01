# -*- coding: utf-8 -*-
"""wordmirror 护栏回归测试。

这个 skill 的护栏集中在：写操作只走命令（记账 promise / 写回 wb，保证格式对、坏行拦得住）、
数据定位（bind / 祖先逐级）、按意思搜没建索引时安静返回空、文案说人话不堆术语不抖机灵。
本文件锁住这些，防止后续迭代把它们改丢。

跑法：cd tests && python -m unittest test_wordmirror_guardrails -v
（纯临时目录夹具，不碰真实数据目录）
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "wordmirror"
SCRIPTS = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ds  # noqa: E402


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


class _TempBase(unittest.TestCase):
    """临时"完整仓库"夹具：data/ 带语料签名，环境变量指过去。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.data = self.repo / "data"
        self.data.mkdir(parents=True)
        _write_jsonl(self.data / "corpus_dedup.jsonl",
                     [{"agent": "zcode", "date": "2026-08-01", "proj": "demo",
                       "sid": "s1", "msg": "我说过要把 demo 收尾"}])
        self._old_env = {k: os.environ.get(k)
                         for k in ("WORD_MIRROR_HOME", "DIGITAL_SELF_HOME")}
        os.environ["WORD_MIRROR_HOME"] = str(self.repo)
        self._reload_ds()

    def _reload_ds(self):
        """ds 模块在 import 时定位数据目录，改环境后必须重载。"""
        import importlib
        ds.__dict__.pop('BASE', None)
        importlib.reload(ds)

    def tearDown(self):
        for k, v in self._old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        importlib_reload_safe()
        self.tmp.cleanup()


def importlib_reload_safe():
    import importlib
    importlib.reload(ds)


class TestLedgerGuards(_TempBase):
    """护栏 2：坏账本停写 + 两层记账（记账只走命令，格式对、坏行拦得住）。"""

    def test_corrupt_ledger_blocks_write(self):
        cwd = tempfile.mkdtemp()
        ledger = Path(cwd) / ".wordmirror" / "promises.jsonl"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("{不是合法json}\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), "promise", "done", "demo"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=cwd, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("不是合法 JSON", r.stdout + r.stderr)

    def test_promise_add_uses_project_layer_outside_repo(self):
        cwd = tempfile.mkdtemp()
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), "promise", "add", "要做的事"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=cwd, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(r.returncode, 0)
        proj = Path(cwd) / ".wordmirror" / "promises.jsonl"
        self.assertTrue(proj.exists())
        row = json.loads(proj.read_text(encoding="utf-8").strip())
        self.assertEqual(row["status"], "open")


class TestBindAndLocate(_TempBase):
    """护栏 4：bind 指针定位——装在 A 处、数据在 B 处时的接桥。"""

    def test_bind_writes_pointer_and_clear_removes(self):
        # bind 指针写到 ~/.wordmirror/bind.json；用 HOME 劫持隔离真实主目录
        fake_home = Path(self.tmp.name) / "home"
        fake_home.mkdir()
        env = {**os.environ, "HOME": str(fake_home), "USERPROFILE": str(fake_home)}
        env.pop("WORD_MIRROR_HOME", None)
        env.pop("DIGITAL_SELF_HOME", None)
        pointer = fake_home / ".wordmirror" / "bind.json"
        # 绑定：bind.json 出现，指向完整仓库
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "bind", str(self.repo)],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(pointer.exists())
        home_val = json.loads(pointer.read_text(encoding="utf-8"))["home"]
        self.assertEqual(os.path.normcase(home_val), os.path.normcase(str(self.repo)))
        # 解绑：bind.json 删掉
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "bind", "--clear"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 0)
        self.assertFalse(pointer.exists())

    def test_bind_rejects_dir_without_data(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), "bind", str(empty)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "WORD_MIRROR_HOME": str(self.repo)})
        self.assertNotEqual(r.returncode, 0)

    def test_ancestor_walk_finds_repo_layout(self):
        # 不设环境变量、无 bind：脚本向上逐级找祖先里带 data/corpus 的仓库布局
        env = {k: v for k, v in os.environ.items()
               if k not in ("WORD_MIRROR_HOME", "DIGITAL_SELF_HOME")}
        env["HOME"] = str(Path(self.tmp.name) / "nowhere")  # 保证 ~/.wordmirror 不存在
        env["USERPROFILE"] = env["HOME"]
        # 把脚本复制进临时仓库的深层目录，模拟"skill 装在别处、数据在祖先目录"
        nested = self.repo / "a" / "b" / "c"
        nested.mkdir(parents=True)
        for f in ("ds.py", "render.py"):
            (nested / f).write_text((SCRIPTS / f).read_text(encoding="utf-8"),
                                    encoding="utf-8")
        # 从深层目录 import ds，看它定位到的 BASE 是不是祖先仓库
        r = subprocess.run(
            [sys.executable, "-c", "import ds; print(ds.BASE)"],
            capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(nested))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(os.path.normcase(r.stdout.strip()), os.path.normcase(str(self.repo)))


class TestRender(_TempBase):
    """护栏 6：月报收两层账本（宣传口径=实现口径）；Wrapped 页月份数按数据实算。"""

    def _run_render(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "render.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
            cwd=cwd or str(self.repo),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def test_monthly_collects_both_ledger_layers(self):
        _write_jsonl(self.data / "corpus_dedup.jsonl", [
            {"agent": "zcode", "date": "2026-08-05", "proj": "demo",
             "sid": "s1", "msg": "定了，就这么做"},
        ])
        _write_jsonl(self.data / "promises.jsonl", [   # 全局层：8 月划掉
            {"date": "2026-07-01", "text": "全局层的欠账", "status": "closed",
             "closed_date": "2026-08-10", "agent": "cli"}])
        proj = Path(self.tmp.name) / "proj"
        proj.mkdir()
        _write_jsonl(proj / ".wordmirror" / "promises.jsonl", [  # 项目层：8 月划掉
            {"date": "2026-07-02", "text": "项目层的欠账", "status": "dropped",
             "closed_date": "2026-08-20", "agent": "zcode"}])
        r = self._run_render("monthly", "2026-08", cwd=str(proj))
        self.assertEqual(r.returncode, 0, r.stderr)
        out = (self.repo / "products" / "monthly" / "2026-08.html").read_text(encoding="utf-8")
        self.assertIn("全局层的欠账", out)
        self.assertIn("项目层的欠账", out)
        self.assertIn("（全局）", out)
        self.assertIn("（这个目录）", out)

    def test_wrapped_month_count_follows_data(self):
        months = {"2025-11": {"n": 10}, "2026-08": {"n": 20}}  # 10 个月跨度
        (self.data / "materials_monthly.json").write_text(
            json.dumps(months), encoding="utf-8")
        (self.data / "stats_wordfreq.json").write_text(
            json.dumps({"看": 5}, ensure_ascii=False), encoding="utf-8")
        (self.data / "stats_agents.json").write_text(
            json.dumps({"zcode": {"msgs": 30}}), encoding="utf-8")
        r = self._run_render("read")
        self.assertEqual(r.returncode, 0, r.stderr)
        out_dir = self.repo / "products" / "html"
        wrapped = (out_dir / "10_翻给你看.html").read_text(encoding="utf-8")
        self.assertIn("这 10 个月", wrapped)   # 不再写死"九个月"
        self.assertFalse((out_dir / "10_这九个月翻给你看.html").exists())


class TestWritebackCommand(_TempBase):
    """护栏 7：写回走命令——格式正确 + 坏行拦截（writeback-protocol 硬门槛的代码侧）。"""

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def test_wb_add_appends_valid_row(self):
        r = self._run_cli("wb", "add", "demo 项目确认关闭", "--topic", "project/demo",
                          "--ref", "用户原话「没有消息」")
        self.assertEqual(r.returncode, 0, r.stderr)
        p = self.data / "user_writebacks.jsonl"
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["msg"], "demo 项目确认关闭")
        self.assertEqual(rows[0]["topic"], "project/demo")
        self.assertEqual(rows[0]["date"], __import__("datetime").date.today().isoformat())

    def test_wb_add_blocks_corrupt_file(self):
        self.data.joinpath("user_writebacks.jsonl").write_text(
            "{坏行}\n", encoding="utf-8")
        r = self._run_cli("wb", "add", "新事实")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("不是合法 JSON", r.stdout + r.stderr)
        # 坏行还在，没被吞
        self.assertIn("坏行", self.data.joinpath("user_writebacks.jsonl").read_text(encoding="utf-8"))

    def test_wb_add_requires_content(self):
        r = self._run_cli("wb", "add", "")
        self.assertNotEqual(r.returncode, 0)


class TestSemanticFallback(_TempBase):
    """护栏 8：按意思搜没建索引时安静返回空（AI 会退回自己搜文件），不许报错。"""

    def test_vecsearch_query_returns_none_without_index(self):
        sys.path.insert(0, str(SCRIPTS))
        import vecsearch
        self.assertIsNone(vecsearch.query("任何问题"))


class TestPlainLanguageCopy(unittest.TestCase):
    """文案规矩（DESIGN.md 宪法条）：产品自己的话不堆术语，也不写硬凹的口号。
    只查产品文案的源文件（模板/脚本/README/输出模板），不查渲染出的数据页——
    用户自己的话里出现任何词（如他做的"向量库"）是正常的，不算产品文案问题。"""

    def _read(self, *parts):
        return (SKILL_DIR.joinpath(*parts)).read_text(encoding="utf-8")

    def test_colophon_is_plain_fact_not_cutesy_slogan(self):
        for f in ("templates/read_shell.html", "templates/tracker.html"):
            s = self._read(*f.split("/"))
            self.assertIn("数据只存在你自己的电脑上", s, f)
            for bad in ("纯本地", "零云端", "只住在", "你的话是你的"):
                self.assertNotIn(bad, s, "%s 还留着造作口号 %r" % (f, bad))

    def test_render_py_page_copy_has_no_jargon(self):
        s = self._read("scripts", "render.py")
        for bad in ("Wrapped", "数字自己档案馆", "语义检索", "语义索引", "画像"):
            self.assertNotIn(bad, s, "render.py 还留着 %r" % bad)

    def test_readme_has_no_jargon(self):
        s = self._read("README.md")
        for bad in ("画像", "蒸馏", "语义索引", "语料", "向量", "纯本地", "零云端"):
            self.assertNotIn(bad, s, "README 还留着 %r" % bad)

    def test_output_templates_are_plain(self):
        for f in ("references/portrait-template.md", "references/habits-template.md", "layers/public.md"):
            s = self._read(*f.split("/"))
            for bad in ("去重原话", "蒸馏", "数据源："):
                self.assertNotIn(bad, s, "%s 还留着 %r" % (f, bad))
        # portrait 头行换成人话（会渲染进网页的色带）
        self.assertIn("这些结论来自", self._read("references", "portrait-template.md"))


if __name__ == "__main__":
    unittest.main()
