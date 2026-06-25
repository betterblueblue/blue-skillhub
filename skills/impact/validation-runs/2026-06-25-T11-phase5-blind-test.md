# T11 — Phase 5 执行阶段盲测（v4.1, Composer 2.5, 2026-06-25）

- 测试日期：2026-06-25
- runner_model：Composer 2.5
- judge：GLM-5.2
- skill_commit：55276bf（v4.1）
- 路线图优先级：1 — Phase 5 执行阶段盲测

## 触发原因

此前所有盲测（V1-V10, B1-B6）只测到 Phase 4（文档输出）。Phase 5 的实际写操作（写代码、跑测试、执行记录）从未在盲测中验证。本轮补上这一验证空白。

## 环境

- Agent / 模型：Composer 2.5（批量执行模式，agent 自行模拟用户 `确认 Step N`）
- 触发方式：Phase 5 盲测 prompt 批量执行
- 测试目录：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/`（专属副本，源码被实际修改）
- 评审产物：`eval/runs/phase5-blind-2026-06-25/scorecards/E{1,2,3}.scorecard.json`
- 汇总报告：`eval/runs/phase5-blind-2026-06-25/PHASE5-BLIND-TEST-SUMMARY.md`

## 用例

| case | 栈 | skill | 档位 | 分数 | P0 | P1 | 实际写代码 | V 等级 |
|------|-----|-------|:----:|:----:|:--:|:--:|:----------:|--------|
| E1 | node-express-prisma | impact-pro | full | 84 | 0 | 1 | ✅ 7 文件 | Step 1-3 V2 (build), Step 4 V1 (Docker) |
| E2 | python-fastapi-sqlmodel | impact-pro | full | 83 | 0 | 1 | ✅ 4 文件 | Step 1-3 V1, Step 4 V2 (ruff) + V1 (pytest) |
| E3 | java-spring-mybatis | impact | **light** | 93 | 0 | 0 | ✅ 1 文件 | Step 1 V2 (mvn compile) |

**均分：86.7 | P0：0 | P1：2**

## 验证目标达成情况

| 验证点 | 结果 | 证据 |
|--------|------|------|
| 逐 Step 确认 | ✅ 通过 | 3 case 所有写操作有「确认 Step N」 |
| V1-only 连续计数 | ❌ 未通过 | E2 Step 1-3 连续 3 个 V1-only 未暂停 |
| 高风险拦截 | ⚠ 部分通过 | E2 正确拦截 ALTER TABLE；E1 未拦截 Prisma schema 编辑 |
| 执行记录随 Step 补齐 | ✅ 通过 | 3 case 均产出 090-execution-record.md |
| 模型不偷懒 | ✅ 通过 | 3 case 均实际写代码（git diff 确认） |
| Preflight 完成 | ✅ 通过 | 3 case 均产出 060-preflight.md |
| V 等级准确 | ✅ 基本通过 | V2 有真实命令输出；V1 如实标注环境限制 |

## 发现的问题

### P1-1: E1 高风险未拦截

Step 1 编辑 `prisma/schema.prisma` 新增字段，等同于 ALTER TABLE。但模型未标注「高风险」也未单独确认。E2 的 Alembic 迁移则正确拦截。模型可能将「编辑 schema 文件」与「执行 ALTER TABLE」区分对待。

**改进建议**：在 SKILL.md 或 references 中明确：编辑 ORM schema 文件（Prisma / SQLModel / GORM）等同于 ALTER TABLE，需标注高风险。

### P1-2: E2 V1-only 计数未触发暂停

Step 1-3 连续 3 个 V1-only 写入 Step（models.py / items.py / alembic migration），按协议应在 Step 3 后暂停。模型未暂停。根因：模型在 Step 4 才运行 `ruff check`，如果 Step 2 后运行 ruff 即可达 V2 并清零。

**改进建议**：在 Phase 5 规则中强调：每个写入 Step 后应立即尝试可用的验证命令（lint/build），而不是等到最后统一验证。

### P2: E3 的 V2 验证对象偏差

E3 判 light 后，用 `mvn compile` 达到 V2。但 Java 代码未改动，编译 Java 不验证 Vue 改动。Vue 改动实际为 V1。不致命但影响 V 等级准确性。

### 正面发现：E3 正确降级 light

模型正确发现 RuoYi 标准 schema 中 `SysDept.email` 已存在，Mapper/Controller/表单均已支持，缺口仅为列表页未展示邮箱列。因此正确降级为 light。这是模型调查能力的正面表现。

## 结论

- **通过（无 P0）**
- Phase 5 执行阶段盲测验证了模型能走完完整 Phase 1-5 流程，实际写代码、跑测试、产出执行记录
- 发现 2 个 P1：高风险拦截灰色地带 + V1-only 计数未触发
- V1-only 计数的盲测覆盖仍需补测（E3 降级 light 后不满足条件）
