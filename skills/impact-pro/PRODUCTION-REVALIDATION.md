# Profile 生产级复验协议 + 状态

> 本手册聚焦 impact-pro 的 **profile 生产级复验**。三 skill 各自的通用复验手册:[pathfinder](../pathfinder/REVALIDATION.md) · [impact](../impact/REVALIDATION.md) · impact-pro(profile 见本文件)。

> Level 1 profile 的 globs/commands/style_axes 是在**单一 demo/模板项目**上首轮验证的。要宣称"生产级可用",必须在本协议定义的真实项目复验上通过。本文是 honest 的状态看板:哪些 profile 已生产级、哪些仍 demo-only、各自还差什么。

## 1. demo 验证 vs 生产级复验

| 维度 | demo 验证(首轮) | 生产级复验 |
|---|---|---|
| 项目 | 官方 tutorial / 模板 / 极简样本 | 有真实复杂度的开源/内部项目(多模块、真实 schema、历史包袱) |
| 跑分 | 静态/L0 通过 + 1 次 full | full + light **各 ≥1**,在 ≥2 个不同真实项目上 |
| 验证命令 | profile 自报的 commands 在 demo 上能跑 | 命令在真项目上**实跑**通过(build/test/lint),不是"应该能跑" |
| discovery_globs | 命中 demo 的文件 | 在真项目命中**正确**文件,无误报/漏报 |
| 风格/约束 | demo 里的模式 | 真项目的实际模式(style_axes 不打架) |
| 降级 | 无 DB 时标注 | 真 project 无 DB/MCP 时**诚实降级**,未确认项显式标注 |
| 记录 | validation-runs/ 一条 | validation-runs/ 一条 + eval/runs/ 评分卡,judge 注明 runner_model |

## 2. 复验 checklist(每个 profile 升级到生产级必须全过)

- [ ] 选 ≥2 个真实项目(非 demo/模板),clone + pin commit
- [ ] full 档:跑完 Phase 1-5(或 1-4 + Phase 5 真执行低风险写),产出 change-impact 文档
- [ ] light 档:跑完一页摘要 + 执行前检查
- [ ] profile 的 `commands.build/test/lint` 在真项目**实跑通过**(贴真实输出)
- [ ] `discovery_globs` 命中真项目的真实文件(无误报/漏报,贴命中清单)
- [ ] `style_axes` 与真项目实际模式一致(不打架)
- [ ] DB 发现:有 DB 连接时验证 schema 查询正确;无 DB 时诚实降级 + 未确认项标注
- [ ] 边界场景(edge_cases)逐条在真项目核对
- [ ] 记录写入 `validation-runs/` + 评分卡写 `eval/runs/`(注 runner_model)
- [ ] 更新本文件第 4 节状态表 + profile 自身 limitations

## 3. 升级路径

`generic 兜底` → demo 首轮(现有 Level 1)→ **生产级复验(本协议)** → 可标 production-validated。
未完成生产级复验的 profile:**可用,但用户需对 globs/命令/风格的命中做人工复核**(尤其弱模型下)。

---

## 4. 状态看板(2026-06-14)

| profile | level | 验证项目 | 生产级? | 关键 gap(升级到生产级还差什么) |
|---|---|---|---|---|
| **java-spring-mybatis** | 2 | RuoYi-Vue(真项目) | ✅ 是 | MyBatis-Plus 逻辑/Spring Security 细节/enum 位置仍需人工(已在 limitations 标注) |
| **dotnet-aspnet-efcore** | 1 | eShopOnWeb(Clean Architecture) | ✅ 是(单项目) | 极简 Web API / Minimal API / Razor Pages 混存需补;建议第 2 个真项目 |
| **go-gin-gorm** | 1 | Go RealWorld | ✅ 是(单项目) | 仅 SQLite 样本,**PG/MySQL 迁移工具未验**;AutoMigrate 项目回滚方案需人工;建议第 2 个真项目 |
| **node-express-prisma** | 1 | prisma-testing-express(demo) | ❌ demo-only | 需 ≥2 真实 Node/Prisma 项目;Fastify/NestJS 未验;Prisma 7 generator 运行时识别未验 |
| **python-fastapi-sqlmodel** | 1 | full-stack-fastapi-template(demo) | ❌ demo-only | 需 ≥2 真实 FastAPI 项目;纯 SQLAlchemy(非 SQLModel)未验;schema/model 多文件分离未验 |
| **frontend-react-vite** | 1 | demo | ❌ demo-only | 需 ≥2 真实 React/Vite 项目;generated client 追踪/主题认证路由未在真项目验 |
| **frontend-nextjs** | 1 | next-learn(demo) | ❌ demo-only | 自述"尚未在生产级 Next monorepo 复验";Server/Client 边界、SSL Postgres、Server Actions/DB 风险均需真项目验 |
| **frontend-nuxt-vue** | 1 | nuxt-ui-dashboard(demo) | ❌ demo-only | 自述"尚未覆盖生产级 Nuxt 后端写入和数据库迁移";`.server/.client.vue` 边界、Nuxt 3/4 目录差异需真项目验 |
| generic | 兜底 | — | n/a(设计为兜底) | 永远是兜底,不升级 |

## 5. 优先级建议

按"日常使用频率 × 当前 gap 风险"排序,生产级复验的下一批优先做:
1. **node-express-prisma**(Prisma 极常见,且 PG adapter 刚加,Prisma+PG 是主力组合)
2. **python-fastapi-sqlmodel**(FastAPI 后端常见,SQLModel/SQLAlchemy 覆盖)
3. **frontend-nextjs**(Next.js 极常见,但 Server/Client 边界 + DB 风险最易踩坑,demo 最不够)

每个复验按第 2 节 checklist 跑,产出 validation-runs/ + eval/runs/ 评分卡,回填本表。

---

## 6. 与"模型敏感性"的关系

生产级复验用**强模型**(Opus / 同级)跑,验证的是 profile 规则本身是否正确。
**弱模型**(Sonnet/Haiku)在 production-validated profile 上仍可能命中不准、证据不实——那是模型方差(见各 README 模型敏感性段 + `eval/runs/2026-06-14-pathfinder-control/`),不是 profile 缺口。两者分别处理。
