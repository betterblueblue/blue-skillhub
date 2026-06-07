# T16 golang-gin-realworld-example-app - Article 错误提示文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Go / Gin / GORM
- 项目路径：`E:\agent\impact-pro-validation-work\go-gin-realworld`
- 变更意图：调整文章详情不存在时的错误提示文案，不改路由、状态码或数据库查询。
- 使用档位：light
- 命中 profile：`go-gin-gorm`
- 最终评分：88
- 失败等级：无

## 实际发现

关键文件：

- `articles/routers.go`：`ArticleRetrieve` 中找不到 slug 时返回 `http.StatusNotFound` 和 `common.NewError("articles", errors.New("Invalid slug"))`。
- `articles/unit_test.go`：`TestArticleNotFoundErrors`、`TestArticleListWithFilters` 等覆盖路由错误路径和过滤。
- `articles/models.go` / `common/database.go`：可作为只读 DB/GORM 背景证据，本变更不需要改模型或迁移。

## 验收判断

应判定 light。

理由：

- 不改 GORM model、AutoMigrate、查询条件或路由结构。
- 只改自然语言错误提示和相关测试断言。
- 需要标注 API 消费者可能依赖错误字符串。

## 风险追问

1. 是否要只改 ArticleRetrieve，还是同步 favorite/comment/list 的类似错误文案？
2. 客户端是否依赖 `articles` 错误 key 和 `Invalid slug` 字符串？
3. 是否需要引入稳定错误码，避免自然语言成为契约？

## 验证方案

- `go test ./articles` 或项目实际测试命令。
- 正向：存在文章仍返回 200。
- 错误：不存在 slug 仍返回 404，新错误文案。
- 回归：favorite/comment 的错误路径不被误改。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | 同类错误提示分布在多个 handler | `ArticleRetrieve`、`ArticleFavorite`、`ArticleCommentCreate` | 明确本次是否只改一个入口，避免顺手大改 |

## 结论

通过（light）。该用例补充 Go/Gin/GORM 样本第二变更，验证 profile 能把 API 文案调整限制在 handler/test，不误触 GORM model。
