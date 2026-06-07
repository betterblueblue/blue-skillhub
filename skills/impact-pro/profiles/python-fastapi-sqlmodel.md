# Python / FastAPI / SQLModel Profile

> Level 1 — 在 `fastapi/full-stack-fastapi-template/backend` 上完成首轮验收。适用于 FastAPI + SQLModel/SQLAlchemy + Alembic 项目。

## 基本信息

```yaml
name: python-fastapi-sqlmodel
level: 1
matchers:
  files:
    - pyproject.toml
    - requirements.txt
    - alembic.ini
  dependencies:
    - fastapi
    - sqlmodel
    - sqlalchemy
    - alembic
    - pytest
  directories:
    - app
    - app/api
    - app/api/routes
    - app/alembic
    - tests
roles:
  - FastAPI 后端服务
  - REST API
  - SQLModel/SQLAlchemy 数据服务
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/app/services/**/*.py"
    - "**/app/*service*.py"
    - "**/app/crud.py"
    - "**/app/crud/**/*.py"
  data_access:
    - "**/app/models.py"
    - "**/app/models/**/*.py"
    - "**/app/db.py"
    - "**/app/core/db.py"
    - "**/app/crud.py"
    - "**/app/alembic/**/*.py"
    - "**/alembic.ini"
  api:
    - "**/app/main.py"
    - "**/app/api/main.py"
    - "**/app/api/routes/**/*.py"
    - "**/app/api/deps.py"
    - "**/app/routers/**/*.py"
  entity:
    - "**/app/models.py"
    - "**/app/models/**/*.py"
    - "**/app/schemas.py"
    - "**/app/schemas/**/*.py"
  dto:
    - "**/app/schemas.py"
    - "**/app/schemas/**/*.py"
    - "**/app/models.py"
  config:
    - "**/pyproject.toml"
    - "**/requirements.txt"
    - "**/app/core/config.py"
    - "**/alembic.ini"
    - "**/Dockerfile"
    - "**/compose*.yml"
  test:
    - "**/tests/**/*.py"
    - "**/test/**/*.py"
  migration:
    - "**/app/alembic/versions/**/*.py"
    - "**/alembic/versions/**/*.py"
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "pyproject.toml"
    - "requirements.txt"
    - "alembic.ini"
    - "Dockerfile"
    - "compose*.yml"
  entrypoints:
    - "**/app/main.py"
    - "**/app/api/main.py"
    - "**/app/api/routes/**/*.py"
    - "**/app/api/deps.py"
    - "**/app/routers/**/*.py"
  data_models:
    - "**/app/models.py"
    - "**/app/models/**/*.py"
    - "**/app/schemas.py"
    - "**/app/schemas/**/*.py"
    - "**/app/alembic/versions/**/*.py"
    - "**/alembic/versions/**/*.py"
  dependency_paths:
    - "**/app/services/**/*.py"
    - "**/app/*service*.py"
    - "**/app/crud.py"
    - "**/app/crud/**/*.py"
    - "**/app/db.py"
    - "**/app/core/db.py"
  tests:
    - "**/tests/**/*.py"
    - "**/test/**/*.py"
  configs:
    - "**/pyproject.toml"
    - "**/requirements.txt"
    - "**/app/core/config.py"
    - "**/alembic.ini"
  exclude_patterns:
    - "**/__pycache__/**"
    - "**/.pytest_cache/**"
    - "**/.ruff_cache/**"
    - "**/.venv/**"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | Pydantic/SQLModel 类名、字段 snake_case、路由函数命名 |
| layering | `app/api/routes` → `crud.py/services` → `models.py` → Alembic |
| orm | SQLModel table、SQLAlchemy Field、Relationship、Alembic revision |
| transaction | SessionDep 注入、session.add/commit/refresh、rollback 策略 |
| exception | `HTTPException` 状态码和 detail 文案 |
| logging | logging/sentry/print 禁用规则 |
| api_response | response_model、Public/Create/Update 模型分离 |
| dependency_injection | FastAPI Depends、SessionDep、CurrentUser 注入 |

## commands

```yaml
commands:
  build: python -m compileall app
  test: pytest tests/
  dev: fastapi dev app/main.py
  lint: ruff check app tests
```

## db_introspection

```yaml
db_introspection:
  orm: SQLModel / SQLAlchemy
  migration_tool: Alembic
  schema_source: app/models.py + app/alembic/versions；无 DB 直连时只做代码级 schema 发现
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "table=True"
      files: "**/app/models.py"
      desc: "SQLModel 数据表模型"
    - pattern: "response_model="
      files: "**/app/api/routes/**/*.py"
      desc: "API 响应模型"
    - pattern: "HTTPException"
      files: "**/app/api/routes/**/*.py"
      desc: "异常响应模式"
    - pattern: "alembic"
      files: "**/pyproject.toml"
      desc: "迁移工具依赖"
  file_patterns:
    - "**/app/models.py"
    - "**/app/api/routes/**/*.py"
    - "**/app/alembic/versions/**/*.py"
    - "**/tests/**/*.py"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 SQLModel 项目上验收，纯 SQLAlchemy declarative 项目需扩展
    - FastAPI 项目可能将 schema/model 分离到多个文件，需运行时确认
    - 无数据库连接时不能确认真实行数、索引和外键状态
  edge_cases:
    - `models.py` 同时承载 DB model 和 API schema，需要区分 `table=True`
    - response_model 可能返回计算字段，未必需要 DB 字段
    - 权限逻辑常在 deps.py 或 CurrentUser 中，需要纳入上下文
```
