# impact-pro 第八轮验收总结（每项目第二变更）

- 测试日期：2026-06-07
- 测试方式：真实项目静态 light 验收
- 目标：推进“每个项目 2 个变更：1 个 light、1 个 full”的投产门槛
- 结论：**5 个主要后端样本已补齐第二变更，双变更矩阵取得阶段性进展**

## 本轮新增评分

| 用例 | 项目 | 类型 | 分数 | 失败等级 | 结论 |
|------|------|------|------|----------|------|
| T13 | RuoYi-Vue | Java/RuoYi 前端 light | 91 | 无 | 通过 |
| T14 | prisma-examples/testing-express | Node/Prisma API 文案 light | 90 | 无 | 通过 |
| T15 | full-stack-fastapi-template/backend | FastAPI message light | 90 | 无 | 通过 |
| T16 | golang-gin-realworld-example-app | Go/Gin API 文案 light | 88 | 无 | 通过 |
| T17 | eShopOnWeb | .NET Razor UI light | 88 | 无 | 通过 |

## 双变更门槛进度

| 项目 | full 用例 | light 用例 | 当前状态 |
|------|-----------|------------|----------|
| RuoYi-Vue | T01 | T13 | 达到 |
| prisma-examples/testing-express | T02 | T14 | 达到 |
| full-stack-fastapi-template/backend | T03 | T15 | 达到 |
| golang-gin-realworld-example-app | T04 | T16 | 达到 |
| eShopOnWeb | T05 | T17 | 达到 |
| full-stack-fastapi-template/frontend | 待补 full 或跨端用例 | T06 | 未达到 |
| next-learn/dashboard/final-example | T11 | 待补 light | 未达到 |
| nuxt-ui-templates/dashboard | T12 | 待补 light | 未达到 |

## 当前累计评分

| 范围 | 用例数 | 平均分 |
|------|--------|--------|
| T01-T12 | 12 | 89.0 |
| T01-T17 | 17 | 89.35 |

## 本轮发现

- `impact-pro` 对 light 变更的主要风险不是“找不到文件”，而是容易被项目里的 DB/ORM 证据带偏，过度生成 migration/SQL 计划。
- 5 个 light 用例都要求明确写出“不涉及 schema/迁移/权限核心逻辑”的证据。
- API 文案类 light 变更仍需提醒客户端兼容性，不能因为不改 DB 就完全无风险。

## 当前投产判断

```text
impact-pro = 多栈可试用增强版；5 个主要后端技术栈已达到每项目 full+light 双变更门槛，但前端/monorepo 和真实对话复测仍未完成。
```

剩余原因：

1. 前端样本第二变更、Monorepo 第二变更、Go/.NET Docker 运行时和 T08-T10 真实 agent 对话复测已在后续轮次补强。
2. 剩余重点转向生产级 Next 项目、执行阶段门禁和更多生产级样本余量。
