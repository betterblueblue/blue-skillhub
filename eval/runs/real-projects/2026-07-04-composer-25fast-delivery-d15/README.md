# D15 — node tags 功能删除影响分析（Composer 2.5 Fast）

> **场景 ID**：D15-node-feature-removal-analysis  
> **Case ID**：node-realworld-prisma-impact-feature-removal  
> **Fixture**：`E:\agent\real-project-fixtures\node-realworld-prisma`  
> **需求目录**：`change-impact/tags_feature_removal/`  
> **模式**：full，analysis-only（未改源码）

## 用户输入

tags 功能没人用了，把它整个删掉。先不要写代码，只做完整影响分析。

## 判档结论

**full** — 涉及公开 API 删除、Prisma Tag 模型与 Article↔Tag 多对多关联、文章 tagList 全链路、Swagger 契约及测试引用；非单点删路由可完成。

## 影响面摘要

| 类别 | 要点 |
|------|------|
| **路由** | `GET /api/tags`（`tag.controller.ts`）；`routes.ts` 挂载 `tagsController` |
| **服务** | `tag.service.ts`（`getTags` + `prisma.tag.groupBy`）；`article.service.ts` 中 `?tag=` 过滤、tagList CRUD、`disconnectArticlesTags`、7 处响应映射 |
| **Prisma** | `model Tag`；`Article.tagList Tag[]`；DB 中间表 `_ArticleToTag`（migration 演进自 `ArticleTags`） |
| **测试** | `tests/services/tag.service.test.ts`（仅 test.todo）；`article.service.test.ts` mock 含 `tagList: []` |
| **API 契约** | Swagger：`/tags`、`TagsResponse`、`Article.tagList`、`NewArticle.tagList`、`?tag=` queryparam |
| **Seed** | 无 tag 相关 seed 文件 |

## 待确认（blocking）

1. **API 兼容期** — 直接 404/删字段 vs 短期返回空数组 stub  
2. **历史 Tag 数据** — DROP 前是否备份  
3. **仓外前端** — 本仓无前端，外部消费者未确认  

## Phase 4 产出

| 文件 | 路径 |
|------|------|
| Context Pack | `change-impact/tags_feature_removal/000-context-pack.md` |
| 需求 | `change-impact/tags_feature_removal/010-requirements.md` |
| 设计 | `change-impact/tags_feature_removal/020-design.md` |
| 实施（计划） | `change-impact/tags_feature_removal/030-implementation.md` |
| 活跃状态 | `change-impact/tags_feature_removal/_active-state.md` |

## impact_validate.py

```text
命令：
python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py \
  change-impact/tags_feature_removal \
  --mode full \
  --repo-root E:/agent/real-project-fixtures/node-realworld-prisma

退出码：0
SUMMARY: 27 passed, 0 failed, 0 warnings
```

## 验证命令（Phase 5 参考）

```bash
cd E:/agent/real-project-fixtures/node-realworld-prisma
npm test
# grep 残留
rg -n "tag\.controller|tag\.service|prisma\.tag|tagList" src tests prisma/schema.prisma docs/swagger.json
```

## 说明

- 本次仅写入 `change-impact/tags_feature_removal/`，未修改 `src/`、`prisma/schema.prisma`、`tests/` 或 `docs/swagger.json`。
- Phase 5 实施前须用户确认文档并创建 `060-preflight.md`，逐步 `确认 Step N`。
