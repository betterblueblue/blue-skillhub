#!/usr/bin/env python3
"""工单类型识别——issues / dev / chain 三个校验器共用，避免各写一份后漂移。

决策工单（intent-issues「决策工单」节）：类型行写「需拍板（决策，不写代码）」。
它只记录要用户拍板的问题，不写代码、不进 dev-record，
所以 dev_validate 和 chain_validate 统计「需要开发记录的工单」时要把它排除。
"""

from __future__ import annotations

import re

# 与 issues_validate 的拆分规则一致：标题里的冒号不强制
ISSUE_HEADING_RE = re.compile(r"^##\s+Issue\s+(\d+)\b", re.MULTILINE)
ISSUE_TYPE_RE = re.compile(r"^-\s*\*\*类型\*\*[：:]\s*(.+)$", re.MULTILINE)
DECISION_TYPE_MARKERS = ("需拍板", "决策")


def is_decision_issue(issue_text: str) -> bool:
    """单个工单段落是否为决策工单（与 issues_validate 的 V2/V14 判定一致）。"""
    match = ISSUE_TYPE_RE.search(issue_text)
    return bool(match) and any(marker in match.group(1) for marker in DECISION_TYPE_MARKERS)


def split_issue_sections(issues_content: str) -> list[tuple[str, str]]:
    """按 `## Issue N:` 标题切分，返回 [(编号, 段落文本), ...]。

    最后一个工单截止到下一个 `##` 级标题（如「覆盖核对」）或文件末尾。
    """
    matches = list(ISSUE_HEADING_RE.finditer(issues_content))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            tail = re.search(r"^##\s+", issues_content[match.end():], re.MULTILINE)
            end = match.end() + tail.start() if tail else len(issues_content)
        sections.append((match.group(1), issues_content[start:end]))
    return sections


def implementation_issue_numbers(issues_content: str) -> set[str]:
    """需要开发记录的工单编号（排除决策工单）。"""
    return {
        number
        for number, section in split_issue_sections(issues_content)
        if not is_decision_issue(section)
    }
