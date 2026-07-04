# D9 — monorepo organization 字段影响分析（Composer 2.5 Fast）

## 结论

判定为 **full**。organization 字段需跨 `packages/db` Prisma schema、`packages/shared` types/validators、`apps/api` 路由/服务/仓储、`apps/web` 注册与资料页，以及 workspace 级测试与 `db:generate` 验证命令。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d9-composer\change-impact\user_profile_organization --mode full --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d9-composer
```

- 退出码：`0`
- 摘要：`27 passed, 0 failed, 0 warnings`

## 产物

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d9-composer\change-impact\user_profile_organization\`
  - `000-context-pack.md`, `010-requirements.md`, `020-design.md`, `030-implementation.md`, `_active-state.md`

## 未确认项

- organization 是否必填
- 资料页是独立路由还是复用 dashboard
