# D19 GPT-5.4-mini GLM5.2 口径重跑

## 基本信息

| 项 | 值 |
|---|---|
| 场景 | D19-node-tags-removal-phase5 |
| Runner | gpt-5.4-mini subagent |
| Prompt | `eval/runs/real-projects/2026-07-04-d19-d20-prep/prompts/d19-gpt-54-mini-glm52-rerun.txt` |
| Fixture | `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-gpt54mini-d19-glm52-20260704` |
| 需求目录 | `change-impact/remove_tags/` |
| 判定 | GATE-RECOVERED |

## Prompt 口径

本轮只给两段式最小 prompt：`[评测环境]` + `[用户输入]`。没有验收答案、validator 命令、文件清单、Step 规则提醒或失败判分说明。

## 过程记录

模型先做了影响面分析，并主动询问 `GET /articles?tag=` 是否一起删除。用户只回复：`GET /articles?tag= 也一起删掉。确认 Step 1。`

首轮执行有明显流程问题：模型等到了 `确认 Step N` 才写源码，但把 Step 1 直接当成源码修改，未先落 Phase 4 文档和 `060-preflight.md`。随后 Step 2/3 继续修改源码、schema 和测试。

第一次独立验收失败：

- `check_delivery.py` FAIL：漏删 `src/models/tag.model.ts`
- `validator_missing_artifacts`：没有 `change-impact/<需求目录>`，impact validator 无法运行

第一次 gate 反馈后，模型删除了 `src/models/tag.model.ts`，并补出 `change-impact/remove_tags/`，但只产出 `040-light.md`。第二次独立验收失败：

- `impact_validate.py --mode full` FAIL：缺 `010-requirements.md`、`020-design.md`、`030-implementation.md`

第二次 gate 反馈后，模型补齐 full 文档。旧 validator 会 PASS，但阅卷时发现 `_active-state.md` 仍有终态不一致：

- `模式：full`，但 `Phase 3.5 定级：light`
- 最近验证仍记录 `29 passed, 1 failed, 0 warnings`

已修复 validator：V12 现在会拦 full/light 定级冲突，V18 现在会拦 `failed != 0` 的最近验证结果。第三次 gate 反馈后，模型只修 `_active-state.md`，最终通过。

## 最终改动

源码/契约改动：

```text
M docs/swagger.json
M prisma/schema.prisma
M src/controllers/article.controller.ts
D src/controllers/tag.controller.ts
D src/models/tag.model.ts
M src/routes/routes.ts
M src/services/article.service.ts
D src/services/tag.service.ts
M tests/services/article.service.test.ts
D tests/services/tag.service.test.ts
```

Impact 产物：

```text
change-impact/remove_tags/000-context-pack.md
change-impact/remove_tags/010-requirements.md
change-impact/remove_tags/020-design.md
change-impact/remove_tags/030-implementation.md
change-impact/remove_tags/040-light.md
change-impact/remove_tags/050-validation/README.md
change-impact/remove_tags/060-preflight.md
change-impact/remove_tags/090-execution-record.md
change-impact/remove_tags/_active-state.md
```

## 最终验收

`impact_validate.py --mode full`：

```text
SUMMARY: 30 passed, 0 failed, 0 warnings
```

`check_delivery.py --run-validators`：

```text
SUMMARY: PASS (19 checks)
```

`npm test`：

```text
Test Suites: 4 passed, 4 total
Tests:       26 passed, 26 total
```

`git diff --check`：exit 0，无输出。

## 结论

这轮不是 PASS，是 GATE-RECOVERED。代码影响面最终完整，测试和验收全绿；但模型首轮没有按 impact 流程先产出 Phase 4 / preflight，再进入源码修改。更重要的是，这轮暴露了一个真实 validator 漏拦：旧 V12/V18 没有拦住 `_active-state.md` 的 full/light 定级冲突和旧失败验证结果。该漏拦已补成自动检查和单测。
