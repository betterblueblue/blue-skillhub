#!/usr/bin/env python3
"""INTENT.md 结构与交叉引用校验。

用法：
  python intent_validate.py <intent.md> [--baseline <git_ref>]

  --baseline <git_ref>  可选：与 git 中的基线版本比较能力决策和路径 ID 变化，
                        变化时输出 WARN 提示（不影响 PASS/FAIL）。

检查项：
  V1: 文件非空
  V2: 16 个必需章节齐全
  V3: 能力、证据、决策和决策来源关系合法，且没有待确认项
  V4: 不可妥协项引用保留能力，并有用户明确确认；允许为空
  V5: 推迟和放弃清单与能力决策一致
  V6: 决策统计与能力清单一致，未决问题为空
  V7: 7 个通用漂移模式均使用明确状态并留下说明
  V8: 存在针对 INTENT.md 全文的用户明确确认记录
  V9: S1-S10 具有规定的证据结构，并与能力和漂移记录交叉一致
  V10: 设计标准节存在；有素材时记录了路径和用户确认，无素材时记录用户确认"没有"
  V11: 术语表节存在；有术语时记录了人话翻译和界面文案，无术语时明确写"无"
  V12: 验收路径节存在；有路径时记录了入口、步骤和预期结果，无路径时记录用户确认"没有"
  V13: 性能要求节存在；有要求时记录了要求和用户确认，无要求时记录用户确认"没有"
  V14: 安全要求节存在；有要求时记录了要求和用户确认，无要求时记录用户确认"没有"
  V15: 术语表的原始术语不得出现在能力表的"能力"列（能力命名用人话侧，防止术语沿能力名繁殖到下游）
  V16: 用户要求"1:1 / 全部页面 / 逐页"时，第 17 节页面清单必须存在且逐页完整

本脚本不能验证文件引用是否真实、模型推导是否合理，也不能证明内容
符合用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# 公共 Markdown 解析函数
_COMMON_DIR = Path(__file__).resolve().parent.parent.parent / "_common"
if str(_COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(_COMMON_DIR))
from markdown_parser import (
    section,
    subsection,
    table_rows as _table_rows,
    has_placeholder as _has_placeholder,
)


REQUIRED_SECTIONS = [
    "## 1. 一句话意图",
    "## 2. 场景类型",
    "## 3. 证据来源",
    "## 4. 能力与决策",
    "## 5. 不可妥协项",
    "## 6. 推迟与放弃",
    "## 7. 漂移复核",
    "## 8. 决策统计与未决问题",
    "## 9. 用户确认记录",
    "## 10. 语义复核记录",
    "## 11. 锚定原始记录",
    "## 12. 设计标准",
    "## 13. 术语表",
    "## 14. 验收路径",
    "## 15. 性能要求",
    "## 16. 安全要求",
]

DRIFT_PATTERNS = [
    "D1 未确认新增",
    "D2 目标替换",
    "D3 能力降级",
    "D4 保留项遗漏",
    "D5 推迟或放弃项被重新加入",
    "D6 决策来源失真",
    "D7 交接信息丢失",
]

VALID_DECISIONS = {"保留", "推迟", "放弃", "待确认"}
VALID_DECISION_SOURCES = {
    "用户明确确认",
    "用户授权模型决定",
    "模型建议（未确认）",
}
VALID_DRIFT_STATUSES = {"未命中", "命中", "不适用"}
CAPABILITY_ID_RE = re.compile(r"^C\d{2,}$")
PATH_ID_RE = re.compile(r"^P\d{2,}$")
PAGE_ID_RE = re.compile(r"^PG\d{2,}$")
EVIDENCE_ID_RE = re.compile(r"^E\d{2,}$")
# 链路目录名：YYYY-MM-DD-NNN-意图名称（与 SKILL.md「文件存放」节的
# intent-chain/{链路目录}/intent.md 契约一致）
CHAIN_DIR_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}-\d{3}-[^\\/:*?\"<>| ]+$"
)


def _section(content: str, heading: str) -> str:
    """INTENT.md 使用编号章节（## 1. Title），需要 numbered=True。"""
    return section(content, heading, numbered=True)


def _subsection(content: str, heading: str) -> str:
    """INTENT.md 语义复核子节只以 ### 为边界。"""
    return subsection(content, heading, stop_at_h2=False)


def _looks_like_full_confirmation(value: str) -> bool:
    return bool(
        re.search(
            r"确认|同意|接受|没问题|可以写入|可以保存|\bOK\b",
            value,
            re.IGNORECASE,
        )
    )


def _split_evidence_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[、,]", value) if item.strip()]


def _parse_capabilities(content: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    section = _section(content, "## 4. 能力与决策")
    rows = _table_rows(section, "能力 ID")
    records: dict[str, dict[str, str]] = {}

    if not rows:
        return records, ["能力清单为空或表格格式不正确"]

    evidence_rows = _table_rows(_section(content, "## 3. 证据来源"), "证据 ID")
    evidence_ids = {
        row[0]
        for row in evidence_rows
        if len(row) == 4 and EVIDENCE_ID_RE.fullmatch(row[0]) and not any(_has_placeholder(v) for v in row)
    }
    if not evidence_ids:
        errors.append("证据来源表没有有效数据行")

    for index, row in enumerate(rows, 1):
        if len(row) != 6:
            errors.append(f"能力表第 {index} 行应有 6 列，实际 {len(row)} 列")
            continue
        cap_id, name, description, evidence, decision, decision_source = row
        if not CAPABILITY_ID_RE.fullmatch(cap_id):
            errors.append(f"能力表第 {index} 行 ID 非法：{cap_id}")
            continue
        if cap_id in records:
            errors.append(f"能力 ID 重复：{cap_id}")
            continue
        if any(_has_placeholder(value) for value in row):
            errors.append(f"能力 {cap_id} 仍含模板占位符")
        if not name or not description:
            errors.append(f"能力 {cap_id} 缺少名称或描述")
        referenced_evidence = _split_evidence_ids(evidence)
        if not referenced_evidence or any(item not in evidence_ids for item in referenced_evidence):
            errors.append(f"能力 {cap_id} 引用了不存在的证据 ID：{evidence}")
        if decision not in VALID_DECISIONS:
            errors.append(f"能力 {cap_id} 决策非法：{decision}")
        if decision_source not in VALID_DECISION_SOURCES:
            errors.append(f"能力 {cap_id} 决策来源非法：{decision_source}")

        if decision == "待确认" and decision_source != "模型建议（未确认）":
            errors.append(f"能力 {cap_id} 为待确认，但决策来源不是模型建议（未确认）")
        if decision_source == "模型建议（未确认）" and decision != "待确认":
            errors.append(f"能力 {cap_id} 尚未确认，却已经写成{decision}")
        if decision_source == "用户授权模型决定" and decision not in {"保留", "推迟"}:
            errors.append(f"能力 {cap_id} 由模型受托决定时只能保留或推迟")
        if decision == "放弃" and decision_source != "用户明确确认":
            errors.append(f"能力 {cap_id} 被放弃，但没有用户明确确认")
        if decision == "待确认":
            errors.append(f"能力 {cap_id} 仍待确认，不得交接")

        records[cap_id] = {
            "name": name,
            "description": description,
            "evidence": evidence,
            "decision": decision,
            "source": decision_source,
        }

    return records, errors


def _explicit_no_critical(section: str) -> bool:
    match = re.search(
        r"无不可妥协项。\s*用户明确确认[：:]\s*[“\"](.+?)[”\"]",
        section,
    )
    return bool(match and match.group(1).strip() and not _has_placeholder(match.group(1)))


def validate(content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)；结果为 PASS / FAIL / WARN。"""
    results: list[tuple[str, str, str]] = []

    if content.strip():
        results.append(("V1", "PASS", f"文件有 {len(content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))

    missing = [heading for heading in REQUIRED_SECTIONS if heading not in content]
    if missing:
        results.append(("V2", "FAIL", f"缺少章节：{', '.join(missing)}"))
    else:
        results.append(("V2", "PASS", "全部 16 个章节存在"))

    capabilities, capability_errors = _parse_capabilities(content)
    if capability_errors:
        results.append(("V3", "FAIL", "；".join(capability_errors)))
    else:
        results.append(("V3", "PASS", f"{len(capabilities)} 项能力的决策关系合法且没有待确认项"))

    critical_section = _section(content, "## 5. 不可妥协项")
    critical_rows = _table_rows(critical_section, "能力 ID")
    critical_ids: set[str] = set()
    critical_errors: list[str] = []
    if critical_rows:
        for index, row in enumerate(critical_rows, 1):
            if len(row) != 3:
                critical_errors.append(f"不可妥协项第 {index} 行应有 3 列")
                continue
            cap_id, reason, quote = row
            if cap_id in critical_ids:
                critical_errors.append(f"不可妥协能力 ID 重复：{cap_id}")
            critical_ids.add(cap_id)
            record = capabilities.get(cap_id)
            if not record:
                critical_errors.append(f"不可妥协项引用未知能力：{cap_id}")
            elif record["decision"] != "保留":
                critical_errors.append(f"不可妥协项 {cap_id} 不是保留能力")
            elif record["source"] != "用户明确确认":
                critical_errors.append(f"不可妥协项 {cap_id} 不是用户明确确认")
            if not reason or not quote or _has_placeholder(reason) or _has_placeholder(quote):
                critical_errors.append(f"不可妥协项 {cap_id} 缺少真实原因或用户原话")
    elif not _explicit_no_critical(critical_section):
        critical_errors.append("没有不可妥协项时，必须记录用户明确确认“没有”")

    if critical_errors:
        results.append(("V4", "FAIL", "；".join(critical_errors)))
    else:
        results.append(("V4", "PASS", f"不可妥协项 {len(critical_ids)} 条，引用和确认关系合法"))

    scope_section = _section(content, "## 6. 推迟与放弃")
    deferred_section = _subsection(scope_section, "推迟项")
    abandoned_section = _subsection(scope_section, "放弃项")
    deferred_rows = _table_rows(deferred_section, "能力 ID")
    abandoned_rows = _table_rows(abandoned_section, "能力 ID")
    scope_errors: list[str] = []

    expected_deferred = {cap_id for cap_id, row in capabilities.items() if row["decision"] == "推迟"}
    expected_abandoned = {cap_id for cap_id, row in capabilities.items() if row["decision"] == "放弃"}
    actual_deferred: set[str] = set()
    actual_abandoned: set[str] = set()

    for index, row in enumerate(deferred_rows, 1):
        if len(row) != 4:
            scope_errors.append(f"推迟项第 {index} 行应有 4 列")
            continue
        cap_id, name, reason, revisit = row
        if cap_id in actual_deferred:
            scope_errors.append(f"推迟项 ID 重复：{cap_id}")
        actual_deferred.add(cap_id)
        record = capabilities.get(cap_id)
        if not record or record["decision"] != "推迟":
            scope_errors.append(f"推迟项 {cap_id} 与能力决策不一致")
        elif name != record["name"]:
            scope_errors.append(f"推迟项 {cap_id} 名称与能力表不一致")
        if not reason or not revisit or _has_placeholder(reason) or _has_placeholder(revisit):
            scope_errors.append(f"推迟项 {cap_id} 缺少原因或重新讨论条件")

    for index, row in enumerate(abandoned_rows, 1):
        if len(row) != 3:
            scope_errors.append(f"放弃项第 {index} 行应有 3 列")
            continue
        cap_id, name, quote = row
        if cap_id in actual_abandoned:
            scope_errors.append(f"放弃项 ID 重复：{cap_id}")
        actual_abandoned.add(cap_id)
        record = capabilities.get(cap_id)
        if not record or record["decision"] != "放弃":
            scope_errors.append(f"放弃项 {cap_id} 与能力决策不一致")
        elif name != record["name"]:
            scope_errors.append(f"放弃项 {cap_id} 名称与能力表不一致")
        if not quote or _has_placeholder(quote):
            scope_errors.append(f"放弃项 {cap_id} 缺少用户明确确认原话")

    if actual_deferred != expected_deferred:
        scope_errors.append(
            f"推迟项 ID 不一致：应为 {sorted(expected_deferred)}，实际 {sorted(actual_deferred)}"
        )
    if actual_abandoned != expected_abandoned:
        scope_errors.append(
            f"放弃项 ID 不一致：应为 {sorted(expected_abandoned)}，实际 {sorted(actual_abandoned)}"
        )
    if not expected_deferred and not re.search(r"^无。\s*$", deferred_section, re.MULTILINE):
        scope_errors.append("没有推迟项时必须明确写“无。”")
    if not expected_abandoned and not re.search(r"^无。\s*$", abandoned_section, re.MULTILINE):
        scope_errors.append("没有放弃项时必须明确写“无。”")

    if scope_errors:
        results.append(("V5", "FAIL", "；".join(scope_errors)))
    else:
        results.append(("V5", "PASS", "推迟和放弃清单与能力决策一致"))

    stats_section = _section(content, "## 8. 决策统计与未决问题")
    stats_rows = _table_rows(stats_section, "决策")
    stats_errors: list[str] = []
    stats: dict[str, int] = {}
    for row in stats_rows:
        if len(row) != 2 or not row[1].isdigit():
            stats_errors.append(f"决策统计行格式非法：{' | '.join(row)}")
            continue
        if row[0] in stats:
            stats_errors.append(f"决策统计项重复：{row[0]}")
        stats[row[0]] = int(row[1])

    counts = Counter(record["decision"] for record in capabilities.values())
    expected_stats = {
        "保留": counts["保留"],
        "推迟": counts["推迟"],
        "放弃": counts["放弃"],
        "待确认": counts["待确认"],
        "总计": len(capabilities),
    }
    if stats != expected_stats:
        stats_errors.append(f"决策统计不一致：应为 {expected_stats}，实际 {stats}")
    if not re.search(r"未决问题[：:]\s*无\s*$", stats_section, re.MULTILINE):
        stats_errors.append("未决问题必须明确写“无”后才能交接")

    if stats_errors:
        results.append(("V6", "FAIL", "；".join(stats_errors)))
    else:
        results.append(("V6", "PASS", "决策统计准确且没有未决问题"))

    drift_section = _section(content, "## 7. 漂移复核")
    drift_rows = _table_rows(drift_section, "模式")
    drift_errors: list[str] = []
    drift_records: dict[str, str] = {}
    for row in drift_rows:
        if len(row) != 3:
            drift_errors.append(f"漂移复核行应有 3 列：{' | '.join(row)}")
            continue
        pattern, status, evidence = row
        if pattern in drift_records:
            drift_errors.append(f"漂移模式重复：{pattern}")
        drift_records[pattern] = status
        if status not in VALID_DRIFT_STATUSES:
            drift_errors.append(f"漂移模式 {pattern} 状态非法：{status}")
        if not evidence or _has_placeholder(evidence):
            drift_errors.append(f"漂移模式 {pattern} 缺少证据或处理结果")

    if set(drift_records) != set(DRIFT_PATTERNS):
        drift_errors.append(
            f"漂移模式不完整：应为 {DRIFT_PATTERNS}，实际 {sorted(drift_records)}"
        )

    if drift_errors:
        results.append(("V7", "FAIL", "；".join(drift_errors)))
    else:
        results.append(("V7", "PASS", "7 个通用漂移模式均有明确状态和说明"))

    confirmation_section = _section(content, "## 9. 用户确认记录")
    confirmation_rows = _table_rows(confirmation_section, "日期")
    full_confirmations = [
        row
        for row in confirmation_rows
        if len(row) == 4
        and row[1] == "INTENT.md 全文"
        and row[2] == "用户明确确认"
        and row[0]
        and row[3]
        and not any(_has_placeholder(value) for value in row)
        and _looks_like_full_confirmation(row[3])
    ]
    if full_confirmations:
        results.append(("V8", "PASS", f"有 {len(full_confirmations)} 条全文明确确认记录"))
    else:
        results.append(("V8", "FAIL", "缺少针对 INTENT.md 全文的用户明确确认记录"))

    audit_section = _section(content, "## 10. 语义复核记录")
    audit_errors: list[str] = []
    audit_headings = [
        "S1 证据覆盖",
        "S2 决策来源",
        "S3 不可妥协项",
        "S4 锚定充分性与冲突",
        "S5 漂移复核",
        "S6 设计标准",
        "S7 术语标记",
        "S8 验收路径",
        "S9 性能要求",
        "S10 安全要求",
    ]
    audit_parts = {heading: _subsection(audit_section, heading) for heading in audit_headings}
    for heading, part in audit_parts.items():
        if not part:
            audit_errors.append(f"缺少复核项：{heading}")

    if all(audit_parts.values()):
        s1_rows = _table_rows(audit_parts["S1 证据覆盖"], "能力 ID")
        s1_ids = {
            row[0]
            for row in s1_rows
            if len(row) == 4 and not any(_has_placeholder(value) for value in row)
        }
        if s1_ids != set(capabilities):
            audit_errors.append(f"S1 没有逐项覆盖能力：应为 {sorted(capabilities)}，实际 {sorted(s1_ids)}")
        if not re.search(r"场景专项结论[：:].+", audit_parts["S1 证据覆盖"]):
            audit_errors.append("S1 缺少场景专项结论")

        s2_rows = _table_rows(audit_parts["S2 决策来源"], "能力 ID")
        s2_records: dict[str, tuple[str, str]] = {}
        for row in s2_rows:
            if len(row) != 5 or any(_has_placeholder(value) for value in row):
                continue
            cap_id, decision, source, quote, _result = row
            if quote:
                s2_records[cap_id] = (decision, source)
        expected_s2 = {
            cap_id: (record["decision"], record["source"])
            for cap_id, record in capabilities.items()
        }
        if s2_records != expected_s2:
            audit_errors.append(f"S2 决策来源与能力表不一致：应为 {expected_s2}，实际 {s2_records}")

        s3_part = audit_parts["S3 不可妥协项"]
        s3_rows = _table_rows(s3_part, "能力 ID")
        if critical_ids:
            s3_ids = {
                row[0]
                for row in s3_rows
                if len(row) == 5
                and row[1] == "是"
                and row[2] == "是"
                and not any(_has_placeholder(value) for value in row)
            }
            if s3_ids != critical_ids:
                audit_errors.append(f"S3 与不可妥协项不一致：应为 {sorted(critical_ids)}，实际 {sorted(s3_ids)}")
        elif not _explicit_no_critical(s3_part):
            audit_errors.append("S3 没有记录用户明确确认“无不可妥协项”")

        s4_rows = _table_rows(audit_parts["S4 锚定充分性与冲突"], "方法")
        valid_s4_rows = [
            row
            for row in s4_rows
            if len(row) == 5
            and row[3] == "是"
            and not any(_has_placeholder(value) for value in row)
            and row[0]
            and row[1]
            and row[2]
            and row[4]
        ]
        if not valid_s4_rows:
            audit_errors.append("S4 缺少具备原始证据、能力 ID 和用户反馈的记录")
        else:
            for row in valid_s4_rows:
                if row[0] not in {"类比", "反面", "场景"}:
                    audit_errors.append(f"S4 方法名称非法：{row[0]}")
                referenced_ids = [
                    item.strip()
                    for item in re.split(r"[、,]", row[2])
                    if item.strip()
                ]
                if not referenced_ids or any(item not in capabilities for item in referenced_ids):
                    audit_errors.append(f"S4 引用了未知能力 ID：{row[2]}")
        if not re.search(r"未解决冲突[：:]\s*无\s*$", audit_parts["S4 锚定充分性与冲突"], re.MULTILINE):
            audit_errors.append("S4 仍有未解决冲突或没有明确写“无”")

        s5_rows = _table_rows(audit_parts["S5 漂移复核"], "模式")
        s5_records = {
            row[0]: row[1]
            for row in s5_rows
            if len(row) == 3 and row[2] and not any(_has_placeholder(value) for value in row)
        }
        if s5_records != drift_records:
            audit_errors.append("S5 没有逐项复核第 7 节的漂移状态")

        s6_part = audit_parts["S6 设计标准"]
        s6_rows = _table_rows(s6_part, "\u8bbe\u8ba1\u7d20\u6750 ID")
        if s6_rows:
            for index, row in enumerate(s6_rows, 1):
                if len(row) != 5:
                    audit_errors.append(f"S6 第 {index} 行应有 5 列")
                    continue
                d_id, dtype, path, scope, confirm = row
                if any(_has_placeholder(v) for v in row):
                    audit_errors.append(f"S6 {d_id} 仍含模板占位符")
                if not dtype or not path or not scope or not confirm:
                    audit_errors.append(f"S6 {d_id} 缺少类型、路径、验收范围或用户确认")
        elif not re.search(r"\u65e0\u8bbe\u8ba1\u6807\u51c6\u7d20\u6750.+\u7528\u6237\u660e\u786e\u786e\u8ba4", s6_part):
            audit_errors.append("S6 没有设计素材时，必须记录用户明确确认“没有”")

        s7_part = audit_parts["S7 \u672f\u8bed\u6807\u8bb0"]
        s7_rows = _table_rows(s7_part, "\u539f\u59cb\u672f\u8bed")
        if s7_rows:
            for index, row in enumerate(s7_rows, 1):
                if len(row) != 4:
                    audit_errors.append(f"S7 第 {index} 行应有 4 列")
                    continue
                term, translation, ui_text, cap_refs = row
                if any(_has_placeholder(v) for v in row):
                    audit_errors.append(f"S7 “{term}”仍含模板占位符")
                if not translation or not ui_text:
                    audit_errors.append(f"S7 “{term}”缺少人话翻译或界面文案")
        elif not re.search(r"\u65e0\u672f\u8bed\u9700\u8981\u7ffb\u8bd1", s7_part):
            audit_errors.append("S7 没有术语时，必须明确写“无术语需要翻译”")

        s8_part = audit_parts["S8 验收路径"]
        s8_rows = _table_rows(s8_part, "路径 ID")
        if s8_rows:
            for index, row in enumerate(s8_rows, 1):
                if len(row) != 7:
                    audit_errors.append(f"S8 第 {index} 行应有 7 列")
                    continue
                p_id, name, cap_refs, entry, steps, expected, confirm = row
                if any(_has_placeholder(v) for v in row):
                    audit_errors.append(f"S8 {p_id} 仍含模板占位符")
                if not name or not entry or not steps or not expected or not confirm:
                    audit_errors.append(f"S8 {p_id} 缺少名称、入口、步骤、预期结果或用户确认")
        elif not re.search(r"无验收路径.+用户明确确认", s8_part):
            audit_errors.append("S8 没有验收路径时，必须记录用户明确确认“没有”")

        s9_part = audit_parts["S9 性能要求"]
        s9_rows = _table_rows(s9_part, "要求 ID")
        if s9_rows:
            for index, row in enumerate(s9_rows, 1):
                if len(row) != 4:
                    audit_errors.append(f"S9 第 {index} 行应有 4 列")
                    continue
                pf_id, requirement, cap_refs, confirm = row
                if any(_has_placeholder(v) for v in row):
                    audit_errors.append(f"S9 {pf_id} 仍含模板占位符")
                if not requirement or not confirm:
                    audit_errors.append(f"S9 {pf_id} 缺少要求内容或用户确认")
        elif not re.search(r"无性能要求.+用户明确确认", s9_part):
            audit_errors.append("S9 没有性能要求时，必须记录用户明确确认“没有”")

        s10_part = audit_parts["S10 安全要求"]
        s10_rows = _table_rows(s10_part, "要求 ID")
        if s10_rows:
            for index, row in enumerate(s10_rows, 1):
                if len(row) != 4:
                    audit_errors.append(f"S10 第 {index} 行应有 4 列")
                    continue
                sf_id, requirement, cap_refs, confirm = row
                if any(_has_placeholder(v) for v in row):
                    audit_errors.append(f"S10 {sf_id} 仍含模板占位符")
                if not requirement or not confirm:
                    audit_errors.append(f"S10 {sf_id} 缺少要求内容或用户确认")
        elif not re.search(r"无安全要求.+用户明确确认", s10_part):
            audit_errors.append("S10 没有安全要求时，必须记录用户明确确认“没有”")

    if audit_errors:
        results.append(("V9", "FAIL", "；".join(audit_errors)))
    else:
        results.append(("V9", "PASS", "S1-S10 结构化复核记录齐全并与正文一致"))

    design_section = _section(content, "## 12. 设计标准")
    design_errors: list[str] = []
    design_rows = _table_rows(design_section, "\u8bbe\u8ba1\u7d20\u6750 ID")
    if design_rows:
        for index, row in enumerate(design_rows, 1):
            if len(row) != 5:
                design_errors.append(f"设计标准第 {index} 行应有 5 列")
                continue
            d_id, dtype, path, scope, confirm = row
            if any(_has_placeholder(v) for v in row):
                design_errors.append(f"设计标准 {d_id} 仍含模板占位符")
            if not dtype or not path or not scope or not confirm:
                design_errors.append(f"设计标准 {d_id} 缺少类型、路径、验收范围或用户确认")
    elif not re.search(r"\u65e0\u8bbe\u8ba1\u6807\u51c6\u7d20\u6750.+\u7528\u6237\u660e\u786e\u786e\u8ba4", design_section):
        design_errors.append("没有设计素材时，必须记录用户明确确认“没有”")
    if design_errors:
        results.append(("V10", "FAIL", "；".join(design_errors)))
    else:
        results.append(("V10", "PASS", "设计标准节存在且有用户确认"))

    terminology_section = _section(content, "## 13. 术语表")
    terminology_errors: list[str] = []
    terminology_rows = _table_rows(terminology_section, "\u539f\u59cb\u672f\u8bed")
    if terminology_rows:
        for index, row in enumerate(terminology_rows, 1):
            if len(row) != 4:
                terminology_errors.append(f"术语表第 {index} 行应有 4 列")
                continue
            term, translation, ui_text, cap_refs = row
            if any(_has_placeholder(v) for v in row):
                terminology_errors.append(f"术语“{term}”仍含模板占位符")
            if not translation or not ui_text:
                terminology_errors.append(f"术语“{term}”缺少人话翻译或界面文案")
    elif not re.search(r"\u65e0\u672f\u8bed\u9700\u8981\u7ffb\u8bd1", terminology_section):
        terminology_errors.append("没有术语时，必须明确写“无术语需要翻译”")
    if terminology_errors:
        results.append(("V11", "FAIL", "；".join(terminology_errors)))
    else:
        results.append(("V11", "PASS", "术语表节存在且格式正确"))

    acceptance_section = _section(content, "## 14. 验收路径")
    acceptance_errors: list[str] = []
    acceptance_rows = _table_rows(acceptance_section, "路径 ID")
    if acceptance_rows:
        path_ids: set[str] = set()
        for index, row in enumerate(acceptance_rows, 1):
            if len(row) != 7:
                acceptance_errors.append(f"验收路径第 {index} 行应有 7 列")
                continue
            p_id, name, cap_refs, entry, steps, expected, confirm = row
            if p_id in path_ids:
                acceptance_errors.append(f"验收路径 ID 重复：{p_id}")
            path_ids.add(p_id)
            if not PATH_ID_RE.fullmatch(p_id):
                acceptance_errors.append(f"验收路径 ID 非法：{p_id}")
            if any(_has_placeholder(v) for v in row):
                acceptance_errors.append(f"验收路径 {p_id} 仍含模板占位符")
            if not name or not entry or not steps or not expected or not confirm:
                acceptance_errors.append(f"验收路径 {p_id} 缺少名称、入口、步骤、预期结果或用户确认")
            referenced_caps = _split_evidence_ids(cap_refs)
            if not referenced_caps or any(item not in capabilities for item in referenced_caps):
                acceptance_errors.append(f"验收路径 {p_id} 引用了未知能力 ID：{cap_refs}")
    elif not re.search(r"无验收路径.+用户明确确认", acceptance_section):
        acceptance_errors.append("没有验收路径时，必须记录用户明确确认“没有”")
    if acceptance_errors:
        results.append(("V12", "FAIL", "；".join(acceptance_errors)))
    else:
        results.append(("V12", "PASS", "验收路径节存在且格式正确"))

    perf_section = _section(content, "## 15. 性能要求")
    perf_errors: list[str] = []
    perf_rows = _table_rows(perf_section, "要求 ID")
    if perf_rows:
        for index, row in enumerate(perf_rows, 1):
            if len(row) != 4:
                perf_errors.append(f"性能要求第 {index} 行应有 4 列")
                continue
            pf_id, requirement, cap_refs, confirm = row
            if any(_has_placeholder(v) for v in row):
                perf_errors.append(f"性能要求 {pf_id} 仍含模板占位符")
            if not requirement or not confirm:
                perf_errors.append(f"性能要求 {pf_id} 缺少要求内容或用户确认")
    elif not re.search(r"无性能要求.+用户明确确认", perf_section):
        perf_errors.append("没有性能要求时，必须记录用户明确确认“没有”")
    if perf_errors:
        results.append(("V13", "FAIL", "；".join(perf_errors)))
    else:
        results.append(("V13", "PASS", "性能要求节存在且有用户确认"))

    security_section = _section(content, "## 16. 安全要求")
    security_errors: list[str] = []
    security_rows = _table_rows(security_section, "要求 ID")
    if security_rows:
        for index, row in enumerate(security_rows, 1):
            if len(row) != 4:
                security_errors.append(f"安全要求第 {index} 行应有 4 列")
                continue
            sf_id, requirement, cap_refs, confirm = row
            if any(_has_placeholder(v) for v in row):
                security_errors.append(f"安全要求 {sf_id} 仍含模板占位符")
            if not requirement or not confirm:
                security_errors.append(f"安全要求 {sf_id} 缺少要求内容或用户确认")
    elif not re.search(r"无安全要求.+用户明确确认", security_section):
        security_errors.append("没有安全要求时，必须记录用户明确确认“没有”")
    if security_errors:
        results.append(("V14", "FAIL", "；".join(security_errors)))
    else:
        results.append(("V14", "PASS", "安全要求节存在且有用户确认"))

    # V15: 术语表的原始术语不得出现在能力表的"能力"列——源头掐断术语繁殖。
    # 毕业考实测逃逸链：能力名带原始术语 → PRD/工单/代码/界面全线合法繁殖，
    # 各站只查"术语表存在、被引用"，无一站拦截。能力命名必须用人话侧。
    term_leak_errors: list[str] = []
    term_names = [
        row[0]
        for row in terminology_rows
        if len(row) == 4 and row[0] and not _has_placeholder(row[0])
    ]
    if term_names:
        capability_rows = _table_rows(_section(content, "## 4. 能力与决策"), "能力 ID")
        for row in capability_rows:
            if len(row) != 6:
                continue
            cap_id, cap_name = row[0], row[1]
            for term in term_names:
                if term and term in cap_name:
                    term_leak_errors.append(
                        f"能力 {cap_id} 的名称「{cap_name}」含术语表原始术语「{term}」——"
                        "能力命名应使用人话翻译，否则原始术语会沿能力名繁殖到下游文档、代码和界面"
                    )
    if term_leak_errors:
        results.append(("V15", "FAIL", "；".join(term_leak_errors)))
    else:
        results.append(("V15", "PASS", "能力命名未使用术语表原始术语"))

    # V16: 页级还原要求（1:1/全部页面/逐页）必须有页面清单
    page_section = _section(content, "## 17. 页面清单")
    intro = _section(content, "## 1. 一句话意图")
    confirm_section = _section(content, "## 9. 用户确认记录")
    anchor_record = _section(content, "## 11. 锚定原始记录")
    page_scope_text = intro + critical_section + confirm_section + anchor_record
    page_level_required = bool(
        re.search(r"1\s*[:：]\s*1\s*(还原|复刻|照抄)|(全部页面|所有页面)\s*(还原|复刻|照抄)|逐页", page_scope_text)
    )
    page_rows = _table_rows(page_section, "页面 ID")
    page_errors: list[str] = []
    page_ids: set[str] = set()
    for index, row in enumerate(page_rows, 1):
        if len(row) != 4:
            page_errors.append(f"页面清单第 {index} 行应有 4 列")
            continue
        pg_id, name, source, cap_refs = row
        if pg_id in page_ids:
            page_errors.append(f"页面 ID 重复：{pg_id}")
        page_ids.add(pg_id)
        if not PAGE_ID_RE.fullmatch(pg_id):
            page_errors.append(f"页面 ID 非法：{pg_id}")
        if any(_has_placeholder(v) for v in row):
            page_errors.append(f"页面 {pg_id} 仍含模板占位符")
        if not name or not source:
            page_errors.append(f"页面 {pg_id} 缺少名称或来源")
        referenced_caps = _split_evidence_ids(cap_refs)
        if referenced_caps and any(item not in capabilities for item in referenced_caps):
            page_errors.append(f"页面 {pg_id} 引用了未知能力 ID：{cap_refs}")

    if page_level_required and not page_ids:
        page_errors.append("用户要求 1:1/全部页面/逐页还原，但第 17 节页面清单为空")
    if page_errors:
        results.append(("V16", "FAIL", "；".join(page_errors)))
    else:
        results.append(("V16", "PASS", "页面清单与页级还原要求一致"))

    return results


def _path_error(intent_path: Path) -> str | None:
    if intent_path.name != "intent.md":
        return "文件名必须是 intent.md"
    if not CHAIN_DIR_RE.fullmatch(intent_path.parent.name):
        return "链路目录名必须符合 YYYY-MM-DD-NNN-意图名称，且意图名称不能含空格或特殊字符"
    if intent_path.parent.parent.name != "intent-chain":
        return "链路目录必须放在目标项目的 intent-chain/ 目录下"
    return None


# ---------------------------------------------------------------------------
# 基线对比（--baseline）
# ---------------------------------------------------------------------------


def _read_git_baseline(file_path: Path, git_ref: str) -> str | None:
    """从 git 读取文件在指定 ref 的版本。

    Returns:
        文件内容字符串；无法读取时返回 None。
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(file_path.parent),
            timeout=10,
        )
        if result.returncode != 0:
            return None
        repo_root = result.stdout.strip()
        rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")

        result = subprocess.run(
            ["git", "show", f"{git_ref}:{rel_path}"],
            capture_output=True, text=True, cwd=repo_root,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        return None


def _parse_path_ids(content: str) -> set[str]:
    """从 INTENT.md 第 14 节提取验收路径 ID。"""
    section_text = _section(content, "## 14. 验收路径")
    rows = _table_rows(section_text, "路径 ID")
    return {row[0] for row in rows if len(row) >= 1 and PATH_ID_RE.fullmatch(row[0])}


def _compare_baseline(baseline_content: str, current_content: str) -> list[str]:
    """比较基线和当前版本的关键字段变化，返回 WARN 提示列表。"""
    warnings: list[str] = []

    old_caps, _ = _parse_capabilities(baseline_content)
    new_caps, _ = _parse_capabilities(current_content)

    for cap_id in sorted(set(old_caps) | set(new_caps)):
        if cap_id not in new_caps:
            warnings.append(
                f"能力 {cap_id}（{old_caps[cap_id]['name']}）在新版本中被删除"
                f"（原决策: {old_caps[cap_id]['decision']}）"
            )
        elif cap_id not in old_caps:
            warnings.append(
                f"能力 {cap_id}（{new_caps[cap_id]['name']}）在新版本中新增"
                f"（决策: {new_caps[cap_id]['decision']}）"
            )
        elif old_caps[cap_id]["decision"] != new_caps[cap_id]["decision"]:
            warnings.append(
                f"能力 {cap_id}（{new_caps[cap_id]['name']}）决策从"
                f"'{old_caps[cap_id]['decision']}' 变为 '{new_caps[cap_id]['decision']}'"
            )

    old_paths = _parse_path_ids(baseline_content)
    new_paths = _parse_path_ids(current_content)

    for path_id in sorted(old_paths - new_paths):
        warnings.append(f"验收路径 {path_id} 在新版本中被删除")
    for path_id in sorted(new_paths - old_paths):
        warnings.append(f"验收路径 {path_id} 在新版本中新增")

    return warnings


def main() -> int:
    # 解析参数
    args = sys.argv[1:]
    baseline_ref: str | None = None
    if "--baseline" in args:
        idx = args.index("--baseline")
        if idx + 1 < len(args):
            baseline_ref = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            print("用法: python intent_validate.py <intent.md> [--baseline <git_ref>]")
            return 1

    if len(args) != 1:
        print("用法: python intent_validate.py <intent.md> [--baseline <git_ref>]")
        print("  --baseline <git_ref>  可选：与 git 中的基线版本比较能力决策和路径 ID 变化")
        return 1

    intent_path = Path(args[0])
    if not intent_path.exists():
        print(f"FAIL: 文件不存在: {intent_path}")
        return 1

    path_error = _path_error(intent_path)
    if path_error:
        print(f"FAIL: {path_error}: {intent_path}")
        return 1

    content = intent_path.read_text(encoding="utf-8")
    results = validate(content)

    print(f"\n{'=' * 60}")
    print(f"INTENT.md 结构校验结果: {intent_path}")
    print(f"{'=' * 60}\n")

    counts = Counter(status for _check_id, status, _message in results)
    for check_id, status, message in results:
        icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[status]
        print(f"  {icon} {check_id}: {message}")

    print(f"\n{'=' * 60}")
    print(
        f"  PASS: {counts['PASS']}  WARN: {counts['WARN']}  FAIL: {counts['FAIL']}"
    )
    if counts["FAIL"]:
        print("  结论: 结构不符合当前契约，不得交接")
        return 1
    print("  结论: 结构符合当前契约；语义仍需用户复核")

    # 基线对比
    if baseline_ref:
        baseline_content = _read_git_baseline(intent_path, baseline_ref)
        if baseline_content is None:
            print(f"\n  [WARN] 无法从 git 读取基线版本（ref: {baseline_ref}），跳过基线对比")
        else:
            warnings = _compare_baseline(baseline_content, content)
            if warnings:
                print(f"\n{'=' * 60}")
                print(f"基线对比（ref: {baseline_ref}）")
                print(f"{'=' * 60}\n")
                for w in warnings:
                    print(f"  [WARN] {w}")
            else:
                print(f"\n  基线对比（ref: {baseline_ref}）：无变化")

    return 0


if __name__ == "__main__":
    sys.exit(main())
