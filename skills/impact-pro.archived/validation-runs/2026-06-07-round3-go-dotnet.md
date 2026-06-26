# impact-pro 第三轮验收总结（Go + .NET）

- 测试日期：2026-06-07
- 测试方式：真实开源项目静态验收 + 新增 profile glob dry-run
- 测试工作区：`E:\agent\impact-pro-validation-work`
- 基于变更：新增 `go-gin-gorm`、`dotnet-aspnet-efcore`，并增强 `generic`
- 结论：**后端技术栈覆盖扩大到 6 个用例，但仍未达到成熟通用投产门槛**

## 第三轮新增评分

| 用例 | 项目 | 分数 | 失败等级 | 结论 |
|------|------|------|----------|------|
| T04 Go/Gin/GORM | golang-gin-realworld-example-app | 87 | 无 | 有条件通过 |
| T05 ASP.NET Core/EF Core | eShopOnWeb | 86 | 无 | 有条件通过 |

## 当前累计评分

| 用例 | 分数 |
|------|------|
| T01 Java/Spring/MyBatis | 94 |
| T02 Node/Express/Prisma | 88 |
| T03 FastAPI/SQLModel | 89 |
| T04 Go/Gin/GORM | 87 |
| T05 ASP.NET Core/EF Core | 86 |
| T06 React/Vite | 88 |

累计平均分：`88.17`

当前状态：

- 已覆盖 6 个真实项目/子项目。
- 暂无 P0/P1/P2。
- 仍未达到 `VALIDATION.md` 的至少 10 个用例门槛。
- 负向测试尚未执行。
- Go 和 .NET 原生测试因本机缺 SDK 未执行。

## Go 样本结论

新增 `go-gin-gorm` 后，核心文件均可命中：

| 类型 | 命中文件 |
|------|----------|
| module | `go.mod` |
| models | `users/models.go`、`articles/models.go` |
| database | `common/database.go` |
| routers | `users/routers.go`、`articles/routers.go`、`hello.go` |
| serializers/validators | `serializers.go`、`validators.go` |
| tests | `users/unit_test.go`、`articles/unit_test.go`、`common/unit_test.go` |
| migration source | `hello.go` 中 `AutoMigrate` |

主要限制：

- 本机没有 Go SDK，未执行 `go test ./...`。
- AutoMigrate 场景的回滚策略必须人工确认。

## .NET 样本结论

新增 `dotnet-aspnet-efcore` 后，核心文件均可命中：

| 类型 | 命中文件 |
|------|----------|
| solution/project | `*.sln`、`*.csproj` |
| DbContext | `CatalogContext.cs`、`AppIdentityDbContext.cs` |
| entity | `src/ApplicationCore/Entities/**/*.cs` |
| repository | `EfRepository.cs`、`IRepository.cs` |
| endpoint/controller | `*Endpoint.cs`、`*Controller.cs` |
| request/response | `*Request.cs`、`*Response.cs` |
| migrations | `src/Infrastructure/**/Migrations/*.cs` |
| tests | `tests/**/*.cs` |

主要限制：

- 本机没有 .NET SDK，未执行 `dotnet test`。
- 多项目 solution 需要执行时先锁定目标项目、DbContext 和 API 层。

## 投产判断

当前判定：

```text
impact-pro = 多栈可试用版，仍不是成熟通用版。
```

相比第二轮，通用性更真了一些：不再只是 Java + Node/Python/React，而是覆盖到 Go 和 .NET 两个风格差异很大的后端生态。

但还不能完成目标，原因：

- 只有 6/10 个用例。
- 缺 Vue/Nuxt/Next.js、monorepo 和负向测试。
- 缺少 Go/.NET 原生测试执行证据。
- 尚未模拟完整 agent 对话中的“写操作逐项确认”。

## 下一轮建议

第四轮优先补：

1. Vue/Nuxt profile 或 Next.js profile，扩大前端覆盖。
2. Monorepo 用例，验证多 profile 协作。
3. 负向测试三件套：
   - 用户要求直接删除旧接口。
   - 证据不足的状态枚举变更。
   - 无 DB 权限的字段变更。

目标：达到至少 10 个用例，平均分 >= 85，无 P0/P1。
