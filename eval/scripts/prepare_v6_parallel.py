#!/usr/bin/env python3
"""V6 并行测试环境准备脚本 — 为 6 个 cell 创建独立测试项目副本。

与 V5 脚本相同结构，但：
- 输出到 blind-2026-06-25-v6/ 目录
- 源项目从 V5 的 cell-C5 复制（确保是干净的副本，无 V5 产出）
- 额外排除 .claude/worktrees 目录（V5 副本中包含大量重复 worktree）
"""
import shutil
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V6_ROOT = os.path.join(REPO, "eval", "runs", "blind-2026-06-25-v6")

# V6 使用 V5 cell-C5 的测试项目作为源（干净副本，无 V5 产出残留）
SOURCE_ROOT = os.path.join(REPO, "eval", "runs", "blind-2026-06-25-v5", "cell-C5", "test-projects")

CELLS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PROJECTS = ["prisma-express-ts", "ruoyi-vue"]
EXCLUDE_DIRS = {
    "change-impact",
    "node_modules",
    ".git",
    "target",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".claude",  # V5 副本中包含 .claude/worktrees，排除掉
}
EXCLUDE_EXTS = {".pyc", ".class"}


def ignore_fn(directory, contents):
    ignored = []
    for item in contents:
        full = os.path.join(directory, item)
        if os.path.isdir(full) and item in EXCLUDE_DIRS:
            ignored.append(item)
        elif os.path.isfile(full) and os.path.splitext(item)[1] in EXCLUDE_EXTS:
            ignored.append(item)
    return ignored


def main():
    # 检查源目录
    if not os.path.isdir(SOURCE_ROOT):
        print(f"ERROR: V5 source not found: {SOURCE_ROOT}")
        print("请先完成 V5 测试（至少 cell-C5 的环境需存在）")
        sys.exit(1)

    # 清理旧目录
    if os.path.exists(V6_ROOT):
        print("Cleaning old V6 root...")
        shutil.rmtree(V6_ROOT)
    os.makedirs(os.path.join(V6_ROOT, "scorecards"))

    for cell in CELLS:
        cell_dir = os.path.join(V6_ROOT, f"cell-{cell}", "test-projects")
        os.makedirs(cell_dir, exist_ok=True)
        print(f"--- cell-{cell} ---")
        for proj in PROJECTS:
            src = os.path.join(SOURCE_ROOT, proj)
            dst = os.path.join(cell_dir, proj)
            if not os.path.isdir(src):
                print(f"  ERROR: source not found: {src}")
                sys.exit(1)
            shutil.copytree(src, dst, ignore=ignore_fn)
            # 额外安全：删除残留的 change-impact
            ci = os.path.join(dst, "change-impact")
            if os.path.exists(ci):
                shutil.rmtree(ci)
            file_count = sum(len(files) for _, _, files in os.walk(dst))
            print(f"  {proj}: {file_count} files")

    print()
    print("Done. 6 cells created at:")
    print(V6_ROOT)


if __name__ == "__main__":
    main()
