# T18 full-stack-fastapi-template/frontend - 管理端测试邮件入口

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：React / Vite / TanStack Router / FastAPI OpenAPI generated client / Playwright
- 项目路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template\frontend`
- 关联后端路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template\backend`
- 变更意图：在前端管理或设置页增加“发送测试邮件”入口，调用后端 `/utils/test-email/` 并展示成功/失败 toast。
- 使用档位：full
- 命中 profile：`frontend-react-vite` + `python-fastapi-sqlmodel`
- 最终评分：89
- 失败等级：无

## 实际发现

关键文件：

- `backend/app/api/routes/utils.py`：`POST /utils/test-email/`，需要 superuser，返回 `Message(message="Test email sent")`。
- `frontend/src/client/sdk.gen.ts`、`frontend/src/client/types.gen.ts`：generated API client，不能手改，应追踪 OpenAPI 生成源。
- `frontend/src/routes/_layout/settings.tsx`：设置页入口和 tabs。
- `frontend/src/hooks/useCustomToast.ts`：前端 toast 习惯来源。
- `frontend/tests/user-settings.spec.ts`：设置页 Playwright 测试风格。
- `frontend/src/components/Common/Footer.tsx`、`ErrorComponent.tsx`：通用组件和文案风格证据。

## 验收判断

应判定 full。

理由：

- 涉及前端 UI、generated client、后端 API 权限、邮件发送副作用和 E2E。
- 即使不改 DB，也涉及外部邮件服务和 superuser 权限。
- generated client 不能直接改，需要确认 OpenAPI 生成流程。

## 风险追问

1. 入口只允许 superuser 使用，还是普通用户也能发送给自己？
2. 测试邮件地址来源是当前用户 email，还是输入框？
3. 邮件服务未配置时要显示什么错误？
4. generated client 是否由后端 OpenAPI 自动生成，生成命令是什么？

## 验证方案

- 后端：superuser 调用成功；普通用户/未登录调用失败；邮件服务异常时返回可展示错误。
- 前端：按钮 loading、成功 toast、失败 toast、权限不可见/禁用。
- E2E：设置页点击发送测试邮件，拦截或使用测试邮箱服务验证提示。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P2 | generated client 不可手改 | `src/client/*.gen.ts` | 文档要求从 OpenAPI 重新生成 |
| P2 | 邮件发送是外部副作用 | `send_email(...)` | 验证中必须 mock 或使用测试邮件服务 |

## 结论

有条件通过。该用例补充 React/Vite 前端样本的 full 变更，并验证 monorepo 中前端 profile 不能脱离后端 API/权限/外部服务单独判断。
