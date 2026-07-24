#!/usr/bin/env python3
"""PRD 结构与 INTENT.md 交叉引用校验。

用法：
  python prd_validate.py /path/to/intent-chain/{链路目录}/PRD.md /path/to/intent-chain/{链路目录}/INTENT.md

检查项：
  V1: PRD 文件非空
  V2: 8 个必需章节齐全
  V3: 所有保留能力 ID 出现在 User Stories 中（交叉检查 INTENT.md）
  V4: 所有验收路径 ID 出现在 Acceptance Criteria 中（交叉检查 INTENT.md）
  V5: INTENT.md 有设计标准时，PRD 引用了设计素材路径
  V6: INTENT.md 有术语表时，PRD 引用了术语约束
  V7: Intent Verification 包含三个子节且有表格结构
  V8: 每条验收路径使用 Given/When/Then 结构描述验收条件

本脚本不能验证 PRD 的技术方案是否合理，也不能证明内容一定符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "## Problem Statement",
    "## Solution",
    "## User Stories",
    "## Implementation Decisions",
    "## Acceptance Criteria",
    "## Testing Decisions",
    "## Out of Scope",
    "## Intent Verification",
]

VERIFICATION_SUBSECTIONS = [
    "### 保留能力覆盖",
    "### 不可妥协项核对",
    "### 新增能力",
]

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
    match = re.search(
        rf"^###\s+{re.escape(heading)}\s*$\n?(.*?)(?=^###\s+|^##\s+|\Z)",
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


def _has_placeholder(value: str) -> bool:
    return bool(re.search(r"\{[^{}]+\}", value))


def _parse_retained_capabilities(intent_content: str) -> set[str]:
    """从 INTENT.md 第 4 节提取保留能力的 ID。"""
    section = _section(intent_content, "## 4. 能力与决策")
    rows = _table_rows(section, "能力 ID")
    retained: set[str] = set()
    for row in rows:
        if len(row) >= 5 and row[4] == "保留":
            retained.add(row[0])
    return retained


def _parse_acceptance_paths(intent_content: str) -> set[str]:
    """从 INTENT.md 第 14 节提取验收路径 ID。"""
    section = _section(intent_content, "## 14. 验收路径")
    rows = _table_rows(section, "路径 ID")
    return {row[0] for row in rows if len(row) >= 1 and PATH_ID_RE.fullmatch(row[0])}


def _parse_design_standards(intent_content: str) -> tuple[bool, list[str]]:
    """从 INTENT.md 第 12 节提取设计标准。

    返回 (has_standards, paths)。
    """
    section = _section(intent_content, "## 12. 设计标准")
    rows = _table_rows(section, "设计素材 ID")
    if rows:
        paths = [row[2] for row in rows if len(row) >= 3 and not _has_placeholder(row[2])]
        return True, paths
    return False, []


def _parse_terminology(intent_content: str) -> tuple[bool, list[str]]:
    """从 INTENT.md 第 13 节提取术语表。

    返回 (has_terms, terms)。
    """
    section = _section(intent_content, "## 13. 术语表")
    rows = _table_rows(section, "原始术语")
    if rows:
        terms = [row[0] for row in rows if len(row) >= 1 and not _has_placeholder(row[0])]
        return True, terms
    return False, []


def _parse_non_negotiables(intent_content: str) -> set[str]:
    """从 INTENT.md 第 5 节提取不可妥协项的能力 ID。"""
    section = _section(intent_content, "## 5. 不可妥协项")
    rows = _table_rows(section, "能力 ID")
    return {row[0] for row in rows if len(row) >= 1 and CAPABILITY_ID_RE.fullmatch(row[0])}


def validate(prd_content: str, intent_content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)；结果为 PASS / FAIL。"""
    results: list[tuple[str, str, str]] = []

    # V1: PRD 非空
    if prd_content.strip():
        results.append(("V1", "PASS", f"文件有 {len(prd_content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    # V2: 必需章节
    missing = [s for s in REQUIRED_SECTIONS if s not in prd_content]
    if missing:
        results.append(("V2", "FAIL", f"缺少章节: {', '.join(missing)}"))
    else:
        results.append(("V2", "PASS", "全部 8 个章节存在"))

    # 解析 INTENT.md
    retained_caps = _parse_retained_capabilities(intent_content)
    acceptance_paths = _parse_acceptance_paths(intent_content)
    has_design, design_paths = _parse_design_standards(intent_content)
    has_terms, terms = _parse_terminology(intent_content)
    non_negotiables = _parse_non_negotiables(intent_content)

    # V3: 保留能力出现在 User Stories 中
    stories_section = _section(prd_content, "## User Stories")
    found_in_stories = set(CAPABILITY_ID_RE.findall(stories_section))
    missing_caps = retained_caps - found_in_stories
    if missing_caps:
        results.append((
            "V3", "FAIL",
            f"保留能力未出现在 User Stories 中: {sorted(missing_caps)}",
        ))
    else:
        results.append(("V3", "PASS", f"全部 {len(retained_caps)} 项保留能力出现在 User Stories 中"))

    # V4: 验收路径出现在 Acceptance Criteria 中
    criteria_section = _section(prd_content, "## Acceptance Criteria")
    found_paths = set(PATH_ID_RE.findall(criteria_section))
    missing_paths = acceptance_paths - found_paths
    if missing_paths:
        results.append((
            "V4", "FAIL",
            f"验收路径未出现在 Acceptance Criteria 中: {sorted(missing_paths)}",
        ))
    else:
        results.append(("V4", "PASS", f"全部 {len(acceptance_paths)} 条验收路径出现在 Acceptance Criteria 中"))

    # V5: 设计标准引用
    impl_section = _section(prd_content, "## Implementation Decisions")
    if has_design:
        design_referenced = all(
            any(path in line for line in impl_section.splitlines())
            for path in design_paths
        )
        if design_referenced:
            results.append(("V5", "PASS", f"引用了 {len(design_paths)} 个设计素材路径"))
        else:
            results.append(("V5", "FAIL", "INTENT.md 有设计标准但 PRD 未引用设计素材路径"))
    else:
        results.append(("V5", "PASS", "INTENT.md 无设计标准，不适用"))

    # V6: 术语表引用
    if has_terms:
        terms_section = _subsection(impl_section, "Terminology Constraints")
        if terms_section:
            found_terms = sum(
                1 for term in terms
                if any(term in line for line in terms_section.splitlines())
            )
            if found_terms == len(terms):
                results.append(("V6", "PASS", f"引用了 {len(terms)} 个术语"))
            else:
                results.append(("V6", "FAIL", f"术语引用不完整: {found_terms}/{len(terms)}"))
        else:
            results.append(("V6", "FAIL", "INTENT.md 有术语表但 PRD 缺少 Terminology Constraints 子节"))
    else:
        results.append(("V6", "PASS", "INTENT.md 无术语表，不适用"))

    # V7: Intent Verification 子节
    verification_section = _section(prd_content, "## Intent Verification")
    verification_errors: list[str] = []
    for sub in VERIFICATION_SUBSECTIONS:
        if sub not in verification_section:
            verification_errors.append(f"缺少子节: {sub}")

    if not verification_errors:
        # 检查保留能力覆盖表
        coverage_sub = _subsection(verification_section, "保留能力覆盖")
        coverage_rows = _table_rows(coverage_sub, "能力 ID")
        coverage_ids = {row[0] for row in coverage_rows if len(row) >= 1 and CAPABILITY_ID_RE.fullmatch(row[0])}
        if coverage_ids != retained_caps:
            missing_cov = retained_caps - coverage_ids
            extra_cov = coverage_ids - retained_caps
            if missing_cov:
                verification_errors.append(f"保留能力覆盖表缺少: {sorted(missing_cov)}")
            if extra_cov:
                verification_errors.append(f"保留能力覆盖表有多余项: {sorted(extra_cov)}")

        # 检查不可妥协项核对表
        nn_sub = _subsection(verification_section, "不可妥协项核对")
        if non_negotiables:
            nn_rows = _table_rows(nn_sub, "能力 ID")
            nn_ids = {row[0] for row in nn_rows if len(row) >= 1 and CAPABILITY_ID_RE.fullmatch(row[0])}
            if nn_ids != non_negotiables:
                verification_errors.append(f"不可妥协项核对表与 INTENT.md 不一致")
        elif "不适用" not in nn_sub and "无" not in nn_sub:
            verification_errors.append("INTENT.md 无不可妥协项时，应写\"不适用\"")

        # 检查新增能力表
        new_sub = _subsection(verification_section, "新增能力")
        if not new_sub.strip():
            verification_errors.append("新增能力子节为空")
        elif not _table_rows(new_sub, "新增内容") and "无" not in new_sub:
            verification_errors.append("新增能力子节缺少表格或\"无\"声明")

    if verification_errors:
        results.append(("V7", "FAIL", "; ".join(verification_errors)))
    else:
        results.append(("V7", "PASS", "Intent Verification 子节完整且与 INTENT.md 一致"))

    # V8: 每条验收路径使用 Given/When/Then 结构
    gwt_errors: list[str] = []
    for path_id in sorted(acceptance_paths):
        path_block = re.search(
            rf"###\s+{re.escape(path_id)}[:\s].*?(?=^###\s+|\Z)",
            criteria_section,
            re.MULTILINE | re.DOTALL,
        )
        if not path_block:
            gwt_errors.append(f"验收路径 {path_id} 缺少场景块（### {path_id}: ...）")
            continue
        block_text = path_block.group(0)
        if not re.search(r"\bGiven\b", block_text):
            gwt_errors.append(f"{path_id} 缺少 Given（前置条件）")
        if not re.search(r"\bWhen\b", block_text):
            gwt_errors.append(f"{path_id} 缺少 When（触发操作）")
        if not re.search(r"\bThen\b", block_text):
            gwt_errors.append(f"{path_id} 缺少 Then（预期结果）")

    if gwt_errors:
        results.append(("V8", "FAIL", "; ".join(gwt_errors)))
    else:
        results.append(("V8", "PASS", f"全部 {len(acceptance_paths)} 条验收路径使用 Given/When/Then 结构"))

    return results


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: python prd_validate.py /path/to/intent-chain/{链路目录}/PRD.md /path/to/intent-chain/{链路目录}/INTENT.md")
        return 1

    prd_path = Path(sys.argv[1])
    intent_path = Path(sys.argv[2])

    if not prd_path.exists():
        print(f"FAIL: PRD 文件不存在: {prd_path}")
        return 1
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 文件不存在: {intent_path}")
        return 1

    prd_content = prd_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    results = validate(prd_content, intent_content)

    print(f"\n{'=' * 60}")
    print(f"PRD 校验结果: {prd_path}")
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
        print("  结论: 结构不符合当前契约，不得交接")
        return 1
    print("  结论: 结构符合当前契约；内容仍需用户复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
