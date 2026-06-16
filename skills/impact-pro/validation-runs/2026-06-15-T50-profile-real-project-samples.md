# T50 Profile 真实项目样本池补位

日期：2026-06-15

## 触发原因

- 本轮补齐 `impact-pro` 未生产级 profile 的真实项目样本入口。
- 目标不是把 profile 直接晋级生产级，而是把下一轮 full/light 生产复验的候选项目从 demo/template 换成真实项目，并留下可核验证据。

## 环境

- Agent / 模型（runner_model）：Codex GPT-5
- 触发方式：只读 GitHub HEAD + raw 文件抽查
- 工作目录：`E:\agent\blue-skillhub`
- 写入范围：仅本验证记录、索引和状态文档

## 样本池

| profile | 真实项目样本 | HEAD | 只读证据 | 当前结论 |
|---|---|---|---|---|
| `python-fastapi-sqlmodel` | `open-webui/open-webui` | `02dc3e689ceac915a870b373318b99c029ddf603` | `backend/open_webui/main.py`、`backend/open_webui/internal/db.py`、`backend/open_webui/models/users.py` 存在；`backend/requirements.txt` 含 `fastapi==0.135.1`、`sqlalchemy[asyncio]==2.0.48`、`alembic==1.18.4`、`pydantic==2.12.5` | 可作为 FastAPI + SQLAlchemy/Alembic 真实项目样本；不宣称 SQLModel 路径已覆盖 |
| `frontend-nextjs` | `calcom/cal.com` | `dcd0da831f013be8b2a5767457ea6d187b352ccc` | `apps/web/pages/_app.tsx`、`apps/web/app/layout.tsx`、`packages/prisma/schema.prisma` 存在；根 `package.json` 含 Next/React/Prisma/Turbo 相关命令 | 可作为 Next.js App Router + Pages Router + Prisma monorepo 样本 |
| `frontend-nuxt-vue` | `nuxt/nuxt.com` | `4b353856d56366679294f5e7fc30eb0cb79ab78a` | `package.json`、`nuxt.config.ts`、`app/app.vue`、`app/pages/index.vue` 存在；`package.json` 含 `nuxt`、`@nuxt/ui`、`vue-tsc`、`vitest` | 可作为 Nuxt 4 + Vue + Nuxt UI 真实站点样本 |

## 本轮未做

- 未 clone 全仓库。
- 未运行 build/test/lint。
- 未执行 `/impact-pro` full/light 双变更。
- 未把上述 profile 从 demo-only 直接晋级生产级。

## 后续复验要求

每个 profile 晋级前仍需满足 `docs/skill-eval/REVALIDATION.md` 的生产级判据：

1. 至少 2 个真实项目。
2. full + light 各至少 1 个场景。
3. 真实项目 build/test/lint 有命令输出。
4. profile globs 命中正确文件，且误报/漏报记录清楚。
5. 无 DB/MCP 时诚实回退并保留未确认项。

## 结论

T50 通过：3 个未生产级 profile 已有真实项目样本池和只读框架证据。它降低了下一轮生产级复验选题成本，但不改变当前生产级状态。
