#!/usr/bin/env python3
"""Issues 文件结构与 INTENT.md、PRD 交叉引用校验。

用法：
  python issues_validate.py /path/to/intent-chain/{链路目录}/issues.md /path/to/intent-chain/{链路目录}/intent.md /path/to/intent-chain/{链路目录}/prd.md /path/to/intent-chain/{链路目录}/architecture.md

检查项：
  V1: 文件非空
  V2: 每个工单包含必需子节；类型字段不得使用内部术语 AFK/HITL（应写 自动完成 / 需人工参与）
  V3: 所有验收路径被至少一个工单覆盖（交叉检查 INTENT.md）
  V4: 所有保留能力被至少一个工单覆盖（交叉检查 INTENT.md）
  V5: Coverage Verification 节存在且包含三个子节
  V6: INTENT.md 有设计标准时，至少一个工单的 Acceptance criteria 包含"对照"（交叉检查 INTENT.md）
  V7: INTENT.md 有术语表时，至少一个工单的 Acceptance criteria 引用了术语表中的术语（交叉检查 INTENT.md）
  V8: INTENT.md 有性能要求时，所有性能要求 ID 被至少一个工单引用（交叉检查 INTENT.md）
  V9: INTENT.md 有安全要求时，所有安全要求 ID 被至少一个工单引用（交叉检查 INTENT.md）
  V10: PRD 中每条验收路径的 Then/And 条件数量不少于工单中对应路径的条目数（交叉检查 PRD）
  V11: 工单的"涉及模块"引用的模块名必须在 architecture.md 第 2 节中定义（强制检查 architecture.md）
  V12: 数据管理类工单（标题/做什么含 档案/配置/模板/账号/角色/商品/规则）必须分条覆盖新增/编辑/删除，显式「不做什么」可豁免单动作
  V13: 真值追溯——INTENT 有页面清单时，「真值追溯」节必须把每个页面 ID 映射到存在的工单，且不得包含未知页面

本脚本不能验证工单的技术可行性，也不能证明内容一定符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 公共 Markdown 解析函数
_COMMON_DIR = Path(__file__).resolve().parent.parent.parent / "_common"
if str(_COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(_COMMON_DIR))
from markdown_parser import (
    ISSUES_HEADING_ALIASES,
    PRD_HEADING_ALIASES,
    normalize_legacy_headings,
    section as _section,
    table_rows as _table_rows,
    has_placeholder as _has_placeholder,
)


REQUIRED_ISSUE_SUBSECTIONS = [
    "### 做什么",
    "### 验收标准",
    "### 前置依赖",
    "### 覆盖的用户故事",
]

COVERAGE_SUBSECTIONS = [
    "### 验收路径覆盖",
    "### 保留能力覆盖",
    "### 新增能力",
]

CAPABILITY_ID_RE = re.compile(r"C\d{2,}")
PATH_ID_RE = re.compile(r"P\d{2,}")
PERF_ID_RE = re.compile(r"PF\d{2,}")
SECURITY_ID_RE = re.compile(r"SF\d{2,}")
ISSUE_HEADING_RE = re.compile(r"^##\s+Issue\s+\d+", re.MULTILINE)
ISSUE_TYPE_RE = re.compile(r"^-\s*\*\*类型\*\*[：:]\s*(.+)$", re.MULTILINE)
MANAGE_HINT_RE = re.compile(r"档案|配置|模板|账号|角色|商品|规则")
CREATE_RE = re.compile(r"新增")
EDIT_RE = re.compile(r"编辑")
DELETE_RE = re.compile(r"删除")
THEN_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(?:Then|And):\s*(.+)$", re.MULTILINE)

# PRD Acceptance Criteria 中的 Then/And 行
PRD_THEN_RE = re.compile(r"^\s*-\s*\*\*Then\*\*\s*(.+)$", re.MULTILINE)
PRD_AND_RE = re.compile(r"^\s*-\s*\*\*And\*\*\s*(.+)$", re.MULTILINE)
# Issues Acceptance criteria 中的 Then/And 行
ISSUE_THEN_RE = re.compile(r"^\s*-\s*\[.\]\s*Then:\s*(.+)$", re.MULTILINE)
ISSUE_AND_RE = re.compile(r"^\s*-\s*\[.\]\s*And:\s*(.+)$", re.MULTILINE)


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


def _parse_perf_requirements(intent_content: str) -> set[str]:
    """从 INTENT.md 第 15 节提取性能要求 ID。"""
    section = _section(intent_content, "## 15. 性能要求")
    rows = _table_rows(section, "要求 ID")
    return {row[0] for row in rows if len(row) >= 1 and PERF_ID_RE.fullmatch(row[0])}


def _parse_security_requirements(intent_content: str) -> set[str]:
    """从 INTENT.md 第 16 节提取安全要求 ID。"""
    section = _section(intent_content, "## 16. 安全要求")
    rows = _table_rows(section, "要求 ID")
    return {row[0] for row in rows if len(row) >= 1 and SECURITY_ID_RE.fullmatch(row[0])}


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


def _count_prd_thens_per_path(prd_content: str) -> dict[str, int]:
    """从 PRD 的 Acceptance Criteria 中统计每条路径的 Then/And 条目数。"""
    criteria_section = _section(prd_content, "## 验收标准")
    result: dict[str, int] = {}
    # 按 ### P01: ... 拆分
    path_blocks = re.split(r"(?=^###\s+P\d{2,})", criteria_section, flags=re.MULTILINE)
    for block in path_blocks:
        path_match = PATH_ID_RE.match(block.strip())
        if not path_match:
            continue
        path_id = path_match.group(0)
        then_count = len(PRD_THEN_RE.findall(block)) + len(PRD_AND_RE.findall(block))
        if then_count > 0:
            result[path_id] = then_count
    return result


def _parse_architecture_modules(arch_content: str) -> set[str]:
    """从 architecture.md 第 2 节提取模块名。"""
    section = _section(arch_content, "## 2. 模块与边界")
    rows = _table_rows(section, "模块")
    return {row[0] for row in rows if len(row) >= 1 and not _has_placeholder(row[0])}


def _extract_issue_modules(issue: str) -> set[str]:
    """从工单的"涉及模块"子节提取模块名列表项。"""
    modules_match = re.search(
        r"### 涉及模块\s*\n(.*?)(?=^###\s+|\Z)",
        issue,
        re.MULTILINE | re.DOTALL,
    )
    if not modules_match:
        return set()
    modules_text = modules_match.group(1)
    # 提取列表项中的模块名，跳过注释和占位符
    modules = re.findall(r"^-\s+(.+)$", modules_text, re.MULTILINE)
    return {m.strip() for m in modules if m.strip() and not m.strip().startswith("{")}


def _count_issue_thens_per_path(issues: list[str]) -> dict[str, int]:
    """从工单的 Acceptance criteria 中统计每条路径的 Then/And 条目数。"""
    result: dict[str, int] = {}
    for issue in issues:
        criteria_match = re.search(
            r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
            issue,
            re.MULTILINE | re.DOTALL,
        )
        if not criteria_match:
            continue
        criteria_text = criteria_match.group(1)
        path_ids = PATH_ID_RE.findall(criteria_text)
        then_count = len(ISSUE_THEN_RE.findall(criteria_text)) + len(ISSUE_AND_RE.findall(criteria_text))
        for pid in set(path_ids):
            result[pid] = result.get(pid, 0) + then_count
    return result


def validate(issues_content: str, intent_content: str, prd_content: str = "", architecture_content: str = "") -> list[tuple[str, str, str]]:
    issues_content = normalize_legacy_headings(issues_content, ISSUES_HEADING_ALIASES)
    if prd_content:
        prd_content = normalize_legacy_headings(prd_content, PRD_HEADING_ALIASES)
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
            type_m = ISSUE_TYPE_RE.search(issue)
            if type_m and re.search(r"\b(AFK|HITL)\b", type_m.group(1), re.IGNORECASE):
                missing_subs.append(
                    f"Issue {i} 的类型字段使用了内部术语 AFK/HITL，用户可见处须写「自动完成 / 需人工参与」"
                )
        if missing_subs:
            results.append(("V2", "FAIL", "; ".join(missing_subs)))
        else:
            results.append(("V2", "PASS", f"全部 {len(issues)} 个工单包含必需子节"))

    # 解析 INTENT.md
    retained_caps = _parse_retained_capabilities(intent_content)
    acceptance_paths = _parse_acceptance_paths(intent_content)
    perf_ids = _parse_perf_requirements(intent_content)
    security_ids = _parse_security_requirements(intent_content)

    # V3: 验收路径覆盖
    found_paths: set[str] = set()
    for issue in issues:
        criteria_match = re.search(
            r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
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
            r"### 覆盖的用户故事\s*\n(.*?)(?=^###\s+|\Z)",
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
    coverage_section = _section(issues_content, "## 覆盖核对")
    coverage_errors: list[str] = []
    if not coverage_section:
        coverage_errors.append("缺少「覆盖核对」节")
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
        results.append(("V5", "PASS", "覆盖核对完整且与 INTENT.md 一致"))

    # V6: 设计标准传递检查
    has_design, _design_paths = _parse_design_standards(intent_content)
    if has_design:
        found_design_ref = False
        for issue in issues:
            criteria_match = re.search(
                r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
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
                r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
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

    # V8: 性能要求传递检查
    if perf_ids:
        found_perf: set[str] = set()
        for issue in issues:
            criteria_match = re.search(
                r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
                issue,
                re.MULTILINE | re.DOTALL,
            )
            if criteria_match:
                found_perf.update(PERF_ID_RE.findall(criteria_match.group(1)))
        missing_perf = perf_ids - found_perf
        if missing_perf:
            results.append(("V8", "FAIL", f"性能要求未被任何工单引用: {sorted(missing_perf)}"))
        else:
            results.append(("V8", "PASS", f"全部 {len(perf_ids)} 个性能要求被工单引用"))
    else:
        results.append(("V8", "PASS", "INTENT.md 无性能要求，不适用"))

    # V9: 安全要求传递检查
    if security_ids:
        found_sec: set[str] = set()
        for issue in issues:
            criteria_match = re.search(
                r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)",
                issue,
                re.MULTILINE | re.DOTALL,
            )
            if criteria_match:
                found_sec.update(SECURITY_ID_RE.findall(criteria_match.group(1)))
        missing_sec = security_ids - found_sec
        if missing_sec:
            results.append(("V9", "FAIL", f"安全要求未被任何工单引用: {sorted(missing_sec)}"))
        else:
            results.append(("V9", "PASS", f"全部 {len(security_ids)} 个安全要求被工单引用"))
    else:
        results.append(("V9", "PASS", "INTENT.md 无安全要求，不适用"))

    # V10: PRD Then 覆盖检查
    if prd_content:
        prd_then_counts = _count_prd_thens_per_path(prd_content)
        issue_then_counts = _count_issue_thens_per_path(issues)
        v10_errors: list[str] = []
        for path_id, prd_count in prd_then_counts.items():
            issue_count = issue_then_counts.get(path_id, 0)
            if issue_count < prd_count:
                v10_errors.append(
                    f"路径 {path_id} 在 PRD 中有 {prd_count} 条 Then/And，但工单中只有 {issue_count} 条"
                )
        if v10_errors:
            results.append(("V10", "FAIL", "; ".join(v10_errors)))
        else:
            results.append(("V10", "PASS", "PRD 中所有验收路径的 Then/And 条件被工单覆盖"))
    else:
        results.append(("V10", "PASS", "未提供 PRD，跳过 Then 覆盖检查"))

    # V11: 架构模块引用检查（强制——intent-design 是 intent-chain 的必经环节）
    if not architecture_content:
        results.append(("V11", "FAIL", "未提供 architecture.md；intent-design 是必经环节，architecture.md 必须存在"))
    else:
        arch_modules = _parse_architecture_modules(architecture_content)
        if not arch_modules:
            results.append(("V11", "FAIL", "architecture.md 第 2 节无模块定义"))
        else:
            v11_errors: list[str] = []
            for i, issue in enumerate(issues, 1):
                modules_text = re.search(
                    r"### 涉及模块\s*\n(.*?)(?=^###\s+|\Z)",
                    issue,
                    re.MULTILINE | re.DOTALL,
                )
                if not modules_text:
                    v11_errors.append(f"Issue {i} 缺少涉及模块子节")
                else:
                    issue_modules = _extract_issue_modules(issue)
                    undefined = issue_modules - arch_modules
                    if undefined:
                        v11_errors.append(f"Issue {i} 引用了架构文档中未定义的模块: {sorted(undefined)}")
            if v11_errors:
                results.append(("V11", "FAIL", "; ".join(v11_errors)))
            else:
                results.append(("V11", "PASS", f"全部工单的涉及模块引用了架构文档中定义的模块"))

    # V12: 数据管理类工单必须分条覆盖新增/编辑/删除；显式「不做什么」可豁免单动作
    v12_errors: list[str] = []
    for i, issue in enumerate(issues, 1):
        title_match = re.search(r"^##\s+Issue\s+\d+:\s*(.+)$", issue, re.MULTILINE)
        title = title_match.group(1) if title_match else ""
        do_match = re.search(r"### 做什么\s*\n(.*?)(?=^###\s+|\Z)", issue, re.MULTILINE | re.DOTALL)
        do_text = do_match.group(1) if do_match else ""
        crit_match = re.search(r"### 验收标准\s*\n(.*?)(?=^###\s+|\Z)", issue, re.MULTILINE | re.DOTALL)
        crit_text = crit_match.group(1) if crit_match else ""
        if re.search(MANAGE_HINT_RE, title + do_text):
            then_texts = [m.group(1) for m in THEN_LINE_RE.finditer(crit_text)]
            create_lines = {j for j, t in enumerate(then_texts) if CREATE_RE.search(t)}
            edit_lines = {j for j, t in enumerate(then_texts) if EDIT_RE.search(t)}
            delete_lines = {j for j, t in enumerate(then_texts) if DELETE_RE.search(t)}
            not_do_match = re.search(r"###\s*不做什么\s*\n(.*?)(?=^###\s+|\Z)", issue, re.MULTILINE | re.DOTALL)
            not_do_text = not_do_match.group(1) if not_do_match else ""

            missing: list[str] = []
            if not create_lines and not re.search(r"(不支持|不做|无需)\s*新增", not_do_text):
                missing.append("缺「新增」")
            if not edit_lines and not re.search(r"(不支持|不做|无需)\s*编辑", not_do_text):
                missing.append("缺「编辑」")
            if not delete_lines and not re.search(r"(不支持|不做|无需)\s*删除", not_do_text):
                missing.append("缺「删除」")
            present_actions = (1 if create_lines else 0) + (1 if edit_lines else 0) + (1 if delete_lines else 0)
            present_lines = create_lines | edit_lines | delete_lines
            if not missing and len(present_lines) < present_actions:
                missing.append("写操作未分条（新增/编辑/删除需各一条 Then）")
            if missing:
                v12_errors.append(f"Issue {i} 疑似管理/维护类工单: {'; '.join(missing)}")
    if v12_errors:
        results.append(("V12", "FAIL", "; ".join(v12_errors)))
    else:
        results.append(("V12", "PASS", "数据管理类工单均分条覆盖新增/编辑/删除"))

    # V13: 真值追溯——INTENT 有页面清单时，每个页面 ID 必须在「真值追溯」节映射到工单
    page_section = _section(intent_content, "## 17. 页面清单")
    page_ids = {
        row[0]
        for row in _table_rows(page_section, "页面 ID")
        if row and row[0] and not _has_placeholder(row[0])
    }
    if page_ids:
        trace_section = _section(issues_content, "### 真值追溯")
        trace_rows = _table_rows(trace_section, "页面 ID")
        traced_pages = {row[0] for row in trace_rows if row and row[0]}
        covered_issue_ids = set(re.findall(r"^##\s+Issue\s+(\d+)", issues_content, re.MULTILINE))
        v13_errors: list[str] = []
        for pg in sorted(page_ids - traced_pages):
            v13_errors.append(f"页面 {pg} 未出现在真值追溯表")
        for row in trace_rows:
            if not row or len(row) < 2:
                continue
            pg, issue_ref = row[0], row[1]
            if pg not in page_ids:
                v13_errors.append(f"真值追溯表包含未知页面：{pg}（不在 INTENT 第 17 节）")
            m = re.search(r"(\d+)", issue_ref)
            if not m or m.group(1) not in covered_issue_ids:
                v13_errors.append(f"页面 {pg} 映射的工单不存在：{issue_ref}")
        if v13_errors:
            results.append(("V13", "FAIL", "; ".join(v13_errors)))
        else:
            results.append(("V13", "PASS", f"真值追溯完整：{len(page_ids)} 页全部映射到工单"))
    else:
        results.append(("V13", "PASS", "INTENT 无页面清单，真值追溯不适用"))

    return results


def main() -> int:
    if len(sys.argv) < 5:
        print("用法: python issues_validate.py /path/to/intent-chain/{链路目录}/issues.md /path/to/intent-chain/{链路目录}/intent.md /path/to/intent-chain/{链路目录}/prd.md /path/to/intent-chain/{链路目录}/architecture.md")
        return 1

    issues_path = Path(sys.argv[1])
    intent_path = Path(sys.argv[2])
    prd_path = Path(sys.argv[3])
    arch_path = Path(sys.argv[4])

    if not issues_path.exists():
        print(f"FAIL: Issues 文件不存在: {issues_path}")
        return 1
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 文件不存在: {intent_path}")
        return 1
    if not prd_path.exists():
        print(f"FAIL: PRD 文件不存在: {prd_path}")
        return 1
    if not arch_path.exists():
        print(f"FAIL: architecture.md 不存在: {arch_path}")
        return 1

    issues_content = issues_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    prd_content = prd_path.read_text(encoding="utf-8")
    architecture_content = arch_path.read_text(encoding="utf-8")
    results = validate(issues_content, intent_content, prd_content, architecture_content)

    print(f"\n{'=' * 60}")
    print(f"Issues 校验结果: {issues_path}")
    print(f"INTENT.md: {intent_path}")
    print(f"PRD: {prd_path}")
    print(f"Architecture: {arch_path}")
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
