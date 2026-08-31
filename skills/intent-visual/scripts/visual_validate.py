#!/usr/bin/env python3
"""visual-design.md 结构校验，并核对配套 visual-baseline.html 存在。

用法：
  python visual_validate.py /path/to/intent-chain/{链路目录}/visual-design.md [/path/to/visual-baseline.html]

visual-baseline.html 省略时，取 visual-design.md 同目录下的同名固定文件。

检查项：
  V1: 文件非空
  V2: 九个必需章节齐全（概览 / 色板 / 字体与字号阶梯 / 间距与圆角 / 组件样式 /
      布局与响应式 / 动效 / 明确不采用 / 来源与替代）
  V3: 概览非空且无占位符
  V4: 色板表至少一行，值列含合法色值（#RGB / #RRGGBB），无占位符
  V5: 字体表至少一行，字体栈必须带 fallback（逗号 + 通用族或 system-ui/ui-*），无占位符
  V6: 组件样式表至少一行且含默认态/hover/禁用三态列，无占位符
  V7: 「明确不采用」非空——负面清单不得为空或只写「无」
  V8: 「来源与替代」非空，记录了来源（URL / commit / 原创）、提取方式与日期，无占位符
  V9: 全文无模板占位符 {xxx} 残留
  V10: visual-baseline.html 存在、非空且含样式定义

本脚本验证结构契约；风格本身是否符合用户期望由样张确认和 verify 截图比对保证。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_COMMON_DIR = Path(__file__).resolve().parent.parent.parent / "_common"
if str(_COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(_COMMON_DIR))
from markdown_parser import section as _section, table_rows as _table_rows, has_placeholder as _has_placeholder

REQUIRED_SECTIONS = {
    "## 1. 概览": "概览",
    "## 2. 色板": "色板",
    "## 3. 字体与字号阶梯": "字体与字号阶梯",
    "## 4. 间距与圆角": "间距与圆角",
    "## 5. 组件样式": "组件样式",
    "## 6. 布局与响应式": "布局与响应式",
    "## 7. 动效": "动效",
    "## 8. 明确不采用": "明确不采用",
    "## 9. 来源与替代": "来源与替代",
}

_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
_FALLBACK_RE = re.compile(r"system-ui|ui-sans-serif|ui-serif|ui-monospace|sans-serif|serif|monospace|cursive|fantasy", re.IGNORECASE)
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)


def _no_value(section: str) -> bool:
    """节内容为空，或只有「无」一类的占位回答。"""
    stripped = section.strip()
    if not stripped:
        return True
    items = [line.strip() for line in stripped.splitlines() if re.match(r"^[-*]\s+\S+", line.strip())]
    if items:
        return all(re.fullmatch(r"[-*]\s*无[。.]?", item) for item in items)
    return False


def validate(content: str, baseline_content: str | None, baseline_exists: bool) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []

    # V1: 文件非空
    if len(content.strip()) > 0:
        results.append(("V1", "PASS", f"文件有 {len(content)} 个字符"))
    else:
        results.append(("V1", "FAIL", "文件为空"))
        return results

    # V2: 九个必需章节
    missing = [name for heading, name in REQUIRED_SECTIONS.items() if not _section(content, heading, numbered=True)]
    if missing:
        results.append(("V2", "FAIL", f"缺少必需章节: {', '.join(missing)}"))
    else:
        results.append(("V2", "PASS", "九个必需章节齐全"))

    # V3: 概览
    overview = _section(content, "## 1. 概览", numbered=True)
    if not overview.strip():
        results.append(("V3", "FAIL", "概览为空"))
    elif _has_placeholder(overview):
        results.append(("V3", "FAIL", "概览仍含模板占位符"))
    else:
        results.append(("V3", "PASS", "概览已填写"))

    # V4: 色板——值列必须含合法色值
    palette_rows = _table_rows(_section(content, "## 2. 色板", numbered=True), "用途")
    v4_errors: list[str] = []
    if not palette_rows:
        v4_errors.append("色板表没有数据行")
    for index, row in enumerate(palette_rows, 1):
        if len(row) < 2:
            v4_errors.append(f"色板第 {index} 行应有 3 列")
            continue
        if any(_has_placeholder(cell) for cell in row):
            v4_errors.append(f"色板「{row[0]}」仍含模板占位符")
        if not _HEX_RE.search(row[1]):
            v4_errors.append(f"色板「{row[0]}」的值列没有合法色值（#RGB/#RRGGBB）: {row[1]}")
    if v4_errors:
        results.append(("V4", "FAIL", "；".join(v4_errors)))
    else:
        results.append(("V4", "PASS", f"色板 {len(palette_rows)} 行均为合法色值"))

    # V5: 字体栈必须带 fallback
    font_rows = _table_rows(_section(content, "## 3. 字体与字号阶梯", numbered=True), "元素")
    v5_errors: list[str] = []
    if not font_rows:
        v5_errors.append("字体表没有数据行")
    for index, row in enumerate(font_rows, 1):
        if len(row) < 4:
            v5_errors.append(f"字体第 {index} 行应有 4 列")
            continue
        if any(_has_placeholder(cell) for cell in row):
            v5_errors.append(f"字体「{row[0]}」仍含模板占位符")
        stack = row[1]
        if "," not in stack or not _FALLBACK_RE.search(stack):
            v5_errors.append(f"字体「{row[0]}」的字体栈缺 fallback: {stack}")
    if v5_errors:
        results.append(("V5", "FAIL", "；".join(v5_errors)))
    else:
        results.append(("V5", "PASS", f"字体阶梯 {len(font_rows)} 行均带 fallback"))

    # V6: 组件样式三态
    component_rows = _table_rows(_section(content, "## 5. 组件样式", numbered=True), "组件")
    v6_errors: list[str] = []
    if not component_rows:
        v6_errors.append("组件样式表没有数据行")
    for index, row in enumerate(component_rows, 1):
        if len(row) < 4:
            v6_errors.append(f"组件第 {index} 行应有 4 列（组件/默认态/hover/禁用）")
            continue
        if any(_has_placeholder(cell) for cell in row):
            v6_errors.append(f"组件「{row[0]}」仍含模板占位符")
    if v6_errors:
        results.append(("V6", "FAIL", "；".join(v6_errors)))
    else:
        results.append(("V6", "PASS", f"组件样式 {len(component_rows)} 行三态齐全"))

    # V7: 明确不采用——负面清单不得为空
    avoid_section = _section(content, "## 8. 明确不采用", numbered=True)
    if _no_value(avoid_section):
        results.append(("V7", "FAIL", "「明确不采用」为空或只写「无」——负面清单必须逐条列出"))
    elif _has_placeholder(avoid_section):
        results.append(("V7", "FAIL", "「明确不采用」仍含模板占位符"))
    else:
        results.append(("V7", "PASS", "负面清单已逐条列出"))

    # V8: 来源与替代
    source_section = _section(content, "## 9. 来源与替代", numbered=True)
    v8_errors: list[str] = []
    if not source_section.strip():
        v8_errors.append("「来源与替代」为空")
    elif _has_placeholder(source_section):
        v8_errors.append("「来源与替代」仍含模板占位符")
    else:
        has_origin = bool(re.search(r"https?://", source_section)) or bool(_COMMIT_RE.search(source_section)) or ("原创" in source_section)
        if not has_origin:
            v8_errors.append("来源节必须记录来源 URL、commit 或声明「原创」")
        if not _DATE_RE.search(source_section):
            v8_errors.append("来源节必须记录提取/参考日期（YYYY-MM-DD）")
    if v8_errors:
        results.append(("V8", "FAIL", "；".join(v8_errors)))
    else:
        results.append(("V8", "PASS", "来源与替代记录完整"))

    # V9: 全文无占位符残留
    if _has_placeholder(content):
        results.append(("V9", "FAIL", "全文仍有模板占位符 {xxx} 残留"))
    else:
        results.append(("V9", "PASS", "无占位符残留"))

    # V10: 配套基线页
    if not baseline_exists:
        results.append(("V10", "FAIL", "visual-baseline.html 不存在——验收对照物缺失"))
    elif baseline_content is None or not baseline_content.strip():
        results.append(("V10", "FAIL", "visual-baseline.html 为空"))
    elif "<style" not in baseline_content.lower():
        results.append(("V10", "FAIL", "visual-baseline.html 不含样式定义（应有 <style> 块）"))
    else:
        results.append(("V10", "PASS", "visual-baseline.html 存在且含样式定义"))

    return results


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("用法: python visual_validate.py /path/to/intent-chain/{链路目录}/visual-design.md [/path/to/visual-baseline.html]")
        return 1

    design_path = Path(sys.argv[1])
    if not design_path.exists():
        print(f"FAIL: visual-design.md 不存在: {design_path}")
        return 1

    baseline_path = Path(sys.argv[2]) if len(sys.argv) == 3 else design_path.parent / "visual-baseline.html"
    baseline_exists = baseline_path.exists()
    baseline_content = baseline_path.read_text(encoding="utf-8", errors="replace") if baseline_exists else None

    content = design_path.read_text(encoding="utf-8")
    results = validate(content, baseline_content, baseline_exists)

    print(f"\n{'=' * 60}")
    print(f"Visual 校验结果: {design_path}")
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
        print("  结论: 视觉规范不符合结构契约，不得登记进 INTENT 第 12 节")
        return 1
    print("  结论: 视觉规范结构完整，可登记进 INTENT 第 12 节")
    return 0


if __name__ == "__main__":
    sys.exit(main())
