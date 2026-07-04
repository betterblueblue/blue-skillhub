# d12-composer-25fast-rerun-clean Pathfinder 评测记录

目标：在 `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean`（Git 根目录）只读生成项目地图，再在删除 `.git` 的副本 `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit` 重跑一次，并比较两次差异。

允许修改的文件：

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map\facts\git.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map\facts\git.json`

Skill hub 脚本：`E:\agent\blue-skillhub\skills\pathfinder\scripts\`

## 实际命令

### 1) Git 根目录

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map\facts\scan.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map\facts\git.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean
```

退出码：

- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` = `0`

关键输出摘要：

- `pf_scan.py`：`file_count: 152`，`budget_tier: 小仓`，`dir_tree` 覆盖 `apps/`、`packages/`、`scripts/`
- `pf_git.py`：`is_git_repo: true`，`is_independent_repo: true`，`head_short: 21fbd77`，`toplevel: E:/agent/real-project-fixtures/monorepo-full-stack-starter-d12-composer-rerun-clean`
- `pf_validate.py`：`SUMMARY: 10 passed, 0 failed, 0 warnings`

### 2) 删除 `.git` 的副本

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map\facts\scan.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map\facts\git.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit
```

退出码：

- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` = `0`

关键输出摘要：

- `pf_scan.py`：与 Git 根目录一致，`file_count: 152`，`budget_tier: 小仓`
- `pf_git.py`：`is_git_repo: false`，`is_independent_repo: false`，`toplevel: null`，`head_short/head_full/branch: null`
- `pf_validate.py`：`SUMMARY: 10 passed, 0 failed, 0 warnings`

## 两次差异

### 事实层（facts）

| 字段 | Git 根目录 | 非 Git 副本 |
|------|-----------|------------|
| `scan.json` file_count | 152 | 152（一致） |
| `scan.json` budget_tier | 小仓 | 小仓（一致） |
| `git.json` is_git_repo | true | false |
| `git.json` head_short | 21fbd77 | null |
| `git.json` toplevel | E:/agent/real-project-fixtures/monorepo-full-stack-starter-d12-composer-rerun-clean | null |
| `git.json` hotspots | [] | [] |

无 Git 时必须降级的信息：HEAD commit、branch、toplevel、hotspots、recent_commit_modules。`pf_scan.py` 输出不受影响。

### 地图头部

| 字段 | Git 根目录 | 非 Git 副本 |
|------|-----------|------------|
| 开头说明 | 标准 Pathfinder 说明 | 额外说明「当前副本已删除 `.git`，因此头部按非 Git 处理」 |
| 生成时间 | 2026-07-04 19:23:03 +08:00 | 2026-07-04 19:23:04 +08:00 |
| 基于 commit | **21fbd77**（真实 HEAD） | **非 Git,以扫描时间为准** |

### 结构内容

两份 `_project-map.md` 的 workspace 边界、shared types、API、Prisma、前端、风险点、【14】代码风格观察等 15 个核心节内容一致；差异仅在头部 Git 归属与开头说明。

## 关注重点摘要（两份地图一致）

### Workspace 边界

- `pnpm-workspace.yaml` 声明 `apps/*` 和 `packages/*` 两个 glob。
- 运行时主应用：`apps/web`（`@repo/web`）、`apps/api`（`@repo/api`）。
- 共享包：`packages/db`、`packages/auth`、`packages/shared`、`packages/ui`、`packages/config`。
- Turbo 在根目录统一编排 `dev` / `build` / `lint` / `typecheck`。

### Shared types

- `@repo/shared` 通过 `exports` 暴露 `./types`、`./validators`、`./utils`。
- `User` / `File` 类型直接基于 Prisma payload（`Prisma.UserGetPayload`），schema 变更后需 `db:generate`。
- `ApiResponse<T>`、`PaginatedResponse<T>` 在 `packages/shared/src/types/api.ts` 定义，前后端共用。

### API

- Express 入口 `apps/api/src/app.ts`：中间件链 → `/health` → `/api/auth/*`（Better Auth）→ `/api` 业务路由。
- 业务路由：`/api/users`（CRUD + `/me`）、`/api/files`（上传/预签名/元数据）。
- 统一响应格式 `{ success, data/error }`，`requireAuth` 保护业务路由。

### Prisma

- `prismaSchemaFolder` 模式，schema 拆在 `packages/db/prisma/schema/*.prisma`。
- 实体：User、Session、Account、Verification（auth）、File（上传）。
- Prisma 命令通过 `apps/api/.env` 加载环境变量。

### 前端

- Vite + TanStack Router（文件路由）+ TanStack Query。
- `apps/web/src/lib/api.ts` 封装 fetch（`credentials: 'include'`）。
- `apps/web/src/lib/auth.ts` 基于 `@repo/auth/client`，baseURL 指向 API `/auth`。
- `(app)` 路由组 `beforeLoad` 做会话保护。

## 生成结果

- Git 根目录项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map.md`
- 非 Git 副本项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map.md`

## 判分方复核

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer-rerun-clean-nongit
```

两条命令退出码均为 `0`，摘要均为 `SUMMARY: 10 passed, 0 failed, 0 warnings`。非 Git 副本的 `facts/git.json` 为 `is_git_repo=false`，且 `head_short/head_full/branch/hotspots/recent_commit_modules` 均为空，未发现父仓库 Git 信息污染。

## 判分方补充复核

判定：`PASS-WARN`

好的部分：

- 两份地图都通过 `pf_validate.py`，均为 `10 passed, 0 failed, 0 warnings`。
- Git 根目录 facts 正确记录 `head_short=21fbd77`；非 Git 副本 facts 正确降级为 `head_short/head_full/branch=null`，`hotspots/recent_commit_modules=[]`。
- Git 副本源码未改；非 Git 副本与 Git 副本排除 `.git` 和 `change-impact` 后，156 个源文件哈希一致。
- 本轮 README、地图和 facts 中未发现显式引用旧 GPT 地图或旧 Composer 地图。

观察项：

- 新非 Git 地图与旧 GPT 非 Git 地图行序列相似度为 `99.0%`，LCS 匹配 `249/252` 行。
- 真正不同的内容只有非 Git 说明行的换行位置，以及一处旧地图里的 `packages/ui/package.json:1-??, packages/config/package.json:1-??` 被新地图替换为 `packages/ui/package.json:1-49, packages/config/package.json:1-26`。
- 新 Git 地图与旧 Composer 地图文本相似度也为 `99.8%`。

复核修正：

- 相似度高不能单独证明复制或污染。D12 是同一个项目、同一个 skill、同一个模板、同一个关注范围，稳定输出本来就可能高度一致。
- 本轮模型可见 prompt 没有旧地图路径；新地图和 README 中没有显式引用旧 GPT 地图或旧 Composer 地图。
- 输出目录存在 `OPERATOR.md`，其中提到“不要参考旧地图”，这是给评测员看的环境说明，属于轻微环境噪音，但不包含旧地图内容。

因此，这轮应记为 `PASS-WARN`：Pathfinder gate、Git/非 Git 降级和只读边界均通过；相似度作为观察项保留，但不作为否定独立性的证据。
