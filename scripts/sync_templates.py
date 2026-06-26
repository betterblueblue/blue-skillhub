#!/usr/bin/env python3
"""sync_templates.py — 检查 impact skill 模板自洽性。

impact-pro 已于 2026-06-26 合并到 impact。本脚本不再做双向同步，
改为检查 impact/templates/ 目录下模板文件的完整性（文件存在且非空）。

历史：原脚本以 impact-pro/templates/ 为源同步到 impact/templates/。
合并后 impact-pro 已归档，impact/templates/ 成为唯一源。

用法：
    python scripts/sync_templates.py           # 检查模板完整性
    python scripts/sync_templates.py --check   # 同上（兼容 L0 测试调用）

退出码：
    0 = 一切正常
    1 = 发现问题（模板缺失或为空）
"""

import argparse
import sys
from pathlib import Path

# 脚本所在目录的父目录 = 仓库根目录
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

TEMPLATES_DIR = REPO_ROOT / "skills" / "impact" / "templates"

# 预期模板文件清单（合并后 impact 应包含的全部模板）
EXPECTED_TEMPLATES = [
    "000-context-pack.md",
    "005-change-summary.md",
    "010-requirements.md",
    "020-design.md",
    "030-implementation.md",
    "040-light.md",
    "060-preflight.md",
    "090-execution-record.md",
    "_active-state.md",
    "subagent-decisions.md",
]


def do_check() -> int:
    """检查模板目录完整性和非空。"""
    if not TEMPLATES_DIR.exists():
        print(f"ERROR: 模板目录不存在: {TEMPLATES_DIR}")
        return 1

    print(f"模板目录: {TEMPLATES_DIR}")
    print(f"预期模板: {len(EXPECTED_TEMPLATES)} 个")
    print()

    all_ok = True
    problems = []

    for name in EXPECTED_TEMPLATES:
        path = TEMPLATES_DIR / name
        if not path.exists():
            print(f"  FAIL  {name} (文件不存在)")
            problems.append(name)
            all_ok = False
        elif path.stat().st_size == 0:
            print(f"  FAIL  {name} (文件为空)")
            problems.append(name)
            all_ok = False
        else:
            print(f"  OK    {name}")

    # 检查是否有预期之外的文件（信息性提示，不算 FAIL）
    actual_files = {f.name for f in TEMPLATES_DIR.iterdir() if f.is_file()}
    expected_set = set(EXPECTED_TEMPLATES)
    extra = actual_files - expected_set
    if extra:
        print()
        print(f"  注意: 发现 {len(extra)} 个额外模板文件（不影响检查）:")
        for name in sorted(extra):
            print(f"        {name}")

    print()
    if all_ok:
        print(f"一致: {len(EXPECTED_TEMPLATES)}/{len(EXPECTED_TEMPLATES)} 个预期模板")
        return 0
    else:
        print(f"不一致: {len(problems)}/{len(EXPECTED_TEMPLATES)} 个模板有问题")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="检查 impact skill 模板完整性"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="兼容 L0 测试调用（行为与不带参数相同）",
    )
    args = parser.parse_args()

    return do_check()


if __name__ == "__main__":
    sys.exit(main())
