# Impact 模板来源说明

这个目录不再保存模板副本。`impact-pro` 已于 2026-06-26 合并到 ImpactRadar，当前唯一有效的模板目录是 `skills/impact/templates/`。

## 完整性检查

`scripts/sync_templates.py` 会检查以下 10 个必需模板是否存在且不为空：

- `000-context-pack.md`
- `005-change-summary.md`
- `010-requirements.md`
- `020-design.md`
- `030-implementation.md`
- `040-light.md`
- `060-preflight.md`
- `090-execution-record.md`
- `_active-state.md`
- `subagent-decisions.md`

`_style-rules.md`、`final-readiness-audit.md` 和 `scorecard.md` 也是现有模板，但目前不属于该脚本的必需文件清单。

## 如何改

1. 直接修改 `skills/impact/templates/` 中的源文件。
2. 如果新增、删除或重命名必需模板，同步更新 `scripts/sync_templates.py` 中的 `EXPECTED_TEMPLATES`。
3. 运行 `python scripts/sync_templates.py --check`。
