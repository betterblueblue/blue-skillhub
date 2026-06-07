# Round 16: Docker 运行时复验补强

## 背景

Round 14 中 eShopOnWeb 和 Go RealWorld 因本机缺少 .NET SDK / Go SDK，只能标为有条件通过。用户启动 Docker Desktop 后，本轮使用 SDK 容器补运行时证据，避免全局安装 SDK。

## Docker 状态

`docker ps` 成功，Docker daemon 可用。

## eShopOnWeb

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

补充观察：

- 测试期间出现 `System.Text.Json` 高危 advisory 和 `Azure.Identity` 中危 advisory。
- 出现若干 `xUnit2013` analyzer warning。
- 这些属于项目依赖治理风险，不是 impact-pro profile 发现失败。

## Go RealWorld

执行命令：

```powershell
docker run --rm -v "E:/agent/impact-pro-validation-work/go-gin-realworld:/src" -w /src golang:1.21 bash -lc "/usr/local/go/bin/go test ./..."
```

结果：部分通过，全量失败。

```text
ok   github.com/gothinkster/golang-gin-realworld-example-app/articles
ok   github.com/gothinkster/golang-gin-realworld-example-app/users
FAIL github.com/gothinkster/golang-gin-realworld-example-app/common
```

失败点：

```text
common/unit_test.go:39
Error: An error is expected but got nil.
Messages: Db should not be able to ping
```

T24 收藏审计直接相关的 `articles` 包已通过；全量失败来自 `common` 包数据库连接期望。该失败需要后续单独分析是测试环境前置条件还是项目既有断言问题。

## 结论

```text
生产级复验从 1 个完整通过 + 2 个有条件通过，提升到 2 个完整通过 + 1 个有条件通过。
```

长期目标第 4 条“至少 2-3 个生产级项目复验通过”已达到最低门槛，但整体目标仍保持 active：Go 全量测试、Next.js 完整 build、更多生产级样本和执行阶段门禁仍需要继续积累证据。
