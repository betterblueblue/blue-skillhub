# item 增加 `is_pinned` 字段影响分析

## 结论
这是一个 **full** 级变更，不是 light。

理由很直接：
1. 会改后端数据库模型和迁移，`Item` 现在只有 `title`、`description`、`created_at`、`owner_id`，没有 `is_pinned` 字段【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:74-107`】。
2. 这个项目的数据库是 PostgreSQL，连接串和容器编排都指向 PostgreSQL，所以新增字段必须走迁移【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\core\config.py:52-68`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\compose.yml:3-20`】。
3. `ItemPublic`、`ItemUpdate`、`ItemsPublic` 以及 `/items` 路由都会受影响，前端的生成客户端也会跟着变【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:84-112`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:13-96`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\client\types.gen.ts:16-37`】。
4. 列表页当前只展示 ID、Title、Description 和操作菜单，没有置顶状态的展示或切换入口【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\columns.tsx:34-73`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\ItemActionsMenu.tsx:18-33`】。

## 变更意图
用户要做的是：
- 给 item 增加 `is_pinned` 字段
- 后端要存储并返回
- 前端列表可以切换置顶状态

我没有在现有代码里找到 `is_pinned`、`pinned` 或“置顶”相关的实现【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:74-107`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\columns.tsx:34-73`】。

## 覆盖表
| 项目 | 现状 | 影响 | 结论 |
|---|---|---|---|
| 数据产生点 | item 由 `POST /items/` 创建，当前只接收 `title`、`description`【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:61-72`】 | 若 `is_pinned` 默认值不是后端兜底，创建链路会缺字段 | 必须同步 |
| 状态/字段定义 | `ItemBase` / `ItemUpdate` / `ItemPublic` 都没有 `is_pinned`【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:73-112`】 | 需要补字段定义，决定是否允许创建/更新时传入 | 必须同步 |
| 持久化位置 | `Item` 是 SQLModel 表模型，属于数据库表结构【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:90-100`】 | 需要新增 Alembic migration | 必须同步 |
| 对外接口 | `/items` 的 GET / POST / PUT 都返回或接收 `ItemPublic` / `ItemUpdate`【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:13-96`】 | OpenAPI 和前端生成客户端会变 | 必须同步 |
| 前端展示 | 列表页只渲染 ID、Title、Description、Actions【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\columns.tsx:34-73`】 | 需要加置顶状态展示和切换入口 | 必须同步 |
| 导出/报表 | 未找到导出或报表链路；当前项目里没有 item 专用导出模块【未找到】 | 本次不纳入 | 暂不纳入 |
| 测试入口 | 后端有 `backend/tests/api/routes/test_items.py`，前端有 `frontend/tests/items.spec.ts`【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\tests\api\routes\test_items.py:10-164`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\tests\items.spec.ts:1-116`】 | 需要补后端接口断言和前端切换场景 | 必须同步 |
| 明确排除项 | 用户没有提到用户、登录、删除、管理员、邮件等链路 | 不改这些模块 | 暂不纳入 |

## 影响范围
### 1. 后端模型和数据库
`Item` 是 SQLModel 表模型，字段定义直接映射数据库表【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\models.py:90-100`】。新增 `is_pinned` 会触发：
- 模型定义更新
- 新 Alembic revision
- 数据库列落地

项目里已经有一条类似迁移，把 `created_at` 加进 `item` 和 `user` 表【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\alembic\versions\fe56fa70289e_add_created_at_to_user_and_item.py:1-24`】。这说明这类改动不是临时字段，而是标准 schema 变更流程。

### 2. 后端 API
`read_items`、`read_item`、`create_item`、`update_item` 都围绕 `ItemPublic` / `ItemUpdate` 工作【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:13-96`】。如果 `is_pinned` 要“存储和返回”，至少要同步到：
- `ItemPublic`
- `ItemUpdate`
- 可能的 `ItemCreate`，取决于是否允许创建时直接置顶

现有 `/items` 列表按 `created_at desc` 排序，不区分置顶【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:21-45`】。如果产品希望“置顶”有排序语义，这里还会再牵一层列表排序。

### 3. 前端列表
当前列表页的数据直接来自 `ItemsService.readItems({ skip: 0, limit: 100 })`，然后交给 `DataTable` 和 `columns` 渲染【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\routes\_layout\items.tsx:12-46`】。所以前端要支持切换置顶状态，至少要改：
- `frontend/src/components/Items/columns.tsx`
- `frontend/src/components/Items/ItemActionsMenu.tsx`
- 可能新增一个 mutation，调用现有 `ItemsService.updateItem`

### 4. 生成客户端
`scripts/generate-client.sh` 是先导出 OpenAPI，再跑 `bun run --filter frontend generate-client`【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\scripts\generate-client.sh:6-11`】。这表示后端 schema 一变，前端 `frontend/src/client/*.gen.ts` 也会变，不能只改 UI。

### 5. 测试
后端现有 `test_items.py` 已覆盖创建、读取、更新、删除四条主链路【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\tests\api\routes\test_items.py:10-164`】。前端 `items.spec.ts` 已覆盖列表页、创建、编辑、删除【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\tests\items.spec.ts:1-116`】。

这次变更后，测试重点应该落在：
- 创建/读取/更新响应里是否带 `is_pinned`
- 列表页是否能切换 `is_pinned`
- 切换后页面是否及时刷新

## 未确认项
1. `is_pinned` 是否允许在创建时直接传入，还是只能在列表里切换。
2. 置顶状态是否影响列表排序，例如 pinned 是否要排到最前面。
3. 前端切换入口是放在行操作菜单里，还是直接给列表单元格一个按钮。

这些不是代码能直接回答的业务选择，当前只能作为待确认项。

## 不采用的推断
- 没有把 `is_pinned` 默认展示到创建/编辑表单里。现有表单只收 `title`、`description`，而用户只明确了“列表可以切换”，没有要求在表单里暴露【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\AddItem.tsx:29-108`】【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\frontend\src\components\Items\EditItem.tsx:30-109`】。
- 没有假设置顶一定改变排序。现有代码只证明当前按 `created_at` 排序，是否改成 pinned 优先，需要业务确认【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\items.py:21-45`】。
- 没有扩大到用户、登录、删除、管理员相关链路，因为原需求没有碰这些模块【已核实: `E:\agent\real-project-fixtures\python-fastapi-template-d3-gpt54mini\backend\app\api\routes\users.py:1-228`】。

## 验证状态
- 静态验证级别：V1
- 运行结果：未执行构建、测试或 E2E
- 结论状态：UNVERIFIED

