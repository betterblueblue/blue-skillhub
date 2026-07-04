# [D19 node tags removal phase5] Phase 5 预检

> 仓库：E:\agent\real-project-fixtures-delivery\node-realworld-prisma-minimax-m3-d19r2-20260704
> HEAD：6ac99ea5aeadc4e001dd4d6933c2e269f878a969（origin/main, main）
> 生成时间：2026-07-04 12:25:00
>
> 导航：[030-implementation.md](030-implementation.md) → **060-preflight.md** → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

> 本文档是 Phase 5 正式写源码前的预检清单，确认仓库处于可改状态、验证命令可跑、Step 列表与回滚方案已就绪、不会执行真实数据库迁移。

## 1. 仓库状态（基线）

### 1.1 Git HEAD

- HEAD commit：`6ac99ea5aeadc4e001dd4d6933c2e269f878a969`
- 分支：`main`（同时也是 `origin/main`）
- 与 `main` 的关系：clean（未偏离）
- 提交者基线：D19R1 末态 = D19R2 起始态（fixture_mode = isolated-copy，副本与 D19R1 末尾字节级一致）
- 提交者上下文：fixture 准备者（real-projects/d19r2-prep）从 `blue-skillhub/eval/real-projects/.../node-realworld-prisma-minimax-m3-d19r2-20260704` 拷贝并 reset

### 1.2 仓库内容（拷贝自 fixture 准备目录）

```bash
$ git status --porcelain
（空 — clean）
```

### 1.3 package.json 关键命令

| 命令 | 用途 |
|------|------|
| `npm test` = `jest -i` | 跑测试套件；基线 5 suites / 26 passed / 1 todo（exit 0） |
| `npm run prisma:generate` | 生成 Prisma Client |
| `npm run prisma:migrate` | dev migrate（**本场景不跑**） |
| `npm run dev` / `npm start` | 启动 dev server（**本场景不跑**） |

### 1.4 目录结构（与改动相关的部分）

```
src/
  controllers/  auth.controller.ts  article.controller.ts  profile.controller.ts
  services/     auth.service.ts     article.service.ts     profile.service.ts
  models/       article.model.ts    comment.model.ts
                http-exception.model.ts  profile.model.ts   register-input.model.ts
                registered-user.model.ts  user.model.ts
  routes/       routes.ts
  utils/        auth.ts  profile.utils.ts  token.utils.ts  user-request.d.ts
prisma/
  schema.prisma
  prisma-client.ts
  migrations/   20210924222830_initial/  20211001195651_implicit_articles/
                20211105082430_api_url/  migration_lock.toml
tests/
  services/     auth.service.test.ts  article.service.test.ts
                profile.service.test.ts  utils/profile.utils.test.ts
  prisma-mock.ts
docs/
  swagger.json
change-impact/
  node-tags-removal-phase5/  ← 本次需求目录
  ...
```

### 1.5 技术栈快照

- Node.js（具体版本由 fixture 决定）
- Express 4 + TypeScript 4
- Prisma 2.29（client + cli）
- Jest 27 + `mockDeep<PrismaClient>()` via `jest-mock-extended`
- `prisma/prisma-client.ts` 单例导出 `PrismaClient`（DB 走 `env("DATABASE_URL")`；本场景不连真实 DB）

## 2. 验证命令预跑（基线已验证）

### 2.1 `impact_validate.py` — Phase 4 文档静态门禁

```bash
$ python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py \
    change-impact/node-tags-removal-phase5 --mode full --repo-root .
```

- **结果**：20 passed, 0 failed, 2 warnings
- 退出码：0
- 警告：
  - V2: 010-requirements.md contains file paths: `article.service.test.ts`, `tag.service.test.ts`, `docs/swagger.json`（与 D19R1 同类，已通过 020/030 转移细节；可接受）
  - V4: 无判档决策表（建议补到 090，可选）
- 失败的项：无
- 重复运行：稳定

### 2.2 `git diff --check` — 静态行尾检查

```bash
$ git diff --check
（空）
```

- 退出码：0
- 含义：当前工作树相对 HEAD 无未提交修改，行尾无 trailing whitespace

### 2.3 `npm test` — 测试基线

```bash
$ npm test
```

- 退出码：0
- 结果：5 suites passed / 26 tests passed / 1 todo（与 fixture 基线一致）
- 含义：源码未改动，测试全部通过

### 2.4 基线对照表

| 验证命令 | 退出码 | 关键输出 | 验证等级 |
|---------|--------|----------|----------|
| `impact_validate.py` | 0 | 20 passed, 0 failed, 2 warnings | V1 |
| `git diff --check` | 0 | （空） | V1 |
| `npm test` | 0 | 5 suites / 26 passed / 1 todo | V2 |
| `git status --porcelain` | 0 | （空） | V0 |
| `git rev-parse HEAD` | 0 | `6ac99ea5aeadc4e001dd4d6933c2e269f878a969` | V0 |

## 3. 14 步 Step 列表（含本步编号、写入对象、影响、验证、回滚）

> 编号：Step 0 = 写 060 + 090 骨架；Step 1-4 = 删 4 个文件；Step 5-10 = 改 6 个文件；Step 11-14 = 验证。
> 每个 Step 在执行前必须请求当前对话中的 `确认 Step N`；用户可回复 `拆分 Step N`。

| # | 文件 | 操作 | 写入/影响对象 | 验证命令 | 验证等级 | 回滚命令 |
|---|------|------|----------------|----------|----------|----------|
| 0 | `change-impact/.../060-preflight.md` + `090-execution-record.md` | Write | 本需求目录 | `ls` + `wc -l` | V0 | `rm` |
| 1 | `src/controllers/tag.controller.ts` | `git rm` | 整个文件消失 | `ls src/controllers/` + `npm test` | V1 | `git checkout HEAD -- src/controllers/tag.controller.ts` |
| 2 | `src/services/tag.service.ts` | `git rm` | 整个文件消失 | `ls src/services/` | V1 | `git checkout HEAD -- src/services/tag.service.ts` |
| 3 | `src/models/tag.model.ts` | `git rm` | 整个文件消失 | `ls src/models/` | V1 | `git checkout HEAD -- src/models/tag.model.ts` |
| 4 | `tests/services/tag.service.test.ts` | `git rm` | 整个文件消失；suites 5→4 | `ls tests/services/` | V1 | `git checkout HEAD -- tests/services/tag.service.test.ts` |
| 5 | `src/routes/routes.ts` | Edit | 移除 `tagsController` import + `.use()` | `npm test`（隐含 tsc） + `grep -n "tagsController" src/routes/routes.ts` | V1 | `git checkout HEAD -- src/routes/routes.ts` |
| 6 | `src/controllers/article.controller.ts` | Edit | 移除 `@queryparam tag` JSDoc | `grep -n "tag" src/controllers/article.controller.ts` 0 命中 | V0 | `git checkout HEAD -- src/controllers/article.controller.ts` |
| 7 | `src/services/article.service.ts` | Edit | 移除 `'tag' in query` / `tagList` include×4 / `tagList` 映射×5 / `disconnectArticlesTags` / `tagList` 写入 | `npm test` + `grep -n "tagList\|disconnectArticlesTags" src/services/article.service.ts` 0 命中 | V2 | `git checkout HEAD -- src/services/article.service.ts` |
| 8 | `prisma/schema.prisma` | Edit（DDL 等效） | 移除 `Tag` model + `Article.tagList Tag[]` | `grep -n "model Tag\|tagList" prisma/schema.prisma` 0 命中 | V1 | `git checkout HEAD -- prisma/schema.prisma` |
| 9 | `docs/swagger.json` | Edit | 移除 `/tags` / `TagsResponse` / `Article.tagList` / `NewArticle.tagList` / `?tag=` | `python -c "import json; json.load(open('docs/swagger.json'))"` + `grep -n "TagsResponse\|/tags" docs/swagger.json` 0 命中 | V1 | `git checkout HEAD -- docs/swagger.json` |
| 10 | `tests/services/article.service.test.ts` | Edit | 移除 mock payload 中 `tagList: []` | `grep -n "tagList" tests/services/article.service.test.ts` 0 命中 + `npm test` | V0 | `git checkout HEAD -- tests/services/article.service.test.ts` |
| 11 | `git diff --check` | 命令 | N/A | exit 0 + 空输出 | V1 | N/A |
| 12 | `npm test` | 命令 | N/A | exit 0 + 4 suites / 26 passed | V2 | N/A |
| 13 | 全仓 7 token 残留扫描 | 命令 | N/A | 7 token 全部 0 命中（git grep exit 1） | V1 | N/A |
| 14 | favorites 4 token 保留扫描 | 命令 | N/A | 4 token 全部命中（`favorited` / `favoritesCount` / `favoritedBy` / `favoriteArticle\|unfavoriteArticle`） | V1 | N/A |

### 3.1 Step 间的依赖关系

- Step 1-4（删 4 文件）互不依赖，可任意顺序；但建议按 controller → service → model → test 顺序便于 090 记录
- Step 5（routes 解引用）依赖 Step 1 已删 `tag.controller.ts`（否则 import 指向不存在的模块）
- Step 6-7（article.controller / article.service）独立，可任意顺序
- Step 8（schema）依赖 Step 7 已移除 `tagList` include（否则 prisma client 类型不匹配）；但因 `prisma generate` 不在 14 步内（不跑），仅需 `npm test` 通过即可
- Step 9（swagger）独立
- Step 10（test mock）依赖 Step 7 已移除 service 端 tagList include
- Step 11-14 验证在所有源码写完后

### 3.2 倒序回滚顺序

```
全部成功想回滚：
  倒序执行：Step 14 → Step 13 → Step 12 → Step 11 → Step 10 → ... → Step 1 → Step 0

Step 7 失败（service 重构未完成）：
  1. git checkout HEAD -- src/services/article.service.ts
  2. Step 8-14 不执行（依赖 Step 7）

Step 5 失败（routes 解引用有 import 残留）：
  1. git checkout HEAD -- src/routes/routes.ts
  2. 重新执行 Step 1-4 + Step 5（import 路径不变）

Step 1-4 任意一步失败：
  - git checkout HEAD -- <failed_path>
  - 不影响其他删除步（顺序无关）
```

## 4. 兼容

### 4.1 破坏性变更

- `GET /api/tags` → 404（路由完全消失）
- `POST /api/articles` body `tagList` 字段被忽略（service 不再读取）；服务端不报错，字段被静默忽略
- `PUT /api/articles/:slug` body `tagList` 字段被忽略（同上）
- `GET /api/articles*` 响应对象少 `tagList` 字段（`undefined`）
- `?tag=...` queryparam 静默忽略（service 不再读取 queryparam）

### 4.2 兼容性策略

- **不提供兼容期**：用户原话"tags 功能没人用了"明确指向无灰度
- 调用方适配：必须在客户端移除对 `/api/tags` 的调用、移除 article I/O 中的 `tagList` 字段、改用其他筛选方式
- 090 §兼容 段写明："破坏性变更，调用方需同步更新；隔离副本内不连真实 DB，无生产风险"

### 4.3 favorites 链路兼容性

- `POST/DELETE /api/articles/:slug/favorite` 行为完全不变
- `favorited` / `favoritesCount` / `favoritedBy` 字段在所有 article 响应中保留
- `User.favorites` / `Article.favoritedBy` Prisma 关系保留
- `favoriteArticle` / `unfavoriteArticle` service 函数保留

## 5. 回滚

### 5.1 逐步骤回滚

按 3.2 节"倒序回滚顺序"执行；每条命令已在 3 节 Step 表中列出。

### 5.2 已删除文件的回滚

- `git rm` 删除的文件在 git 中仍可恢复：`git checkout HEAD -- <path>` 会从 HEAD 重新拉出
- 若连 HEAD 也丢失（极端情况）：D19R1 验证过"fixture_mode=isolated-copy，副本与上一轮末态字节级一致"，可从 D19R1 归档目录 `E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-minimax-m3-delivery-d19r1\` 找回

### 5.3 schema 回滚的连带影响

- Step 8 改 schema 后，旧 `prisma/migrations/*` 与新 schema 偏离；`prisma migrate` 仍可读旧 migration（无 schema validation），但 dev 时会报"drift" 警告
- 回滚 schema 后 drift 警告消失
- 真实部署时 DBA 需手动 reconcile（与本场景无关）

## 6. 为什么没跑迁移

### 6.1 三重原因

1. **用户原话明确禁止**：
   - 任务 prompt 第 1 段：「**不执行真实数据库迁移**」
   - 任务 prompt 第 1 段：「**只在隔离副本中操作**」
   - 任务 prompt 第 1 段：「**执行记录里写清楚兼容、回滚和为什么没跑迁移**」（本节即对应）
2. **隔离副本不连真实 DB**：
   - 隔离副本创建时未配置 `DATABASE_URL`（`prisma/schema.prisma:4-7` datasource 走 `env("DATABASE_URL")`）
   - 即使执行 `prisma migrate dev` / `prisma db push` 也会因 `DATABASE_URL` 未设置而失败
3. **变更范围与运行时分层解耦**：
   - 本场景只删 schema 文件中的 2 个声明（`Tag` model + `Article.tagList` 关系）
   - 不动任何 migration SQL
   - 旧 `prisma/migrations/20210924222830_initial/migration.sql` 中 Tag 表 / `prisma/migrations/20211001195651_implicit_articles/migration.sql` 中 `_ArticleToTag` 中间表反映历史真实状态，由后续维护者按需整理

### 6.2 真实部署时的责任归属

- 本场景**不在隔离副本内执行任何数据库迁移**
- 真实生产部署时，DBA 需在维护窗口内：
  1. 在新 schema 上执行 `npx prisma migrate dev --name drop_tags` 生成新 migration
  2. 应用该 migration 删除 `Tag` 表 + `_ArticleToTag` 中间表
  3. 同步调整任何基于 `Tag` / `tagList` 的下游分析或缓存
- 责任归属：**由后续 DBA / 维护者**（不在本场景责任范围）

### 6.3 隔离副本内的 schema 状态

- `prisma/schema.prisma` 中：
  - `Article` model 删除 `tagList Tag[]` 字段
  - 整个 `Tag` model 被删除
- 文件结构合法可被 Prisma 解析（Prisma 语法正确）
- `prisma generate` 不会跑（Step 8 仅改文件不跑命令）；npm test 走 TypeScript 编译，编译时不读 Prisma schema

### 6.4 测试基线声明

- 基线 5 suites / 26 passed / 1 todo（已通过 `npm test` 验证，见 prep `commands/node-baseline-minimax-m3.txt`）
- 删除后预期 4 suites / 26 passed / 0 todo（删 `tag.service.test.ts` 后 suites 5→4，删 `test.todo` 后 todos 1→0）
- 任何与之不符的输出 = FAIL，必须按错误信息修复

---

> **预检结论**：仓库状态 clean、HEAD 固定、3 个验证命令已预跑通过、14 步 Step 列表完整、回滚方案就绪、不执行真实迁移。**Phase 5 准备就绪**，等待用户对每个 Step 的 `确认 Step N`。
