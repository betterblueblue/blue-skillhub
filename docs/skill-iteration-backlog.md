# Pathfinder / Impact 迭代清单

> 目的：记录还不适合立刻加重门禁的优化项。后续 agent 拿到真实使用日志、失败样本或复跑结果后，按[经验进入核心规则的条件](skill-eval/rule-promotion.md)继续更新。

## 更新规则

- 先登记 `RC-NNN` 候选，再改规则。P0/P1 需要 1 个可复现的真实失败；P2 通常需要至少 3 个同类记录。完整受理条件见 `skill-eval/rule-promotion.md`。
- 能脚本验证的优先脚本化；不能脚本验证的先放模板或使用记录，不急着写硬规则。
- 简单需求不能被复杂流程拖慢。任何新增检查都要说明它只影响哪些模式：Pathfinder / Impact light / Impact full / Phase 5。
- 更新本文件时保留旧项，不删除历史判断。候选状态使用 `waiting-evidence / reproduced / accepted / implemented / verified / rejected`；完成后链接到对应规则、脚本、测试或评测记录。

## P0 已落地

| 项 | 状态 | 落地位置 | 验证 |
|---|---|---|---|
| Pathfinder facts schema 固定 | done | `skills/pathfinder/references/facts-schema.md`、`pf_scan.py`、`pf_git.py`、`pf_validate.py` V6 | `test_v6_legacy_facts_schema_fails` |
| Pathfinder 地图过期检查 | done | `pf_validate.py` V9/V11 | `test_v11_current_head_mismatch_fails` |
| Impact 记录 Pathfinder 消费情况 | done | `templates/000-context-pack.md`、`phase-2-context-discovery.md`、`impact_validate.py` V22 | `TestV22PathfinderConsumption` |
| Phase 4 文档授权口径 | done | `skills/impact/SKILL.md`、`references/phase-4-output.md` | `quick_validate` + 现有 validator 测试 |
| 收尾使用记录 | done | `skills/pathfinder/SKILL.md`、`skills/impact/SKILL.md`、根 README | 人工检查最终回复格式 |

## P1：等真实日志后做

| 编号 | 项 | 当前证据 | 影响范围 | 建议做法 | 完成标准 | 状态 |
|---|---|---|---|---|---|---|
| RC-001 | Pathfinder 核心模块漏扫 | 待收集入口、路由或核心包漏扫产物 | Pathfinder Phase 2/3 | 增加入口候选/模块候选扫描脚本，输出给 Phase 2/3 | 漏扫样本能被脚本提示，地图【13】能解释未覆盖原因 | waiting-evidence |
| RC-002 | Pathfinder 推断写成事实 | 待收集无证据却标成【已核实】的地图 | Pathfinder Phase 3/4 | 强化 `pf_validate.py` 证据路径检查 | 修改前失败样本被新检查稳定拦住 | waiting-evidence |
| RC-003 | Impact 语义验收不足 | 待收集 validator 全绿但业务未改对的产物 | Impact light/full Phase 5 | 为字段、API、权限、配置等高频场景补任务验收 fixture | 至少 1 个明确 P0/P1，或 3 个同类 P2 样本被复现并拦住 | waiting-evidence |
| RC-004 | Impact light/full 判档偏差 | 待收集简单需求做重或复杂需求判轻的记录 | Impact Phase 3.5 | 根据误判样本调整 V7 和判档模板，不只增加口号 | 新规则降低误判，且不增加 light 常规噪音 | waiting-evidence |
| RC-005 | Step 确认体验摩擦 | 待收集确认往返次数和用户困惑记录 | Impact Phase 4/5 | 缩短 Step 模板中的写入对象、风险、回滚和验证说明 | 多个独立任务显示确认往返减少，安全边界不退化 | waiting-evidence |

## 已受理的产品调整

| 编号 | 调整 | 决定来源 | 影响范围 | 做法 | 验证 | 状态 |
|---|---|---|---|---|---|---|
| RC-006 | 改进记录暴露了内部流程，普通用户难以理解 | 2026-07-12 用户明确反馈：“我也不会这么复杂的看不懂的操作啊” | IntentAnchor / Pathfinder / ImpactRadar 收尾交互 | 用户只回答“记录”或“不用”；内部编号、状态和维护文档不面向用户 | [RC-006 验证记录](#rc-006-验证记录) | verified |

### RC-006 验证记录

- 修改前：`tests/test_skill_improvement_prompt.py` 退出码 1，三项 Skill 都因缺少“改进记录提示”而失败。
- 修改后：同一测试退出码 0，2 项检查全部通过。
- 相关回归：IntentAnchor 16 项、Pathfinder Python 35 项、ImpactRadar Python 54 项全部通过；Pathfinder L0 为 43 PASS / 0 FAIL；`git diff --check` 通过。
- 本地限制：ImpactRadar Bash 汇总脚本完成模板同步 10/10 后，因当前捆绑 Python 未安装 `pytest` 而停止。对应的 `test_impact_validate.py` 已用同一 Python 直接运行并通过 54 项；CI 会先安装 `pytest` 再运行完整脚本。

## P2：产品化后做

| 项 | 价值 | 建议做法 | 完成标准 | 状态 |
|---|---|---|---|---|
| 跨客户端安装检查 | 降低新用户上手成本 | 一键检查 skill、脚本、Python、hook、agents metadata 是否可用 | 新用户按 README 能自查安装问题 | todo |
| 小型真实项目矩阵 | 长期判断版本是否退步 | 固定 Java / Node / Python / 前端 / monorepo / 非 Git 样本 | 每次大改可复跑，产出统一评分卡 | todo |
| 失败样本库 | 优化不靠印象 | 按模型、需求、漏点、门禁、修复成本记录 | 每个新门禁能追溯到失败样本 | todo |
| 使用记录归档机制 | 把最终回复里的使用记录沉淀下来 | 先不自动写文件；等用户确认保存规则后再设计 `eval/usage-logs/` | 不增加日常使用负担，日志可被后续统计 | todo |
| 评分卡趋势 | 看质量趋势而不是单次表现 | 记录漏扫、误判、跳确认、假完成、修复成本 | 能比较版本间质量变化 | todo |

## 使用日志最小字段

每次 Pathfinder / Impact 收尾时，agent 已在最终回复里生成使用记录。需要长期沉淀时，优先保留这些字段：

```text
- 日期：
- 模型：
- skill：
- 项目类型：
- 需求类型：
- 模式：
- 是否使用 Pathfinder 地图：
- 验证：
- 出现的问题：
- 门禁是否拦住：
- 最终结果：
- 值得沉淀的改进：
```
