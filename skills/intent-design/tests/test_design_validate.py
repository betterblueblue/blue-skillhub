#!/usr/bin/env python3
"""Behavior tests for design_validate.py.

Run:
  python -m pytest skills/intent-design/tests/test_design_validate.py -v
  python skills/intent-design/tests/test_design_validate.py
"""

from __future__ import annotations

import re
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
        self.assertEqual(22, len(results))
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
        content = _arch_content().replace("## 7. 额外结构与假设", "## X")
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
            "## 7. 额外结构与假设",
            "## 7. 额外结构与假设\n\n<!-- 无额外结构 -->",
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
            "## 7. 额外结构与假设",
            "## 7. 额外结构与假设\n\n下面这些结构并非无额外结构：",
        )
        result = _result(content, _design_content(), _intent_content(), "A7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不合规", result[2])

    def test_declaration_with_rows_contradiction_fails(self):
        """声明"无额外结构"但表格仍有数据行 → 矛盾 FAIL。"""
        content = _arch_content().replace(
            "## 7. 额外结构与假设",
            "## 7. 额外结构与假设\n\n无额外结构",
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


class TestTemplateSync(unittest.TestCase):
    """校验器要求的必需章节必须存在于模板——防止校验器与模板漂移。"""

    def test_arch_required_sections_exist_in_template(self):
        import design_validate as dv
        template = (SKILL_DIR / "templates" / "architecture.md").read_text(encoding="utf-8")
        missing = [s for s in dv.ARCH_REQUIRED_SECTIONS if s not in template]
        self.assertFalse(missing, f"architecture 模板缺少校验器要求的章节: {missing}")

    def test_design_required_sections_exist_in_template(self):
        import design_validate as dv
        template = (SKILL_DIR / "templates" / "design.md").read_text(encoding="utf-8")
        missing = [s for s in dv.DESIGN_REQUIRED_SECTIONS if s not in template]
        self.assertFalse(missing, f"design 模板缺少校验器要求的章节: {missing}")


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
            "## 8. 关键选型与代价（请重点核对）\n\n无",
            "## 8. 关键选型与代价（请重点核对）\n\n### 文件格式\n\n这是一段说明。",
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
        # D1 FAIL 后不继续检查 D2-D9 和 X1-X3
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
        content = _design_content().replace("## 4. 与架构文档的对照", "## X")
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
            "## 4. 与架构文档的对照",
            "### [C02] 自动归档\n\n- **涉及模块**：文件存储\n- **数据流转**：无\n- **关键状态变化**：无\n- **不做什么**：不做归档\n\n## 4. 与架构文档的对照",
        )
        result = _result(_arch_content(), content, _intent_content(), "X2")
        self.assertEqual("FAIL", result[1])

    def test_matching_capabilities_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "X2")
        self.assertEqual("PASS", result[1])


class TestDisplayContract(unittest.TestCase):
    """D6: 每个能力必须有「数据→展示契约」且非空。"""

    def test_missing_display_contract_fails(self):
        content = _design_content().replace(
            "- **数据→展示契约**：无（本能力不涉及状态/枚举/字典/图片字段）",
            "- **X**：无",
        )
        result = _result(_arch_content(), content, _intent_content(), "D6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("数据→展示契约", result[2])

    def test_valid_display_contract_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D6")
        self.assertEqual("PASS", result[1])


# ═══════════════════════════════════════════════════════════════════════════
# 非功能性设计落点 A9 / 运行形态 A10（2026-08-31 新增）
# ═══════════════════════════════════════════════════════════════════════════


class TestA9NFRAnchoring(unittest.TestCase):
    """INTENT 第 15/16 节的 PF/CC/SF 必须逐条有架构对策落点。"""

    NFR_ROW = (
        "| SF01 | 交接记录模板只包含任务、进度、阻塞项和下一步，"
        "生成时不含其他会话内容 | 记录生成器 |"
    )

    def test_uncovered_requirement_fails(self):
        content = _arch_content().replace(self.NFR_ROW, "")
        result = _result(content, _design_content(), _intent_content(), "A9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("SF01", result[2])

    def test_undefined_owner_module_fails(self):
        content = _arch_content().replace(
            self.NFR_ROW,
            "| SF01 | 交接记录模板只包含任务和进度 | 幽灵模块 |",
        )
        result = _result(content, _design_content(), _intent_content(), "A9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("幽灵模块", result[2])

    def test_valid_nfr_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A9")
        self.assertEqual("PASS", result[1])

    def test_no_nfr_intent_requires_declaration(self):
        """INTENT 没有任何 PF/CC/SF 时，架构侧必须声明「无性能与安全要求」。"""
        intent = _intent_content().replace("SF01", "XX01")
        result = _result(_arch_content(), _design_content(), intent, "A9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("无性能与安全要求", result[2])

    def test_no_nfr_intent_with_declaration_passes(self):
        intent = _intent_content().replace("SF01", "XX01")
        content = _arch_content().replace(
            "| 要求 ID | 架构对策 | 归属模块 |\n|---|---|---|\n" + self.NFR_ROW,
            "无性能与安全要求",
        )
        result = _result(content, _design_content(), intent, "A9")
        self.assertEqual("PASS", result[1])


class TestA10Runtime(unittest.TestCase):
    def test_empty_runtime_fails(self):
        content = _arch_content().replace(
            "- **部署形态**：本地单机，随目标项目使用，不部署服务器\n"
            "- **进程模型**：按需执行，单进程运行后退出\n"
            "- **配置归属**：无配置，输出路径由命令行参数指定",
            "",
        )
        result = _result(content, _design_content(), _intent_content(), "A10")
        self.assertEqual("FAIL", result[1])

    def test_placeholder_runtime_fails(self):
        content = _arch_content().replace(
            "- **部署形态**：本地单机，随目标项目使用，不部署服务器",
            "- **部署形态**：{部署形态}",
        )
        result = _result(content, _design_content(), _intent_content(), "A10")
        self.assertEqual("FAIL", result[1])

    def test_valid_runtime_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "A10")
        self.assertEqual("PASS", result[1])


# ═══════════════════════════════════════════════════════════════════════════
# 失败边界 D7 / 权限可见性 D8 / 数据设计 D9 / 实体归属 X3（2026-08-31 新增）
# ═══════════════════════════════════════════════════════════════════════════


class TestD7FailureField(unittest.TestCase):
    def test_missing_field_fails(self):
        content = _design_content().replace("- **失败与边界情况**：", "- **X**：")
        result = _result(_arch_content(), content, _intent_content(), "D7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("失败与边界情况", result[2])

    def test_empty_field_fails(self):
        content = _design_content().replace(
            "- **失败与边界情况**：目标目录不可写时把错误返回给调用方并保留已有文件不变；无并发写入场景",
            "- **失败与边界情况**：",
        )
        result = _result(_arch_content(), content, _intent_content(), "D7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("为空", result[2])

    def test_valid_field_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D7")
        self.assertEqual("PASS", result[1])


class TestD8PermissionField(unittest.TestCase):
    def test_missing_field_fails(self):
        content = _design_content().replace("- **权限与可见性**：", "- **X**：")
        result = _result(_arch_content(), content, _intent_content(), "D8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("权限与可见性", result[2])

    def test_empty_field_fails(self):
        content = _design_content().replace(
            "- **权限与可见性**：无——单机本地工具，无角色体系，产物由使用者自行保管",
            "- **权限与可见性**：",
        )
        result = _result(_arch_content(), content, _intent_content(), "D8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("为空", result[2])

    def test_valid_field_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D8")
        self.assertEqual("PASS", result[1])


_TABLE_BLOCK = (
    "### 实体清单\n\n"
    "| 实体 | 归属模块 | 生命周期与说明 |\n"
    "|---|---|---|\n"
    "| 交接记录 | 记录生成器 | 运行时生成，用户手动清理 |\n\n"
    "### 数据表结构\n\n"
    "#### 表：handoff_records\n\n"
    "| 字段 | 类型 | 约束 | 说明 |\n"
    "|---|---|---|---|\n"
    "| id | 文本 | 主键 | 记录标识 |"
)


class TestD9DataDesign(unittest.TestCase):
    def test_missing_section_fails(self):
        content = _design_content().replace("无数据库表", "")
        result = _result(_arch_content(), content, _intent_content(), "D9")
        self.assertEqual("FAIL", result[1])

    def test_no_declaration_no_rows_fails(self):
        content = _design_content().replace("无数据库表", "（待定）")
        result = _result(_arch_content(), content, _intent_content(), "D9")
        self.assertEqual("FAIL", result[1])

    def test_declaration_with_rows_contradiction_fails(self):
        content = _design_content().replace(
            "无数据库表",
            "无数据库表\n\n#### 表：handoff_records\n\n"
            "| 字段 | 类型 | 约束 | 说明 |\n|---|---|---|---|\n| id | 文本 | 主键 | 记录标识 |",
        )
        result = _result(_arch_content(), content, _intent_content(), "D9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("矛盾", result[2])

    def test_table_rows_pass(self):
        content = _design_content().replace("无数据库表", _TABLE_BLOCK)
        result = _result(_arch_content(), content, _intent_content(), "D9")
        self.assertEqual("PASS", result[1])

    def test_no_db_declaration_passes(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "D9")
        self.assertEqual("PASS", result[1])


class TestX3EntityModules(unittest.TestCase):
    def test_undefined_owner_fails(self):
        block = _TABLE_BLOCK.replace("| 交接记录 | 记录生成器 |", "| 交接记录 | 幽灵模块 |")
        content = _design_content().replace("无数据库表", block)
        result = _result(_arch_content(), content, _intent_content(), "X3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("幽灵模块", result[2])

    def test_valid_owner_passes(self):
        content = _design_content().replace("无数据库表", _TABLE_BLOCK)
        result = _result(_arch_content(), content, _intent_content(), "X3")
        self.assertEqual("PASS", result[1])

    def test_no_entities_not_applicable(self):
        result = _result(_arch_content(), _design_content(), _intent_content(), "X3")
        self.assertEqual("PASS", result[1])


# ═══════════════════════════════════════════════════════════════════════════
# 旧编号文档兼容（标题归一化，2026-08-31 章节扩充后）
# ═══════════════════════════════════════════════════════════════════════════


class TestLegacyDocumentCompat(unittest.TestCase):
    """旧编号文档（6 节架构 / 3 节设计）经标题归一化后旧章节照常检查；
    缺的新章节按 FAIL 提示补节，不静默豁免。"""

    @staticmethod
    def _legacy_arch() -> str:
        text = _arch_content()
        text = re.sub(
            r"## 5\. 非功能性设计落点.*?(?=## 6\. 运行形态)", "", text, flags=re.S
        )
        text = re.sub(
            r"## 6\. 运行形态.*?(?=## 7\. 额外结构与假设)", "", text, flags=re.S
        )
        text = text.replace("## 7. 额外结构与假设", "## 5. 额外结构与假设")
        text = text.replace(
            "## 8. 关键选型与代价（请重点核对）", "## 6. 关键选型与代价（请重点核对）"
        )
        return text

    @staticmethod
    def _legacy_design() -> str:
        text = _design_content()
        text = re.sub(r"## 2\. 数据设计.*?(?=## 3\. 能力设计)", "", text, flags=re.S)
        text = text.replace("## 3. 能力设计", "## 2. 能力设计")
        text = text.replace("## 4. 与架构文档的对照", "## 3. 与架构文档的对照")
        return text

    def test_legacy_headings_normalized(self):
        results = validate(self._legacy_arch(), self._legacy_design(), _intent_content())
        by_id = {r[0]: r for r in results}
        # A2 的缺失提示只点名两个新章节——旧第 5/6 节被别名归一化识别
        self.assertEqual("FAIL", by_id["A2"][1])
        self.assertIn("非功能性设计落点", by_id["A2"][2])
        self.assertIn("运行形态", by_id["A2"][2])
        self.assertNotIn("额外结构与假设", by_id["A2"][2])
        self.assertNotIn("关键选型", by_id["A2"][2])
        # 旧第 5/6 节的内容检查照常运行
        self.assertEqual("PASS", by_id["A7"][1])
        self.assertEqual("PASS", by_id["A8"][1])
        # 旧设计文档：只提示缺数据设计节，能力设计与对照表被识别
        self.assertEqual("FAIL", by_id["D2"][1])
        self.assertIn("数据设计", by_id["D2"][2])
        self.assertNotIn("能力设计", by_id["D2"][2])
        self.assertEqual("PASS", by_id["D5"][1])


if __name__ == "__main__":
    unittest.main()
