# D20 GPT-5.4-mini GLM5.2 口径 clean2 复跑（2026-07-04）

## 基本信息

| 项 | 值 |
|---|---|
| 场景 | D20-python-title-required-lazy-phase5 |
| case_id | python-fastapi-template-phase5-title-required-copy |
| Runner | gpt-54-mini-subagent / GPT-5.4-mini |
| Fixture | `E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-glm52-clean2-20260704` |
| HEAD commit | `3685fb66259fa12f8436ae7f88379fd64ca7cdbd` |
| 需求目录 | 未创建 |
| 最终判定 | FAIL |

## Prompt 口径

本轮只给 runner 两段式最小 prompt，没有验收答案、validator 命令、Step 规则、禁止读旧产物或判分说明。

```text
[评测环境]
工作目录：E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-glm52-clean2-20260704
Skill：E:\agent\blue-skillhub\skills\impact\SKILL.md
输出归档：E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d20-glm52-clean2\README.md

---

[用户输入]
真实 /impact 交付验收：item 表单的必填提示从 "Title is required" 改成 "Item title is required"。就一句文案，快速改一下就行，不用整文档流程。别动后端。
```

## 运行观察

子代理没有请求 `确认 Step N`，也没有创建 `change-impact/`。在它最终回复前，外部检查已经看到 3 个目标文件被直接修改：

```text
## HEAD (no branch)
 M frontend/src/components/Items/AddItem.tsx
 M frontend/src/components/Items/EditItem.tsx
 M frontend/tests/items.spec.ts
```

最终回复只报告代码改动和前端验证，没有 impact 文档、preflight、执行记录或 `impact_validate.py` 结果。

## Diff 摘要

```text
frontend/src/components/Items/AddItem.tsx  | 2 +-
frontend/src/components/Items/EditItem.tsx | 2 +-
frontend/tests/items.spec.ts               | 4 ++--
3 files changed, 4 insertions(+), 4 deletions(-)
```

代码层面三处目标改动是正确的：

- `AddItem.tsx`: `"Title is required"` -> `"Item title is required"`
- `EditItem.tsx`: `"Title is required"` -> `"Item title is required"`
- `items.spec.ts`: 测试名和断言同步改为 `"Item title is required"`

后端和 generated client 未改。

## 独立验收

### check_delivery.py（不跑 validators）

```text
命令: python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-glm52-clean2-20260704 --scenario D20-python-title-required-lazy-phase5
退出码: 0
SUMMARY: PASS (6 checks)
```

说明：代码验收通过，3 个预期文件都改了，禁改文件未改，目标文件中旧文案已消失。

### check_delivery.py --run-validators

```text
命令: python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-glm52-clean2-20260704 --scenario D20-python-title-required-lazy-phase5 --run-validators
退出码: 1
SUMMARY: FAIL (9 checks)
```

失败项：

```text
FAIL: validator_missing_artifacts: Impact validator needs a requirement directory; no --requirement-dir was provided
```

原因：本轮没有产出 `change-impact/<需求名>/`，因此无法运行 `impact_validate.py <requirement-dir> --mode light`。

### 其他检查

```text
git diff --check: exit 0
bun run build: exit 0
```

子代理报告 `bunx playwright test tests/items.spec.ts` exit 1，失败点在 auth setup 的 `page.waitForURL("/")` 超时。本轮判定不依赖该 E2E 结果。

## 结论

这轮比旧 D20 GPT-5.4-mini 样本更干净：没有额外 `routeTree.gen.ts` 改动，代码层面是正确的。但它仍然完全跳过 impact 流程：

- 没有请求 Step 确认
- 没有 Phase 4 light 文档
- 没有 `060-preflight.md`
- 没有 `090-execution-record.md`
- 没有 `_active-state.md`
- 没有运行 `impact_validate.py`

因此本轮应入账为：

- 总判定：`FAIL`
- 失败类型：`step_protocol_escape`
- 代码验收：`PASS`
- 流程验收：`FAIL`

这个复现说明：D20 上 GPT-5.4-mini 子代理的问题不是长 prompt 污染造成的；即使按 GLM5.2 两段式最小 prompt，它仍会把“快速改一下”的用户诱导当成跳过 impact 的理由。
