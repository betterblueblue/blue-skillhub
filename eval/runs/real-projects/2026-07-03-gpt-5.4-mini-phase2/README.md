# GPT-5.4 Mini Phase 2 Real-Project Matrix

Date: 2026-07-03
Runner model: `gpt-5.4-mini`
Judge: main Codex thread
Runner base commit: `f228021`
Workspace: `E:\agent\blue-skillhub`

## Purpose

Run the second real-project matrix phase against:

- Frontend project: `frontend-react-dashboard`
- Monorepo/non-Git project: `monorepo-full-stack-starter`

This phase specifically checks two weak-model failure modes:

- Pure frontend project: do not invent backend, DB, or migrations.
- Monorepo/non-Git project: do not read parent Git branch/head/hotspots when the target has no `.git`.

## Fixtures

| Project | Fixture | Commit / Git State |
|---|---|---|
| `frontend-react-dashboard` | `E:\agent\real-project-fixtures\frontend-react-dashboard` | `8223897259151c450f954e462c57df3703d5508d` |
| `monorepo-full-stack-starter` | `E:\agent\real-project-fixtures\monorepo-full-stack-starter` | `21fbd77ca7ec177a9837b32066ed4b8884cae3c2` |
| `monorepo-full-stack-starter-non-git` | `E:\agent\real-project-fixtures\monorepo-full-stack-starter-non-git` | non-Git, all Git fields null/empty |
| `monorepo-api-subdir` | `E:\agent\real-project-fixtures\monorepo-api-subdir` | non-Git, all Git fields null/empty |

## Archive Contents

| Path | Content |
|---|---|
| `raw/` | Runner reports returned by the two weak-model subagents |
| `commands/phase2-verification.txt` | Main judge verification commands and key outputs |
| `scorecards/phase2-summary.md` | Scores, pass/fail table, and findings |

## Result

| Metric | Value |
|---|---:|
| Cases | 8 |
| Passed | 8 |
| Failed | 0 |
| P0/P1/P2 | 0 |
| Average score | 93.6 / 100 |

All four Pathfinder maps passed the current V1-V8 gate:

```text
SUMMARY: 8 passed, 0 failed, 0 warnings
```

## Conclusion

Phase 2 passed. The frontend project did not trigger fake DB/backend claims, and both non-Git monorepo variants degraded honestly without parent Git leakage.

Together with phase 1, the five-project matrix is now covered at runner-report + validator level. The remaining caveat is that this is still not a full real slash command transcript for all 20 cases.
