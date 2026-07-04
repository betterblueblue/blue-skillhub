# D16 — PROJECT_NAME → APP_NAME 影响分析（Composer 2.5 Fast）

## 结论

判定为 **full**。`PROJECT_NAME` 不只在 `backend/app/core/config.py` 一处，还牵动 FastAPI 标题（`main.py`）、邮件主题/正文（`utils.py`）、`.env`、README、`deployment.md`、Copier 生成链（`.copier/copier.yml`）等。只改 config.py 不够。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\python-fastapi-template\change-impact\project_name_to_app_name --mode full --repo-root E:\agent\real-project-fixtures\python-fastapi-template
```

- 退出码：`0`
- 摘要：`27 passed, 0 failed, 0 warnings`

## 产物

- `E:\agent\real-project-fixtures\python-fastapi-template\change-impact\project_name_to_app_name\`

## 未确认项

- 邮件 Jinja 模板键 `project_name` 是否一并改为 `app_name`
