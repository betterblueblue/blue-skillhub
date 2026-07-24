# Intent-Dev

> 按 TDD 循环开发每个工单，工单完成后实际运行验证确认通过。检查的是每个零件合不合格。

## 为什么需要它

intent-issues 产出工单后，开发阶段缺少两样东西：

1. **开发纪律**：没有 TDD，可以先写代码再补一个永远通过的测试，测试质量很低。
2. **验证纪律**：工单做完直接标 done，没人实际跑验证确认。

Intent-Dev 解决这两个问题：

1. **TDD 循环**：先写测试看到红灯 → 写代码看到绿灯 → 重构。修 bug 必须先写复现测试。
2. **实际验证**：探索项目找到验证命令，实际运行，根据真实输出判定每条 Then 的验证等级。

## TDD 规则

按工单类型适用不同规则：

| 工单类型 | TDD 要求 | 说明 |
|---|---|---|
| 新功能 | 推荐 Red-Green-Refactor | 先写测试看到失败，再写代码看到通过 |
| 修 bug | 必须先写复现测试 | 先写测试复现 bug，再修代码 |
| 纯样式/配置 | 不要求 TDD | 直接写代码，实际运行看结果 |

## 验证等级

| 等级 | 含义 | 证据要求 | 能否标 done |
|---|---|---|---|
| V0 | 未验证 | 无 | 不能 |
| V1 | 代码审查 | 代码位置和审查结论 | 不能单独标 done |
| V2 | 实际运行验证通过 | 真实命令 + 输出摘要 | 可以 |

**标 V2 但没有真实命令输出 → 视为 V1 冒充，不允许标 done。**

## 什么时候使用

适合：

- intent-issues 已完成，工单文件通过 `issues_validate.py` 校验。
- 开始进入开发阶段。

不适合：

- 没有 INTENT.md、PRD 或工单文件（先运行前置 skill）。
- 所有工单已开发完成（该用 intent-verify 做端到端验收）。

## 校验

`dev_validate.py` 运行 4 项检查：

| 检查项 | 检查内容 |
|---|---|
| V1 | 文件非空 |
| V2 | 每个工单有开发记录段（含 TDD 过程、验证结果、工单状态），且工单编号与 issues.md 一致 |
| V3 | 每条 Then 有验证等级，V2 必须附命令输出 |
| V4 | 标 done 的工单：所有 Then >= V2（用户确认 V1 标 done 除外） |

```bash
python skills/intent-dev/scripts/dev_validate.py intent-chain/{链路目录}/dev-record.md intent-chain/{链路目录}/issues.md
```

## 文件结构

```text
intent-dev/
├── SKILL.md
├── README.md
├── templates/
│   └── dev-record.md                 ← 开发执行记录模板
├── scripts/
│   └── dev_validate.py               ← 4 项结构与交叉引用检查
└── tests/
    ├── fixtures/
    │   ├── valid-dev-record.md       ← 有效样本
    │   └── valid-issues.md           ← 工单样本（交叉校验用）
    └── test_dev_validate.py          ← 行为回归测试
```

## 能力边界

Intent-Dev 能够：

- 按 TDD 循环管理每个工单的开发过程。
- 探索目标项目，发现真实的构建和测试命令。
- 实际运行验证命令，捕获真实输出。
- 根据命令输出判定每条 Then 的验证等级。

Intent-Dev 做不到：

- 代替用户写代码和测试。
- 做端到端验收（那是 intent-verify 的事）。
- 强制用户修复未通过项（只阻止进下一个工单）。
