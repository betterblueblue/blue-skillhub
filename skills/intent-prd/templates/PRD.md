# PRD - {产品名称}

<!--
  本文件由 intent-prd skill 生成。
  前置文件：intent-chain/{链路目录}/intent.md
  生成日期：{日期}
  PRD 不是自动执行授权，用户确认后才能进入任务拆分。
-->

## Problem Statement

{从 INTENT.md 第 1 节一句话意图推导，用用户视角描述问题}

## Solution

{从 INTENT.md 第 4 节保留能力和第 5 节不可妥协项推导，描述解决方案}

## User Stories

1. As a {角色}, I want {功能}, so that {收益} [C01]
2. As a {角色}, I want {功能}, so that {收益} [C02]

<!-- 每个保留能力至少对应一个 User Story，末尾标注能力 ID。 -->

## Implementation Decisions

{技术决策：模块、接口、schema、API contracts、交互}

### Design Standards

<!--
  如果 INTENT.md 第 12 节有设计素材，在此列出文件路径和验收范围。
  没有设计素材时写：无设计标准素材。
-->

| 设计素材 | 路径 | 验收范围 |
|---|---|---|
| {类型} | {路径} | {覆盖哪些页面或交互} |

### Terminology Constraints

<!--
  如果 INTENT.md 第 13 节有术语表，在此列出界面文案约束。
  没有术语时写：无术语约束。
-->

| 原始术语 | 界面文案 |
|---|---|
| {术语} | {界面上的文字} |

### Performance Requirements

<!--
  如果 INTENT.md 第 15 节有性能要求，在此逐条列出。
  引用要求 ID（如 PF01）。
  没有性能要求时写：无性能要求。
-->

| 要求 ID | 性能要求 | 对应能力 |
|---|---|---|
| PF01 | {要求内容} | {C01} |

### Security Requirements

<!--
  如果 INTENT.md 第 16 节有安全要求，在此逐条列出。
  引用要求 ID（如 SF01）。
  没有安全要求时写：无安全要求。
-->

| 要求 ID | 安全要求 | 对应能力 |
|---|---|---|
| SF01 | {要求内容} | {C01} |

## Acceptance Criteria

<!--
  从 INTENT.md 第 14 节验收路径推导。
  每条路径用 Given/When/Then 结构描述验收条件：
  - Given：执行操作前的系统状态（前置条件）
  - When：触发被验收功能的操作
  - Then：操作完成后可判定的预期结果（每条能回答是/否）
  每条路径对应一个 ### 场景块，块标题格式：### {路径 ID}: {路径名称}
-->

### P01: {路径名称}

对应 User Stories: {Story 编号}

- **Given** {前置条件}
- **When** {触发操作}
- **Then** {预期结果，每条能回答是/否}
- **And** {预期结果}

## Testing Decisions

- {测试策略：测什么、用什么缝、参考已有测试}
- {测试范围}

## Out of Scope

<!--
  从 INTENT.md 第 6 节推迟和放弃项推导，逐项列出并标注原因。
-->

- {能力}：{推迟/放弃}，原因：{INTENT.md 中的原因}

## Intent Verification

### 保留能力覆盖

| 能力 ID | 保留能力 | PRD 中的位置 | 状态 |
|---|---|---|---|
| C01 | {能力} | {User Story / Implementation Decision} | 已体现 |
| C02 | {能力} | {User Story / Implementation Decision} | 已体现 |

<!-- 状态只使用：已体现 / 本阶段不适用（说明原因）/ 遗漏。存在遗漏时停止进入下一阶段。 -->

### 不可妥协项核对

<!-- 如果 INTENT.md 明确写"无不可妥协项"，本节写"不适用"。 -->

| 能力 ID | 不可妥协项 | PRD 是否支持 | 证据 |
|---|---|---|---|
| C01 | {不可妥协的原因} | 支持 | {位置或原因} |

### 新增能力

| 新增内容 | 是否在 INTENT.md 中 | 处理方式 |
|---|---|---|
| {能力} | 否 | 等待用户确认 |

<!-- 没有新增能力时写"无"。 -->
