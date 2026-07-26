#!/usr/bin/env python3
"""d5_check.py 行为测试：推迟/放弃项回流反查 + 排除规则。

Run:
  python -m pytest skills/_common/tests/test_d5_check.py -v
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
    from d5_check import check
    from chain_validate import main as chain_main
finally:
    sys.path.pop(0)

SKILLS_ROOT = SCRIPT_DIR.parent
FIXTURES = {
    "intent.md": SKILLS_ROOT / "intent-anchor" / "tests" / "fixtures" / "valid-intent.md",
    "prd.md": SKILLS_ROOT / "intent-prd" / "tests" / "fixtures" / "valid-prd.md",
    "architecture.md": SKILLS_ROOT / "intent-design" / "tests" / "fixtures" / "valid-architecture.md",
    "design.md": SKILLS_ROOT / "intent-design" / "tests" / "fixtures" / "valid-design.md",
    "issues.md": SKILLS_ROOT / "intent-issues" / "tests" / "fixtures" / "valid-issues.md",
    "dev-record.md": SKILLS_ROOT / "intent-dev" / "tests" / "fixtures" / "valid-dev-record.md",
}


def _make_chain(files: dict[str, str]) -> Path:
    chain = Path(tempfile.mkdtemp()) / "intent-chain" / "2026-07-26-002-D5测试"
    chain.mkdir(parents=True)
    for name, content in files.items():
        (chain / name).write_text(content, encoding="utf-8")
    return chain


def _fixture(name: str) -> str:
    return FIXTURES[name].read_text(encoding="utf-8")


class TestD5CleanChain(unittest.TestCase):
    def test_official_fixtures_pass(self):
        """六个官方 fixture 组成的干净链路必须 PASS——PRD Out of Scope 和
        design「不做什么」里对推迟/放弃项的合法点名不得误报。"""
        chain = _make_chain({name: _fixture(name) for name in FIXTURES})
        passes, fails = check(chain)
        self.assertEqual([], fails, f"干净链路被误报: {fails}")
        self.assertTrue(any("未发现回流" in p for p in passes), passes)

    def test_intent_only_passes(self):
        chain = _make_chain({"intent.md": _fixture("intent.md")})
        passes, fails = check(chain)
        self.assertEqual([], fails)
        self.assertTrue(any("尚无下游" in p for p in passes), passes)

    def test_no_deferred_items_passes(self):
        chain = _make_chain({
            "intent.md": (
                "# INTENT\n\n## 4. 能力与决策\n\n"
                "| 能力 ID | 能力 | 描述 | 证据 ID | 决策 | 决策来源 |\n"
                "|---|---|---|---|---|---|\n"
                "| C01 | 生成交接记录 | 描述 | E01 | 保留 | 用户明确确认 |\n"
            ),
            "prd.md": _fixture("prd.md"),
        })
        passes, fails = check(chain)
        self.assertEqual([], fails)
        self.assertTrue(any("无推迟/放弃项" in p for p in passes), passes)


class TestD5Reintroduction(unittest.TestCase):
    def test_user_story_name_and_id_fails(self):
        """推迟项以名字+ID 回流到 User Stories → FAIL。"""
        drifted_prd = _fixture("prd.md").replace(
            "1. As a 开发者, I want 在会话结束前自动生成包含任务进度和阻塞的交接记录, "
            "so that 新会话能准确继续工作 [C01]",
            "1. As a 开发者, I want 在会话结束前自动生成包含任务进度和阻塞的交接记录, "
            "so that 新会话能准确继续工作 [C01]\n"
            "2. As a 开发者, I want 自动归档旧记录, so that 历史整洁 [C02]",
        )
        chain = _make_chain({"intent.md": _fixture("intent.md"), "prd.md": drifted_prd})
        passes, fails = check(chain)
        self.assertTrue(any("C02" in f and "User Stories" in f for f in fails),
                        f"应命中 User Stories 回流: {fails}")

    def test_issue_name_reintroduction_fails(self):
        """放弃项以名字回流到工单 What to build → FAIL。"""
        drifted_issues = _fixture("issues.md").replace(
            "在会话结束前触发生成交接记录，记录包含任务、进度、阻塞和下一步。新会话读取记录后能恢复进度。",
            "在会话结束前触发生成交接记录，记录包含任务、进度、阻塞和下一步。"
            "同时实现自动发送通知。",
        )
        chain = _make_chain({"intent.md": _fixture("intent.md"), "issues.md": drifted_issues})
        passes, fails = check(chain)
        self.assertTrue(any("C03" in f and "issues.md" in f for f in fails),
                        f"应命中工单回流: {fails}")

    def test_id_in_dev_record_fails(self):
        """放弃项以 ID 回流到开发记录 → FAIL。"""
        drifted_dev = _fixture("dev-record.md").replace(
            "- 重构内容：无",
            "- 重构内容：顺带实现了 C03 的通知逻辑",
        )
        chain = _make_chain({"intent.md": _fixture("intent.md"), "dev-record.md": drifted_dev})
        passes, fails = check(chain)
        self.assertTrue(any("C03" in f and "dev-record.md" in f for f in fails),
                        f"应命中开发记录回流: {fails}")


class TestD5NegativeGuard(unittest.TestCase):
    def test_negative_mention_in_issue_passes(self):
        """实现承载区里的负面提及（本期不做 X）不算回流。"""
        guarded_issues = _fixture("issues.md").replace(
            "在会话结束前触发生成交接记录，记录包含任务、进度、阻塞和下一步。新会话读取记录后能恢复进度。",
            "在会话结束前触发生成交接记录，记录包含任务、进度、阻塞和下一步。\n\n"
            "本期不做自动归档旧记录。",
        )
        chain = _make_chain({"intent.md": _fixture("intent.md"), "issues.md": guarded_issues})
        passes, fails = check(chain)
        self.assertEqual([], fails, f"负面提及被误报: {fails}")


class TestD5ChainIntegration(unittest.TestCase):
    def test_chain_validate_reports_d5_fail(self):
        """chain_validate 对回流链路输出 D5 FAIL 行并退出 1——
        即使单文件校验器各自通过，D5 交叉检查也能兜底。"""
        drifted_prd = _fixture("prd.md").replace(
            "1. As a 开发者, I want 在会话结束前自动生成包含任务进度和阻塞的交接记录, "
            "so that 新会话能准确继续工作 [C01]",
            "1. As a 开发者, I want 在会话结束前自动生成包含任务进度和阻塞的交接记录, "
            "so that 新会话能准确继续工作 [C01]\n"
            "2. As a 开发者, I want 自动归档旧记录, so that 历史整洁 [C02]",
        )
        chain = _make_chain({"intent.md": _fixture("intent.md"), "prd.md": drifted_prd})
        old_argv = sys.argv
        sys.argv = ["chain_validate.py", str(chain)]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = chain_main()
        finally:
            sys.argv = old_argv
        out = buf.getvalue()
        self.assertEqual(1, code, out)
        self.assertIn("D5", out)
        self.assertTrue(any("D5" in line and "FAIL" in line for line in out.splitlines()), out)


if __name__ == "__main__":
    unittest.main()
