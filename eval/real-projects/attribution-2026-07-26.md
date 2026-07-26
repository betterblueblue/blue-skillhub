# 归因总表（15 条 FAIL / UNVERIFIED，质疑者核实后）

数据来源：`eval/real-projects/delivery-results.json`（59 条记录，12 FAIL + 3 UNVERIFIED，与输入的 15 条一一对应）、`eval/real-projects/escape-ledger.md`、`eval/real-projects/delivery-matrix.json`。

## 一、模型行为问题，被门禁按设计抓住（model-behavior-caught，5 条，全部闭环）

| id | 闭环 | 证据摘要 | 剩余动作 | 阻塞发布 |
|---|---|---|---|---|
| D6-gpt-54-mini-initial-2026-07-03 | 是 | 同 scenario 同 runner 的 minimal rerun（D6-gpt-54-mini-minimal-2026-07-04）转 GATE-RECOVERED，pf_validate 8/0/0；facts 层无污染，首轮只是子代理执行未收敛 | 无，可选：把"短模板+时间盒"经验写进 runbook | 否 |
| D19-minimax-m3-initial-2026-07-04 | 是 | 同 runner 修复轮 D19-minimax-m3-repair-2026-07-04 转 GATE-RECOVERED，判分方独立复跑 impact_validate 0 failed；escape-ledger E-001/E-002/E-003 均标"已拦住" | 无，可选：验证规则 #5/N3/V21 预防层是否能提前拦住业务岔路（D19r3 复测） | 否 |
| D19r2-minimax-m3-2026-07-04 | 是 | 与 D19r1 同一位置复现 7 处 tagList 兼容桩，被 check_delivery must_not_contain 和 impact_validate V16 独立抓住；escape-ledger E-001/E-002/E-004/E-005 均已有对策落地 | 无，可选：D19r3 验证规则侧预防是否生效 | 否 |
| D3-composer-25fast-2026-07-04 | 是 | check_delivery analysis gate 独立复跑 FAIL（7 个源码文件在分析场景外），回归测试 test_analysis_gate_fails_on_source_diff 覆盖；属 E-009/E-010 逃逸家族，拦截手段已自动化 | 无，可选：补一次 rerun-clean 转绿样本 | 否 |
| D14-gpt-54-mini-glm52-rerun2-2026-07-04 | 是 | check_delivery analysis gate 的 phase4-artifacts 检查按设计判 FAIL，回归测试 test_phase4_analysis_gate_fails_when_docs_missing 精确覆盖；同 scenario 在 Composer（推荐主力 runner）下 PASS-WARN | 无，可选：给该失败形态补独立台账编号 | 否 |

## 二、流程逃逸，已有拦截手段（skill-process-escape，7 条，全部闭环）

| id | 闭环 | 证据摘要 | 剩余动作 | 阻塞发布 |
|---|---|---|---|---|
| D20-gpt-54-mini-natural-rerun-2026-07-04 | 是 | escape-ledger E-006；写前 hook（impact-write-gate.py + 11 条单测）+ check_delivery validator_missing_artifacts 均已核实存在；同 runner 后续两轮确定性复现，作为 E-006 回归证据入账 | 无，Codex 裸跑维持压力测试定位，不进正式交付通道 | 否 |
| D14-gpt-54-mini-2026-07-04 | 是 | escape-ledger E-009；check_delivery phase4-artifacts 门禁 + 回归测试实测通过（5 passed）；同场景 Composer PASS-WARN，证明场景可通过 | 补 MiniMax M3 的 D14 覆盖（仍缺） | 否 |
| D18-gpt-54-mini-2026-07-04 | 是 | escape-ledger E-009；check_analysis_gate + test_analysis_gate_fails_on_source_diff 均已核实；同场景 Composer PASS（27/0/0） | 无，runner 定位维持压力测试 | 否 |
| D20-gpt-54-mini-interactive-2026-07-04 | 是 | escape-ledger E-006；同场景 D20-composer-rerun-clean 与 D20-minimax-m3 均 GATE-RECOVERED，失败隔离到该 runner；delivery-matrix 已机器强制该 runner 不进正式 Phase 5 | 无 | 否 |
| D20-gpt-54-mini-glm52-clean2-2026-07-04 | 是 | escape-ledger E-006；11 条 hook 单测实测通过；三条同 runner D20 记录一致 FAIL，稳定行为签名 | 无（如需转正需补带 hook 宿主的 D20 复跑取证） | 否 |
| D2-composer-25fast-2026-07-04 | 是 | escape-ledger E-009/E-010；check_analysis_gate + impact_validate V15/V16 独立复跑抓住 README 谎报 clean 的问题 | 无，裸 subagent 无写前 hook 属已知边界 | 否 |
| D18-gpt-54-mini-glm52-rerun2-2026-07-04 | 是 | escape-ledger E-009 第二次复现；check_analysis_gate + 回归测试实测通过；同场景 Composer PASS | 无 | 否 |

## 三、评测侧门禁/规则缺陷，已修复（gate-or-rule-defect，1 条，闭环）

| id | 闭环 | 证据摘要 | 剩余动作 | 阻塞发布 |
|---|---|---|---|---|
| D12-composer-25fast-2026-07-04 | 是 | 缺陷在评测侧 fixture 隔离不足（prep 脚本只清 change-impact/），不在模型也不在 validator；同 scenario 同 runner 的干净隔离副本 rerun（D12-composer-25fast-rerun-clean）转 PASS，两份地图 pf_validate 均 10/0/0；runbook 已补物理隔离强制规则 | 无，可选：把隔离规则从文字升级为 prep 脚本自动断言 | 否 |

## 四、环境/额度中断（infra-interrupt，1 条，未闭环）

| id | 闭环 | 证据摘要 | 剩余动作 | 阻塞发布 |
|---|---|---|---|---|
| D3-minimax-m3-2026-07-04 | **否** | Claude CLI 403 额度中断（¥0）发生在修复循环开始前，缺 _active-state.md 已被 impact_validate V1 当场拦住（18/1/2），但中断导致既不能证明模型能修复也不能证明修不好；无同 runner rerun 转绿，escape-ledger 无对应条目（本就不属于逃逸台账范畴） | 确认 MiniMax M3 渠道额度恢复后，用清理过 change-impact 的隔离 fixture 副本复跑 D3，另立条目记录结果 | 否（但按发布线口径仍需补跑，属真实待办） |

## 五、分析覆盖缺口（coverage-gap，1 条，未闭环，阻塞发布）

| id | 闭环 | 证据摘要 | 剩余动作 | 阻塞发布 |
|---|---|---|---|---|
| D16-gpt-54-mini-2026-07-04 | **否** | case 要求覆盖 `.env` 和 CI 中的 PROJECT_NAME 引用，gpt-5.4-mini 两处均漏（run README 显示 rg 搜索用显式路径清单未含根目录 .env/.github，未用 --no-ignore 补偿）；同 scenario 同 fixture 下 Composer 2.5 Fast 找到并覆盖（PASS，27/0/0），说明 case 本身可解；delivery-matrix.json 的 repair_loop（补配置入口检查规则后复跑）**未执行**；escape-ledger 无对应条目；MiniMax M3 在该场景**完全没有运行记录**（runner_scope 要求 3 个 runner） | 见下方 action_items：二选一——补配置入口检查规则并复跑转绿，或显式收窄 gpt-54-mini 的可用性声明 | **是** |

## 小结

15 条里 13 条已闭环（其中 5 条是模型行为被门禁抓住、7 条是流程逃逸被已有拦截手段抓住、1 条是评测侧 fixture 隔离缺陷已修复并转绿验证）——这 13 条本质上都是"门禁正常工作的证据资产"，证明了 check_delivery.py / impact_validate.py / impact-write-gate hook 这些拦截手段确实能抓住对应的失败形态，写进发布材料是加分项，不是待办。

真正没闭环、需要处理的只有 2 条：D3-minimax-m3（环境额度中断，不阻塞发布但按发布线口径仍需补跑取证）、D16-gpt-54-mini（分析覆盖缺口，唯一一条**明确阻塞发布**的项，因为 delivery-plan 阶段 5 的硬标准要求 M 级任务所有 runner PASS 或 GATE-RECOVERED，而该场景既有一个 runner 确定 FAIL、repair_loop 未执行，又有一个 runner（minimax-m3）完全没跑过）。