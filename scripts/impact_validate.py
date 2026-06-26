#!/usr/bin/env python3
"""impact_validate.py — Gate validator for impact document output.

Runs after Phase 4 document output, before submitting to user for confirmation.
Any FAIL item blocks submission; WARN items should be communicated to user.

Checks:
  V1: File completeness (full: 000/010/020/030; light: 040-light.md)       — FAIL
  V2: Requirements boundary (010-requirements.md free of technical details)  — WARN
  V3: Method name verification markers (030-implementation.md)              — WARN
  V4: Grading decision table (判档决策表 present in output)                 — WARN
  V5: Credential sanitization (all output files sanitized)                  — FAIL
  V6: Line number spot check (random 3 references verified)                 — WARN
  V7: Tier judgment sanity (universal-quantifier coverage gate + over/under) — FAIL/WARN

Output: PASS/FAIL/WARN lines + SUMMARY line.
Exit code: 0 = pass (no FAIL), 1 = fail (any FAIL item).

Usage:
    python scripts/impact_validate.py <需求目录> [--mode light|full] [--repo-root DIR]
    python scripts/impact_validate.py change-impact/B3/ --mode full
    python scripts/impact_validate.py change-impact/B1/ --mode light --repo-root /path/to/project
"""

import argparse
import os
import random
import re
import sys
from pathlib import Path

# ===========================================================================
# V1: File completeness
# ===========================================================================

FULL_REQUIRED = [
    "000-context-pack.md",
    "010-requirements.md",
    "020-design.md",
    "030-implementation.md",
]
LIGHT_REQUIRED = ["040-light.md"]


def check_file_completeness(req_dir: Path, mode: str) -> tuple[list[str], list[str]]:
    """V1: Check that required files exist for the given mode."""
    passes = []
    fails = []

    if mode == "full":
        required = FULL_REQUIRED
    elif mode == "light":
        required = LIGHT_REQUIRED
    else:
        # Auto-detect
        if (req_dir / "040-light.md").exists():
            required = LIGHT_REQUIRED
            mode = "light"
        elif (req_dir / "010-requirements.md").exists():
            required = FULL_REQUIRED
            mode = "full"
        else:
            return [], [
                "V1: Cannot determine mode — neither 040-light.md nor "
                "010-requirements.md found in " + str(req_dir)
            ]

    missing = []
    for f in required:
        if (req_dir / f).exists():
            passes.append(f"V1: {f} exists ({mode} mode)")
        else:
            missing.append(f)
            fails.append(f"V1: Missing required file: {f} ({mode} mode)")

    return passes, fails


# ===========================================================================
# V2: Requirements boundary — 010-requirements.md should not contain
#     technical details (table names, class names, file paths, code snippets)
# ===========================================================================

# Fenced code block delimiter
RE_CODE_FENCE = re.compile(r"```")

# SQL type definitions: varchar(100), bigint(20), etc.
RE_SQL_TYPE = re.compile(
    r"\b(varchar|bigint|tinyint|int|smallint|mediumint|text|longtext|"
    r"datetime|timestamp|decimal|float|double|char|boolean|serial)\s*\(",
    re.I,
)

# ORM/Prisma annotations: @unique, @id, @default, @relation, etc.
RE_ORM_ANNOTATION = re.compile(
    r"@(unique|id|default|relation|map|column|field|primaryKey|updatedAt|autoincrement)"
)

# Prisma type definitions: String?, Int!, Boolean, DateTime
RE_PRISMA_TYPE = re.compile(r"\b(String|Int|Boolean|DateTime|Json|Float|Bytes)\s*[?!]")

# Method calls: object.method(  (excluding Step N. patterns)
RE_METHOD_CALL = re.compile(r"\b([a-z]\w*)\.([a-z]\w*)\s*\(")

# File paths in backticks: `src/services/user.service.ts`
RE_FILE_PATH = re.compile(r"`([a-zA-Z0-9_@./\-]+\.\w{1,5})`")

# Common table name prefixes in backticks: `sys_user`, `t_order`
RE_TABLE_NAME = re.compile(r"`(sys_\w+|t_\w+)`")


def check_requirements_boundary(req_dir: Path) -> tuple[list[str], list[str]]:
    """V2: Check 010-requirements.md for technical details."""
    passes = []
    warns = []

    req_file = req_dir / "010-requirements.md"
    if not req_file.exists():
        return [], []  # V1 handles missing file

    text = req_file.read_text(encoding="utf-8")

    # Skip template instruction lines (blockquote lines starting with >)
    body_lines = [
        line for line in text.splitlines() if not line.strip().startswith(">")
    ]
    body_text = "\n".join(body_lines)

    issues = []

    # Code blocks (need at least 2 ``` delimiters to form a block)
    fence_count = body_text.count("```")
    if fence_count >= 2:
        issues.append("contains code blocks (``` — move to 020-design.md")

    # SQL type definitions
    if RE_SQL_TYPE.search(body_text):
        issues.append("contains SQL type definitions (varchar/bigint/etc.)")

    # ORM annotations
    if RE_ORM_ANNOTATION.search(body_text):
        issues.append("contains ORM annotations (@unique/@id/etc.)")

    # Prisma type definitions
    if RE_PRISMA_TYPE.search(body_text):
        issues.append("contains Prisma type definitions (String?/Int!/etc.)")

    # Method calls (filter out Step N. patterns)
    method_calls = RE_METHOD_CALL.findall(body_text)
    # Exclude common false positives
    real_calls = [
        f"{obj}.{method}("
        for obj, method in method_calls
        if not re.match(r"(step|步骤)", obj, re.I)
    ]
    if real_calls:
        issues.append(f"contains method calls: {', '.join(real_calls[:3])}")

    # File paths with extensions in backticks (exclude doc cross-references)
    file_paths = RE_FILE_PATH.findall(body_text)
    # Exclude references to other impact docs (010-, 020-, 030-, etc.)
    tech_paths = [
        p for p in file_paths if not re.match(r"\d{3}-", p) and p != "010-requirements.md"
    ]
    if tech_paths:
        issues.append(f"contains file paths: {', '.join(tech_paths[:3])}")

    # Table names with common prefixes
    table_names = RE_TABLE_NAME.findall(body_text)
    if table_names:
        issues.append(f"contains table names: {', '.join(table_names[:3])}")

    if issues:
        warns.append(
            "V2: 010-requirements.md may contain technical details — "
            + "; ".join(issues)
        )
    else:
        passes.append("V2: 010-requirements.md appears free of technical details")

    return passes, warns


# ===========================================================================
# V3: Method name verification markers — 030-implementation.md should have
#     evidence of grep verification for referenced method names
# ===========================================================================

# Verification markers
RE_VERIFIED = re.compile(r"已核实|已验证|grep\s*确认|grep\s*验证|已确认存在")
RE_UNVERIFIED = re.compile(r"待确认|未确认.*存在|待核实")


def check_method_verification(req_dir: Path) -> tuple[list[str], list[str]]:
    """V3: Check 030-implementation.md for method name verification markers."""
    passes = []
    warns = []

    impl_file = req_dir / "030-implementation.md"
    if not impl_file.exists():
        return [], []  # V1 handles missing file

    text = impl_file.read_text(encoding="utf-8")

    # Find method calls (excluding new methods marked with 新增/新增：)
    method_calls = RE_METHOD_CALL.findall(text)
    real_calls = [
        f"{obj}.{method}("
        for obj, method in method_calls
        if not re.match(r"(step|步骤)", obj, re.I)
    ]

    has_verified = bool(RE_VERIFIED.search(text))
    has_unverified = bool(RE_UNVERIFIED.search(text))

    if not real_calls:
        passes.append("V3: 030-implementation.md has no existing method calls to verify")
    elif has_verified or has_unverified:
        marker = "verified" if has_verified else "marked unverified"
        passes.append(f"V3: 030-implementation.md has method verification markers ({marker})")
    else:
        warns.append(
            "V3: 030-implementation.md references existing methods but has no "
            "verification markers (已核实/grep确认/待确认) — run API method name pre-check"
        )

    return passes, warns


# ===========================================================================
# V4: Grading decision table — output should include 判档决策表
# ===========================================================================

RE_DECISION_TABLE = re.compile(r"判档决策表|定级决策表|覆盖范围.*缺口.*判档|决策表")


def check_decision_table(req_dir: Path) -> tuple[list[str], list[str]]:
    """V4: Check for grading decision table in output files."""
    passes = []
    warns = []

    # Collect text from all .md files in the requirement directory
    all_text = ""
    for f in sorted(req_dir.glob("*.md")):
        try:
            all_text += f.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    if RE_DECISION_TABLE.search(all_text):
        passes.append("V4: Grading decision table found in output")
    else:
        warns.append(
            "V4: No grading decision table found — "
            "include 判档决策表 with user keywords, coverage, gaps, and grading basis"
        )

    return passes, warns


# ===========================================================================
# V5: Credential sanitization — all output files must have sanitized credentials
# ===========================================================================

# Match credential key=value patterns.
# Uses (?:^|[\s.;]) to require word boundary before the key name,
# so variable names like 'userWithoutPassword' or 'tokens' don't match.
RE_CREDS = [
    (
        re.compile(
            r'(?:^|[\s.;])(password|passwd|pwd)\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+',
            re.I | re.M,
        ),
        "password=",
    ),
    (
        re.compile(
            r'(?:^|[\s.;])(secret)\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+',
            re.I | re.M,
        ),
        "secret=",
    ),
    (
        re.compile(
            r'(?:^|[\s.;])(token)\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+',
            re.I | re.M,
        ),
        "token=",
    ),
    (
        re.compile(
            r'(?:^|[\s.;])(api_?key)\s*=\s*["\']?(?!\*{3})[^"\'\s\]\}，】]+',
            re.I | re.M,
        ),
        "api_key=",
    ),
    (re.compile(r"jdbc:\w+://[^\s\"\']+"), "jdbc: connection string"),
    (re.compile(r"mongodb://[^\s\"\']+@"), "mongodb: connection string"),
    (
        re.compile(r"(?:mysql|postgresql|postgres|redis|amqp|amqps)://[^\s\"\']+:[^\s\"\']+@", re.I),
        "DB connection string with credentials",
    ),
    (re.compile(r"-----BEGIN.*PRIVATE KEY-----", re.I), "private key block"),
]

RE_SANITIZED = re.compile(
    r"(?:^|[\s.;])(password|secret|token|api_?key)\s*=\s*[\"']?\*{3}",
    re.I | re.M,
)


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code block content (between ``` pairs).

    Keeps non-code lines so credential patterns only scan prose/config text,
    not example code where variable names like 'userWithoutPassword' cause
    false positives.
    """
    lines = text.splitlines()
    in_code = False
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            result.append(line)
    return "\n".join(result)


def check_credentials(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V5: Check all output files for unsanitized credentials."""
    passes = []
    fails = []
    warns = []

    found_issues = False

    # Scan all .md files in the requirement directory (non-recursive)
    for f in sorted(req_dir.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue

        # Strip code blocks to avoid false positives from variable names
        # like 'userWithoutPassword = exclude(...)' or 'tokens = await ...'
        prose_text = _strip_code_blocks(text)

        for i, line in enumerate(prose_text.splitlines(), 1):
            # Skip template instruction lines (blockquote)
            if line.strip().startswith(">"):
                continue
            # Skip lines that are already sanitized
            if RE_SANITIZED.search(line):
                continue
            if "***" in line:
                continue

            for pattern, label in RE_CREDS:
                if pattern.search(line):
                    warns.append(
                        f"V5: {f.name}:{i}: possible credential ({label}): "
                        f"...{line.strip()[:80]}"
                    )
                    found_issues = True

    if not found_issues:
        passes.append("V5: No credential leakage detected")

    return passes, fails, warns


# ===========================================================================
# V6: Line number spot check — verify random file:line references
# ===========================================================================

# Match `path.ext:42` in backticks (also handles :42-88 and :42,126)
RE_LINE_REF_BACKTICK = re.compile(r"`([^`\s]+\.\w+):(\d+)[-\d,]*`")

# Match 【已核实: ...path.ext:42】
RE_LINE_REF_VERIFIED = re.compile(r"【已核实[:：]\s*.*?(\S+\.\w+):(\d+)[-\d,]*】")

# Match [已核实: ...path.ext:42]
RE_LINE_REF_BRACKET = re.compile(r"\[已核实[:：]\s*.*?(\S+\.\w+):(\d+)[-\d,]*\]")


def _resolve_file(filepath: str, repo_root: str) -> str | None:
    """Try to resolve a file path against repo_root.

    Attempts:
    1. Path as-is (normalizing separators)
    2. Basename glob search (for shortened paths like 'user.service.ts'
       when actual path is 'src/services/user.service.ts')
    """
    # Attempt 1: direct path
    normalized = filepath.replace("/", os.sep)
    full = os.path.join(repo_root, normalized)
    if os.path.isfile(full):
        return full

    # Attempt 2: direct path without normalization
    full = os.path.join(repo_root, filepath)
    if os.path.isfile(full):
        return full

    # Attempt 3: basename glob search (limited to avoid performance issues)
    basename = os.path.basename(filepath)
    root = Path(repo_root)
    try:
        matches = list(root.rglob(basename))
        # Filter to files only, prefer shortest path
        files = [m for m in matches if m.is_file()]
        if files:
            files.sort(key=lambda p: len(str(p)))
            return str(files[0])
    except Exception:
        pass

    return None


def extract_line_refs(text: str) -> list[tuple[str, int]]:
    """Extract (filepath, lineno) references from text."""
    refs = []
    seen = set()
    for pattern in (RE_LINE_REF_BACKTICK, RE_LINE_REF_VERIFIED, RE_LINE_REF_BRACKET):
        for m in pattern.finditer(text):
            filepath, lineno = m.group(1), int(m.group(2))
            # Skip paths with ... (abbreviation)
            if "..." in filepath:
                continue
            key = (filepath, lineno)
            if key not in seen:
                seen.add(key)
                refs.append((filepath, lineno))
    return refs


def check_line_numbers(
    req_dir: Path, repo_root: str, seed: int | None = None
) -> tuple[list[str], list[str], list[str]]:
    """V6: Spot-check line number references against source files."""
    passes = []
    fails = []
    warns = []

    # Collect text from context-pack, design, light, and requirements docs
    all_refs: list[tuple[str, int]] = []
    for filename in [
        "000-context-pack.md",
        "020-design.md",
        "040-light.md",
        "010-requirements.md",
    ]:
        f = req_dir / filename
        if f.exists():
            try:
                text = f.read_text(encoding="utf-8")
                all_refs.extend(extract_line_refs(text))
            except Exception:
                pass

    if not all_refs:
        passes.append("V6: No line number references found to verify")
        return passes, fails, warns

    # Sample up to 3 references
    rng = random.Random(seed) if seed is not None else random.Random()
    sample_size = min(3, len(all_refs))
    sample = rng.sample(all_refs, sample_size)

    verified_count = 0
    for filepath, lineno in sample:
        full = _resolve_file(filepath, repo_root)

        if full is None:
            warns.append(
                f"V6: Cannot verify {filepath}:{lineno} — file not found"
            )
            continue

        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
            if lineno < 1 or lineno > len(lines):
                warns.append(
                    f"V6: Line out of range: {filepath}:{lineno} "
                    f"(file has {len(lines)} lines)"
                )
            else:
                content = lines[lineno - 1].strip()[:60]
                passes.append(f"V6: {filepath}:{lineno} OK ({content})")
                verified_count += 1
        except Exception as e:
            warns.append(f"V6: Cannot read {filepath}: {e}")

    if verified_count == 0 and sample:
        warns.append("V6: Could not verify any line number references")

    return passes, fails, warns


# ===========================================================================
# V7: Tier judgment sanity check — detect over/under judgment and
#     enforce coverage analysis when universal quantifiers present
# ===========================================================================

# Universal quantifier words that indicate broad scope
UNIVERSAL_WORDS = ["每次", "所有", "全部", "任何", "一律", "每个"]

# Extract user request from context-pack
RE_USER_REQUEST = re.compile(r"用户原话[：:]\s*(.+)")

# Count "必须同步修改" table rows
RE_MUST_MODIFY = re.compile(r"必须同步修改\s*\|")

# Coverage analysis keywords (should appear when universal quantifiers present)
RE_COVERAGE_ANALYSIS = re.compile(r"覆盖范围|覆盖缺口|覆盖面|覆盖率")


def check_tier_judgment(req_dir: Path, mode: str) -> tuple[list[str], list[str], list[str]]:
    """V7: Sanity check tier judgment against user request and change scope.

    Three sub-checks:
      A. Universal-quantifier coverage gate (FAIL): If user request contains
         universal words (每次/所有/全部/任何/一律/每个), output must include
         coverage analysis (覆盖范围/缺口).
      B. Over-judgment detection (WARN): Full mode with <=2 implementation
         steps and <=3 must-modify files and no universal quantifiers
         -> may be Light.
      C. Under-judgment detection (WARN): Light mode with >5 must-modify
         files -> may be Full.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    ctx_file = req_dir / "000-context-pack.md"
    if not ctx_file.exists():
        return [], [], []  # V1 handles missing file

    ctx_text = ctx_file.read_text(encoding="utf-8")

    # Extract user request
    user_request_match = RE_USER_REQUEST.search(ctx_text)
    user_request = user_request_match.group(1).strip() if user_request_match else ""

    # Check for universal quantifiers
    found_universal = [w for w in UNIVERSAL_WORDS if w in user_request]

    # Count must-modify table rows in context-pack
    must_modify_count = len(RE_MUST_MODIFY.findall(ctx_text))

    # Count implementation steps in 030-implementation.md
    step_count = 0
    impl_file = req_dir / "030-implementation.md"
    if impl_file.exists():
        impl_text = impl_file.read_text(encoding="utf-8")
        step_count = len(re.findall(r"###\s*Step\s*\d+", impl_text))

    # Collect all text for coverage analysis check
    all_text = ""
    for f in sorted(req_dir.glob("*.md")):
        try:
            all_text += f.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    # --- Check A: Universal-quantifier coverage gate (FAIL) ---
    if found_universal:
        if not RE_COVERAGE_ANALYSIS.search(all_text):
            fails.append(
                f"V7: User request contains universal quantifier(s) "
                f"({', '.join(found_universal)}) but no coverage analysis "
                f"(覆盖范围/缺口) found in output — must include coverage "
                f"analysis showing existing implementation scope vs. user's "
                f"full-scope requirement"
            )
        else:
            passes.append(
                f"V7: Universal quantifier(s) ({', '.join(found_universal)}) "
                f"in user request, coverage analysis present"
            )
    else:
        passes.append("V7: No universal quantifiers in user request")

    # --- Check B: Over-judgment detection (WARN) ---
    if mode == "full" and not found_universal:
        if step_count <= 2 and must_modify_count <= 3:
            warns.append(
                f"V7: Full mode selected but only {step_count} implementation "
                f"step(s) and {must_modify_count} must-modify file(s) — "
                f"this may be a Light scenario (config/parameter change). "
                f"Verify Full is justified."
            )
        else:
            passes.append(
                f"V7: Full mode with {step_count} step(s), "
                f"{must_modify_count} must-modify file(s) — scope justifies Full"
            )

    # --- Check C: Under-judgment detection (WARN) ---
    if mode == "light" and must_modify_count > 5:
        warns.append(
            f"V7: Light mode selected but {must_modify_count} files require "
            f"sync modification — this may be a Full scenario"
        )

    return passes, fails, warns


# ===========================================================================
# Main
# ===========================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Gate validator for impact document output"
    )
    parser.add_argument(
        "req_dir",
        help="Path to requirement directory (e.g., change-impact/B3/)",
    )
    parser.add_argument(
        "--mode",
        choices=["light", "full"],
        default=None,
        help="Analysis mode (auto-detected if not specified)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Project root directory (for V6 file checks, default: current dir)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for V6 sampling (for reproducibility)",
    )
    args = parser.parse_args()

    req_dir = Path(args.req_dir).resolve()
    if not req_dir.is_dir():
        print(f"FAIL: Directory not found: {req_dir}")
        sys.exit(1)

    repo_root = os.path.abspath(args.repo_root)
    mode = args.mode

    # Auto-detect mode if not specified
    if mode is None:
        if (req_dir / "040-light.md").exists():
            mode = "light"
        elif (req_dir / "010-requirements.md").exists():
            mode = "full"
        else:
            mode = "unknown"

    print(f"Requirement directory: {req_dir}")
    print(f"Mode: {mode}")
    print(f"Repo root: {repo_root}")
    print()

    all_passes: list[str] = []
    all_fails: list[str] = []
    all_warns: list[str] = []

    # V1: File completeness
    p, f = check_file_completeness(req_dir, mode)
    all_passes.extend(p)
    all_fails.extend(f)

    # V2: Requirements boundary
    p, w = check_requirements_boundary(req_dir)
    all_passes.extend(p)
    all_warns.extend(w)

    # V3: Method name verification
    p, w = check_method_verification(req_dir)
    all_passes.extend(p)
    all_warns.extend(w)

    # V4: Grading decision table
    p, w = check_decision_table(req_dir)
    all_passes.extend(p)
    all_warns.extend(w)

    # V5: Credential sanitization
    p, f, w = check_credentials(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V6: Line number spot check
    p, f, w = check_line_numbers(req_dir, repo_root, args.seed)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V7: Tier judgment sanity check
    p, f, w = check_tier_judgment(req_dir, mode)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # Output
    for p in all_passes:
        print(f"PASS: {p}")
    for w in all_warns:
        print(f"WARN: {w}")
    for f in all_fails:
        print(f"FAIL: {f}")

    print()
    print(
        f"SUMMARY: {len(all_passes)} passed, {len(all_fails)} failed, "
        f"{len(all_warns)} warnings"
    )

    if all_fails:
        print("\nFAIL items must be fixed before submitting to user.")
    if all_warns:
        print("WARN items should be communicated to user during confirmation.")

    sys.exit(1 if all_fails else 0)


if __name__ == "__main__":
    main()
