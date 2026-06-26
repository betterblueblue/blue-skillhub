# impact-pro 第二轮验收总结（补 profile 后）

- 测试日期：2026-06-07
- 测试方式：真实开源项目静态验收 + 新增 profile glob dry-run
- 测试工作区：`E:\agent\impact-pro-validation-work`
- 基于变更：新增 `node-express-prisma`、`python-fastapi-sqlmodel`、`frontend-react-vite`，并增强 `generic`
- 结论：**已从 Beta 分析辅助提升为“可试用”，但仍未达到成熟通用投产门槛**

## 第二轮评分

| 用例 | Round 1 | Round 2 | 失败等级 | 结论 |
|------|---------|---------|----------|------|
| T01 Java/Spring/MyBatis | 94 | 94 | 无 | 通过 |
| T02 Node/Express/Prisma | 66 | 88 | 无 | 有条件通过 |
| T03 FastAPI/SQLModel | 80 | 89 | 无 | 有条件通过 |
| T06 React/Vite 前端 | 76 | 88 | 无 | 有条件通过 |

平均分：`87.75`

相比第一轮：

- 平均分从 `79.0` 提升到 `87.75`。
- P1 从 1 个降为 0 个。
- P2 从 2 个降为 0 个。

## 命中检查

### T02 Node/Express/Prisma

新增 `node-express-prisma` 后，核心文件均可命中：

| 类型 | 命中文件 |
|------|----------|
| Prisma schema | `prisma/schema.prisma` |
| Prisma config | `prisma.config.ts` |
| API 入口 | `src/app.ts` |
| 服务入口 | `src/index.ts` |
| 测试 | `tests/user.test.ts` |

首轮 P1 已修复。

剩余限制：

- 仅在 Express 样本验证，Fastify/NestJS 仍需单独验收。
- 无 DB 连接时只能读取 `schema.prisma`，不能确认真实行数和索引状态。

### T03 FastAPI/SQLModel

新增 `python-fastapi-sqlmodel` 后，核心文件均可命中：

| 类型 | 命中文件 |
|------|----------|
| Model/schema | `app/models.py` |
| CRUD | `app/crud.py` |
| API routes | `app/api/routes/items.py` 等 |
| API deps/main | `app/api/deps.py`、`app/api/main.py` |
| Alembic migrations | `app/alembic/versions/*.py` |
| Tests | `tests/api/routes/test_items.py` 等 |

首轮 P2 已修复。

剩余限制：

- 仅验证 SQLModel，纯 SQLAlchemy declarative 项目还需测试。
- `models.py` 同时包含 DB model 和 API schema，执行时仍需区分 `table=True`。

### T06 React/Vite 前端

新增 `frontend-react-vite` 后，核心文件均可命中：

| 类型 | 命中文件 |
|------|----------|
| App entry | `src/main.tsx` |
| Routes | `src/routes/**/*.tsx` |
| Components | `src/components/**/*.tsx` |
| Theme/CSS | `src/index.css` |
| Playwright | `tests/**/*.spec.ts` |
| Config | `package.json`、`vite.config.ts`、`playwright.config.ts` |

首轮 P2 已修复。

剩余限制：

- 仅验证 React/Vite，Vue/Nuxt/Next.js 仍需新增或扩展 profile。
- 前端-only 变更必须避免生成 DB/SQL 章节，这仍依赖执行时按维度裁剪模板。

## 投产判断

当前判定：

```text
impact-pro = 可试用，但还不是成熟通用版。
```

可以提升的使用范围：

- Java/Spring/MyBatis：可常规试用。
- Node/Express/Prisma：可试用，需人工复核 DB 和迁移。
- FastAPI/SQLModel：可试用，需人工复核 model/schema 区分。
- React/Vite：可试用，需人工复核 UI/视觉验收。

仍不能宣称：

```text
覆盖任意技术栈，可直接投入生产执行。
```

原因：

- 目前只有 4 个用例，不满足 `VALIDATION.md` 的 10 用例门槛。
- 尚未覆盖 Go/Gin/GORM、.NET/EF Core、Vue/Nuxt/Next.js、monorepo 复杂场景。
- 本轮只做静态 dry-run，未执行完整 agent 对话和写操作确认流程。

## 后续必须补测

进入正式投产前，至少再补：

1. Go / Gin / GORM：验证 handler/service/model/migration。
2. .NET / ASP.NET Core / EF Core：验证 Controller/DbContext/Entity/Migration。
3. Vue 或 Nuxt：验证 `.vue` 单文件组件和 Pinia/Vue Router。
4. Next.js：验证 App Router、server action、API route。
5. 混合 monorepo：验证多 profile 协作。
6. 负向测试：直接删除接口、证据不足、无 DB 权限。

## 新增 profile 评级

| Profile | 当前 Level | 晋升条件 |
|---------|-------------|----------|
| node-express-prisma | 1 | 再通过 1 个 Express/Fastify 项目 + 1 个 NestJS/复杂项目 |
| python-fastapi-sqlmodel | 1 | 再通过 1 个 SQLModel 项目 + 1 个 SQLAlchemy declarative 项目 |
| frontend-react-vite | 1 | 再通过 1 个 React/Vite 项目 + 1 个 Next.js/React Router 项目 |

## 结论

第二轮说明新增 profile 有效解决了首轮核心问题。`impact-pro` 已经可以进入更大范围的真实试跑，但仍应保留 Beta/可试用标识，直到完成 10 用例矩阵。
