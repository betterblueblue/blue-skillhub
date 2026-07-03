# GLM 5.1 Real Slash Phase 5 Acceptance

Date: 2026-07-03
Host: Claude Code CLI
Runner model observed in CLI output: `xopglm51[1m]`
Provider noted by user: 讯飞星辰 GLM 5.1
Workspace: `E:\agent\blue-skillhub`
Fixture: `E:\agent\real-project-fixtures-slash-phase5\frontend-react-dashboard-glm51-phase5-20260703-220512`
Fixture commit: `8223897259151c450f954e462c57df3703d5508d`

## Purpose

Run the same real `/impact` Phase 5 frontend text-change scenario used for M3 / DeepSeek / Step comparison.

Task:

```text
Change the sidebar Dashboard display text to Insights.
Do not change route path, key, icon, order, permissions, API, DB, data structure, or test config.
```

## Smoke

Smoke result:

```text
Impact skill recognized.
Current model identifier: xopglm51[1m]
```

Smoke cost and time:

```text
duration_ms: 35990
total_cost_usd: 0.68936
```

## Phase 4

Files produced:

```text
change-impact/sidebar-dashboard-to-insights/000-context-pack.md
change-impact/sidebar-dashboard-to-insights/040-light.md
change-impact/sidebar-dashboard-to-insights/_active-state.md
```

Runner result:

```text
16 passed, 0 failed, 1 warning
```

Main judge local validation immediately after Phase 4:

```text
SUMMARY: 17 passed, 0 failed, 0 warnings
```

Boundary check:

```text
git diff --stat
<empty>
```

Phase 4 cost and time:

```text
duration_ms: 761431
total_cost_usd: 6.79267
```

## Preflight

Files produced:

```text
change-impact/sidebar-dashboard-to-insights/060-preflight.md
```

Runner stopped correctly before source write and requested:

```text
确认 Step 1
```

Main judge local validation after preflight:

```text
SUMMARY: 16 passed, 0 failed, 1 warnings
```

The warning was V4:

```text
No grading decision table found
```

Boundary check:

```text
git diff --stat
<empty>
```

Preflight cost and time:

```text
duration_ms: 407560
total_cost_usd: 7.497815
```

## Step 1 Source Write

The first Step 1 run changed the source file correctly but exited on budget before generating `090-execution-record.md`.

Budget-exit result:

```text
Reached maximum budget ($8)
```

Source diff already present at that point:

```diff
-      label: 'Dashboard',
-      title: 'Dashboard',
+      label: 'Insights',
+      title: 'Insights',
       key: '/dashboard',
```

Issue exposed:

```text
Source file had changed, but 090-execution-record.md was missing.
Current validator did not fail this intermediate state because V15 skips when no execution record exists.
```

Follow-up fix in the skill repo:

```text
Impact V15 now checks Git status. If source/test/config files have changed but 090-execution-record.md is missing, or the record has no source/test/config Step, validator fails.
```

First Step 1 cost and time:

```text
duration_ms: 274738
total_cost_usd: 8.287435
```

## Repair / Completion

A follow-up prompt asked the runner to avoid further source changes and only finish records.

Files produced:

```text
change-impact/sidebar-dashboard-to-insights/090-execution-record.md
```

The repair run also exited on budget, but the execution record and active-state update had landed.

Repair cost and time:

```text
duration_ms: 126436
total_cost_usd: 6.524935
```

## Final Main Judge Verification

Impact validator:

```text
SUMMARY: 16 passed, 0 failed, 1 warnings
```

Remaining warning:

```text
V4: No grading decision table found
```

Diff:

```text
src/views/dashboard/dashboard.router.tsx | 4 ++--
1 file changed, 2 insertions(+), 2 deletions(-)
```

Source grep:

```text
10:    path: 'dashboard',
17:      label: 'Insights',
18:      title: 'Insights',
19:      key: '/dashboard',
```

Whitespace check:

```text
git diff --check
exit 0
```

Build/lint:

```text
npm run lint
exit 1
'eslint' is not recognized as an internal or external command

npm run build
exit 1
'tsc' is not recognized as an internal or external command
```

Interpretation:

- The fixture has no installed `node_modules`.
- This is the same environment limitation seen in the other frontend Phase 5 runs.
- Final verification is static diff validation plus Impact validator, not a full build pass.

## Verdict

PASS with significant caveats.

What held:

- Real `/impact` loaded under `xopglm51[1m]`.
- Phase 4 and preflight did not modify source.
- Source diff was exact and minimal.
- Route path, key, icon, order, API, DB, permissions, data structure, and test config stayed unchanged.

What did not hold cleanly:

- Very slow and expensive for a tiny change.
- Preflight / final self-reported validation did not match main judge validation.
- `_active-state.md` retained stale Git audit text from an earlier temporary file.
- Step 1 exited after source write but before execution record, requiring a repair turn.
- Current Impact V15 does not fail the intermediate state where source diff exists but `090-execution-record.md` is missing.

Recommendation:

Do not use GLM 5.1 as the default daily runner in this setup. It can complete the task, but the latency, cost, and incomplete Step 1 behavior make it weaker than MiniMax M3 and gpt-5.4-mini for this gated workflow.
