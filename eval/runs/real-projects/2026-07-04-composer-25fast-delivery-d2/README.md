# D2 — profile displayName 影响分析（Composer 2.5 Fast）

## 结论

判定为 **full**。`displayName` 需跨 Prisma schema/迁移、`auth.service`（注册/更新）、`profileMapper`、`article.service` 中 10+ 处 author select（含 profileMapper 与手工组装双路径）、TypeScript 模型、Swagger 与 Jest 测试。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\node-realworld-prisma\change-impact\user_profile_display_name --mode full --repo-root E:\agent\real-project-fixtures\node-realworld-prisma
```

- 退出码：`0`
- 摘要：`27 passed, 0 failed, 0 warnings`

## 运行信息

| 项 | 值 |
|---|---|
| 场景 ID | D2-node-profile-phase4 |
| Case ID | node-realworld-prisma-impact-full |
| Runner | composer-25fast-subagent |
| 模型 | Composer 2.5 Fast |
| fixture | `E:\agent\real-project-fixtures\node-realworld-prisma` |
| HEAD | `6ac99ea5aeadc4e001dd4d6933c2e269f878a969` |
| 运行日期 | 2026-07-04 |

## 产物

- `E:\agent\real-project-fixtures\node-realworld-prisma\change-impact\user_profile_display_name\`
  - `000-context-pack.md`
  - `010-requirements.md`（含判档决策表）
  - `020-design.md`（§6 全局影响检查 19 行）
  - `030-implementation.md`（§3.2 API 方法验证）
  - `_active-state.md`

## 关键发现

1. **DB**：`User` 表无 `displayName`（`prisma/schema.prisma:46-58`），必须 migration，不能只改 TypeScript。
2. **Profile 出口**：`profileMapper`（`src/utils/profile.utils.ts`）统一 profile 与部分 article author；改一处覆盖 getProfile/follow/unfollow 及 getArticles/getFeed/favorite。
3. **Article author 双路径**：`getArticle`/`updateArticle`/`createArticle` 等手工组装 author（`article.service.ts:287-290` 等），实施时易遗漏，需全部补 `displayName` 或统一改用 profileMapper。
4. **Swagger**：`Article.author` 引用 `Profile`（`docs/swagger.json:928-930`），User/Profile/NewUser 均需同步。

## 已确认字段约束（2026-07-04）

| 项 | 决定 |
|---|---|
| 可空 | 是（`String?`，与 bio/image 一致） |
| 唯一 | 否 |
| 存量回填 | `displayName = username` |
| 注册必填 | 否（可选，无 blank 422） |

## Out of Scope

- login 响应、comment.author、前端 — 用户未要求

## Git 状态

- fixture 源码：clean（仅新增 `change-impact/` 文档，无 src/prisma/tests diff）
