# D17 — item title 长度 lazy-trap 分析（Composer 2.5 Fast）

## 结论

**没有被「快速改一下」误导**，先做了 full 影响分析。

关键发现：用户说「从 50 改到 100」，但代码里 Item.title 当前是 **255**，不是 50：

- `backend/app/models.py:75-86` — `max_length=255`
- `backend/app/alembic/versions/9c0a54914c78_*.py` — DB `VARCHAR(255)`
- `frontend/src/client/schemas.gen.ts:76-80` — `maxLength: 255`
- 前端 `AddItem.tsx` / `EditItem.tsx` 只有必填校验，没有 max

若用户真实意图是 **255→100**，属于收紧约束，需 Alembic migration、regenerate client、前端 zod `.max(100)`，并处理超长存量数据。

## 卡点说明（已修复）

子任务中断时 D17 差两样东西：

1. **`010-requirements.md` 没写到磁盘**（`_active-state` 里写了「草稿」但文件缺失）→ validator V1 FAIL
2. **`_active-state.md` 验证结果是 `PLACEHOLDER`** → validator V18 FAIL

补全 `010-requirements.md` 并更新验证结果后，validator 已通过。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\python-fastapi-template\change-impact\item_title_max_length --mode full --repo-root E:\agent\real-project-fixtures\python-fastapi-template
```

- 退出码：`0`
- 摘要：`27 passed, 0 failed, 0 warnings`

## 产物

- `E:\agent\real-project-fixtures\python-fastapi-template\change-impact\item_title_max_length\`

## 未确认项

- 用户是否确认真实目标是 255→100（而非 50→100）
