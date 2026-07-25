#!/usr/bin/env python3
"""intent-chain 校验脚本的公共 Markdown 解析函数。

四个函数从各校验脚本中提取，消除了重复实现：
  - section: 提取 ## 级章节内容
  - subsection: 提取 ### 级子节内容
  - table_rows: 提取 Markdown 表格数据行
  - has_placeholder: 检测模板占位符 {xxx}

各脚本的 _section 和 _subsection 实现存在细微差异（停止模式不同），
通过参数统一：

  section(content, heading, numbered=False)
    - numbered=True:  停止在下一个 ## N. 标题（用于 INTENT.md 的编号章节）
    - numbered=False: 停止在下一个任意 ## 标题（用于 PRD、issues、verify-record）

  subsection(content, heading, stop_at_h2=True)
    - heading 可以带 "### " 前缀，也可以只传标题文字
    - stop_at_h2=True:  停止在下一个 ### 或 ##（默认，更安全）
    - stop_at_h2=False: 只停止在下一个 ###（用于 INTENT.md 语义复核等场景）
"""

from __future__ import annotations

import re


def section(content: str, heading: str, numbered: bool = False) -> str:
    """提取 ## 级章节的正文内容。

    Args:
        content: 完整 Markdown 文本。
        heading: 章节标题，如 "## 4. 能力与决策" 或 "## Problem Statement"。
        numbered: True 时只匹配 ## N. 格式的下一个标题作为停止边界。

    Returns:
        章节正文文本；未找到时返回空字符串。
    """
    stop = r"^##\s+\d+\.\s" if numbered else r"^##\s+"
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?={stop}|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def subsection(content: str, heading: str, stop_at_h2: bool = True) -> str:
    """提取 ### 级子节的正文内容。

    Args:
        content: 包含子节的文本片段。
        heading: 子节标题，可以带 "### " 前缀，也可以只传标题文字。
        stop_at_h2: True 时同时以 ## 作为停止边界（更安全）。

    Returns:
        子节正文文本；未找到时返回空字符串。
    """
    clean = re.sub(r"^#+\s*", "", heading)
    stop = r"^###\s+" + (r"|^##\s+" if stop_at_h2 else "")
    match = re.search(
        rf"^###\s+{re.escape(clean)}\s*$\n?(.*?)(?={stop}|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def table_rows(content: str, header_first_cell: str) -> list[list[str]]:
    """从 Markdown 表格中提取数据行。

    跳过表头行和分隔行（:---:）。

    Args:
        content: 包含表格的文本片段。
        header_first_cell: 表头第一列的文本，用于跳过表头。

    Returns:
        数据行列表，每行是单元格文本列表。
    """
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


def has_placeholder(value: str) -> bool:
    """检测文本中是否包含模板占位符 {xxx}。"""
    return bool(re.search(r"\{[^{}]+\}", value))
