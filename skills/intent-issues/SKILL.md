---
name: intent-issues
description: 读取 INTENT.md 和 PRD，按垂直切片拆分工单。工单的 Acceptance criteria 自动引用验收路径编号，输出前自动检查所有路径被覆盖。强制要求 INTENT.md 和 PRD 作为输入。
allowed-tools: Read, Grep, Glob, Write, Bash
---

# Intent-Issues

## 目标

读取 `INTENT.md` 和 `PRD`，把 PRD 拆分为独立可抓取的工单。每个工单是贯穿所有集成层的垂直切片（tracer bullet），不是单层的水平切片。

本 skill 只负责拆分工单：

- 不做需求澄清（那是 intent-anchor 的事）。
- 不写 PRD（那是 intent-prd 的事）。
- 不修改业务代码。

## 前置条件

1. 必须存在通过 `intent_validate.py` 校验的 `INTENT.md`。
2. 必须存在通过 `prd_validate.py` 校验的 `PRD`。
3. 两者缺一不可。

## 垂直切片规则

- 每个工单交付一条贯穿所有层（schema、API、UI、测试）的完整路径。
- 完成的工单可以独立演示或验证。
- 偏好多个薄切片，而非少数厚切片。
- 工单可以是 HITL（需人工交互）或 AFK（可自动完成）。优先 AFK。

## 工单与验收路径的关系

工单按垂直切片拆分，不按验收路径拆分。但每条验收路径必须被至少一个工单覆盖：

- 工单的 Acceptance criteria 引用涉及的验收路径编号（如 `[P01]`）。
- 输出前自动检查：INTENT.md 第 14 节的所有验收路径至少被一个工单引用。
- 未被覆盖的路径会列出来，要求用户确认或补充工单。

## 工作流程

### Phase 1：前置检查

1. 确认 INTENT.md 和 PRD 路径。
2. 读取两者全文。
3. 运行 `intent_validate.py` 和 `prd_validate.py` 确认通过。任一 FAIL 则停止。
4. 从 INTENT.md 路径推导链路目录，工单写入同一目录下的 `issues.md`。不创建目录、不写文件。

输出：确认后的文件路径和候选输出路径。

### Phase 2：草拟工单

1. 从 PRD 的 User Stories 出发，按垂直切片拆分工单。
2. 每个工单包含：
   - **标题**：简短描述
   - **类型**：HITL / AFK
   - **Blocked by**：依赖的其他工单（如有）
   - **What to build**：端到端行为描述，不写逐层实现
   - **Acceptance criteria**：从 PRD 的 Given/When/Then 场景拆解。Given 和 When 作为场景上下文，每条 Then 拆为一个可勾选的 `[ ] Then: ...` 条目。引用验收路径编号（如 `[P01]`）。
   - **User stories covered**：对应的 User Story 编号和能力 ID
3. 如果设计标准存在，涉及界面的工单 Acceptance criteria 必须包含"对照 {设计文件} 结构一致"。
4. 如果术语表存在，涉及界面的工单必须要求使用术语表中的界面文案。
5. 如果 INTENT.md 有性能要求（第 15 节），涉及的工单 Acceptance criteria 必须引用性能要求 ID（如 `[PF01]`）。
6. 如果 INTENT.md 有安全要求（第 16 节），涉及的工单 Acceptance criteria 必须引用安全要求 ID（如 `[SF01]`）。
7. 按依赖顺序排列（阻塞者在前）。

输出：工单列表草案。

### Phase 3：用户确认

1. 展示工单列表，每个工单显示标题、类型、依赖、覆盖的 User Stories。
2. 询问用户：
   - 粒度是否合适？（太粗 / 太细）
   - 依赖关系是否正确？
   - 是否需要合并或拆分？
   - HITL / AFK 标记是否正确？
3. 迭代直到用户确认。

输出：用户确认后的工单列表。

### Phase 4：写入并校验

1. 按 `templates/issue-template.md` 的格式写入候选路径。
2. 运行：

   ```bash
   python "{intent-issues skill 目录}/scripts/issues_validate.py" "{issues 路径}" "{intent.md 路径}" "{prd 路径}"
   ```

3. 修复结构问题后重新运行。若有验收路径未被覆盖，补充工单或请用户确认放弃。

输出：通过校验的工单文件。

### Phase 5：交接

给用户以下提示：

```text
工单已生成。下一步用 intent-dev 开发——按 TDD 循环逐个工单开发，每个工单完成后实际运行验证。

读取 intent-chain/{链路目录}/intent.md 和 prd.md，开始拆工单。工单写入同一目录下的 issues.md。全部工单开发完成后，用 intent-dev 做开发。
```

## 强制规则

1. **INTENT.md 和 PRD 必须存在且通过校验**。
2. **每条验收路径至少被一个工单覆盖**：未被覆盖的不得跳过。
3. **工单的 Acceptance criteria 必须引用验收路径编号**，并用 Given/When/Then 结构拆解验收条件。
4. **设计标准、术语表、性能和安全要求约束必须传递到工单**。性能要求引用 PF 编号，安全要求引用 SF 编号。
5. **先确认再写文件**。
6. **结构校验必须通过**：写入后运行 `issues_validate.py`（需传入 issues.md、intent.md 和 prd.md 三个路径），校验器会交叉检查验收路径、保留能力、设计标准、术语表、性能和安全要求是否与 INTENT.md 一致，以及 PRD 的 Then/And 条件是否被工单覆盖。

## 工单必需段落

每个工单必须包含：

1. What to build
2. Acceptance criteria
3. Blocked by
4. User stories covered

文件末尾必须包含：

5. Coverage Verification（覆盖验证）

## 文件存放

最终文件放在目标项目根目录：

```text
intent-chain/{链路目录}/issues.md
```

- 链路目录由 intent-anchor 创建，工单写入同一目录。

## 能力边界

Intent-Issues 能够：

- 从 PRD 原生推导工单，按垂直切片拆分。
- 自动检查验收路径和保留能力的覆盖情况。
- 把设计标准、术语表、性能和安全要求约束传递到工单。
- 交叉检查 PRD 中每条验收路径的 Then/And 条件是否被工单覆盖。

Intent-Issues 做不到：

- 自动判断工单的技术可行性。
- 代替用户确认工单拆分。
- 自动发布到 issue tracker（产出的是 markdown 文件，用户自行复制）。
