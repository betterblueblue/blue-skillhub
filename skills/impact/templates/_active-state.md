# [变更名称] Active State

> Cross-session recovery state for impact / impact-pro. This file is a
> checkpoint, not an authorization. It never replaces `确认 Step N`.

## State Header

- updated_at: [真实系统时间]
- skill: impact
- target_project_root:
  - absolute_path: [绝对路径，如 E:\projects\ruoyi-vue]
  - determination_method: [git-rev-parse / user-specified / pom-dot-xml / build-dot-gradle / inferred-from-cwd / other]
  - verification_timestamp: [真实系统时间 ISO 8601]
- change_dir: `change-impact/[需求名称]/`
- current_phase: [Phase 4 / Phase 5 / blocked / complete]
- mode: [light / full]
- current_git_head: [HEAD / 非 Git / Git 不可用]
- git_audit_status: [clean / dirty / non-git / unavailable]
- confirmation_required: [true / false]
- pending_step: [Step N / none]
- last_prompted_step: [Step N / none]
- last_confirmed_step: [Step N / none]
- last_completed_step: [Step N / none]
- v1_only_count: [N]

## Current Intent

- user_goal: [用户原始变更意图摘要]
- current_assumption: [当前假设]
- success_criteria: [可验证完成标准]
- simpler_option: [更简单方案 / 不适用]

## Document Status

| Document | Status | Notes |
| --- | --- | --- |
| 000-context-pack.md | missing / draft / confirmed | |
| 010-requirements.md | missing / draft / confirmed / n/a | |
| 020-design.md | missing / draft / confirmed / n/a | |
| 030-implementation.md | missing / draft / confirmed / n/a | |
| 040-light.md | missing / draft / confirmed / n/a | |
| 060-preflight.md | missing / draft / pass / blocked | |
| 090-execution-record.md | missing / active | |

## Step Ledger

| Step | Status | Write Objects | Confirmation | Validation | Notes |
| --- | --- | --- | --- | --- | --- |
| Step N | planned / pending / confirmed / success / failed / skipped | [files/tables/configs] | [required / confirmed / skipped] | [V0-V3] | |

## Pending Recovery Check

Before any resumed write operation:

- [ ] Re-read this file
- [ ] Re-read 030-implementation.md or 040-light.md
- [ ] Re-read 060-preflight.md if present
- [ ] Check current git status / target file state
- [ ] Restate pending Step and write objects
- [ ] Require a fresh current-dialogue `确认 Step N`

## Open Items

- [未确认项 / 风险 / 用户决策]

## Last Validation

- command: `[命令]`
- result: [pass / fail / skipped]
- validation_level: [V0 / V1 / V2 / V3]
- reason_if_skipped: [原因 / 不适用]

## Resume Notes

- [恢复时读到的冲突、不一致、阻塞项、下一步安全动作]
