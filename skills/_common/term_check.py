#!/usr/bin/env python3
"""术语落地交叉检查：术语表的原始术语不得出现在前端源码的用户可见内容里。

毕业考实测逃逸（2026-07-27）：术语表正确登记"金刚区→首页功能入口"，但原始
术语沿能力名合法繁殖到代码与界面，各站校验只查"术语表存在、被引用"，无一站
查实现层落地。本检查是兜底层（源头层见 intent_validate V15）。

规则：
  1. 从 intent.md 第 13 节术语表取"原始术语"列。
  2. 扫描链路目录所在项目根下的前端 UI 文件（.vue/.html/.jsx/.tsx）。
  3. 排除：node_modules/dist/build/unpackage/.git/intent-chain，以及
     intent.md 第 12 节设计标准里登记的素材路径（原型和设计稿是输入材料，
     允许包含原始术语）。
  4. 注释行豁免（以 //、/*、*、<!-- 开头的行）——注释不是用户可见内容；
     中文术语不会出现在标识符里，因此非注释行命中即视为文案命中。
  5. 命中 → FAIL 并给出 文件:行 与摘录；无术语或无前端文件 → PASS。

用法：python term_check.py /path/to/intent-chain/{链路目录}
退出码：命中 → 1；其余 → 0。
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

UI_SUFFIXES = {".vue", ".html", ".jsx", ".tsx"}
EXCLUDED_DIRS = {"node_modules", "dist", "build", "unpackage", ".git", "intent-chain"}
RE_COMMENT_LINE = re.compile(r"^\s*(//|/\*|\*|<!--)")
RE_BACKTICK_PATH = re.compile(r"`([^`]+)`")


def _terms_from_intent(intent_text: str) -> list[str]:
    rows = table_rows(section(intent_text, "## 13. 术语表"), "原始术语")
    return [row[0] for row in rows if len(row) == 4 and row[0]]


def _design_material_roots(intent_text: str) -> set[str]:
    """第 12 节设计标准里登记的素材路径的首段目录名。"""
    roots: set[str] = set()
    for token in RE_BACKTICK_PATH.findall(section(intent_text, "## 12. 设计标准")):
        first = token.replace("\\", "/").lstrip("./").split("/")[0].strip()
        if first and "." not in first:
            roots.add(first)
        elif first:
            roots.add(first)  # 单文件素材也按首段记录
    return roots


def _ui_files(project_root: Path, extra_excluded: set[str]):
    excluded = EXCLUDED_DIRS | extra_excluded
    for path in project_root.rglob("*"):
        if not (path.is_file() and path.suffix in UI_SUFFIXES):
            continue
        rel_parts = path.relative_to(project_root).parts
        if any(part in excluded for part in rel_parts):
            continue
        yield path


def check(chain_dir: Path) -> tuple[list[str], list[str]]:
    """返回 (passes, fails)。fails 非空即术语落地违约。"""
    passes: list[str] = []
    fails: list[str] = []

    intent = chain_dir / "intent.md"
    if not intent.exists():
        fails.append("术语落地: intent.md 不存在，无法读取术语表")
        return passes, fails

    intent_text = intent.read_text(encoding="utf-8")
    terms = _terms_from_intent(intent_text)
    if not terms:
        passes.append("术语落地: 术语表为空，无需反查")
        return passes, fails

    if chain_dir.resolve().parent.name != "intent-chain":
        passes.append("术语落地: 链路目录不在 intent-chain/ 下，无法定位项目根，跳过")
        return passes, fails
    project_root = chain_dir.resolve().parent.parent

    hits: list[str] = []
    scanned = 0
    for ui_file in _ui_files(project_root, _design_material_roots(intent_text)):
        scanned += 1
        try:
            lines = ui_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            if RE_COMMENT_LINE.match(line):
                continue
            for term in terms:
                if term in line:
                    rel = ui_file.relative_to(project_root)
                    hits.append(
                        f"{rel}:{lineno} 出现原始术语「{term}」（应使用界面文案侧）: "
                        f"{line.strip()[:50]}"
                    )

    if scanned == 0:
        passes.append("术语落地: 项目根下无前端 UI 文件，无需反查")
    elif hits:
        fails.extend(f"术语落地: {h}" for h in hits[:5])
        if len(hits) > 5:
            fails.append(f"术语落地: …另有 {len(hits) - 5} 处命中未展开")
    else:
        passes.append(
            f"术语落地: {len(terms)} 个原始术语在 {scanned} 个前端文件中零出现"
        )
    return passes, fails


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python term_check.py /path/to/intent-chain/{链路目录}")
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
