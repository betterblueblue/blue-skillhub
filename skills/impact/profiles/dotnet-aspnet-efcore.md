# .NET / ASP.NET Core / EF Core Profile

> Level 1 — 在 `dotnet-architecture/eShopOnWeb` 上完成首轮验收。适用于 ASP.NET Core + Entity Framework Core 项目。

## 基本信息

```yaml
name: dotnet-aspnet-efcore
level: 1
matchers:
  files:
    - "*.sln"
    - "*.csproj"
    - Directory.Packages.props
  dependencies:
    - Microsoft.EntityFrameworkCore
    - Microsoft.AspNetCore
    - Microsoft.EntityFrameworkCore.SqlServer
    - Microsoft.EntityFrameworkCore.Tools
  directories:
    - src
    - tests
roles:
  - ASP.NET Core API/Web 应用
  - EF Core 数据服务
  - 多项目 solution
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/Services/**/*.cs"
    - "**/*Service.cs"
    - "**/*Handler.cs"
    - "**/Features/**/*.cs"
    - "**/Interfaces/**/*.cs"
  data_access:
    - "**/*DbContext.cs"
    - "**/*Context.cs"
    - "**/Infrastructure/**/*.cs"
    - "**/*Repository.cs"
    - "**/Data/**/*.cs"
  api:
    - "**/Controllers/**/*.cs"
    - "**/*Controller.cs"
    - "**/*Endpoint.cs"
    - "**/*Endpoints/**/*.cs"
    - "**/Pages/**/*.cshtml.cs"
    - "**/Program.cs"
  entity:
    - "**/Entities/**/*.cs"
    - "**/*Entity.cs"
    - "**/ApplicationCore/**/*.cs"
  dto:
    - "**/*Request.cs"
    - "**/*Response.cs"
    - "**/*Dto.cs"
    - "**/Models/**/*.cs"
    - "**/ViewModels/**/*.cs"
  config:
    - "**/*.sln"
    - "**/*.csproj"
    - "**/Directory.Packages.props"
    - "**/appsettings*.json"
    - "**/docker-compose*.yml"
    - "**/global.json"
  test:
    - "**/tests/**/*.cs"
    - "**/*Tests/**/*.cs"
    - "**/*Test.cs"
  migration:
    - "**/Migrations/**/*.cs"
    - "**/*Migration*.cs"
  ui: []  # 纯后端栈，无前端 UI 层
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "*.sln"
    - "*.csproj"
    - "Directory.Packages.props"
    - "global.json"
  entrypoints:
    - "**/Controllers/**/*.cs"
    - "**/*Controller.cs"
    - "**/*Endpoint.cs"
    - "**/*Endpoints/**/*.cs"
    - "**/Pages/**/*.cshtml.cs"
    - "**/Program.cs"
  data_models:
    - "**/Entities/**/*.cs"
    - "**/*Entity.cs"
    - "**/ApplicationCore/**/*.cs"
    - "**/*Request.cs"
    - "**/*Response.cs"
    - "**/*Dto.cs"
    - "**/Models/**/*.cs"
    - "**/ViewModels/**/*.cs"
    - "**/Migrations/**/*.cs"
  dependency_paths:
    - "**/Services/**/*.cs"
    - "**/*Service.cs"
    - "**/*Handler.cs"
    - "**/Features/**/*.cs"
    - "**/Interfaces/**/*.cs"
    - "**/*DbContext.cs"
    - "**/*Context.cs"
    - "**/Infrastructure/**/*.cs"
    - "**/*Repository.cs"
    - "**/Data/**/*.cs"
  tests:
    - "**/tests/**/*.cs"
    - "**/*Tests/**/*.cs"
    - "**/*Test.cs"
  configs:
    - "**/*.sln"
    - "**/*.csproj"
    - "**/Directory.Packages.props"
    - "**/appsettings*.json"
    - "**/docker-compose*.yml"
    - "**/global.json"
  exclude_patterns:
    - "**/bin/**"
    - "**/obj/**"
    - "**/TestResults/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件确认。

| 轴 | 观察方向 |
|----|----------|
| naming | C# PascalCase、async 方法后缀、Request/Response/Dto 命名 |
| layering | Web/PublicApi → ApplicationCore → Infrastructure → tests |
| orm | DbContext、DbSet、Fluent API、EF Core migration |
| transaction | Unit of Work、SaveChangesAsync、显式 transaction |
| exception | middleware、ProblemDetails、endpoint response、ModelState |
| logging | ILogger<T>、Serilog、LoggerAdapter |
| api_response | Controller/Endpoint 返回类型、BaseResponse、Result pattern |
| dependency_injection | Program.cs、ConfigureServices、constructor injection |

## commands

```yaml
commands:
  build: dotnet build
  test: dotnet test
  dev: dotnet run --project src/Web
  lint: dotnet format --verify-no-changes
```

## db_introspection

```yaml
db_introspection:
  orm: Entity Framework Core
  migration_tool: EF Core Migrations
  schema_source: 见 DbContext + Entities + Migrations（代码级 schema 发现路径）；默认 db-adapter 由 EF Core provider 决定（SqlServer → 暂无 sqlserver adapter，降级 generic-sql.md / Postgres → postgresql.md / MySQL → mysql.md），运行时 DB 类型探测可覆盖
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "DbContext|DbSet<"
      files: "**/*.cs"
      desc: "EF Core context 和 DbSet"
    - pattern: "IRepository|EfRepository"
      files: "**/*.cs"
      desc: "Repository 模式"
    - pattern: "Controller|Endpoint"
      files: "**/*.cs"
      desc: "HTTP 入口"
    - pattern: "SaveChangesAsync|AddAsync|Update"
      files: "**/*.cs"
      desc: "数据写入方式"
    - pattern: "Fact|Theory|Test"
      files: "**/tests/**/*.cs"
      desc: "测试覆盖"
  file_patterns:
    - "**/*.cs"
    - "**/*.csproj"
    - "**/appsettings*.json"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 eShopOnWeb 的 Clean Architecture 样本验证，极简 Web API 项目需继续验证
    - Minimal API、Razor Pages、Controller、Endpoint class 可能并存，需按项目确认
    - 无数据库连接时不能确认真实索引、约束和迁移应用状态
  edge_cases:
    - 多 DbContext 项目：必须确认目标 context，如 CatalogContext/AppIdentityDbContext
    - DTO、ViewModel、Entity 可能分散在多个项目，不能只扫 Web 层
    - EF migration 目录可能在 Infrastructure/Data/Migrations 或 Identity/Migrations
```
