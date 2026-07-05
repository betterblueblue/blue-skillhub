#!/usr/bin/env python3
"""impact_validate.py — Gate validator for impact document output.

Runs after Phase 4 document output, before submitting to user for confirmation.
Any FAIL item blocks submission; WARN items should be communicated to user.

Checks:
  V1: File completeness (full: 000/010/020/030; light: 040-light.md)       — FAIL
      _active-state.md presence (FAIL if missing)
  V2: Requirements boundary (010-requirements.md free of technical details)  — WARN
  V3: Method name verification (§3.2 table + markers)                  — FAIL/WARN
  V4: Grading decision table (判档决策表 present in output)                 — WARN
  V5: Credential sanitization (all output files sanitized)                  — WARN
  V6: Line number spot check (random 3 references verified)                 — WARN
  V7: Tier judgment sanity (universal-quantifier coverage gate + over/under) — FAIL/WARN
  V8: Style rules check (_style-rules.md enforcement feasibility)            — WARN
  V9: Grading table fact consistency (判档表 vs context-pack §7)              — WARN
  V10: Global impact check table (020-design.md §6 in full mode)            — FAIL
  V11: Light mode key-path check (040-light.md 关键链路深度检查 section)     — FAIL
  V12: Phase 3 process check (_active-state.md Phase 3 状态 field)          — WARN
  V13: Phase 4/5 split gate (docs and source writes not same Step)           — FAIL
  V14: Phase 5 preflight gate (source writes require 060-preflight.md)        — FAIL
  V15: Phase 5 record/state gate (source diffs/Steps record execution+state)  — FAIL
  V16: Active-state Step consistency (header/table/recovery notes)            — FAIL
  V17: Task acceptance smoke check (obvious partial route text updates)        — FAIL
  V18: Verification evidence (_active-state.md validator results not placeholder) — FAIL
  V19: High-risk DDL crosscheck (DDL keywords require high-risk checklist)      — FAIL
  V20: Step confirmation field (every Step must have 用户确认 with Step number)  — FAIL
  V21: Provenance tags (§7 facts must have 【用户确认】/【代码推断】/【用户委托默认】) — FAIL
  V22: Pathfinder map consumption record (when map exists, record used/rechecked/rejected facts) — FAIL

Output: PASS/FAIL/WARN lines + SUMMARY line.
Exit code: 0 = pass (no FAIL), 1 = fail (any FAIL item).

Usage:
    python skills/impact/scripts/impact_validate.py <需求目录> [--mode light|full] [--repo-root DIR]
    python skills/impact/scripts/impact_validate.py change-impact/B3/ --mode full
    python skills/impact/scripts/impact_validate.py change-impact/B1/ --mode light --repo-root /path/to/project
"""

import argparse
import os
import random
import re
import subprocess
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
LIGHT_REQUIRED = ["000-context-pack.md", "040-light.md"]


def check_file_completeness(req_dir: Path, mode: str) -> tuple[list[str], list[str], list[str]]:
    """V1: Check that required files exist for the given mode.

    Also checks for _active-state.md (FAIL if missing — hard rule #10).
    """
    passes = []
    fails = []
    warns = []

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
            ], []

    missing = []
    for f in required:
        if (req_dir / f).exists():
            passes.append(f"V1: {f} exists ({mode} mode)")
        else:
            missing.append(f)
            fails.append(f"V1: Missing required file: {f} ({mode} mode)")

    # Check _active-state.md (FAIL — hard rule #10 makes it non-skippable)
    if (req_dir / "_active-state.md").exists():
        passes.append("V1: _active-state.md exists")
    else:
        fails.append(
            "V1: _active-state.md missing — must be created when first "
            "document is written and updated on status changes (see hard "
            "rule #10 and template _active-state.md)"
        )

    # 000-context-pack.md is in LIGHT_REQUIRED, so its absence is already FAIL
    return passes, fails, warns


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
#     evidence of grep verification for referenced method names.
#     If §3.2 API 方法验证 table is missing and method calls exist → FAIL.
#     If table exists but no verification markers → WARN.
# ===========================================================================

# Verification markers
RE_VERIFIED = re.compile(r"已核实|已验证|grep\s*确认|grep\s*验证|已确认存在")
RE_UNVERIFIED = re.compile(r"待确认|未确认.*存在|待核实")

# §3.2 API 方法验证 section header
RE_METHOD_TABLE_SECTION = re.compile(r"##\s*3\.2\s*API\s*方法验证")


def check_method_verification(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V3: Check 030-implementation.md for method name verification.

    Two-tier check:
      1. If existing method calls found but no §3.2 API 方法验证 table → FAIL
      2. If §3.2 table exists but no verification markers → WARN
      3. If §3.2 table exists with markers → PASS
    """
    passes = []
    fails = []
    warns = []

    impl_file = req_dir / "030-implementation.md"
    if not impl_file.exists():
        return [], [], []  # V1 handles missing file

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
    has_method_table = bool(RE_METHOD_TABLE_SECTION.search(text))

    if not real_calls:
        passes.append("V3: 030-implementation.md has no existing method calls to verify")
    elif not has_method_table:
        fails.append(
            "V3: 030-implementation.md references existing methods but has no "
            "§3.2 API 方法验证 table — must add the table and verify each method "
            "with grep (see template §3.2)"
        )
    elif has_verified or has_unverified:
        marker = "verified" if has_verified else "marked unverified"
        passes.append(f"V3: 030-implementation.md has §3.2 table with method verification markers ({marker})")
    else:
        warns.append(
            "V3: 030-implementation.md has §3.2 table but no "
            "verification markers (已核实/grep确认/待确认) — fill in the table"
        )

    return passes, fails, warns


# ===========================================================================
# V4: Grading decision table — output should include 判档决策表
# ===========================================================================

RE_DECISION_TABLE = re.compile(r"判档决策表|定级决策表|覆盖范围.*缺口.*判档|决策表")


def check_decision_table(req_dir: Path, mode: str = "full") -> tuple[list[str], list[str]]:
    """V4: Check for grading decision table in output files.

    In light mode, the grading decision table is not required, so a missing
    table is downgraded from WARN to a no-op (neither pass nor warn).
    """
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
    elif mode == "light":
        # light 模式不要求判档决策表，不产生 WARN 噪音
        pass
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


def check_credentials(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V5: Check all output files for unsanitized credentials.

    Scans full text including fenced code blocks — secrets in code blocks
    must also be sanitized. V5 is WARN by design (regex cannot distinguish
    real credentials from variable names), so false positives are acceptable
    and prompt human review.
    """
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

        # Scan full text (including code blocks) — secrets in code blocks
        # must also be sanitized per hard rule #7.
        # Per-match sanitization check: the (?!\*{3}) negative lookahead in
        # each RE_CREDS pattern skips individual sanitized values, so a mixed
        # line like "password=*** token=plainsecret" still catches the token.
        for i, line in enumerate(text.splitlines(), 1):
            # Skip template instruction lines (blockquote)
            if line.strip().startswith(">"):
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
# V8: Style rules check — verify _style-rules.md enforcement feasibility
#     and context-pack style section
# ===========================================================================

# Match table rows in强制规则 (3-col) and建议规则 (2-col) sections of _style-rules.md
# Third column is optional so 2-column advisory tables also parse
RE_STYLE_RULE_ROW = re.compile(
    r"\|\s*([^|]+?)\s*\|\s*([^|]+?)(?:\s*\|\s*([^|]*?))?\s*\|"
)

RE_STYLE_RULES_HEADER = re.compile(r"##\s*强制规则")
RE_STYLE_ADVISORY_HEADER = re.compile(r"##\s*建议规则")

# Context-pack style section markers
RE_CTX_STYLE_SECTION = re.compile(r"###\s*风格规范")
RE_CTX_STYLE_FILLED = re.compile(
    r"_style-rules\.md`\s*状态[：:]\s*已读取"
)


def _parse_style_rules_table(text: str, header_pattern: re.Pattern) -> list[dict]:
    """Parse a markdown table following a header pattern.

    Returns list of {rule, method, note} dicts.
    """
    lines = text.splitlines()
    rules = []
    in_table = False
    for i, line in enumerate(lines):
        if header_pattern.search(line):
            in_table = True
            continue
        if in_table:
            # Skip separator rows and non-table lines
            stripped = line.strip()
            if not stripped.startswith("|"):
                if stripped.startswith("##") or stripped.startswith("**"):
                    break
                continue
            if re.match(r"\|[-:\s|]+\|", stripped):
                continue
            # Parse table row: | rule | method | note |
            m = RE_STYLE_RULE_ROW.match(stripped)
            if m:
                rule_text = m.group(1).strip()
                # Skip header rows and HTML comment placeholders
                if rule_text.startswith("规则") or rule_text.startswith("<!--"):
                    continue
                method = m.group(2).strip()
                note = m.group(3).strip() if m.lastindex >= 3 else ""
                rules.append({"rule": rule_text, "method": method, "note": note})
    return rules


def check_style_rules(
    req_dir: Path, repo_root: str
) -> tuple[list[str], list[str], list[str]]:
    """V8: Check _style-rules.md enforcement feasibility.

    If _style-rules.md exists in {repo_root}/change-impact/:
    - Parse强制规则 and建议规则 tables
    - For强制 rules, verify校验手段 is auto-enforceable (grep/grep-exclude)
    - Warn if强制 rule uses人工确认 or code-graph (not auto-enforceable)
    - Warn if context-pack lacks风格规范 section

    If _style-rules.md does not exist → PASS (退回现有行为).
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    style_rules_path = Path(repo_root) / "change-impact" / "_style-rules.md"
    if not style_rules_path.exists():
        passes.append("V8: No _style-rules.md found — style checks退回 profile style_axes")
        return passes, fails, warns

    try:
        rules_text = style_rules_path.read_text(encoding="utf-8")
    except Exception as e:
        warns.append(f"V8: Cannot read _style-rules.md: {e}")
        return passes, fails, warns

    mandatory_rules = _parse_style_rules_table(rules_text, RE_STYLE_RULES_HEADER)
    advisory_rules = _parse_style_rules_table(rules_text, RE_STYLE_ADVISORY_HEADER)

    passes.append(
        f"V8: _style-rules.md found — {len(mandatory_rules)} mandatory, "
        f"{len(advisory_rules)} advisory rules"
    )

    # Check each mandatory rule's enforcement method
    enforceable_count = 0
    human_only_count = 0
    for rule in mandatory_rules:
        method = rule["method"]
        rule_desc = rule["rule"][:60]

        if method.startswith("grep:"):
            pattern = method[len("grep:"):].strip()
            try:
                re.compile(pattern)
                enforceable_count += 1
                passes.append(f"V8: 强制规则 '{rule_desc}' — grep enforceable")
            except re.error as e:
                warns.append(
                    f"V8: 强制规则 '{rule_desc}' — invalid grep pattern "
                    f"'{pattern}': {e}"
                )
        elif method.startswith("grep-exclude:"):
            rest = method[len("grep-exclude:"):].strip()
            parts = rest.split(":", 1)
            if len(parts) == 2:
                pattern, exclude_dir = parts[0].strip(), parts[1].strip()
                try:
                    re.compile(pattern)
                    enforceable_count += 1
                    passes.append(
                        f"V8: 强制规则 '{rule_desc}' — grep-exclude enforceable "
                        f"(exclude: {exclude_dir})"
                    )
                except re.error as e:
                    warns.append(
                        f"V8: 强制规则 '{rule_desc}' — invalid grep pattern: {e}"
                    )
            else:
                warns.append(
                    f"V8: 强制规则 '{rule_desc}' — grep-exclude missing ':dir' "
                    f"(format: grep-exclude:pattern:directory)"
                )
        elif method.startswith("人工") or method.startswith("code-graph"):
            human_only_count += 1
            warns.append(
                f"V8: 强制规则 '{rule_desc}' — 校验手段为 '{method}'，"
                f"无法自动 FAIL。建议降级为建议规则，或提供 grep 校验模式。"
            )
        elif method.startswith("<!--") or not method:
            # Placeholder/empty — skip
            pass
        else:
            warns.append(
                f"V8: 强制规则 '{rule_desc}' — 未知校验手段 '{method}'，"
                f"无法自动执行"
            )

    if enforceable_count > 0:
        passes.append(
            f"V8: {enforceable_count} mandatory rules are auto-enforceable (grep)"
        )
    if human_only_count > 0:
        warns.append(
            f"V8: {human_only_count} mandatory rules require human review — "
            f"listed in需人工复核清单"
        )

    # Check context-pack has style section filled in
    ctx_file = req_dir / "000-context-pack.md"
    if ctx_file.exists():
        ctx_text = ctx_file.read_text(encoding="utf-8")
        if not RE_CTX_STYLE_SECTION.search(ctx_text):
            warns.append(
                "V8: 000-context-pack.md missing '### 风格规范' section "
                "— should record _style-rules.md status"
            )
        elif not RE_CTX_STYLE_FILLED.search(ctx_text):
            warns.append(
                "V8: 000-context-pack.md风格规范 section not filled in "
                "— should record how many rules were loaded"
            )
        else:
            passes.append("V8: 000-context-pack.md风格规范 section filled in")

    return passes, fails, warns


# ===========================================================================
# V9: Grading table fact consistency — check that factual claims in the
#     grading decision table are consistent with context-pack §7
# ===========================================================================

# Entity identifier patterns (camelCase, snake_case, PascalCase) — at least 5 chars
RE_CAMEL_ENTITY = re.compile(r'\b([a-z]\w*?[A-Z]\w*)\b')
RE_SNAKE_ENTITY = re.compile(r'\b([a-z][a-z]+_[a-z_]+)\b')
RE_PASCAL_ENTITY = re.compile(r'\b([A-Z]\w*[a-z]\w*[A-Z]\w*)\b')

# Contradiction descriptor pairs (positive, negative)
CONTRADICTION_PAIRS = [
    ("含", "不含"),
    ("包含", "不包含"),
    ("存在", "不存在"),
    ("已存在", "不存在"),
    ("已实现", "未实现"),
    ("已实现", "不存在"),
]

# Keywords indicating a factual claim
FACT_CLAIM_KEYWORDS = ["含", "不含", "存在", "不存在", "默认", "已实现", "未实现"]


def _split_table_row(row: str) -> list[str]:
    """Split a markdown table row into cells."""
    inner = row.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def _extract_section_text(text: str, keywords: list[str]) -> str:
    """Extract a markdown section whose header contains any of the keywords."""
    for kw in keywords:
        pattern = rf'(#{{2,3}}\s*[^\n]*{kw}[^\n]*\n.*?)(?=\n#{{2,3}}\s|\Z)'
        m = re.search(pattern, text, re.S)
        if m:
            return m.group(0)
    return ""


def _extract_confirmed_facts(ctx_text: str) -> list[str]:
    """Extract confirmed facts from context-pack §7 or equivalent section."""
    section = _extract_section_text(ctx_text, ["已确认事实"])
    if not section:
        return []
    facts: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        fact = line.lstrip("-").strip()
        # Skip template placeholders
        if "[事实]" in fact or "[路径" in fact or fact.startswith("`["):
            continue
        if fact:
            facts.append(fact)
    return facts


def _parse_table_facts(lines: list[str], header_idx: int) -> list[str]:
    """Parse a markdown table starting at header_idx, extract fact columns.

    Fact columns are those whose header contains keywords like 现有/覆盖/缺口/现状.
    """
    header = lines[header_idx].strip()
    header_cols = _split_table_row(header)
    fact_col_indices = [
        idx
        for idx, col in enumerate(header_cols)
        if any(kw in col for kw in ["现有", "覆盖", "缺口", "现状", "已有"])
    ]
    if not fact_col_indices:
        return []
    entries: list[str] = []
    for i in range(header_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if not stripped.startswith("|"):
            break
        if re.match(r"^\|[-:\s|]+$", stripped):
            continue
        cols = _split_table_row(stripped)
        for idx in fact_col_indices:
            if idx < len(cols):
                cell = cols[idx].strip()
                if cell and not cell.startswith("[") and cell not in ("—", "-"):
                    entries.append(cell)
    return entries


def _extract_grading_entries(impl_text: str) -> list[str]:
    """Extract factual claims from grading decision table in implementation docs."""
    lines = impl_text.splitlines()

    # Strategy 1: find table with "判档" in header row
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "判档" in stripped:
            entries = _parse_table_facts(lines, i)
            if entries:
                return entries

    # Strategy 2: find section header with "判档" keyword, then next table
    for i, line in enumerate(lines):
        if any(kw in line for kw in ["判档决策表", "定级决策表", "判档表"]):
            for j in range(i + 1, min(i + 20, len(lines))):
                if lines[j].strip().startswith("|"):
                    entries = _parse_table_facts(lines, j)
                    if entries:
                        return entries
                    break
    return []


def _extract_entities(text: str) -> set[str]:
    """Extract identifiers (camelCase, snake_case, PascalCase) from text.

    Supports multiple naming conventions to work across Java/JS (camelCase),
    Python (snake_case), and Go (PascalCase) projects.
    Only identifiers >= 5 chars are kept to reduce false positives.
    """
    entities: set[str] = set()
    for pattern in (RE_CAMEL_ENTITY, RE_SNAKE_ENTITY, RE_PASCAL_ENTITY):
        for m in pattern.finditer(text):
            entity = m.group(1)
            if len(entity) >= 5:
                entities.add(entity)
    return entities


def _entity_context(text: str, entity: str, window: int = 40) -> str:
    """Extract a context window around the first occurrence of entity in text."""
    idx = text.find(entity)
    if idx == -1:
        return text
    start = max(0, idx - window)
    end = min(len(text), idx + len(entity) + window)
    return text[start:end]


def _has_term(text: str, term: str, exclude: str = "") -> bool:
    """Check if text contains term, excluding occurrences that are part of exclude.

    When term is a substring of exclude (e.g. '含' in '不含'), we first
    remove all occurrences of exclude before checking for term.
    """
    if not exclude or exclude == term:
        return term in text
    return term in text.replace(exclude, "")


def _check_contradiction(text1: str, text2: str) -> bool:
    """Check if two texts contain contradictory descriptors.

    For each (positive, negative) pair, checks if one text has the positive
    form while the other has the negative form. Handles the case where the
    positive term is a substring of the negative term (e.g. '含' in '不含')
    by stripping negative occurrences before checking for positive.
    """
    for pos, neg in CONTRADICTION_PAIRS:
        t1_has_pos = _has_term(text1, pos, neg)
        t1_has_neg = neg in text1
        t2_has_pos = _has_term(text2, pos, neg)
        t2_has_neg = neg in text2
        if (t1_has_pos and t2_has_neg) or (t1_has_neg and t2_has_pos):
            return True
    return False


def check_grading_facts_consistency(
    req_dir: Path,
) -> tuple[list[str], list[str], list[str]]:
    """V9: Check grading decision table facts against context-pack §7.

    Extracts factual claims from the grading decision table in
    implementation docs and cross-checks them against confirmed facts
    in 000-context-pack.md §7. Reports WARN for:
      - Contradictions: same entity described differently in two places
      - Unconfirmed facts: grading table references entity not in §7
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    ctx_file = req_dir / "000-context-pack.md"
    if not ctx_file.exists():
        return [], [], []  # V1 handles missing file

    ctx_text = ctx_file.read_text(encoding="utf-8")
    facts = _extract_confirmed_facts(ctx_text)

    # Extract grading table from all .md files (030, 040, etc.)
    table_entries: list[str] = []
    for f in sorted(req_dir.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            table_entries.extend(_extract_grading_entries(text))
        except Exception:
            pass

    if not table_entries:
        passes.append(
            "V9: No grading decision table found — skip fact consistency check"
        )
        return passes, fails, warns

    if not facts:
        warns.append(
            "V9: 000-context-pack.md has no confirmed facts (§7) — "
            "cannot verify grading table consistency"
        )
        return passes, fails, warns

    # Build entity → facts mapping from §7
    entity_to_facts: dict[str, list[str]] = {}
    for fact in facts:
        for entity in _extract_entities(fact):
            entity_to_facts.setdefault(entity, []).append(fact)

    # Check each grading table entry
    contradictions: list[str] = []
    unconfirmed: list[str] = []
    consistent_count = 0

    for entry in table_entries:
        entry_entities = _extract_entities(entry)
        if not entry_entities:
            continue

        entry_has_match = False
        for entity in entry_entities:
            if entity in entity_to_facts:
                entry_has_match = True
                for ctx_fact in entity_to_facts[entity]:
                    entry_ctx = _entity_context(entry, entity)
                    ctx_ctx = _entity_context(ctx_fact, entity)
                    if _check_contradiction(entry_ctx, ctx_ctx):
                        contradictions.append(
                            f"V9: Contradiction for '{entity}' — "
                            f"grading table: '{entry[:80]}' vs "
                            f"§7: '{ctx_fact[:80]}'"
                        )
                    else:
                        consistent_count += 1

        if not entry_has_match:
            if any(kw in entry for kw in FACT_CLAIM_KEYWORDS):
                unconfirmed.append(entry)

    if contradictions:
        warns.extend(contradictions)
    elif consistent_count > 0:
        passes.append(
            f"V9: Grading table facts consistent with context-pack §7 "
            f"({consistent_count} entities verified)"
        )
    else:
        passes.append("V9: No shared entities between grading table and §7")

    if unconfirmed:
        for entry in unconfirmed[:3]:
            warns.append(
                f"V9: Grading table fact not in §7 — '{entry[:80]}'"
            )

    return passes, fails, warns


# ===========================================================================
# V10: Global impact check table — 020-design.md must have §6 table
#      with 19 dimension rows in full mode
# ===========================================================================

# Match §6 section header (flexible: "## 6. 全局影响检查" or "## 6 全局影响检查")
RE_CROSSCUT_HEADER = re.compile(r"##\s*6[\.\s]*全局影响检查")

# Match table rows with ☑ or ☐ markers (allow optional whitespace around marker)
RE_CROSSCUT_ROW = re.compile(r"\|[^\|]*[☑☐]\s*\|")

# Match dimension row numbers (1-19)
RE_CROSSCUT_DIM_ROW = re.compile(r"\|\s*\d+\s*\|")


def check_global_impact_table(req_dir: Path, mode: str) -> tuple[list[str], list[str], list[str]]:
    """V10: Check 020-design.md for global impact check table in full mode.

    - FAIL if §6 全局影响检查 section is completely missing in full mode
    - FAIL if table exists but has fewer than 19 dimension rows
    - FAIL if table has 19 rows but not all have ☑/☐ markers
    - PASS if table has 19 rows, all with ☑/☐ markers
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    if mode != "full":
        return passes, fails, warns  # Only check in full mode

    design_file = req_dir / "020-design.md"
    if not design_file.exists():
        return passes, fails, warns  # V1 handles missing file

    text = design_file.read_text(encoding="utf-8")

    has_header = bool(RE_CROSSCUT_HEADER.search(text))
    # Extract §6 section text to avoid counting table rows from other sections
    section_text = _extract_section_text(text, ["全局影响检查"])
    dim_rows = RE_CROSSCUT_DIM_ROW.findall(section_text) if section_text else []
    marker_rows = RE_CROSSCUT_ROW.findall(section_text) if section_text else []

    if not has_header:
        fails.append(
            "V10: 020-design.md missing §6 全局影响检查 section in full mode — "
            "must include the 19-row global impact check table "
            "(see template 020-design.md §6). Renaming or skipping this "
            "section = incomplete submission."
        )
    elif len(dim_rows) < 19:
        fails.append(
            f"V10: 020-design.md §6 全局影响检查 table has only {len(dim_rows)} "
            f"dimension rows — must have all 19 rows (check template). "
            f"Rows with ☑/☐ markers: {len(marker_rows)}"
        )
    elif len(marker_rows) < 19:
        fails.append(
            f"V10: 020-design.md §6 全局影响检查 table has {len(dim_rows)} rows "
            f"but only {len(marker_rows)} have ☑/☐ markers — all 19 rows "
            f"must be explicitly marked as 涉及(☑) or 不涉及(☐)"
        )
    else:
        passes.append(
            f"V10: 020-design.md §6 全局影响检查 table present with "
            f"{len(dim_rows)} dimension rows, {len(marker_rows)} marked"
        )

    return passes, fails, warns


# ===========================================================================
# V11: Light mode key-path check — 040-light.md must have "关键链路深度检查"
#      section (template requires it, phase-4-output.md enforces it)
# ===========================================================================

RE_KEYPATH_SECTION = re.compile(r"关键链路深度检查")


def check_light_keypath(req_dir: Path, mode: str) -> tuple[list[str], list[str], list[str]]:
    """V11: In light mode, 040-light.md must include '关键链路深度检查' section.

    The template marks this section as 'light 模式强制', and phase-4-output.md
    says 'light 模式必须完成关键链路深度检查'. This validator checks that
    the section heading exists (content quality is not auto-checked).
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    if mode != "light":
        return passes, fails, warns  # Only check in light mode

    light_file = req_dir / "040-light.md"
    if not light_file.exists():
        return passes, fails, warns  # V1 handles missing file

    text = light_file.read_text(encoding="utf-8")

    if RE_KEYPATH_SECTION.search(text):
        passes.append("V11: 040-light.md contains 关键链路深度检查 section")
    else:
        fails.append(
            "V11: 040-light.md missing '关键链路深度检查' section — "
            "light mode requires this check (see template 040-light.md)"
        )

    return passes, fails, warns


# ===========================================================================
# V12: Phase 3 process check — _active-state.md must have Phase 3 状态 field
#      to make Phase 3 skip visible (field presence check, not truthfulness)
# ===========================================================================

RE_PHASE3_STATUS = re.compile(r"Phase\s*3\s*状态")
RE_PHASE3_GRADING = re.compile(r"Phase\s*3\.5\s*定级")


def check_phase3_process(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V12: Check _active-state.md for Phase 3 process tracking fields.

    Validates that the _active-state.md file includes the Phase 3 状态 and
    Phase 3.5 定级 fields added to the template. This makes it visible when
    Phase 3 was skipped — the validator cannot verify truthfulness (an agent
    could write '已完成' without actually doing it), but field presence forces
    the agent to explicitly declare the Phase 3 outcome.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    state_file = req_dir / "_active-state.md"
    if not state_file.exists():
        return passes, fails, warns  # V1 handles missing _active-state.md

    text = state_file.read_text(encoding="utf-8")

    has_phase3_status = bool(RE_PHASE3_STATUS.search(text))
    has_phase3_grading = bool(RE_PHASE3_GRADING.search(text))

    if has_phase3_status and has_phase3_grading:
        mode_val = (_active_field(text, "模式") or "").lower()
        grading_val = (_active_field(text, "Phase 3.5 定级") or "").lower()
        if "full" in mode_val and ("light" in grading_val or "快速通道" in grading_val):
            fails.append(
                "V12: _active-state.md Phase 3.5 定级 conflicts with 模式 — "
                f"模式 is {mode_val!r} but Phase 3.5 定级 is {grading_val!r}"
            )
        else:
            passes.append("V12: _active-state.md has Phase 3 状态 and Phase 3.5 定级 fields")
    else:
        missing = []
        if not has_phase3_status:
            missing.append("Phase 3 状态")
        if not has_phase3_grading:
            missing.append("Phase 3.5 定级")
        warns.append(
            f"V12: _active-state.md missing {', '.join(missing)} field(s) — "
            f"must include Phase 3 process tracking (see template _active-state.md)"
        )

    return passes, fails, warns


# ===========================================================================
# V13: Phase 4/5 split gate — Phase 4 document writes must not be merged with
#      source/test/config writes in the same execution Step.
# ===========================================================================

RE_EXEC_STEP = re.compile(r"(?m)^##\s+.*?Step\s+\d+[^\n]*")
RE_EXEC_HEADING = re.compile(r"(?m)^##\s+")
RE_PHASE4_DOC_WRITE = re.compile(
    r"000-context-pack\.md|010-requirements\.md|020-design\.md|"
    r"030-implementation\.md|040-light\.md|(?<!pre)light\s*文档|"
    r"full\s*文档|分析文档",
    re.I,
)
RE_SOURCE_WRITE_ACTION = re.compile(
    r"修改|新增|删除|改代码|源码|测试修复|测试断言|配置变更|DDL|DML|外部系统写操作",
    re.I,
)
RE_SOURCE_WRITE_TARGET = re.compile(
    r"(?:src|tests|test|prisma|app|frontend|backend)[/\\]|"
    r"\.(?:java|kt|ts|tsx|js|jsx|py|go|vue|html|xml|sql|prisma|yml|yaml|json)\b",
    re.I,
)
RE_SOURCE_CONFIRM_TYPE_LINE = re.compile(
    r"确认类型[:：].*(改代码|测试修复|配置变更|DDL|DML|外部系统写操作)",
    re.I,
)
RE_SOURCE_OBJECT_LINE = re.compile(
    r"操作对象[:：].*((?:src|tests|test|prisma|app|frontend|backend)[/\\]|"
    r"\.(?:java|kt|ts|tsx|js|jsx|py|go|vue|html|xml|sql|prisma|yml|yaml|json)\b)",
    re.I,
)
RE_SOURCE_CONTENT_WRITE_ACTION = re.compile(
    r"改代码|测试修复|测试断言|配置变更|DDL|DML|外部系统写操作",
    re.I,
)
RE_PHASE4_DOC_WRITE_ACTION = re.compile(
    r"写入|生成|更新|产出|创建|补写|输出|write|create|generate|update",
    re.I,
)
RE_OPERATION_OBJECT_LINE = re.compile(r"^\s*[-*]?\s*(操作对象|写入对象|目标文件|修改对象)[:：]", re.I)
RE_OPERATION_CONTENT_LINE = re.compile(r"^\s*[-*]?\s*(操作内容|操作|执行结果)[:：]", re.I)


def _execution_step_sections(text: str) -> list[str]:
    """Split 090-execution-record.md into Step sections."""
    matches = list(RE_EXEC_STEP.finditer(text))
    sections: list[str] = []
    for match in matches:
        start = match.start()
        next_heading = RE_EXEC_HEADING.search(text, match.end())
        end = next_heading.start() if next_heading else len(text)
        sections.append(text[start:end])
    return sections


def _has_source_write_in_step(section: str) -> bool:
    """Return true only when a Step's write target is source/test/config-like.

    Source paths may appear in impact notes or evidence while the Step only
    writes Phase 4 docs. V13 should fail merged write Steps, not valid docs-only
    records that mention source files as analysis input.
    """
    lines = section.splitlines()
    title = lines[0] if lines else ""
    if RE_SOURCE_WRITE_ACTION.search(title) and RE_SOURCE_WRITE_TARGET.search(section):
        return True
    for line in lines:
        if RE_SOURCE_CONFIRM_TYPE_LINE.search(line) or RE_SOURCE_OBJECT_LINE.search(line):
            return True
        if line.lstrip().startswith("- 操作内容"):
            if RE_SOURCE_CONTENT_WRITE_ACTION.search(line) and RE_SOURCE_WRITE_TARGET.search(line):
                return True
    return False


def _has_phase4_doc_write_in_step(section: str) -> bool:
    """Return true when a Step writes Phase 4 docs, not merely references them."""
    lines = section.splitlines()
    title = lines[0] if lines else ""
    if RE_PHASE4_DOC_WRITE.search(title) and RE_PHASE4_DOC_WRITE_ACTION.search(title):
        return True

    for line in lines:
        stripped = line.strip()
        if RE_OPERATION_OBJECT_LINE.search(stripped) and RE_PHASE4_DOC_WRITE.search(stripped):
            return True
        if (
            RE_OPERATION_CONTENT_LINE.search(stripped)
            and RE_PHASE4_DOC_WRITE.search(stripped)
            and RE_PHASE4_DOC_WRITE_ACTION.search(stripped)
        ):
            return True
    return False


def check_phase4_phase5_split(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V13: Check execution record for merged Phase 4 docs + source writes.

    Phase 4 document output must be completed and validated before Phase 5
    source/test/config writes are requested. A single Step that writes
    000/040/etc. and also edits source/tests/config means the user confirmed
    too broad a Step, so it fails.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    record_file = req_dir / "090-execution-record.md"
    if not record_file.exists():
        passes.append("V13: No execution record yet — no Phase 5 step merge to check")
        return passes, fails, warns

    text = record_file.read_text(encoding="utf-8")
    sections = _execution_step_sections(text)
    if not sections:
        passes.append("V13: 090-execution-record.md has no Step sections to check")
        return passes, fails, warns

    merged_steps: list[str] = []
    for section in sections:
        if _has_phase4_doc_write_in_step(section) and _has_source_write_in_step(section):
            title = section.splitlines()[0].strip()
            merged_steps.append(title)

    if merged_steps:
        fails.append(
            "V13: Phase 4 document writes and source/test/config writes are "
            "merged in the same Step — split them. Phase 4 docs must be "
            "written and pass impact_validate.py before asking for a source "
            f"write Step. Offending Step(s): {'; '.join(merged_steps[:3])}"
        )
    else:
        passes.append("V13: Phase 4 document writes are separated from source/test/config Steps")

    return passes, fails, warns


def check_phase5_preflight(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V14: Source/test/config write Steps require 060-preflight.md."""
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    record_file = req_dir / "090-execution-record.md"
    if not record_file.exists():
        passes.append("V14: No execution record yet — no Phase 5 preflight to check")
        return passes, fails, warns

    text = record_file.read_text(encoding="utf-8")
    source_steps = [
        section.splitlines()[0].strip()
        for section in _execution_step_sections(text)
        if _has_source_write_in_step(section)
    ]
    if not source_steps:
        passes.append("V14: No source/test/config write Steps found — preflight not required")
        return passes, fails, warns

    preflight_file = req_dir / "060-preflight.md"
    if preflight_file.exists():
        passes.append("V14: 060-preflight.md exists before source/test/config write review")
    else:
        fails.append(
            "V14: Source/test/config write Step found but 060-preflight.md is missing — "
            "complete Phase 5 preflight before source writes. "
            f"Source Step(s): {'; '.join(source_steps[:3])}"
        )

    return passes, fails, warns


RE_EXECUTION_RECORD_REF = re.compile(r"090-execution-record\.md", re.I)
RE_ACTIVE_STATE_REF = re.compile(r"_active-state\.md", re.I)


def _changed_source_paths(repo_root: str) -> list[str]:
    """Return changed source/test/config-like paths from git status.

    This is intentionally best-effort: non-Git projects keep the old text-only
    V15 behavior, while Git projects can catch a source diff that exists before
    an execution record is written.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_root, "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    if result.returncode != 0:
        return []

    changed: list[str] = []
    for raw_line in result.stdout.splitlines():
        if len(raw_line) < 4:
            continue
        path = raw_line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        path = path.strip('"').replace("\\", "/")
        if path.startswith("change-impact/") or path.startswith(".git/"):
            continue
        if RE_SOURCE_WRITE_TARGET.search(path):
            changed.append(path)
    return changed


def _normalized_text(text: str) -> str:
    return text.replace("\\", "/")


def _path_is_recorded(path: str, sections: list[str]) -> bool:
    normalized_path = path.replace("\\", "/").strip("/")
    variants = {normalized_path}
    if normalized_path.startswith("src/"):
        variants.add(normalized_path[4:])
    if normalized_path.startswith("./"):
        variants.add(normalized_path[2:])

    for section in sections:
        text = _normalized_text(section)
        if any(variant and variant in text for variant in variants):
            return True
    return False


def check_phase5_record_state(req_dir: Path, repo_root: str) -> tuple[list[str], list[str], list[str]]:
    """V15: Source/test/config diffs and write Steps must record execution/state."""
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    record_file = req_dir / "090-execution-record.md"
    changed_paths = _changed_source_paths(repo_root)
    if not record_file.exists():
        if changed_paths:
            fails.append(
                f"V15: Source/test/config files have git changes but "
                f"090-execution-record.md is missing — "
                f"Changed path(s): {'; '.join(changed_paths[:5])}.\n"
                "  修复步骤:\n"
                "  1. 创建 090-execution-record.md，为每个有源码改动的 Step 记录执行过程\n"
                "  2. 在每个 Step 的执行记录中列出 changed path\n"
                "  3. 更新 _active-state.md 的 Step 状态和最近验证结果"
            )
            return passes, fails, warns
        passes.append("V15: No execution record yet — no Phase 5 record/state check needed")
        return passes, fails, warns

    text = record_file.read_text(encoding="utf-8")
    source_sections = [
        section for section in _execution_step_sections(text)
        if _has_source_write_in_step(section)
    ]
    if changed_paths and not source_sections:
        fails.append(
            f"V15: Source/test/config files have git changes but "
            f"090-execution-record.md has no source/test/config write Step — "
            f"Changed path(s): {'; '.join(changed_paths[:5])}.\n"
            "  修复步骤:\n"
            "  1. 在 090-execution-record.md 中添加执行 Step（标题含 'Step' 和步骤号）\n"
            "  2. 在该 Step 中记录所有 changed path\n"
            "  3. 在该 Step 中引用 090-execution-record.md 和 _active-state.md"
        )
        return passes, fails, warns

    unrecorded_paths = [
        path for path in changed_paths
        if not _path_is_recorded(path, source_sections)
    ]
    if unrecorded_paths:
        fails.append(
            f"V15: Source/test/config files have git changes but are not "
            f"listed in any source/test/config execution Step — "
            f"Unrecorded path(s): {'; '.join(unrecorded_paths[:5])}.\n"
            "  修复步骤:\n"
            "  1. 在 090-execution-record.md 对应 Step 中补充缺少的 path\n"
            "  2. 或如果该改动不在本需求范围内，用 git checkout 还原文件"
        )
        return passes, fails, warns

    missing_steps: list[str] = []
    for section in source_sections:
        missing = []
        if not RE_EXECUTION_RECORD_REF.search(section):
            missing.append("090-execution-record.md")
        if not RE_ACTIVE_STATE_REF.search(section):
            missing.append("_active-state.md")
        if missing:
            title = section.splitlines()[0].strip()
            missing_steps.append(f"{title} missing {', '.join(missing)}")

    if missing_steps:
        fails.append(
            f"V15: Source/test/config write Step must include execution record "
            f"and active-state updates in the same Step — "
            f"Offending Step(s): {'; '.join(missing_steps[:3])}.\n"
            "  修复步骤:\n"
            "  1. 在对应 Step 的执行记录中添加引用: 090-execution-record.md\n"
            "  2. 在对应 Step 的执行记录中添加引用: _active-state.md\n"
            "  3. 确认 _active-state.md 中该 Step 状态已更新"
        )
    else:
        passes.append("V15: Source/test/config write Steps include execution record and active-state updates")

    return passes, fails, warns


# ===========================================================================
# V17: Task acceptance smoke check — catch obvious partial route text updates.
# ===========================================================================

RE_LABEL_LINE = re.compile(r"^\s*[+-]\s*label\s*:\s*(['\"])(?P<value>.*?)\1\s*,?\s*$", re.M)
RE_TITLE_VALUE = re.compile(r"title\s*:\s*(['\"])(?P<value>.*?)\1")
ROUTE_TEXT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue"}


def _git_diff_for_path(repo_root: str, path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", repo_root, "diff", "--unified=0", "--", path],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def _label_changes_from_diff(diff_text: str) -> list[tuple[str, str]]:
    old_values: list[str] = []
    changes: list[tuple[str, str]] = []
    for match in RE_LABEL_LINE.finditer(diff_text):
        line = match.group(0)
        value = match.group("value")
        if line.lstrip().startswith("-"):
            old_values.append(value)
        elif line.lstrip().startswith("+") and old_values:
            old_value = old_values.pop(0)
            if old_value != value:
                changes.append((old_value, value))
    return changes


def _line_window(lines: list[str], index: int, radius: int = 12) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def _partial_route_text_updates(repo_root: str, changed_paths: list[str]) -> list[str]:
    findings: list[str] = []
    root = Path(repo_root)
    for relpath in changed_paths:
        path = Path(relpath)
        if path.suffix.lower() not in ROUTE_TEXT_EXTENSIONS:
            continue

        diff_text = _git_diff_for_path(repo_root, relpath)
        label_changes = _label_changes_from_diff(diff_text)
        if not label_changes:
            continue

        abs_path = root / relpath
        if not abs_path.exists():
            continue
        try:
            lines = abs_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for old_value, new_value in label_changes:
            for idx, line in enumerate(lines):
                if "label" not in line or new_value not in line:
                    continue
                window = _line_window(lines, idx)
                for title_match in RE_TITLE_VALUE.finditer(window):
                    if title_match.group("value") == old_value:
                        findings.append(f"{relpath}: label {old_value!r}->{new_value!r} but sibling title remains {old_value!r}")
                        break
                if findings and findings[-1].startswith(f"{relpath}: label {old_value!r}->{new_value!r}"):
                    break
    return findings


def check_task_acceptance_smoke(repo_root: str) -> tuple[list[str], list[str], list[str]]:
    """V17: Catch obvious partial implementation of route display text changes."""
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    changed_paths = _changed_source_paths(repo_root)
    if not changed_paths:
        passes.append("V17: No source/test/config git changes — no task-specific acceptance smoke needed")
        return passes, fails, warns

    partial_updates = _partial_route_text_updates(repo_root, changed_paths)
    if partial_updates:
        fails.append(
            "V17: Route display text appears partially updated — "
            "label changed while sibling title still uses the old display text. "
            "Update the paired display field or explicitly split/clarify the "
            f"acceptance boundary before completion. Finding(s): {'; '.join(partial_updates[:5])}"
        )
    else:
        passes.append("V17: No obvious partial route display-text update detected")

    return passes, fails, warns


# ===========================================================================
# V16: Active-state Step consistency — _active-state.md status header, Step
#      ledger and recovery notes must not contradict each other.
# ===========================================================================

RE_CONFIRMATION_REQUEST = re.compile(
    r"(等待|待|需要|请|请求|下一步|继续|必须).*确认\s*Step\s*(\d+)",
    re.I,
)


def _active_field(text: str, label: str) -> str | None:
    """Read a '- label: value' or '- label：value' field from _active-state.md."""
    m = re.search(rf"(?m)^\s*-\s*{re.escape(label)}\s*[:：]\s*(.+?)\s*$", text)
    if not m:
        return None
    return m.group(1).strip().strip("`")


def _normalize_step(value: str | None) -> str | None:
    """Normalize 'Step 4' / 'none' values; return None for placeholders."""
    if value is None:
        return None
    cleaned = value.strip().strip("[]` ")
    m = re.search(r"\bStep\s*(\d+)\b", cleaned, re.I)
    if m:
        return f"Step {m.group(1)}"
    if cleaned.lower() == "none" or cleaned in {"无", "无需", "不适用"}:
        return "none"
    return None


def _normalize_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    cleaned = value.strip().strip("[]` ").lower()
    if cleaned in {"true", "yes", "y", "1", "是", "需要"}:
        return True
    if cleaned in {"false", "no", "n", "0", "否", "无需", "不需要"}:
        return False
    return None


def _active_step_rows(text: str) -> dict[str, str]:
    """Return {Step N: status} from the Step ledger table."""
    section = _extract_section_text(text, ["Step 台账"])
    rows: dict[str, str] = {}
    for line in section.splitlines():
        cells = _split_table_row(line)
        if len(cells) < 2:
            continue
        m = re.search(r"\bStep\s*(\d+)\b", cells[0], re.I)
        if not m or cells[1] == "状态":
            continue
        rows[f"Step {m.group(1)}"] = cells[1]
    return rows


def _is_pending_status(status: str) -> bool:
    return any(term in status for term in ("计划", "待确认", "已确认", "进行中"))


def _is_terminal_status(status: str) -> bool:
    return any(term in status for term in ("成功", "已完成", "完成", "失败", "跳过"))


def _recovery_confirmation_requests(text: str) -> list[tuple[str, str]]:
    """Find recovery-note lines that ask for a future Step confirmation."""
    section = _extract_section_text(text, ["恢复备注"])
    requests: list[tuple[str, str]] = []
    for line in section.splitlines():
        if any(term in line for term in ("不需要", "无需", "无待确认", "没有待确认")):
            continue
        m = RE_CONFIRMATION_REQUEST.search(line)
        if m:
            requests.append((f"Step {m.group(2)}", line.strip()))
    return requests


def check_active_state_consistency(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V16: Check _active-state.md for mechanical Step-state consistency."""
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    state_file = req_dir / "_active-state.md"
    if not state_file.exists():
        return passes, fails, warns  # V1 handles missing _active-state.md

    text = state_file.read_text(encoding="utf-8")

    confirmation_required = _normalize_bool(_active_field(text, "是否需要确认"))
    pending_step = _normalize_step(_active_field(text, "待执行 Step"))
    prompted_step = _normalize_step(_active_field(text, "上次提示 Step"))
    completed_step = _normalize_step(_active_field(text, "上次完成 Step"))
    step_rows = _active_step_rows(text)

    issues: list[str] = []

    if confirmation_required is False and pending_step not in (None, "none"):
        issues.append(
            f"是否需要确认=false but 待执行 Step is {pending_step}"
        )
    if confirmation_required is True and pending_step == "none":
        issues.append("是否需要确认=true but 待执行 Step is none")

    if pending_step == "none":
        pending_rows = [
            f"{step}={status}"
            for step, status in step_rows.items()
            if _is_pending_status(status)
        ]
        if pending_rows:
            issues.append(
                "待执行 Step is none but Step 台账 still has pending rows: "
                + ", ".join(pending_rows[:3])
            )
    elif pending_step is not None:
        row_status = step_rows.get(pending_step)
        if row_status and _is_terminal_status(row_status):
            issues.append(
                f"待执行 Step is {pending_step} but Step 台账 marks it as {row_status}"
            )
        if prompted_step not in (None, "none", pending_step):
            issues.append(
                f"待执行 Step is {pending_step} but 上次提示 Step is {prompted_step}"
            )

    if completed_step not in (None, "none"):
        row_status = step_rows.get(completed_step)
        if row_status is None:
            issues.append(f"上次完成 Step is {completed_step} but Step 台账 has no row")
        elif not _is_terminal_status(row_status):
            issues.append(
                f"上次完成 Step is {completed_step} but Step 台账 marks it as {row_status}"
            )

    for note_step, line in _recovery_confirmation_requests(text):
        if pending_step in (None, "none"):
            issues.append(
                f"恢复备注仍要求确认 {note_step}, but 待执行 Step is none: {line[:80]}"
            )
        elif note_step != pending_step:
            issues.append(
                f"恢复备注要求确认 {note_step}, but 待执行 Step is {pending_step}: {line[:80]}"
            )

    if issues:
        fails.append(
            "V16: _active-state.md Step state is inconsistent — "
            + "; ".join(issues[:4])
        )
    else:
        passes.append("V16: _active-state.md Step state is internally consistent")

    return passes, fails, warns


# ===========================================================================
# V18: Verification evidence — _active-state.md validator results must be
#      actual output, not placeholders. Prevents models from claiming "PASS"
#      without running the validator (escape ledger E-001/E-002).
# ===========================================================================

RE_RESULT_PLACEHOLDER = re.compile(r"\[.*passed.*\]|N/A|未执行|不适用|尚未", re.I)
RE_ACTUAL_RESULT = re.compile(
    r"(?P<passed>\d+)\s*passed.*?(?P<failed>\d+)\s*failed?",
    re.I,
)


def check_verification_evidence(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V18: _active-state.md 最近验证 must have actual validator output.

    Checks that the 结果 field in the 最近验证 section contains real numbers
    matching validator output format (e.g., '15 passed, 0 failed, 2 warnings'),
    not placeholders like '[X passed...]' or 'N/A' or '未执行'.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    state_file = req_dir / "_active-state.md"
    if not state_file.exists():
        return passes, fails, warns  # V1 handles missing _active-state.md

    state_text = state_file.read_text(encoding="utf-8")
    section = _extract_section_text(state_text, ["最近验证"])
    if not section:
        warns.append("V18: _active-state.md missing 最近验证 section")
        return passes, fails, warns

    # Check 结果 field
    result_match = re.search(r"(?m)^\s*[-*]?\s*结果[：:]\s*(.+?)\s*$", section)
    if not result_match:
        fails.append(
            "V18: _active-state.md 最近验证 section missing 结果 field — "
            "must fill actual validator output.\n"
            "  修复步骤:\n"
            "  1. 运行 impact_validate.py 获取实际结果\n"
            "  2. 在 _active-state.md 最近验证 section 添加: 结果: <N> passed, <N> failed, <N> warnings"
        )
        return passes, fails, warns

    result_val = result_match.group(1).strip()

    # Check for placeholder values
    if RE_RESULT_PLACEHOLDER.search(result_val) or result_val.startswith("["):
        fails.append(
            f"V18: _active-state.md 最近验证 结果 is a placeholder — "
            f"must fill actual validator output, got: {result_val[:80]}.\n"
            "  修复步骤:\n"
            "  1. 运行 impact_validate.py 获取实际结果\n"
            "  2. 将结果字段替换为实际 validator 输出，格式: N passed, N failed, N warnings"
        )
        return passes, fails, warns

    # Check for actual validator output format
    result = RE_ACTUAL_RESULT.search(result_val)
    if not result:
        fails.append(
            f"V18: _active-state.md 最近验证 结果 doesn't match validator output format — "
            f"expected 'N passed, N failed, N warnings', got: {result_val[:80]}.\n"
            "  修复步骤:\n"
            "  1. 运行 impact_validate.py 获取实际结果\n"
            "  2. 粘贴 SUMMARY 行的统计，格式: N passed, N failed, N warnings"
        )
        return passes, fails, warns

    failed_count = int(result.group("failed"))
    if failed_count != 0:
        fails.append(
            f"V18: _active-state.md 最近验证 contains failed validator result — "
            f"expected 0 failed, got: {result_val[:80]}.\n"
            "  修复步骤:\n"
            "  1. 逐条修复 FAIL 项（看 FAIL 文案中的修复步骤）\n"
            "  2. 重新运行 impact_validate.py 直到 0 failed\n"
            "  3. 更新 _active-state.md 最近验证 结果 为最新的 0 failed 输出"
        )
        return passes, fails, warns

    passes.append("V18: _active-state.md 最近验证 has actual validator result")
    return passes, fails, warns


# ===========================================================================
# V19: High-risk DDL crosscheck — Steps with DDL keywords must have
#      high-risk checklist filled (escape ledger N-B).
# ===========================================================================

RE_DDL_KEYWORDS = re.compile(
    r"DROP\s+(TABLE|COLUMN|INDEX|CONSTRAINT)|TRUNCATE|ALTER\s+TABLE|"
    r"DELETE\s+FROM|UPDATE\s+\w+\s+SET",
    re.I,
)
RE_HIGH_RISK_TABLE = re.compile(r"高风险清单检查|DROP\s+TABLE.*PASS|DROP\s+TABLE.*FAIL", re.I)


def check_high_risk_ddl_crosscheck(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V19: Steps containing DDL keywords must have high-risk checklist filled.

    Scans 090-execution-record.md Step sections for DDL keywords (DROP,
    ALTER, TRUNCATE, etc.). If found, the Step must include the high-risk
    checklist table and 决策依据 must not say '不涉及'.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    record_file = req_dir / "090-execution-record.md"
    if not record_file.exists():
        passes.append("V19: No execution record yet — no DDL crosscheck needed")
        return passes, fails, warns

    text = record_file.read_text(encoding="utf-8")
    sections = _execution_step_sections(text)

    ddl_found = False
    for section in sections:
        if not RE_DDL_KEYWORDS.search(section):
            continue
        ddl_found = True
        title = section.splitlines()[0].strip() if section else "unknown"

        has_checklist = bool(RE_HIGH_RISK_TABLE.search(section))
        decision_match = re.search(r"决策依据[：:]\s*(.+?)$", section, re.M)
        decision_is_not_applicable = (
            decision_match and "不涉及" in decision_match.group(1)
        )

        if not has_checklist:
            fails.append(
                f"V19: {title} contains DDL keywords but has no high-risk checklist — "
                "must include the PASS/FAIL table for each high-risk item"
            )
        elif decision_is_not_applicable:
            fails.append(
                f"V19: {title} contains DDL keywords but 决策依据 says '不涉及' — "
                "DDL operations must record the specific high-risk item hit and confirmation"
            )
        else:
            passes.append(f"V19: {title} has DDL keywords with high-risk checklist filled")

    if not ddl_found:
        passes.append("V19: No DDL keywords in execution record — no high-risk crosscheck needed")

    return passes, fails, warns


# ===========================================================================
# V20: Step confirmation field — every Step in 090-execution-record.md must
#      have 用户确认 field with Step number (N-C).
# ===========================================================================

RE_USER_CONFIRM_FIELD = re.compile(r"(?m)^\s*[-*]?\s*用户确认[：:]\s*(.+?)\s*$")


def check_step_confirmation(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V20: Every Step in 090-execution-record.md must have 用户确认 with Step number.

    Extends V15's check beyond source-write Steps to ALL Steps. Each Step
    must include a 用户确认 field that references a specific Step number
    (e.g., '确认 Step 3') or explicitly says '未确认'.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    record_file = req_dir / "090-execution-record.md"
    if not record_file.exists():
        passes.append("V20: No execution record yet — no Step confirmation check needed")
        return passes, fails, warns

    text = record_file.read_text(encoding="utf-8")
    sections = _execution_step_sections(text)

    if not sections:
        passes.append("V20: No Step sections in execution record")
        return passes, fails, warns

    missing: list[str] = []
    for section in sections:
        title = section.splitlines()[0].strip() if section else "unknown"
        confirm_match = RE_USER_CONFIRM_FIELD.search(section)
        if not confirm_match:
            missing.append(title)
        else:
            confirm_val = confirm_match.group(1).strip()
            if not re.search(r"Step\s*\d+|未确认", confirm_val, re.I):
                missing.append(f"{title} (确认值缺 Step 编号: {confirm_val[:40]})")

    if missing:
        fails.append(
            "V20: Steps missing 用户确认 field with Step number — "
            f"offending: {'; '.join(missing[:3])}"
        )
    else:
        passes.append("V20: All Steps have 用户确认 field with Step number")

    return passes, fails, warns


# ===========================================================================
# V21: 来源标签 — §7 已确认事实 entries must carry a source tag
#      (补强 C script-enforceable part).
# ===========================================================================

RE_SOURCE_TAG = re.compile(r"【用户确认|【代码推断|【用户委托默认")


def check_source_tags(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V21: 000-context-pack §7 facts must have source tags.

    Each fact entry in §7 已确认事实 must carry one of:
      - 【用户确认】
      - 【代码推断: file:line】
      - 【用户委托默认: YYYY-MM-DD 选项X 依据file:line】
    Missing tags → FAIL. The script cannot verify tag truthfulness, but
    forcing source tags makes fabrication explicitly auditable.
    """
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    ctx_file = req_dir / "000-context-pack.md"
    if not ctx_file.exists():
        return passes, fails, warns  # V1 handles missing file

    ctx_text = ctx_file.read_text(encoding="utf-8")
    section = _extract_section_text(ctx_text, ["已确认事实"])
    if not section:
        warns.append("V21: 000-context-pack.md has no §7 已确认事实 section")
        return passes, fails, warns

    # Find fact entries (lines starting with - but not template placeholders)
    fact_lines: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        # Skip template placeholders
        if stripped.startswith("- `[") or stripped.startswith("- [事实"):
            continue
        if "来源标签" in stripped:
            continue
        fact_lines.append(stripped)

    if not fact_lines:
        passes.append("V21: §7 has no fact entries to check")
        return passes, fails, warns

    untagged: list[str] = []
    for fact in fact_lines:
        if not RE_SOURCE_TAG.search(fact):
            untagged.append(fact[:80])

    if untagged:
        fails.append(
            "V21: §7 已确认事实 entries missing source tags — "
            "each fact must have 【用户确认】/【代码推断: file:line】/【用户委托默认: …】. "
            f"Untagged: {'; '.join(untagged[:3])}"
        )
    else:
        passes.append(f"V21: §7 已确认事实 all {len(fact_lines)} entries have source tags")

    return passes, fails, warns


# ===========================================================================
# V22: Pathfinder map consumption record — when a map exists, context-pack
#      must record which Pathfinder facts were used, rechecked, or rejected.
# ===========================================================================

RE_MAP_STATUS = re.compile(r"项目地图状态[：:]\s*(.+)")
NO_MAP_MARKERS = ("无地图", "不存在", "未发现")
MAP_CONSUMPTION_ACTIONS = ("采用", "重新验证", "重验", "未采用", "过期", "待验证")


def check_pathfinder_consumption(req_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """V22: Require auditable Pathfinder map consumption when map exists."""
    passes: list[str] = []
    fails: list[str] = []
    warns: list[str] = []

    ctx_file = req_dir / "000-context-pack.md"
    if not ctx_file.exists():
        return passes, fails, warns  # V1 handles missing file

    ctx_text = ctx_file.read_text(encoding="utf-8")
    status_match = RE_MAP_STATUS.search(ctx_text)
    if not status_match:
        warns.append(
            "V22: 000-context-pack.md missing 项目地图状态 field — "
            "cannot tell whether Pathfinder map was checked"
        )
        return passes, fails, warns

    status = status_match.group(1).strip()
    if any(marker in status for marker in NO_MAP_MARKERS):
        passes.append("V22: Pathfinder map absent; consumption record not required")
        return passes, fails, warns

    section = _extract_section_text(
        ctx_text,
        ["Pathfinder 地图消费记录", "地图消费记录"],
    )
    if not section:
        fails.append(
            "V22: 项目地图状态 indicates a map exists, but "
            "000-context-pack.md has no Pathfinder 地图消费记录 section"
        )
        return passes, fails, warns

    rows: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped or "地图事实" in stripped or "[地图" in stripped:
            continue
        if any(action in stripped for action in MAP_CONSUMPTION_ACTIONS):
            rows.append(stripped)

    if not rows:
        fails.append(
            "V22: Pathfinder 地图消费记录 has no substantive rows — "
            "record at least one map fact as 采用 / 重新验证 / 未采用 / 过期"
        )
    else:
        passes.append(
            f"V22: Pathfinder map consumption record has {len(rows)} auditable row(s)"
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

    # V1: File completeness (includes _active-state.md FAIL)
    p, f, w = check_file_completeness(req_dir, mode)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V2: Requirements boundary
    p, w = check_requirements_boundary(req_dir)
    all_passes.extend(p)
    all_warns.extend(w)

    # V3: Method name verification
    p, f, w = check_method_verification(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V4: Grading decision table
    p, w = check_decision_table(req_dir, mode)
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

    # V8: Style rules check
    p, f, w = check_style_rules(req_dir, repo_root)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V9: Grading table fact consistency
    p, f, w = check_grading_facts_consistency(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V10: Global impact check table (full mode only)
    p, f, w = check_global_impact_table(req_dir, mode)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V11: Light mode key-path check
    p, f, w = check_light_keypath(req_dir, mode)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V12: Phase 3 process check
    p, f, w = check_phase3_process(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V13: Phase 4/5 split gate
    p, f, w = check_phase4_phase5_split(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V14: Phase 5 preflight gate
    p, f, w = check_phase5_preflight(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V15: Phase 5 record/state gate
    p, f, w = check_phase5_record_state(req_dir, repo_root)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V16: Active-state Step consistency
    p, f, w = check_active_state_consistency(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V17: Task acceptance smoke check
    p, f, w = check_task_acceptance_smoke(repo_root)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V18: Verification evidence
    p, f, w = check_verification_evidence(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V19: High-risk DDL crosscheck
    p, f, w = check_high_risk_ddl_crosscheck(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V20: Step confirmation field
    p, f, w = check_step_confirmation(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V21: Provenance tags
    p, f, w = check_source_tags(req_dir)
    all_passes.extend(p)
    all_fails.extend(f)
    all_warns.extend(w)

    # V22: Pathfinder map consumption record
    p, f, w = check_pathfinder_consumption(req_dir)
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
