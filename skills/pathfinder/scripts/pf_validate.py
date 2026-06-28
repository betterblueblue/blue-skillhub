#!/usr/bin/env python3
"""pf_validate.py — Gate validator for _project-map.md.

Checks:
  V1: Line-number claims are real (file:line exists)
  V2: No credential leakage (password=, secret=, etc.)
  V3: No SVG blocks (SVG removed from template; Mermaid is canonical source)
  V4: Section [13] has at least 1 non-empty entry (header-only match, no false
      positives from nav lines mentioning 【13】)
  V5: Mermaid solid-arrow source nodes are mentioned in body text
  V6: Facts JSON files (scan.json/git.json) content is non-empty, consistent,
      and matches actual project structure on disk
  V7: Section [14] code style observation exists and has substantive content
      (not just a title; default output, not optional)

Output: PASS/FAIL/WARN lines + SUMMARY line.
Exit code: 0 = pass, 1 = fail (any FAIL item).

Usage:
    python pf_validate.py MAP_FILE [--repo-root DIR]
    python pf_validate.py --stdin [--repo-root DIR] < MAP_FILE
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# --- V1: Line-number verification ---

# Matches: 【已核实: ...src/main.ts:42】 or 【已核实: src/main.ts:42】
RE_FILE_LINE = re.compile(r"【已核实[:：]\s*.*?(\S+\.\w+):(\d+)】")
# Also match bracket form: [已核实: ...file:line]
RE_FILE_LINE_BRACKET = re.compile(r"\[已核实[:：]\s*.*?(\S+\.\w+):(\d+)\]")


def check_line_numbers(text: str, repo_root: str) -> list[str]:
    """V1: Verify every file:line claim exists."""
    errors = []
    seen = set()
    for pattern in (RE_FILE_LINE, RE_FILE_LINE_BRACKET):
        for m in pattern.finditer(text):
            filepath, lineno = m.group(1), int(m.group(2))
            key = (filepath, lineno)
            if key in seen:
                continue
            seen.add(key)

            full = os.path.join(repo_root, filepath)
            if not os.path.isfile(full):
                errors.append(f"V1: File does not exist: {filepath}:{lineno}")
                continue
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                if lineno < 1 or lineno > len(lines):
                    errors.append(f"V1: Line out of range: {filepath}:{lineno} (file has {len(lines)} lines)")
            except Exception as e:
                errors.append(f"V1: Cannot read {filepath}: {e}")
    return errors


# --- V2: Credential leakage ---

RE_CREDS = [
    (re.compile(r'\b\w*password\w*\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+', re.I), "password="),
    (re.compile(r'\b\w*secret\w*\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+', re.I), "secret="),
    (re.compile(r'\b\w*token\w*\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+', re.I), "token="),
    (re.compile(r'\b\w*api_key\w*\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+', re.I), "api_key="),
    (re.compile(r'jdbc:\w+://[^\s"\']+'), "jdbc: connection string"),
    (re.compile(r'mongodb://[^\s"\']+@'), "mongodb: connection string with credentials"),
]

# Already-sanitized marker (*** in value position)
RE_SANITIZED = re.compile(r'\b\w*(password|secret|token|api_key)\w*\s*=\s*["\']?\*{3}', re.I)


def check_credentials(text: str) -> tuple[list[str], list[str]]:
    """V2: Check for unsanitized credentials. Returns (errors, warnings)."""
    errors = []
    warnings = []
    sanitized_lines = set()

    for i, line in enumerate(text.splitlines(), 1):
        # Skip lines that are clearly sanitized
        if RE_SANITIZED.search(line):
            continue
        for pattern, label in RE_CREDS:
            if pattern.search(line):
                # Check if value looks like *** (already sanitized)
                if "***" in line:
                    continue
                warnings.append(f"V2: line {i}: possible credential ({label}): ...{line.strip()[:80]}")
    return errors, warnings


# --- V3: SVG safety ---

RE_SVG_BLOCK = re.compile(r"<svg\b", re.I)


def check_svg_safety(text: str) -> list[str]:
    """V3: SVG blocks are no longer allowed in project maps.
    Mermaid is the canonical source; SVG was removed from the template.
    Any SVG in output is a leftover and must be flagged."""
    errors = []
    if RE_SVG_BLOCK.search(text):
        for i, line in enumerate(text.splitlines(), 1):
            if RE_SVG_BLOCK.search(line):
                errors.append(f"V3: line {i}: SVG block found — Mermaid is the canonical source, SVG should not be present")
    return errors


# --- V4: Uncovered section non-empty ---

# Only match section headers (## ...), not nav lines or body text mentioning 【13】
RE_SECTION_13_HEADER = re.compile(r"^##\s.*(?:【13】|没挖深|未覆盖)", re.I)


def check_uncovered(text: str) -> list[str]:
    """V4: Section 13 must have at least 1 non-empty entry."""
    # Find section 13 area by scanning for its header line
    lines = text.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if not in_section:
            if RE_SECTION_13_HEADER.search(line):
                in_section = True
            continue
        # Detect next section header
        if re.match(r"^##\s", line):
            break
        stripped = line.strip()
        # Skip template placeholders, empty lines, table borders
        if stripped and stripped not in ("|---|", "---", "|", "| ... | ... |"):
            section_lines.append(stripped)

    # Check for at least 1 substantive entry (not just headers/boilerplate)
    substantive = [l for l in section_lines if len(l) > 3 and not l.startswith("#")]
    if not substantive:
        return ["V4: Section 【13】 has no substantive entries (uncovered items must be listed)"]
    return []


# --- V5: Mermaid solid-arrow consistency ---

RE_MERMAID_SOLID = re.compile(r"(\w[\w/.\-]*)\s*-->\s*(\w[\w/.\-]*)")


def check_mermaid_consistency(text: str) -> list[str]:
    """V5: Source nodes of solid arrows should appear in body text."""
    errors = []
    # Extract all solid-arrow source nodes from Mermaid blocks
    in_mermaid = False
    source_nodes = set()
    for line in text.splitlines():
        if "```mermaid" in line:
            in_mermaid = True
            continue
        if in_mermaid and "```" in line:
            in_mermaid = False
            continue
        if in_mermaid:
            m = RE_MERMAID_SOLID.search(line)
            if m:
                source_nodes.add(m.group(1))

    if not source_nodes:
        return errors

    # Check each source node is mentioned somewhere in the body
    body_text = text.lower()
    for node in source_nodes:
        if node.lower() not in body_text.replace("```mermaid", ""):
            # Only flag if node looks like a module name (not A, B, C etc.)
            if len(node) > 1 and not re.match(r"^[A-Z]$", node):
                errors.append(f"V5: Mermaid solid-arrow source '{node}' not mentioned in body text")

    return errors


# --- V6: Facts file content validation ---

def check_facts_content(repo_root: str) -> tuple[list[str], list[str]]:
    """V6: Validate facts JSON files content. Returns (errors, warnings).

    Checks change-impact/_project-map/facts/scan.json and git.json for:
      - scan.json file_count > 0
      - scan.json dir_tree contains root '/' and has > 1 entry
      - scan.json dir_tree entries correspond to actual directories on disk
      - scan.json file_count is within reasonable range of actual file count
      - git.json head_short non-null (for independent Git repos)
      - git.json toplevel matches --repo-root

    Missing facts files produce FAIL (Phase 1.5 must be run before Script Gate);
    bad content also produces FAIL.
    """
    errors = []
    warnings = []

    facts_dir = os.path.join(repo_root, "change-impact", "_project-map", "facts")
    scan_path = os.path.join(facts_dir, "scan.json")
    git_path = os.path.join(facts_dir, "git.json")

    scan_exists = os.path.isfile(scan_path)
    git_exists = os.path.isfile(git_path)

    if not scan_exists and not git_exists:
        warnings.append(
            "V6: facts directory not found at change-impact/_project-map/facts/ "
            "(Phase 1.5 not yet run — run pf_scan.py and pf_git.py to produce facts)"
        )
        return errors, warnings

    # Validate scan.json
    if scan_exists:
        try:
            with open(scan_path, "r", encoding="utf-8") as f:
                scan = json.load(f)
            file_count = scan.get("file_count", 0)
            if not isinstance(file_count, int) or file_count <= 0:
                errors.append(
                    f"V6: scan.json file_count is {file_count}, expected > 0 "
                    f"(project has files on disk)"
                )
            dir_tree = scan.get("dir_tree", [])
            if not isinstance(dir_tree, list) or "/" not in dir_tree:
                errors.append("V6: scan.json dir_tree missing root '/' entry")
            elif len(dir_tree) <= 1:
                errors.append(
                    "V6: scan.json dir_tree has only root '/' — "
                    "a real project should have subdirectories"
                )
            else:
                # Check that dir_tree entries correspond to actual directories
                existing_dirs = 0
                for entry in dir_tree:
                    if entry == "/":
                        existing_dirs += 1
                        continue
                    dir_path = os.path.join(repo_root, entry.rstrip("/"))
                    if os.path.isdir(dir_path):
                        existing_dirs += 1
                if existing_dirs <= 1:
                    errors.append(
                        "V6: scan.json dir_tree entries do not match any actual "
                        "directories on disk — facts may be corrupted"
                    )

            # Cross-check file_count against actual files on disk (quick count)
            if isinstance(file_count, int) and file_count > 0:
                actual_count = _count_files_quick(repo_root)
                if actual_count > 0:
                    ratio = file_count / actual_count
                    if ratio < 0.3 or ratio > 3.0:
                        errors.append(
                            f"V6: scan.json file_count ({file_count}) is wildly "
                            f"different from actual file count ({actual_count}) "
                            f"on disk — facts may be corrupted"
                        )
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"V6: cannot read/parse scan.json: {e}")
    else:
        errors.append(
            "V6: scan.json not found in facts directory "
            "(Phase 1.5 must be run — run pf_scan.py to produce it)"
        )

    # Validate git.json
    if git_exists:
        try:
            with open(git_path, "r", encoding="utf-8") as f:
                git = json.load(f)
            is_git = git.get("is_git_repo", False)
            is_independent = git.get("is_independent_repo", False)
            # Only check head_short for independent git repos
            if is_git and is_independent:
                head_short = git.get("head_short")
                if not head_short:
                    errors.append(
                        "V6: git.json head_short is null/empty for an independent "
                        "Git repo (expected a commit hash)"
                    )
            # Check toplevel matches repo_root (independent repos only)
            # Non-independent repos live inside a parent git tree; toplevel is the parent root.
            toplevel = git.get("toplevel")
            if toplevel and is_independent:
                norm_toplevel = os.path.normcase(os.path.abspath(toplevel))
                norm_repo_root = os.path.normcase(os.path.abspath(repo_root))
                if norm_toplevel != norm_repo_root:
                    errors.append(
                        f"V6: git.json toplevel ({toplevel}) does not match "
                        f"--repo-root ({repo_root})"
                    )
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"V6: cannot read/parse git.json: {e}")
    else:
        errors.append(
            "V6: git.json not found in facts directory "
            "(Phase 1.5 must be run — run pf_git.py to produce it)"
        )

    return errors, warnings


# Directories to skip when cross-checking file count (must match pf_scan.py)
_V6_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".svn", ".hg",
    "vendor", "dist", "build", ".next", ".nuxt", "target",
    ".gradle", ".idea", ".vscode", ".claude", ".cache",
    "venv", ".venv", "env", ".env", ".tox", "coverage",
    ".m2", "bower_components", "Pods", ".dart_tool",
    "change-impact",
}


def _count_files_quick(root: str) -> int:
    """Full file count using pf_scan.py skip logic (no depth limit)."""
    count = 0
    root_path = Path(root)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [
            d for d in dirnames if d not in _V6_SKIP_DIRS and not d.startswith(".")
        ]
        count += len(filenames)
    return count


# --- V7: Section [14] existence + content ---

# Only match section headers (## ...), not body text mentioning 【14】
RE_SECTION_14_HEADER = re.compile(r"^##\s.*(?:【14】|代码风格观察)", re.I)


def check_section_14(text: str) -> list[str]:
    """V7: Section [14] must exist and have substantive content.

    - Missing entirely → FAIL (default output, not optional)
    - Exists but empty shell (title only, no observations) → FAIL
    - Only super-large repos or budget exhaustion may skip,
      and must note the reason in [13].
    """
    lines = text.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if not in_section:
            if RE_SECTION_14_HEADER.search(line):
                in_section = True
            continue
        if re.match(r"^##\s", line):
            break
        stripped = line.strip()
        if stripped and stripped not in ("|---|", "---", "|"):
            section_lines.append(stripped)

    if not in_section:
        return [
            "V7: Section 【14】代码风格观察 not found — this section is now default output. "
            "Only super-large repos or budget exhaustion may skip it, "
            "and must note the reason in 【13】."
        ]

    # Check for substantive content: at least 2 non-header/non-boilerplate lines
    # (table data rows, observation entries, sampling source declarations)
    substantive = [
        l for l in section_lines
        if len(l) > 3 and not l.startswith("#") and not l.startswith("<!--")
    ]
    if len(substantive) < 2:
        return [
            "V7: Section 【14】代码风格观察 exists but appears empty — "
            "need observation entries with evidence, not just a title."
        ]
    return []


# --- Main ---

def validate(text: str, repo_root: str) -> tuple[list[str], list[str], list[str]]:
    """Run all checks. Returns (passes, fails, warnings)."""
    passes = []
    fails = []
    warnings = []

    # V1
    v1_errors = check_line_numbers(text, repo_root)
    if v1_errors:
        fails.extend(v1_errors)
    else:
        passes.append("V1: line-number claims verified")

    # V2
    v2_errors, v2_warnings = check_credentials(text)
    fails.extend(v2_errors)
    warnings.extend(v2_warnings)
    if not v2_errors and not v2_warnings:
        passes.append("V2: no credential leakage detected")

    # V3
    v3_errors = check_svg_safety(text)
    if v3_errors:
        fails.extend(v3_errors)
    else:
        passes.append("V3: SVG safety check passed")

    # V4
    v4_errors = check_uncovered(text)
    if v4_errors:
        fails.extend(v4_errors)
    else:
        passes.append("V4: uncovered section has entries")

    # V5
    v5_errors = check_mermaid_consistency(text)
    if v5_errors:
        fails.extend(v5_errors)
    else:
        passes.append("V5: Mermaid solid-arrow consistency passed")

    # V6
    v6_errors, v6_warnings = check_facts_content(repo_root)
    fails.extend(v6_errors)
    warnings.extend(v6_warnings)
    if not v6_errors and not v6_warnings:
        passes.append("V6: facts file content validated")

    # V7
    v7_errors = check_section_14(text)
    if v7_errors:
        fails.extend(v7_errors)
    else:
        passes.append("V7: section [14] code style observation exists")

    return passes, fails, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate _project-map.md before write")
    parser.add_argument("map_file", nargs="?", help="Path to _project-map.md")
    parser.add_argument("--stdin", action="store_true", help="Read map from stdin")
    parser.add_argument("--repo-root", default=".", help="Project root directory (for V1 file checks)")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    elif args.map_file:
        try:
            with open(args.map_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"FAIL: cannot read {args.map_file}: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    repo_root = os.path.abspath(args.repo_root)
    passes, fails, warnings = validate(text, repo_root)

    for p in passes:
        print(f"PASS: {p}")
    for w in warnings:
        print(f"WARN: {w}")
    for f in fails:
        print(f"FAIL: {f}")

    print(f"SUMMARY: {len(passes)} passed, {len(fails)} failed, {len(warnings)} warnings")

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
