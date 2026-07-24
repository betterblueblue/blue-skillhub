#!/usr/bin/env python3
"""Issues 文件结构与 INTENT.md 交叉引用校验。

用法：
  python issues_validate.py /path/to/intent-chain/{链路目录}/issues.md /path/to/intent-chain/{链路目录}/intent.md

检查项：
  V1: 文件非空
  V2: 每个工单包含必需子节
  V3: 所有验收路径被至少一个工单覆盖（交叉检查 INTENT.md）
  V4: 所有保留能力被至少一个工单覆盖（交叉检查 INTENT.md）
  V5: Coverage Verification 节存在且包含三个子节
  V6: INTENT.md 有设计标准时，至少一个工单的 Acceptance criteria 包含"对照"（交叉检查 INTENT.md）
  V7: INTENT.md 有术语表时，至少一个工单的 Acceptance criteria 引用了术语表中的术语（交叉检查 INTENT.md）

本脚本不能验证工单的技术可行性，也不能证明内容一定符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_ISSUE_SUBSECTIONS = [
    "### What to build",
    "### Acceptance criteria",
    "### Blocked by",
    "### User stories covered",
]

COVERAGE_SUBSECTIONS = [
    "### 验收路径覆盖",
    "### 保留能力覆盖",
    "### 新增能力",
]

CAPABILITY_ID_RE = re.compile(r"C\d{2,}")
PATH_ID_RE = re.compile(r"P\d{2,}")
ISSUE_HEADING_RE = re.compile(r"^##\s+Issue\s+\d+", re.MULTILINE)


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
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


def _parse_retained_capabilities(intent_content: str) -> set[str]:
    section = _section(intent_content, "## 4. 能力与决策")
    rows = _table_rows(section, "能力 ID")
    return {row[0] for row in rows if len(row) >= 5 and row[4] == "保留"}


def _parse_acceptance_paths(intent_content: str) -> set[str]:
    section = _section(intent_content, "## 14. 验收路径")
    rows = _table_rows(section, "路径 ID")
    return {row[0] for row in rows if len(row) >= 1 and PATH_ID_RE.fullmatch(row[0])}


def _split_issues(content: str) -> list[str]:
    """按 ## Issue N: 标题 拆分工单段落。"""
    issue_starts = [(m.start(), m.end()) for m in ISSUE_HEADING_RE.finditer(content)]
    if not issue_starts:
        return []
    issues: list[str] = []
    for i, (start, _end) in enumerate(issue_starts):
        end = issue_starts[i + 1][0] if i + 1 < len(issue_starts) else None
        if end is None:
            # 最后一个 issue 到 Coverage Verification 或文件结尾
            cov_match = re.search(r"^##\s+Coverage\s+Verification", content[start:], re.MULTILINE)
            end = start + cov_match.start() if cov_match else len(content)
        issues.append(content[start:end])
    return issues


def validate(issues_content: str, intent_content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)。"""
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if issues_content.strip():
        results.append(("V1", "PASS", f"文件有 {len(issues_content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    # V2: 每个工单包含必需子节
    issues = _split_issues(issues_content)
    if not issues:
        results.append(("V2", "FAIL", "未找到工单（需要 ## Issue N: 标题）"))
    else:
        missing_subs: list[str] = []
        for i, issue in enumerate(issues, 1):
            for sub in REQUIRED_ISSUE_SUBSECTIONS:
                if sub not in issue:
                    missing_subs.append(f"Issue {i} 缺少 {sub}")
        if missing_subs:
            results.append(("V2", "FAIL", "; ".join(missing_subs)))
        else:
            results.append(("V2", "PASS", f"全部 {len(issues)} 个工单包含必需子节"))

    # 解析 INTENT.md
    retained_caps = _parse_retained_capabilities(intent_content)
    acceptance_paths = _parse_acceptance_paths(intent_content)

    # V3: 验收路径覆盖
    found_paths: set[str] = set()
    for issue in issues:
        criteria_match = re.search(
            r"### Acceptance criteria\s*\n(.*?)(?=^###\s+|\Z)",
            issue,
            re.MULTILINE | re.DOTALL,
        )
        if criteria_match:
            found_paths.update(PATH_ID_RE.findall(criteria_match.group(1)))
    missing_paths = acceptance_paths - found_paths
    if missing_paths:
        results.append((
            "V3", "FAIL",
            f"验收路径未被任何工单覆盖: {sorted(missing_paths)}",
        ))
    else:
        results.append(("V3", "PASS", f"全部 {len(acceptance_paths)} 条验收路径被工单覆盖"))

    # V4: 保留能力覆盖
    found_caps: set[str] = set()
    for issue in issues:
        stories_match = re.search(
            r"### User stories covered\s*\n(.*?)(?=^###\s+|\Z)",
            issue,
            re.MULTILINE | re.DOTALL,
        )
        if stories_match:
            found_caps.update(CAPABILITY_ID_RE.findall(stories_match.group(1)))
    missing_caps = retained_caps - found_caps
    if missing_caps:
        results.append((
            "V4", "FAIL",
            f"保留能力未被任何工单覆盖: {sorted(missing_caps)}",
        ))
    else:
        results.append(("V4", "PASS", f"全部 {len(retained_caps)} 项保留能力被工单覆盖"))

    # V5: Coverage Verification
    coverage_section = _section(issues_content, "## Coverage Verification")
    coverage_errors: list[str] = []
    if not coverage_section:
        coverage_errors.append("缺少 Coverage Verification 节")
    else:
        for sub in COVERAGE_SUBSECTIONS:
            if sub not in coverage_section:
                coverage_errors.append(f"缺少子节: {sub}")

        if not coverage_errors:
            path_cov = _table_rows(
                _section(coverage_section, "### 验收路径覆盖"),
                "路径 ID",
            )
            path_cov_ids = {row[0] for row in path_cov if len(row) >= 1 and PATH_ID_RE.fullmatch(row[0])}
            if path_cov_ids != acceptance_paths:
                coverage_errors.append(
                    f"验收路径覆盖表与 INTENT.md 不一致: "
                    f"应为 {sorted(acceptance_paths)}, 实际 {sorted(path_cov_ids)}"
                )

            cap_cov = _table_rows(
                _section(coverage_section, "### 保留能力覆盖"),
                "能力 ID",
            )
            cap_cov_ids = {row[0] for row in cap_cov if len(row) >= 1 and CAPABILITY_ID_RE.fullmatch(row[0])}
            if cap_cov_ids != retained_caps:
                coverage_errors.append("保留能力覆盖表与 INTENT.md 不一致")

            new_section = _section(coverage_section, "### 新增能力")
            if not new_section.strip():
                coverage_errors.append("新增能力子节为空")
            elif not _table_rows(new_section, "新增内容") and "无" not in new_section:
                coverage_errors.append("新增能力子节缺少表格或声明")

    if coverage_errors:
        results.append(("V5", "FAIL", "; ".join(coverage_errors)))
    else:
        results.append(("V5", "PASS", "Coverage Verification 完整且与 INTENT.md 一致"))

    # V6: 设计标准传递检查
    has_design, _design_paths = _parse_design_standards(intent_content)
    if has_design:
        found_design_ref = False
        for issue in issues:
            criteria_match = re.search(
                r"### Acceptance criteria\s*\n(.*?)(?=^###\s+|\Z)",
                issue,
                re.MULTILINE | re.DOTALL,
            )
            if criteria_match and "对照" in criteria_match.group(1):
                found_design_ref = True
                break
        if found_design_ref:
            results.append(("V6", "PASS", "设计标准约束已传递到工单 Acceptance criteria"))
        else:
            results.append(("V6", "FAIL", "INTENT.md 有设计标准但工单 Acceptance criteria 未包含对照设计文件的要求"))
    else:
        results.append(("V6", "PASS", "INTENT.md 无设计标准，不适用"))

    # V7: 术语表传递检查
    has_terms, terms = _parse_terminology(intent_content)
    if has_terms:
        found_term_ref = False
        for issue in issues:
            criteria_match = re.search(
                r"### Acceptance criteria\s*\n(.*?)(?=^###\s+|\Z)",
                issue,
                re.MULTILINE | re.DOTALL,
            )
            if criteria_match:
                for term in terms:
                    if term in criteria_match.group(1):
                        found_term_ref = True
                        break
            if found_term_ref:
                break
        if found_term_ref:
            results.append(("V7", "PASS", f"术语表约束已传递到工单（{len(terms)} 个术语）"))
        else:
            results.append(("V7", "FAIL", "INTENT.md 有术语表但工单未引用任何术语"))
    else:
        results.append(("V7", "PASS", "INTENT.md 无术语表，不适用"))

    return results


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: python issues_validate.py /path/to/intent-chain/{链路目录}/issues.md /path/to/intent-chain/{链路目录}/intent.md")
        return 1

    issues_path = Path(sys.argv[1])
    intent_path = Path(sys.argv[2])

    if not issues_path.exists():
        print(f"FAIL: Issues 文件不存在: {issues_path}")
        return 1
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 文件不存在: {intent_path}")
        return 1

    issues_content = issues_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    results = validate(issues_content, intent_content)

    print(f"\n{'=' * 60}")
    print(f"Issues 校验结果: {issues_path}")
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
