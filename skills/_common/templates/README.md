# 公共模板目录

> 本目录存放 impact skill 模板的结构定义参考。
>
> impact-pro 已于 2026-06-26 合并到 impact，不再独立维护。
> 所有模板以 `skills/impact/templates/` 为唯一源。

## 模板清单

| 模板文件 | 用途 |
|----------|------|
| `000-context-pack.md` | 项目背景、分层格式、相关性分级、排除项 |
| `010-requirements.md` | 章节骨架、NFR、Goals/Non-Goals |
| `020-design.md` | 替代方案、横切关注点、接口契约 |
| `030-implementation.md` | 组合回滚顺序、Step 确认格式 |
| `040-light.md` | 定级证据、信息不全兜底 |
| `060-preflight.md` | P0/P1 分档、Go/No-Go 阈值 |
| `090-execution-record.md` | 时间戳格式、脱敏提示 |
| `_active-state.md` | 恢复检查清单、并发锁 |
| `subagent-decisions.md` | request-human-confirm、eval 沙盒 |
| `final-readiness-audit.md` | 最终就绪审计（full 模式） |
| `scorecard.md` | 评分卡模板 |

## 如何改

1. 直接在 `skills/impact/templates/` 里改
2. 在 commit message 里写清楚改了哪个模板
3. 改动涉及结构（新增/删除/重排章节）时，检查 `scripts/sync_templates.py` 的 `EXPECTED_TEMPLATES` 列表是否需要同步更新
