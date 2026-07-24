# Intent-PRD

> 读取 INTENT.md，原生引用能力表、验收路径、设计标准和术语表，生成结构化 PRD。

## 为什么需要它

intent-anchor 产出 `INTENT.md` 后，需要把意图转化为 PRD 才能进入任务拆分。使用第三方 to-prd 时，约束只能通过交接 prompt 注入，下游 skill 不认识 INTENT.md 的结构，约束传递不可靠。如果没有 INTENT.md，直接用原版 to-prd 即可。

Intent-PRD 原生读取 INTENT.md 各节，把能力表、验收路径、设计标准和术语表直接映射到 PRD 对应段落，并用校验脚本自动检查覆盖情况。

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
| 第 6 节推迟/放弃 | Out of Scope |

## 校验

`prd_validate.py` 运行 8 项检查：

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

```bash
python skills/intent-prd/scripts/prd_validate.py prd/PRD.md intent-anchor/INTENT.md
```

## 文件结构

```text
intent-prd/
├── SKILL.md
├── README.md
├── templates/
│   └── PRD.md                        ← PRD 模板
├── scripts/
│   └── prd_validate.py               ← 8 项结构与交叉引用检查
└── tests/
    ├── fixtures/valid-prd.md          ← 有效样本
    └── test_prd_validate.py           ← 行为回归测试
```

## 能力边界

Intent-PRD 能够：

- 从 INTENT.md 原生推导 PRD，不需要交接 prompt 注入约束。
- 自动检查保留能力和验收路径的覆盖情况。
- 引用设计标准和术语表约束。

Intent-PRD 做不到：

- 自动判断 PRD 的技术方案是否合理。
- 代替用户确认 PRD 内容。
- 强制 intent-issues 读取 PRD。
