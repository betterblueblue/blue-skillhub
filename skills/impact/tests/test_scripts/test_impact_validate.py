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

    # _active-state.md (Phase 3 fields for V12, Step state for V16)
    with open(os.path.join(req_dir, "_active-state.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Active State

## 状态头

- 当前阶段：Phase 4
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：full
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 恢复备注

- 无
"""
        )

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
        ctx = "# Context Pack\n\n## 7. 已确认事实\n\n- updateUserById 默认不含 password 【代码推断: src/services/user.service.ts:92】\n"
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
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92-100` 【代码推断: src/services/user.service.ts:92】\n"
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
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92-100` 【代码推断: src/services/user.service.ts:92】\n"
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
            "- getUserById 默认含 password — 来源：`src/services/user.service.ts:81-90` 【代码推断: src/services/user.service.ts:81】\n"
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
            "- getUserById 默认含 password — 来源：`src/services/user.service.ts:81-90` 【代码推断: src/services/user.service.ts:81】\n"
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
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92` 【代码推断: src/services/user.service.ts:92】\n"
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


def _write_active_state(req_dir: str, content: str):
    """Write _active-state.md into req_dir."""
    with open(os.path.join(req_dir, "_active-state.md"), "w", encoding="utf-8") as f:
        f.write(content)


def _init_git_with_source(
    repo_root: str,
    relpath: str = "src/routes/sidebar.ts",
    content: str = "export const label = 'Dashboard';\n",
) -> str:
    """Create a committed source file, then return its absolute path."""
    source_path = os.path.join(repo_root, *relpath.split("/"))
    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(content)

    def run_git(*args: str):
        subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

    run_git("init")
    run_git("config", "user.email", "impact-test@example.com")
    run_git("config", "user.name", "Impact Test")
    run_git("add", relpath)
    run_git("commit", "-m", "seed source")
    return source_path


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
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`; `090-execution-record.md`; `_active-state.md`
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
- 操作对象：`src/services/auth.service.ts`、`tests/services/auth.service.test.ts`、`090-execution-record.md`、`_active-state.md`
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

    def test_source_step_with_associated_docs_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## Step 1：修改 dashboard.router.tsx 展示文案

### 执行信息

- 确认类型：改代码
- 操作对象：`src/views/dashboard/dashboard.router.tsx`; `090-execution-record.md`; `_active-state.md`
- 关联文档：040-light.md、060-preflight.md
- 操作内容：修改 `src/views/dashboard/dashboard.router.tsx` 第 17-18 行
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v13 = _v13_lines(out)
        self.assertEqual(code, 0, f"Associated docs in a source Step should not trip V13, got {code}\n{out}")
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
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`; `090-execution-record.md`; `_active-state.md`
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
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`; `090-execution-record.md`; `_active-state.md`
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


def _v15_lines(stdout: str) -> list[str]:
    """Extract V15-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V15:" in l]


class TestV15Phase5RecordState(unittest.TestCase):
    """V15: Source/test/config writes must include execution record and active state."""

    def test_source_diff_without_execution_record_fails(self):
        td, rd = _make_repo()
        source_path = _init_git_with_source(td)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write("export const label = 'Insights';\n")

        code, out = _run_validator(td, rd)
        v15 = _v15_lines(out)
        self.assertEqual(code, 1, f"Source diff without execution record should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("090-execution-record.md is missing" in l for l in v15),
            f"Expected V15 missing execution-record FAIL, got: {v15}"
        )

    def test_source_diff_with_record_but_no_source_step_fails(self):
        td, rd = _make_repo()
        source_path = _init_git_with_source(td)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write("export const label = 'Insights';\n")
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:40:00] Step 1: 写入 light 文档

- 确认类型：写文件
- 操作对象：`000-context-pack.md`; `040-light.md`; `_active-state.md`
- 用户确认：确认 Step 1
""",
        )

        code, out = _run_validator(td, rd)
        v15 = _v15_lines(out)
        self.assertEqual(code, 1, f"Source diff with docs-only record should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("has no source/test/config write Step" in l for l in v15),
            f"Expected V15 no source Step FAIL, got: {v15}"
        )

    def test_source_step_missing_record_state_fails(self):
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
        v15 = _v15_lines(out)
        self.assertEqual(code, 1, f"Source Step missing record/state should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("must include execution record" in l for l in v15),
            f"Expected V15 record/state FAIL, got: {v15}"
        )

    def test_source_step_with_record_state_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 3: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/services/auth.service.ts`; `tests/services/auth.service.test.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改登录失败提示并同步测试断言，追加执行记录并更新状态文件
- 用户确认：确认 Step 3
""",
        )
        code, out = _run_validator(td, rd)
        v15 = _v15_lines(out)
        self.assertEqual(code, 0, f"Source Step with record/state should pass, got {code}\n{out}")
        self.assertTrue(
            any("include execution record and active-state" in l for l in v15),
            f"Expected V15 record/state PASS, got: {v15}"
        )

    def test_unrecorded_source_diff_fails_even_with_valid_source_step(self):
        td, rd = _make_repo()
        source_path = _init_git_with_source(td)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write("export const label = 'Insights';\n")
        with open(os.path.join(td, "debug_v13.py"), "w", encoding="utf-8") as f:
            f.write("print('debug')\n")
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 源码修改

- 确认类型：改代码
- 操作对象：`src/routes/sidebar.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改侧边栏文案
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v15 = _v15_lines(out)
        self.assertEqual(code, 1, f"Unrecorded debug_v13.py should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("debug_v13.py" in l and "Unrecorded path" in l for l in v15),
            f"Expected V15 unrecorded path FAIL, got: {v15}"
        )


def _v17_lines(stdout: str) -> list[str]:
    """Extract V17-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V17:" in l]


ROUTER_BEFORE = """const dashboardRoutes = [
  {
    path: 'dashboard',
    meta: {
      label: 'Dashboard',
      title: 'Dashboard',
      key: '/dashboard',
      icon: 'DashboardOutlined',
      order: 1,
    },
  },
];
"""


def _write_source_step_record(req_dir: str, relpath: str):
    _write_preflight(req_dir)
    _write_execution_record(
        req_dir,
        f"""# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改展示文案

- 确认类型：改代码
- 操作对象：`{relpath}`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改路由展示文案
- 用户确认：确认 Step 1
""",
    )


class TestV17TaskAcceptanceSmoke(unittest.TestCase):
    """V17: Catch obvious partial route display text updates."""

    def test_route_label_changed_but_title_left_old_fails(self):
        td, rd = _make_repo()
        relpath = "src/views/dashboard/dashboard.router.tsx"
        source_path = _init_git_with_source(td, relpath, ROUTER_BEFORE)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(ROUTER_BEFORE.replace("label: 'Dashboard'", "label: 'Insights'"))
        _write_source_step_record(rd, relpath)

        code, out = _run_validator(td, rd)
        v17 = _v17_lines(out)
        self.assertEqual(code, 1, f"label-only route text update should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("partially updated" in l and "title remains" in l for l in v17),
            f"Expected V17 partial route text FAIL, got: {v17}"
        )

    def test_route_label_and_title_changed_together_passes(self):
        td, rd = _make_repo()
        relpath = "src/views/dashboard/dashboard.router.tsx"
        source_path = _init_git_with_source(td, relpath, ROUTER_BEFORE)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(
                ROUTER_BEFORE
                .replace("label: 'Dashboard'", "label: 'Insights'")
                .replace("title: 'Dashboard'", "title: 'Insights'")
            )
        _write_source_step_record(rd, relpath)

        code, out = _run_validator(td, rd)
        v17 = _v17_lines(out)
        self.assertEqual(code, 0, f"paired route text update should pass, got {code}\n{out}")
        self.assertTrue(
            any("No obvious partial route" in l for l in v17),
            f"Expected V17 PASS, got: {v17}"
        )


def _v16_lines(stdout: str) -> list[str]:
    """Extract V16-related lines from stdout."""
    return [l for l in stdout.splitlines() if "V16:" in l]


class TestV16ActiveStateConsistency(unittest.TestCase):
    """V16: _active-state.md header, Step ledger and notes must agree."""

    def test_completed_step_with_pending_row_fails(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 4: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/routes/sidebar.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改侧边栏文案并同步执行记录
- 用户确认：确认 Step 4
""",
        )
        _write_active_state(
            rd,
            """# Active State

## 状态头

- 当前阶段：完成
- 模式：light
- Phase 3 状态：快速通道跳过
- Phase 3.5 定级：快速通道跳过
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：Step 4
- 上次确认 Step：Step 4
- 上次完成 Step：Step 4
- V1-only 计数：1

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Step 4 | 待确认 | `src/routes/sidebar.ts` | 需要 | V1 | |

## 恢复备注

- 下一步需要确认 Step 3 后继续源码写入
""",
        )
        code, out = _run_validator(td, rd)
        v16 = _v16_lines(out)
        self.assertEqual(code, 1, f"Stale active-state should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("Step state is inconsistent" in l for l in v16),
            f"Expected V16 inconsistency FAIL, got: {v16}"
        )

    def test_completed_step_with_terminal_row_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 4: 源码/测试修改

- 确认类型：改代码 / 测试修复
- 操作对象：`src/routes/sidebar.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改侧边栏文案并同步执行记录
- 用户确认：确认 Step 4
""",
        )
        _write_active_state(
            rd,
            """# Active State

## 状态头

- 当前阶段：完成
- 模式：light
- Phase 3 状态：快速通道跳过
- Phase 3.5 定级：快速通道跳过
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：Step 4
- 上次确认 Step：Step 4
- 上次完成 Step：Step 4
- V1-only 计数：1

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Step 4 | 成功 | `src/routes/sidebar.ts` | 已确认 | V1 | 验证受限 |

## 恢复备注

- 任务已完成，无待确认 Step
""",
        )
        code, out = _run_validator(td, rd)
        v16 = _v16_lines(out)
        self.assertEqual(code, 0, f"Consistent active-state should pass, got {code}\n{out}")
        self.assertTrue(
            any("internally consistent" in l for l in v16),
            f"Expected V16 consistency PASS, got: {v16}"
        )


# ===========================================================================
# V12 Tests: Phase 3 process state consistency
# ===========================================================================


def _v12_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V12:" in l]


class TestV12Phase3ProcessConsistency(unittest.TestCase):
    """V12: full-mode active-state must not keep a light grading."""

    def test_full_mode_with_light_grading_fails(self):
        td, rd = _make_repo()
        _write_active_state(
            rd,
            """# Active State

## 状态头

- 当前阶段：完成
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：light
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 恢复备注

- 无
""",
        )
        code, out = _run_validator(td, rd)
        v12 = _v12_lines(out)
        self.assertEqual(code, 1, f"Conflicting active-state grading should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("conflicts with 模式" in l for l in v12),
            f"Expected V12 conflict FAIL, got: {v12}"
        )


# ===========================================================================
# V18 Tests: Verification evidence
# ===========================================================================


def _v18_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V18:" in l]


class TestV18VerificationEvidence(unittest.TestCase):
    """V18: _active-state.md 最近验证 must have actual validator output."""

    def test_placeholder_result_fails(self):
        td, rd = _make_repo()
        _write_active_state(rd, """# Active State

## 状态头

- 当前阶段：Phase 4
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：full
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 最近验证

- 命令：`python skills/impact/scripts/impact_validate.py`
- 结果：[X passed, Y failed, Z warnings]
- 验证等级：V1
- 跳过原因：不适用 — 必须运行

## 恢复备注

- 无
""")
        code, out = _run_validator(td, rd)
        v18 = _v18_lines(out)
        self.assertEqual(code, 1, f"Placeholder result should FAIL, got {code}\n{out}")
        self.assertTrue(any("placeholder" in l for l in v18), f"Expected placeholder FAIL, got: {v18}")

    def test_na_result_fails(self):
        td, rd = _make_repo()
        _write_active_state(rd, """# Active State

## 状态头

- 当前阶段：Phase 4
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：full
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 最近验证

- 命令：`python skills/impact/scripts/impact_validate.py`
- 结果：N/A
- 验证等级：V0
- 跳过原因：不适用

## 恢复备注

- 无
""")
        code, out = _run_validator(td, rd)
        v18 = _v18_lines(out)
        self.assertEqual(code, 1, f"N/A result should FAIL, got {code}\n{out}")
        self.assertTrue(any("placeholder" in l for l in v18), f"Expected placeholder FAIL, got: {v18}")

    def test_actual_result_passes(self):
        td, rd = _make_repo()
        _write_active_state(rd, """# Active State

## 状态头

- 当前阶段：Phase 4
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：full
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 最近验证

- 命令：`python skills/impact/scripts/impact_validate.py`
- 结果：15 passed, 0 failed, 2 warnings
- 验证等级：V1
- 跳过原因：不适用 — 必须运行

## 恢复备注

- 无
""")
        code, out = _run_validator(td, rd)
        v18 = _v18_lines(out)
        self.assertEqual(code, 0, f"Actual result should pass, got {code}\n{out}")
        self.assertTrue(any("actual validator result" in l for l in v18), f"Expected V18 PASS, got: {v18}")

    def test_nonzero_failed_result_fails(self):
        td, rd = _make_repo()
        _write_active_state(rd, """# Active State

## 状态头

- 当前阶段：Phase 4
- 模式：full
- Phase 3 状态：已完成
- Phase 3.5 定级：full
- 是否需要确认：false
- 待执行 Step：none
- 上次提示 Step：none
- 上次确认 Step：none
- 上次完成 Step：none
- V1-only 计数：0

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 最近验证

- 命令：`python skills/impact/scripts/impact_validate.py`
- 结果：29 passed, 1 failed, 0 warnings
- 验证等级：V1
- 跳过原因：不适用

## 恢复备注

- 无
""")
        code, out = _run_validator(td, rd)
        v18 = _v18_lines(out)
        self.assertEqual(code, 1, f"Nonzero failed result should FAIL, got {code}\n{out}")
        self.assertTrue(any("0 failed" in l for l in v18), f"Expected nonzero failed FAIL, got: {v18}")


# ===========================================================================
# V19 Tests: High-risk DDL crosscheck
# ===========================================================================


def _v19_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V19:" in l]


class TestV19DDLCCrosscheck(unittest.TestCase):
    """V19: Steps with DDL keywords must have high-risk checklist."""

    def test_ddl_without_checklist_fails(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: DROP TABLE old_tags

- 确认类型：DDL
- 操作对象：`old_tags` table
- 操作内容：DROP TABLE old_tags
- 决策依据：不涉及
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v19 = _v19_lines(out)
        self.assertEqual(code, 1, f"DDL without checklist should FAIL, got {code}\n{out}")
        self.assertTrue(any("high-risk checklist" in l for l in v19), f"Expected V19 FAIL, got: {v19}")

    def test_ddl_with_checklist_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: DROP TABLE old_tags

- 确认类型：DDL
- 操作对象：`old_tags` table
- 操作内容：DROP TABLE old_tags
- 决策依据：命中 DROP TABLE，用户已单独确认
- 高风险清单检查（PASS/FAIL 表格）：

  | 检查项 | 状态 | 说明 |
  | --- | --- | --- |
  | DROP TABLE | PASS | 用户已确认 |

- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v19 = _v19_lines(out)
        self.assertTrue(any("checklist filled" in l for l in v19), f"Expected V19 PASS, got: {v19}")

    def test_no_ddl_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改文案

- 确认类型：改代码
- 操作对象：`src/views/dashboard.tsx`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改展示文案
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v19 = _v19_lines(out)
        self.assertTrue(any("No DDL keywords" in l for l in v19), f"Expected V19 no-DDL PASS, got: {v19}")


# ===========================================================================
# V20 Tests: Step confirmation field
# ===========================================================================


def _v20_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V20:" in l]


class TestV20StepConfirmation(unittest.TestCase):
    """V20: Every Step must have 用户确认 with Step number."""

    def test_step_without_confirmation_fails(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改文案

- 确认类型：改代码
- 操作对象：`src/views/dashboard.tsx`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改展示文案
""",
        )
        code, out = _run_validator(td, rd)
        v20 = _v20_lines(out)
        self.assertEqual(code, 1, f"Step without confirmation should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing" in l for l in v20), f"Expected V20 FAIL, got: {v20}")

    def test_step_with_confirmation_passes(self):
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改文案

- 确认类型：改代码
- 操作对象：`src/views/dashboard.tsx`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改展示文案
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v20 = _v20_lines(out)
        self.assertTrue(any("All Steps have" in l for l in v20), f"Expected V20 PASS, got: {v20}")


# ===========================================================================
# V21 Tests: Provenance tags
# ===========================================================================


def _v21_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V21:" in l]


class TestV21ProvenanceTags(unittest.TestCase):
    """V21: §7 facts must have source tags."""

    def test_untagged_facts_fail(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92`\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        code, out = _run_validator(td, rd)
        v21 = _v21_lines(out)
        self.assertEqual(code, 1, f"Untagged facts should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing source" in l for l in v21), f"Expected V21 FAIL, got: {v21}")

    def test_tagged_facts_pass(self):
        ctx = (
            "# Context Pack\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92` 【代码推断: src/services/user.service.ts:92】\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        code, out = _run_validator(td, rd)
        v21 = _v21_lines(out)
        self.assertEqual(code, 0, f"Tagged facts should pass, got {code}\n{out}")
        self.assertTrue(any("source tags" in l for l in v21), f"Expected V21 PASS, got: {v21}")

    def test_no_facts_passes(self):
        ctx = "# Context Pack\n\n## 1. 变更意图\n\n- 用户原话：test\n"
        td, rd = _make_repo(context_pack=ctx)
        code, out = _run_validator(td, rd)
        v21 = _v21_lines(out)
        self.assertTrue(any("no §7" in l for l in v21) or any("no fact entries" in l for l in v21),
                        f"Expected V21 no-facts WARN/PASS, got: {v21}")


def _v22_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V22:" in l]


class TestV22PathfinderConsumption(unittest.TestCase):
    """V22: Existing Pathfinder maps must have an auditable consumption record."""

    def test_map_exists_without_consumption_record_fails(self):
        ctx = (
            "# Context Pack\n\n"
            "## 1. 变更意图\n\n"
            "- 项目地图状态：新鲜 — 地图 commit：`abc1234` / 当前 HEAD：`abc1234`\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92` 【代码推断: src/services/user.service.ts:92】\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        code, out = _run_validator(td, rd)
        v22 = _v22_lines(out)
        self.assertEqual(code, 1, f"Missing map consumption record should FAIL, got {code}\n{out}")
        self.assertTrue(any("no Pathfinder" in l for l in v22), f"Expected V22 FAIL, got: {v22}")

    def test_map_exists_with_consumption_record_passes(self):
        ctx = (
            "# Context Pack\n\n"
            "## 1. 变更意图\n\n"
            "- 项目地图状态：新鲜 — 地图 commit：`abc1234` / 当前 HEAD：`abc1234`\n\n"
            "## 3. 分层上下文\n\n"
            "### Pathfinder 地图消费记录\n\n"
            "| 地图事实 / 章节 | 处理方式 | Impact 复核证据 | 结论 |\n"
            "|---|---|---|---|\n"
            "| 地图【8】构建运行测试 | 重新验证 | `package.json:7` | 使用 npm test 作为候选验证入口 |\n\n"
            "## 7. 已确认事实\n\n"
            "- updateUserById 默认不含 password — 来源：`src/services/user.service.ts:92` 【代码推断: src/services/user.service.ts:92】\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        code, out = _run_validator(td, rd)
        v22 = _v22_lines(out)
        self.assertEqual(code, 0, f"Map consumption record should pass, got {code}\n{out}")
        self.assertTrue(any("consumption record" in l for l in v22), f"Expected V22 PASS, got: {v22}")


if __name__ == "__main__":
    unittest.main()
