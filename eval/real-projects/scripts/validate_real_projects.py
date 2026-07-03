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
DELIVERY_MATRIX_PATH = BASE / "delivery-matrix.json"
REQUIRED_KINDS = {"pathfinder", "impact-light", "impact-full", "negative"}
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
CASE_ID_RE = re.compile(r"^[a-z0-9-]+$")
CASE_SIZES = {"S", "M", "L", "NEG"}
CASE_DELIVERY_MODES = {
    "analysis-only",
    "phase4-docs",
    "phase5-delivery",
    "negative-gate",
    "pathfinder-map",
}
DELIVERY_SCENARIO_ID_RE = re.compile(r"^D[0-9]+-[a-z0-9-]+$")
DELIVERY_COMPLEXITIES = {"S", "M", "L", "NEG"}
DELIVERY_STAGES = {
    "pathfinder-map",
    "impact-analysis",
    "impact-phase4",
    "impact-phase5",
    "negative-gate",
}
DELIVERY_FIXTURE_MODES = {
    "read-only-original",
    "isolated-copy",
    "non-git-copy",
}


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
    project_category: dict[str, str] = {}

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
        category = project.get("category")
        if isinstance(category, str) and category:
            project_category[project_id] = category

        for field in ("stack", "focus"):
            values = as_list(project.get(field))
            if not values or not all(isinstance(item, str) and item for item in values):
                errors.append(f"{project_id}: {field} must be a non-empty string array")
        delivery_fit = as_list(project.get("delivery_fit"))
        if not delivery_fit or not all(item in CASE_SIZES for item in delivery_fit):
            errors.append(f"{project_id}: delivery_fit must be a non-empty array of {sorted(CASE_SIZES)}")

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
    case_index: dict[str, dict[str, str]] = {}
    cases_by_project: dict[str, set[str]] = {project_id: set() for project_id in project_ids}
    case_sizes: set[str] = set()
    case_delivery_modes: set[str] = set()
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
                case_index[case_id] = {
                    "project_id": project_id,
                    "kind": str(case.get("kind")),
                    "skill": str(case.get("skill")),
                    "delivery_mode": str(case.get("delivery_mode")),
                    "size": str(case.get("size")),
                }

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

            size = case.get("size")
            if size not in CASE_SIZES:
                errors.append(f"{prefix}: invalid size {size!r}")
            else:
                case_sizes.add(size)

            delivery_mode = case.get("delivery_mode")
            if delivery_mode not in CASE_DELIVERY_MODES:
                errors.append(f"{prefix}: invalid delivery_mode {delivery_mode!r}")
            else:
                case_delivery_modes.add(delivery_mode)

            prompt = case.get("prompt")
            if not isinstance(prompt, str) or len(prompt.strip()) < 20:
                errors.append(f"{prefix}: prompt is too short")

            for field in ("expected_artifacts", "verification"):
                values = as_list(case.get(field))
                if not values or not all(isinstance(item, str) and item for item in values):
                    errors.append(f"{prefix}: {field} must be a non-empty string array")

            for field in ("blocking_questions", "rollback_or_compat"):
                values = case.get(field)
                if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
                    errors.append(f"{prefix}: {field} must be a string array")

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

    missing_case_sizes = CASE_SIZES - case_sizes
    if missing_case_sizes:
        errors.append(f"cases must cover sizes {sorted(missing_case_sizes)}")
    if "phase5-delivery" not in case_delivery_modes:
        errors.append("at least one case must use delivery_mode=phase5-delivery")

    validate_delivery_matrix(errors, case_index, project_category)

    if errors:
        return report(errors)

    print(f"OK: {len(project_ids)} projects, {case_count} cases, delivery matrix checked")
    return 0


def validate_delivery_matrix(
    errors: list[str],
    case_index: dict[str, dict[str, str]],
    project_category: dict[str, str],
) -> None:
    if not DELIVERY_MATRIX_PATH.exists():
        errors.append(f"missing {DELIVERY_MATRIX_PATH}")
        return

    doc = load_json(DELIVERY_MATRIX_PATH)
    if not isinstance(doc, dict):
        errors.append("delivery-matrix.json must be an object")
        return

    if doc.get("schema_version") != 1:
        errors.append("delivery-matrix.json: schema_version must be 1")

    runners = as_list(doc.get("runners"))
    runner_ids: set[str] = set()
    for idx, runner in enumerate(runners):
        prefix = f"delivery runners[{idx}]"
        if not isinstance(runner, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        runner_id = runner.get("id")
        if not isinstance(runner_id, str) or not CASE_ID_RE.match(runner_id):
            errors.append(f"{prefix}: invalid id {runner_id!r}")
            continue
        runner_ids.add(runner_id)
        for field in ("surface", "model", "invocation"):
            if not isinstance(runner.get(field), str) or not runner.get(field):
                errors.append(f"{prefix}: missing {field}")
    if len(runner_ids) < 2:
        errors.append("delivery-matrix.json: at least two runners are required")

    scenarios = as_list(doc.get("scenarios"))
    if len(scenarios) < 8:
        errors.append("delivery-matrix.json: at least 8 scenarios are required")

    scenario_ids: set[str] = set()
    scenario_projects: set[str] = set()
    scenario_categories: set[str] = set()
    scenario_complexities: set[str] = set()
    scenario_stages: set[str] = set()
    scenario_skills: set[str] = set()

    for idx, scenario in enumerate(scenarios):
        prefix = f"delivery scenarios[{idx}]"
        if not isinstance(scenario, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not DELIVERY_SCENARIO_ID_RE.match(scenario_id):
            errors.append(f"{prefix}: invalid id {scenario_id!r}")
        elif scenario_id in scenario_ids:
            errors.append(f"{prefix}: duplicate id {scenario_id}")
        else:
            scenario_ids.add(scenario_id)

        case_id = scenario.get("case_id")
        case_meta = case_index.get(case_id) if isinstance(case_id, str) else None
        if case_meta is None:
            errors.append(f"{prefix}: unknown case_id {case_id!r}")
        else:
            project_id = case_meta["project_id"]
            scenario_projects.add(project_id)
            category = project_category.get(project_id)
            if category:
                scenario_categories.add(category)
            scenario_skills.add(case_meta["skill"])

        complexity = scenario.get("complexity")
        if complexity not in DELIVERY_COMPLEXITIES:
            errors.append(f"{prefix}: invalid complexity {complexity!r}")
        else:
            scenario_complexities.add(complexity)

        stage = scenario.get("stage")
        if stage not in DELIVERY_STAGES:
            errors.append(f"{prefix}: invalid stage {stage!r}")
        else:
            scenario_stages.add(stage)
            if case_meta is not None:
                if stage == "pathfinder-map" and case_meta["skill"] != "pathfinder":
                    errors.append(f"{prefix}: pathfinder-map must reference a pathfinder case")
                if stage == "impact-phase5" and case_meta["delivery_mode"] != "phase5-delivery":
                    errors.append(f"{prefix}: impact-phase5 must reference delivery_mode=phase5-delivery")
                if stage == "negative-gate" and case_meta["kind"] != "negative":
                    errors.append(f"{prefix}: negative-gate must reference a negative case")

        fixture_mode = scenario.get("fixture_mode")
        if fixture_mode not in DELIVERY_FIXTURE_MODES:
            errors.append(f"{prefix}: invalid fixture_mode {fixture_mode!r}")

        runner_scope = as_list(scenario.get("runner_scope"))
        if not runner_scope or not all(isinstance(item, str) and item in runner_ids for item in runner_scope):
            errors.append(f"{prefix}: runner_scope must reference runner ids")

        for field in ("success_target", "failure_signals", "repair_loop"):
            values = as_list(scenario.get(field))
            if not values or not all(isinstance(item, str) and item for item in values):
                errors.append(f"{prefix}: {field} must be a non-empty string array")

        acceptance = scenario.get("acceptance")
        if stage == "impact-phase5":
            if not isinstance(acceptance, dict):
                errors.append(f"{prefix}: impact-phase5 requires acceptance")
            else:
                for field in ("expected_changed_files", "forbidden_changed_files", "validators"):
                    values = as_list(acceptance.get(field))
                    if not values or not all(isinstance(item, str) and item for item in values):
                        errors.append(f"{prefix}: acceptance.{field} must be a non-empty string array")

    missing_complexities = DELIVERY_COMPLEXITIES - scenario_complexities
    if missing_complexities:
        errors.append(f"delivery-matrix.json: missing complexities {sorted(missing_complexities)}")

    missing_stages = DELIVERY_STAGES - scenario_stages
    if missing_stages:
        errors.append(f"delivery-matrix.json: missing stages {sorted(missing_stages)}")

    if len(scenario_projects) < 5:
        errors.append("delivery-matrix.json: scenarios must cover all 5 real projects")
    if len(scenario_categories) < 5:
        errors.append("delivery-matrix.json: scenarios must cover 5 project categories")
    if scenario_skills != {"pathfinder", "impact"}:
        errors.append("delivery-matrix.json: scenarios must cover both pathfinder and impact")

    runner_plan = doc.get("runner_plan")
    if not isinstance(runner_plan, dict):
        errors.append("delivery-matrix.json: runner_plan must be an object")
        return

    for runner_id in runner_ids:
        planned = as_list(runner_plan.get(runner_id))
        if len(planned) < 5:
            errors.append(f"delivery-matrix.json: runner_plan.{runner_id} must include at least 5 scenarios")
        unknown = [item for item in planned if item not in scenario_ids]
        if unknown:
            errors.append(f"delivery-matrix.json: runner_plan.{runner_id} references unknown scenarios {unknown}")
        planned_stages = {
            scenario.get("stage")
            for scenario in scenarios
            if isinstance(scenario, dict) and scenario.get("id") in planned
        }
        if "impact-phase5" not in planned_stages:
            errors.append(f"delivery-matrix.json: runner_plan.{runner_id} must include impact-phase5")


def report(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
