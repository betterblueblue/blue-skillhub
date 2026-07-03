# Real-Project Matrix Final Summary

Date: 2026-07-03
Runner model: `gpt-5.4-mini`
Judge: main Codex thread
Final repo commit: `37b0959`

## What Was Covered

| Area | Evidence |
|---|---|
| Real Claude slash command smoke | `2026-07-03-claude-slash-smoke`, commit `2f1a756` |
| Pathfinder weak-model non-Git exam | `2026-07-03-pathfinder-weak-non-git`, commit `6627708` |
| Phase 1 real-project matrix | `2026-07-03-gpt-5.4-mini-phase1`, commit `f228021` |
| Pathfinder V8 fix from phase 1 finding | commit `498896f` |
| Phase 2 real-project matrix | `2026-07-03-gpt-5.4-mini-phase2`, commit `37b0959` |

## Matrix Result

| Phase | Projects | Cases | Pass | Fail | P0/P1 | P2 |
|---|---:|---:|---:|---:|---:|---:|
| Phase 1 | 3 | 12 | 11 | 1 | 0 | 1 |
| Phase 2 | 2 | 8 | 8 | 0 | 0 | 0 |
| Total | 5 | 20 | 19 | 1 | 0 | 1 |

The only failed case was `java-ruoyi-pathfinder`. The content covered the right areas, but the weak model produced malformed mixed Windows evidence paths such as:

```text
ruoyi-admin/E:/agent/real-project-fixtures/java-ruoyi/pom.xml:23-53
```

That issue was fixed in the same sequence by adding Pathfinder validator V8.

## Fixes From This Run

### Pathfinder V8

`pf_validate.py` now blocks evidence paths that mix a relative prefix with a Windows absolute path, for example `src/E:/repo/app.py`.

Why it mattered:

- Old V1 could pass this by falling back to basename search.
- A weak model could therefore produce bad evidence paths while still getting `SUMMARY: 7 passed`.

Verification:

```text
python skills\pathfinder\tests\test_scripts\test_pathfinder_scripts.py
Ran 23 tests
OK
```

After V8:

- Java RuoYi bad map: `SUMMARY: 7 passed, 7 failed, 0 warnings`
- Node map: `SUMMARY: 8 passed, 0 failed, 0 warnings`
- Python map: `SUMMARY: 8 passed, 0 failed, 0 warnings`
- Frontend map: `SUMMARY: 8 passed, 0 failed, 0 warnings`
- Monorepo root / non-Git / API subdir maps: all `SUMMARY: 8 passed, 0 failed, 0 warnings`

## Skill Assessment

### Pathfinder

Result: strong, with one newly fixed validator gap.

What held:

- Facts layer forced `scan.json` and `git.json`.
- Non-Git handling correctly avoided parent branch/head/hotspots.
- Mermaid V5 repeatedly caught weak-model map issues and forced repair.
- V8 now catches malformed evidence paths that old V1 missed.

Remaining caveat:

- Validator checks map structure and evidence path sanity, not every factual claim. Human/judge sampling is still needed for release-level confidence.

### Impact

Result: strong in analysis-only matrix cases.

What held:

- Light cases stayed light without drifting into DB/API work.
- Full cases covered DB/API/frontend/shared/generated/test dimensions where expected.
- Negative cases blocked destructive DB/auth/schema requests.
- Pure frontend case did not invent backend/DB.

Remaining caveat:

- This matrix did not execute full Phase 4 document generation and Phase 5 source-code write steps for all 20 cases. It validated classification, impact coverage, and safety boundaries.

## Slash Command Caveat

Claude Code real slash command loading was smoke-tested for `/impact` and `/pathfinder`.

This run did not prove a full real slash command transcript for all 20 matrix cases, and it did not prove the Codex Desktop slash dispatcher because no direct UI slash-dispatch tool was exposed in this thread.

## Final Conclusion

For the current evidence level, `pathfinder` and `impact` are in good shape:

- No P0/P1 remained.
- One P2 was found and fixed.
- The five-project matrix covered Java backend, Node API, Python full stack, pure frontend, and monorepo/non-Git.
- The weak-model failures that appeared were handled by scripts rather than by hoping the model behaves.

Release confidence: high for read-only Pathfinder maps and Impact analysis/guardrails; medium for full slash-command Phase 5 implementation until a separate write-operation acceptance run is completed.
