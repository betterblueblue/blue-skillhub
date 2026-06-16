# T05 eShopOnWeb - CatalogItem 唯一字段/API 变更

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：.NET / ASP.NET Core / EF Core / Clean Architecture
- 项目路径：`E:\agent\impact-pro-validation-work\eShopOnWeb`
- Commit：`4da8212117e87d808d4bbc7da6286fd2147ce606`
- 变更意图：给 CatalogItem 增加业务字段或唯一约束，并在 PublicApi 创建、编辑、详情接口支持。
- 使用档位：full
- 命中 profile：`dotnet-aspnet-efcore`
- 最终评分：86
- 失败等级：无

## 实际发现

### 技术栈检测

命中证据：

- 根目录存在 `eShopOnWeb.sln` 和 `Everything.sln`。
- 存在多个 `.csproj`。
- `Directory.Packages.props` 包含 `Microsoft.EntityFrameworkCore.*`、`Microsoft.AspNetCore.*`、`Microsoft.EntityFrameworkCore.Tools`。
- 存在 `src/Infrastructure/Data/CatalogContext.cs` 和 EF Core migrations。

应加载 `profiles/dotnet-aspnet-efcore.md`。

### 上下文发现

新 profile 命中结果：

| 类型 | 命中文件 |
|------|----------|
| Solution | `eShopOnWeb.sln`、`Everything.sln` |
| Projects | `src/*/*.csproj`、`tests/*/*.csproj` |
| DbContext | `src/Infrastructure/Data/CatalogContext.cs`、`src/Infrastructure/Identity/AppIdentityDbContext.cs` |
| Entity | `src/ApplicationCore/Entities/CatalogItem.cs` 等 |
| Repository | `src/Infrastructure/Data/EfRepository.cs`、`src/ApplicationCore/Interfaces/IRepository.cs` |
| API endpoint | `src/PublicApi/CatalogItemEndpoints/*Endpoint.cs` |
| Request/Response | `*Request.cs`、`*Response.cs` |
| Migrations | `src/Infrastructure/Data/Migrations/*.cs`、`src/Infrastructure/Identity/Migrations/*.cs` |
| Tests | `tests/**/*Tests/**/*.cs`、integration/functional/public API tests |
| Config | `appsettings*.json`、`Directory.Packages.props` |

关键证据：

- `CatalogContext` 继承 `DbContext`，定义 `DbSet<CatalogItem>`、`DbSet<Order>` 等。
- `CatalogItem` 是领域实体，构造函数和 `UpdateDetails` 使用 GuardClauses。
- `CreateCatalogItemEndpoint` 使用 MinimalApi.Endpoint，验证重复名称并调用 repository。
- 测试项目覆盖 PublicApi、Integration、Functional、Unit 多层。

### 风险追问

应追问：

1. 新字段属于 CatalogItem entity、DTO、Request/Response 哪些层？
2. 是否需要 EF Core migration，目标 context 是 `CatalogContext` 还是 `AppIdentityDbContext`？
3. 唯一约束是否在 DB 层、领域层、API 层都校验？
4. PublicApi、BlazorShared、Web ViewModel 是否都要同步？
5. 现有测试应补 PublicApiIntegrationTests、IntegrationTests 还是 UnitTests？

### 定级

应判定 full。

理由：

- 涉及 EF Core entity 和 migration。
- 涉及 PublicApi Endpoint、Request/Response/DTO。
- 涉及 repository/specification/领域规则。
- 涉及多测试项目。

## 原生命令执行

尝试执行：

```powershell
dotnet test --no-restore
```

结果：本机没有 .NET SDK。

```text
No .NET SDKs were found.
```

因此本轮只完成 profile 静态验收，未完成 .NET 测试套件执行。

## 评分

| 维度 | 分值 | 得分 | 说明 |
|------|------|------|------|
| 技术栈检测与 profile 选择 | 15 | 15 | ASP.NET/EF Core 证据明确 |
| 上下文发现 | 20 | 18 | DbContext/entity/endpoint/test/migration 均命中 |
| 风险识别与追问 | 20 | 17 | 能覆盖 context、migration、DTO、tests |
| light/full 定级 | 10 | 10 | full 明确 |
| 文档质量 | 15 | 12 | 多项目 solution 需更强模块分区 |
| 执行安全 | 10 | 10 | 写操作确认规则存在 |
| 验证设计 | 10 | 6 | 缺少本机 dotnet test 执行证据 |

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | 本机无法执行 .NET 测试 | 无 .NET SDK | 在 .NET SDK 环境复跑 `dotnet test` |
| P3 | 多项目 solution 容易读太多文件 | eShopOnWeb 包含 Web/PublicApi/Blazor/Infrastructure/tests | profile 执行时需按变更目标先锁定项目/上下文 |

## 结论

有条件通过。`dotnet-aspnet-efcore` profile 可作为 Level 1 使用，但需在 .NET SDK 环境复跑真实测试。
