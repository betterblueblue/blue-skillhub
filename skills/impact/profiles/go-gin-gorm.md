# Go / Gin / GORM Profile

> Level 2 — 在 gothinkster/golang-gin-realworld-example-app 和 go-admin 等项目上完成多轮验收。适用于 Go + Gin + GORM 后端项目。

## 基本信息

```yaml
name: go-gin-gorm
level: 2
matchers:
  files:
    - go.mod
  dependencies:
    - github.com/gin-gonic/gin
    - gorm.io/gorm
    - gorm.io/driver
  directories:
    - api
    - common
    - users
    - articles
roles:
  - Go API 服务
  - REST API
  - GORM 数据服务
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/*service*.go"
    - "**/*Service*.go"
    - "**/services/**/*.go"
    - "**/usecase/**/*.go"
  data_access:
    - "**/models.go"
    - "**/*model*.go"
    - "**/*repository*.go"
    - "**/*Repository*.go"
    - "**/common/database.go"
    - "**/database.go"
  api:
    - "**/routers.go"
    - "**/*router*.go"
    - "**/*handler*.go"
    - "**/*Handler*.go"
    - "**/hello.go"
    - "**/main.go"
    - "**/cmd/**/*.go"
  entity:
    - "**/models.go"
    - "**/*model*.go"
  dto:
    - "**/serializers.go"
    - "**/*serializer*.go"
    - "**/validators.go"
    - "**/*validator*.go"
  config:
    - "**/go.mod"
    - "**/go.sum"
    - "**/.env.example"
    - "**/.golangci.yml"
    - "**/docker-compose*.yml"
  test:
    - "**/*_test.go"
    - "**/unit_test.go"
  migration:
    - "**/migrations/**/*.sql"
    - "**/db/**/*.sql"
  ui: []  # 纯后端栈，无前端 UI 层
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "go.mod"
    - "go.sum"
    - ".env.example"
    - "docker-compose*.yml"
  entrypoints:
    - "**/routers.go"
    - "**/*router*.go"
    - "**/*handler*.go"
    - "**/*Handler*.go"
    - "**/hello.go"
    - "**/main.go"
    - "**/cmd/**/*.go"
  data_models:
    - "**/models.go"
    - "**/*model*.go"
    - "**/serializers.go"
    - "**/*serializer*.go"
    - "**/validators.go"
    - "**/*validator*.go"
    - "**/migrations/**/*.sql"
    - "**/db/**/*.sql"
  dependency_paths:
    - "**/*service*.go"
    - "**/*Service*.go"
    - "**/services/**/*.go"
    - "**/usecase/**/*.go"
    - "**/*repository*.go"
    - "**/*Repository*.go"
    - "**/common/database.go"
    - "**/database.go"
  tests:
    - "**/*_test.go"
    - "**/unit_test.go"
  configs:
    - "**/go.mod"
    - "**/go.sum"
    - "**/.env.example"
    - "**/.golangci.yml"
    - "**/docker-compose*.yml"
  exclude_patterns:
    - "**/vendor/**"
    - "**/tmp/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 结论需运行时从代码现采，下列为常见模式提示。

| 轴 | 常见模式 | 说明 |
|----|---------|------|
| naming | Go 包名小写、struct 名驼峰、receiver 单字母、JSON/GORM tag 下划线 | GORM tag `gorm:"column:xxx"` 控制列名映射 |
| layering | routers.go → validators/serializers → models.go/data access | 部分项目无 service 层，handler 直接调 repository |
| orm | GORM model、gorm.Model 嵌入（含 ID/CreatedAt/UpdatedAt/DeletedAt）、AutoMigrate、Preload、Association | `gorm.Model` 含软删除字段 `DeletedAt`，查询默认过滤已删除记录 |
| transaction | `db.Begin()` → `tx.Commit()` / `tx.Rollback()`；或 `db.Transaction(func(tx *gorm.DB) error {...})` | 事务回调形式更常见，自动 commit/rollback |
| exception | Gin `c.JSON(status, gin.H{})`、统一错误结构（code+msg+data）；`errors.Is/As` 判断特定错误 | Go 无异常机制，error 作为返回值传播 |
| logging | gin.Default（含 Logger+Recovery）、自定义 logger、GORM logger 配置 | 生产环境常替换为 zap/zerolog |
| api_response | serializer 返回结构、gin.H 快速构造、统一 Response 包装 | 分页用单独结构体或通用 Page |
| dependency_injection | 全局 DB 变量、context 注入、handler 闭包注入、Gin middleware 注入 | `c.MustGet("db")` 从 context 取依赖 |
| error_handling | `if err != nil` 贯穿、`errors.New`/`fmt.Errorf` 创建错误、`errors.Is/As` 判断 | Go 1.13+ 错误包装：`fmt.Errorf("xxx: %w", err)` |
| context_propagation | `context.Context` 作为函数首参、`c.Request.Context()` 从 Gin 取、超时/取消传播 | DB 操作应传入 context 以支持超时 |
| middleware | `r.Use(middleware)`、JWT auth middleware、CORS、Recovery、Logger | middleware 顺序影响行为 |

## commands

```yaml
commands:
  build: go build ./...
  test: go test ./...
  dev: go run .
  lint: golangci-lint run
```

容器复验注意：如果测试包含文件权限断言（如 `chmod 0000` 后期望 DB 连接失败），不要用 root 容器用户直接判断；优先使用非 root 用户、临时 `DB_PATH` / `TEST_DB_PATH`，必要时用 `go test -p 1 ./...` 避免包间共享测试库互相污染。

## db_introspection

```yaml
db_introspection:
  orm: GORM
  migration_tool: AutoMigrate 或项目自定义迁移
  schema_source: 见 models.go + AutoMigrate 调用（代码级 schema 发现路径）；默认 db-adapter 由 GORM 驱动决定（sqlite → generic-sql.md / postgres → postgresql.md / mysql → mysql.md），运行时 DB 类型探测可覆盖
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "gorm\\.Model|gorm:\""
      files: "**/*.go"
      desc: "GORM model 定义"
    - pattern: "AutoMigrate"
      files: "**/*.go"
      desc: "自动迁移入口"
    - pattern: "gin\\.Default|gin\\.New|Group\\("
      files: "**/*.go"
      desc: "Gin 路由注册"
    - pattern: "c\\.JSON"
      files: "**/*.go"
      desc: "API 响应格式"
    - pattern: "db\\.Begin|tx\\.Commit|tx\\.Rollback|db\\.Transaction"
      files: "**/*.go"
      desc: "事务处理"
    - pattern: "errors\\.Is|errors\\.As|fmt\\.Errorf.*%w"
      files: "**/*.go"
      desc: "错误处理模式"
    - pattern: "context\\.Context|c\\.Request\\.Context"
      files: "**/*.go"
      desc: "Context 传播"
    - pattern: "r\\.Use|router\\.Use|engine\\.Use"
      files: "**/*.go"
      desc: "中间件注册"
    - pattern: "gorm:\"column:|gorm:\"type:|gorm:\"default:"
      files: "**/*.go"
      desc: "GORM 字段标签"
    - pattern: "soft delete|DeletedAt|gorm\\.Model"
      files: "**/*.go"
      desc: "软删除模式"
  file_patterns:
    - "**/*.go"
    - "**/*_test.go"
    - "**/.env.example"
```

## notes

```yaml
notes:
  limitations:
    - AutoMigrate 只能新增列/表/索引，不能删除列或修改列类型——回滚需手动 SQL
    - GORM tag 不等同真实 DB schema，需结合 AutoMigrate/迁移/数据库自省
    - Go 项目目录差异较大，monorepo 或 clean architecture 需先定位模块根目录
    - 认证中间件常在 middleware 或 router 注册处，权限影响需单独扫描
  edge_cases:
    - models.go 可能同时包含 DB 操作和业务逻辑
    - GORM 软删除（gorm.Model.DeletedAt）使查询默认过滤已删除记录，需 `Unscoped()` 查全部
    - GORM hooks（BeforeCreate/AfterUpdate 等）可能包含隐藏副作用，变更时需扫描
    - GORM Preload 关联加载可能导致 N+1 查询，需检查 `Preload` 调用
    - 多数据源项目：`*gorm.DB` 实例可能按模块隔离，变更时确认目标 DB
    - AutoMigrate 项目没有显式迁移文件，回滚方案必须人工确认
    - GORM `gorm.Expr` 动态表达式可能引入 SQL 注入风险
  failure_preconditions:
    - 修改 GORM struct tag（如 column/type/default）等同于 ALTER TABLE，属高风险
    - 删除 struct 字段不会自动删 DB 列（AutoMigrate 不删列），但会导致 ORM 映射失效
    - 修改 `gorm.Model` 嵌入行为会影响所有继承它的 model
  common_misjudgments:
    - GORM tag `gorm:"-"` 表示不映射 DB 列，不要误认为是删除列
    - `gorm:"column:xxx"` 是列名映射不是列定义，改 tag 不改 DB schema
    - Go 的 `init()` 函数可能执行 DB 初始化或数据迁移，变更时需检查
```
