# Intent-Issues

> 读取 INTENT.md 和 PRD，按垂直切片拆分工单，自动检查验收路径覆盖。

## 为什么需要它

PRD 生成后需要拆分为独立可抓取的工单。使用第三方 to-issues 时，验收路径约束只能通过交接 prompt 注入，工单的 Acceptance criteria 不会自动引用路径编号，也无法自动检查覆盖情况。如果没有 INTENT.md，直接用原版 to-issues 即可。

Intent-Issues 原生读取 INTENT.md 的验收路径，在工单的 Acceptance criteria 中自动引用路径编号，并在输出前自动检查所有路径被至少一个工单覆盖。

## 什么时候使用

适合：

- intent-prd 已完成，PRD 通过 `prd_validate.py` 校验。
- 需要把 PRD 拆分为工单，进入开发阶段。

不适合：

- 没有 INTENT.md 或 PRD（先运行前置 skill）。
- PRD 未通过校验（先修正）。

## 垂直切片规则

- 每个工单交付一条贯穿所有层（schema、API、UI、测试）的完整路径。
- 完成的工单可以独立演示或验证。
- 偏好多个薄切片，而非少数厚切片。
- 工单可以是 HITL（需人工交互）或 AFK（可自动完成）。优先 AFK。

## 校验

`issues_validate.py` 运行 5 项检查：

| 检查项 | 检查内容 |
|---|---|
| V1 | 文件非空 |
| V2 | 每个工单包含 4 个必需子节 |
| V3 | 所有验收路径被至少一个工单覆盖 |
| V4 | 所有保留能力被至少一个工单覆盖 |
| V5 | Coverage Verification 包含三个子节且与 INTENT.md 一致 |

```bash
python skills/intent-issues/scripts/issues_validate.py issues/issues.md intent-anchor/INTENT.md
```

## 文件结构

```text
intent-issues/
├── SKILL.md
├── README.md
├── templates/
│   └── issue-template.md             ← 工单模板
├── scripts/
│   └── issues_validate.py            ← 5 项结构与交叉引用检查
└── tests/
    ├── fixtures/valid-issues.md       ← 有效样本
    └── test_issues_validate.py        ← 行为回归测试
```

## 能力边界

Intent-Issues 能够：

- 从 PRD 原生推导工单，按垂直切片拆分。
- 自动检查验收路径和保留能力的覆盖情况。
- 把设计标准和术语表约束传递到工单。

Intent-Issues 做不到：

- 自动判断工单的技术可行性。
- 代替用户确认工单拆分。
- 自动发布到 issue tracker（产出的是 markdown 文件，用户自行复制）。
