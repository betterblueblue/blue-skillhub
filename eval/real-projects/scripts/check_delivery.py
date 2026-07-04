#!/usr/bin/env python3
"""Check a Phase 5 delivery fixture against an acceptance block."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = BASE / "delivery-matrix.json"
ALLOWED_CONTENT_SCOPES = {"expected", "repo"}


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
    for scenario in doc.get("scenarios", []):
        if isinstance(scenario, dict) and scenario.get("id") == scenario_id:
            acceptance = scenario.get("acceptance")
            if not isinstance(acceptance, dict):
                raise ValueError(f"scenario {scenario_id} has no acceptance block")
            return acceptance
    raise ValueError(f"scenario not found: {scenario_id}")


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
                    add_check(checks, "FAIL", "validator", "Validator needs --requirement-dir", command)
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
        else:
            acceptance = load_acceptance_from_matrix(Path(args.matrix), args.scenario)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    report = check_acceptance(fixture, acceptance, args.run_validators, args.requirement_dir, args.validator_timeout)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
