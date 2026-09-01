# -*- coding: utf-8 -*-
"""wordmirror 护栏回归测试。

这个 skill 的核心价值是一组"不许静默失败"的护栏（导出守门 / 坏账停写 /
两层记账 / 数据定位），它们写在 prompt 里没有执行手段，只能靠代码层硬拦。
本文件锁住这些护栏，防止后续迭代把它们改丢。

跑法：cd tests && python -m unittest test_wordmirror_guardrails -v
（纯临时目录夹具，不碰真实数据目录）
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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


class TestExportGate(_TempBase):
    """护栏 1：随身说明书只出公开层——公开层为空必须硬拦，绝不导画像。"""

    def test_empty_public_layer_blocks_export(self):
        # 不创建 layers/public.md → 导出必须失败退出，且明说原因
        r = self._run_cli("export")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("公开层", r.stdout + r.stderr)

    def test_public_layer_too_short_blocks_export(self):
        (self.data / "layers").mkdir()
        (self.data / "layers" / "public.md").write_text(
            "# 关于我\n<!-- 只有模板头 -->", encoding="utf-8")
        r = self._run_cli("export")
        self.assertNotEqual(r.returncode, 0)

    def test_valid_public_layer_exports_without_portrait(self):
        (self.data / "layers").mkdir()
        (self.data / "layers" / "public.md").write_text(
            "## 说话风格\n- 直说结论，别铺垫。" + "细" * 60, encoding="utf-8")
        (self.data / "profile").mkdir()
        (self.data / "profile" / "portrait.md").write_text(
            "# 我是谁（v1 · 2026-08-01）\n\n真实姓名：张三；薪资 20 万", encoding="utf-8")
        r = self._run_cli("export")
        self.assertEqual(r.returncode, 0)
        out = self.repo / "products" / "ME_随身说明书.md"
        self.assertTrue(out.exists())
        content = out.read_text(encoding="utf-8")
        self.assertIn("说话风格", content)
        self.assertNotIn("张三", content)      # 画像全文绝不进导出
        self.assertNotIn("20 万", content)     # 敏感数值不进导出

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})


class TestLedgerGuards(_TempBase):
    """护栏 2：坏账本停写；护栏 3：两层记账 + 定位方式透明。"""

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

    def test_where_reports_how_base_was_found(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ds.cmd_where()
        out = buf.getvalue()
        self.assertIn("定位方式", out)
        self.assertIn("WORD_MIRROR_HOME", out)


class TestBindAndLocate(_TempBase):
    """护栏 4：bind 指针定位——装在 A 处、数据在 B 处时的接桥。"""

    def test_bind_then_where_uses_pointer(self):
        # bind 指针写到 ~/.wordmirror/bind.json；用 HOME 劫持隔离真实主目录
        fake_home = Path(self.tmp.name) / "home"
        fake_home.mkdir()
        env = {**os.environ, "HOME": str(fake_home),
               "USERPROFILE": str(fake_home),
               "WORD_MIRROR_HOME": ""}
        env.pop("WORD_MIRROR_HOME", None)
        env.pop("DIGITAL_SELF_HOME", None)
        # 无绑定时：默认 ~/.wordmirror，明确告知还没数据
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "where"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertIn("定位方式", r.stdout)
        self.assertIn("默认", r.stdout)
        # 绑定后：定位到完整仓库
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), "bind", str(self.repo)],
            capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "where"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertIn("bind 指针", r.stdout)
        self.assertIn(str(self.repo), r.stdout)
        # 解绑
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "bind", "--clear"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 0)
        r = subprocess.run([sys.executable, str(SCRIPTS / "ds.py"), "where"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertNotIn("bind 指针", r.stdout)

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
        r = subprocess.run([sys.executable, str(nested / "ds.py"), "where"],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertIn("仓库布局", r.stdout)
        self.assertIn(str(self.repo), r.stdout)


class TestSynonymSearch(_TempBase):
    """护栏 5：检索扩词——记不住原词也能查到（含用户自扩 synonyms.json）。"""

    def test_builtin_synonym_group(self):
        _write_jsonl(self.data / "corpus_dedup.jsonl", [
            {"agent": "zcode", "date": "2026-08-01", "proj": "demo",
             "sid": "s1", "msg": "这周开始投简历找工作了"},
            {"agent": "zcode", "date": "2026-08-02", "proj": "demo",
             "sid": "s2", "msg": "随便写点别的"},
        ])
        buf = io.StringIO()
        with redirect_stdout(buf):
            ds.cmd_ask("求职")  # 内置组：求职/找工作/投简历/面试
        out = buf.getvalue()
        self.assertIn("投简历找工作", out)
        self.assertIn("近义词", out)

    def test_user_synonyms_json(self):
        _write_jsonl(self.data / "corpus_dedup.jsonl", [
            {"agent": "zcode", "date": "2026-08-01", "proj": "demo",
             "sid": "s1", "msg": "打印机又离线了"},
        ])
        (self.data / "synonyms.json").write_text(
            json.dumps({"打印机": ["一体机", "喷墨"]}, ensure_ascii=False), encoding="utf-8")
        self._reload_ds()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ds.cmd_ask("打印机")
        self.assertIn("离线", buf.getvalue())


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
        self.assertIn("全局账本", out)
        self.assertIn("项目账本", out)

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
    """护栏 8：ask 的降级链——无索引/无依赖时降回关键词+近义词，不许报错停摆。"""

    def test_ask_falls_back_to_keyword_without_index(self):
        # 临时夹具没建向量索引，也不装依赖：ask 必须安静降级到关键词路径
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "ds.py"), "ask", "收尾"],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("收尾", r.stdout)  # 找到夹具语料里那条

    def test_vecsearch_query_returns_none_without_index(self):
        sys.path.insert(0, str(SCRIPTS))
        import vecsearch
        self.assertIsNone(vecsearch.query("任何问题"))


if __name__ == "__main__":
    unittest.main()
