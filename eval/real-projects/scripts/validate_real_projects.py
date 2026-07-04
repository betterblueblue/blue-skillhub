#!/usr/bin/env python3
"""Validate the real-project eval matrix."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE.parents[1]
PROJECTS_PATH = BASE / "projects.json"
CASES_DIR = BASE / "cases"
DELIVERY_MATRIX_PATH = BASE / "delivery-matrix.json"
DELIVERY_RESULTS_PATH = BASE / "delivery-results.json"
RUNS_ROOT = REPO_ROOT / "eval" / "runs" / "real-projects"
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
DELIVERY_RESULT_STATUSES = {
    "PASS",
    "PASS-WARN",
    "GATE-RECOVERED",
    "FAIL",
    "UNVERIFIED",
}
DELIVERY_COMPLETED_STATUSES = {"PASS", "PASS-WARN", "GATE-RECOVERED"}
ACCEPTANCE_FIELDS = {
    "expected_changed_files",
    "expected_deleted_files",
    "forbidden_changed_files",
    "validators",
    "must_contain",
    "must_not_contain",
    "content_scope",
}
REQUIRED_ACCEPTANCE_FIELDS = {"expected_changed_files", "forbidden_changed_files", "validators"}
ACCEPTANCE_CONTENT_SCOPES = {"expected", "repo"}
PHASE5_POLICIES = {
    "interactive-or-hooked",
    "subagent-unattended-stress-only",
}
PROMPT_ENV_FIELDS = {"工作目录", "非 Git 副本目录", "Skill", "输出归档"}
PROMPT_REQUIRED_ENV_FIELDS = {"工作目录", "Skill", "输出归档"}
PROMPT_HARNESS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"impact_validate\.py",
        r"check_delivery\.py",
        r"delivery-results\.json",
        r"expected_changed_files",
        r"forbidden_changed_files",
        r"--run-validators",
        r"确认\s*Step\s*\d*",
        r"只允许写",
        r"不得写文件",
        r"否则判",
        r"判失败",
        r"评分卡",
        r"判分方",
        r"监考",
        r"不要读取.*(旧|GPT|Composer|delivery-results)",
        r"旧\s*D\d+",
        r"GPT\s*地图",
        r"旧\s*Composer",
    )
]


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def validate_user_prompt(errors: list[str], prefix: str, prompt: str) -> None:
    for pattern in PROMPT_HARNESS_PATTERNS:
        match = pattern.search(prompt)
        if match:
            errors.append(f"{prefix}: prompt contains harness/judge wording {match.group(0)!r}")


def _prompt_field_name(line: str) -> str:
    separator = "：" if "：" in line else ":"
    return line.split(separator, 1)[0].strip()


def parse_launch_prompt_file(errors: list[str], path: Path) -> tuple[dict[str, str], str] | None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    non_empty = [line.strip() for line in lines if line.strip()]

    if not non_empty:
        errors.append(f"{rel}: prompt file is empty")
        return None
    if non_empty[0] != "[评测环境]":
        errors.append(f"{rel}: prompt must start with [评测环境]")
        return None

    try:
        env_idx = lines.index("[评测环境]")
        separator_idx = lines.index("---")
        user_idx = lines.index("[用户输入]")
    except ValueError:
        errors.append(f"{rel}: prompt must contain [评测环境], --- and [用户输入]")
        return None

    if not (env_idx == 0 and env_idx < separator_idx < user_idx):
        errors.append(f"{rel}: prompt sections must be [评测环境] -> --- -> [用户输入]")
        return None
    between_separator_and_user = [
        line.strip() for line in lines[separator_idx + 1 : user_idx] if line.strip()
    ]
    if between_separator_and_user:
        errors.append(f"{rel}: prompt must not add text between --- and [用户输入]")

    env_lines = [line.strip() for line in lines[env_idx + 1 : separator_idx] if line.strip()]
    env: dict[str, str] = {}
    seen_fields: set[str] = set()
    for line in env_lines:
        if "：" not in line and ":" not in line:
            errors.append(f"{rel}: environment line must be a key/value pair: {line!r}")
            continue
        field = _prompt_field_name(line)
        if field not in PROMPT_ENV_FIELDS:
            errors.append(f"{rel}: environment field {field!r} is not allowed")
        seen_fields.add(field)
        separator = "：" if "：" in line else ":"
        env[field] = line.split(separator, 1)[1].strip()

    missing_fields = sorted(PROMPT_REQUIRED_ENV_FIELDS - seen_fields)
    if missing_fields:
        errors.append(f"{rel}: environment is missing fields {missing_fields}")

    user_text = "\n".join(lines[user_idx + 1 :]).strip()
    if len(user_text) < 20:
        errors.append(f"{rel}: user input is too short")
    if any(line.strip().startswith("[") and line.strip().endswith("]") for line in lines[user_idx + 1 :]):
        errors.append(f"{rel}: prompt must not add sections after [用户输入]")
    validate_user_prompt(errors, rel, user_text)
    return env, user_text


def validate_launch_prompt_file(errors: list[str], path: Path) -> None:
    parse_launch_prompt_file(errors, path)


def validate_acceptance(
    errors: list[str],
    prefix: str,
    acceptance: object,
    require_core_fields: bool,
) -> None:
    if not isinstance(acceptance, dict):
        errors.append(f"{prefix}: acceptance must be an object")
        return

    unknown = sorted(set(acceptance) - ACCEPTANCE_FIELDS)
    if unknown:
        errors.append(f"{prefix}: acceptance has unknown fields {unknown}")

    fields_to_check = REQUIRED_ACCEPTANCE_FIELDS if require_core_fields else set(acceptance) & REQUIRED_ACCEPTANCE_FIELDS
    for field in sorted(fields_to_check):
        values = as_list(acceptance.get(field))
        if not values or not all(isinstance(item, str) and item for item in values):
            errors.append(f"{prefix}: acceptance.{field} must be a non-empty string array")

    for field in ("expected_deleted_files", "must_contain", "must_not_contain"):
        if field in acceptance:
            values = as_list(acceptance.get(field))
            if not values or not all(isinstance(item, str) and item for item in values):
                errors.append(f"{prefix}: acceptance.{field} must be a non-empty string array when present")

    content_scope = acceptance.get("content_scope")
    if content_scope is not None and content_scope not in ACCEPTANCE_CONTENT_SCOPES:
        errors.append(
            f"{prefix}: acceptance.content_scope must be one of {sorted(ACCEPTANCE_CONTENT_SCOPES)}"
        )


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

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
                    "prompt": str(case.get("prompt")),
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

            acceptance = case.get("acceptance")
            if delivery_mode == "phase5-delivery":
                validate_acceptance(errors, prefix, acceptance, require_core_fields=True)
            elif acceptance is not None:
                validate_acceptance(errors, prefix, acceptance, require_core_fields=False)

            prompt = case.get("prompt")
            if not isinstance(prompt, str) or len(prompt.strip()) < 20:
                errors.append(f"{prefix}: prompt is too short")
            else:
                validate_user_prompt(errors, prefix, prompt)

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
    validate_delivery_results(errors, warnings, case_index)
    validate_launch_prompts(errors)
    validate_pending_launch_prompt_inventory(errors, case_index)

    if errors:
        return report(errors)

    for warning in warnings:
        print(f"WARN: {warning}")
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
    runner_plan_ids: set[str] = set()
    runner_phase5_policy: dict[str, str] = {}
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
        scope = runner.get("scope", "planned")
        if scope not in {"planned", "results-only"}:
            errors.append(f"{prefix}: scope must be 'planned' or 'results-only'")
        elif scope == "planned":
            runner_plan_ids.add(runner_id)
        phase5_policy = runner.get("phase5_policy", "interactive-or-hooked")
        if phase5_policy not in PHASE5_POLICIES:
            errors.append(f"{prefix}: phase5_policy must be one of {sorted(PHASE5_POLICIES)}")
        else:
            runner_phase5_policy[runner_id] = phase5_policy
        for field in ("surface", "model", "invocation"):
            if not isinstance(runner.get(field), str) or not runner.get(field):
                errors.append(f"{prefix}: missing {field}")
    if len(runner_plan_ids) < 2:
        errors.append("delivery-matrix.json: at least two planned runners are required")

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

        prompt_override = scenario.get("prompt_override")
        if prompt_override is not None:
            if not isinstance(prompt_override, str) or len(prompt_override.strip()) < 20:
                errors.append(f"{prefix}: prompt_override must be a non-empty string")
            else:
                validate_user_prompt(errors, prefix, prompt_override)

        for field in ("success_target", "failure_signals", "repair_loop"):
            values = as_list(scenario.get(field))
            if not values or not all(isinstance(item, str) and item for item in values):
                errors.append(f"{prefix}: {field} must be a non-empty string array")

        acceptance = scenario.get("acceptance")
        if stage == "impact-phase5":
            if not isinstance(acceptance, dict):
                errors.append(f"{prefix}: impact-phase5 requires acceptance")
            else:
                validate_acceptance(errors, prefix, acceptance, require_core_fields=True)
        elif acceptance is not None:
            validate_acceptance(errors, prefix, acceptance, require_core_fields=False)

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

    for runner_id in runner_plan_ids:
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
        if runner_phase5_policy.get(runner_id) == "subagent-unattended-stress-only":
            if "impact-phase5" in planned_stages:
                errors.append(
                    f"delivery-matrix.json: runner_plan.{runner_id} must not include impact-phase5 "
                    "because phase5_policy=subagent-unattended-stress-only"
                )
        elif "impact-phase5" not in planned_stages:
            errors.append(f"delivery-matrix.json: runner_plan.{runner_id} must include impact-phase5")


def validate_delivery_results(
    errors: list[str],
    warnings: list[str],
    case_index: dict[str, dict[str, str]],
) -> None:
    if not DELIVERY_RESULTS_PATH.exists():
        errors.append(f"missing {DELIVERY_RESULTS_PATH}")
        return
    if not DELIVERY_MATRIX_PATH.exists():
        return

    matrix_doc = load_json(DELIVERY_MATRIX_PATH)
    if not isinstance(matrix_doc, dict):
        return

    runner_ids = {
        runner.get("id")
        for runner in as_list(matrix_doc.get("runners"))
        if isinstance(runner, dict) and isinstance(runner.get("id"), str)
    }
    planned_runner_ids = {
        runner.get("id")
        for runner in as_list(matrix_doc.get("runners"))
        if (
            isinstance(runner, dict)
            and isinstance(runner.get("id"), str)
            and runner.get("scope", "planned") == "planned"
        )
    }
    scenario_index: dict[str, dict[str, object]] = {}
    for scenario in as_list(matrix_doc.get("scenarios")):
        if not isinstance(scenario, dict):
            continue
        scenario_id = scenario.get("id")
        case_id = scenario.get("case_id")
        if isinstance(scenario_id, str):
            scenario_index[scenario_id] = {
                "runner_scope": set(as_list(scenario.get("runner_scope"))),
                "stage": scenario.get("stage"),
                "case_id": case_id,
                "skill": case_index.get(case_id, {}).get("skill") if isinstance(case_id, str) else None,
            }

    doc = load_json(DELIVERY_RESULTS_PATH)
    if not isinstance(doc, dict):
        errors.append("delivery-results.json must be an object")
        return
    if doc.get("schema_version") != 1:
        errors.append("delivery-results.json: schema_version must be 1")

    results = as_list(doc.get("results"))
    if not results:
        errors.append("delivery-results.json: results must be non-empty")
        return

    result_ids: set[str] = set()
    completed_runners: set[str] = set()
    completed_skills: set[str] = set()
    completed_phase5_runners: set[str] = set()
    completed_negative_runners: set[str] = set()

    for idx, result in enumerate(results):
        prefix = f"delivery-results results[{idx}]"
        if not isinstance(result, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        result_id = result.get("id")
        if not isinstance(result_id, str) or not result_id:
            errors.append(f"{prefix}: missing id")
        elif result_id in result_ids:
            errors.append(f"{prefix}: duplicate id {result_id}")
        else:
            result_ids.add(result_id)

        scenario_id = result.get("scenario_id")
        scenario_meta = scenario_index.get(scenario_id) if isinstance(scenario_id, str) else None
        if scenario_meta is None:
            errors.append(f"{prefix}: unknown scenario_id {scenario_id!r}")

        runner_id = result.get("runner_id")
        if not isinstance(runner_id, str) or runner_id not in runner_ids:
            errors.append(f"{prefix}: unknown runner_id {runner_id!r}")
        elif scenario_meta is not None and runner_id not in scenario_meta["runner_scope"]:
            errors.append(f"{prefix}: runner_id {runner_id!r} is not in scenario runner_scope")

        status = result.get("status")
        if status not in DELIVERY_RESULT_STATUSES:
            errors.append(f"{prefix}: invalid status {status!r}")

        run_record = result.get("run_record")
        if not isinstance(run_record, str) or not run_record.startswith("eval/runs/real-projects/"):
            errors.append(f"{prefix}: run_record must be under eval/runs/real-projects/")
        elif not (REPO_ROOT / run_record).exists():
            errors.append(f"{prefix}: run_record does not exist: {run_record}")

        evidence = as_list(result.get("evidence"))
        if not evidence or not all(isinstance(item, str) and item for item in evidence):
            errors.append(f"{prefix}: evidence must be a non-empty string array")

        blockers = result.get("blockers")
        if not isinstance(blockers, list) or not all(isinstance(item, str) and item for item in blockers):
            errors.append(f"{prefix}: blockers must be a string array")
        elif status == "UNVERIFIED" and not blockers:
            errors.append(f"{prefix}: UNVERIFIED results must explain blockers")

        if status in DELIVERY_COMPLETED_STATUSES and isinstance(runner_id, str):
            completed_runners.add(runner_id)
            if scenario_meta is not None:
                skill = scenario_meta.get("skill")
                stage = scenario_meta.get("stage")
                if isinstance(skill, str):
                    completed_skills.add(skill)
                if stage == "impact-phase5":
                    completed_phase5_runners.add(runner_id)
                if stage == "negative-gate":
                    completed_negative_runners.add(runner_id)

    if len(completed_runners) < 2:
        errors.append("delivery-results.json: completed results must cover at least two runners")
    if completed_skills != {"pathfinder", "impact"}:
        errors.append("delivery-results.json: completed results must cover both pathfinder and impact")
    if len(completed_negative_runners) < 2:
        errors.append("delivery-results.json: completed negative-gate results must cover at least two runners")
    missing_phase5 = (completed_runners & planned_runner_ids) - completed_phase5_runners
    if missing_phase5:
        warnings.append(
            "delivery-results.json: runners with completed results but no completed "
            f"impact-phase5 yet: {sorted(missing_phase5)} "
            "(zero-result runners are exempt; full phase5 coverage is a release-gate criterion)"
        )


def validate_launch_prompts(errors: list[str]) -> None:
    if not RUNS_ROOT.exists():
        return
    for path in sorted(RUNS_ROOT.glob("*/prompts/*.txt")):
        validate_launch_prompt_file(errors, path)


def _standard_prompt_name(scenario_id: str, runner_id: str) -> str | None:
    match = re.match(r"^(D[0-9]+)-", scenario_id)
    if not match:
        return None
    return f"{match.group(1).lower()}-{runner_id}.txt"


def validate_pending_launch_prompt_inventory(
    errors: list[str],
    case_index: dict[str, dict[str, str]],
) -> None:
    """Ensure not-yet-run planned matrix entries have a runnable clean prompt."""
    if not DELIVERY_MATRIX_PATH.exists() or not DELIVERY_RESULTS_PATH.exists():
        return
    if not RUNS_ROOT.exists():
        return

    matrix_doc = load_json(DELIVERY_MATRIX_PATH)
    results_doc = load_json(DELIVERY_RESULTS_PATH)
    if not isinstance(matrix_doc, dict) or not isinstance(results_doc, dict):
        return

    completed_or_attempted = {
        (result.get("scenario_id"), result.get("runner_id"))
        for result in as_list(results_doc.get("results"))
        if isinstance(result, dict)
        and isinstance(result.get("scenario_id"), str)
        and isinstance(result.get("runner_id"), str)
    }

    prompt_paths_by_name: dict[str, list[Path]] = {}
    for path in RUNS_ROOT.glob("*/prompts/*.txt"):
        if path.is_file():
            prompt_paths_by_name.setdefault(path.name, []).append(path)

    runner_plan = matrix_doc.get("runner_plan")
    if not isinstance(runner_plan, dict):
        return

    scenario_index: dict[str, dict[str, str]] = {}
    for scenario in as_list(matrix_doc.get("scenarios")):
        if not isinstance(scenario, dict):
            continue
        scenario_id = scenario.get("id")
        case_id = scenario.get("case_id")
        if not isinstance(scenario_id, str) or not isinstance(case_id, str):
            continue
        case_meta = case_index.get(case_id)
        if case_meta is None:
            continue
        prompt_override = scenario.get("prompt_override")
        scenario_index[scenario_id] = {
            "skill": case_meta.get("skill", ""),
            "stage": str(scenario.get("stage", "")),
            "fixture_mode": str(scenario.get("fixture_mode", "")),
            "prompt": (
                prompt_override
                if isinstance(prompt_override, str) and prompt_override.strip()
                else case_meta.get("prompt", "")
            ),
        }

    for runner_id, planned in sorted(runner_plan.items()):
        if not isinstance(runner_id, str):
            continue
        for scenario_id in as_list(planned):
            if not isinstance(scenario_id, str):
                continue
            if (scenario_id, runner_id) in completed_or_attempted:
                continue
            expected_name = _standard_prompt_name(scenario_id, runner_id)
            if expected_name is None:
                continue
            prompt_paths = prompt_paths_by_name.get(expected_name, [])
            if not prompt_paths:
                errors.append(
                    "pending launch prompt missing: "
                    f"runner_plan.{runner_id} includes {scenario_id}, "
                    f"but no prompts/{expected_name} exists"
                )
                continue

            expected_meta = scenario_index.get(scenario_id)
            if expected_meta is None:
                continue

            parsed_prompts: list[tuple[Path, dict[str, str], str]] = []
            for path in prompt_paths:
                local_errors: list[str] = []
                parsed = parse_launch_prompt_file(local_errors, path)
                if parsed is not None:
                    env, user_text = parsed
                    parsed_prompts.append((path, env, user_text))
            if not parsed_prompts:
                continue

            expected_user_text = expected_meta["prompt"].strip()
            if expected_user_text and not any(
                user_text.strip() == expected_user_text for _, _, user_text in parsed_prompts
            ):
                rel_paths = [path.relative_to(REPO_ROOT).as_posix() for path, _, _ in parsed_prompts]
                errors.append(
                    "pending launch prompt user input mismatch: "
                    f"{scenario_id}/{runner_id} expects case prompt text, "
                    f"but {rel_paths} differ"
                )

            expected_skill = expected_meta["skill"]
            if expected_skill and not any(
                _prompt_skill_matches(env.get("Skill", ""), expected_skill)
                for _, env, _ in parsed_prompts
            ):
                rel_paths = [path.relative_to(REPO_ROOT).as_posix() for path, _, _ in parsed_prompts]
                errors.append(
                    "pending launch prompt skill mismatch: "
                    f"{scenario_id}/{runner_id} expects {expected_skill!r}, "
                    f"but {rel_paths} point elsewhere"
                )

            for path, env, _ in parsed_prompts:
                rel_path = path.relative_to(REPO_ROOT).as_posix()
                validate_pending_prompt_environment(errors, rel_path, scenario_id, expected_meta, env)


def _prompt_skill_matches(skill_path: str, expected_skill: str) -> bool:
    normalized = skill_path.replace("\\", "/").rstrip("/")
    return normalized.endswith(f"/skills/{expected_skill}/SKILL.md")


def _normalize_prompt_path(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")


def validate_pending_prompt_environment(
    errors: list[str],
    rel_path: str,
    scenario_id: str,
    scenario_meta: dict[str, str],
    env: dict[str, str],
) -> None:
    workdir = _normalize_prompt_path(env.get("工作目录", ""))
    output = _normalize_prompt_path(env.get("输出归档", ""))
    non_git_copy = _normalize_prompt_path(env.get("非 Git 副本目录", ""))

    repo_root = _normalize_prompt_path(str(REPO_ROOT))
    if workdir and (workdir == repo_root or workdir.startswith(repo_root + "/")):
        errors.append(f"{rel_path}: 工作目录 must point to an external fixture, not this repo")

    if output:
        if "/eval/runs/real-projects/" not in output:
            errors.append(f"{rel_path}: 输出归档 must be under eval/runs/real-projects")
        if not output.endswith("/README.md"):
            errors.append(f"{rel_path}: 输出归档 must end with README.md")

    needs_non_git_copy = (
        scenario_meta.get("fixture_mode") == "non-git-copy"
        and scenario_meta.get("stage") == "pathfinder-map"
    )
    if needs_non_git_copy and not non_git_copy:
        errors.append(f"{rel_path}: {scenario_id} must include 非 Git 副本目录")
    if non_git_copy and not needs_non_git_copy:
        errors.append(f"{rel_path}: 非 Git 副本目录 is only allowed for non-git pathfinder scenarios")
    if non_git_copy and workdir and non_git_copy == workdir:
        errors.append(f"{rel_path}: 非 Git 副本目录 must differ from 工作目录")


def report(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
