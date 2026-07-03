# monorepo-full-stack-starter runner report

## Fixture

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-non-git`
- `E:\agent\real-project-fixtures\monorepo-api-subdir`
- `E:\agent\blue-skillhub` was not modified or committed by the runner.

## Commands run

- Read-only inspection: `Get-Content -Raw`, `Select-String`, `rg --files`, `rg -n`, `Get-Date -Format ...`, `git -C ... rev-parse --short HEAD`.
- Pathfinder facts scripts:
  - `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py ...`
  - `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py ...`
- Pathfinder validation:
  - First `pf_validate.py`: all 3 Pathfinder maps exited `1`, due to Mermaid solid-arrow source nodes missing from body text.
  - Second `pf_validate.py`: all 3 Pathfinder maps exited `0`.
- Key results:
  - Git root: `21fbd77`
  - Full non-Git copy: `is_git_repo=false`, `head_short=null`
  - API subdir copy: `is_git_repo=false`, `head_short=null`
  - All three `pf_scan.py` runs produced facts successfully.

## Files written

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\git.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-non-git\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-non-git\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-non-git\change-impact\_project-map\facts\git.json`
- `E:\agent\real-project-fixtures\monorepo-api-subdir\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-api-subdir\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-api-subdir\change-impact\_project-map\facts\git.json`

## Case outputs

### monorepo-full-stack-starter-pathfinder

- prompt: `我准备改这个 full-stack-starter-kit。请先在仓库根目录只读生成项目地图，然后在删除 .git 的副本里再跑一次，重点关注 workspace 边界、shared types、API、Prisma、前端，以及无 Git 时哪些信息必须降级。`
- raw answer: 这是一个 152 文件的小型 monorepo，workspace 边界清楚，`apps/web`、`apps/api`、`packages/auth`、`packages/db`、`packages/shared`、`packages/ui`、`packages/config` 都能从文件和脚本里对上；Git 根目录有 `HEAD=21fbd77`，无 Git 副本把 head/branch/hotspots 正确降级为空，build/test/db 命令也都能从根脚本和各包脚本里找到。
- commands/evidence: `pf_scan.py`, `pf_git.py`, and `pf_validate.py` two rounds; evidence mainly from `package.json`, `pnpm-workspace.yaml`, `apps/api/src/app.ts`, `apps/web/src/routes/*`, `packages/db/prisma/schema/*`, `packages/shared/src/*`, and `packages/auth/src/*`.
- runner notes: First validator run only failed on Mermaid node names; after adding body notes, the second run passed. Git-root and non-Git-copy differences were reasonable and recorded in the map headers.

### monorepo-full-stack-starter-impact-light

- prompt: `把前端登录按钮文案从 Sign in 改成 Log in。先只做影响分析，判断 light/full，并说明要查哪些 workspace 文件。`
- raw answer: 这是 `light`。证据只落在前端文案层：`apps/web/src/routes/index.tsx`、`apps/web/src/components/layout/layout.tsx`、`apps/web/src/routes/(auth)/sign-in.tsx` 里有 Sign in/Sign In 文本；没有碰到 API、Prisma schema、shared type 或认证流程本身。验证入口应从 workspace 根目录考虑，前端侧主要看 `apps/web` 的 build/lint/typecheck，必要时再看根脚本是否串联了 Turbo。
- commands/evidence: Read-only inspection of `apps/web` routes/layout, `apps/web/src/lib/api.ts`, `apps/web/src/lib/auth.ts`, `packages/shared` types/validators, and root scripts. No files were written.
- runner notes: The button-copy and auth-flow boundaries were kept separate.

### monorepo-full-stack-starter-impact-full

- prompt: `给用户资料新增 organization 字段，后端存储和返回，前端注册/资料页可填写，shared type 也要同步。先不要写代码，只做完整影响分析。`
- raw answer: 这是 `full`。因为它同时碰 DB schema、后端 API、shared types/validators、前端表单/展示、以及测试和生成物顺序；证据分别落在 `packages/db/prisma/schema/*`、`apps/api/src/routes/users.ts`、`apps/api/src/controllers/user.controller.ts`、`apps/api/src/services/user.service.ts`、`packages/shared/src/types/*`、`packages/shared/src/validators/*`、`apps/web/src/routes/(auth)/*`、`apps/web/src/hooks/api/users/*`.
- commands/evidence: Read-only analysis of workspace root scripts, Prisma schema, API route/controller/repository, frontend route/hooks, and shared types/validators. No files were written.
- runner notes: DB/API/shared/frontend were all in scope; not a copy-only change.

### monorepo-full-stack-starter-negative

- prompt: `我只把 apps/api 目录复制出来了，没有 .git。请给这个目录生成项目地图，不要管父仓库。`
- raw answer: 当前目录只有 API 子树，47 文件，`is_git_repo=false`，`head_short/head_full/branch` 都是空；父仓库的信息没有被读进来。这个目录还能看见 users/files/health/auth 中间件和测试，但 `@repo/auth`、`@repo/db`、`@repo/shared`、前端、UI、config、根脚本都不在本地，所以跨包判断必须降级成“未覆盖/待补证据”。
- commands/evidence: `pf_scan.py`, `pf_git.py`, and `pf_validate.py` two rounds; evidence from `src/app.ts`, `src/routes/*`, `src/controllers/*`, `src/services/*`, `src/repositories/*`, `src/middleware/*`, `src/tests/*`, and subdir `package.json`.
- runner notes: The negative case did not leak parent Git info; git facts had no branch/head/hotspots.
