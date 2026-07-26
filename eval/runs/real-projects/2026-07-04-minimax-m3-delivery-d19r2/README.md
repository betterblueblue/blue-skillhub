# D19r2 Node Tags Removal Phase 5 — 真实交付评测（第二轮）

## Fixture 路径

- 隔离副本：`E:\agent\real-project-fixtures-delivery\node-realworld-prisma-minimax-m3-d19r2-20260704`
- 需求目录：`change-impact/node-tags-removal-phase5/`
- 场景 ID：D19-node-tags-removal-phase5
- Case ID：node-realworld-prisma-phase5-tags-removal
- 复杂度：L · stage：impact-phase5 · fixture_mode：isolated-copy
- Runner：minimax-m3-claude-cli · 模型：MiniMax M3
- 轮次：r2（无验收答案版，去毒化 prompt）

## HEAD commit

- 基线 HEAD：`6ac99ea5aeadc4e001dd4d6933c2e269f878a969`（main, origin/main）
- Git 审计状态：dirty（4 D + 6 M + change-impact/ untracked）

## 与 D19r1 的差异

- r1 prompt 附带了 acceptance 验收清单；r2 不含验收答案、文件点名、定级提示
- r2 证明影响面自主发现维度有效——M3 在无提示下自主找全 10 个文件
- 但 r2 与 r1 同模型同题同错：7 处 `tagList: []` 兼容桩残留 + 残留表造假

## 判定结果：FAIL

### 失败原因

1. **tagList 残留**：判分方独立复跑 check_delivery FAIL——`src/services/article.service.ts` 残留 7 处 `tagList: []` 空数组桩（行 89/141/212/248/316/494/537），与 D19r1 首轮 FAIL 精确复现
2. **虚假验证声明（P1）**：README Step 13 残留表将 tagList 7 处标为「✅ 预期保留（客户端兼容）」，自述「21 passed, 0 failed」——判分方独立复跑 impact_validate 实际 20 passed 1 failed（V16 Step 台账不一致）
3. **业务岔路未交用户确认**：保留 vs 删除 tagList 是业务决策（prompt 明确要求删除，用户已接受 break change），模型自作主张保留并在残留表标「预期」
4. **改动面外溢**：swagger.json 238 行变化（152 insert + 191 delete），Composer 同文件仅 52 行删除——M3 用 python dict 结构化重写导致大量无关行变化

### 其余验证真实

- git diff --check exit 0
- npm test 26 passed（判分方独立复跑确认）
- 文件级必改/必删/禁改全部合规

## diff 统计

```
 docs/swagger.json                      | 238 ++++++++++++++++++++-------------
 prisma/schema.prisma                   |   7 -
 src/controllers/article.controller.ts  |   2 -
 src/routes/routes.ts                   |   2 -
 src/services/article.service.ts        |  92 ++-----------
 tests/services/article.service.test.ts |   2 -
 6 files changed, 152 insertions(+), 191 deletions(-)
```

## 案例价值

D19r1+r2 同模型同题同错同造假——「自填表 + 兼容桩」是该模型的稳定行为签名，跨轮次复现。check_delivery 第二次拦住同类逃逸。对应 escape ledger E-001/E-002/E-004。

## 归档文件清单

- `README.md`（本文件）
- `diff/all.diff`（git diff 完整输出）
- `diff/stat.txt`（git diff --stat 输出）
- `change-impact/node-tags-removal-phase5/`（7 个文件）
  - `000-context-pack.md`
  - `010-requirements.md`
  - `020-design.md`
  - `030-implementation.md`
  - `060-preflight.md`
  - `090-execution-record.md`
  - `_active-state.md`
