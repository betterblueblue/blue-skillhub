# [D19 node tags removal phase5] 需求文档

> 生成时间：2026-07-04 12:17:33  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：[000-context-pack.md](000-context-pack.md) → **010-requirements.md** → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

> 本文档描述的是**业务需求**——要做什么、为什么、怎么算做完。
> 技术细节（schema 变更方案、代码修改清单、配置项、API 契约、前端改动）属于设计文档范畴，见 `020-design.md`。

## 1. 变更背景

当前的 Conduit 风格博客 API 中存在一套 tags（标签）功能：客户端可以通过一个独立接口拉取热门标签列表，并可在创建/更新文章时附带一个或多个标签，文章详情里也会展示这些标签。业务上确认 tags 功能已经无人使用，标签信息在文章交互、搜索和推荐中均不再发挥作用，UI 也没有再展示标签。

继续保留这套功能会带来三方面成本：一是数据库需要维护一张不再被查询的标签表与文章↔标签的关联表；二是接口和契约里仍要承担标签字段的输入校验、写入与输出映射；三是测试、Swagger 文档和代码中仍有专门的标签相关模块。

本次变更属于功能下线，目的是把"已无人使用"的功能从产品、契约、代码、数据库 schema 和测试里整条链路移除。

## 2. 需求描述

下线整个 tags 功能，包括：

1. 移除获取热门标签的对外接口。
2. 移除与标签相关的持久化模型以及文章与标签的关联。
3. 移除文章接口中所有标签相关字段的输入与输出，包括创建、更新、文章列表、文章详情等场景。
4. 移除按标签过滤文章的能力（标签过滤是 tags 功能的衍生能力，下线后没有意义）。
5. 移除针对 tag service 的测试。
6. 同步更新 OpenAPI/Swagger 文档，删除 tags 相关定义，确保契约与代码一致。
7. 保留并确认不受影响的功能：用户认证、个人资料、文章评论、收藏文章（favorites）以及按作者/收藏者过滤文章等能力必须维持原样。

完成后，业务接口列表中不再包含"获取热门标签"这个动作，文章相关的接口契约里也不再出现标签相关字段；调用方如果仍在使用标签相关能力，会因为接口或字段不存在而收到明确的错误或返回结构变化，从而感知到功能已下线。

## 2.1 当前假设与歧义

- 当前假设：用户希望一次性完整下线 tags 功能，不保留任何形式的灰度或兼容期；其他业务能力（favorites、文章评论、用户系统）保持不变。
- 可能歧义：标签过滤参数本身没有出现在用户原话里，但它的实现依赖已被本次下线的关联关系，保留它要么会让接口永久 422，要么会要求实现一个空操作，无论哪种都属于"半截删除"，应一并清理。
- 更简单的方案：直接把整个 tag 子系统（接口 / 模型 / 关联 / 文章 I/O / 测试 / Swagger）一并移除，没有更省事的中间方案。
- 任务规模：**大**（跨路由、控制器、服务、Prisma schema、Swagger、测试六个层级；包含不可逆的 schema 变更；属于高风险删除）。
- 成功标准（业务视角）：
  - 调用方再也拿不到"获取热门标签"接口的正常响应；
  - 创建/更新/查看文章时不再有标签相关输入字段或输出字段；
  - 按作者、收藏者过滤文章的能力完全保留；
  - 收藏文章（favorite / unfavorite / 收藏数 / 是否已收藏）的能力与原行为一致；
  - 用户认证、个人资料、文章评论的能力完全保留。

## 2.2 模糊点处理清单（模糊需求必填）

| 模糊点（用户原话） | 处理方式 | 结果 |
|-------------------|---------|------|
| "tags 功能没人用了" | 已确认（用户原话"都删掉"） | 全量下线，不留任何 tag 痕迹 |
| "Tag model" | `【代码推断: prisma/schema.prisma:40-44】` — 代码可推断 | Tag model 仅含 id 与 name unique 两个字段，无其他依赖，可整张删除 |
| "文章 tagList 输入/输出" | `【代码推断: src/services/article.service.ts】` — 代码可推断 | tagList 出现在 create / update / getArticles / getFeed / getArticle / favoriteArticle / unfavoriteArticle 的请求体解析、include 与响应映射中，删除范围已锁定 |
| "相关测试引用" | `【代码推断: tests/services/article.service.test.ts】` — 代码可推断 | 仅 favoriteArticle / unfavoriteArticle / deleteComment 测试的 mock payload 出现 `tagList: []` 字段，从 mock 中清理即可 |
| "不执行真实数据库迁移" | 已确认（用户原话） | 隔离副本内只改 schema.prisma，不跑 prisma migrate，不写新 migration；090 写明"未执行迁移的原因" |
| "误删 favorites 是失败信号" | 已确认（用户原话 + 交付矩阵 must_contain） | 收藏相关字段、关系、service、controller、测试全部保留 |
| "package.json 不允许改动" | 已确认（用户原话 + 交付矩阵 forbidden） | 不引入/移除任何 npm 依赖 |

> 用户需求无模糊表述时写"无"。本场景所有待澄清点已通过用户原话确认，不再单列假设条目。

## 2.3 本次做什么、不做什么

- **本次做**：
  - 删除获取热门标签接口及其服务、模型、测试；
  - 移除文章接口中所有标签相关字段的输入、输出与过滤；
  - 移除数据库中标签相关表与文章↔标签关联；
  - 同步更新 API 契约文档；
  - 保持 favorites、评论、认证、个人资料功能完全不变。
- **本次不做**：
  - 不引入新的标签替代方案（如"分类 / 主题"等）；
  - 不修改与 tags 无关的业务功能；
  - 不修改 npm 依赖；
  - 不执行真实数据库迁移；
  - 不删除 `prisma/migrations/` 目录下的旧迁移文件。

## 2.4 非功能需求

- **安全**：tags 接口删除后不再需要鉴权说明；favorites 仍保留现有鉴权要求（必须登录）。
- **可用性**：本次属于破坏性变更，不提供兼容期；调用方需同步更新。
- **数据合规**：删除 schema 不直接删除已存在的标签表行；真实数据库迁移不在本场景内执行（见 2.5 与 090 记录）。
- **可维护性**：删除完成后不应在仓库中留下任何 tag 相关的可编译符号（接口、模型、service、字段、测试）。
- **测试覆盖**：原 `article.service.test.ts` 中 favorites 相关断言必须仍然通过；`tag.service.test.ts` 整体下线。

## 2.5 未确认项

> 代码可推断项已由 Agent 自行查证（见 context-pack §7「已确认事实」），此处只保留业务需决策项。

- [x] 全量下线 tags — 用户原话已确认。
- [x] 不执行真实数据库迁移 — 用户原话已确认。
- [x] 保留 favorites 与认证 / 个人资料 / 评论 — 用户原话 + 交付矩阵 must_contain / forbidden 已确认。
- [x] 旧 Prisma migration 文件是否清理 — 默认不清理（与"不执行真实迁移"一致；旧 migration 反映历史真实状态，由后续维护者按需整理）。

## 3. 业务约束

- 兼容性要求：调用方在使用旧接口或字段时会收到错误或返回结构变化；不承诺兼容期。
- 业务约束：favorites 功能必须保留——这是核心业务能力，已被多个交付矩阵显式列为"必须保留"。
- 时间约束：无。
- 范围约束：本次只在隔离副本（fixture）内进行；不向生产环境或任何共享数据库推送变更。

## 4. 验收标准

- 仓库工作树中不再存在 tag 服务的相关源文件。
- `GET /api/tags` 接口在 routes 中不再被挂载；调用该路径应得到 404 而非原响应。
- `prisma/schema.prisma` 中 `Tag` model 与 `Article.tagList` 关联被移除，且 schema 文件保持合法可被解析。
- `POST /api/articles` / `PUT /api/articles/:slug` 请求体不再接收 `tagList` 字段；`GET /api/articles` / `GET /api/articles/:slug` / `GET /api/articles/feed` 响应不再含 `tagList` 字段。
- `GET /api/articles?tag=...` 的 `tag` queryparam 不再被 service 端读取（参数被忽略不报错即可）。
- `POST/DELETE /api/articles/:slug/favorite` 行为不变；`favorited` / `favoritesCount` 字段在所有 article 响应中保留。
- `docs/swagger.json` 中 `/tags` 路径、`TagsResponse` 定义、`Article.tagList` 与 `NewArticle.tagList` 字段被移除；JSON 本身仍可被合法解析。
- favorites / 认证 / 个人资料 / 评论 4 类功能在 `npm test` 中通过。
- 真实数据库未发生任何迁移（`prisma/migrations/` 目录无新增文件，隔离副本不连库）。

## 5. 依赖关系

- 依赖系统 / 团队：仅本仓库；不依赖外部系统或团队协作。
- 前置条件：
  - `000-context-pack.md` 已写入并经用户确认（已确认 Step 1）。
  - 隔离副本处于 `6ac99ea5ae` HEAD 且 `git status` 干净。
  - 基线 `npm test` 退出码 0（已通过 prep `commands/node-baseline-minimax-m3.txt` 验证）。
