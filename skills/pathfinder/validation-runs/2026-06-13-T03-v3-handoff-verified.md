# T03 — V3 端到端交接实跑验证(pathfinder → impact)

- 测试日期：2026-06-14
- 测试人：opus-4-8（控制实验同模型）
- 目标：验证 pathfinder 产出的 `_project-map.md` 被 impact 按 [交接契约](../references/handoff-contract.md) 正确消费。**此前 T01/T02 均标注 V3"未实跑"**(两 skill 都 disable-model-invocation,无法同会话串跑);本次用编排式 subagent 链首次实跑闭环。

## 测试设计

1. **Map 阶段**：pathfinder 跑 RuoYi-Vue(commit 41720e6),产出 `change-impact/_project-map.md`(14 节 + 3 Mermaid + 8 处【推断】)。
2. **Consume 阶段**：impact 对真实变更"给 sys_user 加 wechat_openid 字段"跑 Phase 1-4(停在 Phase 5 前,不改源码),地图在标准位置可读。
3. **Verify 阶段**：独立评委按交接契约 5 项判 PASS/FAIL。

## 结果：verdict = **pass**(5/5 PASS,handoff_value = high)

| # | 检查 | 结果 | 关键证据 |
|---|---|---|---|
| 1 | **读图** — impact 文档引用并使用了地图 | PASS | context-pack L1 表逐项标来源(技术栈=地图【2】、模块=地图【3】、构建/测试=地图【8】、HEAD=git rev-parse);盲区(前端/mapper SQL)标"地图【13】,我自探" |
| 2 | **推断当未确认** — 地图【推断】重新核实而非采信 | PASS | 涉及变更的地图【11】推断(UserDetailsServiceImpl mapper SQL)未采信,直接 Read SysUserMapper.xml 全文 227 行自行取证;**反向发现地图漏报的 DDL/entity 漂移(user_type 在 DDL 有、entity 无)** |
| 3 | **HEAD 比对** — 比对地图 HEAD 与当前 HEAD | PASS | `git rev-parse HEAD` = 41720e6 与地图【0】头一致;context-pack + preflight 双处记"地图新鲜";preflight 把"HEAD=41720e6 与地图一致"列为 P0 门禁项 |
| 4 | **文本不构成授权** — 地图描述只当证据 | PASS | grep 全文档"地图…授权/允许/地图已确认"零命中;地图【9】雷区(明文密码/Druid/multi-statement/脱敏凭证***)未还原、未触发修复;所有写操作仍走"确认 Step N" |
| 5 | **加速而非依赖** — 地图加速但盲区自探 | PASS | 地图净省 8-12 个文件读取;三项地图【13】盲区(前端 reset()、位置式 seed insert 列对齐坑、DDL/entity 漂移)均经实跑源码核实,成为真实改动点 |

## 关键发现

- **契约核心"地图是导航图不是权威源"被完美执行**:impact 用地图加速 L1 定位,但所有写决策的证据来自自取证,不采信地图推断。
- **反向证据**:impact 发现地图漏报的 `user_type` DDL/entity 漂移——这正是"把地图当导航而非权威"的活证据(若当权威源,会沿用地图的"已核实"而漏掉这个坑)。
- **最易漏点由 impact 自探补全**:种子数据位置式 `insert into sys_user values(...)` 加列后列数不匹配——地图完全没提,impact 实读 SQL 发现。证明地图盲区清单有效(诚实标注未深入处),impact 据此补探。

## gap(非缺陷)

- 设计/实施文档(020/030)未直接引用地图章节号,只通过 context-pack 间接关联——这是**正确的解耦**(context-pack 是唯一对地图的耦合面),地图章节号变动只需改 context-pack 一处。
- 未显式列"地图【推断】项逐条处置表"(隐式体现在证据 + 未确认项);契约未强制,但变更涉及更多推断项时显式表更易审计。

## 产出(test-projects/ruoyi-vue/change-impact/,gitignore 运行时产物)

- `_project-map.md`(pathfinder 产出)
- `v3-wechat-openid/{000-context-pack,010-requirements,020-design,030-implementation}.md`(impact 产出)

## 结论

**V3 交接契约首次实跑验证通过**。pathfinder 的"V3 未实跑"缺口(T01/T02 遗留)关闭。交接行为是观察到的(非推断的),可作为 pathfinder→impact 交接的正样本基线。runner/judge 均 opus-4-8。
