#!/usr/bin/env python3
"""pf_git.py — Git metadata extractor.

Outputs a facts JSON to stdout with:
  - is_git_repo, is_independent_repo
  - head_short, head_full, branch
  - toplevel
  - hotspots (top 10 recently-changed files)
  - recent_commit_modules (unique top-level dirs from hotspots)

Usage:
    python pf_git.py [PROJECT_ROOT]

If PROJECT_ROOT is omitted, uses current working directory.
Non-Git directories produce is_git_repo=false with null fields.
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HOTSPOT_LIMIT = 10
HOTSPOT_DAYS = 30


def _run_git(args: list[str], cwd: str) -> tuple[int, str]:
    """Run a git command, return (exit_code, stdout)."""
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.returncode, r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 1, ""


def check_git_repo(root: Path) -> tuple[bool, bool, str]:
    """Return (is_git, is_independent, toplevel)."""
    code, toplevel = _run_git(["rev-parse", "--show-toplevel"], str(root))
    if code != 0:
        return False, False, ""

    # Check if .git exists directly under root (independent repo)
    git_dir = root / ".git"
    is_independent = git_dir.exists()
    return True, is_independent, toplevel


def get_head(cwd: str) -> tuple[str, str]:
    """Return (short_hash, full_hash). Empty strings on failure."""
    code_short, short = _run_git(["rev-parse", "--short", "HEAD"], cwd)
    code_full, full = _run_git(["rev-parse", "HEAD"], cwd)
    return (short if code_short == 0 else ""), (full if code_full == 0 else "")


def get_branch(cwd: str) -> str:
    """Return current branch name, empty on failure."""
    code, name = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    return name if code == 0 else ""


def get_hotspots(cwd: str) -> list[dict]:
    """Return top N recently-changed files (30-day window)."""
    code, output = _run_git(
        ["log", f"--since={HOTSPOT_DAYS} days ago", "--name-only", "--pretty=format:"],
        cwd,
    )
    if code != 0 or not output:
        return []

    counter: Counter = Counter()
    for line in output.splitlines():
        line = line.strip()
        if line:
            counter[line] += 1

    return [
        {"path": path, "commits": count}
        for path, count in counter.most_common(HOTSPOT_LIMIT)
    ]


def extract_modules(hotspots: list[dict]) -> list[str]:
    """Extract unique top-level directories from hotspot paths."""
    seen = set()
    result = []
    for item in hotspots:
        parts = item["path"].replace("\\", "/").split("/")
        if len(parts) > 1 and parts[0] not in seen:
            seen.add(parts[0])
            result.append(parts[0])
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Git metadata extractor")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root directory")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    root = Path(args.project_root)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    is_git, is_independent, toplevel = check_git_repo(root)

    if not is_git:
        result = {
            "is_git_repo": False,
            "is_independent_repo": False,
            "toplevel": None,
            "head_short": None,
            "head_full": None,
            "branch": None,
            "hotspots": [],
            "recent_commit_modules": [],
        }
        _write_output(result, args.output)
        return

    cwd = str(root)
    head_short, head_full = get_head(cwd)

    # Non-independent repo: don't leak parent repo HEAD
    if not is_independent:
        head_short = None
        head_full = None

    branch = get_branch(cwd)
    hotspots = get_hotspots(cwd)
    modules = extract_modules(hotspots)

    result = {
        "is_git_repo": True,
        "is_independent_repo": is_independent,
        "toplevel": toplevel.replace("\\", "/") if toplevel else None,
        "head_short": head_short,
        "head_full": head_full,
        "branch": branch,
        "hotspots": hotspots,
        "recent_commit_modules": modules,
    }

    _write_output(result, args.output)


def _write_output(result: dict, output_path: str | None):
    """Write JSON to file or stdout."""
    output_str = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output_str, encoding="utf-8")
    else:
        sys.stdout.write(output_str)


if __name__ == "__main__":
    main()
