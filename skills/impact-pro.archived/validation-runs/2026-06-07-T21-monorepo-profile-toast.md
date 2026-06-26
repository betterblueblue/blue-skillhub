# T21 full-stack-fastapi-template - Profile 保存成功提示文案

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：FastAPI backend + React/Vite frontend monorepo
- 项目路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template`
- 变更意图：调整用户资料保存成功后的前端 toast 文案，确认不改后端用户更新 API。
- 使用档位：light
- 命中 profile：`frontend-react-vite` 为主，`python-fastapi-sqlmodel` 只读辅助
- 最终评分：90
- 失败等级：无

## 实际发现

关键文件：

- `frontend/src/components/UserSettings/UserInformation.tsx`：用户资料编辑表单和成功 toast 的可能位置。
- `frontend/tests/user-settings.spec.ts`：断言 `User updated successfully`。
- `frontend/src/routes/_layout/settings.tsx`：设置页 tabs 和页面标题。
- `backend/app/api/routes/users.py`：后端用户更新 API 只读确认，本变更不应修改。
- `frontend/src/client/*.gen.ts`：generated client 只读确认，本变更不应修改。

## 验收判断

应判定 light。

理由：

- 只改前端 toast 文案和 E2E 断言。
- 不改后端 API、OpenAPI schema、generated client、数据库或权限。
- monorepo 场景仍需列出后端只读确认，避免完全忽略 API 契约。

## 风险追问

1. 是否只改资料保存成功 toast，还是密码更新/删除账号等成功文案也同步？
2. 是否有测试或文档依赖原始 `User updated successfully` 文案？
3. 是否需要统一 toast 文案规范？

## 验证方案

- Playwright：编辑用户资料成功后展示新 toast。
- 回归：无效 email 仍显示 `Invalid email address`。
- 只读确认：后端用户更新 endpoint 和 generated client 未改。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | monorepo light 变更容易漏掉后端契约确认 | 前端 toast 来自用户更新 API 调用结果 | 文档中明确后端只读确认，不进入实施 |

## 结论

通过（light）。该用例补充 monorepo 第二变更，验证多 profile 场景下可以以前端 profile 为主、后端 profile 只读辅助，而不是强行 full。
