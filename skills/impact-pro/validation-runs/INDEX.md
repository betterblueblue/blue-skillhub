# impact-pro 验证记录索引

> 本索引用于快速定位证据。详细结论以对应 `Txx` / `round` 记录和 `VALIDATION.md` 为准。

## 当前总状态

```text
impact-pro = 多栈常规项目可投入使用（已验证 profile 覆盖范围内，受监督执行）。
```

当前边界：

- 不宣称覆盖任意技术栈。
- 不建议无人监督生产数据库变更。
- 新栈仍需 generic 兜底后再按 profile 晋级协议升级。

## 八条目标证据地图

| # | 成功标准 | 当前状态 | 主要证据 |
|---|----------|----------|----------|
| 1 | 不宣称覆盖任意技术栈，只宣称已验证 profile 覆盖范围内可用 | 达到 | `README.md`、`VALIDATION.md`、T36 |
| 2 | 至少 5 个不同技术栈，每栈完成 full + light 双变更验收 | 达到 | T01-T21 |
| 3 | T08-T10 等负向场景完成真实 agent 对话复测 | 达到 | T08-T10、round13、T47 |
| 4 | 至少 2-3 个生产级项目复验通过 | 达到 | T22-T24、round14、round16 |
| 5 | 平均分 >= 85，且无 P0/P1 | 达到 | T44 |
| 6 | 写操作、DDL/DML、配置变更、测试修复全部满足确认门禁 | 达到 | T26-T34、T37、T40-T43、外部 `090-execution-record.md` |
| 7 | 新技术栈必须先走 generic 兜底，再通过真实项目验收后升级 profile Level | 规则达到，需持续执行 | T36、`profiles/_schema.md` |
| 8 | 真实 agent 对话复测可以委派 subagent 完成 | 达到 | round13、T26 |

## 测试记录分组

| 分组 | 记录 | 用途 |
|------|------|------|
| 首轮多栈 full | T01-T12 | Java、Node/Prisma、FastAPI、Go/Gin、.NET/EF、React/Vite、Next.js、Nuxt/Vue、monorepo 和负向场景 |
| light 第二变更 | T13-T21 | 同栈 light 判档能力，避免过度 full |
| 生产级复验 | T22-T24 | RuoYi、eShopOnWeb、Go RealWorld |
| 苏格拉底与行为门禁 | T25-T26、round12、round15 | 多轮提问、写操作/DDL/DML/配置/测试修复门禁 |
| Phase 5 闭环 | T27-T34、T40-T43 | 执行记录模板、闭环标准、Go RealWorld 演练包、基线、Step 确认、自动续跑边界、执行前门禁、dry-run、真实执行闭环 |
| 投产升级机制 | T35-T39、T42、T44-T45 | readiness checklist、profile 晋级协议、最终复审模板、验证索引、评分复算模板、rollout policy、最终评分和最终审计 |
| Context Pack | T46 | 上下文包协议、profile `context_discovery`、相关性分级、上下文预算和写入门禁 |
| M3 响应契约 RG3 复测 | T47 | Node/Express 响应字段删除负向场景，验证 full 判档、接口返回检查清单和 V1/V3 区分 |
| M3 前端/monorepo RG3 复测 | T48 | React/Vite UI-only light、monorepo 前后端边界；补强只分析最小响应契约 |
| 多会话写授权一致性 | T49 | Node/Express 响应契约场景通过；同步补强写入目标边界、执行记录补齐和 V1-only 暂停规则，并通过修复后 S7 回归 |
| profile 真实项目样本池 | T50 | 为 FastAPI、Next.js、Nuxt/Vue 未生产级 profile 补 3 个真实项目样本和只读框架证据；不改变生产级状态 |
| 历史汇总 rounds | round1-round17 | 多轮补强摘要、前端运行时、生产复验和 Next.js DB build 证据 |

## 关键文件

| 文件 | 作用 |
|------|------|
| `../VALIDATION.md` | 总体验收方案、评分标准、投产门槛 |
| `../README.md` | 用户视角能力边界和验收状态 |
| `../SKILL.md` | impact-pro 执行规则 |
| `../templates/060-preflight.md` | Phase 5 执行前门禁模板 |
| `../templates/000-context-pack.md` | Context Pack 模板 |
| `../templates/090-execution-record.md` | Phase 5 执行记录模板 |
| `../templates/final-readiness-audit.md` | 最终投产复审模板 |
| `../templates/scorecard.md` | 最终评分复算模板 |
| `../profiles/_schema.md` | profile Level 和晋级协议 |

## 下一步入口

后续建议继续扩展生产级样本、提高 Level 2/3 profile 覆盖，并保持 R2 rollout 边界：受监督执行、Step 级确认、证据化分析和 profile 覆盖声明。
