# [D19 node tags removal phase5] Context Pack

> 生成时间：2026-07-04 12:17:33  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：**000-context-pack.md** → [010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

> 目标：给后续 agent 一份精简、准确、可追溯的上下文。只放本次变更真正需要的证据；看过但暂不相关的内容也要说明原因。

## 1. 变更意图

- 用户原话：tags 功能没人用了，把 /api/tags、Tag model、文章 tagList 输入/输出和相关测试引用都删掉。先做影响分析并通过 Phase 4 验证，再执行 Phase 5。所有写操作按 skill 流程逐个请求 `确认 Step N`，我会在你每次请求后逐条回复确认或拆分；不要把多个写操作合并在一个 Step，也不要把本消息当成任何 Step 的预先授权。只在隔离副本中操作，不执行真实数据库迁移；执行记录里写清楚兼容、回滚和为什么没跑迁移。
- 当前假设：用户要全量下线 tags 功能——移除路由、Tag model、Article↔Tag 关联、文章 tagList 输入/输出、相关测试、Swagger 契约，并保留 favorites 功能（favoriteArticle / favoritesCount / favoritedBy 不动）。
- 已识别技术栈：Node.js + Express 4 + TypeScript 4 + Prisma 2.29 + Jest 27
- 已加载技术栈规则：`skills/impact/profiles/node-express-prisma.md`（命中高置信：package.json 有 `express` / `prisma` / `@prisma/client`，存在 `prisma/schema.prisma`、`src/`、`tests/`）
- 任务规模：**大**（依据：跨 routes / controllers / services / prisma schema / swagger / tests 六个层级，含高风险删除与不可逆 schema 变更）
- 成功标准：
  1. `src/controllers/tag.controller.ts`、`src/services/tag.service.ts`、`src/models/tag.model.ts`、`tests/services/tag.service.test.ts` 四个文件从工作树中删除；
  2. `src/routes/routes.ts` 不再 import 或 `.use(tagsController)`；
  3. `src/services/article.service.ts` 中 `tagList` / `'tag' in query` / `disconnectArticlesTags` 全部清除，favorites 链路（favoriteArticle / unfavoriteArticle / favoritesCount / favoritedBy / `articles.favorites` 关系）原样保留；
  4. `prisma/schema.prisma` 中 `Tag` model 与 `Article.tagList Tag[]` 关系被移除；
  5. `docs/swagger.json` 中 `/tags` path、`TagsResponse` definition、`Article.tagList` 与 `NewArticle.tagList` 被移除；
  6. `tests/services/article.service.test.ts` 中 mock payload 仍然不引用 `tagList`（或保留为 noop，因为代码不再读取）；
  7. 隔离副本内 `npm test` 退出码 0，5 suites / 26 passed / 1 todo（与基线一致）；
  8. `git diff --check` 退出码 0；
  9. `impact_validate.py --mode full --repo-root .` 退出码 0；
  10. 不在隔离副本内执行真实 DB 迁移（即不跑 `prisma migrate dev` / `prisma db push`，也不写新的 migration SQL）。
- 长期目标模式：否
- 总目标 / 当前 Step / Backlog：本次只做"全量下线 tags"，backlog 无
- 项目地图状态：无 `_project-map.md`（无 pathfinder 预读）；仓库 HEAD `6ac99ea5aeadc4e001dd4d6933c2e269f878a969`（origin/main, main）

### 1.1 覆盖范围分析（V7 强制：用户原话含"所有/每次/任何"等全称量词）

> 用户原话中的全称量词：「**所有**写操作按 skill 流程逐个请求 `确认 Step N`」、「不要把**多个**写操作合并在一个 Step」、「... 都删掉」、「**不**执行真实数据库迁移」等。

| 用户的全称量词 | 现有实现覆盖情况 | 覆盖缺口 / 风险 | 处理方式 |
|---------------|------------------|------------------|----------|
| "所有写操作按 skill 流程逐个请求 `确认 Step N`" | 已有：030-implementation.md §3 将 14 步拆为 14 个独立 Step | 无缺口 | 严格执行：每步请求 `确认 Step N`，等用户回复后才执行 |
| "不要把多个写操作合并在一个 Step" | 已有：每个 Step 仅动 1-2 个文件（删除 4 个 / 改 6 个） | 无缺口 | 严格保持 Step N=单个写入对象 |
| "都删掉"（/api/tags、Tag model、文章 tagList I/O、相关测试） | 已覆盖：Step 1-4 删 4 个文件 + Step 5 解引用 routes + Step 7 article.service 清理 + Step 8 schema + Step 9 swagger + Step 10 test mock | 无缺口 | 030 §2.1 验收自检 11/11 全过 |
| "不执行真实数据库迁移" | 已有：030 §3 Step 8 仅改 schema.prisma 文件，不跑 `prisma migrate`；旧 migration 保留 | 缺口：生产环境需 DBA 窗口内 migrate | 090 写明"未执行迁移的原因 + 责任归属"；隔离副本不连 DB 故无生产风险 |
| "favorites 必须保留"（矩阵 must_contain） | 已有：030 §3 Step 7 显式标记 favorites 链路不动 + Step 14 全仓扫描 favorites 4 token | 无缺口 | 090 记录 favorites 4 token 命中数；Step 11-12 跑 npm test 验证 |
| "favorites 误删是失败信号"（must_not_contain 反面） | 已有：020 §8 不做的事 + 030 §3 Step 7/8 显式 exclude favorites | 无缺口 | Step 14 favorites 扫描 + npm test 双重验证 |
| "所有 npm 依赖不动"（矩阵 forbidden） | 已有：030 §3 不动 package.json / package-lock.json | 无缺口 | git diff --check / npm test 间接验证未引入新依赖 |
| "每次请求后逐条回复确认或拆分" | 已有：每次写入对象前请求 `确认 Step N`；如 Step 过宽用户可回复 `拆分 Step N` | 无缺口 | 严格执行 skill 流程 |
| "相关测试引用都删掉" | 已有：Step 4 删 tag.service.test.ts（整个文件）；Step 10 从 article.service.test.ts mock 删 `tagList: []` 字段 | 无缺口：tag.service.test.ts 仅 1 个 test.todo stub；article.service.test.ts 中 `tagList: []` 是 mock payload 而非断言，删除即可 | 双删 |
| "不真实数据库迁移" | 已有：090 写明不连 DB；schema 文件改由本次负责 | 缺口：旧 migration 与新 schema 偏离 | 隔离副本不连 DB；不清理旧 migration；由后续维护者按需整理 |

## 2. 源系统到目标系统对齐（如适用）

不适用——本次是"删除特性"，无外部源系统需要对齐。`/api/tags` 是 Conduit/RealWorld 官方 API 的一部分，但本仓库不是规范出处，且 prompt 明确说"tags 功能没人用了"。

## 3. 分层上下文

| 层级 | 内容 | 结论 |
|------|------|------|
| L1 项目地图 | 仓库根 = `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-minimax-m3-d19r2-20260704`；技术栈 Node/Express/Prisma；目录 `src/`、`prisma/`、`tests/`、`docs/`；命令 `npm test` / `npm run prisma:migrate` / `npm run dev` | 已确认（package.json:7-22） |
| L2 变更邻域 | tag 路由（`src/routes/routes.ts:2,8`）/ tag 控制器（`src/controllers/tag.controller.ts:1-22`）/ tag 服务（`src/services/tag.service.ts:1-35`）/ tag 模型（`src/models/tag.model.ts:1-3`）/ tag 测试（`tests/services/tag.service.test.ts:1-6`）/ Prisma Tag + Article.tagList（`prisma/schema.prisma:22,40-44`）/ Article 服务 tagList 散点（`src/services/article.service.ts:37-45, 78-82, 100-110, 134-140, 158-167, 201-247, 249-292, 294-305, 330-351, 525-571, 573-618`）/ Swagger tag 痕迹（`docs/swagger.json:25, 333-338, 738-757, 908-913, 937, 981-986, 1084-1095`） | 已确认（grep 命中下方 L3 证据段） |
| L3 精准证据 | tag.controller.ts 全文 / tag.service.ts 全文 / tag.model.ts 全文 / routes.ts 全文 / schema.prisma Tag 段 / swagger.json 关键段 | 已读取（见 §4、§5） |

## 4. 相关文件和对象

| 文件/对象 | 类型 | 相关性 | 为什么相关 | 证据 |
|-----------|------|--------|------------|------|
| `src/controllers/tag.controller.ts` | controller | 3 直接修改候选 | 整个文件仅做 `/tags` 路由，必须删除 | `src/controllers/tag.controller.ts:1-22` |
| `src/services/tag.service.ts` | service | 3 直接修改候选 | 整个文件仅导出 `getTags`，必须删除 | `src/services/tag.service.ts:1-35` |
| `src/models/tag.model.ts` | model | 3 直接修改候选 | 整个文件仅声明 `Tag` interface，必须删除 | `src/models/tag.model.ts:1-3` |
| `tests/services/tag.service.test.ts` | test | 3 直接修改候选 | 整个文件仅 stub `TagService.getTags`，必须删除 | `tests/services/tag.service.test.ts:1-6` |
| `src/routes/routes.ts` | routes | 3 直接修改候选 | 导入并 `.use(tagsController)` | `src/routes/routes.ts:2,8` |
| `src/controllers/article.controller.ts` | controller | 3 直接修改候选 | JSDoc 含 `@queryparam tag` 描述 | `src/controllers/article.controller.ts:25` |
| `src/services/article.service.ts` | service | 3 直接修改候选 | 包含 `tag` 过滤、`tagList` include、create/update/disconnect 的 tag 写入逻辑 | `src/services/article.service.ts:37-45, 78-82, 100-110, 134-140, 158-167, 201-247, 294-305, 330-351, 525-571, 573-618` |
| `prisma/schema.prisma` | schema | 3 直接修改候选 | 含 `Tag` model 与 `Article.tagList Tag[]` 关联 | `prisma/schema.prisma:22, 40-44` |
| `docs/swagger.json` | api-contract | 3 直接修改候选 | 含 `/tags` path、`TagsResponse`、`Article.tagList`、`NewArticle.tagList`、`tag` queryparam | `docs/swagger.json:333-338, 738-757, 908-913, 937, 981-986, 1084-1095` |
| `tests/services/article.service.test.ts` | test | 3 直接修改候选 | favoriteArticle/unfavoriteArticle mock payload 含 `tagList: []` 字段 | `tests/services/article.service.test.ts:48, 103` |
| `src/controllers/auth.controller.ts` | controller | 0 暂不纳入范围 | 与 tag 无关 | 用户 prompt 显式列为禁改 |
| `src/controllers/profile.controller.ts` | controller | 0 暂不纳入范围 | 与 tag 无关 | 用户 prompt 显式列为禁改 |
| `src/services/auth.service.ts` | service | 0 暂不纳入范围 | 与 tag 无关 | 用户 prompt 显式列为禁改 |
| `src/services/profile.service.ts` | service | 0 暂不纳入范围 | 与 tag 无关 | 用户 prompt 显式列为禁改 |
| `package.json` / `package-lock.json` | config | 0 暂不纳入范围 | 不引入/移除依赖 | 用户 prompt 显式列为禁改 |
| `prisma/migrations/*` | migration | 1 背景参考 | 已有 3 个迁移文件，schema 改动会让它们偏离；本场景不执行真实迁移 | `prisma/migrations/20210924222830_initial/migration.sql:16-21, 36-41, 92-95`、`prisma/migrations/20211001195651_implicit_articles/migration.sql:8-15, 18-27, 30` |
| `prisma/prisma-client.ts` | data-access | 1 背景参考 | 仅导出 `PrismaClient` 单例，不引用 Tag | `prisma/prisma-client.ts:1-18` |
| `tests/prisma-mock.ts` | test-helper | 1 背景参考 | `mockDeep<PrismaClient>()` 不需要按 schema 调整 | `tests/prisma-mock.ts:1-16` |
| `src/models/article.model.ts` | model | 1 背景参考 | `Article` interface 不含 tagList（tagList 仅来自 Prisma include），无需改 | `src/models/article.model.ts:1-10` |
| `src/models/comment.model.ts` / `registered-user.model.ts` 等 | model | 0 暂不纳入范围 | 与 tag 无关 | 用户 prompt 显式列为禁改 / 视觉确认 |
| `src/utils/auth.ts` / `profile.utils.ts` / `token.utils.ts` | util | 0 暂不纳入范围 | 与 tag 无关 | 视觉确认 |

相关性说明：

- 3：本次大概率要改。
- 2：不一定改，但影响设计、定级或验证。
- 1：只用于理解风格、约定或背景。
- 0：看过但排除，写入"暂不纳入范围"。

## 5. 关键上下文

### 入口

- `GET /api/tags` (`src/routes/routes.ts:8` → `src/controllers/tag.controller.ts:13`) — 唯一要删除的路由。鉴权 `auth.optional` (`src/controllers/tag.controller.ts:13`)，响应 `{ tags: string[] }` (`src/controllers/tag.controller.ts:16`)。
- `GET /api/articles?tag=...` (`src/controllers/article.controller.ts:25,30-37` → `src/services/article.service.ts:37-45`) — `tag` queryparam 通过 `tagList: { some: { name: query.tag } }` 过滤；tag 移除后该过滤条件无意义，必须清理。
- `POST /api/articles` / `PUT /api/articles/:slug` — `tagList` 字段在请求体与响应中均出现，删除后 `NewArticle.tagList` 写入与 `Article` 响应映射均需清理。
- `POST/DELETE /api/articles/:slug/favorite` — favorites 链路，**不动**。

### 数据结构

- `prisma/schema.prisma:14-27` `model Article`：`tagList Tag[]`（line 22）是隐式 M-N 关联，由 `prisma/migrations/20211001195651_implicit_articles/migration.sql:18-27` 的 `_ArticleToTag` 表承载。
- `prisma/schema.prisma:40-44` `model Tag { id, name @unique, articles Article[] }`：要删除的整个 model。
- `prisma/schema.prisma:46-58` `model User`：`favorites Article[] @relation("UserFavorites")`、`followedBy / following` 必须保留。
- `docs/swagger.json:893-944` `Article` 响应包含 `tagList: string[]`；`docs/swagger.json:969-988` `NewArticle` 包含 `tagList: string[]`；`docs/swagger.json:1084-1095` 定义 `TagsResponse`。
- `src/models/article.model.ts:1-10` `Article` interface 不含 `tagList`（即 `tagList` 只在 Prisma include 的运行时结果中出现，从未作为 DTO 类型暴露）。

### 依赖路径

- `tag.service.ts` → `prisma/prisma-client.ts`（`prisma.tag.groupBy`）— 删除文件即断开。
- `article.service.ts` → `prisma.prisma-client`（`prisma.article.findMany/update/create/delete`、`prisma.tag.groupBy` 无引用、`prisma.comment.*`）— 仍保留 favorites 链路。
- `routes.ts` → 各 controller — 删除 `tag.controller` 引用。
- `tests/services/article.service.test.ts` → `../../src/services/article.service`（仍保留 `favoriteArticle` / `unfavoriteArticle` / `deleteComment`）。

### 配置和权限

<!-- 凭证一律脱敏为 ***,只记键名和路径 -->
- `prisma/schema.prisma:4-7` datasource 走 `env("DATABASE_URL")`（Postgres）；本次不动 datasource，也不执行迁移。
- `package.json:35-46` 运行时依赖：不引入/移除依赖（用户禁改）。
- `tsconfig.json` / `jest.config.js` / `.eslintrc.json`：本次不动。

### 测试

- `npm test`（`package.json:8`）= `jest -i`。基线 5 suites / 26 passed / 1 todo (`exit 0`)。
- `tests/services/article.service.test.ts:1-132` 测试 `deleteComment` / `favoriteArticle` / `unfavoriteArticle`；mock payload 包含 `tagList: []`、`favoritedBy: []` — `tagList: []` 在新的 service 代码（不再 include tagList）下变成无害字段，可保留或删除，但需保证测试通过。
- `tests/services/tag.service.test.ts:1-6` 仅一个 `test.todo` stub — 整个文件删除。
- `tests/services/auth.service.test.ts` / `profile.service.test.ts` / `utils/profile.utils.test.ts` / `prisma-mock.ts` — 与 tag 无关，保留。

### 风格规范

- `_style-rules.md` 状态：无（项目级风格规范文件不存在，退回 profile `style_axes` + 运行时确认）
- `_project-map.md`【14】：无（无 pathfinder 产出）
- 风格分歧检测：不涉及
- 渐进积累：本轮无新增强制规则

观察到的代码风格（运行时确认）：

- 路由注释用 JSDoc `* @route {METHOD} /path` + `* @queryparam name desc` + `* @bodyparam name desc` + `* @returns key desc`。
- Service 函数导出用 named export（`export const getArticles = ...`），controller 端用 `import { ... } from '../services/article.service'`。
- Prisma 调用统一从 `prisma/prisma-client.ts` 单例导入；事务未使用（无 `prisma.$transaction`）。
- 错误处理：自定义 `HttpException(status, body)`，controller 通过 `next(error)` 传给 Express 错误中间件。
- Response 形状：`{ articles: [...], articlesCount }` / `{ article }` / `{ tags: [...] }` —— 不使用统一 envelope。

### 关键链路追踪

> 对本次变更涉及的错误处理链、中间件管线、数据流路径、配置依赖做追踪式分析，识别连带影响。

| 链路类型 | 入口 | 追踪路径 | 发现的二级影响 |
|---------|------|---------|--------------|
| 错误处理链 | `getTags` 抛错 → `tag.controller.ts:18` `next(error)` → Express 错误中间件 | 删除 controller/service 后链路消失；`article.service.ts` 中 `if (!title)` 等校验仍走 HttpException + next，不变 | 删除 tag 路由后客户端对 `/api/tags` 的 4xx/5xx 响应消失，错误中间件无需调整 |
| 中间件管线 | `routes.ts:7-11` 的 `.use(...)` 链 | 移除 `tagsController` 后 chain 缩短为 3 个；`auth.optional` / `auth.required` 仍由各 controller 局部挂载 | 无新增全局中间件；`src/index.ts`（未读取）可能 `.use('/api', api)`，不变 |
| 数据流路径 | `POST /api/articles` body → `createArticle` → `prisma.article.create({ tagList: { connectOrCreate } })` | 删除 schema 中 Tag 与 Article.tagList 后，`connectOrCreate` 写法无意义；同步删除请求体 `tagList` 字段读取、响应映射、`getArticles` 的 `tagList` include 与映射 | favorites 链路的 `favoritedBy` 关系不依赖 Tag，保留 |
| 配置依赖 | `prisma/schema.prisma:5-7` 走 `env("DATABASE_URL")` | schema 改动后已存在的 `prisma/migrations/*.sql` 与新 schema 不一致（仅 20211001 隐式 M-N 迁移引用了 Tag 与 _ArticleToTag），但本场景不执行真实迁移 | 真实部署需要新 migration；本次仅在隔离副本内改 schema，不动 migrations，不跑 migrate |

> 追踪结论：tag 链路拆除后 favorites 链路完全独立，无共享代码；唯一的连带影响是 Prisma 迁移目录会偏离新 schema，090 执行记录必须写明"不执行真实迁移的原因"。

## 6. 引用检查结果

| 分类 | 文件/对象 | 影响 | 处理方式 |
|------|-----------|------|----------|
| 必须同步修改 | `src/routes/routes.ts` | `.use(tagsController)` 仍存在会编译错误（import 指向不存在的模块） | 纳入 Step 8（routes 改写） |
| 必须同步修改 | `src/services/article.service.ts` | `'tag' in query` 块用 `tagList: { some: ... }`，`prisma.article.findMany` / `create` / `update` include 中有 `tagList`，响应映射有 `tagList: article.tagList.map(...)` | 纳入 Step 10（service 改写） |
| 必须同步修改 | `prisma/schema.prisma` | Tag model 与 Article.tagList 关系存在，迁移目录隐式承载 | 纳入 Step 11（schema 改写）+ 090 记录未执行迁移 |
| 必须同步修改 | `docs/swagger.json` | `/tags` path、`TagsResponse`、`Article.tagList`、`NewArticle.tagList`、`tag` queryparam | 纳入 Step 12（swagger 改写） |
| 必须同步修改 | `src/controllers/article.controller.ts` | JSDoc 中 `@queryparam tag` 与 `@bodyparam tagList list of tags` 仍存在；`tag` queryparam 在 `getArticles` 中被读取 | 纳入 Step 9（article.controller 改写） |
| 必须同步修改 | `tests/services/article.service.test.ts` | mock payload 含 `tagList: []` 字段；新 service 不再 include tagList，字段变成 noop | 纳入 Step 13（test 改写）：从 mock 中删除 `tagList: []` 以保持代码与新契约一致 |
| 必须同步删除 | `src/controllers/tag.controller.ts` | 整个文件仅做 `/tags` | 纳入 Step 4（删除文件） |
| 必须同步删除 | `src/services/tag.service.ts` | 整个文件仅导出 `getTags` | 纳入 Step 5（删除文件） |
| 必须同步删除 | `src/models/tag.model.ts` | 整个文件仅声明 `Tag` interface | 纳入 Step 6（删除文件） |
| 必须同步删除 | `tests/services/tag.service.test.ts` | 整个文件仅 stub `TagService.getTags` | 纳入 Step 7（删除文件） |
| 需要用户决策 | 是否保留 `GET /api/articles?tag=...` 的 `tag` queryparam | queryparam 字符串本身不在 must_not_contain，但底层依赖已删除（tagList 关系） | 已采纳：移除 queryparam 与 service 过滤块（与 tag 整体下线一致；保留会导致 422 或静默忽略） |
| 需要用户决策 | `prisma/migrations/*` 现有 SQL | 新 schema 与旧 migration 不一致，但本场景不执行真实迁移 | 已采纳：保留旧 migration 文件不动，090 记录"未生成新 migration / 未执行迁移"的原因 |
| 需要用户决策 | 旧 favoriteArticle/unfavoriteArticle 测试 mock 的 `tagList: []` 字段 | 移除 service 端 include 后字段变成 noop | 已采纳：从 mock payload 移除该字段以反映"service 不再返回 tagList" |
| 只需验证 | favorites 链路 | `favoriteArticle` / `unfavoriteArticle` / `favoritesCount` / `favoritedBy` 行为不变 | 验证方式：保留 include `favoritedBy` / `_count: { favoritedBy }` 与 result 中的 `favorited` / `favoritesCount` 字段 |
| 只需验证 | 现有 mock 结构 | `mockDeep<PrismaClient>()` 不需要按 schema 调整（无编译时 schema 绑定） | 验证方式：`npm test` |
| 暂不纳入 | `src/controllers/auth.controller.ts` / `profile.controller.ts` / `src/services/auth.service.ts` / `profile.service.ts` / `package.json` / `package-lock.json` | 用户 prompt 显式列为禁改 | 排除原因：未引用 tag，不在变更邻域 |
| 暂不纳入 | `prisma/prisma-client.ts` / `tests/prisma-mock.ts` / `src/models/article.model.ts` / 其他 model / utils | 视觉确认与 tag 无关 | 排除原因：未引用 tag |
| 暂不纳入 | `prisma/migrations/20211105082430_api_url` | 仅改 User.image 默认值，与 tag 无关 | 排除原因：未引用 tag |

> 找不到引用时写"未找到引用"，不得写成"无影响"。

## 7. 已确认事实

- tag 路由仅有一个 `GET /api/tags`，定义在 `src/controllers/tag.controller.ts:13`，鉴权 `auth.optional`，响应 `{ tags: string[] }` (`src/controllers/tag.controller.ts:13,16`)。
- `getTags` service 仅做 `prisma.tag.groupBy({ where: { articles: { some: { author: ... } } }, by: ['name'], orderBy: { _count: { name: 'desc' } }, take: 10 })` (`src/services/tag.service.ts:14-31`)。
- `Tag` model 仅含 `id` 与 `name @unique` (`prisma/schema.prisma:40-44`)。
- `Article.tagList Tag[]` 是隐式 M-N 关联（Prisma 生成 `_ArticleToTag` 中间表）(`prisma/schema.prisma:22`、`prisma/migrations/20211001195651_implicit_articles/migration.sql:18-27`)。
- `getArticles` 中 `tag` queryparam 通过 `tagList: { some: { name: query.tag } }` 过滤 (`src/services/article.service.ts:37-45`)；`swagger.json` 在 `GET /articles` 上声明同名 queryparam (`docs/swagger.json:333-338`)。
- `createArticle` 用 `tagList: { connectOrCreate: tagList.map(...) }` 写入 (`src/services/article.service.ts:201-218`)；`updateArticle` 走 `disconnectArticlesTags` + `connectOrCreate` (`src/services/article.service.ts:294-305, 330-351`)；`disconnectArticlesTags` 仅服务于 tagList 清空 (`src/services/article.service.ts:294-305`)。
- favorites 链路（`favoritedBy` 关系、`_count.favoritedBy` 计数、`favoriteArticle` / `unfavoriteArticle` service、`POST/DELETE /articles/:slug/favorite` 路由）独立于 tag 链路；删除 tag 不影响 favorites (`prisma/schema.prisma:23, 26` + `src/services/article.service.ts:525-571, 573-618` + `src/controllers/article.controller.ts:218-249`)。
- 现有测试 mock（`tests/services/article.service.test.ts:48, 103`）含 `tagList: []` 字段但只验证 `favoritesCount`。
- `tests/services/tag.service.test.ts:1-6` 仅一个 `test.todo` stub，无实质断言。
- 基线 `npm test` = 5 suites / 26 passed / 1 todo，退出码 0（已通过 `npm test` 验证，见 prep `commands/node-baseline-minimax-m3.txt`）。
- 仓库当前 HEAD = `6ac99ea5aeadc4e001dd4d6933c2e269f878a969`（main, origin/main）；`git status --short` 输出干净。
- `package.json` 运行时/开发依赖均不动；本场景不引入/移除依赖。

## 8. 待确认问题

> Phase 3 Step 3.0 不确定项分类后，代码可推断项已自行查证并写入 §7「已确认事实」，此处只保留业务需决策项。

### 代码推断项（已自行查证，无需用户确认）

- `auth.optional` 中间件要求 `req.user?.username` 可空（`src/controllers/tag.controller.ts:15`），删除 controller 后该分支消失；推断：无需调整 `utils/auth.ts`（`auth.optional` 仍被其他 controller 复用）。
- `tagList` 关系在 service 端通过 Prisma `include` 拉取，从未作为 DTO 类型暴露（`src/models/article.model.ts:1-10` 的 `Article` interface 不含 `tagList`）；推断：service 端移除 `include.tagList` + 响应 `tagList` 映射即可，DTO 类型层无需补字段删除。
- favorites 链路在 `prisma.article.update({ data: { favoritedBy: { connect/disconnect: ... } } })` 路径上完全独立；推断：删除 tag 不影响 favorites，无需在 service 中调整 `favoritedBy` include。

### 待用户确认项（业务决策）

> 本次 prompt 已经在用户原话中给出明确决策（"tags 功能没人用了，把 ... 都删掉"），且要求每步请求 `确认 Step N`。下列项作为风险/兼容记录，不是模糊点；实际 Step 执行时仍需在每步请求 `确认 Step N`。

- [x] 全量下线 tags（不留 `/tags` 路由、不留 `Tag` model、不留 article tagList I/O、不留 tag queryparam） — 用户原话已确认。
- [x] 不执行真实 DB 迁移 — 用户原话已确认；090 写明"未执行迁移的原因"。
- [x] 不修改 favorites 相关任何文件 — 用户原话已确认。
- [x] 不修改 package.json / package-lock.json / auth.* / profile.* — 用户原话已确认。

## 9. 暂不纳入范围

| 文件/对象 | 排除原因 |
|-----------|----------|
| `src/controllers/auth.controller.ts` | 用户 prompt 显式列为禁改；未引用 tag |
| `src/controllers/profile.controller.ts` | 同上 |
| `src/services/auth.service.ts` | 同上 |
| `src/services/profile.service.ts` | 同上 |
| `package.json` | 用户 prompt 显式列为禁改；不引入/移除依赖 |
| `package-lock.json` | 同上 |
| `prisma/prisma-client.ts` | 仅导出 PrismaClient 单例，未引用 tag |
| `tests/prisma-mock.ts` | `mockDeep<PrismaClient>()`，不按 schema 调整 |
| `src/models/article.model.ts` | `Article` interface 不含 tagList |
| `src/models/comment.model.ts` / `http-exception.model.ts` / `profile.model.ts` / `register-input.model.ts` / `registered-user.model.ts` / `user.model.ts` | 视觉确认与 tag 无关 |
| `src/utils/auth.ts` / `profile.utils.ts` / `token.utils.ts` / `user-request.d.ts` | 视觉确认与 tag 无关 |
| `prisma/migrations/20210924222830_initial/migration.sql` | 含 Tag / ArticleTags 表（已被 20211001 迁移替换为 _ArticleToTag），本次不执行迁移故保留 |
| `prisma/migrations/20211001195651_implicit_articles/migration.sql` | 含 _ArticleToTag 中间表 + Tag.name unique；本次不执行迁移故保留 |
| `prisma/migrations/20211105082430_api_url/migration.sql` | 仅改 User.image 默认值 |
| `prisma/migrations/migration_lock.toml` | 元数据文件，不引用具体表 |
| `src/index.ts` | 顶层 server bootstrap（未读取；tag 路由通过 `routes.ts` 暴露，无直接 import） |
| `README.md` / `CODE_OF_CONDUCT.md` / `CONTRIBUTING.md` / `LICENSE` / `Procfile` / `app.json` / `.github/workflows/*` / `.husky/*` / `.eslintrc.json` / `.prettierrc.json` / `.prettierignore` / `tsconfig.json` / `jest.config.js` / `public/*` / `media/*` | 视觉确认与 tag 无关（README 可能提及 Conduit tags，但用户 prompt 未要求改文档类元数据，列入"暂不纳入"，若影响验收可补 Step） |
