#!/usr/bin/env python3
"""Behavior tests for design_validate.py.

Run:
  python -m pytest skills/intent-design/tests/test_design_validate.py -v
  python skills/intent-design/tests/test_design_validate.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
INTENT_FIXTURE = SKILL_DIR.parent / "intent-anchor" / "tests" / "fixtures" / "valid-intent.md"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from design_validate import validate
finally:
    sys.path.pop(0)


def _arch_content() -> str:
    return (FIXTURE_DIR / "valid-architecture.md").read_text(encoding="utf-8")


def _design_content() -> str:
    return (FIXTURE_DIR / "valid-design.md").read_text(encoding="utf-8")


def _intent_content() -> str:
    return INTENT_FIXTURE.read_text(encoding="utf-8")


def _result(arch: str, design: str, intent: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(arch, design, intent) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


# ═══════════════════════════════════════════════════════════════════════════
# 有效 fixture 全通过
# ═══════════════════════════════════════════════════════════════════════════


class TestValidFixture(unittest.TestCase):
    def test_valid_files_pass_all_checks(self):
        results = validate(_arch_content(), _design_content(), _intent_content())
        self.assertEqual(15, len(results))
        failed = [(r[0], r[2]) for r in results if r[1] != "PASS"]
        self.assertFalse(failed, f"Unexpected failures: {failed}")


# ═══════════════════════════════════════════════════════════════════════════
# 架构层检查 A1-A8
# ═══════════════════════════════════════════════════════════════════════════


class TestA1NonEmpty(unittest.TestCase):
    def test_empty_architecture_fails(self):
        results = validate("", _design_content(), _intent_content())
        self.assertEqual("FAIL", results[0][1])
        self.assertEqual("A1", results[0][0])
        self.assertEqual(1, len(results))


class TestA2RequiredSections(unittest.TestCase):
    def test_missing_section_fails(self):
        content = _arch_content().replace("## 5. 额外结构与假设", "## X")
        result = _result(content, _design_content(), _intent_content(), "A2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("额外结构与假设", result[2])

    def test_all_sections_present_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A2")
        self.assertEqual("PASS", result[1])


class TestA3CapabilityIDs(unittest.TestCase):
    def test_invalid_capability_id_fails(self):
        content = _arch_content().replace("C01", "C99", 1)
        result = _result(content, _design_content(), _intent_content(), "A3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("C99", result[2])

    def test_valid_capability_ids_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A3")
        self.assertEqual("PASS", result[1])


class TestA4ModuleDependencies(unittest.TestCase):
    def test_undefined_dependency_fails(self):
        content = _arch_content().replace("| 无 |", "| 不存在的模块 |", 1)
        result = _result(content, _design_content(), _intent_content(), "A4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未定义", result[2])

    def test_valid_dependencies_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A4")
        self.assertEqual("PASS", result[1])


class TestA5TechSelection(unittest.TestCase):
    def test_forbidden_word_in_reason_fails(self):
        content = _arch_content().replace(
            "JSON 不便于人直接阅读和编辑，交接记录需要人能快速查看",
            "JSON 不是最佳实践",
        )
        result = _result(content, _design_content(), _intent_content(), "A5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("禁用词", result[2])

    def test_valid_tech_selection_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A5")
        self.assertEqual("PASS", result[1])


class TestA6DataFlow(unittest.TestCase):
    def test_missing_acceptance_path_fails(self):
        content = _arch_content().replace("P01", "P99")
        result = _result(content, _design_content(), _intent_content(), "A6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("P01", result[2])

    def test_undefined_module_in_flow_fails(self):
        content = _arch_content().replace(
            "记录生成器 → 文件存储",
            "记录生成器 → 未知模块",
        )
        result = _result(content, _design_content(), _intent_content(), "A6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未定义", result[2])

    def test_valid_data_flow_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A6")
        self.assertEqual("PASS", result[1])


class TestA7Assumptions(unittest.TestCase):
    def test_forbidden_word_in_scenario_fails(self):
        content = _arch_content().replace(
            "多个项目复用时不冲突",
            "为了扩展性",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("禁用词", result[2])

    def test_no_evidence_item_not_in_summary_fails(self):
        content = _arch_content().replace(
            "用户原话\"放项目根目录\"",
            "无依据，属于假设",
        )
        # 同时删除汇总中的「无」，替换为一个不包含结构名的占位
        content = content.replace("### 需要你确认的假设\n\n无", "### 需要你确认的假设\n\n（空）")
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未出现在", result[2])

    def test_valid_assumptions_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_html_comment_bypass_fails(self):
        """HTML 注释中的"无额外结构"不能跳过假设表检查。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "模型判断确有必要",
        )
        content = content.replace(
            "## 5. 额外结构与假设",
            "## 5. 额外结构与假设\n\n<!-- 无额外结构 -->",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])

    def test_non_evidence_text_fails(self):
        """证据列填不含文件路径或引号的文本应 FAIL。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "模型判断确有必要",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不合规", result[2])

    def test_code_location_evidence_passes(self):
        """证据列填代码位置（文件路径:行号）应 PASS。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "src/handoff.js:42",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_no_extra_structure_as_text_passes(self):
        """假设表为空、正文写"无额外结构"时 A7 应 PASS。"""
        content = _arch_content().replace(
            "| handoff/ 独立目录 | 多个项目复用时不冲突 | 用户原话\"放项目根目录\" | 便宜（改路径配置即可） |",
            "无额外结构",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_bare_filename_evidence_passes(self):
        """裸文件名（无路径、无行号）是合法代码位置证据。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "package.json 已有 fs-extra 依赖",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_curly_quote_evidence_passes(self):
        """弯引号包裹的用户原话是合法证据。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "用户原话“放项目根目录”",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_no_evidence_with_trailing_period_counts_as_unconfirmed(self):
        """"无依据，属于假设。"（带句尾标点）应按无依据项处理，不误判为不合规。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "无依据，属于假设。",
        )
        content = content.replace(
            "### 需要你确认的假设\n\n无",
            "### 需要你确认的假设\n\n1. handoff/ 独立目录：多项目复用会发生吗？",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_quoted_forbidden_word_evidence_passes(self):
        """用户原话里合法出现"为了性能"这类词，不应被禁用词误杀。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            '用户原话"为了性能，必须放根目录"',
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("PASS", result[1])

    def test_negated_no_extra_is_not_declaration(self):
        """"并非无额外结构"这类子串不构成声明，表格照常检查。"""
        content = _arch_content().replace(
            '用户原话"放项目根目录"',
            "模型判断确有必要",
        )
        content = content.replace(
            "## 5. 额外结构与假设",
            "## 5. 额外结构与假设\n\n下面这些结构并非无额外结构：",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不合规", result[2])

    def test_declaration_with_rows_contradiction_fails(self):
        """声明"无额外结构"但表格仍有数据行 → 矛盾 FAIL。"""
        content = _arch_content().replace(
            "## 5. 额外结构与假设",
            "## 5. 额外结构与假设\n\n无额外结构",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("矛盾", result[2])

    def test_commented_out_table_fails(self):
        """整张表包在 HTML 注释里（渲染为空节）不能通过 A7。"""
        content = _arch_content().replace(
            "| 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再改的成本 |",
            "<!--\n| 加了什么结构 | 为了解决什么情况 | 这种情况的依据 | 以后再改的成本 |",
        )
        content = content.replace(
            "| handoff/ 独立目录 | 多个项目复用时不冲突 | 用户原话\"放项目根目录\" | 便宜（改路径配置即可） |",
            "| handoff/ 独立目录 | 多个项目复用时不冲突 | 用户原话\"放项目根目录\" | 便宜（改路径配置即可） |\n-->",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])


class TestModuleNameWithSpace(unittest.TestCase):
    def test_spaced_module_name_not_split(self):
        """中英混合含空格的模块名（如 "CLI 入口"）不应被拆散误报未定义（冒烟 B-1）。"""
        arch = _arch_content().replace("记录生成器", "CLI 入口")
        design = _design_content().replace("记录生成器", "CLI 入口")
        results = validate(arch, design, _intent_content())
        failed = [(r[0], r[2]) for r in results if r[1] != "PASS"]
        self.assertFalse(failed, f"Unexpected failures: {failed}")


class TestA8ExpensiveDetails(unittest.TestCase):
    def test_missing_expensive_detail_fails(self):
        """有贵决策但第 6 节没有对应说明。"""
        content = _arch_content().replace(
            "| 文件格式 | Markdown | C01 | JSON 不便于人直接阅读和编辑，交接记录需要人能快速查看 | 便宜 |",
            "| 文件格式 | Markdown | C01 | JSON 不便于人直接阅读和编辑 | 贵 |",
        )
        result = _result(content, _design_content(), _intent_content(), "A8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("缺少详细说明", result[2])

    def test_cheap_item_with_detail_fails(self):
        """便宜决策不应该有详细说明。"""
        # 在第 6 节添加一个便宜条目的说明
        content = _arch_content().replace(
            "## 6. 重要决策的详细说明\n\n无",
            "## 6. 重要决策的详细说明\n\n### 文件格式\n\n这是一段说明。",
        )
        result = _result(content, _design_content(), _intent_content(), "A8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不应有", result[2])

    def test_no_expensive_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A8")
        self.assertEqual("PASS", result[1])


# ═══════════════════════════════════════════════════════════════════════════
# 功能设计层检查 D1-D5
# ═══════════════════════════════════════════════════════════════════════════


class TestD1NonEmpty(unittest.TestCase):
    def test_empty_design_fails(self):
        results = validate(_arch_content(), "", _intent_content())
        d1_results = [r for r in results if r[0] == "D1"]
        self.assertEqual("FAIL", d1_results[0][1])
        # D1 FAIL 后不继续检查 D2-D5 和 X1-X2
        d_and_x = [r for r in results if r[0].startswith("D") or r[0].startswith("X")]
        self.assertEqual(1, len(d_and_x))


class TestD2CapabilityCoverage(unittest.TestCase):
    def test_missing_capability_section_fails(self):
        content = _design_content().replace("### [C01] 生成交接记录", "### [C99] 生成交接记录")
        result = _result(_arch_content(), content, _intent_content(), "D2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("C01", result[2])

    def test_all_capabilities_present_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D2")
        self.assertEqual("PASS", result[1])


class TestD3NotDoField(unittest.TestCase):
    def test_missing_not_do_field_fails(self):
        content = _design_content().replace("- **不做什么**：", "- **X**：")
        result = _result(_arch_content(), content, _intent_content(), "D3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不做什么", result[2])

    def test_empty_not_do_field_fails(self):
        content = _design_content().replace(
            "- **不做什么**：不做自动归档旧记录，不做通知发送，不做交接记录的版本管理",
            "- **不做什么**：",
        )
        result = _result(_arch_content(), content, _intent_content(), "D3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("为空", result[2])

    def test_valid_not_do_field_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D3")
        self.assertEqual("PASS", result[1])


class TestD4CodePatterns(unittest.TestCase):
    def test_code_function_fails(self):
        content = _design_content() + "\nfunction generateReport() {\n}\n"
        result = _result(_arch_content(), content, _intent_content(), "D4")
        self.assertEqual("FAIL", result[1])

    def test_code_def_fails(self):
        content = _design_content() + "\ndef generate_report():\n    pass\n"
        result = _result(_arch_content(), content, _intent_content(), "D4")
        self.assertEqual("FAIL", result[1])

    def test_code_create_table_fails(self):
        content = _design_content() + "\nCREATE TABLE handoff_records ();\n"
        result = _result(_arch_content(), content, _intent_content(), "D4")
        self.assertEqual("FAIL", result[1])

    def test_no_code_patterns_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D4")
        self.assertEqual("PASS", result[1])


class TestD5ConsistencyCheck(unittest.TestCase):
    def test_missing_check_table_fails(self):
        content = _design_content().replace("## 3. 与架构文档的对照", "## X")
        result = _result(_arch_content(), content, _intent_content(), "D5")
        self.assertEqual("FAIL", result[1])

    def test_valid_check_table_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D5")
        self.assertEqual("PASS", result[1])


# ═══════════════════════════════════════════════════════════════════════════
# 跨文件检查 X1-X2
# ═══════════════════════════════════════════════════════════════════════════


class TestX1ModuleConsistency(unittest.TestCase):
    def test_undefined_module_in_design_fails(self):
        content = _design_content().replace(
            "- **涉及模块**：记录生成器、文件存储",
            "- **涉及模块**：不存在的模块",
        )
        result = _result(_arch_content(), content, _intent_content(), "X1")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未定义", result[2])

    def test_valid_modules_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "X1")
        self.assertEqual("PASS", result[1])


class TestX2CapabilityConsistency(unittest.TestCase):
    def test_capability_mismatch_fails(self):
        """architecture.md 没有 C02 但 design.md 有 [C02]。"""
        content = _design_content().replace(
            "## 3. 与架构文档的对照",
            "### [C02] 自动归档\n\n- **涉及模块**：文件存储\n- **数据流转**：无\n- **关键状态变化**：无\n- **不做什么**：不做归档\n\n## 3. 与架构文档的对照",
        )
        result = _result(_arch_content(), content, _intent_content(), "X2")
        self.assertEqual("FAIL", result[1])

    def test_matching_capabilities_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "X2")
        self.assertEqual("PASS", result[1])


if __name__ == "__main__":
    unittest.main()
