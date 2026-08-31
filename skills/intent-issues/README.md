# Intent-Issues

> 把 PRD 和设计拆成一条条能独立开发、独立验证的工单，并自动检查没有任何验收路径被漏掉。

这是 intent-chain 链路的第 5 步：intent-anchor → intent-prd → intent-design → intent-visual（仅 UI 项目）→ **intent-issues** → intent-dev → intent-adversarial → intent-verify。

## 为什么需要它

本 Skill 改造自 Matt Pocock 的 [to-tickets](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets)（MIT 许可，版权归原作者；早期版本叫 to-issues）。

PRD 和设计文件生成后需要拆分为独立可抓取的工单。原版不认识这套结构：验收路径只能靠一段转述提示词带过去，工单的 Acceptance criteria 不会自动引用路径编号，覆盖情况也没人检查。如果没有 INTENT.md，直接用原版即可。

Intent-Issues 直接读取 INTENT.md 的验收路径，在工单的 Acceptance criteria 中自动引用路径编号，并在输出前自动检查所有路径被至少一个工单覆盖。

## 快速开始

```text
/intent-issues
用 intent-chain/todo-cli/ 下的文档拆工单。
```

产出同一链路目录下的 `issues.md`，完整工单草稿经你确认后写入，写入前运行 `issues_validate.py` 的 11 项检查（见下文）。

下一步：交给 [intent-dev](../intent-dev/) 逐工单开发。

## 什么时候使用

适合：

- intent-prd 已完成，PRD 通过 `prd_validate.py` 校验。
- intent-design 已完成，`architecture.md` 和 `design.md` 通过 `design_validate.py` 校验。
- 需要把 PRD 拆分为工单，进入开发阶段。

不适合：

- 没有 INTENT.md、PRD、architecture.md 或 design.md（先运行前置 skill）。
- PRD 未通过校验（先修正）。

## 垂直切片规则

- 每个工单交付一条贯穿所有层（schema、API、UI、测试）的完整路径。
- 完成的工单可以独立演示或验证。
- 偏好多个薄切片，而非少数厚切片。
- 工单可以是 HITL（需人工交互）或 AFK（可自动完成）。优先 AFK。

## 轻量档

轻量档是小项目的精简模式，由 intent-anchor 定档并标注在 INTENT.md 第 2 节（触发条件见其 README）。标注轻量档时，允许只拆一个 AFK 工单覆盖全部验收路径，路径确认并入完整工单草稿的一次确认。路径覆盖检查不降级。

**上游已答不重问**：INTENT.md 或上游链路文档已记录的信息（技术偏好、无性能/安全要求、术语表等）直接引用使用，不再重复提问；仅当发现现状与记录冲突时才向用户确认。确认阶段展示的是完整工单草稿（含 What to build、Acceptance criteria、涉及模块等），不是只有标题的摘要。

## 校验

`issues_validate.py` 运行 11 项检查：

| 检查项 | 检查内容 |
|---|---|
| V1 | 文件非空 |
| V2 | 每个工单包含 4 个必需子节 |
| V3 | 所有验收路径被至少一个工单覆盖 |
| V4 | 所有保留能力被至少一个工单覆盖 |
| V5 | Coverage Verification 包含三个子节且与 INTENT.md 一致 |
| V6 | INTENT.md 有设计标准时，至少一个工单 Acceptance criteria 包含"对照" |
| V7 | INTENT.md 有术语表时，至少一个工单 Acceptance criteria 引用了术语 |
| V8 | INTENT.md 有性能要求时，所有性能要求 ID 被工单引用 |
| V9 | INTENT.md 有安全要求时，所有安全要求 ID 被工单引用 |
| V10 | PRD 中每条验收路径的 Then/And 条件被工单覆盖 |
| V11 | 工单的"涉及模块"引用的模块名必须在 architecture.md 中定义（强制检查） |

```bash
python skills/intent-issues/scripts/issues_validate.py intent-chain/{链路目录}/issues.md intent-chain/{链路目录}/intent.md intent-chain/{链路目录}/prd.md intent-chain/{链路目录}/architecture.md
```

## 文件结构

```text
intent-issues/
├── SKILL.md
├── README.md
├── templates/
│   └── issue-template.md             ← 工单模板
├── scripts/
│   └── issues_validate.py            ← 11 项结构与交叉引用检查
└── tests/
    ├── fixtures/valid-issues.md       ← 有效样本
    └── test_issues_validate.py        ← 行为回归测试
```

## 能力边界

Intent-Issues 能够：

- 直接从 PRD 推导工单，按垂直切片拆分。
- 自动检查验收路径和保留能力的覆盖情况。
- 把设计标准、术语表、性能和安全要求约束传递到工单。
- 交叉检查 PRD 中每条验收路径的 Then/And 条件是否被工单覆盖。

Intent-Issues 做不到：

- 自动判断工单的技术可行性。
- 代替用户确认工单拆分。
- 自动发布到 issue tracker（产出的是 markdown 文件，用户自行复制）。
