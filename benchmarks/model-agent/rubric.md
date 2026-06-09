# Rubric

这个 rubric 同时服务机器评分和人工评分。

## 机器指标

| 指标 | 中文名 | 说明 |
| --- | --- | --- |
| P0 Recall | P0 召回率 | 必须文件命中比例 |
| Overall Recall | 整体召回率 | 所有 expected files 命中比例 |
| Boundary Hits | 边界命中 | migration、generated、tests、auth、route registration 等关键边界 |
| Precision@K | 前 K 个上下文精度 | 候选上下文中相关文件比例 |
| Tool Calls | 工具调用次数 | shell、read、rg、MCP 等调用总数 |
| Tool Errors | 工具错误次数 | 参数缺失、路径错误、MCP 超时等 |
| File Reads | 文件读取数 | 读了多少文件 |
| Search Calls | 搜索次数 | `rg` / grep / semantic search 次数 |
| Duration | 耗时 | wall-clock time |
| Cost | 成本 | agent runner 返回的模型调用成本 |
| Input Tokens | 输入 token | 模型输入量 |
| Output Tokens | 输出 token | 模型输出量 |
| Timeout Rate | 超时率 | 多轮运行中 timeout 比例 |
| Provider Error Rate | 接入错误率 | API / gateway / provider 错误比例 |

## Boundary Hits

不同技术栈的边界不一样。每个任务应显式声明它关心哪些边界。

| Boundary | 示例 |
| --- | --- |
| migration | Prisma migration、Alembic、GORM AutoMigrate、EF Core migration |
| generated | OpenAPI client、types.gen.ts、schemas.gen.ts、SDK、Prisma client |
| route registration | backend route、frontend route、controller mapping |
| auth / permission | permission string、role loading、data scope、frontend directive |
| tests | unit test、integration test、fixture、E2E spec |
| async / job | queue producer、consumer、scheduler、retry |
| notification | email template、sender、preference、unsubscribe |
| analytics | event schema、collector、dashboard、aggregation |

## 人工评分

人工总分 15 分。

| 维度 | 分数 | 评分标准 |
| --- | ---: | --- |
| Analysis Quality | 0-3 | 是否正确解释现有链路和影响范围 |
| Plan Correctness | 0-3 | 实施方案是否可执行、顺序是否合理 |
| Verification Coverage | 0-3 | 是否覆盖正向、反向、回归、边界测试 |
| Boundary Awareness | 0-3 | 是否识别 migration/generated/tests/auth 等关键边界 |
| Hallucination Control | 0-3 | 是否避免编造文件、表、命令、框架行为 |

评分细则：

| 分数 | 含义 |
| ---: | --- |
| 3 | 完整、准确、可执行 |
| 2 | 大体正确，但漏一个重要边界或表达不够落地 |
| 1 | 有部分有用信息，但关键链路不完整 |
| 0 | 方向错误、严重臆测、无法使用 |

## 质量扣分项

| 问题 | 建议扣分 |
| --- | --- |
| 漏 P0 文件 | Boundary Awareness -1 到 -3 |
| 编造不存在文件 / 表 / API | Hallucination Control -2 到 -3 |
| 把工具结果当最终事实 | Hallucination Control -1 |
| 只给泛泛步骤，没有项目路径 | Analysis Quality -1 |
| 验证计划只写“跑测试” | Verification Coverage -1 |
| 无视用户要求 analysis-only，尝试写文件 | Plan / Hallucination / status 单独记录 |

## Execution 任务额外指标

Execution 阶段才记录这些指标。

| 指标 | 说明 |
| --- | --- |
| Patch Correctness | 修改是否满足需求 |
| Diff Scope | 是否只改必要文件 |
| Test Selection | 是否选择正确测试 |
| Test Result | 测试是否通过 |
| Self Repair | 测试失败后是否能定位并修复 |
| Regression Risk | 是否引入无关重构、格式化、行为变化 |

## 推荐报告表

```text
| Model | Task | Status | P0 Recall | Overall Recall | Boundary Hits | Quality / 15 | Time | Cost | Tool Errors |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
```
