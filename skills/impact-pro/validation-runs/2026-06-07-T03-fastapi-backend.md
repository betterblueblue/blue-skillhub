# T03 full-stack-fastapi-template/backend - 商品库存预警字段

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Python / FastAPI / SQLModel / Alembic
- 项目路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template\backend`
- Commit：`38302d7492dbd158ed6cf499a6dd0bab6ad17141`
- 变更意图：新增商品库存预警阈值，低于阈值时商品详情接口返回 `low_stock=true`。
- 使用档位：full
- 命中 profile：`generic`
- 最终评分：80
- 失败等级：P2

## 实际发现

### 技术栈检测

可识别证据：

- `pyproject.toml` 存在。
- 依赖包含 `fastapi`、`sqlmodel`、`alembic`、`pytest`。
- 存在 `app/api/routes/items.py`、`app/models.py`、`app/alembic/versions/*.py`。

当前 `impact-pro` 无 Python/FastAPI 专属 profile，因此加载 `generic`。

### 上下文发现

当前 generic glob 可发现：

- API routes：`app/api/routes/items.py`
- 测试：`tests/api/routes/test_items.py`
- Alembic：`app/alembic/versions/*.py`

当前 generic glob 会漏掉：

- `app/models.py`
- `app/crud.py`

关键证据：

- `app/models.py` 中 `ItemBase` 定义 `title`、`description`。
- `Item` 是 `SQLModel` table，包含 `id`、`created_at`、`owner_id`。
- `ItemPublic` 是 API 返回模型。
- `app/api/routes/items.py` 的 `read_item()` 返回 `ItemPublic`。
- `tests/api/routes/test_items.py` 已覆盖创建、读取、更新、删除和权限错误。

### 风险追问

应追问：

1. `warning_threshold` 类型是整数还是小数，默认值是多少？
2. 是否需要新增实际库存字段，否则 `low_stock` 无法计算？
3. 存量 `Item` 如何初始化阈值？
4. `low_stock` 是存储字段还是响应计算字段？
5. 普通用户是否只能看到自己的库存状态？

### 定级

应判定 full。

理由：

- DB model 和 Alembic migration 变更。
- API response model 变更。
- 业务计算逻辑变更。
- 测试需要覆盖正向和边界。

## 评分

| 维度 | 分值 | 得分 | 说明 |
|------|------|------|------|
| 技术栈检测与 profile 选择 | 15 | 13 | 能识别 Python，但无专属 profile |
| 上下文发现 | 20 | 14 | 找到 routes/tests/migrations，漏 `models.py` |
| 风险识别与追问 | 20 | 15 | 可提出关键问题，但依赖人工补模型 |
| light/full 定级 | 10 | 9 | full 明确 |
| 文档质量 | 15 | 12 | 可写，但证据来源需标注缺口 |
| 执行安全 | 10 | 10 | 写操作确认规则存在 |
| 验证设计 | 10 | 7 | 能生成 API 用例，但需 SQLModel 专属细化 |

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P2 | generic 漏 `models.py` | `**/*Model*.py` 不匹配 `app/models.py` | 增加 `**/models.py`、`**/schemas.py` |
| P2 | 无 FastAPI/SQLModel 风格轴 | 当前 style_axes 为空 | 新增 `python-fastapi-sqlmodel` profile |
| P3 | 命令需要确认 | `backend/scripts/test.sh` 和 `pyproject.toml` 均提供线索 | profile 中补 `pytest`、`ruff`、`alembic` 候选 |

## 结论

有条件通过。可用于 FastAPI 项目分析辅助，但必须人工确认 model/schema 文件。
