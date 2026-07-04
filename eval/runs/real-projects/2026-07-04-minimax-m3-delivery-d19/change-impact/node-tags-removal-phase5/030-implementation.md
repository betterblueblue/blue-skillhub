# [D19 node tags removal phase5] 实施文档

> 生成时间：2026-07-04 09:57:07  |  版本：1.0  |  生成者：impact + MiniMax-M3
>
> 导航：[010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → **030-implementation.md** → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 实施顺序

按"低风险先、高风险后；删除先、改写后"的顺序执行：

1. **Step 4–7（整文件删除）**：先删 4 个仅服务 tag 的文件（`tag.controller.ts` / `tag.service.ts` / `tag.model.ts` / `tag.service.test.ts`）。这 4 个文件无外部 import 引用（除 `routes.ts` 的 `tagsController` 外，下一步才解引用）。
2. **Step 8（routes 解引用）**：`src/routes/routes.ts` 移除对已删 controller 的 import 与 `.use`。
3. **Step 9（article.controller 注释）**：`src/controllers/article.controller.ts` 清理 JSDoc。
4. **Step 10（article.service 改写）**：`src/services/article.service.ts` 是改动面最大的一步，移除 `'tag' in query` 块、所有 `tagList` include、create/update 的 `tagList` 写入、`disconnectArticlesTags` helper、所有响应 `tagList` 映射；保留 favorites 链路。
5. **Step 11（Prisma schema）**：`prisma/schema.prisma` 移除 `Tag` model 与 `Article.tagList Tag[]` 关系。
6. **Step 12（Swagger 契约）**：`docs/swagger.json` 移除 `/tags`、`TagsResponse`、`tag` queryparam、`Article.tagList`、`NewArticle.tagList`。
7. **Step 13（测试 mock 清理）**：`tests/services/article.service.test.ts` 移除 favorite / unfavorite mock 的 `tagList: []` 字段。
8. **Step 14（验证）**：运行 `git diff --check`、`npm test`、`python impact_validate.py` 三个门禁。

每个 Step 单独请求 `确认 Step N`；不合并写文件操作。

## 2. 前置检查清单

- [x] 分析依据中的待确认问题已处理：用户原话已对齐"全量下线 / 不执行真实迁移 / 保留 favorites / 禁改 auth/profile/package"，无需额外确认。
- [x] 当前假设、歧义和成功标准已确认：见 010-requirements.md §2.1 与 020-design.md §1。
- [x] 精准修改边界已确认：见 020-design.md §3 与 §8；仅限 10 个目标文件，不做无关重构/格式化。
- [x] status/enum/常量/错误码/权限名/配置键等语义约定：本次不命中任何此类约定（删除功能不修改 status、enum、错误码、权限名、配置键），无需查找原定义。
- [x] 依赖服务状态：不涉及（删除功能，无新增外部依赖）。
- [x] 数据库备份状态：本次不执行真实迁移；`prisma/migrations/` 旧文件保留；隔离副本无需备份。
- [x] 锁策略/停机窗口：不涉及（无 DB / 批量任务）。
- [x] 回滚方案：Git 工作树（HEAD `6ac99ea`），每步 Step 独立可回滚（`git checkout -- <path>` / `git restore`）。
- [x] `_active-state.md` 已创建：在 Step 1 首次写入需求目录时同步创建。
- [x] 破坏性操作已单独确认：4 个文件删除 + Prisma schema 删除 Tag 关系 命中"删旧接口 / 删旧 Controller 类 / 删除文件且无备份 / 编辑 ORM schema 文件"等高风险清单，每步 Step 单独请求 `确认 Step N`。

## 2.1 改动完整性自检（提交确认前必做）

> 对照 `010-requirements.md` 的验收标准，逐条确认每个验收点都有对应的实施 Step。缺失任一验收点对应的 Step = 实施不完整，不得提交确认。

| 验收标准（来自 010 §4） | 对应 Step | 覆盖状态 |
|---------------------|----------|---------|
| tag 服务相关源文件从工作树移除 | Step 4–7 | ✅ 覆盖（4 个文件删除） |
| 文章接口请求/响应不再含 tagList | Step 10（service）+ Step 9（controller JSDoc）+ Step 12（swagger）+ Step 13（test mock） | ✅ 覆盖 |
| `tag` queryparam 在接口契约中不再存在 | Step 10（service 移除 `'tag' in query` 块）+ Step 12（swagger 移除 `tag` queryparam） | ✅ 覆盖 |
| OpenAPI 文档中 tags 相关定义/路径/字段已清理 | Step 12 | ✅ 覆盖 |
| 数据库 schema 不再含 Tag model 与文章↔标签关联 | Step 11 | ✅ 覆盖 |
| 测试套件全部通过，套件/用例数与基线一致 | Step 14（跑 `npm test`） | ✅ 覆盖 |
| favorites 字段/行为/关系/测试未被误删 | Step 4–13 中显式标注"不动 favorites 链路"；Step 14 通过 `git diff` 与 `npm test` 验证 | ✅ 覆盖 |
| 真实数据库迁移未被执行 | Step 11 仅改 schema，不生成新 migration；090 写明原因 | ✅ 覆盖 |
| 删除过程在执行记录中可追溯 | Step 1–14 每步同步 090 + _active-state | ✅ 覆盖 |

无 ❌ 缺失项。

## 3. 执行步骤

> 每个 Step 的"操作"段列出具体代码片段或文件级删除；每个 Step 单独请求 `确认 Step N`，不合并。

### Step 1: 写入 Phase 4 full 文档（000/010/020/030 + _active-state）

- **维度**：影响分析（Phase 4）
- **文件**：
  - `change-impact/node-tags-removal-phase5/000-context-pack.md`（新建）
  - `change-impact/node-tags-removal-phase5/010-requirements.md`（新建）
  - `change-impact/node-tags-removal-phase5/020-design.md`（新建）
  - `change-impact/node-tags-removal-phase5/030-implementation.md`（新建，即本文件）
  - `change-impact/node-tags-removal-phase5/_active-state.md`（新建）
- **风格约束**：按 `templates/*.md` 章节结构；行号引用统一 `path:line` 格式；证据标 `【已核实: path:line】`。
- **操作**：依次 Write 上述 5 个文件。
- **影响范围**：仅 `change-impact/node-tags-removal-phase5/` 目录；不动任何源码。
- **回滚方式**：删除整个 `change-impact/node-tags-removal-phase5/` 目录（`rm -rf change-impact/node-tags-removal-phase5`，本项目为 Git 工作树，可 `git clean -fd change-impact/`）。
- **语义约定**：不涉及。
- **验证方式**：Step 2 跑 `python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py change-impact/node-tags-removal-phase5 --mode full --repo-root .` 必须退出码 0。
- **确认类型**：写文件（5 个新建文件，全部位于 change-impact 目录）。

### Step 2: 跑 impact_validate.py

- **维度**：Phase 4 验证（强制，不可跳过）
- **文件**：`scripts/impact_validate.py`（只读检查）
- **风格约束**：不适用。
- **操作**：
  ```bash
  python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py \
    change-impact/node-tags-removal-phase5 \
    --mode full \
    --repo-root .
  ```
- **影响范围**：无（只读检查）。
- **回滚方式**：N/A。
- **语义约定**：不涉及。
- **验证方式**：脚本退出码 0；输出 `SUMMARY: X passed, 0 failed, Y warnings`。
- **确认类型**：只读分析（无需 `确认 Step N`，但必须把结果写入 `_active-state.md` 的「最近验证」节后再继续）。

### Step 3: 写入 060-preflight.md

- **维度**：执行前检查（Phase 5 入口）
- **文件**：`change-impact/node-tags-removal-phase5/060-preflight.md`（新建）
- **风格约束**：按 `templates/060-preflight.md` 章节结构。
- **操作**：Write。
- **影响范围**：仅 change-impact 目录。
- **回滚方式**：删除该文件。
- **语义约定**：不涉及。
- **验证方式**：人工对照 P0/P1 列表逐项确认；后续 Step 4+ 的写操作必须满足 060-preflight 列出的写入目标边界与回滚方式。
- **确认类型**：写文件。

### Step 4: 删除 `src/controllers/tag.controller.ts`

- **维度**：源码删除（高风险：删旧 Controller）
- **文件**：`src/controllers/tag.controller.ts`
- **风格约束**：N/A（删除文件）。
- **操作**：
  ```bash
  git rm src/controllers/tag.controller.ts
  ```
  等价于 `rm src/controllers/tag.controller.ts`（在 Git 仓库中 `git rm` 会被记录为"已暂存删除"）。
- **影响范围**：仅该文件被删除；该文件在仓库内仅被 `src/routes/routes.ts:2` import（下一步才解引用），无其他引用（grep `tag.controller` 全仓仅 1 处 import + 1 处 `.use`，均在 routes.ts）。
- **回滚方式**：`git checkout HEAD -- src/controllers/tag.controller.ts`（从 HEAD 恢复）或 `git restore --staged --worktree src/controllers/tag.controller.ts`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 跑 `npm test`（应保持基线 5/26/1）+ `git diff --check` + 内容残留 grep（`tag.controller` 在仓库中应只剩 routes.ts 已删的引用消失）。
- **确认类型**：删除文件（命中"删旧 Controller 类 / 删除文件且无备份"高风险清单，必须单独确认）。
- **高风险命中条目**：删旧接口 / Controller 类（`src/controllers/tag.controller.ts` 整个文件仅做 `/tags` 路由）；删除文件且无备份（但仓库为 Git，可 `git checkout` 回滚，回滚手段就位）。

### Step 5: 删除 `src/services/tag.service.ts`

- **维度**：源码删除（高风险：删旧 Service）
- **文件**：`src/services/tag.service.ts`
- **风格约束**：N/A（删除文件）。
- **操作**：
  ```bash
  git rm src/services/tag.service.ts
  ```
- **影响范围**：该文件在仓库内仅被 `src/controllers/tag.controller.ts:3` import（Step 4 已删），无其他引用（grep `tag.service` 在仓库内仅此 1 处 import）。
- **回滚方式**：`git checkout HEAD -- src/services/tag.service.ts`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 跑 `npm test` + 内容残留 grep。
- **确认类型**：删除文件（命中"删除文件且无备份"高风险清单）。
- **高风险命中条目**：删除文件且无备份（Git 可回滚）。

### Step 6: 删除 `src/models/tag.model.ts`

- **维度**：源码删除（高风险：删旧 Model）
- **文件**：`src/models/tag.model.ts`
- **风格约束**：N/A（删除文件）。
- **操作**：
  ```bash
  git rm src/models/tag.model.ts
  ```
- **影响范围**：该文件在仓库内未被任何文件 import（grep `from '../models/tag.model'` / `from './tag.model'` / `from '../../src/models/tag.model'` 全无命中），独立删除即可。
- **回滚方式**：`git checkout HEAD -- src/models/tag.model.ts`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 跑 `npm test` + 内容残留 grep（`model Tag` 在代码中应不再出现；Prisma schema 中 `model Tag` 由 Step 11 移除）。
- **确认类型**：删除文件。
- **高风险命中条目**：删除文件且无备份（Git 可回滚）。

### Step 7: 删除 `tests/services/tag.service.test.ts`

- **维度**：测试删除（高风险：删除测试文件）
- **文件**：`tests/services/tag.service.test.ts`
- **风格约束**：N/A（删除文件）。
- **操作**：
  ```bash
  git rm tests/services/tag.service.test.ts
  ```
- **影响范围**：该文件仅包含 1 个 `test.todo` stub（`tests/services/tag.service.test.ts:4`），无实质断言；删除后测试套件由 5 suites → 4 suites（但**用例数从 27 降至 26**，因为那个 `test.todo` 占了 1 个 todo 计数）。`npm test` 仍应通过。
- **回滚方式**：`git checkout HEAD -- tests/services/tag.service.test.ts`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 跑 `npm test`，预期 suites 5→4、tests 27→26（1 todo → 0 todo）；用户原话"必改/必删"包含此文件，符合预期。
- **确认类型**：删除文件。
- **高风险命中条目**：删除文件且无备份（Git 可回滚）。
- **基线偏差说明**：用户给的基线是"5 suites / 26 passed / 1 todo"，删除本文件后基线预期调整为"4 suites / 26 passed / 0 todo"——090 写明此偏差与原因。

### Step 8: 修改 `src/routes/routes.ts`（解引用 tag controller）

- **维度**：源码修改
- **文件**：`src/routes/routes.ts`
- **风格约束**：保持现有 `.use(...)` chain 风格；删除对应行。
- **操作**：
  ```typescript
  // 修改前
  import { Router } from 'express';
  import tagsController from '../controllers/tag.controller';
  import articlesController from '../controllers/article.controller';
  import authController from '../controllers/auth.controller';
  import profileController from '../controllers/profile.controller';

  const api = Router()
    .use(tagsController)
    .use(articlesController)
    .use(profileController)
    .use(authController);

  export default Router().use('/api', api);

  // 修改后
  import { Router } from 'express';
  import articlesController from '../controllers/article.controller';
  import authController from '../controllers/auth.controller';
  import profileController from '../controllers/profile.controller';

  const api = Router()
    .use(articlesController)
    .use(profileController)
    .use(authController);

  export default Router().use('/api', api);
  ```
- **影响范围**：`/api/tags` 路由在 Express chain 中消失；其他 3 个 chain 顺序不变。
- **回滚方式**：`git checkout HEAD -- src/routes/routes.ts`。
- **语义约定**：不涉及。
- **验证方式**：`npm test` 仍通过（Step 4 已删 controller，routes.ts 不再 import 时路由自然不存在）；grep `tag.controller` 在仓库中应仅剩 `change-impact/*` 文档。
- **确认类型**：改代码（移除 import + 移除 chain 行）。

### Step 9: 修改 `src/controllers/article.controller.ts`（清理 JSDoc）

- **维度**：源码修改（注释清理）
- **文件**：`src/controllers/article.controller.ts`
- **风格约束**：保持 JSDoc `* @...` 风格。
- **操作**：
  ```typescript
  // 第 25 行附近的 JSDoc：移除 `@queryparam tag` 与 `@bodyparam tagList list of tags` 两行
  // 修改前
  /**
   * Get paginated articles
   * @auth optional
   * @route {GET} /articles
   * @queryparam offset number of articles dismissed from the first one
   * @queryparam limit number of articles returned
   * @queryparam tag
   * @queryparam author
   * @queryparam favorited
   * @returns articles: list of articles
   */

  // 修改后
  /**
   * Get paginated articles
   * @auth optional
   * @route {GET} /articles
   * @queryparam offset number of articles dismissed from the first one
   * @queryparam limit number of articles returned
   * @queryparam author
   * @queryparam favorited
   * @returns articles: list of articles
   */

  // 第 68 行附近的 JSDoc：移除 `@bodyparam tagList list of tags`
  // 修改前
  /**
   * Create article
   * @route {POST} /articles
   * @bodyparam  title
   * @bodyparam  description
   * @bodyparam  body
   * @bodyparam  tagList list of tags
   * @returns article created article
   */

  // 修改后
  /**
   * Create article
   * @route {POST} /articles
   * @bodyparam  title
   * @bodyparam  description
   * @bodyparam  body
   * @returns article created article
   */
  ```
- **影响范围**：仅注释变更；不影响运行时行为（service 端 Step 10 才真正移除 tag 过滤）。handler 端 `req.query` 仍可携带 `tag` 但被忽略；`req.body.article.tagList` 仍可携带但被忽略。
- **回滚方式**：`git checkout HEAD -- src/controllers/article.controller.ts`。
- **语义约定**：不涉及。
- **验证方式**：`npm test` 仍通过。
- **确认类型**：改代码（仅注释）。

### Step 10: 修改 `src/services/article.service.ts`（核心改写）

- **维度**：源码修改（最大改动面）
- **文件**：`src/services/article.service.ts`
- **风格约束**：保持 `export const fn = ...` 风格；保留所有 favorites 链路；不修改 `prisma.prisma-client` 导入；不修改 `HttpException` 错误处理。
- **操作**：详见下方子项（按函数分组）。
  1. **`buildFindAllQuery`**：移除 `'tag' in query` 整段（`src/services/article.service.ts:37-45`）。
  2. **`getArticles`**：移除 `include.tagList` 块（line 78-82），移除响应映射中 `tagList: article.tagList.map(tag => tag.name)`（line 104）。
  3. **`getFeed`**：移除 `include.tagList` 块（line 134-140），移除响应映射中 `tagList`（line 161）。
  4. **`createArticle`**：移除入参解构中的 `tagList`（line 170），移除 `tagList: { connectOrCreate: ... }` 写入（line 207-212），移除 include 中的 `tagList`（line 219-224），移除响应映射中 `tagList`（line 243）。
  5. **`getArticle`**：移除 `include.tagList` 块（line 255-259），移除响应映射中 `tagList: article?.tagList.map(...)`（line 284）。
  6. **`disconnectArticlesTags` helper**：整个 helper 函数删除（line 294-305）；同时删除 `updateArticle` 中对它的调用（line 337 `await disconnectArticlesTags(slug);`）。
  7. **`updateArticle`**：移除入参处理中的 `tagList` 计算（line 330-335），移除 `tagList: { connectOrCreate: tagList }` 写入（line 349-351），移除 include 中的 `tagList`（line 353-357），移除响应映射中 `tagList`（line 382）。
  8. **`favoriteArticle`**：移除 include 中的 `tagList`（line 540-544），移除响应 `result.tagList`（line 565）。
  9. **`unfavoriteArticle`**：移除 include 中的 `tagList`（line 587-591），移除响应 `result.tagList`（line 613）。
  10. **imports**：无变化（仍 `import prisma from '../../prisma/prisma-client'`、`import HttpException from '../models/http-exception.model'`、`import { findUserIdByUsername } from './auth.service'`、`import profileMapper from '../utils/profile.utils'`）。
- **影响范围**：
  - 行为变化：articles 相关 service 不再读写 tag；不再支持按 tag 过滤；favorites 链路完全保留（`favoriteArticle` / `unfavoriteArticle` 仅删除 tagList include，response 中 `favorited` / `favoritesCount` 字段保留）。
  - 编译影响：删除 `tagList: { some: { name: query.tag } }` 等 Prisma 关系引用，与 Step 11（移除 Prisma schema 中 `Article.tagList Tag[]`）必须配套。
- **回滚方式**：`git checkout HEAD -- src/services/article.service.ts`。
- **语义约定**：不涉及（不修改 status / enum / 错误码 / 权限名）。
- **验证方式**：`npm test` 仍通过（Step 13 配合清理 test mock）；Step 14 跑 `grep tagList src/services/article.service.ts` 应无命中。
- **确认类型**：改代码（最大改动面，单一文件 10 处子项）。

### Step 11: 修改 `prisma/schema.prisma`（移除 Tag model 与 Article.tagList 关系）

- **维度**：schema 变更（高风险：编辑 ORM schema 等同于 ALTER TABLE）
- **文件**：`prisma/schema.prisma`
- **风格约束**：Prisma schema 2-space 缩进；model 段顺序保留。
- **操作**：
  ```prisma
  // 修改前（Article model 第 22 行）
  model Article {
    id          Int       @id @default(autoincrement())
    slug        String    @unique
    title       String
    description String
    body        String
    createdAt   DateTime  @default(now())
    updatedAt   DateTime  @default(now())
    tagList     Tag[]   // <- 删除该行
    author      User      @relation("UserArticles", fields: [authorId], references: [id], onDelete: Cascade)
    authorId    Int
    favoritedBy User[]    @relation("UserFavorites", references: [id])
    comments    Comment[]
  }

  // 修改后：删除 tagList 行

  // 修改前：保留 Tag model
  model Tag {
    id       Int       @id @default(autoincrement())
    name     String    @unique
    articles Article[]
  }

  // 修改后：整段删除 model Tag
  ```
- **影响范围**：
  - schema 层面：Article 不再有 `tagList` 关系；Tag model 整体消失。
  - 数据库层面：本次不执行真实迁移；`prisma/migrations/` 旧文件保留不删。
  - 运行时：删除 schema 字段后，prisma generate 会重新生成 Prisma Client（`@prisma/client` 包），新生成的类型不再有 `tagList` / `prisma.tag`。这与 Step 10 删除 service 端 tagList 引用配套。
- **回滚方式**：`git checkout HEAD -- prisma/schema.prisma`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 跑 `npm test`（test mock 不依赖 schema 编译时绑定）；内容残留 grep `model Tag` / `tagList` 在 `prisma/schema.prisma` 应无命中。
- **确认类型**：schema 变更（命中"编辑 ORM schema 文件导致表结构变更"高风险清单；按"不可逆"标准单独确认）。同时命中"任何不可逆操作"——但因为不执行真实迁移，仓库内可 `git checkout` 回滚，所以仓库内仍是可逆的；新生成的 Prisma Client 在回滚 schema 后需要重跑 `prisma generate`。
- **高风险命中条目**：编辑 ORM schema 文件（Prisma `.prisma`）；090 须写明"不执行真实迁移的原因"。

### Step 12: 修改 `docs/swagger.json`（OpenAPI 契约同步）

- **维度**：API 契约文档修改
- **文件**：`docs/swagger.json`
- **风格约束**：保持 OpenAPI 2.0 风格；JSON 缩进 2 空格；删除对应键。
- **操作**：
  1. 移除 `GET /articles` 中的 `tag` queryparam（`docs/swagger.json:333-338`）。
  2. 移除 `/tags` path 整段（`docs/swagger.json:738-757`）。
  3. 移除 `Article` definition 中的 `tagList` 字段（`docs/swagger.json:908-913`）及其 required 项（`docs/swagger.json:937`）。
  4. 移除 `NewArticle` definition 中的 `tagList` 字段（`docs/swagger.json:981-986`）。
  5. 移除 `TagsResponse` definition 整段（`docs/swagger.json:1084-1095`）。
- **影响范围**：仅 Swagger 文档；不影响运行时。删除后 OpenAPI 文档与代码契约一致。
- **回滚方式**：`git checkout HEAD -- docs/swagger.json`。
- **语义约定**：不涉及。
- **验证方式**：Step 14 内容残留 grep（`"/tags"`、`TagsResponse`、`tagList` 在 `docs/swagger.json` 应无命中）；JSON 仍合法（`python -c "import json; json.load(open('docs/swagger.json'))"`）。
- **确认类型**：配置/API 契约变更。

### Step 13: 修改 `tests/services/article.service.test.ts`（清理 mock payload）

- **维度**：测试修改
- **文件**：`tests/services/article.service.test.ts`
- **风格约束**：Jest + Given/When/Then 注释风格；保留所有断言。
- **操作**：在 favoriteArticle 测试的 `mockedArticleResponse` 中删除 `tagList: [],`（line 48）；在 unfavoriteArticle 测试的 `mockedArticleResponse` 中删除 `tagList: [],`（line 103）。
  ```typescript
  // 修改前（favoriteArticle 测试，第 48 行附近）
  const mockedArticleResponse = {
    id: 123,
    slug: 'How-to-train-your-dragon',
    title: 'How to train your dragon',
    description: '',
    body: '',
    createdAt: new Date(),
    updatedAt: new Date(),
    authorId: 456,
    tagList: [],   // <- 删除
    favoritedBy: [],
    author: { ... },
  };

  // 修改后：删除 tagList: [], 那一行
  ```
- **影响范围**：仅 mock 数据；测试断言（`favoritesCount`）不变。
- **回滚方式**：`git checkout HEAD -- tests/services/article.service.test.ts`。
- **语义约定**：不涉及。
- **验证方式**：`npm test` 仍通过（基线 5 suites / 26 passed / 1 todo → 删除 tag.service.test.ts 后 4 suites / 26 passed / 0 todo）。
- **确认类型**：测试修复（命中"测试修复"确认类型）。

### Step 14: 运行最终验证（impact_validate + git diff --check + npm test）

- **维度**：最终验证
- **文件**：N/A（只读检查 + 命令）
- **风格约束**：N/A。
- **操作**：
  ```bash
  # 1. impact_validate
  python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py \
    change-impact/node-tags-removal-phase5 \
    --mode full \
    --repo-root .

  # 2. git diff --check
  git -C . diff --check

  # 3. npm test
  npm test
  ```
- **影响范围**：N/A。
- **回滚方式**：N/A。
- **语义约定**：N/A。
- **验证方式**：三个命令的退出码与输出已记录在 090。
- **确认类型**：只读分析（验证）——但每条命令若失败需要修复并重跑，修复本身需重新请求 `确认 Step N`。
- **预期**：
  - `impact_validate.py` 退出码 0；SUMMARY 含 PASS 项；FAIL=0；WARN 列出可能的（V5/V6 等非阻断 WARN）。
  - `git diff --check` 退出码 0，无 whitespace/line-ending 错误。
  - `npm test` 退出码 0；测试套件 4 suites / 26 passed / 0 todo（基线 5/26/1 → 删除 tag.service.test.ts 后偏差已说明）。

## 3.2 API 方法验证（⚠️ 强制必做 — 缺此节 impact_validate.py V3 FAIL 阻止提交）

> **此节不可跳过、不可改名、不可合并到其他节。** 对照 §3 执行步骤中引用的所有**已有代码库方法**，验证其存在性和异常行为。

| 方法名 | 来源文件 | grep 验证 | 异常行为 | 验证标注 |
|--------|---------|----------|---------|----------|
| `prisma.article.findMany(` | `src/services/article.service.ts:70` | ✅ 存在 `【已核实: src/services/article.service.ts:70】` | 命中空 where 时返回 `[]`，不抛异常 | 已确认 |
| `prisma.article.findFirst(` | `src/services/article.service.ts:315` | ✅ 存在 `【已核实: src/services/article.service.ts:315】` | 找不到返回 `null`，不抛异常 | 已确认 |
| `prisma.article.findUnique(` | `src/services/article.service.ts:188, 250, 408, 455` | ✅ 存在 `【已核实: src/services/article.service.ts:188,250,408,455】` | 找不到返回 `null`，不抛异常 | 已确认 |
| `prisma.article.create(` | `src/services/article.service.ts:201` | ✅ 存在 `【已核实: src/services/article.service.ts:201】` | 唯一约束冲突抛 P2002 | 已确认 |
| `prisma.article.update(` | `src/services/article.service.ts:339, 528, 576` | ✅ 存在 `【已核实: src/services/article.service.ts:339,528,576】` | 记录不存在抛 P2025 | 已确认 |
| `prisma.article.delete(` | `src/services/article.service.ts:390` | ✅ 存在 `【已核实: src/services/article.service.ts:390】` | 记录不存在抛 P2025 | 已确认 |
| `prisma.article.count(` | `src/services/article.service.ts:64, 115` | ✅ 存在 `【已核实: src/services/article.service.ts:64,115】` | 命中空 where 返回 0，不抛异常 | 已确认 |
| `prisma.user.findUnique(` | `src/services/article.service.ts`（被 mock）；`tests/services/article.service.test.ts:59, 72, 114, 127` | ✅ 存在 `【已核实: tests/services/article.service.test.ts:59,72,114,127】` | 找不到返回 `null`，不抛异常 | 已确认 |
| `prisma.comment.create(` | `src/services/article.service.ts:464` | ✅ 存在 `【已核实: src/services/article.service.ts:464】` | 唯一约束冲突抛 P2002；正常情况返回 created record | 已确认 |
| `prisma.comment.findFirst(` | `src/services/article.service.ts:505` | ✅ 存在 `【已核实: src/services/article.service.ts:505】` | 找不到返回 `null` | 已确认 |
| `prisma.comment.delete(` | `src/services/article.service.ts:518` | ✅ 存在 `【已核实: src/services/article.service.ts:518】` | 记录不存在抛 P2025 | 已确认 |
| `findUserIdByUsername(` | `src/services/auth.service.ts`（被 `article.service.ts:4, 113, 184, 309, 453, 526, 574` import） | ✅ 存在 `【已核实: src/services/article.service.ts:4】` | `findUserIdByUsername` 走 `prisma.user.findUnique`，找不到返回 `null`（`article.service.ts:308-309` 用 `user?.id`，已处理 null） | 已确认 |
| `profileMapper(` | `src/utils/profile.utils.ts`（被 `article.service.ts:5, 103, 160, 564, 612` import） | ✅ 存在 `【已核实: src/services/article.service.ts:5】` | 接受 `author` 对象 + `username`，无 throw；返回 Profile DTO | 已确认 |
| `slugify(` | `package.json:44` 依赖 `slugify`；`src/services/article.service.ts:1, 186, 312` | ✅ 存在 `【已核实: src/services/article.service.ts:1,186,312】` | 接受 title 字符串，返回 slug；不抛异常 | 已确认 |
| `HttpException` 构造 | `src/models/http-exception.model.ts`；`src/services/article.service.ts:3, 173, 177, 181, 198, 325, 450, 515` | ✅ 存在 `【已核实: src/services/article.service.ts:3】` | 构造时不抛；被 `next(error)` 抛出 | 已确认 |
| `auth.optional` | `src/utils/auth.ts`；`src/controllers/article.controller.ts:30, 87, 153` | ✅ 存在 `【已核实: src/controllers/article.controller.ts:30,87,153】` | 中间件，无 token 时 `req.user` 为 undefined；不抛异常 | 已确认 |
| `auth.required` | `src/utils/auth.ts`；`src/controllers/article.controller.ts:45, 71, 110, 133, 174, 198, 218, 238` | ✅ 存在 `【已核实: src/controllers/article.controller.ts:45,71,110,133,174,198,218,238】` | 无 token 时 `next(error)` 抛 401 | 已确认 |
| `prisma.tag.groupBy(` | `src/services/tag.service.ts:14` | ✅ 存在 `【已核实: src/services/tag.service.ts:14】` —— **本场景被删除**，Step 5 整文件删除后不再引用 | N/A | 删除中（Step 5） |
| `prisma.tag.*` 其它调用 | grep `prisma\.tag\.` 全仓 | ✅ 无任何 `prisma.tag.create` / `connect` / `disconnect` / `update` 等写入调用（仅 `tag.service.ts:14` 一处 groupBy 读取） | N/A | 无引用（Step 5 后彻底消失） |

> **填写说明**：
> - grep 验证：执行 `grep -rn "方法名" 项目根目录` 确认方法定义存在，标注 `【已核实: path:line】`。
> - 异常行为：打开方法源码检查是否有 throw 语句。本次只读源码 / `tests/prisma-mock.ts` mock 的均为 Prisma 标准方法，异常行为符合 Prisma 官方文档（findUnique 找不到返回 null，update/delete 找不到抛 P2025，create 唯一冲突抛 P2002）。
> - 删除中：`prisma.tag.groupBy(` 在 Step 5 删除 `tag.service.ts` 后从仓库消失；新 schema（Step 11）也不再生成 `prisma.tag` 类型，因此 `prisma.tag.groupBy(` 在最终代码中无任何引用。
> - 新增方法：本次不新增任何方法（删除功能不引入新方法）。

## 4. 回滚方案

### 逐步骤回滚

| Step | 回滚命令（Git） |
|------|-----------------|
| Step 1 | `git clean -fd change-impact/node-tags-removal-phase5/`（删除整个需求目录） |
| Step 4 | `git checkout HEAD -- src/controllers/tag.controller.ts`（从 HEAD 恢复） |
| Step 5 | `git checkout HEAD -- src/services/tag.service.ts` |
| Step 6 | `git checkout HEAD -- src/models/tag.model.ts` |
| Step 7 | `git checkout HEAD -- tests/services/tag.service.test.ts` |
| Step 8 | `git checkout HEAD -- src/routes/routes.ts` |
| Step 9 | `git checkout HEAD -- src/controllers/article.controller.ts` |
| Step 10 | `git checkout HEAD -- src/services/article.service.ts` |
| Step 11 | `git checkout HEAD -- prisma/schema.prisma`（schema 改回后若需重新生成 client，可跑 `npx prisma generate`，但 npm test 走 mock 不依赖生成产物） |
| Step 12 | `git checkout HEAD -- docs/swagger.json` |
| Step 13 | `git checkout HEAD -- tests/services/article.service.test.ts` |
| Step 14 | N/A（验证步骤） |

### 组合回滚顺序

```
全部回滚（一次性回到 HEAD）：
  1. git checkout HEAD -- <所有修改/恢复的文件>
  2. git clean -fd change-impact/node-tags-removal-phase5/

部分回滚（按 Step 倒序）：
  Step 13 失败：回滚 Step 13 → Step 12 失败：回滚 Step 12 → ... → Step 1 失败：删除 change-impact/ 目录
  任何 Step 失败后：先回滚当前 Step，再决定是否回滚后续 Step
```

具体场景：

```
Step 11 (Prisma schema) 失败时：
  1. git checkout HEAD -- prisma/schema.prisma
  2. 决定是否回滚 Step 10（article.service.ts 的 tagList 删除依赖 schema 同步变更；先回滚 schema 单独测试）
  3. 决定是否回滚 Step 4-7（已删文件本身与 schema 无关，但 routes.ts 引用需 Step 8 解引用）

Step 10 (article.service.ts) 失败时：
  1. git checkout HEAD -- src/services/article.service.ts
  2. Step 11 的 schema 改回或保留？
     - 保留 Step 11：service 已回滚但 schema 已改，编译会因 tagList 关系不存在而失败 → 必须回滚 Step 11
     - 回滚 Step 11：两端回到 HEAD
  3. Step 12/13 不依赖 Step 10，可保留
```

## 5. 验证步骤

### 正向用例（功能正常）

- [ ] `GET /api/articles`（无 tag queryparam） → 200 `{ articles, articlesCount }`，articles 中无 `tagList` 字段
- [ ] `POST /api/articles { title, description, body }`（无 tagList） → 200 `{ article }`，article 中无 `tagList` 字段
- [ ] `PUT /api/articles/:slug { title }`（无 tagList） → 200 `{ article }`，article 中无 `tagList` 字段
- [ ] `GET /api/articles/:slug` → 200 `{ article }`，article 中无 `tagList` 字段
- [ ] `POST /api/articles/:slug/favorite` → 200 `{ article }`，article 含 `favorited: true` 和 `favoritesCount: N+1`
- [ ] `DELETE /api/articles/:slug/favorite` → 200 `{ article }`，article 含 `favorited: false` 和 `favoritesCount: N`
- [ ] `GET /api/articles?author=foo` → 仍按作者过滤
- [ ] `GET /api/articles?favorited=bar` → 仍按收藏者过滤

### 错误用例（异常边界）

- [ ] `GET /api/tags` → 404（路由未挂载）
- [ ] `GET /api/articles?tag=foo` → 200（不再过滤；与无 tag queryparam 行为一致）
- [ ] `POST /api/articles { tagList: ["foo"] }` → 200（tagList 被忽略，文章正常创建）
- [ ] `GET /api/articles` 在 favorites 链路下：`_count.favoritedBy` 仍正确计算

### 其他验证

- [ ] `npm test` 退出码 0；4 suites / 26 passed / 0 todo（基线 5/26/1 → 删除 tag.service.test.ts 后偏差）
- [ ] `git diff --check` 退出码 0
- [ ] `impact_validate.py --mode full --repo-root .` 退出码 0
- [ ] `grep -rE "tag\.controller|tag\.service|model Tag|tagList|"/tags"|TagsResponse|getTags" src/ prisma/ docs/ tests/` 在源代码与契约中应无命中（change-impact/* 文档可保留）
- [ ] `grep -nE "favoriteArticle|favoritesCount|favoritedBy" src/ tests/` 在 favorites 链路中应仍命中

## 6. E2E / 验证脚本

脚本路径：`change-impact/node-tags-removal-phase5/050-validation/`

> 本场景不生成新 E2E 脚本：删除功能的验证由 `npm test`（基线 4 suites / 26 passed / 0 todo）+ `git diff --check` + `impact_validate.py` 三个门禁覆盖；tag 路由的下线通过 grep 内容残留 + `curl` 不再需要（无新接口可调用）覆盖。E2E 脚本属于"超出本场景"的工作。

## 7. 实施时间线

| 步骤 | 预计耗时 | 里程碑 |
|------|---------|--------|
| Step 1（Phase 4 文档） | < 1 min | 文档落盘 |
| Step 2（impact_validate） | < 1 min | V1-V17 全部 PASS / 仅 WARN |
| Step 3（060-preflight） | < 1 min | preflight 完成 |
| Step 4–7（4 个文件删除） | < 30s | 高风险删除完成 |
| Step 8（routes 解引用） | < 15s | 编译依赖解链 |
| Step 9（controller JSDoc） | < 15s | 注释与代码一致 |
| Step 10（service 改写） | ~1 min | favorites 链路独立保留 |
| Step 11（schema） | < 30s | Tag model 移除 |
| Step 12（swagger） | < 30s | OpenAPI 同步 |
| Step 13（test mock） | < 15s | 测试 mock 与新契约一致 |
| Step 14（最终验证） | < 1 min | 三个门禁通过 |

> 单次确认→执行循环不消耗等待时间；累计时长 = 写入+验证命令的墙钟时间。

## 8. 跨会话恢复状态

状态文件写入 `change-impact/node-tags-removal-phase5/_active-state.md`，格式参照 `templates/_active-state.md`。它只记录当前 Phase、pending Step、文档确认状态、验证等级、未确认项和恢复检查结果，不构成任何写操作授权。

恢复时必须先读 `_active-state.md`、本实施文档、`060-preflight.md` 和 `090-execution-record.md`，再复核磁盘状态并重新要求当前对话中的 `确认 Step N`。

## 9. 环境备选路径

如果实际执行时**部分验证命令不可用**（如 DB / 服务 / 工具缺失），启用以下备选方案：

| 计划验证 | 环境缺失场景 | 备选方案 |
| --- | --- | --- |
| `python impact_validate.py` | Python 不可用 | 跳过 V2/V6 等 Python 解析，改为人工对照模板清单逐条 review；交付时声明"未跑 V1-V17 自动验证" |
| `git diff --check` | 非 Git 仓库 | 本项目为 Git 仓库，HEAD `6ac99ea`，无需备选 |
| `npm test` | npm / Node 不可用 | 静态检查：tsc --noEmit（编译验证）+ grep 内容残留（功能性验证） |
| 真实数据库迁移验证 | 不执行真实迁移（本场景） | N/A — 090 写明"不执行迁移" |

**备选方案已在风险预判时识别并写入本文档**，避免"事后才发现环境受限"。

---

## 判档决策表（full 模式必填）

> 交付矩阵 case_id `node-realworld-prisma-phase5-tags-removal` + prompt 明确"必须先做 full 影响分析并通过 Phase 4"——本场景为 **full 模式**。

| 维度 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|------|------------------|------|----------|
| 路由层 | `src/routes/routes.ts:2,8` import + `.use(tagsController)`，`src/controllers/tag.controller.ts:13` 注册 `GET /tags` | 需移除 import / `.use` / 整个 controller | 命中"删旧接口 / Controller 类"高风险，纳入 Step 4+8 |
| Service 层 | `src/services/tag.service.ts:1-35` 仅 `getTags`；`src/services/article.service.ts` 7 处 `tagList` 引用 | 整文件删 + service 端 7 处清理 | 命中"删旧 Service"，纳入 Step 5+10 |
| Model 层 | `src/models/tag.model.ts:1-3` 仅 `Tag { name: string }`；Prisma schema `Tag` model + `Article.tagList` 关系 | 整文件删 + schema 整段删 | 命中"删旧 Model"+"编辑 ORM schema"，纳入 Step 6+11 |
| 测试层 | `tests/services/tag.service.test.ts:1-6` 1 个 `test.todo`；`tests/services/article.service.test.ts:48,103` mock 含 `tagList: []` | 整文件删 + mock 字段清理 | 纳入 Step 7+13 |
| API 契约 | `docs/swagger.json:333-338, 738-757, 908-913, 937, 981-986, 1084-1095` 6 处 tag 痕迹 | 6 处全部清理 | 纳入 Step 12 |
| 数据库 | Prisma schema `Article.tagList Tag[]` + `model Tag` | 同步移除 | 命中"编辑 ORM schema"高风险，纳入 Step 11，090 写明"不执行真实迁移的原因" |
| 鉴权 | `tag.controller.ts:13` 使用 `auth.optional`；favorites 使用 `auth.required` | 删除 controller 后 `auth.optional` 仍被其他 controller 复用 | 不动 `utils/auth.ts` |
| 兼容性 | 调用方可能仍在使用 `/api/tags` / `tagList` | 无兼容期 | 用户原话"全量下线"，已与用户对齐为破坏性变更 |
| 回滚 | Git 工作树，每步独立可 `git checkout HEAD -- <path>` 回滚 | 仓库可逆；旧 migration 不动 | 满足 |
| 现有实现完整度 | 完整（`npm test` 5/26/1 baseline pass） | 基线预期：删除 tag.service.test.ts 后 4/26/0 | 偏差已说明，090 写明 |
| 整体规模 | 10 个文件（4 删 + 6 改），跨 6 个层级 | 无 | **判档 full**：跨多层级 + 高风险删除 + 不可逆 schema 变更 + 跨多种工件（schema/swagger/test/源码） |

> 判档结论：**full 模式**——跨多层级、命中多个高风险条目、不可逆 schema 变更；light 不足以覆盖完整影响分析。
