# Python / FastAPI / SQLModel Profile

> Level 2 — 在 fastapi/full-stack-fastapi-template/backend 和多个 FastAPI 项目上完成多轮验收。适用于 FastAPI + SQLModel/SQLAlchemy + Alembic 项目。

## 基本信息

```yaml
name: python-fastapi-sqlmodel
level: 2
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
  ui: []  # 纯后端栈，无前端 UI 层
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
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 结论需运行时从代码确认，下列为常见模式提示。

| 轴 | 常见模式 | 说明 |
|----|---------|------|
| naming | Pydantic/SQLModel 类名驼峰、字段 snake_case、路由函数命名 `read_users`/`create_user` | FastAPI 路由函数名影响 OpenAPI operationId |
| layering | `app/api/routes` → `crud.py/services` → `models.py` → Alembic | full-stack-template 模式：routes → crud → model → migration |
| orm | SQLModel `table=True`、SQLAlchemy `Field`、`Relationship`、Alembic revision | SQLModel 同时是 Pydantic schema 和 ORM model |
| transaction | `SessionDep` 注入、`session.add/commit/refresh`、`session.rollback` | FastAPI 依赖注入管理 session 生命周期，自动 close |
| exception | `HTTPException(status_code, detail)`；自定义异常 + exception_handler | 统一错误响应结构（detail 字段） |
| logging | `logging.getLogger(__name__)`、sentry-sdk；生产禁用 print | 结构化日志推荐 structlog 或 loguru |
| api_response | `response_model=` 指定返回模型、Public/Create/Update 模型分离 | response_model 自动生成 OpenAPI schema 和验证输出 |
| dependency_injection | FastAPI `Depends()`、`SessionDep`、`CurrentUser` 注入 | `Annotated[Session, Depends(get_session)]` 是现代写法 |
| async_patterns | `async def` 路由、`async with` session、`await` DB 操作 | SQLAlchemy 2.0 async session 需 `AsyncSession`；SQLModel 对 async 支持有限 |
| settings_management | `pydantic-settings` BaseSettings、`.env` 文件、环境变量覆盖 | `Settings` 类集中管理配置，依赖注入暴露给路由 |
| model_separation | `UserBase` → `UserCreate`/`UserUpdate`/`UserPublic` 继承链 | Create 含密码、Public 不含密码；变更字段需同步多个子类 |

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
  schema_source: 见 app/models.py + app/alembic/versions（代码级 schema 发现路径）；默认 db-adapter 由 SQLAlchemy 连接串决定（sqlite → generic-sql.md / postgresql → postgresql.md / mysql → mysql.md），运行时 DB 类型探测可覆盖
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
    - pattern: "Depends\\(|Annotated\\[.*Depends"
      files: "**/app/api/**/*.py"
      desc: "依赖注入模式"
    - pattern: "async def|await "
      files: "**/app/api/routes/**/*.py"
      desc: "异步路由模式"
    - pattern: "BaseSettings|pydantic_settings"
      files: "**/app/core/config.py"
      desc: "配置管理"
    - pattern: "SessionDep|get_session|AsyncSession"
      files: "**/app/**/*.py"
      desc: "DB session 管理"
    - pattern: "model_validator|field_validator|@validator"
      files: "**/app/models.py"
      desc: "Pydantic 验证器"
    - pattern: "down_revision|revision ="
      files: "**/alembic/versions/**/*.py"
      desc: "Alembic 迁移链"
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
    - SQLModel 对 async session 支持有限，纯 SQLAlchemy async 项目需扩展
    - FastAPI 项目可能将 schema/model 分离到多个文件，需运行时确认
    - 无数据库连接时不能确认真实行数、索引和外键状态
    - migration head 判定必须读取文件确认 down_revision 链，不得按文件名排序推断；未读取前在 preflight 标注为前置条件
    - Alembic autogenerate 不检测所有变更类型（如数据迁移、列重命名、CheckConstraint 变更）
  edge_cases:
    - models.py 同时承载 DB model 和 API schema，需要区分 `table=True`
    - response_model 可能返回计算字段，未必需要 DB 字段
    - 权限逻辑常在 deps.py 或 CurrentUser 中，需要纳入上下文
    - SQLModel + SQLAlchemy 混用：部分 model 可能用纯 SQLAlchemy declarative_base
    - Alembic migration 可能包含数据迁移（`op.execute`），不是纯 schema 变更
    - Pydantic v2 的 model_validator 替代了 v1 的 @validator，行为不同
    - FastAPI 的 BackgroundTasks 可能含隐藏的写操作，变更时需扫描
    - `settings` 对象可能通过依赖注入暴露，修改配置键需检查所有引用
  failure_preconditions:
    - 修改 SQLModel model 定义（加/删/改字段、改 Field 约束）等同于 ALTER TABLE，属高风险
    - Alembic migration head 不唯一（多个 head revision）时，必须先合并 head 再新增迁移
    - 修改 response_model 可能破坏 API 契约（删除字段、改变类型）
    - 修改 deps.py 中的依赖注入函数影响所有使用该依赖的路由
  common_misjudgments:
    - `table=True` 的 SQLModel 才是 DB 表模型，不带 `table=True` 的是纯 Pydantic schema
    - Alembic 的 `revision` ID 是随机字符串，不能按文件名排序推断迁移顺序
    - FastAPI 的 `Depends()` 缓存在同一请求内，多次调用同一依赖只执行一次
    - `Session.commit()` 后对象变为 expired，再次访问属性会触发惰性加载——可能在 async 上下文中出错
```
