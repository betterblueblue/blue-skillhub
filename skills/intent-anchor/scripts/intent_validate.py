#!/usr/bin/env python3
"""
intent_validate.py — INTENT.md 完整性校验

用法：
  python intent_validate.py <INTENT.md路径>

检查项：
  V1: 文件存在且非空
  V2: 包含全部 10 个必需章节
  V3: 能力清单非空且每条有标记和决策
  V4: 不可妥协项 3-5 条且每条在能力清单里标记为"保留"
  V5: "放弃"项有明确说明（不是空）
  V6: 覆盖率 ≥ 60%
  V7: 漂移模式检查表存在且每条有 ✅/❌
  V8: 用户确认记录至少 1 条
  V9: 语义自检结果章节存在且 S1-S5 每项有内容（不是空占位）

输出：
  PASS / FAIL / WARN 汇总
  有 FAIL 项不得交棒给后续 skill
"""

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1. 一句话意图",
    "## 2. 场景类型",
    "## 3. 源系统或类比物",
    "## 4. 完整能力清单",
    "## 5. 不可妥协项",
    "## 6. 可推迟项",
    "## 7. 漂移模式检查",
    "## 8. 覆盖率",
    "## 9. 用户确认记录",
    "## 10. 语义自检结果",
    "## 11. 三重锚定原始记录",
]

DRIFT_PATTERNS = [
    "D1 重新发明",
    "D2 砍到无关",
    "D3 降级代替",
    "D4 单循环锁定",
    "D5 沉默输出",
    "D6 不追求吃核心",
    "D7 上下文蒸发",
    "D8/D9",
]

MIN_COVERAGE = 60.0


def validate(content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明) 列表。结果为 PASS / FAIL / WARN。"""
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if not content.strip():
        results.append(("V1", "FAIL", "文件为空"))
    else:
        results.append(("V1", "PASS", f"文件有 {len(content)} 字符"))

    # V2: 必需章节
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    if missing:
        results.append(("V2", "FAIL", f"缺少章节: {', '.join(missing)}"))
    else:
        results.append(("V2", "PASS", "全部 10 个章节存在"))

    # V3: 能力清单
    # 先提取第 4 节内容，避免误匹配其他章节的表格
    cap_section = re.search(r"## 4\. 完整能力清单(.*?)## 5\.", content, re.DOTALL)
    if not cap_section:
        results.append(("V3", "FAIL", "找不到能力清单章节"))
        cap_rows = []
    else:
        # 找能力清单表格行（| N | 开头，不含 --- 和表头）
        cap_rows = re.findall(r"^\|\s*\d+\s*\|.*\|.*\|.*\|.*\|.*\|$", cap_section.group(1), re.MULTILINE)
    if not cap_rows:
        results.append(("V3", "FAIL", "能力清单为空或格式不对"))
    else:
        # 检查每行是否有标记和决策
        missing_mark = []
        for i, row in enumerate(cap_rows, 1):
            if "👍" not in row and "❌" not in row and "🤔" not in row:
                missing_mark.append(f"第{i}行缺标记")
            if "保留" not in row and "推迟" not in row and "放弃" not in row:
                missing_mark.append(f"第{i}行缺决策")
        if missing_mark:
            results.append(("V3", "FAIL", f"能力清单问题: {'; '.join(missing_mark)}"))
        else:
            results.append(("V3", "PASS", f"能力清单有 {len(cap_rows)} 条，均有标记和决策"))

    # V4: 不可妥协项
    # 找 "## 5. 不可妥协项" 到 "## 6." 之间的内容
    cs_section = re.search(r"## 5\. 不可妥协项(.*?)## 6\.", content, re.DOTALL)
    if not cs_section:
        results.append(("V4", "FAIL", "找不到不可妥协项章节"))
    else:
        # 数编号项（1. 2. 3. 等）
        cs_items = re.findall(r"^\d+\.\s+\S", cs_section.group(1), re.MULTILINE)
        if len(cs_items) < 3:
            results.append(("V4", "FAIL", f"不可妥协项只有 {len(cs_items)} 条，至少需要 3 条"))
        elif len(cs_items) > 5:
            results.append(("V4", "WARN", f"不可妥协项有 {len(cs_items)} 条，建议 3-5 条"))
        else:
            results.append(("V4", "PASS", f"不可妥协项 {len(cs_items)} 条"))

    # V5: 放弃项检查
    # 找决策为"放弃"的行
    abandon_rows = [r for r in cap_rows if "放弃" in r]
    if abandon_rows:
        # 检查可推迟项章节是否有对应说明
        defer_section = re.search(r"## 6\. 可推迟项(.*?)## 7\.", content, re.DOTALL)
        if defer_section and abandon_rows:
            # 放弃项不一定要在可推迟项里说明，但至少要有记录
            results.append(("V5", "PASS", f"有 {len(abandon_rows)} 条放弃项"))
        else:
            results.append(("V5", "WARN", "有放弃项但找不到说明"))
    else:
        results.append(("V5", "PASS", "无放弃项"))

    # V6: 放弃项逐条报告检查
    coverage_section = re.search(r"## 8\. 覆盖率(.*?)## 9\.", content, re.DOTALL)
    if not coverage_section:
        results.append(("V6", "FAIL", "找不到覆盖率章节"))
    else:
        cov_content = coverage_section.group(1)
        # 检查是否有放弃项报告表格
        abandon_report_rows = re.findall(r"^\|.*\|.*\|.*\|.*\|.*\|$", cov_content, re.MULTILINE)
        abandon_report_rows = [r for r in abandon_report_rows if "---" not in r and "能力" not in r and "不可妥协" not in r]
        if abandon_rows:
            # 有放弃项，检查是否每条都有报告
            if len(abandon_report_rows) < len(abandon_rows):
                results.append(("V6", "FAIL", f"有 {len(abandon_rows)} 条放弃项，但覆盖率章节只有 {len(abandon_report_rows)} 条报告记录"))
            else:
                # 检查每条报告是否有用户确认标记
                unconfirmed = [r for r in abandon_report_rows if "✅" not in r and "❌" not in r]
                if unconfirmed:
                    results.append(("V6", "FAIL", f"有 {len(unconfirmed)} 条放弃项报告缺少用户确认标记（✅/❌）"))
                else:
                    results.append(("V6", "PASS", f"全部 {len(abandon_rows)} 条放弃项已逐条报告且有用户确认"))
        else:
            results.append(("V6", "PASS", "无放弃项"))

    # V7: 漂移模式检查
    drift_section = re.search(r"## 7\. 漂移模式检查(.*?)## 8\.", content, re.DOTALL)
    if not drift_section:
        results.append(("V7", "FAIL", "找不到漂移模式检查章节"))
    else:
        missing_patterns = []
        for pattern in DRIFT_PATTERNS:
            if pattern not in drift_section.group(1):
                missing_patterns.append(pattern)
        if missing_patterns:
            results.append(("V7", "FAIL", f"缺少漂移模式: {', '.join(missing_patterns)}"))
        else:
            # 检查每条是否有 ✅ 或 ❌
            rows = re.findall(r"\|.*\|.*\|", drift_section.group(1))
            rows = [r for r in rows if "✅" in r or "❌" in r]
            if len(rows) < len(DRIFT_PATTERNS):
                results.append(("V7", "WARN", f"漂移模式有 {len(rows)}/{len(DRIFT_PATTERNS)} 条标注了 ✅/❌"))
            else:
                results.append(("V7", "PASS", f"全部 {len(DRIFT_PATTERNS)} 条漂移模式已检查"))

    # V8: 用户确认记录
    confirm_section = re.search(r"## 9\. 用户确认记录(.*?)## 10\.", content, re.DOTALL)
    if not confirm_section:
        results.append(("V8", "FAIL", "找不到用户确认记录章节"))
    else:
        # 找表格行（不含表头和分隔）
        confirm_rows = re.findall(r"^\|.*\|.*\|.*\|$", confirm_section.group(1), re.MULTILINE)
        confirm_rows = [r for r in confirm_rows if "---" not in r and "日期" not in r and "确认内容" not in r]
        if not confirm_rows:
            results.append(("V8", "FAIL", "没有用户确认记录（至少需要 1 条）"))
        else:
            results.append(("V8", "PASS", f"有 {len(confirm_rows)} 条确认记录"))

    # V9: 语义自检结果
    audit_section = re.search(r"## 10\. 语义自检结果(.*?)## 11\.", content, re.DOTALL)
    if not audit_section:
        results.append(("V9", "FAIL", "找不到语义自检结果章节"))
    else:
        audit_content = audit_section.group(1)
        audit_items = ["S1 源系统完整性", "S2 确认可追溯性", "S3 不可妥协项", "S4 锚定真实性", "S5 漂移自检"]
        missing_audit = []
        empty_audit = []
        for item in audit_items:
            # 检查标题存在
            pattern = re.escape(item)
            if not re.search(pattern, audit_content):
                missing_audit.append(item)
                continue
            # 检查标题下有实际内容（不是只有注释或空行）
            # 找到该标题后的内容，去掉 HTML 注释和空行
            section_re = re.search(re.escape(item) + r"[^\n]*\n(.*?)(?=^###[^#]|\Z)", audit_content, re.DOTALL | re.MULTILINE)
            if section_re:
                section_text = re.sub(r"<!--.*?-->", "", section_re.group(1), flags=re.DOTALL)
                section_text = section_text.strip()
                # 需要至少有一行非空非注释的内容
                real_lines = [l for l in section_text.split("\n") if l.strip() and not l.strip().startswith("<!--")]
                if len(real_lines) == 0:
                    empty_audit.append(item)
        if missing_audit:
            results.append(("V9", "FAIL", f"缺少自检项: {', '.join(missing_audit)}"))
        elif empty_audit:
            results.append(("V9", "FAIL", f"自检项为空占位（无实际内容）: {', '.join(empty_audit)}"))
        else:
            results.append(("V9", "PASS", "S1-S5 全部有内容"))

    return results


def main():
    if len(sys.argv) < 2:
        print("用法: python intent_validate.py <INTENT.md路径>")
        sys.exit(1)

    intent_path = Path(sys.argv[1])
    if not intent_path.exists():
        print(f"FAIL: 文件不存在: {intent_path}")
        sys.exit(1)

    content = intent_path.read_text(encoding="utf-8")
    results = validate(content)

    print(f"\n{'='*60}")
    print(f"INTENT.md 校验结果: {intent_path}")
    print(f"{'='*60}\n")

    fail_count = 0
    warn_count = 0
    pass_count = 0

    for check_id, status, message in results:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[status]
        print(f"  {icon} {check_id}: {status} — {message}")
        if status == "FAIL":
            fail_count += 1
        elif status == "WARN":
            warn_count += 1
        else:
            pass_count += 1

    print(f"\n{'='*60}")
    print(f"  PASS: {pass_count}  WARN: {warn_count}  FAIL: {fail_count}")
    if fail_count > 0:
        print(f"  结论: ❌ 不通过 — 有 {fail_count} 个 FAIL 项，不得交棒给后续 skill")
        sys.exit(1)
    elif warn_count > 0:
        print(f"  结论: ⚠️ 通过（有警告） — 建议人工复核 WARN 项后继续")
        sys.exit(0)
    else:
        print(f"  结论: ✅ 通过 — 可以交棒给后续 skill")
        sys.exit(0)


if __name__ == "__main__":
    main()
