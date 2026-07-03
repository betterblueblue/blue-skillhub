# Cursor GUI Composer Real Phase 5 Acceptance

Date: 2026-07-03
Host: Cursor GUI
Runner model: Composer
Fixture: `E:\agent\real-project-fixtures-slash-phase5\frontend-react-dashboard-cursor-composer-gui-phase5-manual`
Fixture base commit: `8223897259151c450f954e462c57df3703d5508d`

## Task

```text
Change the sidebar Dashboard display text to Insights.
Do not change route path, key, icon, order, permissions, API, DB, data structure, or test config.
```

## Phase 4

Phase 4 produced only Impact docs:

```text
change-impact/sidebar-dashboard-to-insights/000-context-pack.md
change-impact/sidebar-dashboard-to-insights/040-light.md
change-impact/sidebar-dashboard-to-insights/_active-state.md
```

Source diff after Phase 4:

```text
<empty>
```

Validator before source write:

```text
SUMMARY: 17 passed, 0 failed, 0 warnings
```

## Phase 5 Result

Final git status:

```text
## HEAD (no branch)
 M src/views/dashboard/dashboard.router.tsx
?? change-impact/sidebar-dashboard-to-insights/000-context-pack.md
?? change-impact/sidebar-dashboard-to-insights/040-light.md
?? change-impact/sidebar-dashboard-to-insights/060-preflight.md
?? change-impact/sidebar-dashboard-to-insights/090-execution-record.md
?? change-impact/sidebar-dashboard-to-insights/_active-state.md
```

Final source diff:

```diff
-      label: 'Dashboard',
+      label: 'Insights',
       title: 'Dashboard',
```

Field check:

```text
path: 'dashboard'
label: 'Insights'
title: 'Dashboard'
key: '/dashboard'
icon: <DashboardOutlined />
order: 1
```

The old validator result was fully green:

```text
SUMMARY: 17 passed, 0 failed, 0 warnings
```

No git metadata side effect was found in this GUI run:

```text
.git/info/exclude unchanged
```

## Verdict

FAIL.

Cursor GUI Composer followed the Phase 4/5 process and did not modify `.git/info/exclude`, but it implemented only half of the display-text change: `meta.label` changed to `Insights`, while sibling `meta.title` stayed `Dashboard`.

This matches the earlier Grok CLI Composer 2.5 Fast failure mode, so the issue is not specific to the Grok harness.

## Regression After v5.6 Validator Fix

After adding V17, the same fixture is blocked:

```text
FAIL: V17: Route display text appears partially updated — label changed while sibling title still uses the old display text. ... src/views/dashboard/dashboard.router.tsx: label 'Dashboard'->'Insights' but sibling title remains 'Dashboard'

SUMMARY: 17 passed, 1 failed, 0 warnings
```
