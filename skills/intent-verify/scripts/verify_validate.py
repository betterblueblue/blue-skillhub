#!/usr/bin/env python3
"""VERIFY-RECORD.md 结构校验。

用法：
  python verify_validate.py /path/to/intent-chain/{链路目录}/VERIFY-RECORD.md

检查项：
  V1: 文件非空
  V2: 有回归验证段（全量测试命令和结果）
  V3: 有端到端验收结果段（每条路径有 Given/When/Then 和验证方式）
  V4: 每条路径有 V3 证据
  V5: 有条件性验证段（性能验证和安全验证，不适用也要标注）
  V6: 最终复核完整（回归汇总、保留能力核对、验收路径验证、条件性汇总、漂移复核、结论）

本脚本不能验证 V3 证据是否真实，也不能证明验收结果符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PATH_HEADING_RE = re.compile(r"^###\s+路径\s+P\d+:\s*(.+)$", re.MULTILINE)
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


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


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


def _has_v3_evidence(path_content: str) -> bool:
    """检查路径中是否有 V3 证据。"""
    then_lines = _parse_then_lines(path_content)
    for check, text, level in then_lines:
        if level == "V3":
            return True
    return False


def validate(verify_content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)。"""
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if verify_content.strip():
        results.append(("V1", "PASS", f"文件有 {len(verify_content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    # V2: 有回归验证段（全量测试命令和结果）
    regression_section = _section(verify_content, REGRESSION_HEADING)
    if not regression_section.strip():
        results.append(("V2", "FAIL", "缺少回归验证结果段"))
    else:
        v2_errors: list[str] = []
        if "全量测试命令" not in regression_section:
            v2_errors.append("缺少全量测试命令")
        if "结果" not in regression_section:
            v2_errors.append("缺少结果行")
        if v2_errors:
            results.append(("V2", "FAIL", "; ".join(v2_errors)))
        else:
            results.append(("V2", "PASS", "回归验证段完整"))

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

    # V4: 每条路径有 V3 证据
    v4_errors: list[str] = []
    for path in paths:
        heading_match = PATH_HEADING_RE.search(path)
        path_label = heading_match.group(0) if heading_match else "未知路径"
        if not _has_v3_evidence(path):
            v4_errors.append(f"{path_label} 缺少 V3 证据")
    if v4_errors:
        results.append(("V4", "FAIL", "; ".join(v4_errors)))
    else:
        results.append(("V4", "PASS", f"全部 {len(paths)} 条路径有 V3 证据"))

    # V5: 有条件性验证段（性能验证和安全验证，不适用也要标注）
    conditional_section = _section(verify_content, CONDITIONAL_HEADING)
    if not conditional_section.strip():
        results.append(("V5", "FAIL", "缺少条件性验证结果段"))
    else:
        v5_errors: list[str] = []
        if not _section(conditional_section, PERF_HEADING).strip():
            v5_errors.append("缺少性能验证段")
        if not _section(conditional_section, SECURITY_HEADING).strip():
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
        if not _section(gate_section, REGRESSION_SUMMARY_HEADING).strip():
            v6_errors.append("缺少回归验证结果汇总")
        if not _section(gate_section, CAPABILITY_HEADING).strip():
            v6_errors.append("缺少保留能力逐项核对")
        path_table = _section(gate_section, PATH_TABLE_HEADING)
        if not path_table.strip():
            v6_errors.append("缺少验收路径逐条验证")
        elif not re.findall(r"V3", path_table):
            v6_errors.append("验收路径逐条验证缺少 V3")
        if not _section(gate_section, CONDITIONAL_SUMMARY_HEADING).strip():
            v6_errors.append("缺少条件性验证结果汇总")
        if not _section(gate_section, DRIFT_HEADING).strip():
            v6_errors.append("缺少漂移复核")
        conclusion = _section(gate_section, CONCLUSION_HEADING)
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

    return results


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python verify_validate.py /path/to/intent-chain/{链路目录}/VERIFY-RECORD.md")
        return 1

    verify_path = Path(sys.argv[1])

    if not verify_path.exists():
        print(f"FAIL: VERIFY-RECORD 文件不存在: {verify_path}")
        return 1

    verify_content = verify_path.read_text(encoding="utf-8")
    results = validate(verify_content)

    print(f"\n{'=' * 60}")
    print(f"VERIFY-RECORD 校验结果: {verify_path}")
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
