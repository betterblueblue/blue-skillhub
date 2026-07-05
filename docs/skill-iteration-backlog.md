# Pathfinder / Impact 迭代清单

> 目的：记录还不适合立刻加重门禁的优化项。后续 agent 拿到真实使用日志、失败样本或复跑结果后，按这里继续更新。

## 更新规则

- 先写证据，再改规则：每个新增门禁最好来自至少 3 个同类日志，或 1 个明确 P0/P1 失败。
- 能脚本验证的优先脚本化；不能脚本验证的先放模板或使用记录，不急着写硬规则。
- 简单需求不能被复杂流程拖慢。任何新增检查都要说明它只影响哪些模式：Pathfinder / Impact light / Impact full / Phase 5。
- 更新本文件时，保留旧项的状态，不删除历史判断；完成后把状态改为 `done` 并链接到对应脚本、模板、测试或评测记录。

## P0 已落地

| 项 | 状态 | 落地位置 | 验证 |
|---|---|---|---|
| Pathfinder facts schema 固定 | done | `skills/pathfinder/references/facts-schema.md`、`pf_scan.py`、`pf_git.py`、`pf_validate.py` V6 | `test_v6_legacy_facts_schema_fails` |
| Pathfinder 地图过期检查 | done | `pf_validate.py` V9/V11 | `test_v11_current_head_mismatch_fails` |
| Impact 记录 Pathfinder 消费情况 | done | `templates/000-context-pack.md`、`phase-2-context-discovery.md`、`impact_validate.py` V22 | `TestV22PathfinderConsumption` |
| Phase 4 文档授权口径 | done | `skills/impact/SKILL.md`、`references/phase-4-output.md` | `quick_validate` + 现有 validator 测试 |
| 收尾使用记录 | done | `skills/pathfinder/SKILL.md`、`skills/impact/SKILL.md`、根 README | 人工检查最终回复格式 |

## P1：等真实日志后做

| 项 | 触发条件 | 建议做法 | 完成标准 | 状态 |
|---|---|---|---|---|
| Pathfinder 核心模块漏扫 | 使用日志里出现入口、路由、核心包漏掉 | 增加入口候选/模块候选扫描脚本，输出给 Phase 2/3 | 漏扫样本能被脚本提示，地图【13】能解释未覆盖原因 | todo |
| Pathfinder 推断写成事实 | 地图把无证据结论标成【已核实】 | 强化 `pf_validate.py` 证据路径检查：`【已核实】` 后必须包含可解析证据或命令来源 | 旧失败样本从 PASS 变 FAIL/WARN | todo |
| Impact 语义验收不足 | validator 全绿但业务没改对 | 为高频场景补任务验收 fixture；优先字段/API/权限/配置四类 | 至少 1 个真实失败样本被新 fixture 复现并拦住 | todo |
| Impact light/full 判档偏差 | 简单需求被做重，或复杂需求被判轻 | 收集误判样本，调整 V7 和判档模板；不要只加口号 | 新规则能降低误判，不增加 light 常规噪音 | todo |
| Step 确认体验摩擦 | 用户频繁卡在 Step 确认或问“我该确认什么” | 改写 Step 模板，让写入对象、风险、回滚、验证更短 | 使用记录显示确认来回轮次减少 | todo |

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
