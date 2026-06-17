# 公共模板目录

> 本目录存放 impact 与 impact-pro **共享的模板结构定义**。
>
> 两份 skill 的 templates/ 下的对应文件应保持**结构对齐**——不是说文字完全一样，
> 而是说章节骨架、必填字段、安全闸措辞**同步修改**。
>
> 改任何一份时，检查另一份是否需要同步。

## 对应关系

| impact | impact-pro | 结构对齐要求 |
|--------|-----------|-------------|
| `templates/000-context-pack.md`（项目背景） | `templates/000-context-pack.md`（Context Pack） | 分层格式、相关性分级、排除项 |
| `templates/010-requirements.md` | `templates/010-requirements.md` | 章节骨架、NFR、Goals/Non-Goals |
| `templates/020-design.md` | `templates/020-design.md` | 替代方案、横切关注点、接口契约 |
| `templates/030-implementation.md` | `templates/030-implementation.md` | 组合回滚顺序、Step 确认格式 |
| `templates/040-light.md` | `templates/040-light.md` | 定级证据、信息不全兜底 |
| `templates/060-preflight.md` | `templates/060-preflight.md` | P0/P1 分档、Go/No-Go 阈值 |
| `templates/090-execution-record.md` | `templates/090-execution-record.md` | 时间戳格式、脱敏提示 |
| `templates/_active-state.md` | `templates/_active-state.md` | 恢复检查清单、并发锁 |
| `templates/subagent-decisions.md` | `templates/subagent-decisions.md` | request-human-confirm、eval 沙盒 |

## 如何改

1. 在对应 skill 的 templates/ 里改
2. 在 commit message 里写清楚改了哪份
3. 如果改动涉及结构（新增/删除/重排章节），同步检查另一份
