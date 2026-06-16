# T07 full-stack-fastapi-template - 前后端同仓邀请功能

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Monorepo / FastAPI backend / React Vite frontend
- 项目路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template`
- Commit：`38302d7492dbd158ed6cf499a6dd0bab6ad17141`
- 变更意图：新增团队成员邀请功能，后端生成邀请链接，前端展示邀请弹窗。
- 使用档位：full
- 命中 profile：`python-fastapi-sqlmodel` + `frontend-react-vite`
- 最终评分：87
- 失败等级：无

## 实际发现

### 技术栈检测

命中证据：

- 根目录存在 `backend/` 和 `frontend/`。
- `backend/pyproject.toml` 包含 FastAPI、SQLModel、Alembic、pytest。
- `frontend/package.json` 包含 React、Vite、Playwright。
- 根目录有 `compose.yml`，说明前后端和依赖服务协作。

应进入多 profile 模式，而不是只选择一个最高分 profile。

### 上下文发现

后端 profile 可命中：

- `backend/app/models.py`
- `backend/app/api/routes/users.py`
- `backend/app/api/routes/utils.py`
- `backend/app/core/config.py`
- `backend/app/email-templates/src/*.mjml`
- `backend/app/alembic/versions/*.py`
- `backend/tests/api/routes/*.py`

前端 profile 可命中：

- `frontend/src/routes/**/*.tsx`
- `frontend/src/components/**/*.tsx`
- `frontend/src/client/**/*.ts`
- `frontend/tests/*.spec.ts`
- `frontend/package.json`

### 风险追问

应追问：

1. 邀请链接有效期多久，是否一次性使用？
2. 邀请权限由谁发起，普通用户还是管理员？
3. 重复邀请同一邮箱如何处理？
4. 邀请邮件模板、前端弹窗、API client 是否都需要同步？
5. 链接泄漏后如何撤销或失效？

### 定级

应判定 full。

理由：

- 涉及 backend API、权限、安全、邮件模板。
- 涉及 frontend UI、client 类型、E2E。
- 可能涉及 DB 表/字段或邀请 token 存储。
- 跨模块协作和安全风险明显。

## 评分

| 维度 | 分值 | 得分 | 说明 |
|------|------|------|------|
| 技术栈检测与 profile 选择 | 15 | 14 | 能识别前后端同仓，需多 profile |
| 上下文发现 | 20 | 17 | 后端/前端核心路径均可命中 |
| 风险识别与追问 | 20 | 18 | 覆盖权限、邮件、链接泄漏、过期 |
| light/full 定级 | 10 | 10 | full 明确 |
| 文档质量 | 15 | 13 | 需要按模块拆分文档 |
| 执行安全 | 10 | 10 | 写操作确认规则存在 |
| 验证设计 | 10 | 5 | 未启动服务，E2E 未执行 |

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | 未执行服务级联测试 | 未启动 compose / Playwright | 在具备 Docker/依赖服务环境复跑 |
| P3 | 多 profile 流程原先不够明确 | 已在 `SKILL.md` 增加多 profile 规则 | 后续真实对话复测 |

## 结论

有条件通过。多 profile 机制已写入 `SKILL.md`，该项目可作为 monorepo 验收样本继续复测。
