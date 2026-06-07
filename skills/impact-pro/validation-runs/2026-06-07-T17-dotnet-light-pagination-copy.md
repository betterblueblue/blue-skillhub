# T17 eShopOnWeb - Catalog 分页展示文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：ASP.NET Core / Razor Pages / EF Core
- 项目路径：`E:\agent\impact-pro-validation-work\eShopOnWeb`
- 变更意图：调整 Catalog 分页区域的展示文案，例如 `Showing X of Y products`，不改分页算法。
- 使用档位：light
- 命中 profile：`dotnet-aspnet-efcore`
- 最终评分：88
- 失败等级：无

## 实际发现

关键文件：

- `src/Web/Pages/Shared/_pagination.cshtml`：分页链接、`Previous` / `Next`、展示文案和 `aria-label`。
- `src/Web/ViewModels/PaginationInfoViewModel.cs`：分页信息字段。
- `src/Web/Services/CatalogViewModelService.cs`：`ActualPage`、`ItemsPerPage`、`TotalPages`、`Previous`、`Next` 的计算来源。
- `tests/FunctionalTests/Web/Controllers/CatalogControllerIndex.cs`：首页商品列表功能测试。

## 验收判断

应判定 light。

理由：

- 不改 EF Core Entity、DbContext、Migration。
- 不改分页计算、缓存 key、查询条件。
- 只改 Razor partial 展示文案，可用功能测试或快照/页面断言验证。

## 风险追问

1. 是否只改中间展示文本，还是同步 `Previous`/`Next` 和 `aria-label`？
2. 是否需要本地化资源，而不是硬编码英文？
3. 是否有页面测试断言原始文案？

## 验证方案

- Razor 页面功能测试或 `dotnet test` 中 Web FunctionalTests。
- 正向：首页仍显示商品列表和分页区域。
- 错误/边界：无结果页仍显示 no results 文案；第一页/末页 disabled class 不变。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | eShopOnWeb 同时有 EF Core 和 Razor UI | `CatalogViewModelService` 使用 repository，但 `_pagination.cshtml` 只渲染文案 | profile 需按变更点限制上下文，不因项目有 EF Core 就生成 migration |

## 结论

通过（light）。该用例补充 .NET/EF Core 样本第二变更，验证 profile 能识别 Razor UI-only 变更并避免过度分析数据库。
