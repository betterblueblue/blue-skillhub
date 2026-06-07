# ImpactRadar Pro — 现有系统多栈变更影响分析

## 这个 Skill 是干什么的

面向已验证 profile 覆盖范围内的多栈现有系统，把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成证据化的影响分析；加载专属规则，未知栈先用 generic 兜底扫描，按 light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。新功能开发指的是接入现有系统的新功能，不是空项目脚手架。

## 核心能力

- **通用内核 + 技术栈 profile** — 无栈假设，profile 按需加载
- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，按风险多轮收敛；每轮最多 3 问，不是总共最多 3 问
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档
- **证据化分析** — 用工具发现真实上下文，不靠臆测
- **DB adapter 系统** — MySQL + generic SQL adapter（PG 等其他 DB 走 generic）
- **19 维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求 → 设计 → 实施，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都询问
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **TDD 验证框架** — 正向用例 + 错误用例（边界值/空值/格式校验/XSS）
- **行为准则门禁** — 先澄清假设和成功标准，简单优先，精准修改，改 status/enum/常量前先确认原定义

## 技术栈覆盖

| Profile | Level | 说明 |
|---------|-------|------|
| generic | — | 强兜底，扫描目录结构；用于未知栈首轮分析，不等同于专属 profile 已验证 |
| java-spring-mybatis | 2 | Java/Spring/MyBatis/RuoYi，已深度覆盖 |
| node-express-prisma | 1 | Node.js/TypeScript + Express/Fastify + Prisma，已在 prisma-examples 上首轮验证 |
| python-fastapi-sqlmodel | 1 | FastAPI + SQLModel/SQLAlchemy + Alembic，已在 full-stack-fastapi-template 后端首轮验证 |
| frontend-react-vite | 1 | React + Vite + TypeScript 前端，已在 full-stack-fastapi-template 前端首轮验证 |
| frontend-nextjs | 1 | Next.js App Router / Pages Router，已在 vercel/next-learn 上首轮静态验证 |
| frontend-nuxt-vue | 1 | Nuxt 4 + Vue 3 + Nuxt UI，已在 nuxt-ui-templates/dashboard 上首轮静态验证 |
| go-gin-gorm | 1 | Go + Gin + GORM，已在 golang-gin-realworld-example-app 上首轮验证 |
| dotnet-aspnet-efcore | 1 | ASP.NET Core + EF Core，已在 eShopOnWeb 上首轮验证 |

generic 是兜底能力，专属 profile 负责真实项目里更稳定的文件发现和验证策略。新技术栈必须先走 generic 兜底并保留限制说明；只有完成真实项目 full + light 验收、验证命令可执行、记录写入 `validation-runs/` 后，才能升级为 Level 1 专属 profile。Level 2 需要多个真实项目积累。

## 触发方式

在 Claude Code 终端输入 `/impact-pro` 激活。

## 与 impact v3.0 的区别

| | impact v3.0 | impact-pro |
|--|------------|------------|
| 架构 | 单体 SKILL.md，Java 规则写死 | 通用内核 + profile 系统 |
| 栈适配 | 仅 Java/MyBatis | 通用 + 专属 profile |
| 扩展方式 | 修改 SKILL.md | 新增 profile 文件 |
| 数据库 | 仅 MySQL | MySQL + generic adapter |

## 验收状态

当前 `impact-pro` 已完成多栈静态验收、前端运行时复测、主要样本第二变更验收、T08-T10 独立 subagent 负向对话复测、第一轮生产级项目复验、T25 多轮苏格拉底提问压力测试、T26 执行阶段门禁压力复测、T27 执行记录模板补强、T28 Phase 5 闭环验收标准补强、T29 Go RealWorld 执行演练包准备、T30 Go RealWorld 演练前基线验证、T31 Step 编号确认协议补强、T32 长期目标达成度审计、T33 Phase 5 执行确认包、T34 Docker 恢复后的基线复验与自动续跑确认边界、T35 投产升级 checklist、T36 profile 晋级协议补强、T37 最终复审模板、T38 验证记录索引、T39 最终评分复算模板、T40 Phase 5 执行前门禁模板、T41 Go RealWorld preflight dry-run、T42 分阶段 rollout policy、T43 Go RealWorld Phase 5 真实执行闭环、T44 最终评分复算，以及 T45 最终投产复审，覆盖 T01-T45 用例。补齐 Level 1 profile 后，Node/Express/Prisma、FastAPI/SQLModel、React/Vite、Next.js、Nuxt/Vue、Go/Gin/GORM、ASP.NET Core/EF Core、monorepo 和三类负向场景均已进入已验证 profile 覆盖范围。当前可升级为 **多栈常规项目可投入使用（已验证 profile 覆盖范围内，受监督执行）**；仍不宣称覆盖任意技术栈，也不建议无人监督生产数据库变更。

多栈测试用例、评分标准、行为准则门禁和投产门槛见 [VALIDATION.md](VALIDATION.md)，实际验收记录索引见 [validation-runs/INDEX.md](validation-runs/INDEX.md)。

## 典型流程

```
你：我想给用户表加一个个性签名字段
↓
Phase 2：栈探测 → 加载对应 profile → 上下文发现
↓
Phase 2.5：初步风险预判（不最终定档）
↓
Phase 3：靶向提问（字段长度？哪些接口？缓存？迁移脚本？）
↓
Phase 3.5：Agent 基于证据建议 light/full，用户复核确认
↓
Phase 4：输出文档（light 一页 / full 三文档逐份确认）
↓
Phase 5：执行（每步确认，自动跑风格检查+单测）
```

## light / full 如何判定

判档按风险触发，不按文件数量粗暴决定。

**light** 适合：UI 文案、toast、placeholder、局部样式、单 handler 自然语言 message、前端本地状态展示、文档/日志文案等。前提是证据显示不改 DB schema、API 契约、权限/认证、状态机、generated client、外部服务副作用，也没有破坏兼容。

**full** 适合：DB/migration/索引/外键/存量数据、API/DTO/OpenAPI/GraphQL 契约、权限/认证/支付/订单/状态机、跨前后端联动、缓存/消息队列/异步任务/文件/邮件/短信/第三方 API、删除/重命名/DROP/批量替换/破坏兼容，以及高风险区域证据不足。

判档由 Agent 基于证据先行建议，用户复核确认。时机是在只读发现和苏格拉底式澄清之后；Phase 2.5 只做初步风险预判，不最终定档。正式判档时必须列出：允许 light 的证据、触发 full 的证据、未确认项。用户可以要求简化输出，但不能跳过分析依据、安全闸、写操作确认和验证方案。

## 苏格拉底式提问如何控量

`每轮 ≤ 3 问` 是用户体验上限，不是总问题数上限。light 通常 0-1 轮；full 通常 1-3 轮；高风险 full 最多 5 轮。超过 5 轮仍不清晰时，不继续消耗用户耐心，而是输出“已确认 / 未确认 / 建议默认 / 必须用户拍板”。

问题按风险分级：P0 必问、P1 应问、P2 可默认、P3 可延后。P0/P1 未确认项不能被默认值悄悄吞掉。

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核
├── README.md             # 本文件
├── VALIDATION.md         # 多栈测试验收方案
├── profiles/             # 技术栈 profile
│   ├── _schema.md        # profile 统一接口
│   ├── _template.md      # 新 profile 空白模板
│   ├── generic.md         # 未知栈兜底扫描
│   ├── java-spring-mybatis.md  # Java/Spring/MyBatis (Level 2)
│   ├── node-express-prisma.md  # Node/Express/Prisma (Level 1)
│   ├── python-fastapi-sqlmodel.md # FastAPI/SQLModel (Level 1)
│   ├── frontend-react-vite.md  # React/Vite 前端 (Level 1)
│   ├── frontend-nextjs.md      # Next.js App Router/Pages Router (Level 1)
│   ├── frontend-nuxt-vue.md    # Nuxt/Vue 前端 (Level 1)
│   ├── go-gin-gorm.md       # Go/Gin/GORM (Level 1)
│   └── dotnet-aspnet-efcore.md # ASP.NET Core/EF Core (Level 1)
├── db-adapters/          # 数据库 adapter
│   ├── generic-sql.md    # 通用 SQL 模板
│   └── mysql.md          # MySQL 专用
└── templates/            # 文档模板
    ├── light.md
    ├── requirements.md
    ├── design.md
    ├── implementation.md
    ├── phase5-preflight.md
    ├── execution-record.md
    ├── final-readiness-audit.md
    └── scorecard.md
```
