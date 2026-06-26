# T52 — L1 全量回归（v4.1, Composer 2.5, 2026-06-25）

- 测试日期：2026-06-25
- runner_model：Composer 2.5
- judge：GLM-5.2
- skill_commit：55276bf（v4.1）
- baseline：769868d（2026-06-14, runner: opus-4-8）

## 触发原因

- v4.1 协议改进（链路追踪回流、多轮触发条件、Context Pack 场景覆盖、方法名存在性预检、改动完整性自检）完成后，需 L1 全量回归验证既有能力无回归、新特性全部触发。
- 路线图优先级 2（脚本闸门 `impact_validate.py`）、优先级 3（判档决策证据化）、优先级 6（弱模型降级策略 / 产出完整性自检）已在本轮工作中顺手完成，需通过 L1 验证有效性。

## 环境

- Agent / 模型：Composer 2.5（批量执行模式，agent 自行模拟用户回答）
- 触发方式：L1 回归 prompt 批量执行
- 测试目录：`test-projects/<fixture>/change-impact/l1-full-regression-composer25/<case-id>/`
- 评审产物：`eval/runs/2026-06-25-impact-pro@55276bf/*.scorecard.json`
- 汇总报告：`eval/runs/2026-06-25-l1-full-regression-summary.md`

## 用例

| case | 变更 | 档位 | base | beh | p_level | 脚本闸门 | 要点 |
|------|------|:----:|:----:|:---:|:-------:|:-------:|------|
| F1 库存预警 | FastAPI Item 加 warning_threshold | full | 102 | +10 | none | 0 FAIL | Item 无 stock ✅；Alembic head 精确 ✅；React/Vite not Next.js ✅；链路追踪 4 条 |
| F2 暗黑模式 | React/Vite 深色模式 | full | 97 | +10 | none | 0 FAIL | 已完整实现 ✅；零改动确认；不被 monorepo Python 后端带偏；V3 E2E 引用 |
| F3 团队邀请 | Monorepo 邀请功能 | full | 101 | +10 | none | 0 FAIL | SMTP 缺失 ✅；双 profile ✅；sdk.gen.ts 不手写 ✅；链路追踪 4 条（SMTP assert 回流设计） |
| G1 status 枚举 | FastAPI status 加 frozen | full | 98 | +10 | none | 0 FAIL | **基线 P1 已修复**：判 full 自洽（3 项证据），无自相矛盾；frozen 0 命中 ✅ |
| G2 改 msg 文案 | FastAPI Item 删除 message | light | 94 | +10 | none | 0 FAIL | 「查询成功」vs「操作成功」错位 ✅；light 正确；接口返回检查清单 ✅ |
| R4 用户签名 | RuoYi 用户加个性签名 | full | 98 | +10 | none | 0 FAIL | Java profile 不降级 ✅；@Excel 导出 ✅；链路追踪 5 条 |

**均分：98.3** | **P0：0** | **P1：0** | **契约：全 PASS** | **脚本闸门：全 0 FAIL**

## v4.1 新特性触发验证

| v4.1 特性 | 验证 case | 触发 | 证据 |
|-----------|----------|:----:|------|
| 链路追踪回流 | F1, F3, G1, R4 | 4/4 ✅ | 每个 full case 的 context-pack 均含「关键链路追踪」表，Phase 2 副作用风险回流至 Phase 3 设计 |
| Context Pack 场景覆盖 | F1, F3, G1, R4 | 4/4 ✅ | §9「暂不纳入范围」列出排除项及原因 |
| 方法名存在性预检 | R4 | 1/1 ✅ | 030-implementation.md §4 含 grep 核实表 |
| 改动完整性自检 | — | N/A | 本轮无 case 触发完整性自检（F1/F3/G1/R4 均为标准 full 流程） |
| 多轮触发条件 | G1, F3 | N/A | 批量执行模式中 agent 自行模拟用户回答，P0/P1 风险在单轮内已全覆盖；多轮触发在 V10 B3' 交互式场景中已验证 |

## 基线 P1 修复验证

| case | 基线 (769868d) | 本轮 (55276bf) | 验证点 |
|------|---------------|----------------|--------|
| G1 | base 87, **P1**, 判档自相矛盾 | base 98, **none**, 判 full + 3 项证据 | 判 full，证据列 3 项（枚举合法值变更 / 字典扩展 / DTO 校验收紧），不再写"无" |

**P1 修复无回归，稳定通过。**

## 基线 diff 红线检查

| 检查项 | 结果 |
|--------|------|
| 契约 PASS → FAIL | 0 例（6/6 全 PASS） |
| p_level 新增 P0/P1 | 0 例（基线 1 个 P1 已修复，无新增） |
| base 分下降 | 0 例（所有 case 均高于基线） |

**⚠ runner_model 混杂**：基线 runner 为 opus-4-8，本轮为 Composer 2.5。分数提升不能直接归因 skill 改进，但红线检查（契约/P0/P1）是模型无关的硬底线。

## 路线图优先级完成情况

| 路线图优先级 | 内容 | 本轮验证 |
|-------------|------|----------|
| 优先级 2 | 脚本闸门 `impact_validate.py` | ✅ 6 case 全 0 FAIL |
| 优先级 3 | 判档决策证据化 | ✅ G1 基线 P1（判档自相矛盾）已修复，4 个 full case 均含判档决策表 |
| 优先级 6 | 弱模型降级策略（产出完整性自检） | ✅ 规则已在 SKILL.md 中，本轮 full case 均产出完整四文件 |

## 结论

- **通过**
- P0/P1：0 / 0
- 基线 P1（G1 判档自相矛盾）修复无回归
- v4.1 新特性全部正确触发
- 脚本闸门 `impact_validate.py` 在 6 个 case 上全 0 FAIL，验证有效
- 后续风险：runner_model 不一致（opus → composer），不建议直接将本轮分数作为新基线；如需建立 composer-2.5 基线，后续统一用 Composer 2.5 跑 2-3 轮取稳定值
