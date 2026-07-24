---
name: intent-prd
description: 读取 INTENT.md，原生引用能力表、验收路径、设计标准和术语表，生成结构化 PRD。强制要求 INTENT.md 作为输入。适用于 intent-anchor 完成后、任务拆分之前的阶段。
allowed-tools: Read, Grep, Glob, Write, Bash
---

# Intent-PRD

## 目标

读取 `INTENT.md`，生成一份结构化 PRD。PRD 原生引用 INTENT.md 的能力表、验收路径、设计标准和术语表，不需要交接 prompt 注入约束。

本 skill 只负责把意图转化为 PRD：

- 不做需求澄清（那是 intent-anchor 的事）。
- 不拆任务（那是 intent-issues 的事）。
- 不修改业务代码。

## 前置条件

1. 必须存在通过 `intent_validate.py` 校验的 `INTENT.md`。没有则停止，提示用户先运行 intent-anchor。
2. INTENT.md 中不能有 `待确认` 项。

## INTENT.md 到 PRD 的映射

| INTENT.md 章节 | PRD 段 |
|---|---|
| 第 1 节一句话意图 | Problem Statement |
| 第 4 节保留能力 + 第 5 节不可妥协项 | Solution |
| 第 4 节保留能力 | User Stories（每个保留能力至少对应一个 story） |
| 第 12 节设计标准 | Implementation Decisions > Design Standards |
| 第 13 节术语表 | Implementation Decisions > Terminology Constraints |
| 第 14 节验收路径 | Acceptance Criteria |
| 第 6 节推迟/放弃 | Out of Scope |

## 工作流程

### Phase 1：前置检查

1. 确认 INTENT.md 路径。路径不明时询问用户，不自动选择"最新一份"。
2. 读取 INTENT.md 全文。
3. 运行 `intent_validate.py` 确认通过。FAIL 则停止，提示用户先修正 INTENT.md。
4. 计算候选 PRD 路径：`prd/{YYYY-MM-DD}-{NNN}-{产品名称}.md`。不创建目录、不写文件。

输出：确认后的 INTENT.md 路径和候选 PRD 路径。

### Phase 2：生成 PRD

1. 探索代码库（如果目标项目已有代码），了解现状。
2. 按 `templates/PRD.md` 的骨架生成草稿：
   - **Problem Statement**：从第 1 节一句话意图推导，用用户视角描述问题。
   - **Solution**：从第 4 节保留能力和第 5 节不可妥协项推导，描述解决方案。
   - **User Stories**：每个保留能力至少对应一个 story，格式 `As a <角色>, I want <功能>, so that <收益>`。story 末尾标注对应能力 ID（如 `[C01]`）。
   - **Implementation Decisions**：技术决策。如果有设计标准，在 Design Standards 子节列出文件路径和验收范围。如果有术语表，在 Terminology Constraints 子节列出界面文案约束。
   - **Acceptance Criteria**：从第 14 节验收路径推导。每条路径用 Given/When/Then 结构描述验收条件：Given 是前置条件（操作前系统状态），When 是触发操作，Then 是可判定的预期结果（每条能回答是/否）。每条路径对应一个 `### {路径 ID}: {路径名称}` 场景块。
   - **Testing Decisions**：测试策略，说明测什么、用什么缝、参考已有测试。
   - **Out of Scope**：从第 6 节推迟和放弃项推导，逐项列出并标注原因。
   - **Intent Verification**：逐项核对保留能力覆盖情况、不可妥协项支持情况、新增能力报告。
3. 如果探索代码库时发现了与 INTENT.md 冲突的信息，停下来告诉用户，不要自行改写原意。

输出：完整 PRD 草稿。

### Phase 3：确认并写入

1. 在回复中展示完整草稿。
2. 用户确认全文后，创建 `prd/` 目录并写入候选路径。
3. 运行：

   ```bash
   python "{intent-prd skill 目录}/scripts/prd_validate.py" "{PRD 路径}" "{INTENT.md 路径}"
   ```

4. 修复结构问题后重新运行。若修复改变了能力覆盖或验收路径引用，之前的全文确认立即失效，必须重新确认。

输出：通过结构校验的 PRD。

### Phase 4：交接

给用户以下可直接传给下一会话的 Prompt，并替换真实路径：

```text
先读 prd/{实际文件名}.md 和 intent-anchor/{INTENT.md 文件名}.md，再完成任务拆分。

拆工单用 intent-issues——它会原生读取 INTENT.md 和 PRD，自动处理设计标准、术语表和验收路径。如果使用第三方 skill，需手动检查这些约束是否被遵守。

只把 User Stories 中标注的能力作为开发范围。

发现遗漏、冲突或未经确认的新增项时停下来告诉我，不要自行改写原意。
```

## 强制规则

1. **INTENT.md 必须存在且通过校验**：不通过则不生成 PRD。
2. **每个保留能力至少对应一个 User Story**：不得遗漏。
3. **每条验收路径必须出现在 Acceptance Criteria 中**：不得跳过。使用 Given/When/Then 结构描述。
4. **设计标准和术语表必须引用**：如果 INTENT.md 有对应内容，PRD 必须引用。
5. **先确认再写文件**：在对话中展示完整草稿，得到明确确认后才写入。
6. **结构校验必须通过**：写入后运行 `prd_validate.py`。

## PRD 必需章节

1. Problem Statement
2. Solution
3. User Stories
4. Implementation Decisions
   - Design Standards（如果有）
   - Terminology Constraints（如果有）
5. Acceptance Criteria
6. Testing Decisions
7. Out of Scope
8. Intent Verification
   - 保留能力覆盖
   - 不可妥协项核对
   - 新增能力

## 文件存放

最终文件放在目标项目根目录：

```text
prd/{YYYY-MM-DD}-{NNN}-{产品名称}.md
```

- 日期使用生成当天的实际日期。
- `NNN` 是当日三位序号。
- 同一产品的修订覆盖原文件。

## 能力边界

Intent-PRD 能够：

- 从 INTENT.md 原生推导 PRD，不需要交接 prompt 注入约束。
- 自动检查保留能力和验收路径的覆盖情况。
- 引用设计标准和术语表约束。

Intent-PRD 做不到：

- 自动判断 PRD 的技术方案是否合理。
- 代替用户确认 PRD 内容。
- 强制 intent-issues 读取 PRD（交接仍需用户主动传递文件路径）。
