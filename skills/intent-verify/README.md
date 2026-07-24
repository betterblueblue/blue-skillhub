# Intent-Verify

> 所有工单开发完成后的整体验收。先跑全量测试确认老功能没被改坏，再端到端走通验收路径，最后做条件性验证和最终复核。

## 为什么需要它

intent-dev 完成了每个工单的开发和工单级验证（零件合格），但零件合格不代表整机没问题。intent-verify 做的是：

1. **回归验证**：跑全量测试，确认工单改动没有把老功能改坏。
2. **端到端验收**：按 INTENT.md 第 14 节的验收路径，逐条从头到尾走通，确认用户真正用的时候能用。
3. **条件性验证**：如果 INTENT.md 或 PRD 中有性能或安全要求，逐项验证。没有就标不适用。
4. **最终复核**：保留能力核对 + 漂移复核，确认没有偷偷丢掉或加上什么。

## 验证等级

| 等级 | 含义 | 证据要求 |
|---|---|---|
| V3 | 端到端验证通过 | 验收路径实际走通的证据 |

**标 V3 但没有实际走通的证据 → 不通过。**

## 什么时候使用

适合：

- intent-dev 已完成，dev-record 通过 `dev_validate.py` 校验。
- 所有工单标 done。
- 开始进入端到端验收阶段。

不适合：

- 还有工单未完成（先回 intent-dev）。
- 没有 dev-record（先走 intent-dev）。

## 校验

`verify_validate.py` 运行 6 项检查：

| 检查项 | 检查内容 |
|---|---|
| V1 | 文件非空 |
| V2 | 有回归验证段（全量测试命令和结果） |
| V3 | 每条验收路径有 Given/When/Then 和验证方式 |
| V4 | 每条路径有 V3 证据 |
| V5 | 有条件性验证段（性能验证和安全验证，不适用也要标注） |
| V6 | 最终复核完整（回归汇总、保留能力、验收路径、条件性汇总、漂移复核、结论） |

```bash
python skills/intent-verify/scripts/verify_validate.py verify/VERIFY-RECORD.md
```

## 文件结构

```text
intent-verify/
├── SKILL.md
├── README.md
├── templates/
│   └── VERIFY-RECORD.md              ← 验收记录模板
├── scripts/
│   └── verify_validate.py            ← 6 项结构检查
└── tests/
    ├── fixtures/
    │   └── valid-verify-record.md    ← 有效样本
    └── test_verify_validate.py       ← 行为回归测试
```

## 能力边界

Intent-Verify 能够：

- 跑全量测试确认老功能没被改坏。
- 按 INTENT.md 的验收路径逐条端到端验证。
- 按 INTENT.md 的性能和安全要求做条件性验证。
- 核对保留能力是否都有实现或验证证据。
- 检查 7 种漂移模式是否命中。
- 通过校验器检查 verify-record 的结构完整性。

Intent-Verify 做不到：

- 代替用户开发代码或测试。
- 自动生成 E2E 测试脚本（可以运行已有的，不能自己写）。
- 重新验工单的验收标准（那是 intent-dev 的事）。
- 强制用户修复未通过项（只报告结果，不阻止交付）。
