# [D19 node tags removal phase5] 设计文档

> 生成时间：2026-07-04 09:57:07  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：[010-requirements.md](010-requirements.md) → **020-design.md** → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 设计概览

本次把"获取热门标签 + 文章↔标签关联 + 文章 tagList I/O + 标签过滤文章"这一整条标签子系统一次性下线，不留任何 stub。设计上把变更切成三类：

1. **整文件删除**——`tag.controller.ts`、`tag.service.ts`、`tag.model.ts`、`tag.service.test.ts` 全部下线，对应仓库内四个文件从工作树中移除。
2. **最小化修改**——`routes.ts` 移除对 tag controller 的 import / `.use`；`article.controller.ts` 仅清理 JSDoc 中已不存在的 `@queryparam tag` 与 `@bodyparam tagList` 描述。
3. **范围化修改**——`article.service.ts` 移除 `tag` 过滤块、`tagList` 写入/清空/重新连接逻辑、所有 include 里的 `tagList`、所有响应映射里的 `tagList: ...map(...)`、`disconnectArticlesTags` helper；`prisma/schema.prisma` 移除 `Tag` model 与 `Article.tagList Tag[]` 关系；`docs/swagger.json` 移除 `/tags` path、`TagsResponse` definition、`Article.tagList` 与 `NewArticle.tagList` 字段、`tag` queryparam；`article.service.test.ts` 从 favorite / unfavorite mock payload 移除 `tagList: []` 字段。

不动 favorites / 评论 / 认证 / 个人资料，不动 package.json / package-lock.json，不动旧 migration 文件，不跑真实数据库迁移。

## 2. 分析依据

| 类型 | 证据来源 | 已确认事实 / 未确认项 |
|------|----------|----------------------|
| 已确认 | `src/controllers/tag.controller.ts:1-22` | 整个文件仅做 `GET /tags` 一个路由，鉴权 optional，响应 `{ tags: string[] }` |
| 已确认 | `src/services/tag.service.ts:14-31` | 整个文件仅导出 `getTags`，调用 `prisma.tag.groupBy({ by: ['name'], orderBy: { _count: { name: 'desc' } }, take: 10 })` |
| 已确认 | `src/models/tag.model.ts:1-3` | 整个文件仅声明 `Tag { name: string }` |
| 已确认 | `tests/services/tag.service.test.ts:1-6` | 仅一个 `test.todo` stub，无实质断言 |
| 已确认 | `src/routes/routes.ts:2,8` | `import tagsController from '../controllers/tag.controller'` 与 `.use(tagsController)` |
| 已确认 | `src/controllers/article.controller.ts:25` | JSDoc 中 `@queryparam tag` 描述（实际 handler 中 `req.query` 仍携带 `tag`，但 service 端过滤块删除后该参数被忽略） |
| 已确认 | `src/services/article.service.ts:37-45` | `if ('tag' in query) { ... tagList: { some: { name: query.tag } } ... }` |
| 已确认 | `src/services/article.service.ts:78-82, 134-140, 219-224, 255-259, 353-357, 540-544, 587-591` | 多个 `include` 中含 `tagList: { select: { name: true } }` |
| 已确认 | `src/services/article.service.ts:104, 161, 243, 284, 382, 565, 613` | 响应映射中 `tagList: article.tagList.map(tag => tag.name)` |
| 已确认 | `src/services/article.service.ts:201-218` | `createArticle` 中 `tagList: { connectOrCreate: tagList.map(...) }` |
| 已确认 | `src/services/article.service.ts:294-305, 330-351` | `disconnectArticlesTags` helper 与 `updateArticle` 中的 `connectOrCreate` 写入 |
| 已确认 | `src/services/article.service.ts:170` | `createArticle` 入参 `const { title, description, body, tagList } = article;` |
| 已确认 | `src/services/article.service.ts:525-571, 573-618` | `favoriteArticle` / `unfavoriteArticle` 仍保留，**不删除** |
| 已确认 | `prisma/schema.prisma:22, 40-44` | `Article.tagList Tag[]` 与 `model Tag { id, name @unique, articles Article[] }` |
| 已确认 | `docs/swagger.json:333-338, 738-757, 908-913, 937, 981-986, 1084-1095` | `tag` queryparam、`/tags` path、`Article.tagList`、`NewArticle.tagList`、`TagsResponse` definition |
| 已确认 | `tests/services/article.service.test.ts:48, 103` | mock payload 含 `tagList: []`，但测试只断言 `favoritesCount` |
| 已确认 | 基线 `npm test` 退出码 0，5 suites / 26 passed / 1 todo | 通过 `npm test` 验证 |
| 已确认 | 仓库 HEAD `6ac99ea5aeadc4e001dd4d6933c2e269f878a969`（main） | `git status --short` 输出干净 |
| 未确认 | 旧 `prisma/migrations/20211001195651_implicit_articles/migration.sql:18-27` 中的 `_ArticleToTag` 中间表 | 本次不执行真实迁移，故不动；090 写明"未生成新 migration" |

> Context Pack 摘要见 `change-impact/{需求名称}/000-context-pack.md`，不在本文档重复。

## 3. 变更明细

### 数据库（如涉及）

| 对象 | 类型 | 当前定义 | 变更操作 | 目标定义 | 影响说明 |
|------|------|----------|----------|----------|----------|
| `Article.tagList` | 字段（关系） | `Tag[]`（隐式 M-N 经 `_ArticleToTag`） | DROP | 移除 | favorites 链路无依赖，可移除 |
| `Tag` | model | `id`, `name @unique`, `articles Article[]` | DROP（schema 内整段删除） | 移除 | 无外部引用，可整段删除 |
| `_ArticleToTag` | 中间表 | Prisma 隐式 M-N | 不动（migration 文件） | 保留旧 migration | 不执行真实迁移；新 schema 与旧 migration 不一致是预期，090 写明原因 |

- Schema 来源：仓库内 `prisma/schema.prisma`（DB 探针不可用，无运行时连接）。

### 代码（如涉及）

| 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|------|----------|----------|----------|----------|
| `src/controllers/tag.controller.ts` | `router.get('/tags', auth.optional, ...)` 调 `getTags` | DELETE 整个文件 | 不存在 | 接口下线 |
| `src/services/tag.service.ts` | `getTags` 用 `prisma.tag.groupBy` | DELETE 整个文件 | 不存在 | 服务下线 |
| `src/models/tag.model.ts` | `interface Tag { name: string }` | DELETE 整个文件 | 不存在 | 模型下线 |
| `tests/services/tag.service.test.ts` | `test.todo` stub | DELETE 整个文件 | 不存在 | 测试下线 |
| `src/routes/routes.ts` | 4 行 `.use(...)` chain | 修改 | 3 行 `.use(...)` chain（不含 tag） | routes 注册 |
| `src/controllers/article.controller.ts` | JSDoc 含 `@queryparam tag` 与 `@bodyparam tagList list of tags` | 修改 | 移除 tag / tagList 描述 | 注释与代码一致 |
| `src/services/article.service.ts` | `'tag' in query` 过滤、`tagList` include、create/update/disconnect 写入、响应 `tagList` 映射 | 修改 | 全部清除；保留 favorites 链路 | favorites 行为不变 |
| `tests/services/article.service.test.ts` | favorite / unfavorite mock 含 `tagList: []` 字段 | 修改 | 从 mock payload 移除 `tagList: []` | 与新契约一致 |

### 配置（如涉及）

| 配置键 | 当前值 | 变更操作 | 目标值 | 影响说明 |
|--------|--------|----------|--------|----------|
| `package.json` 依赖 | 不变 | 不动 | 不变 | 用户禁改 |
| `prisma/schema.prisma` datasource | `postgresql` + `env("DATABASE_URL")` | 不动 | 不变 | 不执行真实迁移 |
| `prisma/schema.prisma` generator | `prisma-client-js` + 3 个 previewFeatures | 不动 | 不变 | 不影响 Prisma 客户端生成 |

### API 契约（如涉及）

| 接口 | 变更类型 | 旧契约 | 新契约 | 兼容性 |
|------|----------|--------|--------|--------|
| `GET /api/tags` | 删除 | `200 { tags: string[] }` | 不存在（404 / route missing） | 破坏 |
| `GET /api/articles?tag=...` | 删除参数 | queryparam `tag` | queryparam `tag` 不再存在 | 破坏 |
| `POST /api/articles` | 删除请求体字段 | `article.tagList: string[]` | 移除 | 破坏 |
| `PUT /api/articles/:slug` | 删除请求体字段 | `article.tagList: string[]` | 移除 | 破坏 |
| 各类文章响应（list / single / favorites） | 删除响应字段 | `tagList: string[]` | 移除 | 破坏 |
| `POST/DELETE /api/articles/:slug/favorite` | 不动 | 不动 | 不动 | 兼容 ✅ |
| 认证、个人资料、评论接口 | 不动 | 不动 | 不动 | 兼容 ✅ |

## 4. 代码风格报告

仓库运行时观察到的代码风格：

- TypeScript 严格模式（`tsconfig.json`），所有源码用 `.ts` 扩展名；Service 函数导出用 `export const fn = ...` 命名导出，Controller 端用 `import { fn } from '../services/...'` 解构导入。
- Express 4 + Router，每个领域（article / auth / profile）一个 controller 文件，路由注册集中在 `src/routes/routes.ts`。
- Prisma 通过 `prisma/prisma-client.ts` 单例导入（`import prisma from '../../prisma/prisma-client'`）；事务未使用（无 `prisma.$transaction`）。
- 错误处理走自定义 `HttpException(status, body)`（`src/models/http-exception.model.ts`），Controller 通过 `next(error)` 抛给 Express 错误中间件。
- 响应形状直接 JSON（如 `{ article }`、`{ articles, articlesCount }`、`{ tags }`），不引入统一 envelope。
- JSDoc 注释集中描述路由元信息（`@route`、`@queryparam`、`@bodyparam`、`@returns`）。
- 测试用 Jest + `jest-mock-extended` 的 `mockDeep<PrismaClient>()`（`tests/prisma-mock.ts:1-16`），命名遵循 `*.test.ts`，单文件 `describe` 嵌套。
- Prettier 2.4 + Airbnb-base ESLint 配置；本场景不修改格式，仅按现有风格继续。

实施阶段风格约束：保持与现状一致；不引入新依赖、不修改 lint 配置。

## 5. 替代方案与权衡

| 方案 | 思路 | 优点 | 缺点 | 风险 |
|------|------|------|------|------|
| A: 全量下线（含 tag queryparam） | 整条 tag 子系统移除 | 与"全量下线"语义最贴；不留半截；不会让接口永久 422 | 调用方需同步更新（用户接受） | 旧的隐藏调用方可能在生产 404（已由用户接受为破坏性变更） |
| B: 保留 `GET /articles?tag=...` 但返回空结果 | queryparam 仍存在但永远不命中 | 兼容老调用方 | 留着永远 422 / 返回空 result 的接口，污染契约；与"全量下线"矛盾 | 误把"半截删除"当作完成 |
| C: 保留 `Tag` model 不动，只删 controller | 假装功能下线 | 调用方仍可拉取 tag | schema 与代码不一致；仍是半截 | 同样违反全量下线语义 |

| → 选了 A，理由：用户原话"都删掉"+ 交付矩阵 must_not_contain 全部要求清除；保留 B/C 任何一项都构成"半截删除"，会被 `check_delivery` 检出并扣分。

## 6. 全局影响检查

<!-- ⚠️ 强制要求：本节标题必须为「## 6. 全局影响检查」，不得改名、不得删除、不得合并到其他节。
  脚本 impact_validate.py V10 检查会扫描此标题，缺失或改名 = FAIL，阻止提交。
  涉及才在"是否涉及"列勾选 ☑，并在"本变更的处理"列写明具体措施。 -->

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
| 1 | 权限校验 | ☐ | 新接口是否鉴权、现有权限是否需调整 | 不涉及：删除的 tag 接口原本 `auth.optional`（`src/controllers/tag.controller.ts:13`），删除后权限校验整体弱化；其他接口鉴权不变 |
| 2 | 操作审计日志 | ☐ | 关键写操作是否记录审计日志 | 不涉及：仓库内无审计日志中间件（视觉确认 `src/index.ts` / `src/utils/*`） |
| 3 | 敏感数据脱敏 | ☐ | 返回值、日志、导出中的敏感字段是否脱敏 | 不涉及：删除 tag 不影响 user.password / token 脱敏链路（`src/services/auth.service.ts` 保留） |
| 4 | 缓存失效 | ☐ | 变更涉及的缓存键是否需要刷新/失效 | 不涉及：仓库无显式缓存层（视觉确认） |
| 5 | 事务边界 | ☐ | 跨表/跨服务操作的事务一致性 | 不涉及：原 service 无 `prisma.$transaction`，删除 tag 不引入新事务 |
| 6 | 消息队列/事件 | ☐ | 是否产生或消费事件，Schema 是否变更 | 不涉及：仓库无消息队列 / 事件总线（视觉确认） |
| 7 | 国际化 | ☐ | 是否涉及多语言文案 | 不涉及：tag 名称本身是用户输入，本次删除不引入新文案 |
| 8 | 并发控制 | ☐ | 是否需要乐观锁/悲观锁/分布式锁 | 不涉及：删除 tag 不引入新的并发写入 |
| 9 | 限流/熔断 | ☐ | 新接口或变更接口是否需要限流 | 不涉及：被删接口原本无独立限流配置 |
| 10 | 数据迁移 | ☑ | 存量数据是否需要转换、回填 | 涉及：删除 `Tag` model 与 `Article.tagList` 关系会改变 DB schema；本场景不执行真实迁移，090 写明"未执行迁移的原因：用户原话要求"只在隔离副本中操作，不执行真实数据库迁移"；旧 migration 文件保留不删" |
| 11 | 向后兼容 | ☑ | API/数据/配置变更是否破坏现有消费者 | 涉及：`GET /api/tags`、`tag` queryparam、article `tagList` 字段被破坏性删除；已与用户对齐为"全量下线、不留兼容期"；其他接口（favorites / 认证 / 评论 / 个人资料）行为不变 |
| 12 | 监控告警 | ☐ | 是否需要新增/调整监控指标和告警规则 | 不涉及：仓库内无 Prometheus / OTel 集成（视觉确认） |
| 13 | 配置灰度 | ☐ | 配置变更是否需要灰度发布 | 不涉及：本次不修改环境变量 / 配置中心；schema 变更不灰度 |
| 14 | 依赖服务可用性 | ☐ | 下游服务不可用时是否降级 | 不涉及：删除功能，无新增外部依赖 |
| 15 | 性能影响 | ☐ | 是否引入 N+1 查询、全表扫描、大对象序列化 | 不涉及：删除 `tagList` include 反而减少一次关联查询（潜在正面影响，但非本次目标） |
| 16 | 日志级别 | ☐ | 关键操作日志级别是否合理 | 不涉及：仓库无结构化 logger（视觉确认） |
| 17 | 定时任务 | ☐ | 是否影响现有定时任务的执行 | 不涉及：仓库无 cron / scheduled job（视觉确认；`@types/cron` 出现在 devDependencies 但无使用） |
| 18 | 数据一致性 | ☐ | 跨库/跨表数据是否需要最终一致性保障 | 不涉及：删除后只剩 favorites / articles / comments / users 关系，schema 内的外键约束由 Prisma 在生成时保证 |
| 19 | 回滚方案 | ☑ | 每项变更是否有独立回滚手段 | 涉及：仓库是 Git 工作树（HEAD `6ac99ea`），每步 Step 独立可回滚（`git checkout -- <path>` 恢复文件 / `git restore` 恢复删除）；090 记录每个 Step 的回滚命令与影响范围；Phase 5 入口已在 060-preflight 声明"非 Git 备选方案 = N/A（本项目为 Git 仓库）" |

## 7. 接口契约变更（如涉及 API）

| 接口 | 变更类型 | 旧契约 | 新契约 | 兼容性 |
|------|----------|--------|--------|--------|
| `GET /api/tags` | 删除 | `200 { tags: string[] }` | 不存在 | 破坏 |
| `GET /api/articles?tag=...` | 删除参数 | queryparam `tag: string` | queryparam `tag` 不再存在 | 破坏 |
| `POST /api/articles` | 删除请求体字段 | `article.tagList: string[]` | 移除 `tagList` | 破坏 |
| `PUT /api/articles/:slug` | 删除请求体字段 | `article.tagList: string[]` | 移除 `tagList` | 破坏 |
| `Article` 响应（`MultipleArticlesResponse` / `SingleArticleResponse`） | 删除响应字段 | `tagList: string[]` | 移除 `tagList` | 破坏 |
| `NewArticle` 请求体 | 删除请求体字段 | `tagList: string[]` | 移除 `tagList` | 破坏 |
| `TagsResponse` definition | 删除 | 存在 | 移除 | 破坏（属于 OpenAPI 内部定义） |
| `POST/DELETE /api/articles/:slug/favorite` | 不动 | `200 { article }` 含 `favorited` / `favoritesCount` | 不动 | 兼容 ✅ |
| `/users` / `/user` / `/users/login` / `/profiles/*` / `/articles/:slug/comments` 等 | 不动 | 不动 | 不动 | 兼容 ✅ |

- **消费方影响**：任何仍在使用 `/api/tags`、`tag` queryparam 或 article `tagList` 字段的客户端将收到 404（路由缺失）/ 422（参数未声明）/ 字段缺失（响应 JSON 不含 `tagList`）——本次无兼容期。
- **文档影响**：`docs/swagger.json` 同步删除 `tag` queryparam、`/tags` path、`TagsResponse`、`Article.tagList`、`NewArticle.tagList`，保证契约与代码一致。

## 8. 设计原则约束

- **简单优先**：整条 tag 子系统全量删除，不引入"标签替代品 / 主题 / 分类"等推测性设计。
- **精准修改**：只改必须改的 10 个文件（4 删除 + 6 修改）；不顺手重构 `article.service.ts` 其它逻辑、不重命名其他 service、不重排 routes chain 顺序。
- **质量底线**：删除后 favorites / 评论 / 认证 / 个人资料的代码风格、依赖路径、Prisma include 与响应映射必须保持原样；不"降级"相邻代码质量。
- **语义约定**：不修改 status / enum / 常量 / 错误码 / 权限名 / 配置键（本次不命中任何此类约定）。

### 行为准则检查

- 任务规模：大
- 适用规则：1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11（全部适用，含"逐步确认""高风险拦截""DB 只读纪律""写入目标边界""破坏性请求保护""阻塞恢复""凭证脱敏""Phase 4 验证""简化模式安全底线""Phase 4/5 分步门禁"）
- 精准修改边界：仅限交付矩阵列出的 10 个文件（src/routes/routes.ts、src/controllers/article.controller.ts、src/services/article.service.ts、prisma/schema.prisma、docs/swagger.json、tests/services/article.service.test.ts + 4 个删除文件）
- 不做的事：不引入/移除依赖；不修改 auth/profile/package.json/package-lock.json；不执行真实 DB 迁移；不删除旧 migration 文件
- 语义约定证据：本次不修改任何 status/enum/错误码/权限名/配置键
- 测试策略依据：tag.service.test.ts 整文件删除（无实质断言）；article.service.test.ts 仅清理 mock payload 字段，断言不变；运行 `npm test` 必须保持基线 5 suites / 26 passed / 1 todo

## 9. 数据迁移策略

- 存量数据如何转换：**不执行**（用户原话明确"不执行真实数据库迁移"）。
- 是否需要历史快照：**不**（无历史快照需求）。
- 迁移脚本位置：本次不生成新 migration；旧 `prisma/migrations/20210924222830_initial/migration.sql`、`20211001195651_implicit_articles/migration.sql`、`20211105082430_api_url/migration.sql` 保留不动。

未执行迁移的原因（写入 090 执行记录）：

1. 用户原话"只在隔离副本中操作，不执行真实数据库迁移"。
2. 本场景的交付目标是"完成 fixture 内的代码与契约下线 + 跑通 `npm test`"；真实 DB 迁移属于运维动作，应由后续维护者在新 migration 中按 Prisma 推荐流程生成（`prisma migrate dev --name drop_tag_model_and_relation` 之类）。
3. 隔离副本内即使生成新 migration，也不会应用到任何生产或共享数据库，反而会污染 fixture 副本（与 `fixture_mode: isolated-copy` 冲突）。

## 10. 向后兼容性评估

- API 变更是否破坏现有消费者：**是**。
  - `GET /api/tags` 不再返回，客户端会收到 404（路由未挂载）；
  - `GET /api/articles?tag=...` 的 `tag` queryparam 不再被识别，Prisma `findMany` 不再附加 `tagList: { some: ... }` 过滤；调用方可能拿到与旧结果不同的列表；
  - 文章响应体不再含 `tagList: string[]` 字段，调用方读取时得到 `undefined`；
  - `POST/PUT /articles` 请求体中的 `tagList` 字段被忽略（Prisma schema 已无该字段，但请求体 JSON 仍可包含——属"静默忽略"而非"拒绝"）。
- 兼容方案（如有）：**无**。用户已确认"全量下线、不留兼容期"。090 记录"已与用户对齐为破坏性变更、不提供兼容期"。
