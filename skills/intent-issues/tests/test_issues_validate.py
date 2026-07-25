#!/usr/bin/env python3
"""Behavior tests for issues_validate.py.

Run:
  python -m pytest skills/intent-issues/tests/test_issues_validate.py -v
  python skills/intent-issues/tests/test_issues_validate.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
INTENT_FIXTURE = SKILL_DIR.parent / "intent-anchor" / "tests" / "fixtures" / "valid-intent.md"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from issues_validate import validate, main
finally:
    sys.path.pop(0)


_ARCH_CONTENT = (
    "# 架构 - 测试\n"
    "\n"
    "## 1. 架构概览\n\n"
    "测试用架构。\n\n"
    "## 2. 模块与边界\n\n"
    "| 模块 | 职责 | 服务的能力 | 依赖模块 |\n"
    "|---|---|---|---|\n"
    "| 记录生成器 | 从任务状态生成交接记录内容 | C01 | 无 |\n"
    "| 文件存储 | 读写交接记录 Markdown 文件 | C01 | 无 |\n\n"
    "## 3. 技术选型\n\n"
    "| 决策项 | 选了什么 | 服务的能力 | 为什么不选另一个 | 以后再改的成本 |\n"
    "|---|---|---|---|---|\n"
    "| 文件格式 | Markdown | C01 | JSON 不便阅读 | 便宜 |\n\n"
    "## 4. 关键数据流\n\n"
    "| 路径 ID | 数据从哪来 | 经过模块 | 存到哪 |\n"
    "|---|---|---|---|\n"
    "| P01 | 当前会话任务状态 | 记录生成器 → 文件存储 | handoff/ 目录 |\n\n"
    "## 5. 额外结构与假设\n\n"
    "无额外结构\n\n"
    "### 需要你确认的假设\n\n"
    "无\n\n"
    "## 6. 重要决策的详细说明\n\n"
    "无\n"
)


def _issues_content() -> str:
    return (FIXTURE_DIR / "valid-issues.md").read_text(encoding="utf-8")


def _intent_content() -> str:
    return INTENT_FIXTURE.read_text(encoding="utf-8")


def _result(issues: str, intent: str, check_id: str, arch: str = _ARCH_CONTENT) -> tuple[str, str, str]:
    matches = [item for item in validate(issues, intent, "", arch) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_issues_passes_all_checks(self):
        results = validate(_issues_content(), _intent_content(), "", _ARCH_CONTENT)
        self.assertEqual(11, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestRequiredSubsections(unittest.TestCase):
    def test_missing_what_to_build_fails(self):
        content = _issues_content().replace("### What to build", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("What to build", result[2])

    def test_missing_acceptance_criteria_fails(self):
        content = _issues_content().replace("### Acceptance criteria", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Acceptance criteria", result[2])

    def test_missing_blocked_by_fails(self):
        content = _issues_content().replace("### Blocked by", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Blocked by", result[2])

    def test_missing_user_stories_fails(self):
        content = _issues_content().replace("### User stories covered", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("User stories covered", result[2])

    def test_no_issues_fails(self):
        content = _issues_content().replace("## Issue 1:", "## X:")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])

    def test_empty_file_fails(self):
        results = validate("", _intent_content())
        self.assertEqual("FAIL", results[0][1])


class TestPathCoverage(unittest.TestCase):
    def test_missing_path_in_criteria_fails(self):
        content = _issues_content().replace("[P01]", "")
        result = _result(content, _intent_content(), "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("P01", result[2])

    def test_all_paths_covered_passes(self):
        result = _result(_issues_content(), _intent_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestCapabilityCoverage(unittest.TestCase):
    def test_missing_capability_in_stories_fails(self):
        content = _issues_content().replace("[C01]", "")
        result = _result(content, _intent_content(), "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("C01", result[2])

    def test_all_capabilities_covered_passes(self):
        result = _result(_issues_content(), _intent_content(), "V4")
        self.assertEqual("PASS", result[1])


class TestCoverageVerification(unittest.TestCase):
    def test_missing_coverage_section_fails(self):
        content = _issues_content().replace("## Coverage Verification", "## X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Coverage Verification", result[2])

    def test_missing_path_coverage_subsection_fails(self):
        content = _issues_content().replace("### 验收路径覆盖", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验收路径覆盖", result[2])

    def test_missing_capability_coverage_subsection_fails(self):
        content = _issues_content().replace("### 保留能力覆盖", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("保留能力覆盖", result[2])

    def test_missing_new_capability_subsection_fails(self):
        content = _issues_content().replace("### 新增能力", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("新增能力", result[2])

    def test_valid_coverage_passes(self):
        result = _result(_issues_content(), _intent_content(), "V5")
        self.assertEqual("PASS", result[1])


class TestDesignStandardsPropagation(unittest.TestCase):
    """V6: INTENT.md 有设计标准时，工单 Acceptance criteria 必须包含"对照"。"""

    _DESIGN_SECTION = (
        "| D01 | 可点原型 | prototype/screens/main.html | 首页和交接记录页 | \"按原型做\" |"
    )

    _DESIGN_IN_CRITERIA = (
        '- [ ] 对照 prototype/screens/main.html 结构一致'
    )

    def test_no_design_standards_passes(self):
        result = _result(_issues_content(), _intent_content(), "V6")
        self.assertEqual("PASS", result[1])
        self.assertIn("不适用", result[2])

    def test_design_standards_propagated_passes(self):
        intent = _intent_content().replace(
            '无设计标准素材。用户明确确认：“没有设计素材，不作为验收基线”。',
            self._DESIGN_SECTION,
        )
        # 替换两处（第 12 节和 S6 复核记录）
        intent = intent.replace(
            '无设计标准素材。用户明确确认：“没有设计素材，不作为验收基线”。',
            self._DESIGN_SECTION,
        )
        issues = _issues_content().replace(
            '- [ ] And: 记录包含下一步',
            '- [ ] And: 记录包含下一步\n' + self._DESIGN_IN_CRITERIA,
        )
        result = _result(issues, intent, "V6")
        self.assertEqual("PASS", result[1])

    def test_design_standards_not_propagated_fails(self):
        intent = _intent_content().replace(
            '无设计标准素材。用户明确确认：“没有设计素材，不作为验收基线”。',
            self._DESIGN_SECTION,
        )
        intent = intent.replace(
            '无设计标准素材。用户明确确认：“没有设计素材，不作为验收基线”。',
            self._DESIGN_SECTION,
        )
        # 工单不包含"对照"，应 FAIL
        result = _result(_issues_content(), intent, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("对照", result[2])


class TestTerminologyPropagation(unittest.TestCase):
    """V7: INTENT.md 有术语表时，工单必须引用术语表中的术语。"""

    _TERM_SECTION = (
        '| 进度快照 | 会话进度保存文件 | 进度快照 | C01 |'
    )

    _TERM_IN_CRITERIA = (
        '- [ ] 界面文案使用术语表中的“进度快照”'
    )

    def test_no_terminology_passes(self):
        result = _result(_issues_content(), _intent_content(), "V7")
        self.assertEqual("PASS", result[1])
        self.assertIn("不适用", result[2])

    def test_terminology_propagated_passes(self):
        intent = _intent_content().replace(
            '无术语需要翻译。',
            self._TERM_SECTION,
        )
        # 替换两处（第 13 节和 S7 复核记录）
        intent = intent.replace(
            '无术语需要翻译。',
            self._TERM_SECTION,
        )
        issues = _issues_content().replace(
            '- [ ] And: 记录包含下一步',
            '- [ ] And: 记录包含下一步\n' + self._TERM_IN_CRITERIA,
        )
        result = _result(issues, intent, "V7")
        self.assertEqual("PASS", result[1])

    def test_terminology_not_propagated_fails(self):
        intent = _intent_content().replace(
            '无术语需要翻译。',
            self._TERM_SECTION,
        )
        intent = intent.replace(
            '无术语需要翻译。',
            self._TERM_SECTION,
        )
        # 工单不引用任何术语，应 FAIL
        result = _result(_issues_content(), intent, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("术语", result[2])


class TestArchitectureModuleRef(unittest.TestCase):
    """V11: 工单的"涉及模块"必须引用架构文档中定义的模块名。"""

    def test_no_architecture_fails(self):
        """不提供 architecture.md 时 V11 返回 FAIL。"""
        results = validate(_issues_content(), _intent_content())
        v11 = [r for r in results if r[0] == "V11"]
        self.assertEqual(1, len(v11))
        self.assertEqual("FAIL", v11[0][1])
        self.assertIn("必须存在", v11[0][2])

    def test_valid_module_references_passes(self):
        """工单的涉及模块都定义在 architecture.md 中时 V11 返回 PASS。"""
        results = validate(_issues_content(), _intent_content(), "", _ARCH_CONTENT)
        v11 = [r for r in results if r[0] == "V11"]
        self.assertEqual(1, len(v11))
        self.assertEqual("PASS", v11[0][1])

    def test_missing_module_subsection_fails(self):
        """工单缺少涉及模块子节时 V11 返回 FAIL。"""
        issues = _issues_content().replace("### 涉及模块", "### X")
        results = validate(issues, _intent_content(), "", _ARCH_CONTENT)
        v11 = [r for r in results if r[0] == "V11"]
        self.assertEqual(1, len(v11))
        self.assertEqual("FAIL", v11[0][1])
        self.assertIn("涉及模块", v11[0][2])

    def test_undefined_module_fails(self):
        """工单引用了 architecture.md 中未定义的模块时 V11 返回 FAIL。"""
        issues = _issues_content().replace("- 记录生成器", "- 不存在的模块")
        results = validate(issues, _intent_content(), "", _ARCH_CONTENT)
        v11 = [r for r in results if r[0] == "V11"]
        self.assertEqual(1, len(v11))
        self.assertEqual("FAIL", v11[0][1])
        self.assertIn("未定义", v11[0][2])


class TestCLI(unittest.TestCase):
    """CLI 参数变更测试：architecture.md 从可选改为强制。"""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(_ARCH_CONTENT)
        tmp.close()
        cls._arch_path = tmp.name

    @classmethod
    def tearDownClass(cls):
        Path(cls._arch_path).unlink(missing_ok=True)

    def _run_main(self, *args) -> int:
        old = sys.argv
        sys.argv = ["issues_validate.py"] + list(args)
        try:
            return main()
        finally:
            sys.argv = old

    def test_all_args_valid_exit_0(self):
        """参数完整且文件存在时退出 0。"""
        prd = SKILL_DIR.parent / "intent-prd" / "tests" / "fixtures" / "valid-prd.md"
        code = self._run_main(
            str(FIXTURE_DIR / "valid-issues.md"),
            str(INTENT_FIXTURE),
            str(prd),
            self._arch_path,
        )
        self.assertEqual(0, code)

    def test_missing_arch_arg_exit_1(self):
        """缺少 architecture.md 参数时退出 1。"""
        prd = SKILL_DIR.parent / "intent-prd" / "tests" / "fixtures" / "valid-prd.md"
        code = self._run_main(
            str(FIXTURE_DIR / "valid-issues.md"),
            str(INTENT_FIXTURE),
            str(prd),
        )
        self.assertEqual(1, code)

    def test_nonexistent_arch_file_exit_1(self):
        """architecture.md 文件不存在时退出 1。"""
        prd = SKILL_DIR.parent / "intent-prd" / "tests" / "fixtures" / "valid-prd.md"
        code = self._run_main(
            str(FIXTURE_DIR / "valid-issues.md"),
            str(INTENT_FIXTURE),
            str(prd),
            "/nonexistent/path/architecture.md",
        )
        self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
