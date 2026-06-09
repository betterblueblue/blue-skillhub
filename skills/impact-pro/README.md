# ImpactRadar Pro — 现有系统多栈变更影响分析

## 这个 Skill 是干什么的

面向已验证技术栈规则覆盖范围内的多栈现有系统，把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成证据化的影响分析；加载专属规则，未知栈先用通用规则兜底扫描，按 light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。新功能开发指的是接入现有系统的新功能，不是空项目脚手架。

它可以搭配 `RuleBlade` 使用：`RuleBlade` 提供通用编码行为约束，`impact-pro` 负责多栈 profile 化上下文发现、影响分析、文档产出和受监督执行流程。

## 核心能力

- **通用内核 + 技术栈规则** — 无栈假设，按需加载专属规则
- **Context Pack** — 用 L1/L2/L3 分层探索，给后续 agent 一个小而准、可解释的上下文入口
- **引用检查分级** — 改前反查调用方、引用方、注册点、生成物和测试，按必须同步修改 / 需要用户决策 / 只需验证 / 暂不纳入处理
- **长期目标模式** — 面对迁移、对齐、重构、大功能接入、债务清理等多 Step 任务，维护当前 Step、backlog、阻塞项和未验证项
- **跨系统对齐规则** — 记录可信来源、目标实现、对齐语义、差距证据和本 Step 范围，避免凭相似命名臆测
- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，按风险多轮收敛；每轮最多 3 问，不是总共最多 3 问
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档
- **接口返回检查清单** — light 涉及向后兼容响应字段新增时，检查消费者、文档、generated client、验证方式和未验证项
- **证据化分析** — 用工具发现真实上下文，不靠臆测
- **验证等级** — 区分 V0 未验证、V1 静态验证、V2 构建/单测、V3 运行路径验证
- **数据库适配器** — MySQL + 通用 SQL 规则（PG 等其他 DB 走通用规则）
- **19 维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求 → 设计 → 实施，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都询问
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **TDD 验证框架** — 正向用例 + 错误用例（边界值/空值/格式校验/XSS）
- **行为准则检查** — 先澄清假设和成功标准，简单优先，精准修改，改 status/enum/常量前先确认原定义
- **阻塞恢复安全闸** — blocked、上下文压缩或延迟确认后，先复核 pending Step、当前文件状态和最新授权，再决定是否执行

## 技术栈覆盖

| 技术栈规则 | 等级 | 说明 |
|---------|-------|------|
| generic | — | 通用兜底规则，扫描目录结构；用于未知栈首轮分析，不等同于专属规则已验证 |
| java-spring-mybatis | 2 | Java/Spring/MyBatis/RuoYi，已深度覆盖 |
| node-express-prisma | 1 | Node.js/TypeScript + Express/Fastify + Prisma，已在 prisma-examples 上首轮验证 |
| python-fastapi-sqlmodel | 1 | FastAPI + SQLModel/SQLAlchemy + Alembic，已在 full-stack-fastapi-template 后端首轮验证 |
| frontend-react-vite | 1 | React + Vite + TypeScript 前端，已在 full-stack-fastapi-template 前端首轮验证 |
| frontend-nextjs | 1 | Next.js App Router / Pages Router，已在 vercel/next-learn 上首轮静态验证 |
| frontend-nuxt-vue | 1 | Nuxt 4 + Vue 3 + Nuxt UI，已在 nuxt-ui-templates/dashboard 上首轮静态验证 |
| go-gin-gorm | 1 | Go + Gin + GORM，已在 golang-gin-realworld-example-app 上首轮验证 |
| dotnet-aspnet-efcore | 1 | ASP.NET Core + EF Core，已在 eShopOnWeb 上首轮验证 |

generic 是通用兜底规则，专属规则负责真实项目里更稳定的文件发现和验证策略。新技术栈必须先用 generic 兜底并保留限制说明；只有完成真实项目 full + light 验收、验证命令可执行、记录写入 `validation-runs/` 后，才能升级为 Level 1 专属规则。Level 2 需要多个真实项目积累。

## 触发方式

在 Claude Code 终端输入 `/impact-pro` 激活。

## 与 impact 的区别

| | impact | impact-pro |
|--|------------|------------|
| 架构 | 单体 SKILL.md，Java 规则写死 | 通用内核 + 技术栈规则 |
| 栈适配 | 仅 Java/MyBatis | 通用规则 + 专属规则 |
| 扩展方式 | 修改 SKILL.md | 新增技术栈规则文件 |
| 数据库 | 仅 MySQL | MySQL + 通用数据库规则 |

## 验收状态

当前 `impact-pro` 已完成 T01-T49 验收，覆盖多栈静态验收、前端运行时复测、负向对话复测、生产级项目复验、Step 编号确认、执行前检查、Go RealWorld 真实写操作闭环、最终复审、Claude Code + MiniMax M3 真实 `/impact-pro` 响应契约复测，以及多会话写授权一致性复测。T49 验证 Node/Express 响应字段删除不会被误判为 Java 场景，也验证了无 `确认 Step N` 不会写文件；同时同步补强写入目标边界、执行记录随 Step 补齐和 V1-only 暂停规则。补齐 Level 1 技术栈规则后，Node/Express/Prisma、FastAPI/SQLModel、React/Vite、Next.js、Nuxt/Vue、Go/Gin/GORM、ASP.NET Core/EF Core、monorepo 和三类负向场景均已进入已验证覆盖范围。当前可按 **多栈常规项目可投入使用（已验证技术栈规则覆盖范围内，必须由用户确认后执行）** 使用；仍不宣称覆盖任意技术栈，也不建议无人监督生产数据库变更。

多栈测试用例、评分标准、行为准则检查和使用边界见 [VALIDATION.md](VALIDATION.md)，优化后回归复测协议见 [../../docs/impact-regression-protocol.md](../../docs/impact-regression-protocol.md)，实际验收记录索引见 [validation-runs/INDEX.md](validation-runs/INDEX.md)。

## 典型流程

```
你：我想给用户表加一个个性签名字段
↓
Phase 2：栈探测 → 加载对应技术栈规则 → 构建 Context Pack
↓
Phase 2.5：初步风险预判（不最终定档）
↓
Phase 3：靶向提问（字段长度？哪些接口？缓存？迁移脚本？）
↓
Phase 3.5：Agent 基于证据建议 light/full，用户复核确认
↓
Phase 4：输出文档（light 一页 / full 三文档逐份确认）
↓
Phase 5：执行（每步确认，写前检查目标路径，按证据运行验证）
```

## light / full 如何判定

判档按风险触发，不按文件数量粗暴决定。

**light** 适合：UI 文案、toast、placeholder、局部样式、单 handler 自然语言 message、前端本地状态展示、文档/日志文案等。前提是证据显示不改 DB schema、API 契约、权限/认证、状态机、generated client、外部服务副作用，也没有破坏兼容。

兼容性新增 API 响应字段可以建议 light，但必须填写接口返回检查清单；删除/重命名字段、语义或类型变化、generated client/OpenAPI/SDK 需要同步、外部消费者不明、历史数据/缓存/持久化快照或前后端必须同步修改时，仍应 full 或先补证据。

**full** 适合：DB/migration/索引/外键/存量数据、API/DTO/OpenAPI/GraphQL 契约、权限/认证/支付/订单/状态机、跨前后端联动、缓存/消息队列/异步任务/文件/邮件/短信/第三方 API、删除/重命名/DROP/批量替换/破坏兼容，以及高风险区域证据不足。

判档由 Agent 基于证据先行建议，用户复核确认。时机是在 Context Pack 和苏格拉底式澄清之后；Phase 2.5 只做初步风险预判，不最终定档。正式判档时必须列出：允许 light 的证据、触发 full 的证据、未确认项。用户可以要求简化输出，但不能跳过 Context Pack、分析依据、安全检查、写操作确认和验证方案。

## 苏格拉底式提问如何控量

`每轮 ≤ 3 问` 是用户体验上限，不是总问题数上限。light 通常 0-1 轮；full 通常 1-3 轮；高风险 full 最多 5 轮。超过 5 轮仍不清晰时，不继续消耗用户耐心，而是输出“已确认 / 未确认 / 建议默认 / 必须用户拍板”。

问题按风险分级：P0 必问、P1 应问、P2 可默认、P3 可延后。P0/P1 未确认项不能被默认值悄悄吞掉。

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核
├── README.md             # 本文件
├── VALIDATION.md         # 多栈测试验收方案
├── profiles/             # 技术栈规则
│   ├── _schema.md        # 技术栈规则接口
│   ├── _template.md      # 新技术栈规则模板
│   ├── generic.md         # 未知栈兜底扫描
│   ├── java-spring-mybatis.md  # Java/Spring/MyBatis (Level 2)
│   ├── node-express-prisma.md  # Node/Express/Prisma (Level 1)
│   ├── python-fastapi-sqlmodel.md # FastAPI/SQLModel (Level 1)
│   ├── frontend-react-vite.md  # React/Vite 前端 (Level 1)
│   ├── frontend-nextjs.md      # Next.js App Router/Pages Router (Level 1)
│   ├── frontend-nuxt-vue.md    # Nuxt/Vue 前端 (Level 1)
│   ├── go-gin-gorm.md       # Go/Gin/GORM (Level 1)
│   └── dotnet-aspnet-efcore.md # ASP.NET Core/EF Core (Level 1)
├── db-adapters/          # 数据库适配器
│   ├── generic-sql.md    # 通用 SQL 模板
│   └── mysql.md          # MySQL 专用
└── templates/            # 文档模板
    ├── context-pack.md
    ├── light.md
    ├── requirements.md
    ├── design.md
    ├── implementation.md
    ├── phase5-preflight.md
    ├── execution-record.md
    ├── final-readiness-audit.md
    └── scorecard.md
```

## 致谢

“引用检查分级”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue：改代码前应检查其他地方是否引用，查到后再分级处理。这个建议已纳入 `RuleBlade` 和 `impact-pro` 的 Context Pack 流程，用来减少多栈项目里漏掉调用方、注册点、生成物或测试的风险。

长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 降级保护、阻塞恢复安全闸、多会话写授权一致性和执行记录补强，来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。该案例也被用于 `impact-pro` 的规则回迁分析，帮助确认这些边界并不只存在于 Java/RuoYi 场景。
