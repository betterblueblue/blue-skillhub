#!/usr/bin/env python3
"""sync_templates.py — 同步 impact 和 impact-pro 的共享模板。

以 impact-pro/templates/ 为唯一源，把共享模板同步到 impact/templates/。
共享模板 = 两个 templates/ 目录中都存在的文件名（取交集）。
impact-pro 独有的模板（如 final-readiness-audit.md、scorecard.md）不同步。
impact 独有的模板不存在（impact 是 impact-pro 的子集）。

用法：
    python scripts/sync_templates.py           # 同步（覆盖 impact 侧）
    python scripts/sync_templates.py --check   # 只比对不修改，供 L0 测试调用

退出码：
    0 = 一切正常（同步完成 或 --check 通过）
    1 = --check 模式下发现不一致
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# 脚本所在目录的父目录 = 仓库根目录
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

SOURCE_DIR = REPO_ROOT / "skills" / "impact-pro" / "templates"
TARGET_DIR = REPO_ROOT / "skills" / "impact" / "templates"

HASH_FILE = SCRIPT_DIR / ".template-sync-hash.json"


def file_sha256(path: Path) -> str:
    """计算文件内容的 SHA-256 哈希。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_shared_templates() -> list[str]:
    """返回两个 templates 目录中文件名的交集，按字母排序。"""
    source_files = {f.name for f in SOURCE_DIR.iterdir() if f.is_file()}
    target_files = {f.name for f in TARGET_DIR.iterdir() if f.is_file()}
    shared = sorted(source_files & target_files)
    return shared


def load_hash_record() -> dict:
    """加载上次同步的哈希记录。"""
    if HASH_FILE.exists():
        try:
            with open(HASH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_hash_record(record: dict) -> None:
    """保存哈希记录。"""
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write("\n")


def do_sync() -> int:
    """执行同步：把 SOURCE 的共享模板复制到 TARGET。"""
    shared = get_shared_templates()
    if not shared:
        print("ERROR: 没有找到共享模板")
        return 1

    print(f"源目录:   {SOURCE_DIR}")
    print(f"目标目录: {TARGET_DIR}")
    print(f"共享模板: {len(shared)} 个")
    print()

    synced = 0
    skipped = 0
    hash_record = {}

    for name in shared:
        src = SOURCE_DIR / name
        dst = TARGET_DIR / name

        src_hash = file_sha256(src)

        # 如果目标文件已存在且内容一致，跳过
        if dst.exists() and file_sha256(dst) == src_hash:
            print(f"  SKIP  {name} (已一致)")
            skipped += 1
        else:
            # 二进制模式复制，保持源文件字节完全一致（避免行尾符转换）
            with open(src, "rb") as f:
                content = f.read()
            with open(dst, "wb") as f:
                f.write(content)
            print(f"  SYNC  {name}")
            synced += 1

        hash_record[name] = src_hash

    # 保存哈希记录
    save_hash_record(hash_record)

    print()
    print(f"完成: {synced} 个同步, {skipped} 个跳过")

    return 0


def do_check() -> int:
    """检查模式：只比对不修改。不一致时返回 1。"""
    shared = get_shared_templates()
    if not shared:
        print("ERROR: 没有找到共享模板")
        return 1

    print(f"源目录:   {SOURCE_DIR}")
    print(f"目标目录: {TARGET_DIR}")
    print(f"共享模板: {len(shared)} 个")
    print()

    all_ok = True
    mismatches = []

    for name in shared:
        src = SOURCE_DIR / name
        dst = TARGET_DIR / name

        if not dst.exists():
            print(f"  FAIL  {name} (目标文件不存在)")
            mismatches.append(name)
            all_ok = False
            continue

        src_hash = file_sha256(src)
        dst_hash = file_sha256(dst)

        if src_hash == dst_hash:
            print(f"  OK    {name}")
        else:
            print(f"  FAIL  {name} (内容不一致)")
            mismatches.append(name)
            all_ok = False

    print()
    if all_ok:
        print(f"一致: {len(shared)}/{len(shared)} 个共享模板")
        return 0
    else:
        print(f"不一致: {len(mismatches)}/{len(shared)} 个共享模板")
        print()
        print("运行以下命令同步:")
        print(f"  python {Path(__file__).name}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="同步 impact 和 impact-pro 的共享模板（以 impact-pro 为源）"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只比对不修改，不一致时退出码为 1",
    )
    args = parser.parse_args()

    if not SOURCE_DIR.exists():
        print(f"ERROR: 源目录不存在: {SOURCE_DIR}")
        return 1
    if not TARGET_DIR.exists():
        print(f"ERROR: 目标目录不存在: {TARGET_DIR}")
        return 1

    if args.check:
        return do_check()
    else:
        return do_sync()


if __name__ == "__main__":
    sys.exit(main())
