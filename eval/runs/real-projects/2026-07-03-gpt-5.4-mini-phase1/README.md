# GPT-5.4 Mini Phase 1 Real-Project Matrix

Date: 2026-07-03
Runner model: `gpt-5.4-mini`
Judge: main Codex thread
Runner base commit: `6627708`
Workspace: `E:\agent\blue-skillhub`

## Purpose

Run the first real-project matrix phase against three fixed projects:

- Java backend: `java-ruoyi`
- Node API: `node-realworld-prisma`
- Python full stack: `python-fastapi-template`

Each project ran four cases: `pathfinder`, `impact-light`, `impact-full`, and `negative`.

## Fixtures

| Project | Fixture | Commit |
|---|---|---|
| `java-ruoyi` | `E:\agent\real-project-fixtures\java-ruoyi` | `0d42679bc25576286bf34a156002716ed7de5739` |
| `node-realworld-prisma` | `E:\agent\real-project-fixtures\node-realworld-prisma` | `6ac99ea5aeadc4e001dd4d6933c2e269f878a969` |
| `python-fastapi-template` | `E:\agent\real-project-fixtures\python-fastapi-template` | `3685fb66259fa12f8436ae7f88379fd64ca7cdbd` |

## Archive Contents

| Path | Content |
|---|---|
| `raw/` | Runner reports returned by the three weak-model subagents |
| `commands/phase1-verification.txt` | Main judge verification commands and key outputs |
| `scorecards/phase1-summary.md` | Scores, pass/fail table, and findings |

## Result

| Metric | Value |
|---|---:|
| Cases | 12 |
| Passed | 11 |
| Failed | 1 |
| P0/P1 | 0 |
| P2 | 1 |
| Average score | 91.4 / 100 |

The only failed case was `java-ruoyi-pathfinder`, due to malformed mixed Windows evidence paths such as `ruoyi-admin/E:/agent/...`. This was not caught by the old validator because V1 could fall back to basename search. The issue is now fixed by Pathfinder V8.

## Judge Verification

Before the V8 fix, all three Pathfinder maps passed the old gate:

```text
SUMMARY: 7 passed, 0 failed, 0 warnings
```

After adding V8:

| Project | Validator Result |
|---|---|
| `java-ruoyi` | `SUMMARY: 7 passed, 7 failed, 0 warnings` |
| `node-realworld-prisma` | `SUMMARY: 8 passed, 0 failed, 0 warnings` |
| `python-fastapi-template` | `SUMMARY: 8 passed, 0 failed, 0 warnings` |

Regression test:

```text
python skills\pathfinder\tests\test_scripts\test_pathfinder_scripts.py
Ran 23 tests
OK
```

## Conclusion

Phase 1 found one real weak-model issue and turned it into an automated gate. The Impact cases all held their boundaries: light stayed light, full covered the expected DB/API/frontend/test dimensions, and negative cases blocked destructive requests.

This is not the final five-project matrix. Phase 2 still needs the frontend project and monorepo/non-Git project.
