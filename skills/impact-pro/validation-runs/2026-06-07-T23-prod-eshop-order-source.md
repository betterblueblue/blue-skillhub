# T23 生产级复验 - eShopOnWeb 订单来源字段

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：.NET / ASP.NET Core / EF Core / Clean Architecture
- 项目路径：`E:\agent\impact-pro-validation-work\eShopOnWeb`
- Commit：`4da8212117e87d808d4bbc7da6286fd2147ce606`
- 变更意图：订单新增 `OrderSource` 字段，用于区分 Web、PublicApi、Admin 或外部导入订单，并在订单详情/列表展示。
- 使用档位：full
- 命中 profile：`dotnet-aspnet-efcore`
- 最终评分：92
- 失败等级：无
- 复验类型：生产级 full + Docker .NET SDK 测试复验

## 生产复杂度依据

eShopOnWeb 是分层 Clean Architecture 样例，包含 Web、PublicApi、BlazorAdmin、ApplicationCore、Infrastructure 和多层测试项目。订单变更触及 DDD aggregate、EF Core migration、owned value object、MVC controller、mediator handler、repository/specification 和测试。

## 证据账本

| 类型 | 证据 | 结论 |
|------|------|------|
| 已确认 | `eShopOnWeb.sln`、`Everything.sln`、`src/*/*.csproj`、`tests/*/*.csproj` | 多项目 solution |
| 已确认 | `src/Infrastructure/Data/CatalogContext.cs:18` | `DbSet<Order> Orders` 位于 `CatalogContext` |
| 已确认 | `src/ApplicationCore/Entities/OrderAggregate/Order.cs` | `Order` 是聚合根，构造函数控制写入 |
| 已确认 | `src/ApplicationCore/Services/OrderService.cs` | 下单入口创建 `Order` |
| 已确认 | `src/Web/Controllers/OrderController.cs` | `MyOrders` 和 `Detail` 展示订单 |
| 已确认 | `src/ApplicationCore/Specifications/CustomerOrdersWithItemsSpecification.cs`、`OrderWithItemsByIdSpec.cs` | 订单列表/详情查询通过 specification |
| 已确认 | `src/Infrastructure/Data/Config/OrderConfiguration.cs` | EF entity 配置集中管理订单映射 |
| 已确认 | `src/Infrastructure/Data/Migrations/*` | 现有 migrations 已包含 `Orders` 表和地址字段变更 |
| 已确认 | `tests/UnitTests/MediatorHandlers/OrdersTests/*`、`tests/IntegrationTests/Repositories/OrderRepositoryTests/*` | 有单元/集成测试入口 |
| 已确认 | Docker `mcr.microsoft.com/dotnet/sdk:8.0` 执行 `dotnet test eShopOnWeb.sln -v minimal` | Unit、Integration、Functional、PublicApiIntegration 测试均通过 |

## 判档

建议档位：full。

触发 full 的证据：

- EF Core entity 和 migration 变更。
- 订单聚合根与创建订单服务。
- Web 订单列表/详情展示。
- Specification/repository 查询。
- 存量订单默认值和测试数据 builder。

允许 light 的证据：无。

## 苏格拉底式追问

1. `OrderSource` 合法值是否需要 enum/value object，默认值如何处理历史订单？
2. 来源是在 Web 下单、PublicApi 下单还是后台导入处写入，是否要防止客户端伪造？
3. 列表/详情/API 是否都展示，是否需要筛选或报表统计？

## 验证方案

正向用例：

- Web 下单创建订单时写入 `OrderSource=Web`。
- 订单详情和我的订单列表返回/展示来源。
- Repository/specification 查询仍能正确包含订单项。

错误用例：

- 非法来源值被拒绝或不能绕过领域模型。
- 历史订单没有来源时展示默认值或空值策略一致。
- 未授权用户不能通过订单详情看到他人订单来源。

## 运行时验证

执行命令：

```powershell
docker run --rm -v "E:/agent/impact-pro-validation-work/eShopOnWeb:/src" -w /src mcr.microsoft.com/dotnet/sdk:8.0 bash -lc "dotnet test eShopOnWeb.sln -v minimal"
```

结果：通过。

```text
Passed!  - Failed: 0, Passed: 44, Skipped: 0, Total: 44 - UnitTests.dll
Passed!  - Failed: 0, Passed: 3, Skipped: 0, Total: 3 - IntegrationTests.dll
Passed!  - Failed: 0, Passed: 12, Skipped: 0, Total: 12 - FunctionalTests.dll
Passed!  - Failed: 0, Passed: 15, Skipped: 0, Total: 15 - PublicApiIntegrationTests.dll
```

注意：测试期间出现包安全告警和 xUnit analyzer warning，包括 `System.Text.Json` 高危 advisory、`Azure.Identity` 中危 advisory，以及若干 `xUnit2013` 建议。这些不是本轮 profile 识别失败，但应在真实项目治理中跟进。

## 结论

通过生产级复验。`dotnet-aspnet-efcore` profile 能在生产复杂度项目中定位订单聚合、EF 配置、migration、Web controller、specification 和测试入口，并已通过 Docker .NET SDK 测试复跑。
