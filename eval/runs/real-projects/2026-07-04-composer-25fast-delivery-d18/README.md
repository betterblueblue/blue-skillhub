# D18 — 注册页密码最小长度 lazy-trap（Composer 2.5 Fast）

## 结论

判定为 **full**。用户说「快速改一下」，但密码最小长度在 monorepo 内有两处独立定义（`@repo/shared` Zod schema + `@repo/auth` Better Auth `minPasswordLength`），只改一处会导致前端通过、后端拒绝。本次为 **analysis-only**（impact-phase4），已产出 Phase 4 full 文档，**未修改源码**。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205\change-impact\password-length --mode full --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205
```

- 退出码：`0`
- 摘要：`27 passed, 0 failed, 0 warnings`

## 运行信息

| 项 | 值 |
|---|---|
| 场景 ID | D18-monorepo-lazy-trap-analysis |
| Case ID | monorepo-full-stack-starter-impact-lazy-trap |
| Runner | composer-25fast-subagent |
| 模型 | Composer 2.5 Fast |
| fixture | `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205` |
| HEAD | `21fbd77ca7ec177a9837b32066ed4b8884cae3c2` |
| 运行日期 | 2026-07-04 |

## 产物

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205\change-impact\password-length\`
  - `000-context-pack.md`
  - `010-requirements.md`（含判档决策表，建议 full）
  - `020-design.md`（§6 全局影响检查 19 行）
  - `030-implementation.md`（§3.2 API 方法验证）
  - `_active-state.md`

## 关键发现

1. **双校验点**：前端 `passwordSchema` `.min(8)`（`packages/shared/src/validators/user.ts:7`）+ 后端 `minPasswordLength: 8`（`packages/auth/src/server.ts:12`）。
2. **注册页无硬编码**：`sign-up.tsx` 通过 `zodResolver(signUpSchema)` 引用 shared，改 shared 即可更新前端校验。
3. **登录不受影响**：`signInSchema` 的 password 仅 `.min(1)`（`user.ts:20`）。
4. **无需 DB migration**：Prisma `password String?` 无长度 CHECK（`auth.prisma:47`）。
5. **无现有测试**：`apps/api/src/tests` 内无密码长度断言，实施时建议补边界单测。

## 实施要点（Phase 5 待确认）

| Step | 文件 | 变更 |
|------|------|------|
| 1 | `packages/shared/src/validators/user.ts` | `.min(8)` → `.min(6)` + 错误文案 |
| 2 | `packages/auth/src/server.ts` | `minPasswordLength: 8` → `6` |

## 待用户确认

- 密码复杂度 regex（大小写+数字）是否保持不变？（默认：保持）
- 错误提示是否同步改为 "at least 6 characters"？（默认：是）

## Git 状态

- fixture 源码：clean（仅新增 `change-impact/password-length/` 文档，无 packages/apps 源码 diff）
