# [D19 node tags removal phase5] 设计文档

> 生成时间：2026-07-04 12:17:33  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：[000-context-pack.md](000-context-pack.md) → [010-requirements.md](010-requirements.md) → **020-design.md** → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 设计概览

本次变更的设计思路是"按代码事实全量下线 tags 子系统"，具体包括：删除 `Tag` model 与 `Article↔Tag` 隐式 M-N 关联、删除 `GET /api/tags` 路由与配套 controller/service/model/test、清理 `article.service.ts` 中所有 `tagList` 的 include / 写入 / 响应映射（含 `?tag=` queryparam 过滤块与 `disconnectArticlesTags` 内部辅助函数）、同步更新 `prisma/schema.prisma` 与 `docs/swagger.json` 的 API 契约。**核心决策**：不做兼容期、不保留 tag queryparam、不清理旧 `prisma/migrations/*`（已通过用户原话确认）。favorites 链路（`favoriteArticle` / `unfavoriteArticle` / `favoritedBy` / `_count.favoritedBy` / `favoritesCount`）物理独立，不需任何改动即可保留。**关于数据库迁移**：按用户原话，本次不在隔离副本内执行 `prisma migrate`，仅在 schema 文件中删除 `Tag` model 与 `Article.tagList` 关联；隔离副本不连真实 DB；090 必须写明未执行迁移的原因与替代责任归属。

## 2. 分析依据

| 类型 | 证据来源 | 已确认事实 / 未确认项 |
|------|----------|----------------------|
| 已确认 | `src/routes/routes.ts:2,8` | 路由链中导入并 `.use(tagsController)`，删除后必须同步移除 import 与 use |
| 已确认 | `src/controllers/tag.controller.ts:1-22` | 整个文件仅暴露 `GET /api/tags` 一条路由，鉴权 `auth.optional` |
| 已确认 | `src/services/tag.service.ts:1-35` | 整个文件仅导出 `getTags`，依赖 `prisma.tag.groupBy` |
| 已确认 | `src/models/tag.model.ts:1-3` | 整个文件仅声明 `Tag` interface（与 Prisma model 同名） |
| 已确认 | `tests/services/tag.service.test.ts:1-6` | 整个文件仅一个 `test.todo` stub，无实质断言 |
| 已确认 | `prisma/schema.prisma:14-27,40-44` | `Article.tagList Tag[]` 隐式 M-N；`Tag { id, name @unique, articles Article[] }` |
| 已确认 | `src/services/article.service.ts:37-45` | `?tag=...` 过滤通过 `tagList: { some: { name: query.tag } }` |
| 已确认 | `src/services/article.service.ts:201-218,294-305,330-351` | `createArticle`/`updateArticle` 通过 `connectOrCreate` 写 tagList；`disconnectArticlesTags` 内部辅助函数仅服务于 tagList |
| 已确认 | `src/services/article.service.ts:525-571,573-618` | favorites 链路（`favoriteArticle`/`unfavoriteArticle`）物理独立，仅依赖 `favoritedBy` 与 `_count` |
| 已确认 | `docs/swagger.json:738-757,893-944,969-988,1084-1095` | `/tags` path、`TagsResponse`、`Article.tagList`、`NewArticle.tagList` |
| 已确认 | `prisma/migrations/20211001195651_implicit_articles/migration.sql:18-27` | 隐式 M-N 由 `_ArticleToTag` 中间表承载；本场景不 migrate |
| 已确认 | `tests/services/article.service.test.ts:48,103` | favoriteArticle/unfavoriteArticle 的 mock payload 含 `tagList: []` 字段 |
| 已确认 | `prep/commands/node-baseline-minimax-m3.txt` | 基线 `npm test` = 5 suites / 26 passed / 1 todo / exit 0 |
| 不采用的推断 | "D19R1 经验：可保留 `tagList: []`" | 已被 D19R2 验收矩阵 must_not_contain 否决（`tagList` 必须 0 命中） |
| 未确认 | 生产环境是否有外部 SDK 消费 `/api/tags` | 与本次隔离副本验收无关；090 记录为"破坏性变更，调用方需同步更新" |

> Context Pack 摘要见 `change-impact/node-tags-removal-phase5/000-context-pack.md`，不在本文档重复。

## 3. 变更明细

### 3.1 数据库

| 对象 | 类型 | 当前定义 | 变更操作 | 目标定义 | 影响说明 |
|------|------|----------|----------|----------|----------|
| `Tag` | Prisma model | `id Int @id, name String @unique, articles Article[]` | DROP（仅 schema 文件） | （不存在） | 真实 DB 不连；schema 与旧 migration 偏离；090 写明"未执行迁移" |
| `Article.tagList` | Prisma relation 字段 | `tagList Tag[]`（隐式 M-N `_ArticleToTag`） | DROP（仅 schema 文件） | （不存在） | favorites 链路不依赖 Tag，独立保留 |
| `User.favorites` | Prisma relation 字段 | `favorites Article[] @relation("UserFavorites")` | 不动 | （保持） | favorites 链路保留的核心 |
| `Article.favoritedBy` | Prisma relation 字段 | `favoritedBy User[] @relation("UserFavorites")` | 不动 | （保持） | 收藏计数与是否已收藏字段来源 |
| `_ArticleToTag`（Prisma 隐式 M-N 中间表） | Prisma 隐式生成 | 在 schema 中由 `Article.tagList Tag[]` 隐式生成 | 随 `Article.tagList` 移除而失效 | （不存在） | 不执行真实 migrate；不清理旧 migration 文件 |

- Schema 来源：`prisma/schema.prisma` 全文读取
- DB 真实状态：不连（隔离副本）；任何"删除 Tag 表行"在生产环境的责任不在本场景

### 3.2 代码

| 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|------|----------|----------|----------|----------|
| `src/controllers/tag.controller.ts` | `GET /api/tags` + `auth.optional` + `getTags` 调用 | 删除文件 | （不存在） | `/api/tags` 调用方得 404 |
| `src/services/tag.service.ts` | `getTags(username?)` + `prisma.tag.groupBy` | 删除文件 | （不存在） | 与 controller 一并消失 |
| `src/models/tag.model.ts` | `export interface Tag { name: string }` | 删除文件 | （不存在） | 无其他文件 import 它（视觉确认） |
| `tests/services/tag.service.test.ts` | 单一 `test.todo` stub | 删除文件 | （不存在） | 测试套件 5→4 |
| `src/routes/routes.ts` | `.use(tagsController)` chain | 修改 | chain 缩短为 3 个，移除 import | 编译需通过 |
| `src/controllers/article.controller.ts` | JSDoc 含 `@queryparam tag` | 修改 | 移除该 JSDoc 行 | 不影响运行时 |
| `src/services/article.service.ts` | `'tag' in query` 过滤块 / `tagList` include×4 / `tagList` 响应映射×5 / `disconnectArticlesTags` / `tagList` 写入 | 修改 | 全部移除；favorites include 保留 | favorites 行为不变；API 响应不再含 `tagList` |
| `prisma/schema.prisma` | `Tag` model + `Article.tagList Tag[]` | 修改 | 删除上述两处；`User.favorites`、`favoritedBy` 不动 | schema 与旧 migration 偏离 |
| `docs/swagger.json` | `/tags` / `TagsResponse` / `Article.tagList` / `NewArticle.tagList` / `?tag=` queryparam | 修改 | 全部移除；JSON 保持合法 | API 契约与代码一致 |
| `tests/services/article.service.test.ts` | favoriteArticle/unfavoriteArticle mock 含 `tagList: []` | 修改 | 从 mock payload 删除该字段 | 反映"service 不再返回 tagList" |

### 3.3 配置

无配置项变更（`package.json` / `.env*` / `tsconfig.json` / `jest.config.js` 均不动）。

### 3.4 数据库迁移策略

- **不在隔离副本内执行 `prisma migrate`**（用户原话 + 隔离副本不连真实 DB）。
- 不删除 `prisma/migrations/20210924222830_initial/migration.sql`、`20211001195651_implicit_articles/migration.sql`、`20211105082430_api_url/migration.sql`（它们反映历史真实状态；清理属于后续维护者责任）。
- 真实部署时，生产 DBA 需在窗口内执行 `prisma migrate` 新建 migration 删除 `Tag` + `_ArticleToTag`，与本次隔离副本验证无关。
- 090 必须写明"未执行迁移的原因 + 责任归属"。

## 4. 代码风格报告

- 缩进：2 空格；行尾：源仓库 CRLF（实测有 CRLF，需在写入时保持 LF 以通过 `git diff --check`，D19R1 已踩过坑）。
- 命名：camelCase 函数/字段、PascalCase interface、snake_case 仅在 Prisma `@@map` / 列名（如 `_count`）出现。
- Service 导出：named export；controller 用 `import { ... } from '../services/article.service'`。
- Prisma 客户端：单例从 `prisma/prisma-client.ts` 导入；无 `prisma.$transaction`。
- 错误处理：自定义 `HttpException(status, body)`，controller 用 `next(error)` 提交 Express 错误中间件。
- 响应：非统一 envelope；`{ articles, articlesCount }` / `{ article }` / `{ comments }`。
- 路由注释：JSDoc `* @route {METHOD} /path` + `@queryparam` / `@bodyparam` / `@returns`。
- 测试：Jest + `mockDeep<PrismaClient>()`（来自 `tests/prisma-mock.ts`），断言用 `resolves.toHaveProperty(...)` / `rejects.toThrowError()`。

### 实施阶段风格约束

| style_axes 轴名 | 从代码确认的约束内容 |
|-----------------|---------------------|
| naming | camelCase 函数、PascalCase interface；Prisma model 用 PascalCase 单数；本场景删除 `Tag` interface（PascalCase）符合命名规范 |
| layering | routes → controllers → services → prisma 分层；tag 子系统三层都删；不动 favorites / auth / profile 层级 |
| orm | Prisma schema 单源；`prisma-client.ts` 单例；本场景改 schema 后无新 migration |
| transaction | 无 `$transaction`；本场景不引入 |
| exception | `HttpException(status, body)` + `next(error)`；不引入新错误码 |
| logging | 无 logger；不引入 |
| api_response | 非 envelope；删除后 article 响应少 `tagList` 字段；favorites 字段全部保留 |
| dependency_injection | PrismaClient 单例直接 import；本场景不动 prisma-client.ts |

## 5. 替代方案与权衡

| 方案 | 思路 | 优点 | 缺点 | 风险 |
|------|------|------|------|------|
| A: 全量下线（选定） | 删 Tag model / route / service / article I/O / swagger / test | 简洁；无半截功能；D19R1 已验证可行 | 破坏性变更；旧调用方 404 | favorites 误删；已通过 D19R1 验收与本次未引用 favorites 证明风险低 |
| B: 灰度兼容（不选） | 保留 `Tag` model 与 `/api/tags` 返回空，标记 deprecated | 调用方可平滑过渡 | tag 仍是死代码；"没人用了"的需求未满足；用户原话"都删掉"否决 | 留下"半截删除"反模式 |
| C: 仅删接口不删 schema（不选） | 删 route/controller 但保留 `Tag` model | schema 改动小 | `tagList` 关系无消费者；article service 中 `tagList` 残留；acceptance `model Tag` must_not_contain 必失败 | 留 dead schema；与"全量下线"语义不符 |

→ 选了 **A**，理由：用户原话"tags 功能没人用了，把 ... 都删掉"明确指向全量；D19R1 已证明 favorites 可物理独立保留；隔离副本不连真实 DB，破坏性变更的风险已隔离。

## 6. 全局影响检查

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
| 1 | 权限校验 | ☑ | `auth.optional` 仍被其他路由复用；删除 tag 路由不调整 `utils/auth.ts` | 不动 `utils/auth.ts`；`auth.optional` 在 `article.controller.ts:30,89,155`、`profile.controller` 等继续使用 |
| 2 | 操作审计日志 | ☐ | 项目无 logger | 不涉及 |
| 3 | 敏感数据脱敏 | ☐ | 标签为非敏感字符串；删除后无新返回 | 不涉及 |
| 4 | 缓存失效 | ☐ | 项目无缓存层 | 不涉及 |
| 5 | 事务边界 | ☐ | `prisma.tag.groupBy` 单次调用；删除后无跨表事务变化 | 不涉及（且 favorites 链路不引入 `$transaction`） |
| 6 | 消息队列/事件 | ☐ | 项目无消息队列 | 不涉及 |
| 7 | 国际化 | ☐ | 不涉及多语言文案 | 不涉及 |
| 8 | 并发控制 | ☐ | favorites 链路无乐观锁/悲观锁；删除 tag 不引入并发 | 不涉及 |
| 9 | 限流/熔断 | ☐ | 项目无限流中间件 | 不涉及 |
| 10 | 数据迁移 | ☑ | schema 删除 Tag / Article.tagList；旧 migration 偏离；本场景不执行 migrate | 隔离副本不连真实 DB；090 写明"未执行迁移的原因"；旧 migration 保留 |
| 11 | 向后兼容 | ☑ | `/api/tags` → 404；`POST /api/articles` body.tagList 字段被忽略；article 响应少 `tagList` 字段 | 不承诺兼容期；090 写明"破坏性变更，调用方需同步更新" |
| 12 | 监控告警 | ☐ | 项目无监控指标 | 不涉及 |
| 13 | 配置灰度 | ☐ | 无配置变更 | 不涉及 |
| 14 | 依赖服务可用性 | ☐ | 标签为本地 DB 表，不依赖外部服务 | 不涉及 |
| 15 | 性能影响 | ☑ | 删除 `tagList` include×4 → article 查询少 1 个 join；favorites include 保留 | 净性能略提升；n+1 风险无新增（favorites `_count` 仍是单次聚合） |
| 16 | 日志级别 | ☐ | 项目无 logger | 不涉及 |
| 17 | 定时任务 | ☐ | 无定时任务 | 不涉及 |
| 18 | 数据一致性 | ☑ | 删 schema 后 favorites / articles 关系不变；`_ArticleToTag` 中间表在生产环境需手动迁移 | 090 写明"生产环境需 DBA 窗口内 migrate"；隔离副本不连 DB 无一致性风险 |
| 19 | 回滚方案 | ☑ | 每步独立 `git checkout HEAD -- <path>`；删除的文件可 `git checkout HEAD` 恢复 | 090 表格逐项列出回滚命令；删除文件 4 个 + 修改文件 6 个均独立可回滚 |

## 7. 接口契约变更

| 接口 | 变更类型 | 旧契约 | 新契约 | 兼容性 |
|------|----------|--------|--------|--------|
| `GET /api/tags` | 路径删除 | `200 { tags: string[] }` | `404` | **破坏性** |
| `GET /api/articles?tag=foo` | queryparam 静默忽略 | 仅返回带 `tagList` 含 `foo` 的文章 | queryparam 被忽略，返回所有文章 | **行为破坏**（不再过滤） |
| `POST /api/articles` | 请求体字段忽略 | body 含 `tagList: string[]` 写入关联 | body 中 `tagList` 字段被忽略（service 不再读取） | **行为破坏**（标签不持久化） |
| `PUT /api/articles/:slug` | 请求体字段忽略 | body 含 `tagList: string[]` 重建关联 | body 中 `tagList` 字段被忽略 | **行为破坏** |
| `GET /api/articles` | 响应字段删除 | 文章对象含 `tagList: string[]` | 文章对象不含 `tagList` | **破坏性**（调用方读到 `undefined`） |
| `GET /api/articles/:slug` | 响应字段删除 | 同上 | 同上 | **破坏性** |
| `GET /api/articles/feed` | 响应字段删除 | 同上 | 同上 | **破坏性** |
| `POST /api/articles/:slug/favorite` | 不动 | favorites 行为不变 | 不变 | ✅ |
| `DELETE /api/articles/:slug/favorite` | 不动 | favorites 行为不变 | 不变 | ✅ |

- **消费方影响**：依赖 `tagList` 字段或 `/api/tags` 端点的客户端会读到 `undefined` / 404，必须同步更新。favorites 消费方无影响。
- **文档影响**：`docs/swagger.json` 中 `/tags` / `TagsResponse` / `Article.tagList` / `NewArticle.tagList` / `?tag=` queryparam 全部移除；JSON 文件保持合法可解析。

## 8. 设计原则约束

- **简单优先**：仅删 tag 子系统，不引入替代方案；不动 favorites / auth / profile。
- **精准修改**：仅改 6 个文件 + 删 4 个文件（含 schema），不"清理"无关代码。
- **质量底线**：删除范围内必须保持编译通过、`npm test` 通过、`git diff --check` 通过、`impact_validate.py` 通过。
- **语义约定**：未修改 status/enum/常量/错误码/权限名/配置键；`HttpException` 的使用模式保留。

### 行为准则检查

- 任务规模：**大**（6 改 + 4 删；跨 6 个层级；含 schema 不可逆 + 4 文件不可恢复 + API 破坏性）。
- 适用规则：硬规则 #1（逐步确认）、#2（高风险拦截：删旧接口/Controller/路由 + 删文件 without backup 列入高风险，但 git checkout 满足"备份"语义）、#3（DB 只读）、#5（破坏性保护）、#6（阻塞恢复）、#8（Phase 4 输出验证）、#11（Phase 4/5 分步）。
- 精准修改边界：6 改 + 4 删；不动 favorites / auth / profile / package.json / package-lock.json / prisma-client.ts / prisma-mock.ts / 旧 migration 文件。
- 不做的事：不写新 migration、不执行 migrate、不删旧 migration、不引入 logger、不加 fav/follow 副作用、不重构 article.service.ts 中非 tag 部分。
- 语义约定证据：`HttpException` 用法不变；`favorited` / `favoritesCount` / `favoritedBy` 三处契约保留。
- 测试策略依据：基线 `npm test` 已绿；变更后必须保持 4 suites / 26 passed（删 tag.service.test.ts 后 1 todo 消失）；不动 `tests/prisma-mock.ts`。

## 9. 数据迁移策略

- 存量数据如何转换：**不转换**（隔离副本不连真实 DB；真实生产由后续 DBA 窗口处理）。
- 是否需要历史快照：**不需要**（本场景不删真实数据）。
- 迁移脚本位置：**不写**（用户原话禁止执行真实迁移；schema 文件改由本次负责，新 migration 留待真实部署）。

## 10. 向后兼容性评估

- API 变更是否破坏现有消费者：**是**。`/api/tags` → 404；article I/O 少 `tagList` 字段；`?tag=` 不再过滤。
- 兼容方案：**不提供**。用户原话"tags 功能没人用了"明确指向无兼容期；favorites / auth / profile 消费者零影响。

<!-- 其他章节按需展开：本场景无外键/视图/触发器、无索引调整、无缓存策略、无 MQ 事件、无安全/权限变更、无监控/告警配置变更。 -->
