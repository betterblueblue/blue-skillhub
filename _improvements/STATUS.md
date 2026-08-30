# STATUS · 改进项聚合视图

> **单一真值**:全部 backlog 的改进项状态以此文件为准,backlog 文件是证据与详情。
> 每轮复盘/验证后更新对应行。ID 规则:`R{轮次}-{编号}`,如 R1-A1(第一轮第 A1 项)。

| ID | 标题 | 首次发现 | 状态 | 涉及轮次 | 备注 |
|---|---|---|---|---|---|
| R1-A1 | 验收环节从未运行 | R1 | verified | R1→R2 | chain_validate 已 FAIL 拦截 |
| R1-A2 | 无链级门禁(verify 缺失) | R1 | verified | R1→R2 | 同上 |
| R1-A3 | dev 完成假象无警告 | R1 | fixed | R1→R2 | SKILL 指引级,卡 3 验证 |
| R1-B1 | 真值压缩无反向追溯 | R1 | fixed | R1→R2 | V13 追溯校验,卡 2 验证 |
| R1-B2 | 页面清单规则未触发 | R1 | fixed | R1→R2 | V16 触发面扩大,卡 1 验证 |
| R1-B3 | 校验器声称强制未拦截 | R1 | fixed | R1→R2 | V16/V17 已实现,卡 1 验证 |
| R1-B4 | 1:1 判定靠 Agent 自觉 | R1 | fixed | R1→R2 | 追溯表落地后消解 |
| R1-C1 | 走查粒度路径≠页面 | R1 | fixed | R1→R2 | Phase 3.5,卡 5 验证 |
| R1-C2 | 走查无数据准备/清理 | R1 | fixed | R1→R2 | Phase 1 固定步骤,卡 5 验证 |
| R1-C3 | 性能验证手法未定义 | R1 | fixed | R1→R2 | 三步法,卡 4 验证 |
| R1-C4 | 无数据放大步骤 | R1 | fixed | R1→R2 | 同上,卡 4 验证 |
| R1-C5 | 并发一致性全链路盲区 | R1 | fixed | R1→R2 | CC 类,卡 4 验证 |
| R1-C6 | 安全验证确认型非攻击型 | R1 | fixed | R1→R2 | 六类攻击,卡 4 验证 |
| R1-C7 | 攻击方法论未模板化 | R1 | fixed | R1→R2 | 六类模板,卡 4 验证 |
| R1-D1 | verify 只报告不阻止交付 | R1 | fixed | R1→R2 | V10+A5 门禁,卡 5/6 验证 |
| R1-D2 | 验收缺陷无单可归 | R1 | fixed | R1→R2 | FIX-* 工单,卡 3/5 验证 |
| R1-D3 | 无缺陷闭环循环 | R1 | fixed | R1→R2 | 定向复验规则,卡 5 验证 |
| R1-D4 | 验收不沉淀可复跑资产 | R1 | fixed | R1→R2 | snapshots/ 约定,卡 5 验证 |
| R1-E1 | verify 职责过重 | R1 | fixed | R1→R2 | 拆出 intent-adversarial |
| R1-E2 | 链路完成无硬性定义 | R1 | verified | R1→R2 | chain_validate 状态矩阵 |
| R2-IMP1 | impact 执行后缺风险驱动定向回归 | R2 | fixed | R2 | 回归维度镜像表,V25 校验,卡 7 验证 |
| R2-IMP2 | 改进沉淀未接入 _improvements 回流 | R2 | fixed | R2 | 改进记录提示改指 _improvements,卡 7/卡 8 |

**状态定义**:open(待修复)→ fixed(代码/规则已改)→ verified(下轮实战确认有效)→ regressed(实战中复发,重新打开)。

## 归因分布趋势(每轮验证后追加一行)

| 轮次 | 校验器缺口 | SKILL 指引不够 | Agent 违反指引 | 备注 |
|---|---|---|---|---|
| R2(impact/pathfinder 审查) | 2 | 0 | 本轮为 skill 侧审查,实战归因待下项目 |
