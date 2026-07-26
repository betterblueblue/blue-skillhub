#!/usr/bin/env python3
"""D5 漂移交叉检查：推迟/放弃的能力不得出现在下游实现承载区。

七种漂移模式里的 D5（推迟或放弃项被重新加入）此前只靠模型在漂移复核表里
自查；本脚本按 intent.md 第 4 节的推迟/放弃名单反查下游文档，给自查加一道
机械兜底。

排除规则（本检查能落地的关键——名单里的名字在很多位置是合法出现的）：
  1. 只扫「实现承载区」白名单：
     - prd.md：Solution / User Stories / Implementation Decisions /
       Acceptance Criteria / Testing Decisions
     - design.md：## 2. 能力设计
     - issues.md / dev-record.md：每个 ## Issue N 段
     不扫 intent.md（名单来源）、architecture.md（ID 级回流已由 design
     校验器 A3/X2 覆盖）、verify-record.md（漂移复核表合法提及）、
     PRD 的 Out of Scope、issues 的 Coverage Verification（排除说明合法提及）。
  2. 负面提及行守卫：行内含「不做/不实现/不支持/不包含/不含/推迟/放弃/
     暂不/排除」时跳过——design.md「不做什么」这类位置必须合法点名。
  3. 扫描前剥离 HTML 注释。

匹配：能力 ID 精确匹配（如 C03，前后不接字母数字）；能力名子串匹配
（名字不足 4 个字符时只做 ID 匹配，避免短词噪音）。

用法：
  python d5_check.py /path/to/intent-chain/{链路目录}

退出码：命中回流 → 1；无推迟/放弃项、无下游产物或无命中 → 0。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from markdown_parser import section, table_rows
finally:
    sys.path.pop(0)

RE_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
RE_NEGATIVE_LINE = re.compile(
    r"不做|不实现|不支持|不包含|不含|推迟|放弃|暂不|排除"
)

PRD_SECTIONS = [
    "## Solution",
    "## User Stories",
    "## Implementation Decisions",
    "## Acceptance Criteria",
    "## Testing Decisions",
]


def _deferred_from_intent(intent_text: str) -> list[tuple[str, str, str]]:
    """从第 4 节能力表取（能力 ID, 能力名, 决策）∈ 推迟/放弃。"""
    body = section(intent_text, "## 4. 能力与决策")
    deferred: list[tuple[str, str, str]] = []
    for row in table_rows(body, "能力 ID"):
        if len(row) >= 5 and row[4] in ("推迟", "放弃"):
            deferred.append((row[0], row[1], row[4]))
    return deferred


def _issue_blocks(text: str) -> list[str]:
    """取每个 ## Issue N 段（含标题行，到下一个 ## 级标题为止）。"""
    return [
        m.group(0)
        for m in re.finditer(r"^## Issue\s+\d+[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    ]


def _regions(chain_dir: Path):
    """迭代 (文件名, 区域名, 区域文本)——只产出实现承载区。"""
    prd = chain_dir / "prd.md"
    if prd.exists():
        text = RE_HTML_COMMENT.sub("", prd.read_text(encoding="utf-8"))
        for heading in PRD_SECTIONS:
            body = section(text, heading)
            if body.strip():
                yield ("prd.md", heading.lstrip("# ").strip(), body)

    design = chain_dir / "design.md"
    if design.exists():
        text = RE_HTML_COMMENT.sub("", design.read_text(encoding="utf-8"))
        body = section(text, "## 2. 能力设计")
        if body.strip():
            yield ("design.md", "能力设计", body)

    for fname in ("issues.md", "dev-record.md"):
        path = chain_dir / fname
        if path.exists():
            text = RE_HTML_COMMENT.sub("", path.read_text(encoding="utf-8"))
            for block in _issue_blocks(text):
                title = block.splitlines()[0].strip().lstrip("# ").strip()
                yield (fname, title, block)


def check(chain_dir: Path) -> tuple[list[str], list[str]]:
    """返回 (passes, fails)。fails 非空即存在 D5 回流嫌疑。"""
    passes: list[str] = []
    fails: list[str] = []

    intent = chain_dir / "intent.md"
    if not intent.exists():
        fails.append("D5: intent.md 不存在，无法读取推迟/放弃名单")
        return passes, fails

    deferred = _deferred_from_intent(intent.read_text(encoding="utf-8"))
    if not deferred:
        passes.append("D5: 无推迟/放弃项，无需反查")
        return passes, fails

    hits: list[str] = []
    scanned = 0
    for fname, region, body in _regions(chain_dir):
        scanned += 1
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or RE_NEGATIVE_LINE.search(stripped):
                continue
            for cid, name, decision in deferred:
                id_hit = re.search(rf"(?<![A-Za-z0-9]){re.escape(cid)}(?!\d)", stripped)
                name_hit = len(name) >= 4 and name in stripped
                if id_hit or name_hit:
                    hits.append(
                        f"{fname}「{region}」出现{decision}项 {cid}（{name}）: {stripped[:60]}"
                    )

    if scanned == 0:
        passes.append("D5: 尚无下游实现承载区可查（链路只有 intent.md）")
    elif hits:
        fails.extend(f"D5: {h}" for h in hits[:5])
        if len(hits) > 5:
            fails.append(f"D5: …另有 {len(hits) - 5} 处命中未展开")
    else:
        passes.append(
            f"D5: {len(deferred)} 个推迟/放弃项在 {scanned} 个实现承载区未发现回流"
        )
    return passes, fails


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python d5_check.py /path/to/intent-chain/{链路目录}")
        return 1
    chain_dir = Path(sys.argv[1])
    if not chain_dir.is_dir():
        print(f"FAIL: 链路目录不存在: {chain_dir}")
        return 1
    passes, fails = check(chain_dir)
    for line in passes:
        print(f"PASS: {line}")
    for line in fails:
        print(f"FAIL: {line}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
