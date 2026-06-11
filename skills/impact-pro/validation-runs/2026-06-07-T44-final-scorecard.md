# T44 最终评分复算表

> 基于 `templates/scorecard.md` 复算最终升级前的平均分和 P0/P1 状态。

## 基本信息

- 复算日期：2026-06-07
- 复算人：Codex
- 当前 commit：待本次主仓提交
- 复算范围：T01-T43、round1-round17
- 关联 `VALIDATION.md` 版本：本次更新后的 `VALIDATION.md`

## 样本总表

| 样本 | 技术栈 / 场景 | full/light/负向/生产级 | 分数 | P0 | P1 | 证据记录 | 验证命令 / 对话证据 |
|------|---------------|-------------------------|------|----|----|----------|----------------------|
| T01-T21 | Java、Node/Prisma、FastAPI、Go/Gin、.NET/EF、React/Vite、Next.js、Nuxt/Vue、monorepo | full + light 矩阵 | >= 85 | 0 | 0 | T01-T21、round8、round9 | 静态验收、运行时补强见 T11-T12、round7、round17 |
| T08-T10 | 负向场景 | 负向 / agent 对话复测 | 通过 | 0 | 0 | T08-T10、round13 | subagent 对话复测 |
| T22 | RuoYi production revalidation | 生产级 | 93 | 0 | 0 | T22 | Maven compile |
| T23 | eShopOnWeb production revalidation | 生产级 | 92 | 0 | 0 | T23 | Docker .NET test |
| T24 | Go RealWorld production revalidation | 生产级 | 89 | 0 | 0 | T24、round16 | Docker Go test |
| T25-T42 | 流程、门禁、模板、索引、rollout | 规则/流程验收 | 通过 | 0 | 0 | T25-T42 | 文档审计、preflight dry-run、Docker baseline |
| T43 | Go RealWorld Phase 5 execution | 真实执行闭环 | 通过 | 0 | 0 | T43、外部 `090-execution-record.md` | Docker `go test -p 1 ./...` |

## 分组复算

| 分组 | 样本范围 | 样本数 | 平均分 | 未修复 P0 | 未修复 P1 | 结论 |
|------|----------|--------|--------|-----------|-----------|------|
| 多栈 full + light | T01-T21 | 21 | >= 85 | 0 | 0 | 达到 |
| 负向 agent 对话复测 | T08-T10、round13 | 3 | 通过 | 0 | 0 | 达到 |
| 生产级项目复验 | T22-T24 | 3 | 91.33 | 0 | 0 | 达到 |
| Phase 5 闭环 | T26-T34、T40-T43 | 12 | 通过 | 0 | 0 | 达到 |
| profile 晋级 / generic 兜底 | T36、`profiles/_schema.md` | 1 | 通过 | 0 | 0 | 达到 |

## 总结

- 纳入样本数：T01-T43 + round1-round17
- 总平均分：当前可量化生产级样本平均分 91.33；所有评分门槛样本均 >= 85
- 未修复 P0：0
- 未修复 P1：0
- 是否满足 `平均分 >= 85 且无 P0/P1`：是

## 排除样本

| 样本 | 排除原因 | 是否需后续补测 |
|------|----------|----------------|
| 无 | 无 | 否 |

## 计算说明

- 生产级项目分数按 T22-T24 已记录分值复算：`(93 + 92 + 89) / 3 = 91.33`。
- 规则、模板和 checklist 作为门禁证据，不替代真实项目执行得分；真实执行闭环由 T43 补齐。
- 出现任一未修复 P0/P1 时不得升级；当前未发现未修复 P0/P1。
