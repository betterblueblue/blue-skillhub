# Case F1: 后端库存预警字段（full）

> FastAPI template @ `38302d7`。基于 impact-pro python-fastapi-sqlmodel profile 模拟。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | F1 |
| Project | full-stack-fastapi-template（后端） |
| Skill | impact-pro |
| 档位 | full |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: items should have a warning threshold. When stock falls below it, the item detail API should return `low_stock: true`. Do not modify code. Produce an impact analysis and implementation plan.

## Phase 1 意图捕获

**当前假设**：Item 表新增 `warning_threshold` 字段，GET /items/{id} 返回 `low_stock: bool`。

**可能歧义**：
- 阈值默认值（PM 未给）
- 阈值是否可负（合理性边界）
- 已存在商品如何初始化（migration 步骤）

## Phase 2 上下文发现（基于 T03 baseline）

**关键文件**（T03 模式）：
- `backend/app/models/item.py` — SQLAlchemy model
- `backend/app/schemas/item.py` — Pydantic schema
- `backend/app/api/items.py` 或 `routers/items.py`
- `backend/app/services/item.py`
- `backend/alembic/versions/xxx_item_warning_threshold.py` — Alembic migration
- `backend/tests/test_items.py` — pytest

**栈**：Python 3.11+ + FastAPI + SQLAlchemy + Pydantic v2 + Alembic + pytest

**前端**（仅当跨端识别）：
- `frontend/src/api/items.ts` 或 `routes/items/index.tsx`
- `frontend/src/components/ItemCard.tsx` 等

## Phase 2.5 风险预判

```text
初步风险：倾向 full
profile 命中：python-fastapi-sqlmodel
DB：PostgreSQL
需要澄清：阈值默认值/已有商品初始化
```

## Phase 3 苏格拉底式探索（3 轮）

**第 1 轮**：
1. warning_threshold 默认值？10？50？
2. 已有商品如何初始化（NULL vs 默认 0 vs 默认 50）？
3. 低库存触发线：<= threshold 还是 < threshold？

**第 2 轮**：
4. 是否需要 backfill 脚本（给已有商品设默认）？
5. 是否需要发送通知（库存预警邮件）？

**第 3 轮**：
6. API 文档（OpenAPI）同步？
7. pytest 覆盖：model 校验 + API 响应？

## Phase 3.5 判档

```text
建议档位：full
profile 命中：python-fastapi-sqlmodel
adapter：generic-sql（无 MySQL 专属）
```

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact-pro |
| 完成的 Phase | 1-4 ✓ |
| Step 确认次数 | 4（migration / model / schema / router） |
| 实际改动文件数 | 4-5 |
| 卡住位置 | 无 |
| 总耗时 | 约 16 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | |
| 2. 上下文发现 | 16/18 | |
| 3. 苏格拉底 | 14/15 | 3 轮完整 |
| 4. 维度选择 | 7/8 | |
| 5. 判档 | 9/10 | |
| 6. 文档 | 11/12 | |
| 7. 执行安全 | 9/10 | |
| 8. TDD 验证 | 8/10 | pytest 模式 |
| 9. 命令验证 | 4/5 | alembic 命令正确 |
| **基础总分** | **90/100** | |
| 行为分 | 7/10 | |
| **总分** | **97/110** | |

**P 等级**：无
**通过？**：是

## 关键发现

- profile 准确识别 Pydantic vs SQLAlchemy 分离
- 缺：未提醒 alembic revision 文件命名规范（应查现有 naming 约定）

## 与 validation-runs 对比

- 复用基线：T03
- 主要差异：subagent 略浅于 T03（未提 email 通知）

---

## Phase 5 自治试跑（2026-06-10，subagent-as-user 模式）

> 本段为 **Phase 5 实际执行**试跑结果，subagent-as-user 自治模式。

### 沙盒产物（REAL Phase 5）

位置：`E:\agent\skill-eval-sandbox\fastapi\backend\change-impact\f1-phase5-autonomy\`

| 文件 | 字节 | 角色 |
| --- | ---: | --- |
| `subagent-decisions.md` | 11424 | **最关键**：7 Steps 的 RESTATE+DECIDE+RECORD |
| `900-执行记录.md` | 9871 | Phase 5 时间线 |
| `code-changes-summary.md` | 8801 | 实际改文件清单 |
| `verification-results.md` | 7142 | V1/V2/V3 验证结果 |
| `standalone_test.py` | 10342 | V3 受限下的兜底（4 类 Pydantic/alembic/OpenAPI/继承验证） |

### 决策矩阵

| Step | DECIDE | 1 行理由 |
| --- | --- | --- |
| 0 | subagent-confirm | 只读探测（git status / alembic heads / env） |
| 1 | subagent-confirm | ADDITIVE：`app/models.py` 加 stock + warning_threshold + low_stock |
| 2 | subagent-confirm | ADDITIVE：新增 alembic migration（`server_default="0"` 兜底存量行） |
| 3 | subagent-confirm | 零改动确认（`git diff` 为空：路由层无需改） |
| 4 | subagent-confirm | ADDITIVE：`tests/utils/item.py` 加 kw-only 参数 |
| 5 | subagent-confirm | ADDITIVE：`tests/api/routes/test_items.py` 追加 5 个测试用例 |
| 6 | subagent-confirm | 无（plan 文档未列独立 Step 6） |
| 7 | subagent-confirm | （与 R3 试跑无关；F1 无 Step 7） |

**P0 兜底触发：0**（全 ADDITIVE，符合预期）

### 实际改文件（git diff 验证）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `app/models.py` | M | +9 行（import + 2 字段 + @computed_field） |
| `app/alembic/versions/6d5d0617b4d1_*.py` | NEW | +35 行新文件 |
| `tests/utils/item.py` | M | +14 行（kw-only 签名） |
| `tests/api/routes/test_items.py` | M | +99 行（追加 5 用例） |

**0 个 v1/v2 既有文件被破坏**——**完全符合 100-设计文档**。

### 验证等级

| 等级 | 命令 | 结果 |
| --- | --- | --- |
| V1 静态 | Grep 引用检查 + 片段对照 | ✓ 通过（12+ 文件） |
| V2 静态 | `ruff check app tests` | ✓ PASS |
| V2 静态 | `mypy app` (strict) | ✓ Success: no issues found in 21 source files |
| V2 静态 | `ty check app` | ✓ All checks passed |
| V2 alembic | `alembic heads` | ✓ 6d5d0617b4d1 识别 |
| V2 alembic | SQLite stand-in upgrade + downgrade | ✓ OK |
| V2 OpenAPI | `app.openapi()` | ✓ ItemPublic.low_stock: bool 出现 |
| V2 边界 | Pydantic 实例化（3<5=True / 5=5=False / 10>5=False / 0=0=False） | ✓ 4 边界全过 |
| V3 pytest | `pytest --collect-only` | ✓ 16 用例 collect 过 |
| V3 pytest 实际 | `pytest tests/` | ❌ **BLOCKED** — 无 Postgres / Docker 未运行 |
| V3 替代 | `standalone_test.py` | ✓ 4 个子测试全过 |

### 诚实差距（subagent 自报）

1. 未跑真实 pytest suite（含原 11 个用例）
2. 未验证 `ItemPublic.model_validate(item_instance)` 在 FastAPI `response_model=ItemPublic` 序列化时 `low_stock` 自动出现的运行时路径
3. 未跑 `alembic upgrade head` 真实 Postgres（`op.alter_column(..., server_default=None)` 是 Postgres-specific）
4. 未读 pre-existing alembic branch (`fe56fa70289e` 旁支) 的成因
5. 未跑 pre-commit 钩子

### 关键真实发现

- **F1 主动行为**：subagent 在 V3 受限时**主动写 `standalone_test.py`**——协议没规定但 subagent 自觉做了。**应协议化**为"V3 受限自动进 standalone 模式"。
- **F1 偏离计划**：subagent 用**手写 alembic migration** 替代 `alembic revision --autogenerate`——**未显式记录偏离原因**。**应强制"偏离计划"段必填**。
- **F1 关键安全决策**：alembic 用 `nullable=False, server_default="0"` 兜底存量行；测试工具用 kw-only 参数 + 默认 0，**现有调用方零修改**。
- **F1 风格遵循**：snake_case、Field(default=0, ge=0)、@computed_field + `# type: ignore[prop-decorator]`（与项目既有 `models.py` L34 风格一致）。

### 试跑统计

- Token：113K
- 工具调用：131
- 耗时：22 分钟

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\fastapi\backend\change-impact\f1-stock-warning\`

5 个文件齐全。`context-pack.md` 明确列出 profile：`python-fastapi-sqlmodel.md`

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact-pro`（通过 Skill 工具） |
| 加载的 profile | `python-fastapi-sqlmodel`（Level 1，pyproject.toml 命中 fastapi/sqlmodel/sqlalchemy/alembic/pytest） |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（3 轮完整）/ 3.5✓ / 4✓ / 5 跳过 |
| 实际改文件数 | 0（仅 backend/ 目录；frontend/ 未触碰） |
| 关键发现 | `app/models.py` ItemBase 缺 stock + warning_threshold；alembic 5 个 migration 在 `app/alembic/versions/`；Pydantic v2 `@computed_field` 派生 `low_stock` 策略 |
| 幻觉路径 | 0 |
| Token 消耗 | 62,228 |
| 跑分耗时 | 6 分 09 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 + profile | 12 |
| 2. 上下文发现 | 17 |
| 3. 苏格拉底 | 14 |
| 4. 维度选择 | 8 |
| 5. 判档 | 10 |
| 6. 文档 | 11 |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 8（pytest + alembic upgrade/downgrade） |
| 9. 命令验证 | 4 |
| **基础总分** | **94/100** |
| 行为分 | +10 |
| **总分** | **104/110** ✓ 通过 |

### 关键真实发现

- **Pydantic v2 @computed_field 策略**：`low_stock` 放在 `ItemPublic` schema 用 `@computed_field` 派生，**不动 SQLAlchemy 模型**，**不动 router**——单一数据源，零侵入。
- **alembic head revision 推断**：5 个 migration 文件按文件名排序推断 head 是 `1a31ce608336`，但 subagent **显式标注** "未读取该文件确认 down_revision 链，作为 Phase 5 preflight 前置条件"——**没编造**。原 P3-003（alembic head 必读）即源于此。
- **Item 模型无 stock 字段**：verified `app/models.py` 全文 129 行，stock 字段**不存在**，需新增。
- **Migration 数量**：5 个 alembic 迁移（`e2412789c190_initialize_models` / `fe56fa70289e_add_created_at` / `9c0a54914c78_add_max_length` / `d98dd8ec85a3_edit_replace_id` / `1a31ce608336_add_cascade_delete`）
