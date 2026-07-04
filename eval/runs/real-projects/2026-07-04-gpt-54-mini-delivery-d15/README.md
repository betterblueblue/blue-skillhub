# tags 功能删除影响分析

> 说明：本次只做只读影响分析，不改目标项目源码、测试、配置或数据库。

## 1. 变更意图

用户原话是“`tags` 功能没人用了，把它整个删掉。先不要写代码，只做完整影响分析。”【已核实: E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-analysis-batch\prompts\d15-gpt-54-mini-subagent.txt】

这里有一个关键歧义：`tags` 到底是指公开的 `GET /api/tags` 接口，还是连文章里的 `tagList` 一起删掉。当前代码里两者都存在，而且文章标签还参与查询、创建、更新和 API 文档，所以这不是一个单点删接口的问题。

当前判断：**倾向 full**。原因是它已经碰到公开 API、Prisma schema、文章链路和 Swagger 契约，不是局部文案或单文件逻辑。

## 2. 项目背景

- 技术栈：Node.js + Express + Prisma + PostgreSQL【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\package.json:1-8】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\prisma\schema.prisma:1-10】
- 启动入口：`src/index.ts`，路由总入口：`src/routes/routes.ts`【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\index.ts:1-33】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\routes\routes.ts:1-13】
- 公开文档：`docs/swagger.json`，并由 `src/index.ts` 挂到 `/api-docs`【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\index.ts:20-29】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:738-746】
- 现成的项目级 `_project-map.md` 和 `_style-rules.md` 没找到，刚才在目标项目根目录下检查结果都是 `False`，所以这次只能按仓内代码和脚本规则现查现写。

## 3. 已确认事实

1. `/api/tags` 是真实存在的公开路由，挂在 `tagsController` 上【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\controllers\tag.controller.ts:8-16】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\routes\routes.ts:1-13】
2. `getTags()` 直接查 `prisma.tag.groupBy(...)`，返回热门标签名列表【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\tag.service.ts:3-36】
3. Prisma schema 里有 `Tag` 模型，`Article` 还通过 `tagList` 和它建立多对多关系【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\prisma\schema.prisma:14-42】
4. 文章列表支持 `?tag=` 过滤，文章创建和更新都在写 `tagList`，更新时还会先把旧关联清空【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:7-45】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:170-243】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:294-382】
5. Swagger 里既有 `/tags` 路径，也把 `tagList` 写进文章请求/响应定义【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:738-746】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:908-981】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:1084-1094】
6. `TagService` 的测试只有一个 `todo`，说明这块本身覆盖就很弱【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\tests\services\tag.service.test.ts:1-4】
7. `src/models/tag.model.ts` 里还定义了一个 `Tag` 接口，但在这次扫描里没有看到它被别的文件引用【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\models\tag.model.ts:1-3】

## 4. 影响面

### 4.1 如果只删 `GET /api/tags`

影响会集中在：

- 路由注册：`src/routes/routes.ts`
- 控制器：`src/controllers/tag.controller.ts`
- 服务：`src/services/tag.service.ts`
- Swagger：`docs/swagger.json` 里的 `/tags` 和 `TagsResponse`
- 测试：`tests/services/tag.service.test.ts`
- 可能的死代码清理：`src/models/tag.model.ts`

这个版本已经是公开 API 删除，属于破坏性变更，但还没碰文章本体的数据结构。

### 4.2 如果连文章标签一起删

影响会明显放大，至少还要碰：

- 文章查询过滤：`?tag=` 逻辑
- 文章创建/更新：`tagList` 输入和写入
- 文章读取返回：`tagList` 输出
- Prisma schema：`Article.tagList`、`Tag` 模型和关联关系
- Swagger：文章请求/响应里的 `tagList`
- 文章相关测试：所有带 `tagList` 的 mock 和断言

这个版本已经是 **API + schema + 数据迁移** 联动，必须按 full 级别看。

## 5. 判档决策表

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|---|---|---:|---|
| `tags 功能没人用了，把它整个删掉` | 已确认有 `/api/tags` 公开接口，且 `Article` 仍然依赖 `tagList` 做查询、写入和返回【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\controllers\tag.controller.ts:8-16】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:7-45】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\prisma\schema.prisma:14-42】 | `tags` 语义有歧义：只删 `/api/tags` 还是连 `tagList` 一起删，当前还没被用户拍板 | **full**（公开 API 删除 + 文章链路 + schema 风险） |

## 6. 全局影响检查

> 下面这一段按 19 个维度逐项标记。`☑` 表示这次变更会碰到，`☐` 表示当前证据看不到直接影响。

| # | 维度 | 影响 | 证据 / 说明 |
|---:|---|:---:|---|
| 1 | 数据库 | ☑ | `Tag` 模型和 `Article.tagList` 关系存在，删“整个 tags”很可能要改 schema 或迁移【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\prisma\schema.prisma:14-42】 |
| 2 | 代码 | ☑ | `tag.controller.ts`、`tag.service.ts`、`article.service.ts` 都直接用到 tags 逻辑【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\controllers\tag.controller.ts:8-16】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:7-45】 |
| 3 | 配置 | ☐ | 没看到和 tags 直接相关的配置开关 |
| 4 | 接口/契约 | ☑ | `/api/tags`、`?tag=`、`tagList` 请求/响应都在公开契约里【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:738-746】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:908-981】 |
| 5 | 消息队列/事件 | ☐ | 未找到相关事件流 |
| 6 | 缓存 | ☐ | 未找到相关缓存键 |
| 7 | 基础设施 | ☐ | 没看到和 tags 相关的 Docker / CI 变更需求 |
| 8 | 前端 | ☐ | 仓内没有前端文件，当前只看到后端 API 和 Swagger |
| 9 | 文档/注释 | ☑ | Swagger 里有 `/tags` 和 `tagList`，控制器注释也写了 `Get top 10 popular tags`【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:738-746】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\controllers\tag.controller.ts:8-16】 |
| 10 | 监控/告警 | ☐ | 未找到相关指标或告警 |
| 11 | 测试/用例 | ☑ | `TagService` 只有 `todo`，文章服务测试也带着 `tagList` mock【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\tests\services\tag.service.test.ts:1-4】【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\tests\services\article.service.test.ts:45-60】 |
| 12 | 日志/埋点 | ☐ | 未找到 tags 专用日志 |
| 13 | 凭证/密钥 | ☐ | 没有相关凭证变更 |
| 14 | 网络/路由 | ☑ | `/api/tags` 是显式路由挂载项【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\routes\routes.ts:1-13】 |
| 15 | 存储/文件 | ☐ | 未看到文件存储链路 |
| 16 | 安全/权限 | ☐ | `tags` 当前是 `auth.optional`，删除它本身不改权限模型 |
| 17 | 版本兼容性 | ☑ | 删除公开接口和响应字段是破坏性变更，旧消费者会直接受影响【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\docs\swagger.json:738-746】 |
| 18 | 事务/一致性 | ☑ | 如果连 `tagList` 一起删，会牵到文章写入和关联清理，迁移时要保证数据一致性【已核实: E:\agent\real-project-fixtures\node-realworld-prisma\src\services\article.service.ts:294-382】 |
| 19 | 依赖包/SDK | ☐ | 目前没有看到需要新增或升级依赖包 |

## 7. 未确认项

1. **只删 `/api/tags`，还是连文章 `tagList` 一起删？**
   - 默认建议：如果用户说的是“整个删掉”，应按整条标签链路处理。
   - 但从代码看，这会直接碰到文章查询、创建、更新和 schema，所以需要你最后拍板范围。

2. **是否要保留历史文章里的 tag 数据，还是做一次清理/迁移？**
   - 目前仓内只看到 schema 和业务代码，没看到任何清理策略。

3. **Swagger 文档是否一并删除或改写？**
   - 现在 `/api-docs` 直接对外提供 `docs/swagger.json`，删接口不改文档会留下假入口。

## 8. 结论

这次变更不是一个单点删函数，而是一个 **full 级别的破坏性变更**。

如果最终范围只落在 `GET /api/tags`，影响还算可控，但已经属于公开 API 删除；如果范围扩展到 `tagList`，就要同步处理文章查询、文章写入、Swagger 和 Prisma schema，基本就是完整标签链路下线。

## 9. 命令记录

下面是本次只读分析里跑过的命令，均未修改目标项目源码：

- `Get-Content -Raw .../impact/SKILL.md`，退出码 `0`
- `Get-Content -Raw .../references/*.md`，退出码 `0`
- `rg --files ...`，退出码 `0`
- `rg -n "tags|tagList|/tags" ...`，退出码 `0`
- `Get-Content -Raw` 读取 `package.json`、`prisma/schema.prisma`、`src/routes/routes.ts`、`src/controllers/tag.controller.ts`、`src/services/tag.service.ts`、`src/services/article.service.ts`、`docs/swagger.json`、`tests/services/tag.service.test.ts`，退出码 `0`
- `Test-Path change-impact\\_project-map.md; Test-Path change-impact\\_style-rules.md`，退出码 `0`
- `git rev-parse --short HEAD; git status --short`，退出码 `0`

`impact_validate.py` 没有运行：本次交付按用户约束只允许输出单个 `README.md`，没有生成 `change-impact/{需求名称}/` 多文件目录，脚本的文件完整性门禁不适用。
