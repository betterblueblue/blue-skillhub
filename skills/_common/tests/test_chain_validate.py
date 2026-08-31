#!/usr/bin/env python3
"""chain_validate.py 编排行为测试。

Run:
  python -m pytest skills/_common/tests/test_chain_validate.py -v
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from chain_validate import _dev_all_done, main
finally:
    sys.path.pop(0)

SKILLS_ROOT = SCRIPT_DIR.parent
VALID_INTENT = SKILLS_ROOT / "intent-anchor" / "tests" / "fixtures" / "valid-intent.md"
VALID_VISUAL = SKILLS_ROOT / "intent-visual" / "tests" / "fixtures" / "valid-visual-design.md"
VALID_BASELINE = SKILLS_ROOT / "intent-visual" / "tests" / "fixtures" / "valid-visual-baseline.html"


def _make_chain_dir() -> Path:
    """按 intent-chain/{链路目录}/ 路径契约创建临时链路目录。"""
    root = Path(tempfile.mkdtemp())
    chain = root / "intent-chain" / "2026-07-26-001-测试链路"
    chain.mkdir(parents=True)
    return chain


def _run_main(*args) -> int:
    old = sys.argv
    sys.argv = ["chain_validate.py"] + list(args)
    try:
        return main()
    finally:
        sys.argv = old


class TestChainValidate(unittest.TestCase):
    def test_missing_dir_exit_1(self):
        self.assertEqual(1, _run_main(str(Path(tempfile.mkdtemp()) / "不存在")))

    def test_intent_only_passes_rest_skipped(self):
        """只有 intent.md 时：intent 校验通过，下游标跳过，退出 0。"""
        chain = _make_chain_dir()
        (chain / "intent.md").write_text(
            VALID_INTENT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        self.assertEqual(0, _run_main(str(chain)))

    def test_broken_intent_exit_1(self):
        chain = _make_chain_dir()
        (chain / "intent.md").write_text("# 空壳\n", encoding="utf-8")
        self.assertEqual(1, _run_main(str(chain)))

    def test_missing_intent_with_orphan_prd_exit_1(self):
        """链路起点缺失时即使有下游文件也 FAIL。"""
        chain = _make_chain_dir()
        (chain / "prd.md").write_text("# PRD\n", encoding="utf-8")
        self.assertEqual(1, _run_main(str(chain)))

    def test_dev_all_done_detection(self):
        chain = _make_chain_dir()
        (chain / "issues.md").write_text("## Issue 1: A\n## Issue 2: B\n", encoding="utf-8")
        (chain / "dev-record.md").write_text("- 状态：done\n- 状态：done\n", encoding="utf-8")
        self.assertTrue(_dev_all_done(chain))

    def test_dev_not_all_done(self):
        chain = _make_chain_dir()
        (chain / "issues.md").write_text("## Issue 1: A\n## Issue 2: B\n", encoding="utf-8")
        (chain / "dev-record.md").write_text("- 状态：done\n- 状态：未通过\n", encoding="utf-8")
        self.assertFalse(_dev_all_done(chain))

    def test_dev_done_without_verify_record_exits_1(self):
        chain = _make_chain_dir()
        (chain / "issues.md").write_text("## Issue 1: A\n", encoding="utf-8")
        (chain / "dev-record.md").write_text("- 状态：done\n", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _run_main(str(chain))
        self.assertEqual(1, code)
        self.assertIn("verify-record.md", buf.getvalue())
        self.assertIn("FAIL", buf.getvalue())

    def test_visual_design_present_and_valid_passes(self):
        """visual-design.md 已产出且结构合法：visual 行 PASS，退出 0。"""
        chain = _make_chain_dir()
        (chain / "intent.md").write_text(
            VALID_INTENT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (chain / "visual-design.md").write_text(
            VALID_VISUAL.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (chain / "visual-baseline.html").write_text(
            VALID_BASELINE.read_text(encoding="utf-8"), encoding="utf-8"
        )
        self.assertEqual(0, _run_main(str(chain)))

    def test_visual_design_broken_fails(self):
        """visual-design.md 已产出但缺基线页（V10）：FAIL，退出 1。"""
        chain = _make_chain_dir()
        (chain / "intent.md").write_text(
            VALID_INTENT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (chain / "visual-design.md").write_text(
            VALID_VISUAL.read_text(encoding="utf-8"), encoding="utf-8"
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _run_main(str(chain))
        self.assertEqual(1, code)
        self.assertIn("visual-baseline.html", buf.getvalue())

    def test_visual_design_absent_is_skipped(self):
        """visual-design.md 未产出（非 UI 项目或用户拒绝）：标跳过，不影响退出码。"""
        chain = _make_chain_dir()
        (chain / "intent.md").write_text(
            VALID_INTENT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _run_main(str(chain))
        self.assertEqual(0, code)
        self.assertIn("visual-design.md", buf.getvalue())
        self.assertIn("跳过", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
