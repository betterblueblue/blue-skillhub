# Intent-Design

> 把技术方案落成两份可检查的文件——全局架构决策和每个能力的落地设计；模型多加的每一个结构，都必须写明依据。

这是 intent-chain 六步链路的第 3 步：intent-anchor → intent-prd → **intent-design** → intent-issues → intent-dev → intent-verify。

## 为什么需要它

intent-prd 产出 PRD 后，技术方案没有独立产物。PRD 的 Implementation Decisions 只搬运了产品约束（设计标准、术语、性能、安全），技术决策本身没有约束——模型在这里引入 Repository 抽象层、加乐观锁、加缓存，没有任何东西要求它说明为什么。

Intent-Design 把技术方案拆成两层：
- **架构层**（`architecture.md`）：全局决策——分层、模块边界、技术选型、数据流、额外结构与假设。
- **功能设计层**（`design.md`）：每个保留能力在架构里怎么落地。

其中「额外结构与假设」表是这个 skill 的核心：凡是用户没明确要求、为应对某种情况而多加的结构，必须写清为了解决什么具体情况、这种情况的依据（代码位置、用户原话或"无依据，属于假设"）、以后再改的成本。这样把"这个场景会不会发生"从模型的隐含判断变成用户的显式决策。

## 快速开始

```text
/intent-design
用 intent-chain/todo-cli/ 下的 intent.md 和 prd.md 出技术方案。
```

产出同一链路目录下的 `architecture.md` 和 `design.md`，草稿经你确认后写入，写入前运行 `design_validate.py` 的 15 项检查（见下文）。

下一步：交给 [intent-issues](../intent-issues/) 拆工单。

## 什么时候使用

适合：

- intent-prd 已完成，PRD 通过 `prd_validate.py` 校验。
- 需要把技术方案外化为文件，便于追溯和评审。

不适合：

- 没有 INTENT.md 或 PRD（先运行 intent-anchor 和 intent-prd）。
- 已有系统变更（用 impact 的 020-design.md，它已覆盖功能设计层）。

## 轻量档

轻量档是小项目的精简模式，由 intent-anchor 定档并标注在 INTENT.md 第 2 节（触发条件见其 README）。标注轻量档时，两份文档允许写得更薄（架构概览两三句、各表每行一条、能力设计每能力 3-5 行），路径确认并入草稿确认。必需章节和校验不降级。

## 校验

`design_validate.py` 运行 15 项检查：

| 检查项 | 检查内容 |
|---|---|
| A1 | architecture.md 非空 |
| A2 | 6 个必需章节齐全 |
| A3 | 模块表中的能力 ID 存在于 INTENT.md 保留能力 |
| A4 | 模块依赖引用的模块名都已定义 |
| A5 | 技术选型表列非空，「为什么不选另一个」不含禁用词 |
| A6 | 数据流表覆盖 INTENT.md 全部验收路径，模块名都已定义 |
| A7 | 假设表场景列不含抽象词，证据列合规（白名单：代码位置/裸文件名/第 N 行/反引号/标识符/commit 哈希，或引号包裹的用户原话——直引号弯引号单引号均可，或"无依据，属于假设"），无依据项已汇总；"无额外结构"须独立声明行，与数据行并存判矛盾；HTML 注释内的表格不参与检查 |
| A8 | 贵决策有详细说明，便宜决策没有多余说明 |
| D1 | design.md 非空 |
| D2 | 每个保留能力都有一节 |
| D3 | 「不做什么」非空 |
| D4 | 不含代码特征词 |
| D5 | 架构一致性核对表存在 |
| X1 | design.md 引用的模块名都在 architecture.md 中定义 |
| X2 | 两份文件引用的能力 ID 集合一致 |

```bash
python skills/intent-design/scripts/design_validate.py intent-chain/{链路目录}/architecture.md intent-chain/{链路目录}/design.md intent-chain/{链路目录}/intent.md
```

## 文件结构

```text
intent-design/
├── SKILL.md
├── README.md
├── templates/
│   ├── architecture.md              ← 架构文档模板
│   └── design.md                    ← 功能设计文档模板
├── scripts/
│   └── design_validate.py           ← 15 项结构与交叉引用检查
└── tests/
    ├── fixtures/
    │   ├── valid-architecture.md    ← 有效架构样本
    │   └── valid-design.md          ← 有效设计样本
    └── test_design_validate.py      ← 行为回归测试
```

## 能力边界

Intent-Design 能够：

- 从 INTENT.md 和 PRD 原生推导架构和功能设计。
- 用假设表把模型隐含的假设变成用户的显式决策。
- 通过校验器检查模块引用、能力覆盖、假设合规性。

Intent-Design 做不到：

- 自动判断技术方案是否合理。
- 代替用户确认设计文档。
- 防止直接对话场景下的过度设计（那是律刃的事）。
