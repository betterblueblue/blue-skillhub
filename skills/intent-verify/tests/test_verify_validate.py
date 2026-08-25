#!/usr/bin/env python3
"""Behavior tests for verify_validate.py.

Run:
  python -m pytest skills/intent-verify/tests/test_verify_validate.py -v
  python skills/intent-verify/tests/test_verify_validate.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from verify_validate import _has_ui_artifact, _intent_has_design_standards, validate, main
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
    "| 文件存储 | 读写交接记录 Markdown 文件 | C01 | 无 |\n"
)

_DESIGN_CONTENT = (
    "# 功能设计 - 测试\n\n"
    "## 1. 设计概览\n\n覆盖 1 项能力。\n\n"
    "## 2. 能力设计\n\n"
    "### [C01] 生成交接记录\n\n"
    "- **涉及模块**：记录生成器、文件存储\n"
    "- **数据流转**：无\n"
    "- **关键状态变化**：无\n"
    "- **不做什么**：不做自动归档\n\n"
    "## 3. 与架构文档的对照\n\n无\n"
)


def _content() -> str:
    return (FIXTURE_DIR / "valid-verify-record.md").read_text(encoding="utf-8")


def _intent() -> str:
    return (FIXTURE_DIR / "valid-intent.md").read_text(encoding="utf-8")


def _result(content: str, check_id: str, arch: str = _ARCH_CONTENT) -> tuple[str, str, str]:
    matches = [item for item in validate(content, _intent(), arch) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_verify_record_passes_all_checks(self):
        results = validate(_content(), _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        self.assertEqual(8, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestNonEmpty(unittest.TestCase):
    def test_empty_file_fails(self):
        results = validate("", _intent())
        self.assertEqual("FAIL", results[0][1])


class TestRegressionSection(unittest.TestCase):
    def test_missing_regression_section_fails(self):
        content = _content().replace("## 回归验证结果", "## X")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("回归验证", result[2])

    def test_missing_test_command_fails(self):
        content = _content().replace("全量测试命令", "X")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("全量测试命令", result[2])

    def test_regression_result_not_passing_fails(self):
        content = _content().replace("- 结果：通过", "- 结果：未通过")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未通过", result[2])

    def test_valid_regression_passes(self):
        result = _result(_content(), "V2")
        self.assertEqual("PASS", result[1])


class TestPathRecords(unittest.TestCase):
    def test_no_path_records_fails(self):
        content = _content().replace("### 路径 P01:", "### X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])

    def test_missing_given_fails(self):
        content = _content().replace("- Given:", "- X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Given", result[2])

    def test_missing_when_fails(self):
        content = _content().replace("- When:", "- X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("When", result[2])

    def test_missing_then_fails(self):
        content = (
            _content()
            .replace("- [x] Then:", "- X Then:")
            .replace("- [x] And:", "- X And:")
        )
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Then", result[2])

    def test_missing_verify_method_fails(self):
        content = _content().replace("- 验证方式：", "- X：")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验证方式", result[2])

    def test_valid_paths_pass(self):
        result = _result(_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestV3Evidence(unittest.TestCase):
    def test_unchecked_then_fails(self):
        content = _content().replace(
            "- [x] Then: 记录文件存在",
            "- [ ] Then: 记录文件存在",
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未勾选", result[2])

    def test_then_not_v3_fails(self):
        content = _content().replace(
            "- [x] Then: 记录文件存在 — V3，",
            "- [x] Then: 记录文件存在 — V2，",
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("V3", result[2])

    def test_all_unchecked_thens_fails(self):
        content = _content().replace("- [x] Then:", "- [ ] Then:").replace(
            "- [x] And:", "- [ ] And:"
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])

    def test_valid_v3_passes(self):
        result = _result(_content(), "V4")
        self.assertEqual("PASS", result[1])


class TestConditionalSection(unittest.TestCase):
    def test_missing_conditional_section_fails(self):
        content = _content().replace("## 条件性验证结果", "## X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("条件性验证", result[2])

    def test_missing_perf_section_fails(self):
        content = _content().replace("### 性能验证", "### X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("性能验证", result[2])

    def test_missing_security_section_fails(self):
        content = _content().replace("### 安全验证", "### X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("安全验证", result[2])

    def test_valid_conditional_passes(self):
        result = _result(_content(), "V5")
        self.assertEqual("PASS", result[1])


class TestFinalReview(unittest.TestCase):
    def test_missing_gate_fails(self):
        content = _content().replace("## 最终复核", "## X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("最终复核", result[2])

    def test_missing_regression_summary_fails(self):
        content = _content().replace("### 回归验证结果汇总", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("回归验证结果汇总", result[2])

    def test_missing_capability_table_fails(self):
        content = _content().replace("### 保留能力逐项核对", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("保留能力", result[2])

    def test_missing_path_table_fails(self):
        content = _content().replace("### 验收路径逐条验证", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验收路径", result[2])

    def test_path_table_then_not_passing_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 是 |",
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 否 |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Then 全通过", result[2])

    def test_path_table_without_v3_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 |",
            "| P01 | 生成并查看交接记录 | V2 |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("V3", result[2])

    def test_missing_conditional_summary_fails(self):
        content = _content().replace("### 条件性验证结果汇总", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("条件性验证结果汇总", result[2])

    def test_missing_drift_table_fails(self):
        content = _content().replace("### 漂移复核", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("漂移复核", result[2])

    def test_missing_conclusion_fails(self):
        content = _content().replace("### 结论", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("结论", result[2])

    def test_conclusion_without_verdict_fails(self):
        content = _content().replace("- 结果：通过", "- 结果：待定")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("判定", result[2])

    def test_valid_gate_passes(self):
        result = _result(_content(), "V6")
        self.assertEqual("PASS", result[1])


class TestCrossValidation(unittest.TestCase):
    def test_valid_cross_validation_passes(self):
        result = _result(_content(), "V7")
        self.assertEqual("PASS", result[1])

    def test_missing_path_in_verify_fails(self):
        """verify-record 缺少 INTENT.md 中的路径时 V7 失败。"""
        content = _content().replace("### 路径 P01:", "### 路径 P99:")
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("缺少", result[2])

    def test_extra_path_in_verify_fails(self):
        """verify-record 有 INTENT.md 中不存在的路径时 V7 失败。"""
        # 在 E2E 段末尾插入一条多余路径
        content = _content().replace(
            "## 条件性验证结果",
            "### 路径 P99: 不存在的路径\n\n- Given: test — 就绪\n- When: test — 已执行\n- [x] Then: test — V3，test\n- 验证方式：手动走通\n\n---\n\n## 条件性验证结果",
        )
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])

    def test_missing_capability_in_verify_fails(self):
        """保留能力核对表缺少 INTENT.md 中的能力时 V7 失败。"""
        content = _content().replace("| C01 |", "| C99 |")
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])

    def test_security_marked_not_applicable_when_intent_has_requirement_fails(self):
        """INTENT.md 有安全要求但验收记录标注不适用时 V7 失败。"""
        content = _content().replace(
            "- INTENT.md/PRD 中是否有安全要求：是",
            "- INTENT.md/PRD 中是否有安全要求：否",
        ).replace(
            "- 结果：通过\n\n---\n\n## 最终复核",
            "- 结果：不适用\n\n---\n\n## 最终复核",
        )
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("安全", result[2])


class TestTechDriftCheck(unittest.TestCase):
    """V8: 最终复核必须包含技术漂移复核子节。"""

    def test_no_architecture_fails(self):
        """不提供 architecture.md 时 V8 返回 FAIL。"""
        results = validate(_content(), _intent())
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("必须存在", v8[0][2])

    def test_no_design_fails(self):
        """不提供 design.md 时 V8 返回 FAIL（不再静默跳过交叉检查）。"""
        results = validate(_content(), _intent(), _ARCH_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("design.md", v8[0][2])

    def test_tech_drift_present_passes(self):
        """有技术漂移复核子节时 V8 返回 PASS。"""
        results = validate(_content(), _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("PASS", v8[0][1])

    def test_tech_drift_missing_fails(self):
        """缺少技术漂移复核子节时 V8 返回 FAIL。"""
        content = _content().replace("### 技术漂移复核", "### X")
        results = validate(content, _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("技术漂移复核", v8[0][2])

    def test_tech_drift_only_text_fails(self):
        """技术漂移复核子节只有文字、没有表格行时 V8 返回 FAIL。"""
        content = _content().replace(
            "| 记录生成器 | 是 | 一致 | 代码实现与架构文档定义一致 |\n"
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |",
            "已核对。",
        )
        results = validate(content, _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("数据行", v8[0][2])

    def test_tech_drift_undefined_module_fails(self):
        """技术漂移复核引用了 architecture.md 中未定义的模块时 V8 返回 FAIL。"""
        content = _content().replace(
            "| 记录生成器 | 是 | 一致 | 代码实现与架构文档定义一致 |",
            "| 不存在的模块 | 是 | 一致 | 代码实现与架构文档定义一致 |",
        )
        results = validate(content, _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("未定义", v8[0][2])

    def test_tech_drift_with_design_passes(self):
        """传入 design.md 且模块一致时 V8 PASS。"""
        results = validate(_content(), _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("PASS", v8[0][1])

    def test_tech_drift_undefined_in_design_fails(self):
        """传入 design.md 且模块不在 design.md 中时 V8 FAIL。"""
        design = (
            "# 功能设计 - 测试\n\n"
            "## 1. 设计概览\n\n覆盖 1 项能力。\n\n"
            "## 2. 能力设计\n\n"
            "### [C01] 生成交接记录\n\n"
            "- **涉及模块**：记录生成器\n"
            "- **数据流转**：无\n"
            "- **关键状态变化**：无\n"
            "- **不做什么**：不做自动归档\n\n"
            "## 3. 与架构文档的对照\n\n无\n"
        )
        # design.md 只提了"记录生成器"，没提"文件存储"，但技术漂移复核包含"文件存储"
        results = validate(_content(), _intent(), _ARCH_CONTENT, design)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("design.md", v8[0][2])

    def test_new_module_with_note_passes(self):
        """如实报告新增模块（状态标"新增"且说明列写明原因）不应 FAIL。"""
        content = _content().replace(
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |",
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |\n"
            "| 通知服务 | 否 | 新增 | 开发中发现需要失败通知，architecture.md 未定义 |",
        )
        results = validate(content, _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("PASS", v8[0][1])

    def test_new_module_without_note_fails(self):
        """新增模块没有在说明列写明原因时 V8 FAIL。"""
        content = _content().replace(
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |",
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |\n"
            "| 通知服务 | 否 | 新增 |  |",
        )
        results = validate(content, _intent(), _ARCH_CONTENT, _DESIGN_CONTENT)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("FAIL", v8[0][1])
        self.assertIn("写明原因", v8[0][2])

    def test_spaced_module_name_passes(self):
        """含空格的模块名（如 "CLI 入口"）不被 V8 分词拆散（冒烟 B-1）。"""
        arch = _ARCH_CONTENT.replace("记录生成器", "CLI 入口")
        design = _DESIGN_CONTENT.replace("记录生成器", "CLI 入口")
        content = _content().replace("记录生成器", "CLI 入口")
        results = validate(content, _intent(), arch, design)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("PASS", v8[0][1])

    def test_missing_module_skips_design_check(self):
        """状态标"缺失"的模块（架构定义但代码未实现）不做 design.md 比对。"""
        design = (
            "# 功能设计 - 测试\n\n"
            "## 1. 设计概览\n\n覆盖 1 项能力。\n\n"
            "## 2. 能力设计\n\n"
            "### [C01] 生成交接记录\n\n"
            "- **涉及模块**：记录生成器\n"
            "- **数据流转**：无\n"
            "- **关键状态变化**：无\n"
            "- **不做什么**：不做自动归档\n\n"
            "## 3. 与架构文档的对照\n\n无\n"
        )
        content = _content().replace(
            "| 文件存储 | 是 | 一致 | 代码实现与架构文档定义一致 |",
            "| 文件存储 | 是 | 缺失 | 尚未实现，计划下一迭代补 |",
        )
        results = validate(content, _intent(), _ARCH_CONTENT, design)
        v8 = [r for r in results if r[0] == "V8"]
        self.assertEqual(1, len(v8))
        self.assertEqual("PASS", v8[0][1])


class TestPathTableNegativeMarkers(unittest.TestCase):
    """V6: Then 全通过列和验证等级列不接受"是（部分）"、"V3 未达成"这类搭车写法。"""

    def test_then_pass_partial_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 是 |",
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 是（部分） |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("部分", result[2])

    def test_verify_level_not_achieved_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 |",
            "| P01 | 生成并查看交接记录 | V3 未达成 | 手动走通 |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未达成", result[2])


class TestDriftTableCheck(unittest.TestCase):
    """V6: 漂移复核子节必须有数据行。"""

    def test_drift_only_text_fails(self):
        """漂移复核子节只有文字、没有表格行时 V6 返回 FAIL。"""
        content = _content().replace(
            "| D1 未确认新增 | 未命中 | 所有能力均来自 INTENT.md |\n"
            "| D2 目标替换 | 未命中 | 目标始终是跨会话交接 |\n"
            "| D3 能力降级 | 未命中 | C01 完整实现 |\n"
            "| D4 保留项遗漏 | 未命中 | C01 已体现 |\n"
            "| D5 推迟或放弃项被重新加入 | 未命中 | C02 和 C03 未出现 |\n"
            "| D6 决策来源失真 | 未命中 | 决策来源与 INTENT.md 一致 |\n"
            "| D7 交接信息丢失 | 未命中 | DEV-RECORD 和 VERIFY-RECORD 记录完整 |",
            "已核对。",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("数据行", result[2])


class TestTemplateSync(unittest.TestCase):
    """校验器要求的标题必须存在于模板——防止校验器与模板漂移。

    2026-07 强模型验证曾发现模板缺 技术漂移复核 子节而校验器强制要求，
    照模板写的文档必挂 V8。本测试从机制上杜绝这类不同步。
    """

    def test_validator_headings_exist_in_template(self):
        import verify_validate as vv
        template = (SKILL_DIR / "templates" / "verify-record.md").read_text(encoding="utf-8")
        headings = [
            vv.REGRESSION_HEADING, vv.E2E_HEADING, vv.CONDITIONAL_HEADING,
            vv.PERF_HEADING, vv.SECURITY_HEADING, vv.GATE_HEADING,
            vv.REGRESSION_SUMMARY_HEADING, vv.CAPABILITY_HEADING,
            vv.PATH_TABLE_HEADING, vv.CONDITIONAL_SUMMARY_HEADING,
            vv.DRIFT_HEADING, vv.TECH_DRIFT_HEADING, vv.CONCLUSION_HEADING,
        ]
        missing = [h for h in headings if h not in template]
        self.assertFalse(missing, f"模板缺少校验器要求的标题: {missing}")


class TestCLI(unittest.TestCase):
    """CLI 参数测试：architecture.md 和 design.md 都是强制参数。"""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(_ARCH_CONTENT)
        tmp.close()
        cls._arch_path = tmp.name
        tmp2 = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp2.write(_DESIGN_CONTENT)
        tmp2.close()
        cls._design_path = tmp2.name

    @classmethod
    def tearDownClass(cls):
        Path(cls._arch_path).unlink(missing_ok=True)
        Path(cls._design_path).unlink(missing_ok=True)

    def _run_main(self, *args) -> int:
        old = sys.argv
        sys.argv = ["verify_validate.py"] + list(args)
        try:
            return main()
        finally:
            sys.argv = old

    def test_all_args_valid_exit_0(self):
        """参数完整且文件存在时退出 0。"""
        code = self._run_main(
            str(FIXTURE_DIR / "valid-verify-record.md"),
            str(FIXTURE_DIR / "valid-intent.md"),
            self._arch_path,
            self._design_path,
        )
        self.assertEqual(0, code)

    def test_missing_arch_arg_exit_1(self):
        """缺少 architecture.md 参数时退出 1。"""
        code = self._run_main(
            str(FIXTURE_DIR / "valid-verify-record.md"),
            str(FIXTURE_DIR / "valid-intent.md"),
        )
        self.assertEqual(1, code)

    def test_missing_design_arg_exit_1(self):
        """只传 3 个路径（缺 design.md）时退出 1，不再静默跳过。"""
        code = self._run_main(
            str(FIXTURE_DIR / "valid-verify-record.md"),
            str(FIXTURE_DIR / "valid-intent.md"),
            self._arch_path,
        )
        self.assertEqual(1, code)

    def test_nonexistent_arch_file_exit_1(self):
        """architecture.md 文件不存在时退出 1。"""
        code = self._run_main(
            str(FIXTURE_DIR / "valid-verify-record.md"),
            str(FIXTURE_DIR / "valid-intent.md"),
            "/nonexistent/path/architecture.md",
            self._design_path,
        )
        self.assertEqual(1, code)

    def test_nonexistent_design_file_exit_1(self):
        """design.md 路径打错（文件不存在）时退出 1，不再静默降级。"""
        code = self._run_main(
            str(FIXTURE_DIR / "valid-verify-record.md"),
            str(FIXTURE_DIR / "valid-intent.md"),
            self._arch_path,
            "/nonexistent/path/design.md",
        )
        self.assertEqual(1, code)


class TestVerifyMethodUI(unittest.TestCase):
    """V3 验证方式必须含 UI 特征，纯 API 不能单独构成端到端证据。"""

    def test_pure_api_method_fails(self):
        content = _content().replace("- 验证方式：手动走通", "- 验证方式：API 脚本")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("API", result[2])

    def test_e2e_method_passes(self):
        content = _content().replace("- 验证方式：手动走通", "- 验证方式：E2E 测试")
        result = _result(content, "V3")
        self.assertEqual("PASS", result[1])


class TestDesignStandardArtifact(unittest.TestCase):
    """有设计标准时 V3 必须带真实截图/Playwright 产物。"""

    _DESIGN_INTENT = (
        "## 12. 设计标准\n\n"
        "| 设计素材 ID | 设计素材 | 路径 | 覆盖范围 | 确认 |\n"
        "|---|---|---|---|---|\n"
        '| D01 | 可点原型 | prototype/screens/main.html | 首页 | "按原型做" |\n'
    )

    def test_intent_has_design_standards_true(self):
        self.assertTrue(_intent_has_design_standards(self._DESIGN_INTENT))

    def test_intent_has_design_standards_false(self):
        self.assertFalse(_intent_has_design_standards("## 12. 设计标准\n\n无设计标准素材。"))

    def test_artifact_missing_fails(self):
        ok, msg = _has_ui_artifact("- [x] Then: X — V3，手动走通", None)
        self.assertFalse(ok)
        self.assertIn("截图", msg)

    def test_artifact_marker_present_without_base_passes(self):
        ok, _ = _has_ui_artifact("- [x] Then: X — V3，截图：shots/p01.png", None)
        self.assertTrue(ok)

    def test_artifact_file_exists_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "shots").mkdir()
            (base / "shots" / "p01.png").write_bytes(b"x")
            ok, _ = _has_ui_artifact("- [x] Then: X — V3，截图：shots/p01.png", base)
            self.assertTrue(ok)

    def test_artifact_file_missing_fails(self):
        with tempfile.TemporaryDirectory() as td:
            ok, msg = _has_ui_artifact("- [x] Then: X — V3，截图：shots/p01.png", Path(td))
            self.assertFalse(ok)
            self.assertIn("不存在", msg)


if __name__ == "__main__":
    unittest.main()
