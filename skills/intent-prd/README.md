# Intent-PRD

> 把 `INTENT.md` 变成结构化 PRD，已确认的能力、验收路径和约束一条不漏地带进去。

这是 intent-chain 链路的第 2 步：intent-anchor → **intent-prd** → intent-design → intent-visual（仅 UI 项目）→ intent-issues → intent-dev → intent-adversarial → intent-verify。

## 为什么需要它

本 Skill 改造自 Matt Pocock 的 [to-spec](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec)（MIT 许可，版权归原作者；早期版本叫 to-prd）。

intent-anchor 产出 `INTENT.md` 后，需要把意图转化为 PRD 才能进入任务拆分。原版不认识 `INTENT.md` 的结构：设计标准、术语表这些约束只能靠一段转述提示词带过去，下游也不会检查它们有没有被遵守。如果没有 `INTENT.md`，直接用原版即可。

Intent-PRD 直接解析 `INTENT.md` 各节，把能力表、验收路径、设计标准和术语表映射到 PRD 对应段落，并用校验脚本自动检查覆盖情况。

## 快速开始

```text
/intent-prd
用 intent-chain/todo-cli/intent.md 生成 PRD。
```

产出 `intent-chain/{链路目录}/prd.md`，和 `intent.md` 放在同一目录。草稿经你确认后写入，写入前运行 `prd_validate.py` 的 10 项检查（见下文）。

下一步：把 PRD 交给 [intent-design](../intent-design/) 产出技术方案。

## 什么时候使用

适合：

- intent-anchor 已完成，INTENT.md 通过 `intent_validate.py` 校验。
- 需要把意图转化为 PRD，进入任务拆分阶段。

不适合：

- 没有 INTENT.md（先运行 intent-anchor）。
- INTENT.md 未通过校验（先修正）。
- 已有明确 PRD，不需要重新生成。

## INTENT.md 到 PRD 的映射

| INTENT.md 章节 | PRD 段 |
|---|---|
| 第 1 节一句话意图 | Problem Statement |
| 第 4 节保留能力 + 第 5 节不可妥协项 | Solution |
| 第 4 节保留能力 | User Stories（每个至少对应一个 story） |
| 第 12 节设计标准 | Implementation Decisions > Design Standards |
| 第 13 节术语表 | Implementation Decisions > Terminology Constraints |
| 第 14 节验收路径 | Acceptance Criteria |
| 第 15 节性能要求 | Implementation Decisions > Performance Requirements |
| 第 16 节安全要求 | Implementation Decisions > Security Requirements |
| 第 6 节推迟/放弃 | Out of Scope |

可选子节（Design Standards / Terminology Constraints / Performance / Security Requirements）在 INTENT.md 没有对应内容时直接省略，不保留标题写"无"。

## 轻量档

轻量档是小项目的精简模式，由 intent-anchor 定档并标注在 INTENT.md 第 2 节（触发条件见其 README）。标注轻量档时，各节允许写得更薄（User Story 每能力一行、Implementation Decisions 一行表），Phase 1 的路径确认并入草稿确认。必需章节和校验不降级。

**上游已答不重问**：INTENT.md 已记录的信息（技术偏好、无性能/安全要求、术语表等）直接引用使用，不再重复提问；仅当发现现状与记录冲突时才向用户确认。

## 校验

`prd_validate.py` 运行 10 项检查：

| 检查项 | 检查内容 |
|---|---|
| V1 | PRD 文件非空 |
| V2 | 8 个必需章节齐全 |
| V3 | 所有保留能力 ID 出现在 User Stories 中 |
| V4 | 所有验收路径 ID 出现在 Acceptance Criteria 中 |
| V5 | INTENT.md 有设计标准时，PRD 引用了设计素材路径 |
| V6 | INTENT.md 有术语表时，PRD 引用了术语约束 |
| V7 | Intent Verification 包含三个子节且与 INTENT.md 一致 |
| V8 | 每条验收路径使用 Given/When/Then 结构描述验收条件 |
| V9 | INTENT.md 有性能要求时，PRD 引用了性能要求 ID |
| V10 | INTENT.md 有安全要求时，PRD 引用了安全要求 ID |

```bash
python skills/intent-prd/scripts/prd_validate.py intent-chain/{链路目录}/prd.md intent-chain/{链路目录}/intent.md
```

## 文件结构

```text
intent-prd/
├── SKILL.md
├── README.md
├── templates/
│   └── PRD.md                        ← PRD 模板
├── scripts/
│   └── prd_validate.py               ← 10 项结构与交叉引用检查
└── tests/
    ├── fixtures/valid-prd.md          ← 有效样本
    └── test_prd_validate.py           ← 行为回归测试
```

## 能力边界

Intent-PRD 能够：

- 直接从 INTENT.md 推导 PRD，不需要靠提示词转述约束。
- 自动检查保留能力和验收路径的覆盖情况。
- 引用设计标准、术语表、性能和安全要求约束。
- 交叉检查 PRD 中的性能和安全要求 ID 是否与 INTENT.md 一致。

Intent-PRD 做不到：

- 自动判断 PRD 的技术方案是否合理。
- 代替用户确认 PRD 内容。
- 强制 intent-issues 读取 PRD。
