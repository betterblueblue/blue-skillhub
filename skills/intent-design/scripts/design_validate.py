#!/usr/bin/env python3
"""Architecture & Design 结构与交叉引用校验。

用法：
  python design_validate.py /path/to/architecture.md /path/to/design.md /path/to/intent.md

检查项：
  A1: architecture.md 非空
  A2: 6 个必需章节齐全
  A3: 模块表中的能力 ID 存在于 INTENT.md 保留能力
  A4: 模块依赖引用的模块名都已定义
  A5: 技术选型表列非空，「为什么不选另一个」不含禁用词
  A6: 数据流表覆盖 INTENT.md 全部验收路径，模块名都已定义
  A7: 假设表场景列不含抽象词，证据列合规，无依据项已汇总
  A8: 贵决策有详细说明，便宜决策没有多余说明
  D1: design.md 非空
  D2: 每个保留能力都有一节
  D3: 「不做什么」非空
  D4: 不含代码特征词
  D5: 架构一致性核对表存在
  X1: design.md 引用的模块名都在 architecture.md 中定义
  X2: 两份文件引用的能力 ID 集合一致

本脚本不能验证技术方案是否合理，也不能证明内容一定符合
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
    ARCH_HEADING_ALIASES,
    normalize_legacy_headings,
    section as _section,
    subsection as _subsection,
    table_rows as _table_rows,
    has_placeholder as _has_placeholder,
)

# ── 常量 ──────────────────────────────────────────────────────────────────

CAPABILITY_ID_RE = re.compile(r"C\d{2,}")
PATH_ID_RE = re.compile(r"P\d{2,}")

FORBIDDEN_WORDS = [
    "最佳实践", "常见做法", "业界标准", "行业惯例",
    "更成熟", "更稳定", "更灵活", "扩展性", "可维护性", "健壮性",
]

ARCH_REQUIRED_SECTIONS = [
    "## 1. 架构概览",
    "## 2. 模块与边界",
    "## 3. 技术选型",
    "## 4. 关键数据流",
    "## 5. 额外结构与假设",
    "## 6. 关键选型与代价（请重点核对）",
]

DESIGN_REQUIRED_SECTIONS = [
    "## 1. 设计概览",
    "## 2. 能力设计",
    "## 3. 与架构文档的对照",
]

# 代码特征词——出现即 FAIL，属于提高伪造成本，不是杜绝
CODE_PATTERNS = [
    r"\bfunction\s+\w+\s*\(",
    r"\bpublic\s+(class|void|static|String|int|List|Map)\b",
    r"\bdef\s+\w+\s*\(",
    r"\binterface\s+\w+\s*\{",
    r"\bclass\s+\w+\s*\{",
    r"CREATE\s+TABLE",
]

# ── INTENT.md 解析（与 prd_validate.py 一致）─────────────────────────────


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


# ── 辅助函数 ──────────────────────────────────────────────────────────────


def _split_tokens(cell: str) -> list[str]:
    """按分隔符（顿号/逗号/箭头）拆分模块引用。

    不按空白拆分——"CLI 入口"这类含空格的中英混合模块名是一个整体，
    多个模块之间必须用 、 ， , 或 → 分隔。
    """
    return [t.strip() for t in re.split(r"[、，,→]+", cell) if t.strip()]


def _starts_with_cost(cell: str) -> str | None:
    """判断代价列是'便宜'还是'贵'，返回 None 表示无法识别。"""
    cell = cell.strip()
    if cell.startswith("便宜"):
        return "便宜"
    if cell.startswith("贵"):
        return "贵"
    return None


def _strip_html_comments(text: str) -> str:
    """移除 HTML 注释 <!-- ... -->，防止用注释绕过检查。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


# "无额外结构"必须是独立声明行（可带加粗或句尾标点）；
# "并非无额外结构"这类语句的子串不算声明
RE_NO_EXTRA_LINE = re.compile(r"\**无额外结构\**[。．.！!]*")

# 证据白名单：代码位置类特征。CJK 字符也算 \w，\b 在中英文交界处不可靠，
# 所以边界用 ASCII 字母前后查（lookaround）表达。
RE_EVIDENCE_CODE = re.compile(
    r"[/\\]\w+\.\w{1,5}"          # 路径片段：src/service.py、src\a.java
    r"|\w+\.\w{1,5}:\d+"          # 文件:行号
    r"|\w+\.[A-Za-z]{2,5}"        # 裸文件名 / 方法引用：pom.xml、Service.login()
    r"|第\s*\d+\s*行"              # 中文行号：第 45 行
    r"|`[^`]+`"                   # 反引号代码片段：`sys_config`
    r"|(?<![A-Za-z])[A-Za-z][a-z0-9]+[A-Z][A-Za-z0-9]*"  # camelCase / PascalCase 标识符
    r"|[A-Za-z]\w*_\w+"           # snake_case 标识符：config_type
    r"|(?<![A-Za-z])commit\s+[0-9a-f]{7,40}"             # git commit 哈希
)
# 引号包裹的用户原话：直引号、单引号、弯引号、方引号都接受
RE_EVIDENCE_QUOTE = re.compile("[\"'「『“‘].+[\"'」』”’]")
RE_QUOTED_SPAN = re.compile("[\"'「『“‘][^\"'」』”’]*[\"'」』”’]")


def _is_placeholder_row(row: list[str]) -> bool:
    """模板占位行（任一单元格含 {xxx}）不算真实数据行。"""
    return any(_has_placeholder(cell) for cell in row)


def _extract_design_cap_ids(design_section2: str) -> set[str]:
    """从 design.md 第 2 节的 ### [CXX] 标题中提取能力 ID。"""
    return set(re.findall(r"###\s+\[(C\d{2,})\]", design_section2))


def _extract_cap_section(design_section2: str, cap_id: str) -> str:
    """提取某个能力的子节内容。"""
    match = re.search(
        rf"###\s+\[{re.escape(cap_id)}\].*?(?=^###\s+|\Z)",
        design_section2,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else ""


def _extract_field(section_text: str, field_name: str) -> str | None:
    """从能力子节中提取 **字段名** 的值。返回 None 表示字段不存在。"""
    match = re.search(
        rf"\*\*{re.escape(field_name)}\*\*[：:]\s*(.*)",
        section_text,
    )
    return match.group(1).strip() if match else None


# ── 校验主函数 ────────────────────────────────────────────────────────────


def validate(
    arch_content: str,
    design_content: str,
    intent_content: str,
) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)；结果为 PASS / FAIL。"""
    arch_content = normalize_legacy_headings(arch_content, ARCH_HEADING_ALIASES)
    results: list[tuple[str, str, str]] = []

    # 解析 INTENT.md
    retained_caps = _parse_retained_capabilities(intent_content)
    acceptance_paths = _parse_acceptance_paths(intent_content)

    # ═══════════════════════════════════════════════════════════════════════
    # 架构层检查 A1-A8
    # ═══════════════════════════════════════════════════════════════════════

    # A1: architecture.md 非空
    if not arch_content.strip():
        results.append(("A1", "FAIL", "architecture.md 为空"))
        return results
    results.append(("A1", "PASS", f"文件有 {len(arch_content)} 个字符"))

    # A2: 必需章节
    missing = [s for s in ARCH_REQUIRED_SECTIONS if s not in arch_content]
    if missing:
        results.append(("A2", "FAIL", f"缺少章节: {', '.join(missing)}"))
    else:
        results.append(("A2", "PASS", "全部 6 个章节存在"))

    # ── 解析各节内容（后续检查复用）──

    module_section = _section(arch_content, "## 2. 模块与边界", numbered=True)
    module_rows = _table_rows(module_section, "模块")
    module_names: set[str] = set()
    module_cap_ids: set[str] = set()
    for row in module_rows:
        if len(row) >= 1:
            module_names.add(row[0])
        if len(row) >= 3:
            module_cap_ids.update(CAPABILITY_ID_RE.findall(row[2]))

    tech_section = _section(arch_content, "## 3. 技术选型", numbered=True)
    tech_rows = _table_rows(tech_section, "决策项")
    tech_cap_ids: set[str] = set()
    expensive_tech: list[str] = []
    cheap_tech: list[str] = []

    for row in tech_rows:
        if len(row) >= 3:
            tech_cap_ids.update(CAPABILITY_ID_RE.findall(row[2]))
        if len(row) >= 5:
            cost = _starts_with_cost(row[4])
            if cost == "贵":
                expensive_tech.append(row[0])
            elif cost == "便宜":
                cheap_tech.append(row[0])

    flow_section = _section(arch_content, "## 4. 关键数据流", numbered=True)
    flow_rows = _table_rows(flow_section, "路径 ID")
    flow_path_ids: set[str] = set()

    for row in flow_rows:
        if len(row) >= 1:
            flow_path_ids.add(row[0])

    # A3: 模块表能力 ID 存在于 INTENT.md 保留能力
    invalid_caps = module_cap_ids - retained_caps
    if invalid_caps:
        results.append((
            "A3", "FAIL",
            f"模块表中的能力 ID 不在 INTENT.md 保留能力中: {sorted(invalid_caps)}",
        ))
    else:
        results.append(("A3", "PASS", f"模块表中 {len(module_cap_ids)} 个能力 ID 都在保留能力中"))

    # A4: 模块依赖引用的模块名都已定义
    dep_errors: list[str] = []
    for row in module_rows:
        if len(row) < 4:
            continue
        dep_cell = row[3].strip()
        if dep_cell == "无" or not dep_cell:
            continue
        for token in _split_tokens(dep_cell):
            if token != "无" and token not in module_names:
                dep_errors.append(f"模块 '{row[0]}' 依赖了未定义的模块 '{token}'")

    if dep_errors:
        results.append(("A4", "FAIL", "; ".join(dep_errors)))
    else:
        results.append(("A4", "PASS", "模块依赖中的模块名都已定义"))

    # A5: 技术选型表
    tech_errors: list[str] = []
    for row in tech_rows:
        if len(row) < 5:
            tech_errors.append(f"技术选型表行不足 5 列: {row[0] if row else '?'}")
            continue
        if any(not cell.strip() for cell in row[:5]):
            tech_errors.append(f"技术选型表有空列: {row[0]}")
        for word in FORBIDDEN_WORDS:
            if word in row[3]:
                tech_errors.append(f"技术选型「为什么不选另一个」含禁用词 '{word}'（行: {row[0]}）")
        cost = _starts_with_cost(row[4])
        if cost is None:
            tech_errors.append(f"技术选型代价列无法识别: '{row[4]}'（行: {row[0]}）")

    if tech_errors:
        results.append(("A5", "FAIL", "; ".join(tech_errors)))
    else:
        results.append(("A5", "PASS", f"技术选型表 {len(tech_rows)} 行，列非空，无禁用词"))

    # A6: 数据流覆盖全部验收路径 + 模块名都已定义
    flow_errors: list[str] = []
    for row in flow_rows:
        if len(row) >= 3:
            for token in _split_tokens(row[2]):
                if token and token not in module_names:
                    flow_errors.append(f"数据流引用了未定义的模块 '{token}'")
    missing_paths = acceptance_paths - flow_path_ids
    if missing_paths:
        flow_errors.append(f"缺少验收路径: {sorted(missing_paths)}")

    if flow_errors:
        results.append(("A6", "FAIL", "; ".join(flow_errors)))
    else:
        results.append(("A6", "PASS", f"覆盖全部 {len(acceptance_paths)} 条验收路径，模块名都已定义"))

    # A7: 假设表
    assum_section = _section(arch_content, "## 5. 额外结构与假设", numbered=True)
    # 剥离 HTML 注释后再解析——注释里的声明和整张表格都不参与检查
    stripped_assum = _strip_html_comments(assum_section)
    assum_rows = _table_rows(stripped_assum, "加了什么结构")
    assum_errors: list[str] = []
    no_evidence_items: list[str] = []
    expensive_assum: list[str] = []
    cheap_assum: list[str] = []
    # "无额外结构"必须是独立声明行（"并非无额外结构"这类子串和表格单元格不算）
    has_no_extra = any(
        RE_NO_EXTRA_LINE.fullmatch(line.strip())
        for line in stripped_assum.splitlines()
        if line.strip() and not line.strip().startswith("|")
    )
    real_rows = [row for row in assum_rows if not _is_placeholder_row(row)]

    if not stripped_assum.strip():
        assum_errors.append('第 5 节缺失或为空——没有额外结构时必须写"无额外结构"')
    elif has_no_extra and real_rows:
        assum_errors.append(
            f'声明"无额外结构"但假设表仍有 {len(real_rows)} 行数据，两者矛盾'
        )
    elif not has_no_extra and not assum_rows:
        assum_errors.append('第 5 节既没有声明"无额外结构"，也没有假设表数据行')
    elif not has_no_extra:
        for row in assum_rows:
            if len(row) < 4:
                assum_errors.append(f"假设表行不足 4 列: {row[0] if row else '?'}")
                continue
            # 场景列不含抽象词
            for word in FORBIDDEN_WORDS:
                if word in row[1]:
                    assum_errors.append(f"假设表「为了解决什么情况」含禁用词 '{word}'（行: {row[0]}）")
            # 证据列合规：只能是代码位置、用户原话（引号包裹）或"无依据，属于假设"
            evidence = row[2].strip()
            if evidence.startswith("无依据"):
                no_evidence_items.append(row[0])
            else:
                looks_like_code = bool(RE_EVIDENCE_CODE.search(evidence))
                looks_like_quote = bool(RE_EVIDENCE_QUOTE.search(evidence))
                if not looks_like_code and not looks_like_quote:
                    assum_errors.append(
                        f"假设表证据列不合规（行: {row[0]}）: "
                        f"证据只能是代码位置（如 src/order/service.py:42）、"
                        f"用户原话（用引号包裹）或\"无依据，属于假设\""
                    )
                else:
                    # 禁用词只查引号之外的部分——用户原话里可以合法出现"为了性能"这类词
                    evidence_unquoted = RE_QUOTED_SPAN.sub("", evidence)
                    for word in FORBIDDEN_WORDS:
                        if word in evidence_unquoted:
                            assum_errors.append(f"假设表证据列含禁用词 '{word}'（行: {row[0]}）")
            # 代价列
            cost = _starts_with_cost(row[3])
            if cost is None:
                assum_errors.append(f"假设表代价列无法识别: '{row[3]}'（行: {row[0]}）")
            elif cost == "贵":
                expensive_assum.append(row[0])
            elif cost == "便宜":
                cheap_assum.append(row[0])

        # 无依据项必须出现在汇总中
        if no_evidence_items:
            confirm_sub = _subsection(assum_section, "需要你确认的假设")
            for item in no_evidence_items:
                if item not in confirm_sub:
                    assum_errors.append(f"无依据项 '{item}' 未出现在「需要你确认的假设」中")

    if assum_errors:
        results.append(("A7", "FAIL", "; ".join(assum_errors)))
    else:
        if has_no_extra:
            results.append(("A7", "PASS", "无额外结构"))
        else:
            results.append(("A7", "PASS", f"假设表 {len(assum_rows)} 行，证据合规，无依据项已汇总"))

    # A8: 关键选型与代价（贵决策详细说明）
    detail_section = _section(arch_content, "## 6. 关键选型与代价（请重点核对）", numbered=True)
    all_expensive = expensive_tech + expensive_assum
    all_cheap = cheap_tech + cheap_assum

    # 提取第 6 节中的 ### 标题
    detail_headings: set[str] = set()
    for line in detail_section.splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            detail_headings.add(m.group(1))

    a8_errors: list[str] = []
    for item in all_expensive:
        if not any(item in h for h in detail_headings):
            a8_errors.append(f"代价为「贵」的条目 '{item}' 缺少详细说明")
    for item in all_cheap:
        if any(item in h for h in detail_headings):
            a8_errors.append(f"代价为「便宜」的条目 '{item}' 不应有详细说明")

    if not all_expensive:
        if "无" not in detail_section and not detail_headings:
            a8_errors.append("没有代价为「贵」的条目时，应写「无」")

    if a8_errors:
        results.append(("A8", "FAIL", "; ".join(a8_errors)))
    else:
        if all_expensive:
            results.append((
                "A8", "PASS",
                f"{len(all_expensive)} 条贵决策都有详细说明，"
                f"{len(all_cheap)} 条便宜决策无多余说明",
            ))
        else:
            results.append(("A8", "PASS", "无贵决策，已声明「无」"))

    # ═══════════════════════════════════════════════════════════════════════
    # 功能设计层检查 D1-D5
    # ═══════════════════════════════════════════════════════════════════════

    # D1: design.md 非空
    if not design_content.strip():
        results.append(("D1", "FAIL", "design.md 为空"))
        return results
    results.append(("D1", "PASS", f"文件有 {len(design_content)} 个字符"))

    # ── 解析 design.md 各节 ──

    design_section2 = _section(design_content, "## 2. 能力设计", numbered=True)
    design_cap_ids = _extract_design_cap_ids(design_section2)

    # D2: 每个保留能力都有一节
    missing_caps = retained_caps - design_cap_ids
    if missing_caps:
        results.append(("D2", "FAIL", f"缺少保留能力的功能设计: {sorted(missing_caps)}"))
    else:
        results.append(("D2", "PASS", f"全部 {len(retained_caps)} 项保留能力都有功能设计"))

    # D3: 「不做什么」非空
    d3_errors: list[str] = []
    for cap_id in sorted(retained_caps):
        cap_text = _extract_cap_section(design_section2, cap_id)
        if not cap_text:
            d3_errors.append(f"{cap_id} 缺少功能设计节")
            continue
        not_do = _extract_field(cap_text, "不做什么")
        if not_do is None:
            d3_errors.append(f"{cap_id} 缺少「不做什么」字段")
        elif not not_do.strip():
            d3_errors.append(f"{cap_id} 的「不做什么」为空")

    if d3_errors:
        results.append(("D3", "FAIL", "; ".join(d3_errors)))
    else:
        results.append(("D3", "PASS", f"全部 {len(retained_caps)} 项能力的「不做什么」非空"))

    # D4: 不含代码特征词
    d4_errors: list[str] = []
    for pattern in CODE_PATTERNS:
        if re.search(pattern, design_content, re.IGNORECASE):
            d4_errors.append(f"发现代码特征词匹配: {pattern}")

    if d4_errors:
        results.append(("D4", "FAIL", "; ".join(d4_errors)))
    else:
        results.append(("D4", "PASS", "未发现代码特征词"))

    # D5: 架构一致性核对表存在
    check_section = _section(design_content, "## 3. 与架构文档的对照", numbered=True)
    check_rows = _table_rows(check_section, "核对项")
    if not check_rows and "无" not in check_section:
        results.append(("D5", "FAIL", "缺少架构一致性核对表"))
    else:
        results.append(("D5", "PASS", "架构一致性核对表存在"))

    # ═══════════════════════════════════════════════════════════════════════
    # 跨文件检查 X1-X2
    # ═══════════════════════════════════════════════════════════════════════

    # X1: design.md 引用的模块名都在 architecture.md 中定义
    design_modules: set[str] = set()
    for cap_id in sorted(retained_caps):
        cap_text = _extract_cap_section(design_section2, cap_id)
        if cap_text:
            mod_value = _extract_field(cap_text, "涉及模块")
            if mod_value and mod_value.strip():
                design_modules.update(_split_tokens(mod_value))

    x1_errors: list[str] = []
    for module in design_modules:
        if module != "无" and module not in module_names:
            x1_errors.append(f"design.md 引用了未定义的模块 '{module}'")

    if x1_errors:
        results.append(("X1", "FAIL", "; ".join(x1_errors)))
    else:
        results.append(("X1", "PASS", "design.md 引用的模块名都在 architecture.md 中定义"))

    # X2: 两份文件引用的能力 ID 集合一致
    arch_all_caps = module_cap_ids | tech_cap_ids
    design_all_caps = design_cap_ids

    if arch_all_caps != design_all_caps:
        only_arch = arch_all_caps - design_all_caps
        only_design = design_all_caps - arch_all_caps
        parts: list[str] = []
        if only_arch:
            parts.append(f"只在 architecture.md 中: {sorted(only_arch)}")
        if only_design:
            parts.append(f"只在 design.md 中: {sorted(only_design)}")
        results.append(("X2", "FAIL", "; ".join(parts)))
    else:
        results.append(("X2", "PASS", f"两份文件引用的能力 ID 集合一致（{len(arch_all_caps)} 个）"))

    return results


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "用法: python design_validate.py "
            "/path/to/architecture.md /path/to/design.md /path/to/intent.md"
        )
        return 1

    arch_path = Path(sys.argv[1])
    design_path = Path(sys.argv[2])
    intent_path = Path(sys.argv[3])

    if not arch_path.exists():
        print(f"FAIL: architecture.md 不存在: {arch_path}")
        return 1
    if not design_path.exists():
        print(f"FAIL: design.md 不存在: {design_path}")
        return 1
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 不存在: {intent_path}")
        return 1

    arch_content = arch_path.read_text(encoding="utf-8")
    design_content = design_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    results = validate(arch_content, design_content, intent_content)

    print(f"\n{'=' * 60}")
    print(f"Design 校验结果")
    print(f"  architecture.md: {arch_path}")
    print(f"  design.md:       {design_path}")
    print(f"  INTENT.md:       {intent_path}")
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
