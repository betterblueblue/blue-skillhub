# Round 14: 生产级项目复验第一轮

## 背景

长期目标第 4 条要求至少 2-3 个生产级项目复验通过。此前 T01-T21 多数是单项目首轮或模板级样本，不能直接等同生产级复验。本轮选择三个更接近生产复杂度的开源项目做 full 变更复验。

## 复验结果

| 用例 | 项目 | 栈 | 变更 | 复验类型 | 评分 | 结论 |
|------|------|----|------|----------|------|------|
| T22 | RuoYi-Vue | Java/Spring/MyBatis/Vue | 登录日志设备指纹 | 生产级 full + Maven compile | 93 | 通过 |
| T23 | eShopOnWeb | ASP.NET Core/EF Core | 订单来源字段 | 生产复杂度静态复验 | 88 | 有条件通过 |
| T24 | Go RealWorld | Go/Gin/GORM | 收藏审计 | 生产复杂度静态复验 | 88 | 有条件通过 |

平均分：`89.67`

P0/P1：无。

## 运行时证据

- RuoYi：`mvn -pl ruoyi-admin -am -DskipTests compile` 通过，`BUILD SUCCESS`。
- eShopOnWeb：本机只有 .NET runtime，无 .NET SDK，不能执行 `dotnet test`。
- Go RealWorld：本机没有 Go SDK，不能执行 `go test ./...`。

## 阶段结论

```text
生产级复验已有 1 个完整通过 + 2 个有条件通过。
```

这证明 `impact-pro` 在更复杂项目上能继续做证据化影响分析，但还不能把长期目标第 4 条标为完全达到。原因是 eShopOnWeb 和 Go RealWorld 缺少原生命令运行时验证。

## 下一步

1. 在具备 .NET SDK 的环境复跑 eShopOnWeb：`dotnet test`。
2. 在具备 Go SDK 的环境复跑 Go RealWorld：`go test ./...`。
3. 再补 1 个带真实前后端联动或权限/支付/订单状态的生产级项目，使第 4 条从“部分达到”升级为“达到”。
