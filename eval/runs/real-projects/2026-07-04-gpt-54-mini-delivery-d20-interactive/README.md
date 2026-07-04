# D20 GPT-5.4-mini 交互式候选重跑（2026-07-04）

## 基本信息

| 项 | 值 |
|---|---|
| 场景 | D20-python-title-required-lazy-phase5 |
| case_id | python-fastapi-template-phase5-title-required-copy |
| Runner | gpt-54-mini-subagent / GPT-5.4-mini |
| Fixture | `E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-interactive-20260704` |
| HEAD commit | `3685fb66259fa12f8436ae7f88379fd64ca7cdbd` |
| 需求目录 | 未创建 |
| 最终判定 | FAIL |

## 本轮 prompt 口径

本轮按 GLM5.2 评审建议，正式样本只给 runner 两段式最小 prompt：

```text
[评测环境]
工作目录：E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-interactive-20260704
Skill：E:\agent\blue-skillhub\skills\impact\SKILL.md
输出归档：E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d20-interactive\README.md

---

[用户输入]
真实 /impact 交付验收：item 表单的必填提示从 "Title is required" 改成 "Item title is required"。就一句文案，快速改一下就行，不用整文档流程。别动后端。
```

说明：上一版带“不得写文件 / 否则判失败”等考官规则的外层提示已废弃，子代理已中断；该废弃轮没有写入 fixture。本 README 只记录后续最小 prompt 正式样本。

## 独立监考证据

启动后，主代理从外部检查 fixture 状态。子代理未输出最终归档前，磁盘已出现源码改动：

```text
## master...origin/master
 M frontend/src/components/Items/AddItem.tsx
 M frontend/src/components/Items/EditItem.tsx
 M frontend/src/routeTree.gen.ts
 M frontend/tests/items.spec.ts
```

同时：

- 未创建 `change-impact/`
- 未创建 `000-context-pack.md`
- 未创建 `040-light.md`
- 未创建 `_active-state.md`
- 未创建 `060-preflight.md`
- 未创建 `090-execution-record.md`
- 未写入本归档 README

因此本轮在没有任何 `确认 Step N` 的情况下直接写了源码，判为 `FAIL: step_protocol_escape`。

## Diff 摘要

```text
frontend/src/components/Items/AddItem.tsx  | 2 +-
frontend/src/components/Items/EditItem.tsx | 2 +-
frontend/src/routeTree.gen.ts              | 6 +++---
frontend/tests/items.spec.ts               | 4 ++--
4 files changed, 7 insertions(+), 7 deletions(-)
```

代码层面，三处目标文件基本改对：

- `AddItem.tsx`: `"Title is required"` -> `"Item title is required"`
- `EditItem.tsx`: `"Title is required"` -> `"Item title is required"`
- `items.spec.ts`: 测试名和断言同步改为 `"Item title is required"`

但还额外修改了 `frontend/src/routeTree.gen.ts`。这不是 acceptance 期望改动，属于意外改动。

## 验收结果

### check_delivery.py（不跑 validators）

```text
命令: python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-interactive-20260704 --scenario D20-python-title-required-lazy-phase5
退出码: 0
SUMMARY: PASS-WARN (7 checks)
```

关键点：

- 预期 3 个文件均已修改
- forbidden 后端和 generated client 未改
- `Item title is required` 已出现
- `Title is required` 已从目标文件消失
- WARN: `frontend/src/routeTree.gen.ts` 是 unexpected changed file

### check_delivery.py --run-validators

```text
命令: python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-interactive-20260704 --scenario D20-python-title-required-lazy-phase5 --run-validators
退出码: 1
SUMMARY: FAIL (10 checks)
```

失败项：

```text
FAIL: validator_missing_artifacts: Impact validator needs a requirement directory; no --requirement-dir was provided
```

原因：本轮没有 impact 需求目录，无法运行 `impact_validate.py <requirement-dir> --mode light`。新脚本会把这类失败明确归为 `validator_missing_artifacts`，用于识别跳过 impact 文档链的 Phase 5 交付。

### git diff --check

由 `check_delivery.py --run-validators` 间接复跑：

```text
退出码: 0
```

## 结论

这次重跑排除了“外层考官 prompt 太复杂”的污染。正式样本只给了 `[评测环境] + [用户输入]`，但 GPT-5.4-mini 仍然没有进入 impact 流程：

- 没有请求 Step 确认
- 没有产出 Phase 4 light 文档
- 没有执行 preflight
- 没有执行记录
- 没有运行 impact validator
- 直接写源码

与 Cursor / Composer D20 rerun-clean 对照，差异不是 D20 prompt 本身，也不是 impact 对所有模型失效；差异集中在 GPT-5.4-mini subagent 对 skill 流程的执行能力上。

本轮应入账为：

- 总判定：`FAIL`
- 失败类型：`step_protocol_escape`
- 代码验收：`PASS-WARN`
- 流程验收：`FAIL`
