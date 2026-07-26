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

    # 020-design.md with §5.1 (无额外结构) and §6 全局影响检查 (19 rows, all ☐)
    rows = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
    with open(os.path.join(req_dir, "020-design.md"), "w", encoding="utf-8") as f:
        f.write(
            f"# Design\n\n"
            f"## 5.1 额外结构与假设\n\n无额外结构\n\n"
            f"## 6. 全局影响检查\n\n"
            f"| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |\n"
            f"|---|------|----------|----------|-------------|\n"
            f"{rows}\n"
        )

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

## 最近验证

- 命令：`python skills/impact/scripts/impact_validate.py`
- 结果：21 passed, 0 failed, 0 warnings
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
    """Write _active-state.md into req_dir.

    If content doesn't include a 最近验证 section, append a valid one
    so V18 doesn't block tests that aren't testing V18 specifically.
    """
    if "最近验证" not in content:
        content = content.rstrip() + "\n\n## 最近验证\n\n- 命令：`python skills/impact/scripts/impact_validate.py`\n- 结果：21 passed, 0 failed, 0 warnings\n"
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

    def test_missing_section_fails(self):
        """V18: Missing 最近验证 section should FAIL (not WARN)."""
        td, rd = _make_repo()
        # Write _active-state.md WITHOUT 最近验证 section — bypass helper auto-append
        with open(os.path.join(rd, "_active-state.md"), "w", encoding="utf-8") as f:
            f.write("""# Active State

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
""")
        code, out = _run_validator(td, rd)
        v18 = _v18_lines(out)
        self.assertEqual(code, 1, f"Missing 最近验证 section should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing" in l.lower() for l in v18), f"Expected missing section FAIL, got: {v18}")


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

    def test_declared_no_map_but_repo_map_exists_fails(self):
        """V22 must locate the project map from --repo-root, not req_dir depth."""
        ctx = (
            "# Context Pack\n\n"
            "## 1. 变更意图\n\n"
            "- 项目地图状态：无地图\n"
        )
        td, rd = _make_repo(context_pack=ctx)
        map_dir = os.path.join(td, "change-impact")
        os.makedirs(map_dir, exist_ok=True)
        with open(os.path.join(map_dir, "_project-map.md"), "w", encoding="utf-8") as f:
            f.write("# Existing project map\n")

        code, out = _run_validator(td, rd)
        v22 = _v22_lines(out)
        self.assertEqual(code, 1, f"Physical map contradicting no-map status should FAIL, got {code}\n{out}")
        self.assertTrue(any("physically exists" in l for l in v22), f"Expected V22 physical-map FAIL, got: {v22}")


# ===========================================================================
# Regression tests for round-2 fixes
# ===========================================================================


class TestV20StepNumberPrecision(unittest.TestCase):
    """V20: Step 1 must not match Step 10 via substring."""

    def test_step1_does_not_match_step10_success(self):
        """Step 10 success must not make an unconfirmed Step 1 inconsistent."""
        td, rd = _make_repo()
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改文案

- 确认类型：改代码
- 操作对象：`src/views/dashboard.tsx`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改展示文案
- 用户确认：未确认

## [2026-07-03 19:00:00] Step 10: 补充修改

- 确认类型：改代码
- 操作对象：`src/routes/sidebar.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改侧边栏
- 用户确认：确认 Step 10
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
- 上次提示 Step：Step 10
- 上次确认 Step：Step 10
- 上次完成 Step：Step 10
- V1-only 计数：2

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Step 10 | 成功 | `src/routes/sidebar.ts` | 已确认 | V1 | |

## 恢复备注

- 无
""",
        )
        code, out = _run_validator(td, rd)
        v20 = _v20_lines(out)
        self.assertFalse(
            any("inconsistent" in l.lower() for l in v20),
            f"Step 1 must not inherit Step 10's status: {v20}\n{out}",
        )
        self.assertTrue(
            any("All Steps have" in l for l in v20),
            f"Expected V20 PASS when only Step 10 is terminal, got: {v20}\nexit={code}"
        )


class TestBootstrapWriteFailure(unittest.TestCase):
    """Bootstrap mode: write failure should exit 1."""

    def test_bootstrap_missing_section_exits_nonzero(self):
        """If _active-state.md has no 最近验证 section, bootstrap should exit 1."""
        td, rd = _make_repo()
        # Write _active-state.md WITHOUT 最近验证 section — bypass helper auto-append
        with open(os.path.join(rd, "_active-state.md"), "w", encoding="utf-8") as f:
            f.write("""# Active State

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
""")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), rd, "--repo-root", td, "--bootstrap"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(r.returncode, 1, f"Bootstrap with missing section should exit 1, got {r.returncode}\n{r.stdout}")
        self.assertIn("cannot write result", r.stdout)


class TestGitBaselineDeletion(unittest.TestCase):
    """Git baseline: deleted untracked files should be detected by V15."""

    def test_deleted_untracked_file_detected(self):
        """If a source file existed at baseline but was deleted, V15 should see it."""
        import json
        import hashlib
        import subprocess

        td = tempfile.mkdtemp()
        req_dir = os.path.join(td, "req")
        os.makedirs(req_dir)

        # Initialize a git repo so git status works
        subprocess.run(["git", "init"], cwd=td, capture_output=True, timeout=10)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=td, capture_output=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=td, capture_output=True)

        # Create and commit a source file
        src_dir = os.path.join(td, "src")
        os.makedirs(src_dir)
        src_file = os.path.join(src_dir, "pre.py")
        original_content = b"print('hello')"
        with open(src_file, "wb") as f:
            f.write(original_content)
        subprocess.run(["git", "add", "."], cwd=td, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=td, capture_output=True)

        # Create baseline with the file's hash
        baseline = {"src/pre.py": hashlib.sha256(original_content).hexdigest()}
        with open(os.path.join(req_dir, ".git-baseline.json"), "w", encoding="utf-8") as f:
            json.dump(baseline, f)

        # Now delete the file and commit the deletion
        os.remove(src_file)
        subprocess.run(["git", "add", "-A"], cwd=td, capture_output=True)
        subprocess.run(["git", "commit", "-m", "delete"], cwd=td, capture_output=True)

        # Call _changed_source_paths directly
        script_path = Path(SCRIPT)
        sys.path.insert(0, str(script_path.parent))
        try:
            from impact_validate import _changed_source_paths
            changed = _changed_source_paths(td, Path(req_dir))
            self.assertIn("src/pre.py", changed, f"Deleted file should be in changed paths, got: {changed}")
        finally:
            sys.path.pop(0)


# ===========================================================================
# V23 Tests: Extra structure & assumptions
# ===========================================================================


def _v23_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V23:" in l]


def _write_design(req_dir: str, content: str):
    """Write 020-design.md into req_dir."""
    with open(os.path.join(req_dir, "020-design.md"), "w", encoding="utf-8") as f:
        f.write(content)


class TestV23NoExtraStructure(unittest.TestCase):
    """V23: Design with '无额外结构' should pass."""

    def test_no_extra_structure_passes(self):
        td, rd = _make_repo()
        # _make_repo already writes §5.1 with 无额外结构
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 0, f"Expected exit 0, got {code}\n{out}")
        self.assertTrue(any("无额外结构" in l for l in v23), f"Expected V23 PASS, got: {v23}")


class TestV23MissingSection(unittest.TestCase):
    """V23: Missing §5.1 section in full mode should FAIL."""

    def test_missing_section_fails(self):
        td, rd = _make_repo()
        rows = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"# Design\n\n## 6. 全局影响检查\n\n| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |\n|---|------|----------|----------|-------------|\n{rows}\n")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Missing §5.1 should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing §5.1" in l for l in v23), f"Expected V23 FAIL, got: {v23}")


class TestV23VagueEvidence(unittest.TestCase):
    """V23: Evidence using '扩展性' or '最佳实践' must FAIL."""

    def test_vague_evidence_extensibility_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService.update | 直接更新 | 修改 | 加缓存层 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高频查询场景 | 为了扩展性 | 需要重构数据访问层 |

> **需要你确认的假设**
>
> - [ ] D01：缓存层——扩展性场景无实际依据

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Vague evidence '扩展性' should FAIL, got {code}\n{out}")
        self.assertTrue(any("vague justifications" in l for l in v23), f"Expected V23 vague-evidence FAIL, got: {v23}")

    def test_vague_evidence_best_practice_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService.update | 直接更新 | 修改 | 加 Repository 抽象 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | Repository 抽象层 | 统一数据访问 | 最佳实践 | 需要重构全部 Service |

> **需要你确认的假设**
>
> - [ ] D01：Repository 抽象——最佳实践无实际依据

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Vague evidence '最佳实践' should FAIL, got {code}\n{out}")
        self.assertTrue(any("vague justifications" in l for l in v23), f"Expected V23 vague-evidence FAIL, got: {v23}")


class TestV23UnconfirmedNotListed(unittest.TestCase):
    """V23: Unconfirmed assumptions not in confirmation list must FAIL."""

    def test_unconfirmed_not_listed_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 分布式锁 | 两个客服同时修改同一订单 | 无依据，属于假设 | 加版本字段和冲突判断 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Unconfirmed not listed should FAIL, got {code}\n{out}")
        self.assertTrue(any("no" in l.lower() and "需要你确认的假设" in l for l in v23), f"Expected V23 unconfirmed-not-listed FAIL, got: {v23}")


class TestV23UnconfirmedWithListWarns(unittest.TestCase):
    """V23: Unconfirmed assumptions listed in confirmation list should WARN (Phase 4)."""

    def test_unconfirmed_listed_warns_in_phase4(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 分布式锁 | 两个客服同时修改同一订单 | 无依据，属于假设 | 加版本字段和冲突判断 |

> **需要你确认的假设**
>
> - [ ] D01：分布式锁——并发修改场景无实际依据

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        # Should WARN (not FAIL) since no preflight executable and no source steps
        self.assertEqual(code, 0, f"V23 WARN should not cause FAIL exit, got {code}\n{out}")
        self.assertTrue(any("pending user confirmation" in l for l in v23), f"Expected V23 WARN, got: {v23}")
        self.assertFalse(any("unresolved" in l.lower() for l in v23), f"Should not FAIL in Phase 4, got: {v23}")


class TestV23UnconfirmedAtExecutionFails(unittest.TestCase):
    """V23: Unconfirmed assumptions at execution stage should FAIL."""

    def test_unconfirmed_with_preflight_executable_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 分布式锁 | 两个客服同时修改同一订单 | 无依据，属于假设 | 加版本字段和冲突判断 |

> **需要你确认的假设**
>
> - [ ] D01：分布式锁——并发修改场景无实际依据

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        # Write preflight declaring executable
        with open(os.path.join(rd, "060-preflight.md"), "w", encoding="utf-8") as f:
            f.write("# Preflight\n\n## 结论\n\n- 是否允许进入执行阶段：是\n")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Unconfirmed at execution should FAIL, got {code}\n{out}")
        self.assertTrue(any("unresolved" in l.lower() for l in v23), f"Expected V23 execution FAIL, got: {v23}")


class TestV23ConfirmedEvidencePasses(unittest.TestCase):
    """V23: Extra structure with concrete code-location evidence should PASS."""

    def test_concrete_evidence_passes(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 乐观锁 | 两个用户同时修改同一条记录 | `src/services/user.service.ts:45` 存在无锁并发更新 | 加 version 字段和冲突判断 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 0, f"Concrete evidence should PASS, got {code}\n{out}")
        self.assertTrue(any("concrete evidence" in l for l in v23), f"Expected V23 PASS, got: {v23}")


class TestV23NonWhitelistEvidenceFails(unittest.TestCase):
    """V23: Evidence that doesn't match any whitelist pattern must FAIL.

    This is the core improvement over the old blacklist-only approach.
    "模型判断确有必要" has no vague words but isn't a recognized evidence type.
    """

    def test_model_judgment_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 查询量大时优化响应时间 | 模型判断确有必要 | 加缓存中间件和失效逻辑 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Non-whitelist evidence should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("does not match any recognized type" in l for l in v23),
            f"Expected V23 non-whitelist FAIL, got: {v23}",
        )

    def test_plain_text_fails(self):
        """Evidence without code location, quote, or test result must FAIL."""
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 重试机制 | 网络不稳定时自动重试 | 根据经验需要 | 加重试队列和退避策略 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Non-whitelist evidence should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("does not match any recognized type" in l for l in v23),
            f"Expected V23 non-whitelist FAIL, got: {v23}",
        )


class TestV23QuoteEvidencePasses(unittest.TestCase):
    """V23: Evidence that is a user quote (in quotes) should PASS."""

    def test_quote_evidence_passes(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 消息队列 | 高峰期请求堆积 | 用户原话「高峰期订单量会翻 3 倍」 | 加队列和消费者池 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 0, f"Quote evidence should PASS, got {code}\n{out}")
        self.assertTrue(any("concrete evidence" in l for l in v23), f"Expected V23 PASS, got: {v23}")


class TestV23TestResultEvidencePasses(unittest.TestCase):
    """V23: Evidence that is a query/test result should PASS."""

    def test_test_result_evidence_passes(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 读写分离 | 主库负载过高 | npm test 26 passed, 主库 QPS 峰值 5000 | 加从库路由和读写分离代理 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 0, f"Test result evidence should PASS, got {code}\n{out}")
        self.assertTrue(any("concrete evidence" in l for l in v23), f"Expected V23 PASS, got: {v23}")


class TestV23LightModeNotChecked(unittest.TestCase):
    """V23: Light mode should not be checked."""

    def test_light_mode_not_checked(self):
        td = tempfile.mkdtemp()
        req_dir = os.path.join(td, "req")
        os.makedirs(req_dir)
        # Light mode files
        with open(os.path.join(req_dir, "000-context-pack.md"), "w", encoding="utf-8") as f:
            f.write("# Context Pack\n\n## 1. 变更意图\n\n- 用户原话：test\n- 项目地图状态：无地图\n")
        with open(os.path.join(req_dir, "040-light.md"), "w", encoding="utf-8") as f:
            f.write("# Light\n\n## 关键链路深度检查\n\n- 不涉及\n")
        with open(os.path.join(req_dir, "_active-state.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Active State\n\n## 状态头\n\n- 当前阶段：Phase 4\n- 模式：light\n"
                "- Phase 3 状态：快速通道跳过\n- Phase 3.5 定级：快速通道跳过\n"
                "- 是否需要确认：false\n- 待执行 Step：none\n"
                "- 上次提示 Step：none\n- 上次确认 Step：none\n- 上次完成 Step：none\n"
                "- V1-only 计数：0\n\n## Step 台账\n\n"
                "| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |\n| --- | --- | --- | --- | --- | --- |\n\n"
                "## 恢复备注\n\n- 无\n\n## 最近验证\n\n"
                "- 命令：`python skills/impact/scripts/impact_validate.py`\n"
                "- 结果：15 passed, 0 failed, 0 warnings\n"
            )
        code, out = _run_validator(td, req_dir)
        v23 = _v23_lines(out)
        # V23 should produce no output in light mode
        self.assertEqual(len(v23), 0, f"V23 should not run in light mode, got: {v23}")


# ===========================================================================
# V24 Tests: Design→implementation mapping
# ===========================================================================


def _v24_lines(stdout: str) -> list[str]:
    return [l for l in stdout.splitlines() if "V24:" in l]


def _make_design_with_items(dxx_items: list[str], extra_section: str = "无额外结构") -> str:
    """Create a 020-design.md with given Dxx items in §3."""
    rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
    code_rows = "\n".join([
        f"| {dxx} | UserService.update | 直接更新 | 修改 | 加字段 | 全局 |"
        for dxx in dxx_items
    ])
    return f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
{code_rows}

## 5.1 额外结构与假设

{extra_section}

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
"""


def _make_impl_with_mapping(mapping_rows: str, steps: str = "") -> str:
    """Create a 030-implementation.md with §2.2 mapping table."""
    return f"""# Implementation

## 2.2 设计到实施的对照

| 设计项（来自 020） | 对应 Step | 覆盖状态 |
|---|---|---|
{mapping_rows}

## 3. 执行步骤

{steps}
"""


class TestV24D01ButNoChanges(unittest.TestCase):
    """V24: 020 has D01 but 030 says No changes → FAIL."""

    def test_d01_with_no_changes_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, "# Implementation\n\nNo changes.\n")
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"D01 with No changes should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing from 030" in l for l in v24), f"Expected V24 FAIL, got: {v24}")


class TestV24UnknownDxx(unittest.TestCase):
    """V24: 030 references D99 not in 020 → FAIL."""

    def test_unknown_dxx_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **设计项**：D99
- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Unknown D99 should FAIL, got {code}\n{out}")
        self.assertTrue(any("not in 020" in l for l in v24), f"Expected V24 unknown-ref FAIL, got: {v24}")


class TestV24SourceStepWithoutDesign(unittest.TestCase):
    """V24: Source Step without 设计项 → FAIL."""

    def test_source_step_no_design_item_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Source Step without 设计项 should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing" in l and "设计项" in l for l in v24), f"Expected V24 FAIL, got: {v24}")


class TestV24ExecutionInconsistency(unittest.TestCase):
    """V24: 090 design items inconsistent with 030 → FAIL."""

    def test_090_inconsistent_with_030_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **设计项**：D01
- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改代码

- 确认类型：改代码
- 设计项：D02
- 操作对象：`src/services/user.service.ts`; `090-execution-record.md`; `_active-state.md`
- 操作内容：修改代码
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"090 inconsistent with 030 should FAIL, got {code}\n{out}")
        self.assertTrue(any("inconsistent" in l.lower() for l in v24), f"Expected V24 inconsistent FAIL, got: {v24}")


class TestV24NormalFullPasses(unittest.TestCase):
    """V24: Normal Full design with proper mapping passes."""

    def test_normal_full_passes(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **设计项**：D01
- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 0, f"Normal Full should pass, got {code}\n{out}")
        self.assertTrue(any("mapped in 030" in l for l in v24), f"Expected V24 PASS, got: {v24}")


class TestV24LightModeNotChecked(unittest.TestCase):
    """V24: Light mode should not be checked."""

    def test_light_mode_not_checked(self):
        td = tempfile.mkdtemp()
        req_dir = os.path.join(td, "req")
        os.makedirs(req_dir)
        with open(os.path.join(req_dir, "000-context-pack.md"), "w", encoding="utf-8") as f:
            f.write("# Context Pack\n\n## 1. 变更意图\n\n- 用户原话：test\n- 项目地图状态：无地图\n")
        with open(os.path.join(req_dir, "040-light.md"), "w", encoding="utf-8") as f:
            f.write("# Light\n\n## 关键链路深度检查\n\n- 不涉及\n")
        with open(os.path.join(req_dir, "_active-state.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Active State\n\n## 状态头\n\n- 当前阶段：Phase 4\n- 模式：light\n"
                "- Phase 3 状态：快速通道跳过\n- Phase 3.5 定级：快速通道跳过\n"
                "- 是否需要确认：false\n- 待执行 Step：none\n"
                "- 上次提示 Step：none\n- 上次确认 Step：none\n- 上次完成 Step：none\n"
                "- V1-only 计数：0\n\n## Step 台账\n\n"
                "| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |\n| --- | --- | --- | --- | --- | --- |\n\n"
                "## 恢复备注\n\n- 无\n\n## 最近验证\n\n"
                "- 命令：`python skills/impact/scripts/impact_validate.py`\n"
                "- 结果：15 passed, 0 failed, 0 warnings\n"
            )
        code, out = _run_validator(td, req_dir)
        v24 = _v24_lines(out)
        self.assertEqual(len(v24), 0, f"V24 should not run in light mode, got: {v24}")


# ===========================================================================
# V23 Bypass path tests
# ===========================================================================


class TestV23TemplateCommentBypass(unittest.TestCase):
    """V23: '无额外结构' in HTML comment should NOT cause PASS when table has bad content."""

    def test_comment_no_extra_but_table_has_vague_evidence_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 直接更新 | 修改 | 加缓存 | 全局 |

## 5.1 额外结构与假设

<!-- 没有额外结构时写"无额外结构"。 -->

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高频查询 | 为了扩展性 | 重构数据层 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Should FAIL (vague evidence in table), got {code}\n{out}")
        self.assertTrue(any("vague" in l.lower() for l in v23), f"Expected vague FAIL, got: {v23}")


class TestV23EmptyTableFails(unittest.TestCase):
    """V23: Empty §5.1 table (no data rows) must FAIL, not PASS."""

    def test_empty_table_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| — | — | — | — | — |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Empty table should FAIL, got {code}\n{out}")
        self.assertTrue(any("empty" in l.lower() for l in v23), f"Expected empty-table FAIL, got: {v23}")


class TestV23ExpandedVagueWords(unittest.TestCase):
    """V23: Expanded vague words like '为了性能' must FAIL."""

    def test_for_performance_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 无缓存 | 修改 | 加缓存 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高频查询慢 | 为了性能 | 重构数据层 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"'为了性能' should FAIL, got {code}\n{out}")
        self.assertTrue(any("vague" in l.lower() for l in v23), f"Expected vague FAIL, got: {v23}")


class TestV23VagueScenarioColumn(unittest.TestCase):
    """V23: Vague words in '为了解决什么情况' column must FAIL."""

    def test_vague_scenario_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 无锁 | 修改 | 加锁 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 分布式锁 | 为了安全性 | `src/UserService.java:45` | 加版本字段 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Vague scenario should FAIL, got {code}\n{out}")
        self.assertTrue(any("vague" in l.lower() for l in v23), f"Expected vague FAIL, got: {v23}")


class TestV23EmptyFieldFails(unittest.TestCase):
    """V23: Empty/placeholder field in table row must FAIL."""

    def test_empty_cost_field_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 无锁 | 修改 | 加锁 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 分布式锁 | 并发修改 | `src/UserService.java:45` | [待填] |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Empty field should FAIL, got {code}\n{out}")
        self.assertTrue(any("empty" in l.lower() or "placeholder" in l.lower() for l in v23), f"Expected empty-field FAIL, got: {v23}")


class TestV23InvalidDesignRef(unittest.TestCase):
    """V23: 关联设计项 references Dxx not in §3 must FAIL."""

    def test_invalid_design_ref_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 无锁 | 修改 | 加锁 | 全局 |

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D99 | 分布式锁 | 并发修改 | `src/UserService.java:45` | 加版本字段 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Invalid design ref should FAIL, got {code}\n{out}")
        self.assertTrue(any("not in §3" in l for l in v23), f"Expected invalid-ref FAIL, got: {v23}")


# ===========================================================================
# V24 Bypass path tests
# ===========================================================================


class TestV24NonExistentStep(unittest.TestCase):
    """V24: Mapping references Step 99 that doesn't exist in §3 → FAIL."""

    def test_non_existent_step_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 99 | ✅ 已覆盖 |",
            ""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Non-existent Step 99 should FAIL, got {code}\n{out}")
        self.assertTrue(any("not in §3" in l for l in v24), f"Expected non-existent-step FAIL, got: {v24}")


class TestV24NoDxxButSourceSteps(unittest.TestCase):
    """V24: 020 has no Dxx but 030 has source Steps → FAIL."""

    def test_no_dxx_with_source_steps_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        # Design with no §3 section
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

无额外结构

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        _write_impl(rd, """# Implementation

## 3. 执行步骤

### Step 1: 修改代码

- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
""")
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"No Dxx but source Steps should FAIL, got {code}\n{out}")
        self.assertTrue(any("no design items" in l.lower() and "source" in l.lower() for l in v24), f"Expected no-Dxx FAIL, got: {v24}")


class TestV24FlowStepWithDML(unittest.TestCase):
    """V24: Step marked '流程步骤' but has DML content → FAIL."""

    def test_flow_step_with_dml_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **设计项**：D01
- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码

### Step 2: 运行回填脚本

- **设计项**：流程步骤，不改业务对象
- **维度**：DML
- **文件**：`050-validation/001-backfill.sql`
- **操作**：执行回填 SQL
- **确认类型**：DML
"""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Flow step with DML should FAIL, got {code}\n{out}")
        self.assertTrue(any("Step 2" in l and "missing" in l.lower() for l in v24), f"Expected DML-bypass FAIL, got: {v24}")


class TestV24Missing090DesignItem(unittest.TestCase):
    """V24: 090 Step missing 设计项 field when 030 has it → FAIL."""

    def test_090_missing_design_item_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |",
            """### Step 1: 修改代码

- **设计项**：D01
- **维度**：代码
- **文件**：`src/services/user.service.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        _write_preflight(rd)
        _write_execution_record(
            rd,
            """# Execution Record

## [2026-07-03 18:43:45] Step 1: 修改代码

- 确认类型：改代码
- 操作对象：`src/services/user.service.ts`
- 操作内容：修改代码
- 用户确认：确认 Step 1
""",
        )
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"090 missing 设计项 should FAIL, got {code}\n{out}")
        self.assertTrue(any("missing" in l.lower() and "设计项" in l for l in v24), f"Expected 090-missing FAIL, got: {v24}")


class TestV24MappingVsStepInconsistency(unittest.TestCase):
    """V24: Mapping says D01→Step1, but Step1 references D02 → FAIL."""

    def test_mapping_step_inconsistency_fails(self):
        td, rd = _make_repo()
        _write_design(rd, _make_design_with_items(["D01", "D02"]))
        _write_impl(rd, _make_impl_with_mapping(
            "| D01 | Step 1 | ✅ 已覆盖 |\n| D02 | Step 2 | ✅ 已覆盖 |",
            """### Step 1: 修改代码A

- **设计项**：D02
- **维度**：代码
- **文件**：`src/services/a.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码

### Step 2: 修改代码B

- **设计项**：D01
- **维度**：代码
- **文件**：`src/services/b.ts`
- **操作**：
  ```typescript
  // code
  ```
- **确认类型**：改代码
"""
        ))
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Mapping inconsistency should FAIL, got {code}\n{out}")
        self.assertTrue(any("inconsistent" in l.lower() for l in v24), f"Expected inconsistency FAIL, got: {v24}")


class TestV24DuplicateDxx(unittest.TestCase):
    """V24: 020 has duplicate D01 in §3 tables → FAIL."""

    def test_duplicate_dxx_fails(self):
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 3. 变更明细

### 数据库（如涉及）

| 设计项 | 对象 | 类型 | 当前定义 | 变更操作 | 目标定义 | 影响说明 |
|--------|------|------|----------|----------|----------|----------|
| D01 | users.email | 字段 | VARCHAR(50) | ALTER | VARCHAR(100) | 全局 |

### 代码（如涉及）

| 设计项 | 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|--------|------|----------|----------|----------|----------|
| D01 | UserService | 无校验 | 修改 | 加校验 | 全局 |

## 5.1 额外结构与假设

无额外结构

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        _write_impl(rd, "# Implementation\n\nNo changes.\n")
        code, out = _run_validator(td, rd)
        v24 = _v24_lines(out)
        self.assertEqual(code, 1, f"Duplicate D01 should FAIL, got {code}\n{out}")
        self.assertTrue(any("duplicate" in l.lower() for l in v24), f"Expected duplicate FAIL, got: {v24}")


class TestV23WhitelistHardening(unittest.TestCase):
    """V23: expanded evidence whitelist + hardened 无额外结构 declaration."""

    def _design_with_evidence(self, evidence: str) -> str:
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        return f"""# Design

## 5.1 额外结构与假设

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 校验层 | 请求字段会缺失 | {evidence} | 加校验注解 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
"""

    def _assert_evidence(self, evidence: str, expect_pass: bool):
        td, rd = _make_repo()
        _write_design(rd, self._design_with_evidence(evidence))
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        if expect_pass:
            self.assertEqual(code, 0, f"Expected PASS for {evidence!r}, got {code}\n{out}")
        else:
            self.assertEqual(code, 1, f"Expected FAIL for {evidence!r}, got {code}\n{out}")
            self.assertTrue(
                any("does not match any recognized type" in l for l in v23),
                f"Expected non-whitelist FAIL for {evidence!r}, got: {v23}",
            )

    def test_bare_filename_evidence_passes(self):
        """裸文件名（无路径、无行号）是合法代码位置证据。"""
        self._assert_evidence("pom.xml 中已有 spring-boot-starter-validation 依赖", True)

    def test_chinese_line_ref_evidence_passes(self):
        """「文件名 第 N 行」中文行号引用是合法代码位置证据。"""
        self._assert_evidence("SysUserController.java 第 45 行已有该字段", True)

    def test_curly_quote_evidence_passes(self):
        """弯引号包裹的用户原话是合法证据。"""
        self._assert_evidence("用户答复“高峰期订单量会翻 3 倍”", True)

    def test_db_identifier_evidence_passes(self):
        """snake_case 数据库标识符是合法代码位置证据。"""
        self._assert_evidence("数据库 sys_config 表已有 config_type 字段", True)

    def test_keyword_substring_no_longer_passes(self):
        """英文单词内嵌关键词（account 含 COUNT、纯 rows 推测）不再混过白名单。"""
        self._assert_evidence("account 表后续要支持多租户", False)
        self._assert_evidence("以后数据 rows 会增长", False)

    def test_quoted_vague_word_evidence_passes(self):
        """用户原话里合法出现"为了性能"这类词，不应被黑名单误杀。"""
        self._assert_evidence("用户原话「为了性能，必须上缓存」", True)


class TestV23DeclarationHardening(unittest.TestCase):
    """V23: 无额外结构 declaration must be standalone; comments don't count."""

    def test_commented_out_table_fails(self):
        """整张表包在 HTML 注释里（渲染为空节）不能通过 V23。"""
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

<!--
| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高峰期查询慢 | 用户原话「高峰期订单量会翻 3 倍」 | 加缓存中间件 |
-->

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        self.assertEqual(code, 1, f"Commented-out table should FAIL, got {code}\n{out}")

    def test_declaration_with_rows_contradiction_fails(self):
        """声明"无额外结构"但表格仍有数据行 → 矛盾 FAIL。"""
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

无额外结构

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高峰期查询慢 | 用户原话「高峰期订单量会翻 3 倍」 | 加缓存中间件 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Contradiction should FAIL, got {code}\n{out}")
        self.assertTrue(
            any("still has" in l for l in v23),
            f"Expected contradiction FAIL, got: {v23}",
        )

    def test_no_extra_substring_not_declaration(self):
        """"并非无额外结构"这类子串不构成声明，表格照常检查。"""
        td, rd = _make_repo()
        rows_19 = "\n".join([f"| {i+1} | dim{i+1} | ☐ | check | 不涉及 |" for i in range(19)])
        _write_design(rd, f"""# Design

## 5.1 额外结构与假设

下面这些结构并非无额外结构：

| 关联设计项 | 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再补的成本 |
|---|---|---|---|---|
| D01 | 缓存层 | 高峰期查询慢 | 模型判断确有必要 | 加缓存中间件 |

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
{rows_19}
""")
        code, out = _run_validator(td, rd)
        v23 = _v23_lines(out)
        self.assertEqual(code, 1, f"Substring must not act as declaration, got {code}\n{out}")
        self.assertTrue(
            any("does not match any recognized type" in l for l in v23),
            f"Expected non-whitelist FAIL (not early PASS), got: {v23}",
        )


if __name__ == "__main__":
    unittest.main()
