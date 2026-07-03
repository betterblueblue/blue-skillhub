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

SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "impact_validate.py"


def _run_validator(repo_root: str, req_dir: str) -> tuple[int, str]:
    """Run impact_validate.py, return (exit_code, stdout)."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT), req_dir, "--repo-root", repo_root],
        capture_output=True, text=True, timeout=30,
    )
    return r.returncode, r.stdout


def _make_repo(style_rules: str | None = None, context_pack: str | None = None) -> tuple[str, str]:
    """Create a temp repo with all required files for full-mode validation.

    Creates 000/010/020/030/_active-state.md so V1/V10/V12 pass.
    Tests that need specific 030 content can call _write_impl to overwrite.

    Returns (repo_root, req_dir).
    """
    td = tempfile.mkdtemp()
    req_dir = os.path.join(td, "req")
    os.makedirs(req_dir)

    # 010-requirements.md (triggers full-mode auto-detection)
    with open(os.path.join(req_dir, "010-requirements.md"), "w", encoding="utf-8") as f:
        f.write("# Test Requirements\n\n- 测试需求\n")

    # 000-context-pack.md (use provided or default)
    if context_pack is None:
        context_pack = "# Context Pack\n\n## 1. 变更意图\n\n- 用户原话：test\n"
    with open(os.path.join(req_dir, "000-context-pack.md"), "w", encoding="utf-8") as f:
        f.write(context_pack)

    # 020-design.md with §6 全局影响检查 (19 rows, all ☐)
    rows = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
    with open(os.path.join(req_dir, "020-design.md"), "w", encoding="utf-8") as f:
        f.write(f"# Design\n\n## 6. 全局影响检查\n\n| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |\n|---|------|----------|----------|-------------|\n{rows}\n")

    # 030-implementation.md (minimal, no method calls)
    with open(os.path.join(req_dir, "030-implementation.md"), "w", encoding="utf-8") as f:
        f.write("# Implementation\n\nNo changes.\n")

    # _active-state.md (Phase 3 fields for V12)
    with open(os.path.join(req_dir, "_active-state.md"), "w", encoding="utf-8") as f:
        f.write("# Active State\n\n## Phase 3 状态\n\n已完成\n\n## Phase 3.5 定级\n\nlight\n")

    if style_rules is not None:
        ci_dir = os.path.join(td, "change-impact")
        os.makedirs(ci_dir)
        with open(os.path.join(ci_dir, "_style-rules.md"), "w", encoding="utf-8") as f:
            f.write(style_rules)

    return td, req_dir


def _v8_lines(stdout: str) -> list[str]:
    """Extract V8-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V8:" in l]


class TestV8NoStyleRules(unittest.TestCase):
    """V8: No _style-rules.md → PASS, fall back to profile style_axes."""

    def test_no_style_rules_passes(self):
        td, rd = _make_repo(style_rules=None)
        code, out = _run_validator(td, rd)
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
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
        self.assertEqual(code, 0, f"Expected exit 0 (no FAIL), got {code}\n{out}")
        v9 = _v9_lines(out)
        self.assertTrue(
            any("consistent" in l.lower() for l in v9),
            f"Expected consistent PASS via section header, got: {v9}"
        )


# ===========================================================================
# V5 Tests: Credential sanitization (per-match, not per-line)
# ===========================================================================


def _v5_lines(stdout: str) -> list[str]:
    """Extract V5-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V5:" in l]


class TestV5MixedCredentialLine(unittest.TestCase):
    """V5: A line with both sanitized and unsanitized credentials should
    only warn for the unsanitized one, not skip the entire line."""

    def test_mixed_line_warns_only_unsanitized(self):
        td, rd = _make_repo()
        # Overwrite 030-implementation.md with a mixed credential line
        with open(os.path.join(rd, "030-implementation.md"), "w", encoding="utf-8") as f:
            f.write("# Implementation\n\npassword=*** token=plainsecret\n")
        code, out = _run_validator(td, rd)
        v5 = _v5_lines(out)
        # Should warn about token= but NOT about password=
        self.assertTrue(
            any("possible credential (token=)" in l for l in v5),
            f"Expected WARN for token=, got: {v5}"
        )
        self.assertFalse(
            any("possible credential (password=)" in l for l in v5),
            f"Should not WARN for sanitized password=, got: {v5}"
        )
        # Exit code 0 (V5 is WARN, not FAIL)
        self.assertEqual(code, 0, f"V5 WARN should not cause FAIL exit, got {code}\n{out}")


# ===========================================================================
# V13 Tests: Phase 4/5 split gate
# ===========================================================================


def _v13_lines(stdout: str) -> list[str]:
    """Extract V13-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V13:" in l]


def _write_execution_record(req_dir: str, content: str):
    """Write 090-execution-record.md into req_dir."""
    with open(os.path.join(req_dir, "090-execution-record.md"), "w", encoding="utf-8") as f:
        f.write(content)


def _write_preflight(req_dir: str):
    """Write minimal 060-preflight.md into req_dir."""
    with open(os.path.join(req_dir, "060-preflight.md"), "w", encoding="utf-8") as f:
        f.write("# Preflight\n\n## Phase 4/5 分步\n\n已完成\n")


class TestV13Phase4Phase5Split(unittest.TestCase):
    """V13: Phase 4 docs and source writes must not be merged in one Step."""

    def test_merged_doc_and_source_step_fails(self):
        td, rd = _make_repo()
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 17:52:23] Step 1: 写入 light 文档、修改登录失败提示及对应测试

- 操作对象：`000-context-pack.md`、`040-light.md`、`src/services/auth.service.ts`、`tests/services/auth.service.test.ts`
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v13 = _v13_lines(out)
        self.assertEqual(code, 1, f"Merged docs+source Step should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("merged in the same Step" in l for l in v13),
            f"Expected V13 merged-step FAIL, got: {v13}"
        )

    def test_doc_step_with_source_evidence_passes(self):
        td, rd = _make_repo()
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 17:49:00] Step 1: 写入 light 文档

- 确认类型：写文件
- 操作对象：`000-context-pack.md`、`040-light.md`、`_active-state.md`
- 操作内容：基于 `src/services/auth.service.ts` 和 `tests/services/auth.service.test.ts` 生成 light 文档
- 影响范围：`src/services/auth.service.ts`
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v13 = _v13_lines(out)
        self.assertEqual(code, 0, f"Docs-only Step with source evidence should pass, got {code}\n{out}")
        self.assertTrue(
            any("separated" in l for l in v13),
            f"Expected V13 separated PASS, got: {v13}"
        )

    def test_source_step_with_later_summary_mentions_preflight_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 3: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`
- 操作内容：修改登录失败提示并同步测试断言
- 用户确认：确认 Step 3

## 验证等级汇总

| Step | 验证等级 | 未运行验证原因 |
|------|----------|---------------|
| Step 1 | V1 | Phase 4 文档校验通过 |
| Step 2 | V1 | 仅写 preflight 文档，未进入源码验证 |
| Step 3 | V1 | 本机依赖缺失，`jest` 无法正常启动 |
""",
        )
        code, out = _run_validator(td, rd)
        v13 = _v13_lines(out)
        self.assertEqual(code, 0, f"Source Step with later summary should pass, got {code}\n{out}")
        self.assertTrue(
            any("separated" in l for l in v13),
            f"Expected V13 separated PASS, got: {v13}"
        )

    def test_source_step_after_docs_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 17:50:00] Step 1: 修改登录失败提示及对应测试

- 前置条件：Phase 4 已完成，impact_validate.py 已通过。
- 操作对象：`src/services/auth.service.ts`、`tests/services/auth.service.test.ts`
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v13 = _v13_lines(out)
        self.assertEqual(code, 0, f"Separate source Step should pass, got {code}\n{out}")
        self.assertTrue(
            any("separated" in l for l in v13),
            f"Expected V13 separated PASS, got: {v13}"
        )


def _v14_lines(stdout: str) -> list[str]:
    """Extract V14-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V14:" in l]


class TestV14Phase5Preflight(unittest.TestCase):
    """V14: Source/test/config writes require 060-preflight.md."""

    def test_source_step_without_preflight_fails(self):
        td, rd = _make_repo()
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 3: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`
- 操作内容：修改登录失败提示并同步测试断言
- 用户确认：确认 Step 3
""",
        )
        code, out = _run_validator(td, rd)
        v14 = _v14_lines(out)
        self.assertEqual(code, 1, f"Source Step without preflight should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("060-preflight.md is missing" in l for l in v14),
            f"Expected V14 missing-preflight FAIL, got: {v14}"
        )

    def test_source_step_with_preflight_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 3: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`
- 操作内容：修改登录失败提示并同步测试断言
- 用户确认：确认 Step 3
""",
        )
        code, out = _run_validator(td, rd)
        v14 = _v14_lines(out)
        self.assertEqual(code, 0, f"Source Step with preflight should pass, got {code}\n{out}")
        self.assertTrue(
            any("060-preflight.md exists" in l for l in v14),
            f"Expected V14 preflight PASS, got: {v14}"
        )


if __name__ == "__main__":
    unittest.main()
