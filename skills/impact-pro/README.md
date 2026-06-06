# ImpactRadar Pro — 通用变更影响分析

## 这个 Skill 是干什么的

把模糊的变更意图，通过靶向提问变成证据化的影响分析，自动适配任意技术栈，按 light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

## 核心能力

- **通用内核 + 技术栈 profile** — 无栈假设，profile 按需加载
- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，针对性提问
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档
- **证据化分析** — 用工具发现真实上下文，不靠臆测
- **DB adapter 系统** — MySQL + generic SQL adapter（PG 等其他 DB 走 generic）
- **19 维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求 → 设计 → 实施，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都询问
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **TDD 验证框架** — 正向用例 + 错误用例（边界值/空值/格式校验/XSS）

## 技术栈覆盖

| Profile | Level | 说明 |
|---------|-------|------|
| generic | — | 强兜底，扫描目录结构，任意栈可用 |
| java-spring-mybatis | 2 | Java/Spring/MyBatis/RuoYi，已深度覆盖 |

generic 是「覆盖任意栈」的真正解锁点，专属 profile 按需晋升。

## 触发方式

在 Claude Code 终端输入 `/impact-pro` 激活。

## 与 impact v3.0 的区别

| | impact v3.0 | impact-pro |
|--|------------|------------|
| 架构 | 单体 SKILL.md，Java 规则写死 | 通用内核 + profile 系统 |
| 栈适配 | 仅 Java/MyBatis | 通用 + 专属 profile |
| 扩展方式 | 修改 SKILL.md | 新增 profile 文件 |
| 数据库 | 仅 MySQL | MySQL + generic adapter |

## 典型流程

```
你：我想给用户表加一个个性签名字段
↓
Phase 2：栈探测 → 加载对应 profile → 上下文发现
↓
Phase 2.5：判断 light/full，请确认
↓
Phase 3：靶向提问（字段长度？哪些接口？缓存？迁移脚本？）
↓
Phase 4：输出文档（light 一页 / full 三文档逐份确认）
↓
Phase 5：执行（每步确认，自动跑风格检查+单测）
```

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核
├── README.md             # 本文件
├── profiles/             # 技术栈 profile
│   ├── _schema.md        # profile 统一接口
│   ├── _template.md      # 新 profile 空白模板
│   ├── generic.md         # 强兜底（任意栈）
│   └── java-spring-mybatis.md  # Java/Spring/MyBatis (Level 2)
├── db-adapters/          # 数据库 adapter
│   ├── generic-sql.md    # 通用 SQL 模板
│   └── mysql.md          # MySQL 专用
└── templates/            # 文档模板
    ├── light.md
    ├── requirements.md
    ├── design.md
    └── implementation.md
```
