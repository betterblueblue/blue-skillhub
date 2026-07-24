#!/usr/bin/env python3
"""dev-record.md 结构与工单文件交叉引用校验。

用法：
  python dev_validate.py /path/to/intent-chain/{链路目录}/dev-record.md /path/to/intent-chain/{链路目录}/issues.md

检查项：
  V1: 文件非空
  V2: 每个工单有开发记录段（含 TDD 过程、验证结果、工单状态）
  V3: 每条 Then 有验证等级（V1/V2），V2 必须附命令输出
  V4: 标 done 的工单：所有 Then >= V2

本脚本不能验证命令输出是否真实，也不能证明开发产物符合
用户真实想法。PASS 只表示文件满足当前结构契约。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ISSUE_HEADING_RE = re.compile(r"^##\s+Issue\s+(\d+):\s*(.+)$", re.MULTILINE)
THEN_RE = re.compile(
    r"^\s*-\s*\[([ xX])\]\s*(?:Then|And):\s*(.+)$",
    re.MULTILINE,
)
STATUS_RE = re.compile(r"^-\s*状态[：:]\s*(.+)$", re.MULTILINE)
LEVEL_RE = re.compile(r"V([0-2])")
SCENARIO_RE = re.compile(r"^\*\*\[P\d{2,}\]", re.MULTILINE)
TDD_RE = re.compile(r"###\s+TDD\s+过程")
RED_RE = re.compile(r"####\s+Red")
GREEN_RE = re.compile(r"####\s+Green")


def _split_issues(content: str) -> list[str]:
    issue_starts = [(m.start(), m.end()) for m in ISSUE_HEADING_RE.finditer(content)]
    if not issue_starts:
        return []
    issues: list[str] = []
    for i, (start, _end) in enumerate(issue_starts):
        end = issue_starts[i + 1][0] if i + 1 < len(issue_starts) else None
        if end is None:
            summary_pos = content.find("## 开发总结", start)
            end = summary_pos if summary_pos != -1 else len(content)
        issues.append(content[start:end])
    return issues


def _parse_issue_headings(issues_content: str) -> list[str]:
    return [
        m.group(0)
        for m in re.finditer(r"^##\s+Issue\s+\d+:\s*.+$", issues_content, re.MULTILINE)
    ]


def _parse_then_lines(issue_content: str) -> list[tuple[str, str, str]]:
    """提取工单验证记录中的 Then/And 条目。

    返回 [(check_mark, text, level), ...]。
    check_mark 为 'x' 或 ' '。
    level 为 'V0'/'V1'/'V2' 或 ''（未标注）。
    """
    results: list[tuple[str, str, str]] = []
    for m in THEN_RE.finditer(issue_content):
        check = m.group(1).strip().lower()
        text = m.group(2).strip()
        level_match = LEVEL_RE.search(text)
        level = level_match.group(0) if level_match else ""
        results.append((check, text, level))
    return results


def _parse_issue_status(issue_content: str) -> str | None:
    m = STATUS_RE.search(issue_content)
    return m.group(1).strip() if m else None


def _has_scenario_block(issue_content: str) -> bool:
    return bool(SCENARIO_RE.search(issue_content))


def _has_tdd_section(issue_content: str) -> bool:
    return bool(TDD_RE.search(issue_content))


def _has_red_section(issue_content: str) -> bool:
    return bool(RED_RE.search(issue_content))


def _has_green_section(issue_content: str) -> bool:
    return bool(GREEN_RE.search(issue_content))


def _has_command_output(text: str) -> bool:
    """检查 Then 文本中是否包含命令输出证据。"""
    return bool(
        re.search(r"命令\s*`?.+`?", text)
        or re.search(r"输出[:：]", text)
    )


def validate(dev_content: str, issues_content: str) -> list[tuple[str, str, str]]:
    """返回 (检查项, 结果, 说明)。"""
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if dev_content.strip():
        results.append(("V1", "PASS", f"文件有 {len(dev_content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    dev_issues = _split_issues(dev_content)
    issues_headings = _parse_issue_headings(issues_content)

    # V2: 每个工单有开发记录段（含 TDD 过程、验证结果、工单状态）
    if not dev_issues:
        results.append(("V2", "FAIL", "DEV-RECORD 中未找到工单开发记录"))
    else:
        dev_issue_count = len(dev_issues)
        issues_count = len(issues_headings)
        v2_errors: list[str] = []
        if dev_issue_count < issues_count:
            v2_errors.append(
                f"工单文件有 {issues_count} 个工单，DEV-RECORD 只记录了 {dev_issue_count} 个"
            )
        for issue in dev_issues:
            heading_match = ISSUE_HEADING_RE.search(issue)
            issue_num = heading_match.group(1) if heading_match else "?"
            if not _has_scenario_block(issue):
                v2_errors.append(f"Issue {issue_num} 缺少场景块")
            if not _has_tdd_section(issue):
                v2_errors.append(f"Issue {issue_num} 缺少 TDD 过程段")
            elif not _has_red_section(issue):
                v2_errors.append(f"Issue {issue_num} 缺少 Red 段")
            elif not _has_green_section(issue):
                v2_errors.append(f"Issue {issue_num} 缺少 Green 段")
            if not _parse_issue_status(issue):
                v2_errors.append(f"Issue {issue_num} 缺少状态行")
        if v2_errors:
            results.append(("V2", "FAIL", "; ".join(v2_errors)))
        else:
            results.append(("V2", "PASS", f"全部 {dev_issue_count} 个工单有完整开发记录"))

    # V3: 每条 Then 有验证等级，V2 必须附命令输出
    v3_errors: list[str] = []
    total_thens = 0
    for issue in dev_issues:
        heading_match = ISSUE_HEADING_RE.search(issue)
        issue_label = heading_match.group(0) if heading_match else "未知工单"
        then_lines = _parse_then_lines(issue)
        if not then_lines:
            v3_errors.append(f"{issue_label} 没有可勾选的 Then/And 条目")
        else:
            total_thens += len(then_lines)
            for check, text, level in then_lines:
                if not level:
                    v3_errors.append(f"{issue_label} 的条目缺少验证等级: {text[:50]}")
                elif level == "V2" and not _has_command_output(text):
                    v3_errors.append(
                        f"{issue_label} 的条目标 V2 但缺少命令输出证据: {text[:50]}"
                    )
    if v3_errors:
        results.append(("V3", "FAIL", "; ".join(v3_errors)))
    else:
        results.append(("V3", "PASS", f"共 {total_thens} 条 Then/And，均有验证等级和证据"))

    # V4: 标 done 的工单：所有 Then >= V2
    v4_errors: list[str] = []
    for issue in dev_issues:
        heading_match = ISSUE_HEADING_RE.search(issue)
        issue_label = heading_match.group(0) if heading_match else "未知工单"
        status = _parse_issue_status(issue)
        if status and "done" in status.lower():
            then_lines = _parse_then_lines(issue)
            for check, text, level in then_lines:
                if check != "x":
                    v4_errors.append(f"{issue_label} 标 done 但有未通过项: {text[:50]}")
                elif level and level != "V2":
                    v4_errors.append(
                        f"{issue_label} 标 done 但条目仅为 {level}（需 V2）: {text[:50]}"
                    )
    if v4_errors:
        results.append(("V4", "FAIL", "; ".join(v4_errors)))
    else:
        done_count = sum(
            1
            for issue in dev_issues
            if (status := _parse_issue_status(issue)) and "done" in status.lower()
        )
        results.append(("V4", "PASS", f"{done_count} 个工单标 done，所有条目均达 V2"))

    return results


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: python dev_validate.py /path/to/intent-chain/{链路目录}/dev-record.md /path/to/intent-chain/{链路目录}/issues.md")
        return 1

    dev_path = Path(sys.argv[1])
    issues_path = Path(sys.argv[2])

    if not dev_path.exists():
        print(f"FAIL: DEV-RECORD 文件不存在: {dev_path}")
        return 1
    if not issues_path.exists():
        print(f"FAIL: 工单文件不存在: {issues_path}")
        return 1

    dev_content = dev_path.read_text(encoding="utf-8")
    issues_content = issues_path.read_text(encoding="utf-8")
    results = validate(dev_content, issues_content)

    print(f"\n{'=' * 60}")
    print(f"DEV-RECORD 校验结果: {dev_path}")
    print(f"工单文件: {issues_path}")
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
