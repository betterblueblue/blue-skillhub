#!/usr/bin/env python3
"""V5 并行测试环境准备脚本 — 为 6 个 cell 创建独立测试项目副本。"""
import shutil
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V5_ROOT = os.path.join(REPO, "eval", "runs", "blind-2026-06-25-v5")

CELLS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PROJECTS = ["prisma-express-ts", "ruoyi-vue"]
EXCLUDE_DIRS = {"change-impact", "node_modules", ".git", "target", "__pycache__", ".next", "dist", "build"}
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
    # Clean old
    if os.path.exists(V5_ROOT):
        print("Cleaning old V5 root...")
        shutil.rmtree(V5_ROOT)
    os.makedirs(os.path.join(V5_ROOT, "scorecards"))

    for cell in CELLS:
        cell_dir = os.path.join(V5_ROOT, f"cell-{cell}", "test-projects")
        os.makedirs(cell_dir, exist_ok=True)
        print(f"--- cell-{cell} ---")
        for proj in PROJECTS:
            src = os.path.join(REPO, "test-projects", proj)
            dst = os.path.join(cell_dir, proj)
            if not os.path.isdir(src):
                print(f"  ERROR: source not found: {src}")
                sys.exit(1)
            shutil.copytree(src, dst, ignore=ignore_fn)
            # Extra safety: remove any residual change-impact
            ci = os.path.join(dst, "change-impact")
            if os.path.exists(ci):
                shutil.rmtree(ci)
            file_count = sum(len(files) for _, _, files in os.walk(dst))
            print(f"  {proj}: {file_count} files")

    print()
    print("Done. 6 cells created at:")
    print(V5_ROOT)


if __name__ == "__main__":
    main()
