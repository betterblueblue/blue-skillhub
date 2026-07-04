#!/usr/bin/env python3
"""Check a real-project eval fixture against delivery or analysis gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = BASE / "delivery-matrix.json"
CASES_DIR = BASE / "cases"
ALLOWED_CONTENT_SCOPES = {"expected", "repo"}
PHASE4_DOCS_BY_KIND = {
    "impact-light": ["000-context-pack.md", "040-light.md", "_active-state.md"],
    "impact-full": [
        "000-context-pack.md",
        "010-requirements.md",
        "020-design.md",
        "030-implementation.md",
        "_active-state.md",
    ],
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_path(path: str) -> str:
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def is_change_impact(path: str) -> bool:
    path = normalize_path(path)
    return path == "change-impact" or path.startswith("change-impact/")


def as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def load_acceptance_from_matrix(matrix_path: Path, scenario_id: str) -> dict[str, Any]:
    doc = load_json(matrix_path)
    if not isinstance(doc, dict):
        raise ValueError(f"{matrix_path} must be a JSON object")
    scenario = find_scenario(doc, scenario_id)
    acceptance = scenario.get("acceptance")
    if not isinstance(acceptance, dict):
        raise ValueError(f"scenario {scenario_id} has no acceptance block")
    return acceptance


def find_scenario(matrix_doc: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    for scenario in matrix_doc.get("scenarios", []):
        if isinstance(scenario, dict) and scenario.get("id") == scenario_id:
            return scenario
    raise ValueError(f"scenario not found: {scenario_id}")


def load_case_index(cases_dir: Path = CASES_DIR) -> dict[str, dict[str, str]]:
    cases: dict[str, dict[str, str]] = {}
    for path in sorted(cases_dir.glob("*.json")):
        doc = load_json(path)
        if not isinstance(doc, dict):
            continue
        for case in doc.get("cases", []):
            if not isinstance(case, dict):
                continue
            case_id = case.get("id")
            if isinstance(case_id, str):
                cases[case_id] = {
                    "kind": str(case.get("kind", "")),
                    "skill": str(case.get("skill", "")),
                    "delivery_mode": str(case.get("delivery_mode", "")),
                }
    return cases


def parse_git_status_z(raw: bytes) -> dict[str, str]:
    parts = raw.split(b"\0")
    statuses: dict[str, str] = {}
    i = 0
    while i < len(parts):
        entry = parts[i]
        if not entry:
            i += 1
            continue
        text = entry.decode("utf-8", errors="replace")
        if len(text) < 4:
            i += 1
            continue
        status = text[:2]
        path = text[3:]
        statuses[normalize_path(path)] = status
        i += 1
        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            i += 1
    return statuses


def git_status(fixture: Path) -> tuple[dict[str, str], str | None]:
    result = subprocess.run(
        ["git", "-C", str(fixture), "status", "--porcelain=v1", "--untracked-files=all", "-z"],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return {}, stderr or "git status failed"
    statuses = {
        path: status
        for path, status in parse_git_status_z(result.stdout).items()
        if not is_change_impact(path)
    }
    return statuses, None


def changed_files(fixture: Path) -> tuple[list[str], dict[str, str], str | None]:
    statuses, error = git_status(fixture)
    return sorted(statuses), statuses, error


def git_ls_files(fixture: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(fixture), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        return []
    paths = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = normalize_path(raw.decode("utf-8", errors="replace"))
        if not is_change_impact(path):
            paths.append(path)
    return sorted(set(paths))


def git_diff_numstat(fixture: Path) -> dict[str, tuple[int, int]]:
    """Return {path: (insertions, deletions)} for tracked file changes vs HEAD.

    Excludes change-impact/ paths.  Untracked files are not included.
    """
    result = subprocess.run(
        ["git", "-C", str(fixture), "diff", "HEAD", "--numstat", "--no-renames"],
        capture_output=True,
        timeout=30,
    )
    stats: dict[str, tuple[int, int]] = {}
    for line in result.stdout.decode("utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        ins_s, del_s, path = parts
        try:
            ins = int(ins_s)
            dels = int(del_s)
        except ValueError:
            continue  # binary file marked as '-'
        path = normalize_path(path)
        if not is_change_impact(path):
            stats[path] = (ins, dels)
    return stats


def read_text(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def resolve_requirement_dir(fixture: Path, requirement_dir: str) -> Path:
    path = Path(requirement_dir)
    if path.is_absolute():
        return path
    return fixture / path


def phase4_requirement_candidates(fixture: Path) -> list[Path]:
    change_impact = fixture / "change-impact"
    if not change_impact.is_dir():
        return []
    return sorted(path for path in change_impact.iterdir() if path.is_dir())


def missing_phase4_docs(requirement_path: Path, required_docs: list[str]) -> list[str]:
    return [name for name in required_docs if not (requirement_path / name).is_file()]


def relative_to_fixture(fixture: Path, path: Path) -> str:
    try:
        return normalize_path(str(path.relative_to(fixture)))
    except ValueError:
        return str(path)


def scoped_files(fixture: Path, acceptance: dict[str, Any]) -> list[str]:
    scope = acceptance.get("content_scope", "expected")
    if scope == "repo":
        return git_ls_files(fixture)
    return as_string_list(acceptance.get("expected_changed_files"))


def add_check(checks: list[dict[str, Any]], level: str, code: str, message: str, evidence: Any = None) -> None:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    checks.append(item)


def check_acceptance(
    fixture: Path,
    acceptance: dict[str, Any],
    run_validators: bool,
    requirement_dir: str | None,
    validator_timeout: int = 600,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    expected = {normalize_path(path) for path in as_string_list(acceptance.get("expected_changed_files"))}
    expected_deleted = {normalize_path(path) for path in as_string_list(acceptance.get("expected_deleted_files"))}
    forbidden = {normalize_path(path) for path in as_string_list(acceptance.get("forbidden_changed_files"))}

    changed, statuses, status_error = changed_files(fixture)
    changed_set = set(changed)
    if status_error:
        add_check(checks, "FAIL", "git-status", "Unable to inspect fixture git status", status_error)
    else:
        add_check(checks, "PASS", "git-status", "Fixture git status inspected", changed)

    missing = sorted(expected - changed_set)
    if missing:
        add_check(checks, "FAIL", "expected-changed-files", "Expected files were not changed", missing)
    else:
        add_check(checks, "PASS", "expected-changed-files", "All expected files were changed", sorted(expected))

    if expected_deleted:
        not_deleted = sorted(path for path in expected_deleted if "D" not in statuses.get(path, ""))
        if not_deleted:
            add_check(checks, "FAIL", "expected-deleted-files", "Expected files were not deleted", not_deleted)
        else:
            add_check(checks, "PASS", "expected-deleted-files", "All expected files were deleted", sorted(expected_deleted))

    touched_forbidden = sorted(forbidden & changed_set)
    if touched_forbidden:
        add_check(checks, "FAIL", "forbidden-changed-files", "Forbidden files were changed", touched_forbidden)
    else:
        add_check(checks, "PASS", "forbidden-changed-files", "No forbidden files were changed", sorted(forbidden))

    unexpected = sorted(changed_set - expected - forbidden - expected_deleted)
    if unexpected:
        add_check(checks, "WARN", "unexpected-changed-files", "Changed files are outside expected/forbidden lists", unexpected)

    scope = acceptance.get("content_scope", "expected")
    files = scoped_files(fixture, acceptance)
    if scope not in ALLOWED_CONTENT_SCOPES:
        add_check(checks, "FAIL", "content-scope", "Invalid content_scope", scope)
        files = []

    file_texts: dict[str, str] = {}
    for rel in files:
        text = read_text(fixture / rel)
        if text is not None:
            file_texts[normalize_path(rel)] = text

    for needle in as_string_list(acceptance.get("must_contain")):
        hits = [path for path, text in file_texts.items() if needle in text]
        if hits:
            add_check(checks, "PASS", "must-contain", f"Required text found: {needle}", hits)
        else:
            add_check(checks, "FAIL", "must-contain", f"Required text not found: {needle}", files)

    for needle in as_string_list(acceptance.get("must_not_contain")):
        hits = [path for path, text in file_texts.items() if needle in text]
        if hits:
            add_check(checks, "FAIL", "must-not-contain", f"Forbidden text found: {needle}", hits)
        else:
            add_check(checks, "PASS", "must-not-contain", f"Forbidden text absent: {needle}", files)

    if run_validators:
        for command in as_string_list(acceptance.get("validators")):
            if "<requirement-dir>" in command:
                if not requirement_dir:
                    add_check(
                        checks,
                        "FAIL",
                        "validator_missing_artifacts",
                        "Impact validator needs a requirement directory; no --requirement-dir was provided",
                        {
                            "command": command,
                            "hint": "Phase 5 delivery likely skipped impact artifacts such as change-impact/<request>/000/040/_active-state/060/090.",
                        },
                    )
                    continue
                requirement_path = resolve_requirement_dir(fixture, requirement_dir)
                if not requirement_path.is_dir():
                    add_check(
                        checks,
                        "FAIL",
                        "validator_missing_artifacts",
                        "Impact requirement directory does not exist",
                        {
                            "command": command,
                            "requirement_dir": requirement_dir,
                            "resolved_path": str(requirement_path),
                        },
                    )
                    continue
                command = command.replace("<requirement-dir>", requirement_dir)
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=fixture,
                    capture_output=True,
                    text=True,
                    timeout=validator_timeout,
                )
            except subprocess.TimeoutExpired:
                add_check(
                    checks,
                    "FAIL",
                    "validator",
                    f"Validator timed out after {validator_timeout}s: {command}",
                    {"command": command, "timeout": validator_timeout},
                )
                continue
            evidence = {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            }
            if result.returncode == 0:
                add_check(checks, "PASS", "validator", f"Validator passed: {command}", evidence)
            else:
                add_check(checks, "FAIL", "validator", f"Validator failed: {command}", evidence)

    # E-005: diff overflow check (WARN only, never FAIL)
    max_total = acceptance.get("max_total_diff_lines")
    diff_stats = git_diff_numstat(fixture)
    total_diff_lines = sum(ins + dels for ins, dels in diff_stats.values())
    diff_evidence = {
        "total_changed_lines": total_diff_lines,
        "per_file": {p: {"insertions": i, "deletions": d} for p, (i, d) in sorted(diff_stats.items())},
    }
    if max_total is not None:
        diff_evidence["max_total_diff_lines"] = max_total
        if total_diff_lines > max_total:
            add_check(
                checks,
                "WARN",
                "diff-overflow",
                f"Total diff lines ({total_diff_lines}) exceed max_total_diff_lines ({max_total})",
                diff_evidence,
            )
        else:
            add_check(
                checks,
                "PASS",
                "diff-overflow",
                f"Total diff lines ({total_diff_lines}) within limit ({max_total})",
                diff_evidence,
            )
    else:
        add_check(
            checks,
            "PASS",
            "diff-stats",
            f"Total diff lines: {total_diff_lines}",
            diff_evidence,
        )

    has_fail = any(check["level"] == "FAIL" for check in checks)
    has_warn = any(check["level"] == "WARN" for check in checks)
    status = "FAIL" if has_fail else "PASS-WARN" if has_warn else "PASS"
    return {
        "status": status,
        "fixture": str(fixture),
        "changed_files": changed,
        "content_scope": scope,
        "checks": checks,
    }


def check_analysis_gate(
    fixture: Path,
    scenario: dict[str, Any],
    case_meta: dict[str, str],
    run_record: str | None,
    requirement_dir: str | None,
) -> dict[str, Any]:
    """Check non-Phase-5 impact analysis/phase4 scenarios.

    This is intentionally narrow: it catches the D18-style failure where an
    analysis-only run writes source files or skips the expected artifacts.
    """
    checks: list[dict[str, Any]] = []
    stage = str(scenario.get("stage", ""))
    case_kind = case_meta.get("kind", "")

    changed, _, status_error = changed_files(fixture)
    if status_error:
        add_check(checks, "FAIL", "git-status", "Unable to inspect fixture git status", status_error)
    else:
        add_check(checks, "PASS", "git-status", "Fixture git status inspected", changed)

    # --- impact-phase4 no-source-diff gate ---
    # For impact-phase4 stage, source code changes are forbidden by default.
    # A scenario can opt in to Phase 5 by setting "allow_phase5": true.
    allow_phase5 = bool(scenario.get("allow_phase5", False))
    is_phase4 = stage == "impact-phase4"

    if changed:
        if is_phase4 and not allow_phase5:
            add_check(
                checks,
                "FAIL",
                "analysis-source-diff",
                "impact-phase4 scenario must not change source files (allow_phase5 not set)",
                {
                    "changed_files": changed,
                    "repair": "还原源码改动 (git checkout .)，只保留 change-impact/ 下的分析文档。如需允许实施，在 delivery-matrix.json 中为该场景添加 \"allow_phase5\": true。",
                },
            )
        else:
            add_check(
                checks,
                "FAIL",
                "analysis-source-diff",
                "Analysis scenario changed files outside change-impact",
                changed,
            )
    else:
        add_check(
            checks,
            "PASS",
            "analysis-source-diff",
            "No files outside change-impact were changed",
            changed,
        )

    if not run_record:
        add_check(
            checks,
            "FAIL",
            "run-record",
            "No --run-record was provided for analysis scenario",
            None,
        )
    else:
        run_record_path = Path(run_record)
        if not run_record_path.is_absolute():
            run_record_path = run_record_path.resolve()
        if run_record_path.is_file() and run_record_path.stat().st_size > 0:
            add_check(checks, "PASS", "run-record", "Run record exists", str(run_record_path))
        else:
            add_check(checks, "FAIL", "run-record", "Run record is missing or empty", str(run_record_path))

    required_docs = PHASE4_DOCS_BY_KIND.get(case_kind, []) if stage == "impact-phase4" else []
    if required_docs:
        if not requirement_dir:
            candidates = phase4_requirement_candidates(fixture)
            complete = [path for path in candidates if not missing_phase4_docs(path, required_docs)]
            if len(complete) == 1:
                requirement_path = complete[0]
                add_check(
                    checks,
                    "PASS",
                    "phase4-artifacts",
                    "Required Phase 4 documents exist",
                    {
                        "requirement_dir": relative_to_fixture(fixture, requirement_path),
                        "resolved_path": str(requirement_path),
                        "files": required_docs,
                        "auto_detected": True,
                    },
                )
            elif len(complete) > 1:
                add_check(
                    checks,
                    "FAIL",
                    "phase4-artifacts",
                    "Multiple complete Phase 4 directories found; pass --requirement-dir",
                    {
                        "required_files": required_docs,
                        "complete_candidates": [relative_to_fixture(fixture, path) for path in complete],
                    },
                )
            else:
                add_check(
                    checks,
                    "FAIL",
                    "phase4-artifacts",
                    "Required Phase 4 documents are missing",
                    {
                        "required_files": required_docs,
                        "candidates": [relative_to_fixture(fixture, path) for path in candidates],
                        "missing_by_candidate": {
                            relative_to_fixture(fixture, path): missing_phase4_docs(path, required_docs)
                            for path in candidates
                        },
                        "hint": "Pass --requirement-dir when the runner used a non-standard directory, or rerun impact so it writes the standard Phase 4 documents.",
                    },
                )
        else:
            requirement_path = resolve_requirement_dir(fixture, requirement_dir)
            missing = missing_phase4_docs(requirement_path, required_docs)
            if missing:
                add_check(
                    checks,
                    "FAIL",
                    "phase4-artifacts",
                    "Required Phase 4 documents are missing",
                    {
                        "requirement_dir": requirement_dir,
                        "resolved_path": str(requirement_path),
                        "missing": missing,
                    },
                )
            else:
                add_check(
                    checks,
                    "PASS",
                    "phase4-artifacts",
                    "Required Phase 4 documents exist",
                    {
                        "requirement_dir": requirement_dir,
                        "resolved_path": str(requirement_path),
                        "files": required_docs,
                    },
                )
    elif stage in {"impact-analysis", "negative-gate"}:
        add_check(checks, "PASS", "phase4-artifacts", "Phase 4 documents are not required for this stage", stage)
    else:
        add_check(checks, "WARN", "scenario-stage", "No analysis gate is defined for this stage", stage)

    has_fail = any(check["level"] == "FAIL" for check in checks)
    has_warn = any(check["level"] == "WARN" for check in checks)
    status = "FAIL" if has_fail else "PASS-WARN" if has_warn else "PASS"
    return {
        "status": status,
        "fixture": str(fixture),
        "scenario_id": scenario.get("id"),
        "stage": stage,
        "case_kind": case_kind,
        "changed_files": changed,
        "checks": checks,
    }


def print_text_report(report: dict[str, Any]) -> None:
    for check in report["checks"]:
        print(f"{check['level']}: {check['code']}: {check['message']}")
        if "evidence" in check:
            print(f"  evidence: {check['evidence']}")
    print()
    print(f"SUMMARY: {report['status']} ({len(report['checks'])} checks)")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Path to the isolated delivery fixture")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--scenario", help="Scenario id in delivery-matrix.json, e.g. D4-frontend-dashboard-phase5")
    source.add_argument("--acceptance", help="Path to an acceptance JSON object")
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX), help="Path to delivery-matrix.json")
    parser.add_argument("--requirement-dir", help="Requirement directory used to replace <requirement-dir>")
    parser.add_argument("--run-record", help="Run README used by analysis/phase4 scenario checks")
    parser.add_argument("--run-validators", action="store_true", help="Run acceptance.validators commands")
    parser.add_argument(
        "--validator-timeout",
        type=int,
        default=600,
        help="Per-command timeout in seconds for acceptance.validators (default: 600)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    fixture = Path(args.fixture).resolve()
    if not fixture.exists():
        print(f"ERROR: fixture does not exist: {fixture}", file=sys.stderr)
        return 1

    try:
        if args.acceptance:
            acceptance = load_json(Path(args.acceptance))
            if not isinstance(acceptance, dict):
                raise ValueError("--acceptance must point to a JSON object")
            report = check_acceptance(
                fixture,
                acceptance,
                args.run_validators,
                args.requirement_dir,
                args.validator_timeout,
            )
        else:
            matrix_doc = load_json(Path(args.matrix))
            if not isinstance(matrix_doc, dict):
                raise ValueError(f"{args.matrix} must be a JSON object")
            scenario = find_scenario(matrix_doc, args.scenario)
            acceptance = scenario.get("acceptance")
            if isinstance(acceptance, dict):
                report = check_acceptance(
                    fixture,
                    acceptance,
                    args.run_validators,
                    args.requirement_dir,
                    args.validator_timeout,
                )
            else:
                case_id = scenario.get("case_id")
                case_meta = load_case_index().get(case_id, {}) if isinstance(case_id, str) else {}
                report = check_analysis_gate(
                    fixture,
                    scenario,
                    case_meta,
                    args.run_record,
                    args.requirement_dir,
                )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
