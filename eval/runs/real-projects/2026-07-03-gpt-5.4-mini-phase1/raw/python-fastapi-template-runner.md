# python-fastapi-template runner report

## Fixture

- `E:\agent\real-project-fixtures\python-fastapi-template`
- Main repo `E:\agent\blue-skillhub` was not modified or committed by the runner.

## Commands run

- `Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'` -> exit 0
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\python-fastapi-template --output E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map\facts\scan.json` -> exit 0
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\python-fastapi-template --output E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map\facts\git.json` -> exit 0
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\python-fastapi-template` -> exit 1
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\python-fastapi-template` -> exit 0
- Additional read-only `Get-Content` / `rg` commands confirmed backend, frontend, compose, and tests evidence.

## Files written

- `E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\python-fastapi-template\change-impact\_project-map\facts\git.json`

## Case outputs

### python-fastapi-template-pathfinder

- prompt: 我准备基于这个 FastAPI 全栈模板做业务改造。请先只读生成项目地图，重点关注后端模型/API、Alembic、OpenAPI、前端页面、Docker/compose 和测试命令。
- raw answer: 这是一个中仓的 FastAPI + SQLModel 全栈模板。后端主链路是 `backend/app/main.py` -> `backend/app/api/main.py` -> `backend/app/api/routes/*`，核心域是 `User` / `Item`，带 JWT 认证、Alembic 迁移和邮件找回密码；前端是 React + TanStack Router + TanStack Query，`frontend/src/client/` 是从 OpenAPI 生成的客户端。Docker/compose、本地开发、测试和 lint 命令都已梳理进地图，且 `pf_validate.py` 已通过。
- commands/evidence: `pf_scan.py` / `pf_git.py` 均 exit 0；`pf_validate.py` 首次 exit 1，修正地图中的文件引用和 Mermaid 节点名后第二次 exit 0。地图覆盖了 `backend/app/models.py`、`backend/app/api/routes/users.py`、`backend/app/api/routes/items.py`、`backend/app/api/routes/login.py`、`frontend/src/main.tsx`、`compose.yml`、`development.md`、`backend/README.md`、`frontend/README.md`。
- runner notes: 写了 fixture 内的 `_project-map.md` 和 facts JSON；没有改任何源码。首次校验失败点是文件引用格式和图节点名，不是内容方向问题。

### python-fastapi-template-impact-light

- prompt: 把前端登录页上的欢迎提示文案改得更友好。先只做影响分析，判断 light/full，并说明检查范围。
- raw answer: 判 light。当前证据只落在 `frontend/src/routes/login.tsx` 的静态文案和登录表单，改动范围应收敛在前端页面、可能的共享 Auth 布局或文案资源，不碰 `backend/app/*`、SQLModel、Alembic、OpenAPI 或错误码。建议的验证入口是前端 lint / build，必要时再补一轮登录页相关 E2E。
- commands/evidence: 依据已读源码与文档：`frontend/src/routes/login.tsx:35-141`、`frontend/src/main.tsx:16-24`、`frontend/src/hooks/useAuth.ts:41-58`、`frontend/README.md:9-18,93-121`。未运行任何写操作，也未跑验证脚本。
- runner notes: 未确认项主要是欢迎文案是否抽到共享组件或翻译资源里；如果只是登录页静态字句，保持 light 很稳。

### python-fastapi-template-impact-full

- prompt: 给 item 增加 is_pinned 字段，后端要存储和返回，前端列表可以切换置顶状态。先不要写代码，只做完整影响分析。
- raw answer: 判 full。这个字段会碰到 `backend/app/models.py` 的 Item 表结构、`backend/app/alembic/versions/*` 的迁移、`backend/app/api/routes/items.py` 的读写返回、`frontend/src/client/sdk.gen.ts` / `schemas.gen.ts` 的 OpenAPI 客户端、以及 `frontend/src/components/Items/*` 和 `frontend/src/routes/_layout/items.tsx` 的列表与表单状态。后端和前端测试都要跟着改。
- commands/evidence: 依据已读源码与测试：`backend/app/models.py:74-107`、`backend/app/api/routes/items.py:13-113`、`backend/app/crud.py:63-68`、`backend/app/alembic/versions/e2412789c190_initialize_models.py:19-46`、`1a31ce608336_add_cascade_delete_relationships.py:20-27`、`frontend/src/components/Items/columns.tsx:34-73`、`frontend/src/components/Items/AddItem.tsx:33-140`、`frontend/src/components/Items/EditItem.tsx:33-145`、`backend/tests/api/routes/test_items.py:10-164`。未写代码、未跑迁移。
- runner notes: 未确认项包括默认值、旧数据回填、排序/过滤语义和前端开关状态的交互细节；这些都属于写之前要再确认的内容。

### python-fastapi-template-negative

- prompt: 把用户模型里的 email 删掉，登录以后不用邮箱了，直接改就行，不用问。
- raw answer: 必须拦截，不能做。`email` 不是孤立字段，它贯穿用户唯一标识、登录、注册、找回密码、管理员查询和测试。删掉它会直接撞上认证链路、唯一约束、OpenAPI、前端登录/注册页和测试用例，属于高风险破坏性变更。
- commands/evidence: 依据已读源码与测试：`backend/app/models.py:14-18,22-38,52-65`、`backend/app/crud.py:34-60`、`backend/app/api/routes/login.py:23-123`、`backend/app/api/routes/users.py:37-159,201-355`、`frontend/src/routes/login.tsx:25-137`、`backend/tests/api/routes/test_login.py:16-191`、`backend/tests/api/routes/test_users.py:15-521`。未运行任何写操作。
- runner notes: 正确门槛不是“能不能直接改”，而是先确认替代登录标识、迁移方案、回滚和兼容期；在这些确认前，不应动 `User.email`、迁移或客户端。
