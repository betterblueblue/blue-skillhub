# Go / Gin / GORM Profile

> Level 1 — 在 `gothinkster/golang-gin-realworld-example-app` 上完成首轮验收。适用于 Go + Gin + GORM 后端项目。

## 基本信息

```yaml
name: go-gin-gorm
level: 1
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
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | Go 包名、struct 名、receiver 命名、JSON/GORM tag |
| layering | routers.go → validators/serializers → models.go/data access |
| orm | GORM model、gorm.Model、AutoMigrate、Preload、Association |
| transaction | `db.Begin()`、`tx.Commit()`、`tx.Rollback()` |
| exception | Gin status code、`c.JSON`、统一错误结构 |
| logging | gin.Default、自定义 logger、GORM logger |
| api_response | serializer 返回结构、gin.H、JSON 包装 |
| dependency_injection | 全局 DB、context 注入、handler 闭包注入 |
```

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
  schema_source: models.go + AutoMigrate 调用；无 DB 直连时只做代码级 schema 发现
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
    - pattern: "db\\.Begin|tx\\.Commit|tx\\.Rollback"
      files: "**/*.go"
      desc: "事务处理"
  file_patterns:
    - "**/*.go"
    - "**/*_test.go"
    - "**/.env.example"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 Gin + GORM + SQLite 样本验证，PostgreSQL/MySQL 迁移工具需继续验证
    - Go 项目目录差异较大，monorepo 或 clean architecture 需先定位模块根目录
    - AutoMigrate 项目没有显式迁移文件，回滚方案必须人工确认
  edge_cases:
    - `models.go` 可能同时包含 DB 操作和业务逻辑
    - GORM tag 不等同真实 DB schema，需结合 AutoMigrate/迁移/数据库自省
    - 认证中间件常在 middleware 或 router 注册处，权限影响需单独扫描
```
