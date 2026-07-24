# Issues - {产品名称}

<!--
  本文件由 intent-issues skill 生成。
  前置文件：intent-chain/{链路目录}/intent.md 和 PRD.md
  生成日期：{日期}
  工单按垂直切片拆分，每个工单贯穿所有集成层。
-->

---

## Issue 1: {标题}

- **类型**：HITL / AFK

### What to build

{端到端行为描述，不写逐层实现。描述用户能做什么，而不是怎么做。}

### Acceptance criteria

**[P01] {场景名称}**
- Given: {前置条件}
- When: {触发操作}
- [ ] Then: {预期结果 1}
- [ ] And: {预期结果 2}
- [ ] 对照 {设计文件} 结构一致（如果有设计标准且涉及界面）
- [ ] 界面文案使用术语表中的人话翻译（如果有术语表且涉及界面）

### Blocked by

None - can start immediately / {Issue 编号}

### User stories covered

- Story {编号} [{能力 ID}]

---

## Issue 2: {标题}

- **类型**：HITL / AFK

### What to build

{描述}

### Acceptance criteria

**[P02] {场景名称}**
- Given: {前置条件}
- When: {触发操作}
- [ ] Then: {预期结果}

### Blocked by

{Issue 1}

### User stories covered

- Story {编号} [{能力 ID}]

---

## Coverage Verification

### 验收路径覆盖

| 路径 ID | 验收路径 | 覆盖工单 | 状态 |
|---|---|---|---|
| P01 | {路径名称} | Issue 1 | 已覆盖 |
| P02 | {路径名称} | Issue 2 | 已覆盖 |

<!-- 所有验收路径必须被至少一个工单覆盖。存在未覆盖项时不得交付。 -->

### 保留能力覆盖

| 能力 ID | 保留能力 | 覆盖工单 | 状态 |
|---|---|---|---|
| C01 | {能力} | Issue 1 | 已覆盖 |

### 新增能力

| 新增内容 | 是否在 INTENT.md 中 | 处理方式 |
|---|---|---|
| {能力} | 否 | 等待用户确认 |

<!-- 没有新增能力时写"无"。 -->
