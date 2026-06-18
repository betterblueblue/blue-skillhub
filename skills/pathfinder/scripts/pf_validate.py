#!/usr/bin/env python3
"""pf_validate.py — Gate validator for _project-map.md.

Checks:
  V1: Line-number claims are real (file:line exists)
  V2: No credential leakage (password=, secret=, etc.)
  V3: SVG safety (no script/foreignObject/external links)
  V4: Section [13] has at least 1 non-empty entry
  V5: Mermaid solid-arrow source nodes are mentioned in body text

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
FORBIDDEN_SVG = [
    (re.compile(r"<script\b", re.I), "<script>"),
    (re.compile(r"<foreignObject\b", re.I), "<foreignObject>"),
    (re.compile(r'\bhref\s*=\s*["\']https?://', re.I), "external href"),
    (re.compile(r'\bxlink:href\s*=\s*["\']https?://', re.I), "external xlink:href"),
]


def check_svg_safety(text: str) -> list[str]:
    """V3: If SVG present, check for forbidden elements."""
    errors = []
    if not RE_SVG_BLOCK.search(text):
        return errors
    for i, line in enumerate(text.splitlines(), 1):
        for pattern, label in FORBIDDEN_SVG:
            if pattern.search(line):
                errors.append(f"V3: line {i}: forbidden SVG element ({label})")
    return errors


# --- V4: Uncovered section non-empty ---

RE_SECTION_13 = re.compile(r"【13】|没挖深|未覆盖", re.I)


def check_uncovered(text: str) -> list[str]:
    """V4: Section 13 must have at least 1 non-empty entry."""
    # Find section 13 area
    lines = text.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if RE_SECTION_13.search(line):
            in_section = True
            continue
        # Detect next section header
        if in_section and re.match(r"^##\s", line):
            break
        if in_section:
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
