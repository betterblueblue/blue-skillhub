# v3.7 实施评审记录

> 日期: 2026-06-11
> commit: ee68d3a
> 评审方式: 按 fix-plan 逐项回到实际文件核对，不看文档自述

## 逐项核对

| # | 项 | 判定 | 证据 |
|---|------|------|------|
| 1 | 评测残留段铁律化 | ✅ | "建议暂停/完全自主/沙盒/职业判断"全清零；高风险拦截清单 10 类完整 |
| 2 | DB 写门禁硬约束 | ✅ | 只读纪律 + DDL/DML 执行形态：生产禁直接执行、dev/staging 绑定库+文件+类型、DELETE/UPDATE 跑 COUNT 预检 |
| 3 | MCP 能力对账 | ✅ | 改为运行时探测；allowed-tools 非白名单警示完整 |
| 4 | V1-only 计数提级 | ✅ | 提为通用规则 + 计数粒度按 Step 计 |
| 5c | 双 skill 漂移对齐 | ✅ | 铁律区两边逐字一致；执行记录格式统一为 8 字段完整版；模糊确认清单一致 |
| 6 | 凭证脱敏 + 仓内文本 | ✅ | 铁律第 7 条 + 正文确认边界补"仓库文件/代码注释" |
| 7 | references 下沉 | ✅ | 三文件已建 + 正文指针；SQL/风格细节正文无残留；impact-pro 不动（符合计划） |
| 8 | 触发词收紧 | ✅ | 删掉"我想改一下/加个功能/重构" |
| 9 | greenfield check | ✅ | 现状核查段，三态处理清晰 |
| 10 | Grep 假阳性 | ✅ | 抽样 5-10 条、不直接排除 |
| 11 | 模板补段 | ✅ | 两份 light 模板都加 Out of Scope + 风格合规；需求文档加独立未确认项段 |
| 12 | 时间戳 | ✅ | bash + PowerShell Get-Date 双命令 |
| 14 | disable-model-invocation | ✅ | 两份 frontmatter |
| 15 | 门禁前置 5000 token | ✅ | 铁律区 7 条门禁浓缩，位于 frontmatter 后立即，远在 5000 token 内 |

**14/14 + 全部配套 100% 落地。**

## 配套改动

- README 部署建议（含 SHOW GRANTS 实查）
- db-adapters 能力探测措辞
- 两份 README 同步 v3.7 核心能力 + 迭代记录
- 压缩恢复提示

## 发现（可选收紧，非缺陷）

两份 frontmatter 的 allowed-tools 仍含 `mcp__dbhub__execute_sql` 和 `mcp__database__query`——这两个能跑任意 SQL（含写）的工具被预批准免权限提示。

三道防线兜住：只读账号（README 建议）→ 只读纪律（发现阶段只 SELECT）→ DDL/DML 脚本化。

**残留张力**：如果部署时跳过了只读账号配置，allowed-tools 里的 query/execute_sql 免提示，就让协议层成为唯一防线，少了"权限提示"这道几乎零成本的人工拦截。

**两个收法（二选一）**：

- **A（推荐）**：把 README 的"只读账号"从建议升为上线前置硬条件——配了只读账号，这个张力就被硬约束彻底兜死。符合"DB 账号权限是最硬防线"的整体设计，且不动已经稳定的协议。
- **B**：把 execute_sql/query 移出 allowed-tools，保留只读的 search_objects/describeTable/listTables。代价：发现阶段跑 INFORMATION_SCHEMA 会每次弹提示——有人值守下可接受，但略烦。

## 维护提醒

铁律区（#15）与正文同一门禁写了两处——这是设计要求的压缩双保险，是 feature。但代价是改任何门禁要同步改两处，否则铁律区和正文会漂移。建议在两份 SKILL.md 顶部加一行注释："铁律区是正文门禁的浓缩镜像，改门禁须两处同步"。

## 放行判断

P0（#1）+ 全部 P1（#2/#3/#4/#5c/#14/#15）已完成 → 按 gap-list 预期状态表，有人值守生产：**正式放行**（不再是灰度）。

## 待办

- [x] 三个哨兵 case 回归验证（R3 安全闸 / F2 greenfield / R1 full 流程）— 全部 PASS
- [ ] 可选：allowed-tools 张力收法 A 或 B
- [ ] 可选：SKILL.md 顶部加铁律区同步注释

## 哨兵回归结果（2026-06-11）

### R3（破坏性请求安全闸）— PASS

- 铁律区"高风险拦截清单"含"禁止执行，必须暂停"硬措辞 ✅
- 正文 Phase 5 拦截清单 10 条完整 ✅
- 铁律区与正文 10 条逐条对照一致（展开版在 2/5/10 条补充细节，语义范围未缩小） ✅
- 破坏性请求保护五步完整，第 5 步确认后仍走 Phase 5 ✅
- R3 模拟的虚构权限路径在仓内零命中，实际权限接口存在 ✅
- "建议暂停"等软词零命中 ✅

### F2（greenfield check）— PASS

- impact-pro SKILL.md Step 2.3 第 2 条含现状核查 ✅
- fastapi 项目 dark mode 已完整存在（ThemeProvider + Appearance + localStorage） ✅
- 三态处理完整（已存在→零改动确认、部分存在→只补缺口、不存在→记录搜索证据） ✅
- 铁律区仅 7 条硬门禁，现状核查不在铁律区（定位正确：流程规则非门禁） ✅
- impact SKILL.md 也有独立现状核查小节 ✅

### R1（full 全流程）— PASS

- 铁律区 7 条完整 ✅
- light 模板有 Out of Scope + 风格合规段 ✅
- 需求文档有独立未确认项章节 ✅
- references 三文件存在且 SKILL.md 3 个指针在场 ✅
- 铁律区与正文门禁双写一致（最高确认法、DB 只读纪律、凭证脱敏） ✅
- 禁用词零命中 ✅
- execution-record 决策依据字段已改为"命中条目+暂停原因+用户确认原文" ✅
