# [D19 node tags removal phase5] 实施文档

> 生成时间：2026-07-04 12:17:33  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：[000-context-pack.md](000-context-pack.md) → [010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → **030-implementation.md** → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 实施顺序

按"删除优先于修改"与"先解引用再删文件"原则排列：

1. **Phase 5 文档**（Step 0）：`_active-state.md`（基础恢复状态文件，非源代码写入，可与文档同步）
2. **Step 1-4（删文件）**：`tag.controller.ts` / `tag.service.ts` / `tag.model.ts` / `tag.service.test.ts` —— 顺序无关，互不依赖
3. **Step 5（routes 解引用）**：`src/routes/routes.ts` 移除 `import tagsController` 与 `.use(tagsController)`（依赖 Step 1-3 已删文件，删除后再解引用保证不再 import 不存在模块）
4. **Step 6（article.controller JSDoc 清理）**：移除 `@queryparam tag` 描述
5. **Step 7（article.service 重构）**：删除 `'tag' in query` 块、`tagList` include×4、`tagList` 响应映射×5、`disconnectArticlesTags` 函数、`tagList` 写入块
6. **Step 8（prisma schema）**：删除 `Tag` model 与 `Article.tagList Tag[]`
7. **Step 9（swagger）**：删除 `/tags` path、`TagsResponse` definition、`Article.tagList` / `NewArticle.tagList` 字段、`?tag=` queryparam
8. **Step 10（article.service.test mock 清理）**：删除 `tagList: []` 字段
9. **Step 11-12（验证）**：`git diff --check` + `npm test` + 全仓残留扫描

> 顺序倒过来回滚同样成立：先恢复 Step 10，再恢复 Step 9...直到 Step 1。

## 2. 前置检查清单

- [x] 分析依据中的待确认问题已处理（010 §2.5 4 项均确认）
- [x] 当前假设、歧义和成功标准已确认（010 §2.1 + §4）
- [x] 精准修改边界已确认（020 §8：6 改 + 4 删；不动 favorites / auth / profile / package.json）
- [x] status/enum/常量/错误码/权限名/配置键等语义约定已找到原定义（`HttpException` 用法不变；favorites 字段保留原状）
- [x] 依赖服务状态确认：隔离副本不连真实 DB（用户原话 + 准备记录 README）
- [x] 数据库备份状态确认：仅 schema 文件改动；旧 migration 保留；真实 DB 未触碰
- [x] 锁策略/停机窗口确认：不适用（本场景不执行真实迁移）
- [x] 回滚方案准备完毕（每步独立 `git checkout HEAD -- <path>`）
- [x] `_active-state.md` 已创建或将在 Step 0 首次写入（随后与 Step 0 一并写）
- [x] 破坏性操作已单独确认（4 个文件删除 + API 破坏性 + schema 不可逆，每个独立 `确认 Step N`）

## 2.1 改动完整性自检（提交确认前必做）

| 验收标准（来自 010） | 对应 Step | 覆盖状态 |
|---------------------|----------|---------|
| 仓库工作树中不再存在 tag 服务的相关源文件 | Step 1-4 | ✅ 4 文件全部 `git rm` |
| `GET /api/tags` 不再被挂载 | Step 1（删 controller） + Step 5（routes 解引用） | ✅ |
| `prisma/schema.prisma` 中 `Tag` model 与 `Article.tagList` 被移除 | Step 8 | ✅ |
| `POST/PUT /api/articles` 不再接收 `tagList` 字段 | Step 7（service 删除 tagList 写入） | ✅ |
| `GET /api/articles*` 响应不再含 `tagList` 字段 | Step 7（删除 tagList 响应映射×5） | ✅ |
| `?tag=` queryparam 不再被 service 端读取 | Step 7（删除 `'tag' in query` 块） | ✅ |
| `POST/DELETE /articles/:slug/favorite` 行为不变 | 不动 | ✅ |
| `favorited` / `favoritesCount` / `favoritedBy` 字段保留 | 不动 | ✅ |
| `docs/swagger.json` 中 `/tags` / `TagsResponse` / `tagList` 被移除；JSON 合法 | Step 9 | ✅ |
| `npm test` 退出码 0；favorites / 认证 / 个人资料 / 评论 通过 | Step 11-12 | ✅ |
| 真实 DB 未发生任何迁移（`prisma migrations/` 目录无新增） | 整场景不 migrate | ✅ |

> 11/11 验收点全部覆盖。

## 3. 执行步骤

### Step 0: 写入 `_active-state.md`（基础恢复状态文件，非源代码写入）

- **维度**：Phase 5 基础设施
- **文件**：`change-impact/node-tags-removal-phase5/_active-state.md`
- **风格约束**：N/A（文档）
- **操作**：
  ```text
  Write change-impact/node-tags-removal-phase5/_active-state.md
  ```
- **影响范围**：仅本需求目录
- **回滚方式**：`rm change-impact/node-tags-removal-phase5/_active-state.md`
- **语义约定**：N/A
- **验证方式**：`ls` 确认文件存在
- **确认类型**：写文件（基础设施，与 Phase 4 文档同类；不修改源码）

### Step 1: 删除 `src/controllers/tag.controller.ts`

- **维度**：删除文件
- **文件**：`src/controllers/tag.controller.ts`
- **风格约束**：N/A（删除）
- **操作**：
  ```bash
  git rm src/controllers/tag.controller.ts
  ```
- **影响范围**：`/api/tags` 调用方得 404；`tag.controller` 引用方（routes.ts）需同步解引用（Step 5）
- **回滚方式**：`git checkout HEAD -- src/controllers/tag.controller.ts`
- **语义约定**：N/A
- **验证方式**：`ls src/controllers/` 确认无该文件；`npm test` 编译通过（依赖 Step 5）
- **确认类型**：删除文件（git rm 满足"可恢复"语义）

### Step 2: 删除 `src/services/tag.service.ts`

- **维度**：删除文件
- **文件**：`src/services/tag.service.ts`
- **风格约束**：N/A（删除）
- **操作**：
  ```bash
  git rm src/services/tag.service.ts
  ```
- **影响范围**：与 Step 1 同链路；`getTags` 不再可用
- **回滚方式**：`git checkout HEAD -- src/services/tag.service.ts`
- **验证方式**：`ls src/services/` 确认无该文件
- **确认类型**：删除文件

### Step 3: 删除 `src/models/tag.model.ts`

- **维度**：删除文件
- **文件**：`src/models/tag.model.ts`
- **风格约束**：N/A（删除）
- **操作**：
  ```bash
  git rm src/models/tag.model.ts
  ```
- **影响范围**：`Tag` interface 不再可用；视觉确认无其他文件 import 该 interface
- **回滚方式**：`git checkout HEAD -- src/models/tag.model.ts`
- **验证方式**：`ls src/models/` 确认无该文件
- **确认类型**：删除文件

### Step 4: 删除 `tests/services/tag.service.test.ts`

- **维度**：删除文件
- **文件**：`tests/services/tag.service.test.ts`
- **风格约束**：N/A（删除）
- **操作**：
  ```bash
  git rm tests/services/tag.service.test.ts
  ```
- **影响范围**：测试套件 5 → 4；`1 todo` 消失
- **回滚方式**：`git checkout HEAD -- tests/services/tag.service.test.ts`
- **验证方式**：`ls tests/services/` 确认无该文件
- **确认类型**：删除文件

### Step 5: 修改 `src/routes/routes.ts`（解引用 tag controller）

- **维度**：修改代码
- **文件**：`src/routes/routes.ts`
- **风格约束**：2 空格缩进；行尾 LF（D19R1 经验：CRLF 会被 `git diff --check` 拦下）
- **操作**：
  ```typescript
  // 当前（L2-3）：
  import tagsController from '../controllers/tag.controller';
  import articlesController from '../controllers/article.controller';
  import authController from '../controllers/auth.controller';
  import profileController from '../controllers/profile.controller';
  
  const api = Router()
    .use(tagsController)
    .use(articlesController)
    .use(profileController)
    .use(authController);
  
  // 目标：
  import articlesController from '../controllers/article.controller';
  import authController from '../controllers/auth.controller';
  import profileController from '../controllers/profile.controller';
  
  const api = Router()
    .use(articlesController)
    .use(profileController)
    .use(authController);
  ```
- **影响范围**：编译必须通过（依赖 Step 1 已删文件）；运行链缩短
- **回滚方式**：`git checkout HEAD -- src/routes/routes.ts`
- **语义约定**：N/A
- **验证方式**：`npm test` 编译通过（隐含 `tsc`）；`npx tsc --noEmit` 显式编译
- **确认类型**：改代码

### Step 6: 修改 `src/controllers/article.controller.ts`（清理 JSDoc）

- **维度**：修改代码（JSDoc）
- **文件**：`src/controllers/article.controller.ts:25`
- **风格约束**：保持 JSDoc 风格不变
- **操作**：
  ```diff
   * @queryparam offset number of articles dismissed from the first one
   * @queryparam limit number of articles returned
  - * @queryparam tag
   * @queryparam author
  ```
- **影响范围**：运行时不变；仅 Swagger-style 注释
- **回滚方式**：`git checkout HEAD -- src/controllers/article.controller.ts`
- **验证方式**：`grep -n "tag" src/controllers/article.controller.ts` 不命中
- **确认类型**：改代码

### Step 7: 修改 `src/services/article.service.ts`（核心重构）

- **维度**：修改代码
- **文件**：`src/services/article.service.ts`
- **风格约束**：2 空格缩进；named export；行尾 LF
- **操作**（多块删除）：
  ```diff
  --- a/src/services/article.service.ts
  +++ b/src/services/article.service.ts
  @@ buildFindAllQuery @@
     queries.push(authorQuery);
  
  -  if ('tag' in query) {
  -    queries.push({
  -      tagList: {
  -        some: {
  -          name: query.tag,
  -        },
  -      },
  -    });
  -  }
  -
     if ('favorited' in query) {
  
  @@ getArticles include / map @@
       include: {
  -      tagList: {
  -        select: {
  -          name: true,
  -        },
  -      },
         author: { ... },
         favoritedBy: true,
         _count: { ... },
       },
     });
  
     return {
       articles: articles.map(({ authorId, id, _count, favoritedBy, ...article }) => ({
         ...article,
         author: profileMapper(article.author, username),
  -      tagList: article.tagList.map(tag => tag.name),
         favoritesCount: _count?.favoritedBy,
         favorited: favoritedBy.some(item => item.username === username),
       })),
       articlesCount,
     };
  
  @@ getFeed include / map @@   （同上 include 与 map 块）
  
  @@ createArticle @@
  -  const { title, description, body, tagList } = article;
  +  const { title, description, body } = article;
  
     // ... 校验不变 ...
  
     const { authorId, id, ...createdArticle } = await prisma.article.create({
       data: {
         title, description, body, slug,
  -      tagList: { connectOrCreate: tagList.map(...) },
         author: { connect: { id: user?.id } },
       },
       include: {
  -      tagList: { select: { name: true } },
         author: { ... },
         favoritedBy: true,
         _count: { ... },
       },
     });
  
     return {
       ...createdArticle,
  -    tagList: createdArticle.tagList.map(tag => tag.name),
       favoritesCount: createdArticle._count?.favoritedBy,
       favorited: createdArticle.favoritedBy.some(item => item.username === username),
     };
  
  @@ getArticle include / return @@
       include: {
  -      tagList: { select: { name: true } },
         author: { ... },
         favoritedBy: true,
         _count: { ... },
       },
     });
  
     return {
       ...
  -    tagList: article?.tagList.map(tag => tag.name),
       favoritesCount: article?._count?.favoritedBy,
       ...
     };
  
  @@ disconnectArticlesTags 函数（删除整个函数定义，294-305）@@
  -const disconnectArticlesTags = async (slug: string) => { ... };
  
  @@ updateArticle @@
  -  const tagList = article.tagList?.length
  -    ? article.tagList.map((tag: string) => ({ create: { name: tag }, where: { name: tag } }))
  -    : [];
  -
  -  await disconnectArticlesTags(slug);
  -
     const updatedArticle = await prisma.article.update({
       data: {
         ...(article.title ? { title: article.title } : {}),
         ...(article.body ? { body: article.body } : {}),
         ...(article.description ? { description: article.description } : {}),
         ...(newSlug ? { slug: newSlug } : {}),
         updatedAt: new Date(),
  -      tagList: { connectOrCreate: tagList },
       },
       include: {
  -      tagList: { select: { name: true } },
         author: { ... },
         favoritedBy: true,
         _count: { ... },
       },
     });
  
     return {
       ...
  -    tagList: updatedArticle?.tagList.map(tag => tag.name),
       favoritesCount: updatedArticle?._count?.favoritedBy,
       ...
     };
  
  @@ favoriteArticle / unfavoriteArticle include / return @@
       include: {
  -      tagList: { select: { name: true } },
         author: { ... },
         favoritedBy: true,
         _count: { ... },
       },
     });
  
     const result = {
       ...article,
       author: profileMapper(article.author, usernameAuth),
  -    tagList: article?.tagList.map(tag => tag.name),
       favorited: article.favoritedBy.some(...),
       favoritesCount: _count?.favoritedBy,
     };
  ```
- **影响范围**：favorites 链路完全独立保留；article 响应少 `tagList` 字段；`?tag=` queryparam 静默忽略
- **回滚方式**：`git checkout HEAD -- src/services/article.service.ts`
- **语义约定**：`HttpException` 用法不变；`favorited` / `favoritesCount` / `favoritedBy` 保留
- **验证方式**：`npm test` 编译通过 + 测试通过；`grep -n "tagList\|disconnectArticlesTags" src/services/article.service.ts` 0 命中
- **确认类型**：改代码

### Step 8: 修改 `prisma/schema.prisma`（删除 Tag model + Article.tagList）

- **维度**：DDL 等效（schema 文件）
- **文件**：`prisma/schema.prisma`
- **风格约束**：2 空格缩进；Prisma 语法
- **操作**：
  ```diff
  model Article {
    ...
    updatedAt   DateTime  @default(now())
  -  tagList     Tag[]
    author      User      @relation("UserArticles", fields: [authorId], references: [id], onDelete: Cascade)
    ...
  }
  
  -model Tag {
  -  id       Int       @id @default(autoincrement())
  -  name     String    @unique
  -  articles Article[]
  -}
  -
  model User {
    ...
  }
  ```
- **影响范围**：schema 不可逆 + 等同 ALTER TABLE（高风险）；不执行真实 migrate；隔离副本不连 DB
- **回滚方式**：`git checkout HEAD -- prisma/schema.prisma`
- **语义约定**：N/A
- **验证方式**：`grep -n "model Tag\|tagList" prisma/schema.prisma` 0 命中；schema 文件结构合法（语法）
- **确认类型**：DDL 等效（schema 文件改动命中硬规则 #2，单独确认）

### Step 9: 修改 `docs/swagger.json`（API 契约清理）

- **维度**：API 契约
- **文件**：`docs/swagger.json`
- **风格约束**：JSON 合法；缩进保留
- **操作**：
  ```diff
  --- a/docs/swagger.json
  +++ b/docs/swagger.json
  @@ GET /articles queryparam @@
  -          { "name": "tag", ... },
  
  @@ /tags path（738-757）@@
  -  "/tags": {
  -    "get": {
  -      "summary": "Get tags",
  -      ...
  -    }
  -  },
  
  @@ Article definition tagList 字段（908-913）@@
  -        "tagList": { ... },
  
  @@ NewArticle 或 article response 引用（937, 981-986）@@
  -        "tagList",
  
  @@ TagsResponse definition（1084-1095）@@
  -  "TagsResponse": {
  -    ...
  -  },
  ```
- **影响范围**：API 文档与代码一致；JSON 仍可被解析
- **回滚方式**：`git checkout HEAD -- docs/swagger.json`
- **语义约定**：N/A
- **验证方式**：`python -c "import json; json.load(open('docs/swagger.json'))"` 成功；`grep -n "TagsResponse\|/tags" docs/swagger.json` 0 命中
- **确认类型**：改配置（API 契约文档）

### Step 10: 修改 `tests/services/article.service.test.ts`（mock 清理）

- **维度**：测试修复
- **文件**：`tests/services/article.service.test.ts`
- **风格约束**：Jest describe/test 块；`mockDeep<PrismaClient>()` 不变
- **操作**：
  ```diff
  @@ favoriteArticle mockedArticleResponse @@
  -        tagList: [],
         favoritedBy: [],
  
  @@ unfavoriteArticle mockedArticleResponse @@
  -        tagList: [],
         favoritedBy: [],
  ```
- **影响范围**：测试 mock 与新 service 契约一致
- **回滚方式**：`git checkout HEAD -- tests/services/article.service.test.ts`
- **语义约定**：N/A
- **验证方式**：`grep -n "tagList" tests/services/article.service.test.ts` 0 命中；`npm test` 通过
- **确认类型**：测试修复

### Step 11: 运行 `git diff --check`

- **维度**：V1 静态验证
- **文件**：N/A（命令）
- **操作**：
  ```bash
  git diff --check
  ```
- **验证等级**：V1
- **预期结果**：退出码 0；无输出
- **失败处理**：若 exit 2（trailing whitespace），按 D19R1 经验用 Python binary 模式 `b'\r\n' → b'\n'` 全替换

### Step 12: 运行 `npm test`

- **维度**：V2 测试
- **文件**：N/A（命令）
- **操作**：
  ```bash
  npm test
  ```
- **验证等级**：V2
- **预期结果**：4 suites passed / 26 passed / exit 0（与基线相比：5 suites → 4 suites 因 Step 4 删 tag.service.test.ts；1 todo → 0 todo）
- **失败处理**：先读失败信息；若为 `tsc` 编译错则补源码；若为 mock 字段错则补测试；不裸写通过

### Step 13: 全仓残留扫描（7 tokens，限定 src/ tests/ prisma/ docs/）

- **维度**：V1 静态验证
- **操作**：
  ```bash
  for token in tagList tag.controller tag.service getTags "/tags" TagsResponse "model Tag"; do
    echo "--- Token: $token ---"
    git grep -n "$token" -- "src/" "tests/" "prisma/" "docs/"
    echo "Exit: $?"
  done
  ```
- **预期结果**：7 个 token 全部 0 命中（git grep exit 1）

### Step 14: favorites 链路保留扫描（4 tokens）

- **维度**：V1 静态验证
- **操作**：
  ```bash
  for token in favoriteArticle favoritesCount favoritedBy "favoriteArticle\|unfavoriteArticle"; do
    echo "--- Token: $token ---"
    git grep -n "$token" -- "src/" "tests/" "prisma/" "docs/"
    echo "Exit: $?"
  done
  ```
- **预期结果**：4 个 token 均有命中（favorited 41 处、favoritesCount 10 处、favoritedBy 27 处、favoriteArticle 11 处；按 D19R1 实测）

## 3.2 API 方法验证（⚠️ 强制必做）

> 本次变更**仅删除代码**，不新增任何业务方法。
> 仅删除以下 3 个文件中的 5 个方法（含内部辅助函数）；下方为影响范围表。

| 方法名 | 来源文件 | grep 验证 | 异常行为 | 验证标注 |
|--------|---------|----------|---------|---------|
| `getTags` | `src/services/tag.service.ts:35` (export default) | ✅ 存在 `【已核实: tag.service.ts:35】` | 抛 Prisma 错误时由 `tag.controller.ts:18` `next(error)` 提交中间件 | 随 Step 2 删除 |
| `disconnectArticlesTags` | `src/services/article.service.ts:294` (内部辅助) | ✅ 存在 `【已核实: article.service.ts:294】` | 静默（无 throw） | 随 Step 7 删除 |
| `tagList`（Prisma relation 字段） | `prisma/schema.prisma:22` | ✅ 存在 `【已核实: schema.prisma:22】` | Prisma client 编译期检查；删除后 `prisma.article.*` 的 include/connect 不再含 `tagList` | 随 Step 8 删除 |
| `getTags`（controller 引用） | `src/controllers/tag.controller.ts:15` | ✅ 存在 `【已核实: tag.controller.ts:15】` | 同 service | 随 Step 1 删除 |
| `TagsResponse`（swagger definition） | `docs/swagger.json:1084` | ✅ 存在 `【已核实: swagger.json:1084】` | JSON schema definition；删除后 OpenAPI 不再暴露 | 随 Step 9 删除 |

> **保留方法验证**（不应被误删）：

| 方法名 | 来源文件 | grep 验证 | 异常行为 | 验证标注 |
|--------|---------|----------|---------|---------|
| `favoriteArticle` | `src/services/article.service.ts:525` | ✅ 存在 `【已核实: article.service.ts:525】` | 抛 `HttpException` 当 article 不存在 | 保留（不动） |
| `unfavoriteArticle` | `src/services/article.service.ts:573` | ✅ 存在 `【已核实: article.service.ts:573】` | 抛 `HttpException` 当 article 不存在 | 保留（不动） |
| `prisma.article.update` | Prisma Client | ✅ 通过 `prisma/prisma-client.ts` 单例调用 | 记录不存在抛 P2025 | 保留 |
| `prisma.article.findMany` / `findUnique` / `create` / `delete` | Prisma Client | ✅ 同上 | 同上 | 保留 |
| `prisma.user.findUnique` | Prisma Client | ✅ 在 favorite/unfavorite/findUserIdByUsername 中调用 | null 时后续 `user?.id` undefined 保护 | 保留 |
| `HttpException` | `src/models/http-exception.model.ts` | ✅ 存在 `【已核实: http-exception.model.ts】` | 构造时不抛；status/body 透传给 Express 错误中间件 | 保留 |
| `auth.optional` / `auth.required` | `src/utils/auth.ts` | ✅ 存在 `【已核实: utils/auth.ts】` | 用户未登录时 req.user undefined / 401 | 保留 |
| `findUserIdByUsername` | `src/services/auth.service.ts` | ✅ 存在（service 间 import） | 返回 `user?.id` | 保留 |
| `profileMapper` | `src/utils/profile.utils.ts` | ✅ 存在 `【已核实: utils/profile.utils.ts】` | 静默 | 保留 |

## 4. 回滚方案

### 逐步骤回滚

| Step | 回滚命令 |
|------|----------|
| Step 0 | `rm change-impact/node-tags-removal-phase5/_active-state.md` |
| Step 1 | `git checkout HEAD -- src/controllers/tag.controller.ts` |
| Step 2 | `git checkout HEAD -- src/services/tag.service.ts` |
| Step 3 | `git checkout HEAD -- src/models/tag.model.ts` |
| Step 4 | `git checkout HEAD -- tests/services/tag.service.test.ts` |
| Step 5 | `git checkout HEAD -- src/routes/routes.ts` |
| Step 6 | `git checkout HEAD -- src/controllers/article.controller.ts` |
| Step 7 | `git checkout HEAD -- src/services/article.service.ts` |
| Step 8 | `git checkout HEAD -- prisma/schema.prisma` |
| Step 9 | `git checkout HEAD -- docs/swagger.json` |
| Step 10 | `git checkout HEAD -- tests/services/article.service.test.ts` |
| Step 11-14 | 命令级；无文件状态可回滚；重跑即可 |

### 组合回滚顺序

```
全部成功想回滚：
  倒序执行逐步骤回滚（Step 14 → Step 13 → ... → Step 1 → Step 0）
  
Step 7 失败（service 重构未完成）：
  1. git checkout HEAD -- src/services/article.service.ts
  2. Step 8-14 不执行（依赖 Step 7）
  
Step 8 失败（schema 改了一半）：
  1. git checkout HEAD -- prisma/schema.prisma
  2. Step 7 需补完（service 不再 include tagList，但 schema 还有 tagList → 编译错）
  
Step 1-4 顺序无关（删除 4 个文件互不依赖）：
  任意一个失败 → 仅回滚那一个 + Step 5 同步重做
```
