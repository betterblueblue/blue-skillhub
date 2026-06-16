# Round 14: 生产级项目复验第一轮

## 背景

长期目标第 4 条要求至少 2-3 个生产级项目复验通过。此前 T01-T21 多数是单项目首轮或模板级样本，不能直接等同生产级复验。本轮选择三个更接近生产复杂度的开源项目做 full 变更复验。

## 复验结果

| 用例 | 项目 | 栈 | 变更 | 复验类型 | 评分 | 结论 |
|------|------|----|------|----------|------|------|
| T22 | RuoYi-Vue | Java/Spring/MyBatis/Vue | 登录日志设备指纹 | 生产级 full + Maven compile | 93 | 通过 |
| T23 | eShopOnWeb | ASP.NET Core/EF Core | 订单来源字段 | 生产级 full + Docker .NET test | 92 | 通过 |
| T24 | Go RealWorld | Go/Gin/GORM | 收藏审计 | 生产级 full + Docker Go 全量测试 | 89 | 通过 |

平均分：`91.33`

P0/P1：无。

## 运行时证据

- RuoYi：`mvn -pl ruoyi-admin -am -DskipTests compile` 通过，`BUILD SUCCESS`。
- eShopOnWeb：Docker `.NET SDK 8.0` 执行 `dotnet test eShopOnWeb.sln -v minimal` 通过，Unit/Integration/Functional/PublicApiIntegration 共 74 个测试通过。
- Go RealWorld：Docker `golang:1.21` 在非 root、临时 DB、`-p 1` 串行包前置条件下执行 `/usr/local/go/bin/go test -p 1 ./...` 通过；默认 root 容器会使 `common/unit_test.go:39` 权限断言失真。

## 阶段结论

```text
生产级复验已有 3 个完整通过。
```

这证明 `impact-pro` 在更复杂项目上能继续做基于证据的影响分析。长期目标第 4 条已达到，但整体目标仍不能标记完成：Next.js 完整 build、更多生产级样本和执行阶段安全闸仍需要继续积累证据。

## 下一步

1. 再补 1-2 个带真实前后端联动或权限/支付/订单状态的生产级项目，提高第 4 条证据余量。
2. 将 Go RealWorld 的非 root、临时 DB、串行包执行前置条件写入后续 profile 运行建议，避免 root 容器误判。
3. 将 eShopOnWeb 的包安全告警记录为生产治理风险，不归因于 impact-pro profile。
