---
name: intent-issues
description: 读取 INTENT.md、PRD、architecture.md 和 design.md，按垂直切片拆分工单。工单的 Acceptance criteria 自动引用验收路径编号，输出前自动检查所有路径被覆盖。工单的"涉及模块"字段引用架构文档中定义的模块名。强制要求 INTENT.md、PRD、architecture.md 和 design.md 作为输入。
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
3. 必须存在通过 `design_validate.py` 校验的 `architecture.md` 和 `design.md`。
4. 四者缺一不可。

## 垂直切片规则

- 每个工单交付一条贯穿所有层（schema、API、UI、测试）的完整路径。
- 完成的工单可以独立演示或验证。
- 偏好多个薄切片，而非少数厚切片。
- 工单可以是 HITL（需人工交互）或 AFK（可自动完成）。优先 AFK。

## 轻量档

INTENT.md 第 2 节标注轻量档时：

- 允许单工单直行：一个 AFK 工单覆盖全部验收路径（Acceptance criteria 引用所有路径编号，涉及模块列出全部涉及模块），Blocked by 写无。`issues_validate.py` 照常运行，路径覆盖检查不降级。
- Phase 1 的路径确认并入草稿确认：完整工单草稿开头列出输入文件路径，用户对草稿的一次确认同时覆盖两者（与 intent-prd / intent-design 的轻量档行为一致）。

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
4. 确认 `architecture.md` 和 `design.md` 存在，运行 `design_validate.py` 确认通过。任一缺失或 FAIL 则停止，提示用户先运行 intent-design。
5. 从 INTENT.md 路径推导链路目录，工单写入同一目录下的 `issues.md`。不创建目录、不写文件。

输出：确认后的文件路径和候选输出路径。

### Phase 2：草拟工单

1. 从 PRD 的 User Stories 出发，按垂直切片拆分工单。
2. 每个工单包含：
   - **标题**：简短描述
   - **类型**：自动完成 / 需人工参与（内部可记 AFK/HITL，用户可见处不出现）
   - **前置依赖**（Blocked by）：依赖的其他工单（如有）
   - **做什么**：端到端行为描述，不写逐层实现
   - **验收标准**：从 PRD 的 Given/When/Then 场景拆解。Given 和 When 作为场景上下文，每条 Then 拆为一个可勾选的 `[ ] Then: ...` 条目。引用验收路径编号（如 `[P01]`）。
   - **覆盖的用户故事**：对应的 User Story 编号和能力 ID
3. 每个工单必须包含**涉及模块**子节，列出该工单涉及的模块名（引用 architecture.md 第 2 节定义的模块名）。architecture.md 是强制前置，此子节必填。
4. 如果设计标准存在，涉及界面的工单 Acceptance criteria 必须包含"对照 {设计文件} 结构一致"。
5. 如果术语表存在，涉及界面的工单必须要求使用术语表中的界面文案。
6. 如果 INTENT.md 有性能要求（第 15 节），涉及的工单 Acceptance criteria 必须引用性能要求 ID（如 `[PF01]`）。
7. 如果 INTENT.md 有安全要求（第 16 节），涉及的工单 Acceptance criteria 必须引用安全要求 ID（如 `[SF01]`）。
8. 按依赖顺序排列（阻塞者在前）。

输出：工单列表草案。

### Phase 3：用户确认

1. 展示**完整工单草稿**（每个工单含 做什么、验收标准、前置依赖、覆盖的用户故事、涉及模块），不是只有标题摘要——与其他阶段的全文确认标准一致。
2. 询问用户：
   - 粒度是否合适？（太粗 / 太细）
   - 依赖关系是否正确？
   - 是否需要合并或拆分？
   - 「自动完成 / 需人工参与」标记是否正确？
3. 迭代直到用户确认全文。用户回复“确认”即构成全文确认；“继续”“嗯”“可以”不算。

输出：用户确认后的工单列表。

### Phase 4：写入并校验

1. 按 `templates/issue-template.md` 的格式写入候选路径。
2. 运行：

   ```bash
   python "{intent-issues skill 目录}/scripts/issues_validate.py" "{issues 路径}" "{intent.md 路径}" "{prd 路径}" "{architecture.md 路径}"
   ```

   architecture.md 路径是必需参数。校验器会检查工单的"涉及模块"是否引用了架构文档中定义的模块名。

3. 修复结构问题后重新运行。若有验收路径未被覆盖，补充工单或请用户确认放弃。

输出：通过校验的工单文件。

### Phase 5：完成

`issues.md` 已写入 `intent-chain/{链路目录}/`。下一步：运行 intent-dev，输入 intent.md、prd.md、issues.md、architecture.md 和 design.md，按依赖顺序逐工单开发。

## 强制规则

1. **INTENT.md 和 PRD 必须存在且通过校验**。
2. **每条验收路径至少被一个工单覆盖**：未被覆盖的不得跳过。
3. **工单的 Acceptance criteria 必须引用验收路径编号**，并用 Given/When/Then 结构拆解验收条件。
4. **设计标准、术语表、性能和安全要求约束必须传递到工单**。性能要求引用 PF 编号，安全要求引用 SF 编号。
5. **先确认再写文件**：展示完整工单草稿，用户回复“确认”即构成全文确认。
6. **结构校验必须通过**：写入后运行 `issues_validate.py`（需传入 issues.md、intent.md、prd.md 和 architecture.md 四个路径），校验器会交叉检查验收路径、保留能力、设计标准、术语表、性能和安全要求是否与 INTENT.md 一致，以及 PRD 的 Then/And 条件是否被工单覆盖，以及工单的"涉及模块"是否引用了架构文档中定义的模块名。
7. **上游已答不重问**：用户已在 INTENT.md 或上游链路文档中明确记录的信息（技术偏好、无性能/安全要求、术语表等），直接引用记录使用，不再重复提问；仅当发现现状与记录冲突时才向用户确认。
8. **按模板写入**：写入 issues.md 前必须先读取 `templates/issue-template.md`，按模板的章节结构和行格式产出。本文件的「必需段落」清单只是概要，模板才是完整格式契约。
9. **对用户说人话**：面向用户的汇报、提问和确认请求中，链路内部分类词（如 AFK/HITL）首次出现必须括注一句解释；**工单文件的类型字段、覆盖核对等用户可见处，一律写「自动完成 / 需人工参与」，不出现 AFK/HITL 原文**。INTENT.md 术语表已收录的词，对用户表述时使用"人话翻译"或"界面文案"侧，不用原始术语（用户自己先用了原词的除外）。确认请求必须让用户看得懂再确认。括注解释过的领域词若尚未收录进术语表，主动提请登记（anchor 阶段直接补入第 13 节；下游阶段提醒用户回 intent-anchor 补登记后重跑校验）——需要解释的词就是黑话，解释行为本身即登记信号。

## 工单必需段落

每个工单必须包含：

1. 做什么
2. 验收标准
3. 前置依赖
4. 覆盖的用户故事
5. 涉及模块

文件末尾必须包含：

5. 覆盖核对

> 段落标题以中文为准（2026-07-27 起）。历史文档中的旧英文标题（What to build 等）仍被校验器识别，无需迁移。

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
