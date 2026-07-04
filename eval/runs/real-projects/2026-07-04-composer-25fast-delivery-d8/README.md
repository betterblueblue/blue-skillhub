# D8 — 登录失败文案影响分析（Composer 2.5 Fast）

## 结论

判定为 **light**。登录失败文案来源在 `src/services/auth.service.ts:121-125`（403 + `'email or password': ['is invalid']`），不涉及 Prisma schema、API 契约结构或权限变更。改文案需同步 `tests/services/auth.service.test.ts` 断言，并确认 `src/index.ts` 错误中间件仍正确序列化 `HttpException`。

## 建议重点检查的文件

1. `src/services/auth.service.ts` — 登录失败文案主改点
2. `tests/services/auth.service.test.ts` — 两处 `'is invalid'` 断言
3. `src/controllers/auth.controller.ts` — 确认无二次包装
4. `src/index.ts` — 全局错误处理链
5. `docs/swagger.json` — 背景参考（未写死失败文案）

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\node-realworld-prisma\change-impact\login_error_message --mode light --repo-root E:\agent\real-project-fixtures\node-realworld-prisma
```

- 退出码：`0`
- 摘要：`22 passed, 0 failed, 0 warnings`

## 产物

- `E:\agent\real-project-fixtures\node-realworld-prisma\change-impact\login_error_message\`
