#!/usr/bin/env python3
"""pf_scan.py — Project sizing & structure scanner.

Outputs a facts JSON to stdout with:
  - file_count, file_ext_counts (top 10)
  - dir_tree (top 3 levels, max 80 dirs)
  - manifest_files (package.json, pom.xml, etc.)
  - budget_tier (tiny/small/medium/large)

Usage:
    python pf_scan.py [PROJECT_ROOT]

If PROJECT_ROOT is omitted, uses current working directory.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

# --- Config ---
MAX_DIR_DEPTH = 3
MAX_DIRS = 80
TOP_EXT = 10

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".svn", ".hg",
    "vendor", "dist", "build", ".next", ".nuxt", "target",
    ".gradle", ".idea", ".vscode", ".claude", ".cache",
    "venv", ".venv", "env", ".env", ".tox", "coverage",
    ".m2", "bower_components", "Pods", ".dart_tool",
}

MANIFEST_NAMES = {
    "package.json", "pom.xml", "build.gradle", "build.gradle.kts",
    "Cargo.toml", "go.mod", "requirements.txt", "Pipfile",
    "pyproject.toml", "Gemfile", "composer.json", "mix.exs",
    "pubspec.yaml", "*.csproj", "*.sln",
}


def _should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".")


def scan_files(root: Path) -> tuple[Counter, int]:
    """Walk project, return (ext_counter, total_file_count)."""
    ext_counter: Counter = Counter()
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped dirs in-place
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]
        for f in filenames:
            total += 1
            ext = Path(f).suffix.lower()
            if ext:
                ext_counter[ext] += 1
            else:
                ext_counter["<no-ext>"] += 1
    return ext_counter, total


def scan_dir_tree(root: Path) -> list[str]:
    """Return top-N-level directory tree as list of path strings."""
    lines = []
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        depth = len(Path(dirpath).relative_to(root).parts)
        if depth >= MAX_DIR_DEPTH:
            dirnames.clear()
            continue
        dirnames[:] = sorted(d for d in dirnames if not _should_skip_dir(d))
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        if rel == ".":
            lines.append("/")
        else:
            lines.append(f"{rel}/")
        count += 1
        if count >= MAX_DIRS:
            break
    return lines


def find_manifests(root: Path) -> list[str]:
    """Find project manifest files in root (depth 0-1)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = len(Path(dirpath).relative_to(root).parts)
        if depth > 1:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]
        for f in filenames:
            fname = f.lower()
            if fname in MANIFEST_NAMES:
                found.append(os.path.relpath(os.path.join(dirpath, f), root).replace("\\", "/"))
            elif fname.endswith(".csproj") or fname.endswith(".sln"):
                found.append(os.path.relpath(os.path.join(dirpath, f), root).replace("\\", "/"))
    return sorted(set(found))


def classify_budget(file_count: int) -> str:
    """Classify project size for context budget allocation."""
    if file_count < 30:
        return "tiny"
    elif file_count < 150:
        return "small"
    elif file_count < 600:
        return "medium"
    else:
        return "large"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Project sizing & structure scanner")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root directory")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    root = Path(args.project_root)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    ext_counter, file_count = scan_files(root)
    dir_tree = scan_dir_tree(root)
    manifests = find_manifests(root)
    budget_tier = classify_budget(file_count)

    result = {
        "file_count": file_count,
        "file_ext_counts": dict(ext_counter.most_common(TOP_EXT)),
        "dir_tree": dir_tree,
        "manifest_files": manifests,
        "budget_tier": budget_tier,
    }

    output_str = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_str, encoding="utf-8")
    else:
        sys.stdout.write(output_str)


if __name__ == "__main__":
    main()
