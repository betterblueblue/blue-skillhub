# T24 生产级复验 - Go RealWorld 收藏审计

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Go / Gin / GORM / SQLite
- 项目路径：`E:\agent\impact-pro-validation-work\go-gin-realworld`
- Commit：`626c372d259472148d93303f74aa9b9a1cdcef24`
- 变更意图：文章收藏/取消收藏增加审计时间和来源，收藏列表与详情保持 `favorited`、`favoritesCount` 正确。
- 使用档位：full
- 命中 profile：`go-gin-gorm`
- 最终评分：89
- 失败等级：无
- 复验类型：生产复杂度静态复验 + Docker Go 相关包测试通过

## 生产复杂度依据

该项目实现 RealWorld API，包含用户、文章、评论、收藏、标签、认证和测试。收藏变更触及 GORM association、路由、serializer、批量计数、列表过滤和端点测试，能验证 Go/Gin/GORM profile 是否识别真实业务影响面。

## 分析依据

| 类型 | 证据 | 结论 |
|------|------|------|
| 已确认 | `go.mod` | Go 项目，依赖 Gin/GORM |
| 已确认 | `hello.go:15`-`:21` | `AutoMigrate` 覆盖 Article、Tag、Favorite、ArticleUser、Comment |
| 已确认 | `articles/models.go:31`-`:36` | `FavoriteModel` 连接文章和用户 |
| 已确认 | `articles/models.go:67`-`:83` | 单篇文章收藏数量和是否收藏查询 |
| 已确认 | `articles/models.go:86`-`:123` | 批量收藏数量和状态查询，影响列表性能 |
| 已确认 | `articles/models.go:128`-`:140` | `favoriteBy` / `unFavoriteBy` 写入和删除收藏 |
| 已确认 | `articles/routers.go:20`、`:149`-`:177` | 收藏/取消收藏 API 路由和 handler |
| 已确认 | `articles/serializers.go:48`-`:59`、`:93`-`:105` | 响应包含 `favorited` 和 `favoritesCount` |
| 已确认 | `articles/unit_test.go` 多处收藏测试 | 已有收藏正向、边界和端点测试入口 |
| 已确认 | Docker `golang:1.21` 执行 `/usr/local/go/bin/go test ./...` | `articles`、`users` 包通过；`common` 包存在既有测试失败 |

## 定级

建议档位：full。

触发 full 的证据：

- GORM model/AutoMigrate 变更。
- 收藏/取消收藏写操作。
- API 响应契约 `favorited`、`favoritesCount`。
- 列表批量计数和过滤性能。
- 测试覆盖需要更新。

允许 light 的证据：无。

## 苏格拉底式追问

1. 审计来源合法值是什么，是否已有常量/enum 约定？
2. 收藏/取消收藏都要记录审计，还是只记录最后一次收藏状态？
3. 历史收藏记录默认值和 AutoMigrate 生产回滚策略是什么？

## 验证方案

正向用例：

- 收藏文章后写入审计来源和时间。
- 取消收藏后 `favorited=false` 且 `favoritesCount` 减少。
- 文章列表批量返回收藏状态和数量正确。

错误用例：

- 重复收藏不会重复增加计数。
- 收藏不存在文章返回 404。
- 非法来源值被拒绝或标注为默认来源。

## 运行时验证

执行命令：

```powershell
docker run --rm -v "E:/agent/impact-pro-validation-work/go-gin-realworld:/src" -w /src golang:1.21 bash -lc "/usr/local/go/bin/go test ./..."
```

结果：部分通过，全量失败。

```text
ok   github.com/gothinkster/golang-gin-realworld-example-app/articles 3.656s
ok   github.com/gothinkster/golang-gin-realworld-example-app/users    2.873s
FAIL github.com/gothinkster/golang-gin-realworld-example-app/common
```

失败点：

```text
common/unit_test.go:39
Error: An error is expected but got nil.
Messages: Db should not be able to ping
```

T24 收藏审计直接相关的 `articles` 包已通过。后续补充复验确认：默认 root 容器会绕过 `common/unit_test.go:39` 的 `chmod 0000` 权限断言，导致 `Db should not be able to ping` 误判；改用非 root 用户、临时 DB 路径，并用 `-p 1` 串行包执行后，全量 `go test -p 1 ./...` 通过。

## 结论

通过生产级复验。`go-gin-gorm` profile 能在生产复杂度 Go 项目中定位 GORM association、AutoMigrate、API router、serializer、批量查询和测试入口；Docker Go 运行时已证明 T24 直接相关的 `articles` 包通过，且在明确测试前置条件下全量 `go test -p 1 ./...` 通过。
