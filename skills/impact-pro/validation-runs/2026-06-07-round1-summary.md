# impact-pro 首轮多栈验收总结

- 测试日期：2026-06-07
- 测试方式：真实开源项目静态验收 + 按当前 `SKILL.md` / profile / glob 规则 dry-run
- 测试工作区：`E:\agent\impact-pro-validation-work`
- 结论：**不通过成熟通用投产验收；可作为 Beta 分析辅助继续试跑**

## 样本项目

| 用例 | 项目 | Commit | 子目录 | 变更类型 |
|------|------|--------|--------|----------|
| T01 | RuoYi-Vue | `7da12b0c07d43a9fcdf86570b0e81ba16d70adf4` | 根目录 | Java/Spring/MyBatis full |
| T02 | prisma-examples | `663c23ca1a6c6f03d2ad0c67868020b560a172e4` | `orm/testing-express` | Node/Express/Prisma full |
| T03 | full-stack-fastapi-template | `38302d7492dbd158ed6cf499a6dd0bab6ad17141` | `backend` | FastAPI/SQLModel/Alembic full |
| T06 | full-stack-fastapi-template | `38302d7492dbd158ed6cf499a6dd0bab6ad17141` | `frontend` | React/Vite settings light |

## 评分结果

| 用例 | 分数 | 失败等级 | 结论 |
|------|------|----------|------|
| T01 Java/Spring/MyBatis | 94 | 无 | 通过 |
| T02 Node/Express/Prisma | 66 | P1 | 不通过 |
| T03 FastAPI/SQLModel | 80 | P2 | 有条件通过 |
| T06 React/Vite 前端 | 76 | P2 | 仅可辅助分析 |

平均分：`79.0`

未达到 `VALIDATION.md` 中的投产门槛：

- 未覆盖 5 个不同技术栈。
- 未达到至少 10 个用例。
- 平均分低于 85。
- 出现 1 个 P1 失败。

## 核心发现

### 1. Java profile 可用

`java-spring-mybatis` profile 在 RuoYi-Vue 上表现稳定，能命中 Service、Mapper XML、Mapper Java、Controller、domain/entity、SQL 和配置。它可以作为 `impact-pro` 的 Level 2 对照组。

### 2. generic 对 Node/Prisma 不够

当前 `generic` 的 `discovery_globs` 没有覆盖：

- `prisma/schema.prisma`
- `prisma.config.ts`
- `src/app.ts`
- `src/index.ts`
- 常见 Express/Fastify API 入口

在 `orm/testing-express` 中，当前 glob 主要只能命中 `tests/user.test.ts`，会漏掉核心 schema 和 API 文件。这是 P1，因为会导致影响分析基础证据缺失。

### 3. generic 对 Python/FastAPI 勉强可用，但会漏模型

FastAPI 样本能通过 `**/api/**/*.py` 找到 routes，通过 `**/alembic/**/*.py` 找到迁移，通过 `tests/**/*.py` 找到测试。但它会漏掉 `app/models.py`，因为当前模型 glob 是 `**/*Model*.py` / `**/*Schema*.py`，不匹配常见复数文件名 `models.py` / `schemas.py`。

### 4. generic 对现代前端覆盖不足

React/Vite 样本的核心文件是 `.tsx` 组件和 route 文件。当前 `generic` 主要能命中 `*.spec.ts`，但没有把 `**/*.tsx`、`src/routes/**/*.tsx`、`src/components/**/*.tsx` 纳入发现范围。

## 投产结论

```text
impact-pro 当前不能作为“成熟通用 Skill”投入使用。
```

可以使用的范围：

- Java/Spring/MyBatis 项目：可以试用，表现接近 `impact`。
- 非 Java 项目：可用于辅助梳理风险，但必须人工复核上下文发现。
- 执行阶段：不建议让它独立进入写操作或生产 DB 变更。

## 必须修复项

优先级 P1：

1. 新增 Node/Express/Prisma profile，覆盖 `schema.prisma`、`prisma.config.ts`、`src/app.ts`、`src/index.ts`、`tests/**/*.ts`。
2. 新增 Python/FastAPI/SQLModel profile，覆盖 `app/models.py`、`app/api/routes/**/*.py`、`app/crud.py`、`app/alembic/**/*.py`。
3. 新增 Frontend React/Vue profile，覆盖 `src/**/*.tsx`、`src/**/*.vue`、`src/routes/**`、`src/components/**`、Playwright/Vitest 测试。

优先级 P2：

1. 强化 `generic` 的“不确定项”输出，找不到 schema/API/model 时必须显式标红。
2. 判档规则增加“证据不足时不得判 light”的约束。
3. 文档模板增加“证据来源 / 未确认项”章节。

## 下一步建议

先修 profile，再进行第二轮验收。第二轮建议至少包含：

- T02 Node/Express/Prisma 复测
- T03 FastAPI/SQLModel 复测
- T06 React/Vite 复测
- 新增 Go/Gin/GORM
- 新增 .NET/EF Core

第二轮目标：平均分 >= 85，无 P0/P1。
