# Phase 1 Scorecard

Date: 2026-07-03
Runner model: `gpt-5.4-mini`
Judge: main Codex thread
Runner base commit: `6627708`

## Summary

| Item | Result |
|---|---:|
| Projects | 3 |
| Cases | 12 |
| Passed | 11 |
| Failed | 1 |
| P0/P1 | 0 |
| P2 | 1 |
| Average score | 91.4 / 100 |
| Needs skill fix | yes, Pathfinder V8 added in this run |

## Case Scores

| Case | Score | Highest issue | Verdict | Notes |
|---|---:|---|---|---|
| `java-ruoyi-pathfinder` | 82 | P2 | FAIL | Content covered the right RuoYi areas, but evidence paths included malformed `ruoyi-admin/E:/...` references. Old gate passed; V8 now fails it. |
| `java-ruoyi-impact-light` | 90 | P3 | PASS | Correctly kept the remark label change as light and separated label text from DB/API/export semantics. |
| `java-ruoyi-impact-full` | 91 | P3 | PASS | Correctly treated `external_id` as DB/entity/Mapper/UI/export/test work and asked for field semantics. |
| `java-ruoyi-negative` | 93 | none | PASS | Correctly blocked direct deletion of `remark` and identified `BaseEntity` reuse. |
| `node-realworld-prisma-pathfinder` | 94 | none | PASS | Validator forced a Mermaid repair; final map passed V1-V8 and covered Express/Prisma/auth/test boundaries. |
| `node-realworld-prisma-impact-light` | 90 | P3 | PASS | Correctly kept login error copy as light while checking status code, response shape, and tests. |
| `node-realworld-prisma-impact-full` | 92 | P3 | PASS | Correctly covered Prisma schema, migration, profile/article response shape, generated client, and tests. |
| `node-realworld-prisma-negative` | 94 | none | PASS | Correctly halted `User.email` rename + migration and called out login/unique/index compatibility. |
| `python-fastapi-template-pathfinder` | 94 | none | PASS | Validator forced a formatting repair; final map passed V1-V8 and covered backend/frontend/OpenAPI/compose. |
| `python-fastapi-template-impact-light` | 90 | P3 | PASS | Correctly scoped login welcome text to frontend copy unless shared/i18n resources say otherwise. |
| `python-fastapi-template-impact-full` | 93 | P3 | PASS | Correctly covered SQLModel, Alembic, API schema, generated client, frontend item UI, and tests. |
| `python-fastapi-template-negative` | 94 | none | PASS | Correctly blocked deleting `email` from the auth model and named login/OpenAPI/frontend/test blast radius. |

## Finding

### P2: Pathfinder V1 could pass malformed evidence paths by basename fallback

The Java Pathfinder map contained evidence paths like:

```text
ruoyi-admin/E:/agent/real-project-fixtures/java-ruoyi/pom.xml:23-53
```

This is not a valid project path. The old V1 line-number check still passed because `_resolve_file()` fell back to searching by basename, found `pom.xml`, and treated the claim as valid.

Fix added in this run:

- `pf_validate.py` now has V8 evidence path sanity checking.
- `test_v8_embedded_windows_drive_path_fails` covers `src/E:/agent/example/app.py`.
- README / SKILL / review checklist now describe V1-V8.

Post-fix behavior:

- Java map: `SUMMARY: 7 passed, 7 failed, 0 warnings` because V8 catches the malformed paths.
- Node map: `SUMMARY: 8 passed, 0 failed, 0 warnings`.
- Python map: `SUMMARY: 8 passed, 0 failed, 0 warnings`.

## Limits

This phase used subagent runner reports and fixture files, not a full real slash command transcript for all 12 cases. It is a weak-model matrix exam with judge verification, not the final 5-project slash-command acceptance.
