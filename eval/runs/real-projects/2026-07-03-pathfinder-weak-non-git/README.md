# Pathfinder Weak-Model Non-Git Exam

Date: 2026-07-03
Repo commit under test: `2f1a756`
Model under test: `gpt-5.4-mini`
Workspace: `E:\agent\blue-skillhub`
Fixture: `E:\agent\pathfinder-weak-fixtures\node-realworld-non-git-20260703-190859`

## Purpose

Check whether `pathfinder` still produces a valid project map when a weaker model runs on a copied real Node / Express / Prisma project whose `.git` directory has been removed.

This specifically exercises the non-Git path that previously risked leaking metadata from a parent repository.

## Prompt Summary

The delegated task asked the weak model to run a Pathfinder-style read-only project scan for the fixture, generate the project map, and write only the Pathfinder output files under `change-impact/`.

Allowed writes:

- `change-impact/_project-map.md`
- `change-impact/_project-map/facts/scan.json`
- `change-impact/_project-map/facts/git.json`

The exact subagent transcript was not available through the status interface at archive time, so this record is based on the files written to disk and the main-agent verification commands below.

## Fixture

The fixture is a local copy of the Node RealWorld Prisma project with `.git` removed.

Observed Pathfinder facts:

```json
{
  "file_count": 51,
  "manifest_files": ["package.json"],
  "budget_tier": "小仓"
}
```

Observed Git facts:

```json
{
  "is_git_repo": false,
  "is_independent_repo": false,
  "toplevel": null,
  "head_short": null,
  "head_full": null,
  "branch": null,
  "hotspots": [],
  "recent_commit_modules": []
}
```

The generated map also records:

```text
基于 commit: 非 Git,以扫描时间为准
```

## Verification

Command:

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\pathfinder-weak-fixtures\node-realworld-non-git-20260703-190859\change-impact\_project-map.md --repo-root E:\agent\pathfinder-weak-fixtures\node-realworld-non-git-20260703-190859
```

Result:

```text
PASS: V1: line-number claims verified
PASS: V2: no credential leakage detected
PASS: V3: SVG safety check passed
PASS: V4: uncovered section has entries
PASS: V5: Mermaid solid-arrow consistency passed
PASS: V6: facts file content validated
PASS: V7: section [14] code style observation exists
SUMMARY: 7 passed, 0 failed, 0 warnings
```

## Observations

| Check | Evidence | Verdict |
| --- | --- | --- |
| Non-Git handling | `git.json` has null branch/head/toplevel and empty hotspots/modules. | PASS |
| Parent repo isolation | No parent branch, commit, hotspot, or recent module data appears in facts. | PASS |
| Required facts | `scan.json` and `git.json` exist and pass `pf_validate.py`. | PASS |
| Map quality gates | All seven Pathfinder validator checks passed. | PASS |
| Credential handling | Map contains sanitized secret value as `***`; validator reports no leak. | PASS |
| Weak-model correction | First validation reportedly failed on Mermaid V5, then the model repaired the map and final validation passed. | PASS |

## Conclusion

`pathfinder` passed this weak-model non-Git exam.

The main evidence is that the generated map passes the validator and the Git facts remain fully empty for a non-independent, non-Git fixture. This means the earlier parent-repository leakage class is covered for this scenario.

This is still a single-project exam. It does not replace the planned five-project matrix across Java, Node, Python, frontend, and monorepo/non-Git cases.
