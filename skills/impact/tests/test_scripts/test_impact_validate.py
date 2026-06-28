#!/usr/bin/env python3
"""Tests for impact_validate.py — V8 style rules check.

Run: python -m pytest skills/impact/tests/test_scripts/test_impact_validate.py -v
     or: python skills/impact/tests/test_scripts/test_impact_validate.py
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "impact_validate.py"


def _run_validator(repo_root: str, req_dir: str) -> tuple[int, str]:
    """Run impact_validate.py, return (exit_code, stdout)."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT), req_dir, "--repo-root", repo_root],
        capture_output=True, text=True, timeout=30,
    )
    return r.returncode, r.stdout


def _make_repo(style_rules: str | None = None, context_pack: str | None = None) -> tuple[str, str]:
    """Create a temp repo with optional _style-rules.md and context-pack.

    Returns (repo_root, req_dir).
    """
    td = tempfile.mkdtemp()

    # Create a 010-requirements.md so V1 auto-detects full mode
    req_dir = os.path.join(td, "req")
    os.makedirs(req_dir)
    with open(os.path.join(req_dir, "010-requirements.md"), "w", encoding="utf-8") as f:
        f.write("# Test Requirements\n\n- 测试需求\n")

    if style_rules is not None:
        ci_dir = os.path.join(td, "change-impact")
        os.makedirs(ci_dir)
        with open(os.path.join(ci_dir, "_style-rules.md"), "w", encoding="utf-8") as f:
            f.write(style_rules)

    if context_pack is not None:
        with open(os.path.join(req_dir, "000-context-pack.md"), "w", encoding="utf-8") as f:
            f.write(context_pack)

    return td, req_dir


def _v8_lines(stdout: str) -> list[str]:
    """Extract V8-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V8:" in l]


class TestV8NoStyleRules(unittest.TestCase):
    """V8: No _style-rules.md → PASS, fall back to profile style_axes."""

    def test_no_style_rules_passes(self):
        td, rd = _make_repo(style_rules=None)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("No _style-rules.md" in l for l in v8), f"Expected fallback, got: {v8}")
        self.assertTrue(all("FAIL" not in l for l in v8), f"V8 should not FAIL: {v8}")


class TestV8GrepRule(unittest.TestCase):
    """V8: grep-enforceable mandatory rule → PASS."""

    def test_grep_rule_enforceable(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 System.out | grep:`System\\.out` | 日志统一 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("grep enforceable" in l for l in v8), f"Expected grep enforceable, got: {v8}")
        self.assertTrue(any("1 mandatory rules are auto-enforceable" in l for l in v8), f"Got: {v8}")


class TestV8HumanConfirmRule(unittest.TestCase):
    """V8: '人工确认' mandatory rule → WARN (cannot auto-FAIL)."""

    def test_human_confirm_warns(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 对外接口必须返回 Result<T> | 人工确认返回类型 | 自研封装 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("无法自动 FAIL" in l for l in v8), f"Expected WARN about human review, got: {v8}")
        self.assertTrue(any("require human review" in l for l in v8), f"Got: {v8}")


class TestV8InvalidGrepPattern(unittest.TestCase):
    """V8: Invalid grep pattern → WARN."""

    def test_invalid_grep_pattern_warns(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 foo | grep:`(unclosed` | 语法错误 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("invalid grep pattern" in l for l in v8), f"Expected invalid pattern WARN, got: {v8}")


class TestV8GrepExcludeRule(unittest.TestCase):
    """V8: grep-exclude with correct format → PASS; missing :dir → WARN."""

    def test_grep_exclude_correct(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁止裸 axios | grep-exclude:`axios`:`src/api/` | API 层统一 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("grep-exclude enforceable" in l for l in v8), f"Expected grep-exclude PASS, got: {v8}")

    def test_grep_exclude_missing_dir_warns(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 baz | grep-exclude:`baz` | 缺少目录 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("missing ':dir'" in l for l in v8), f"Expected missing dir WARN, got: {v8}")


class TestV8AdvisoryRulesCount(unittest.TestCase):
    """V8: 2-column advisory table should be parsed correctly (not 0)."""

    def test_advisory_rules_counted(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 System.out | grep:`System\\.out` | 日志统一 |

## 建议规则

| 规则 | 说明 |
|------|------|
| Service 方法驼峰 | 命名一致 |
| 异常抛 BizException | 统一异常处理 |
"""
        td, rd = _make_repo(style_rules=rules)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("1 mandatory, 2 advisory" in l for l in v8), f"Expected 1 mandatory + 2 advisory, got: {v8}")


class TestV8ContextPackCheck(unittest.TestCase):
    """V8: context-pack style section presence/absence detection."""

    def test_context_pack_missing_style_section_warns(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 System.out | grep:`System\\.out` | 日志统一 |
"""
        ctx = "# Context Pack\n\n## 1. 变更意图\n\n- 用户原话：test\n"
        td, rd = _make_repo(style_rules=rules, context_pack=ctx)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("missing '### 风格规范'" in l for l in v8), f"Expected missing section WARN, got: {v8}")

    def test_context_pack_style_section_filled_passes(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 System.out | grep:`System\\.out` | 日志统一 |
"""
        ctx = """# Context Pack

### 风格规范

- `_style-rules.md` 状态：已读取（1 条强制规则，0 条建议规则）
"""
        td, rd = _make_repo(style_rules=rules, context_pack=ctx)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("filled in" in l for l in v8), f"Expected filled-in PASS, got: {v8}")

    def test_context_pack_style_section_empty_warns(self):
        rules = """## 强制规则

| 规则 | 校验手段 | 说明 |
|------|---------|------|
| 禁用 System.out | grep:`System\\.out` | 日志统一 |
"""
        ctx = """# Context Pack

### 风格规范

- `_style-rules.md` 状态：无
"""
        td, rd = _make_repo(style_rules=rules, context_pack=ctx)
        code, out = _run_validator(td, rd)
        v8 = _v8_lines(out)
        self.assertTrue(any("not filled in" in l for l in v8), f"Expected not-filled WARN, got: {v8}")


# ===========================================================================
# V9 Tests: Grading table fact consistency
# ===========================================================================


def _v9_lines(stdout: str) -> list[str]:
    """Extract V9-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V9:" in l]


def _write_impl(req_dir: str, content: str):
    """Write 030-implementation.md into req_dir."""
    with open(os.path.join(req_dir, "030-implementation.md"), "w", encoding="utf-8") as f:
        f.write(content)


class TestV9NoGradingTable(unittest.TestCase):
    """V9: No grading decision table in output → PASS (skip)."""

    def test_no_grading_table_passes(self):
        ctx = "# Context Pack\n\n## 7. 已确认事实\n\n- updateUserById 默认不含 password\n"
        td, rd = _make_repo(context_pack=ctx)
        _write_impl(rd, "# Implementation\n\nNo table here.\n")
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(any("No grading decision table" in l for l in v9), f"Expected skip PASS, got: {v9}")


class TestV9NoFacts(unittest.TestCase):
    """V9: §7 exists but empty (only template placeholders) → WARN."""

    def test_no_facts_warns(self):
        ctx = "# Context Pack\n\n## 7. 已确认事实\n\n- `[事实]` — 来源：`[路径]`\n"
        td, rd = _make_repo(context_pack=ctx)
        impl = "# Implementation\n\n| 现有覆盖 | 缺口 | 判档 |\n|---|---|---|\n| test | test | full |\n"
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(any("no confirmed facts" in l for l in v9), f"Expected no-facts WARN, got: {v9}")


class TestV9Consistent(unittest.TestCase):
    """V9: Grading table facts consistent with §7 → PASS."""

    def test_consistent_facts_pass(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92-100`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        impl = (
            "# Implementation\n\n"
            "| 用户原话关键词 | 现有覆盖 | 缺口 | 判档 |\n"
            "|---|---|---|---|\n"
            "| 返回不含密码 | updateUserById 默认不含 password | 新 service 显式 safe select | full |\n"
        )
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(
            any("consistent" in l.lower() for l in v9),
            f"Expected consistent PASS, got: {v9}"
        )
        self.assertTrue(all("WARN" not in l for l in v9), f"V9 should not WARN: {v9}")


class TestV9Contradiction(unittest.TestCase):
    """V9: Same entity described differently in grading table vs §7 → WARN."""

    def test_contradiction_warns(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92-100`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        impl = (
            "# Implementation\n\n"
            "| 用户原话关键词 | 现有覆盖 | 缺口 | 判档 |\n"
            "|---|---|---|---|\n"
            "| 返回不含密码 | updateUserById 默认含 password | 新 service 显式 safe select | full |\n"
        )
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(
            any("Contradiction" in l and "updateUserById" in l for l in v9),
            f"Expected contradiction WARN for updateUserById, got: {v9}"
        )


class TestV9Unconfirmed(unittest.TestCase):
    """V9: Grading table references entity not found in §7 → WARN."""

    def test_unconfirmed_fact_warns(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- getUserById 默认含 password — 来源：`src/services/user.service.ts:81-90`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        impl = (
            "# Implementation\n\n"
            "| 用户原话关键词 | 现有覆盖 | 缺口 | 判档 |\n"
            "|---|---|---|---|\n"
            "| 更新 phone | deleteUserById 默认含 password | 新 service | full |\n"
        )
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(
            any("not in §7" in l and "deleteUserById" in l for l in v9),
            f"Expected unconfirmed WARN for deleteUserById, got: {v9}"
        )


class TestV9NoSharedEntities(unittest.TestCase):
    """V9: Both §7 and grading table exist but no shared entities → PASS."""

    def test_no_shared_entities_passes(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- getUserById 默认含 password — 来源：`src/services/user.service.ts:81-90`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        impl = (
            "# Implementation\n\n"
            "| 用户原话关键词 | 现有覆盖 | 缺口 | 判档 |\n"
            "|---|---|---|---|\n"
            "| 新增端点 | 无路由 | 全新端点 | full |\n"
        )
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(
            any("No shared entities" in l for l in v9),
            f"Expected no-shared-entities PASS, got: {v9}"
        )


class TestV9SectionHeaderTable(unittest.TestCase):
    """V9: Grading table found via section header (Strategy 2), not header row."""

    def test_section_header_table(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        impl = (
            "# Implementation\n\n"
            "## 判档决策表\n\n"
            "| 关键词 | 现有覆盖 | 缺口 | 判档 |\n"
            "|---|---|---|---|\n"
            "| 返回不含密码 | updateUserById 默认不含 password | 新 service | full |\n"
        )
        _write_impl(rd, impl)
        code, out = _run_validator(td, rd)
        v9 = _v9_lines(out)
        self.assertTrue(
            any("consistent" in l.lower() for l in v9),
            f"Expected consistent PASS via section header, got: {v9}"
        )


if __name__ == "__main__":
    unittest.main()
