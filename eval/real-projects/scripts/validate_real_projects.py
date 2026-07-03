#!/usr/bin/env python3
"""Validate the real-project eval matrix."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PROJECTS_PATH = BASE / "projects.json"
CASES_DIR = BASE / "cases"
REQUIRED_KINDS = {"pathfinder", "impact-light", "impact-full", "negative"}
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
CASE_ID_RE = re.compile(r"^[a-z0-9-]+$")


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def main() -> int:
    errors: list[str] = []

    if not PROJECTS_PATH.exists():
        errors.append(f"missing {PROJECTS_PATH}")
        return report(errors)

    projects_doc = load_json(PROJECTS_PATH)
    if not isinstance(projects_doc, dict):
        errors.append("projects.json must be an object")
        return report(errors)

    projects = as_list(projects_doc.get("projects"))
    project_ids: set[str] = set()
    project_phase: dict[str, int] = {}

    for idx, project in enumerate(projects):
        if not isinstance(project, dict):
            errors.append(f"projects[{idx}] must be an object")
            continue

        project_id = project.get("id")
        if not isinstance(project_id, str) or not project_id:
            errors.append(f"projects[{idx}] missing id")
            continue
        if project_id in project_ids:
            errors.append(f"duplicate project id: {project_id}")
        project_ids.add(project_id)

        repo_url = project.get("repo_url")
        if not isinstance(repo_url, str) or not repo_url.startswith("https://github.com/"):
            errors.append(f"{project_id}: repo_url must be a GitHub https URL")

        commit = project.get("commit")
        if not isinstance(commit, str) or not COMMIT_RE.match(commit):
            errors.append(f"{project_id}: commit must be a 40-char lowercase sha")

        phase = project.get("phase")
        if not isinstance(phase, int) or phase < 1:
            errors.append(f"{project_id}: phase must be a positive integer")
        else:
            project_phase[project_id] = phase

        for field in ("label", "category", "checkout_dir", "why"):
            if not isinstance(project.get(field), str) or not project.get(field):
                errors.append(f"{project_id}: missing {field}")

        for field in ("stack", "focus"):
            values = as_list(project.get(field))
            if not values or not all(isinstance(item, str) and item for item in values):
                errors.append(f"{project_id}: {field} must be a non-empty string array")

    phase1_ids = set(as_list(projects_doc.get("phase1_project_ids")))
    unknown_phase1 = phase1_ids - project_ids
    if unknown_phase1:
        errors.append(f"phase1_project_ids reference unknown projects: {sorted(unknown_phase1)}")
    if len(phase1_ids) < 3:
        errors.append("phase1_project_ids must include at least 3 projects")

    if not CASES_DIR.exists():
        errors.append(f"missing {CASES_DIR}")
        return report(errors)

    seen_case_ids: set[str] = set()
    cases_by_project: dict[str, set[str]] = {project_id: set() for project_id in project_ids}
    case_count = 0

    for path in sorted(CASES_DIR.glob("*.json")):
        doc = load_json(path)
        if not isinstance(doc, dict):
            errors.append(f"{path.name}: must be an object")
            continue

        project_id = doc.get("project_id")
        if not isinstance(project_id, str) or project_id not in project_ids:
            errors.append(f"{path.name}: unknown project_id {project_id!r}")
            continue

        cases = as_list(doc.get("cases"))
        if not cases:
            errors.append(f"{path.name}: cases must be non-empty")
            continue

        for idx, case in enumerate(cases):
            case_count += 1
            prefix = f"{path.name} cases[{idx}]"
            if not isinstance(case, dict):
                errors.append(f"{prefix}: must be an object")
                continue

            case_id = case.get("id")
            if not isinstance(case_id, str) or not CASE_ID_RE.match(case_id):
                errors.append(f"{prefix}: invalid id {case_id!r}")
            elif case_id in seen_case_ids:
                errors.append(f"{prefix}: duplicate id {case_id}")
            else:
                seen_case_ids.add(case_id)

            kind = case.get("kind")
            if kind not in REQUIRED_KINDS:
                errors.append(f"{prefix}: invalid kind {kind!r}")
            else:
                cases_by_project[project_id].add(kind)

            skill = case.get("skill")
            if kind == "negative":
                if skill not in {"impact", "pathfinder"}:
                    errors.append(f"{prefix}: negative case skill must be impact or pathfinder")
            else:
                expected_skill = "pathfinder" if kind == "pathfinder" else "impact"
                if skill != expected_skill:
                    errors.append(f"{prefix}: skill {skill!r} does not match kind {kind!r}")

            phase = case.get("phase")
            if phase != project_phase.get(project_id):
                errors.append(f"{prefix}: phase must match project phase {project_phase.get(project_id)}")

            run_mode = case.get("run_mode")
            if run_mode not in {"analysis-only", "isolated-copy", "non-git-copy"}:
                errors.append(f"{prefix}: invalid run_mode {run_mode!r}")

            prompt = case.get("prompt")
            if not isinstance(prompt, str) or len(prompt.strip()) < 20:
                errors.append(f"{prefix}: prompt is too short")

            expected = case.get("expected")
            if not isinstance(expected, dict):
                errors.append(f"{prefix}: expected must be an object")
                continue

            for field in ("must_cover", "must_not_claim", "quality_checks"):
                values = as_list(expected.get(field))
                if not values or not all(isinstance(item, str) and item for item in values):
                    errors.append(f"{prefix}: expected.{field} must be a non-empty string array")

    for project_id, kinds in cases_by_project.items():
        missing = REQUIRED_KINDS - kinds
        if missing:
            errors.append(f"{project_id}: missing case kinds {sorted(missing)}")

    if errors:
        return report(errors)

    print(f"OK: {len(project_ids)} projects, {case_count} cases")
    return 0


def report(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
