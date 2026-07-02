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


def check_crosscut_table(req_dir: Path, mode: str) -> tuple[list[str], list[str], list[str]]:
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
    p, f, w = check_crosscut_table(req_dir, mode)
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
