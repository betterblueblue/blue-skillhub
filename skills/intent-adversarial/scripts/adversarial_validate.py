#!/usr/bin/env python3
"""adversarial-record.md 结构与 INTENT.md 交叉校验。

用法：
  python adversarial_validate.py /path/to/intent-chain/{链路目录}/adversarial-record.md /path/to/intent-chain/{链路目录}/intent.md

检查项：
  A1: 文件非空
  A2: 六个必需章节齐全（数据准备 / 安全攻击结果 / 并发一致性结果 / 性能基准 / 缺陷清单 / 结论）
  A3: INTENT 第 16 节每条 SF 编号在安全攻击结果中有至少一条关联用例
  A4: INTENT 第 15 节每条 CC 编号在并发一致性结果中有对应记录且通过
  A5: 缺陷清单中高危缺陷未全部修复 → FAIL（阻止交付）
  A6: 结论与缺陷状态一致——存在未修复缺陷时结论不得为「通过」

本脚本验证结构契约与交叉引用；攻击用例本身的质量由执行过程保证。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_COMMON_DIR = Path(__file__).resolve().parent.parent.parent / "_common"
if str(_COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(_COMMON_DIR))
from markdown_parser import section as _section, table_rows as _table_rows


def _has_placeholder(text: str) -> bool:
    return bool(re.search(r"\{[^}]*\}", text))


def _parse_ids(intent_content: str, heading: str, prefix: str) -> set[str]:
    section = _section(intent_content, heading)
    rows = _table_rows(section, "要求 ID")
    return {row[0] for row in rows if row and row[0].startswith(prefix)}


def validate(content: str, intent_content: str) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []

    # A1: 文件非空
    if len(content.strip()) > 0:
        results.append(("A1", "PASS", f"文件有 {len(content)} 个字符"))
    else:
        results.append(("A1", "FAIL", "文件为空"))
        return results

    # A2: 六个必需章节
    required = {
        "## 2. 数据准备": "数据准备",
        "## 3. 安全攻击结果": "安全攻击结果",
        "## 4. 并发一致性结果": "并发一致性结果",
        "## 5. 性能基准": "性能基准",
        "## 6. 缺陷清单": "缺陷清单",
        "## 7. 结论": "结论",
    }
    missing = [name for heading, name in required.items() if not _section(content, heading)]
    if missing:
        results.append(("A2", "FAIL", f"缺少必需章节: {', '.join(missing)}"))
    else:
        results.append(("A2", "PASS", "六个必需章节齐全"))

    # A3: SF 交叉——每条 SF 在安全攻击结果中被引用
    sf_ids = _parse_ids(intent_content, "## 16. 安全要求", "SF")
    if sf_ids:
        atk_section = _section(content, "## 3. 安全攻击结果")
        atk_rows = _table_rows(atk_section, "类别")
        linked = set()
        for row in atk_rows:
            if len(row) >= 3:
                linked |= {m.group(0) for m in re.finditer(r"SF\d+", row[2])}
        uncovered = sorted(sf_ids - linked)
        if uncovered:
            results.append(("A3", "FAIL", f"安全要求未被任何攻击用例关联: {', '.join(uncovered)}"))
        else:
            results.append(("A3", "PASS", f"全部 {len(sf_ids)} 条安全要求有攻击用例关联"))
    else:
        results.append(("A3", "PASS", "INTENT 无安全要求，不适用"))

    # A4: CC 交叉——每条 CC 在并发一致性结果中有记录且通过
    cc_ids = _parse_ids(intent_content, "## 15. 性能要求", "CC")
    if cc_ids:
        cc_section = _section(content, "## 4. 并发一致性结果")
        cc_rows = _table_rows(cc_section, "要求 ID")
        cc_map = {row[0]: row for row in cc_rows if row and row[0].startswith("CC")}
        a4_errors: list[str] = []
        for cc in sorted(cc_ids):
            if cc not in cc_map:
                a4_errors.append(f"{cc} 无实测记录")
                continue
            row = cc_map[cc]
            passed_col = row[4] if len(row) >= 5 else ""
            if passed_col.strip() != "是":
                a4_errors.append(f"{cc} 未通过（实测：{passed_col or '空'}）")
        if a4_errors:
            results.append(("A4", "FAIL", "; ".join(a4_errors)))
        else:
            results.append(("A4", "PASS", f"全部 {len(cc_ids)} 条并发一致性断言实测通过"))
    else:
        results.append(("A4", "PASS", "INTENT 无并发一致性要求，不适用"))

    # A5: 高危缺陷必须全部修复
    defect_section = _section(content, "## 6. 缺陷清单")
    defect_rows = _table_rows(defect_section, "缺陷 ID")
    high_open: list[str] = []
    for row in defect_rows:
        if len(row) < 5:
            continue
        defect_id, severity, _desc, _evidence, status = row[0], row[1], row[2], row[3], row[4]
        if "高" in severity and "fixed" not in status.lower():
            high_open.append(defect_id)
    if high_open:
        results.append(("A5", "FAIL", f"高危缺陷未修复，阻止交付: {', '.join(high_open)}"))
    else:
        results.append(("A5", "PASS", "无未修复的高危缺陷"))

    # A6: 结论与缺陷状态一致
    conclusion = _section(content, "## 7. 结论")
    if defect_rows and high_open and "通过" in conclusion and "不通过" not in conclusion:
        results.append(("A6", "FAIL", "存在未修复高危缺陷，但结论为「通过」"))
    elif not conclusion.strip() or _has_placeholder(conclusion):
        results.append(("A6", "FAIL", "结论缺失或含占位符"))
    else:
        results.append(("A6", "PASS", "结论与缺陷状态一致"))

    return results


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("用法: python adversarial_validate.py /path/to/intent-chain/{链路目录}/adversarial-record.md [/path/to/intent.md]")
        return 1

    record_path = Path(sys.argv[1])
    if not record_path.exists():
        print(f"FAIL: adversarial-record.md 不存在: {record_path}")
        return 1

    intent_path = Path(sys.argv[2]) if len(sys.argv) == 3 else record_path.parent / "intent.md"
    if not intent_path.exists():
        print(f"FAIL: INTENT.md 不存在: {intent_path}")
        return 1

    content = record_path.read_text(encoding="utf-8")
    intent_content = intent_path.read_text(encoding="utf-8")
    results = validate(content, intent_content)

    print(f"\n{'=' * 60}")
    print(f"Adversarial 校验结果: {record_path}")
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
        print("  结论: 结构不符合当前契约或存在未关闭的高危缺陷，不得交接")
        return 1
    print("  结论: 对抗性验证记录完整且通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
