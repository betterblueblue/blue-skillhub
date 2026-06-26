---
name: impact-pro
description: "[已合并到 impact] 本 skill 已合并到 impact。请使用 impact 替代。impact 现在支持多技术栈（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等），通过 profile 注入栈规则。"
disable-model-invocation: true
---

# ImpactRadar Pro — 已合并到 Impact

> **本 skill 已于 2026-06-26 合并到 `impact`。**
>
> `impact` 现在是统一的多栈变更影响分析 skill，包含原 `impact-pro` 的全部能力：
> - 栈无关内核 + `profiles/` 按需加载技术栈规则
> - `db-adapters/` 数据库适配器
> - `code-graph-adapters/` 可选代码图适配器
> - 规则分层加载（progressive disclosure）
> - 快速通道（trivial 出口）
>
> **迁移方式**：
> 1. 卸载 `impact-pro`
> 2. 安装 `impact`（如果已安装则更新）
> 3. 原来用 `impact-pro` 的场景现在直接用 `impact`
>
> Java/Spring/MyBatis 项目原来用 `impact` 的，继续用 `impact`——它现在通过 `profiles/java-spring-mybatis.md` 注入 Java 专属规则，能力不减。
