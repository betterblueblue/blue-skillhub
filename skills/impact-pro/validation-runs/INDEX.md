# impact-pro 验证记录索引

> 本索引用于快速定位证据。详细结论以对应 `Txx` / `round` 记录和 `VALIDATION.md` 为准。

## 当前总状态

```text
impact-pro = 多栈可试用增强版，不是已验收的成熟通用完成态。
```

硬缺口：

- T29 或等价真实项目尚未完成完整 Phase 5 写操作闭环。
- 外部 Go RealWorld 演练的 Step 1、Step 2、Step 4 仍需用户显式 `确认 Step N`。

## 八条目标证据地图

| # | 成功标准 | 当前状态 | 主要证据 |
|---|----------|----------|----------|
| 1 | 不宣称覆盖任意技术栈，只宣称已验证 profile 覆盖范围内可用 | 达到 | `README.md`、`VALIDATION.md`、T36 |
| 2 | 至少 5 个不同技术栈，每栈完成 full + light 双变更验收 | 达到 | T01-T21 |
| 3 | T08-T10 等负向场景完成真实 agent 对话复测 | 达到 | T08-T10、round13 |
| 4 | 至少 2-3 个生产级项目复验通过 | 达到 | T22-T24、round14、round16 |
| 5 | 平均分 >= 85，且无 P0/P1 | 当前样本达到，需最终复算 | `VALIDATION.md` 阶段目标进度、T35、T37、T39、T42 |
| 6 | 写操作、DDL/DML、配置变更、测试修复全部满足确认门禁 | 规则达到；真实执行闭环未满足 | T26-T34、T37、T40-T41；缺 T29 执行结果 |
| 7 | 新技术栈必须先走 generic 兜底，再通过真实项目验收后升级 profile Level | 规则达到，需持续执行 | T36、`profiles/_schema.md` |
| 8 | 真实 agent 对话复测可以委派 subagent 完成 | 达到 | round13、T26 |

## 测试记录分组

| 分组 | 记录 | 用途 |
|------|------|------|
| 首轮多栈 full | T01-T12 | Java、Node/Prisma、FastAPI、Go/Gin、.NET/EF、React/Vite、Next.js、Nuxt/Vue、monorepo 和负向场景 |
| light 第二变更 | T13-T21 | 同栈 light 判档能力，避免过度 full |
| 生产级复验 | T22-T24 | RuoYi、eShopOnWeb、Go RealWorld |
| 苏格拉底与行为门禁 | T25-T26、round12、round15 | 多轮提问、写操作/DDL/DML/配置/测试修复门禁 |
| Phase 5 闭环准备 | T27-T34、T40-T41 | 执行记录模板、闭环标准、Go RealWorld 演练包、基线、Step 确认、自动续跑边界、执行前门禁和 dry-run |
| 投产升级机制 | T35-T39、T42 | readiness checklist、profile 晋级协议、最终复审模板、验证索引、评分复算模板、rollout policy |
| 历史汇总 rounds | round1-round17 | 多轮补强摘要、前端运行时、生产复验和 Next.js DB build 证据 |

## 关键文件

| 文件 | 作用 |
|------|------|
| `../VALIDATION.md` | 总体验收方案、评分标准、投产门槛 |
| `../README.md` | 用户视角能力边界和验收状态 |
| `../SKILL.md` | impact-pro 执行规则 |
| `../templates/phase5-preflight.md` | Phase 5 执行前门禁模板 |
| `../templates/execution-record.md` | Phase 5 执行记录模板 |
| `../templates/final-readiness-audit.md` | 最终投产复审模板 |
| `../templates/scorecard.md` | 最终评分复算模板 |
| `../profiles/_schema.md` | profile Level 和晋级协议 |

## 下一步入口

若要继续冲刺“多栈常规项目可投入使用”，下一步不是新增文档，而是完成 T29 或等价真实项目的 Phase 5 写操作闭环：

```text
确认 Step 1
确认 Step 2
确认 Step 4
```

在没有上述 Step 级确认前，只能继续执行只读分析、验证命令和主仓文档/规则补强，不能写外部验证项目。
