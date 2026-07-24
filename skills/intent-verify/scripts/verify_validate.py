#!/usr/bin/env python3
"""verify-record.md 结构校验与 INTENT.md 交叉引用校验。

用法：
  python verify_validate.py /path/to/intent-chain/{链路目录}/verify-record.md /path/to/intent-chain/{链路目录}/intent.md

检查项：
  V1: 文件非空
  V2: 有回归验证段（全量测试命令和结果，结果必须为通过或不适用）
  V3: 有端到端验收结果段（每条路径有 Given/When/Then 和验证方式）
  V4: 每条路径所有 Then 已勾选且达到 V3
  V5: 有条件性验证段（性能验证和安全验证，不适用也要标注）
  V6: 最终复核完整（回归汇总、保留能力核对、验收路径逐条验证含 Then 全通过、条件性汇总、漂移复核、结论）
  V7: 与 INTENT.md 交叉校验（路径 ID 一致、保留能力 ID 一致、性能/安全结论与 INTENT.md 要求一致）

本脚本不能验证 V3 证据是否真实，也不能证明验收结果符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PATH_HEADING_RE = re.compile(r"^###\s+路径\s+P\d+:\s*(.+)$", re.MULTILINE)
PATH_ID_IN_HEADING_RE = re.compile(r"P\d{2,}")
THEN_RE = re.compile(
    r"^\s*-\s*\[([ xX])\]\s*(?:Then|And):\s*(.+)$",
    re.MULTILINE,
)
GIVEN_RE = re.compile(r"^-\s*Given[：:]\s*(.+)$", re.MULTILINE)
WHEN_RE = re.compile(r"^-\s*When[：:]\s*(.+)$", re.MULTILINE)
VERIFY_METHOD_RE = re.compile(r"^-\s*验证方式[：:]\s*(.+)$", re.MULTILINE)
REGRESSION_HEADING = "## 回归验证结果"
E2E_HEADING = "## 端到端验收结果"
CONDITIONAL_HEADING = "## 条件性验证结果"
PERF_HEADING = "### 性能验证"
SECURITY_HEADING = "### 安全验证"
GATE_HEADING = "## 最终复核"
REGRESSION_SUMMARY_HEADING = "### 回归验证结果汇总"
CAPABILITY_HEADING = "### 保留能力逐项核对"
PATH_TABLE_HEADING = "### 验收路径逐条验证"
CONDITIONAL_SUMMARY_HEADING = "### 条件性验证结果汇总"
DRIFT_HEADING = "### 漂移复核"
CONCLUSION_HEADING = "### 结论"

CAPABILITY_ID_RE = re.compile(r"C\d{2,}")
PATH_ID_RE = re.compile(r"P\d{2,}")


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _subsection(content: str, heading: str) -> str:
    """提取 ### 级别的子节，停在下一个 ### 或 ## 之前。"""
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^###\s+|^##\s+|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _table_rows(content: str, header_first_cell: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        columns = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not columns or columns[0] == header_first_cell:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in columns):
            continue
        rows.append(columns)
    return rows


def _split_paths(content: str) -> list[str]:
    """提取每条验收路径的段落。"""
    e2e_pos = content.find(E2E_HEADING)
    conditional_pos = content.find(CONDITIONAL_HEADING)
    gate_pos = content.find(GATE_HEADING)
    # 路径在 E2E 和条件性验证之间
    search_start = e2e_pos if e2e_pos != -1 else 0
    search_end = conditional_pos if conditional_pos != -1 else (gate_pos if gate_pos != -1 else len(content))
    path_section = content[search_start:search_end]
    path_starts = [(m.start(), m.end()) for m in PATH_HEADING_RE.finditer(path_section)]
    if not path_starts:
        return []
    paths: list[str] = []
    for i, (start, _end) in enumerate(path_starts):
        next_end = path_starts[i + 1][0] if i + 1 < len(path_starts) else None
        if next_end is None:
            next_end = len(path_section)
        paths.append(path_section[start:next_end])
    return paths


def _parse_then_lines(path_content: str) -> list[tuple[str, str, str]]:
    """提取路径中的 Then/And 条目。返回 [(check_mark, text, level), ...]。"""
    results: list[tuple[str, str, str]] = []
    for m in THEN_RE.finditer(path_content):
        check = m.group(1).strip().lower()
        text = m.group(2).strip()
        level_match = re.search(r"V([0-3])", text)
        level = level_match.group(0) if level_match else ""
        results.append((check, text, level))
    return results


def _has_given(path_content: str) -> bool:
    return bool(GIVEN_RE.search(path_content))


def _has_when(path_content: str) -> bool:
    return bool(WHEN_RE.search(path_content))


def _has_verify_method(path_content: str) -> bool:
    return bool(VERIFY_METHOD_RE.search(path_content))


def _all_thens_v3(path_content: str) -> bool:
    """检查路径中所有 Then/And 条目是否都已勾选且达到 V3。"""
    then_lines = _parse_then_lines(path_content)
    if not then_lines:
        return False
    for check, _text, level in then_lines:
        if check != "x":
            return False
        if level != "V3":
            return False
    return True


# ---------------------------------------------------------------------------
# INTENT.md 解析辅助函数
# ---------------------------------------------------------------------------


def _intent_section(intent_content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+\d+\.\s|\Z)",
        intent_content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _parse_retained_capabilities(intent_content: str) -> set[str]:
    section = _intent_section(intent_content, "## 4. 能力与决策")
    rows = _table_rows(section, "能力 ID")
    return {row[0] for row in rows if len(row) >= 5 and row[4] == "保留"}


def _parse_acceptance_paths(intent_content: str) -> set[str]:
    section = _intent_section(intent_content, "## 14. 验收路径")
    rows = _table_rows(section, "路径 ID")
    return {row[0] for row in rows if len(row) >= 1 and PATH_ID_RE.fullmatch(row[0])}


def _intent_has_perf_requirements(intent_content: str) -> bool:
    """INTENT.md 第 15 节是否有性能要求（有表格行而非"无性能要求"）。"""
    section = _intent_section(intent_content, "## 15. 性能要求")
    rows = _table_rows(section, "要求 ID")
    return bool(rows)


def _intent_has_security_requirements(intent_content: str) -> bool:
    """INTENT.md 第 16 节是否有安全要求（有表格行而非"无安全要求"）。"""
    section = _intent_section(intent_content, "## 16. 安全要求")
    rows = _table_rows(section, "要求 ID")
    return bool(rows)


def validate(verify_content: str, intent_content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)。"""
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if verify_content.strip():
        results.append(("V1", "PASS", f"文件有 {len(verify_content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    # V2: 有回归验证段（全量测试命令和结果，结果必须为通过或不适用）
    regression_section = _section(verify_content, REGRESSION_HEADING)
    if not regression_section.strip():
        results.append(("V2", "FAIL", "缺少回归验证结果段"))
    else:
        v2_errors: list[str] = []
        if "全量测试命令" not in regression_section:
            v2_errors.append("缺少全量测试命令")
        result_match = re.search(
            r"^-\s*结果[：:]\s*(.+)$", regression_section, re.MULTILINE
        )
        if not result_match:
            v2_errors.append("缺少结果行")
        else:
            result_value = result_match.group(1).strip()
            if "不适用" in result_value:
                pass
            elif "未通过" in result_value:
                v2_errors.append(f"回归测试结果未通过: {result_value}")
            elif "通过" not in result_value:
                v2_errors.append(f"回归测试结果不是通过或不适用: {result_value}")
        if v2_errors:
            results.append(("V2", "FAIL", "; ".join(v2_errors)))
        else:
            results.append(("V2", "PASS", "回归验证段完整且结果为通过或不适用"))

    paths = _split_paths(verify_content)

    # V3: 有端到端验收结果段（每条路径有 Given/When/Then 和验证方式）
    if not paths:
        results.append(("V3", "FAIL", "未找到验收路径记录"))
    else:
        v3_errors: list[str] = []
        for path in paths:
            heading_match = PATH_HEADING_RE.search(path)
            path_label = heading_match.group(0) if heading_match else "未知路径"
            if not _has_given(path):
                v3_errors.append(f"{path_label} 缺少 Given")
            if not _has_when(path):
                v3_errors.append(f"{path_label} 缺少 When")
            if not _parse_then_lines(path):
                v3_errors.append(f"{path_label} 缺少 Then/And 条目")
            if not _has_verify_method(path):
                v3_errors.append(f"{path_label} 缺少验证方式")
        if v3_errors:
            results.append(("V3", "FAIL", "; ".join(v3_errors)))
        else:
            results.append(("V3", "PASS", f"全部 {len(paths)} 条路径有完整验证记录"))

    # V4: 每条路径所有 Then 已勾选且达到 V3
    v4_errors: list[str] = []
    for path in paths:
        heading_match = PATH_HEADING_RE.search(path)
        path_label = heading_match.group(0) if heading_match else "未知路径"
        then_lines = _parse_then_lines(path)
        if not then_lines:
            v4_errors.append(f"{path_label} 缺少 Then/And 条目")
            continue
        for check, text, level in then_lines:
            if check != "x":
                v4_errors.append(f"{path_label} 有未勾选的 Then: {text[:50]}")
            elif level != "V3":
                v4_errors.append(f"{path_label} 的条目未达 V3（当前 {level}）: {text[:50]}")
    if v4_errors:
        results.append(("V4", "FAIL", "; ".join(v4_errors)))
    else:
        results.append(("V4", "PASS", f"全部 {len(paths)} 条路径的所有 Then 已勾选且达到 V3"))

    # V5: 有条件性验证段（性能验证和安全验证，不适用也要标注）
    conditional_section = _section(verify_content, CONDITIONAL_HEADING)
    if not conditional_section.strip():
        results.append(("V5", "FAIL", "缺少条件性验证结果段"))
    else:
        v5_errors: list[str] = []
        perf_section = _subsection(conditional_section, PERF_HEADING)
        security_section = _subsection(conditional_section, SECURITY_HEADING)
        if not perf_section.strip():
            v5_errors.append("缺少性能验证段")
        if not security_section.strip():
            v5_errors.append("缺少安全验证段")
        if v5_errors:
            results.append(("V5", "FAIL", "; ".join(v5_errors)))
        else:
            results.append(("V5", "PASS", "条件性验证段完整（性能和安全均已标注）"))

    # V6: 最终复核完整
    gate_section = _section(verify_content, GATE_HEADING)
    if not gate_section.strip():
        results.append(("V6", "FAIL", "缺少最终复核节"))
    else:
        v6_errors: list[str] = []
        if not _subsection(gate_section, REGRESSION_SUMMARY_HEADING).strip():
            v6_errors.append("缺少回归验证结果汇总")
        if not _subsection(gate_section, CAPABILITY_HEADING).strip():
            v6_errors.append("缺少保留能力逐项核对")
        path_table = _subsection(gate_section, PATH_TABLE_HEADING)
        if not path_table.strip():
            v6_errors.append("缺少验收路径逐条验证")
        else:
            # 检查路径表每行的 Then 全通过列是否为"是"
            path_rows = _table_rows(path_table, "路径 ID")
            if not path_rows:
                v6_errors.append("验收路径逐条验证缺少数据行")
            else:
                for row in path_rows:
                    if len(row) < 7:
                        v6_errors.append(f"验收路径表行列数不足: {' | '.join(row)}")
                        continue
                    path_id = row[0]
                    then_pass = row[6]  # Then 全通过 列
                    if "是" not in then_pass:
                        v6_errors.append(f"路径 {path_id} 的 Then 全通过列不是'是': {then_pass}")
                    verify_level = row[2]  # 验证等级 列
                    if "V3" not in verify_level:
                        v6_errors.append(f"路径 {path_id} 的验证等级不是 V3: {verify_level}")
        if not _subsection(gate_section, CONDITIONAL_SUMMARY_HEADING).strip():
            v6_errors.append("缺少条件性验证结果汇总")
        if not _subsection(gate_section, DRIFT_HEADING).strip():
            v6_errors.append("缺少漂移复核")
        conclusion = _subsection(gate_section, CONCLUSION_HEADING)
        if not conclusion.strip():
            v6_errors.append("缺少结论")
        else:
            verdict_match = re.search(
                r"^-\s*结果[：:]\s*(.+)$", conclusion, re.MULTILINE
            )
            if not verdict_match:
                v6_errors.append("结论缺少结果行")
            else:
                verdict = verdict_match.group(1).strip()
                if "通过" not in verdict and "不通过" not in verdict:
                    v6_errors.append("结论缺少通过/不通过判定")
        if v6_errors:
            results.append(("V6", "FAIL", "; ".join(v6_errors)))
        else:
            results.append(("V6", "PASS", "最终复核完整"))

    # V7: 与 INTENT.md 交叉校验
    v7_errors: list[str] = []

    # 解析 INTENT.md
    intent_paths = _parse_acceptance_paths(intent_content)
    intent_caps = _parse_retained_capabilities(intent_content)
    intent_has_perf = _intent_has_perf_requirements(intent_content)
    intent_has_security = _intent_has_security_requirements(intent_content)

    # 路径 ID 一致性
    verify_path_ids: set[str] = set()
    for path in paths:
        heading_match = PATH_HEADING_RE.search(path)
        if heading_match:
            ids = PATH_ID_IN_HEADING_RE.findall(heading_match.group(0))
            verify_path_ids.update(ids)
    if intent_paths and verify_path_ids != intent_paths:
        missing = intent_paths - verify_path_ids
        extra = verify_path_ids - intent_paths
        if missing:
            v7_errors.append(f"验收路径缺少 INTENT.md 中的路径: {sorted(missing)}")
        if extra:
            v7_errors.append(f"验收路径包含 INTENT.md 中不存在的路径: {sorted(extra)}")

    # 保留能力 ID 一致性
    capability_section = _subsection(gate_section, CAPABILITY_HEADING)
    cap_rows = _table_rows(capability_section, "能力 ID")
    verify_cap_ids = {
        row[0] for row in cap_rows if len(row) >= 1 and CAPABILITY_ID_RE.fullmatch(row[0])
    }
    if intent_caps and verify_cap_ids != intent_caps:
        missing = intent_caps - verify_cap_ids
        extra = verify_cap_ids - intent_caps
        if missing:
            v7_errors.append(f"保留能力核对表缺少 INTENT.md 中的能力: {sorted(missing)}")
        if extra:
            v7_errors.append(f"保留能力核对表包含 INTENT.md 中不存在的能力: {sorted(extra)}")

    # 性能验证结论与 INTENT.md 一致
    perf_section = _subsection(conditional_section, PERF_HEADING)
    if perf_section.strip():
        perf_result_match = re.search(
            r"^-\s*结果[：:]\s*(.+)$", perf_section, re.MULTILINE
        )
        if perf_result_match:
            perf_result = perf_result_match.group(1).strip()
            if intent_has_perf and "不适用" in perf_result:
                v7_errors.append("INTENT.md 有性能要求但验收记录标注性能验证不适用")
            elif not intent_has_perf and "不适用" not in perf_result and "通过" not in perf_result:
                v7_errors.append(f"性能验证结果不明确: {perf_result}")

    # 安全验证结论与 INTENT.md 一致
    security_section = _subsection(conditional_section, SECURITY_HEADING)
    if security_section.strip():
        sec_result_match = re.search(
            r"^-\s*结果[：:]\s*(.+)$", security_section, re.MULTILINE
        )
        if sec_result_match:
            sec_result = sec_result_match.group(1).strip()
            if intent_has_security and "不适用" in sec_result:
                v7_errors.append("INTENT.md 有安全要求但验收记录标注安全验证不适用")
            elif not intent_has_security and "不适用" not in sec_result and "通过" not in sec_result:
                v7_errors.append(f"安全验证结果不明确: {sec_result}")

    if v7_errors:
        results.append(("V7", "FAIL", "; ".join(v7_errors)))
    else:
        results.append(("V7", "PASS", "与 INTENT.md 交叉校验一致"))

    return results


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: python verify_validate.py /path/to/intent-chain/{链路目录}/verify-record.md /path/to/intent-chain/{链路目录}/intent.md")
        return 1

    verify_path = Path(sys.argv[1])
    intent_path = Path(sys.argv[2])

    if not verify_path.exists():
        print(f"FAIL: VERIFY-RECORD 文件不存在: {verify_path}")
        return 1
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 文件不存在: {intent_path}")
        return 1

    verify_content = verify_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    results = validate(verify_content, intent_content)

    print(f"\n{'=' * 60}")
    print(f"VERIFY-RECORD 校验结果: {verify_path}")
    print(f"INTENT.md: {intent_path}")
    print(f"{'=' * 60}\n")

    fail_count = 0
    for check_id, status, message in results:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {icon} {check_id}: {message}")
        if status == "FAIL":
            fail_count += 1

    print(f"\n{'=' * 60}")
    if fail_count:
        print(f"  FAIL: {fail_count}")
        print("  结论: 结构不符合当前契约，不得交付")
        return 1
    print("  结论: 结构符合当前契约；内容仍需用户复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
