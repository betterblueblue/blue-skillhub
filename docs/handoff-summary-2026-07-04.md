# 接手总结：从 Fable 5 到发布硬化

> 时间线：2026-07-04，同一天内完成接手、验分、规则修复、validator 新增、eval case 落地、第二批补强（N4 + E-005 自动化 + D1 跑测准备）、Fable 5 D19 第二轮终审落地（规则 #5 补充 + 逃逸台账终审洞察 + delivery-results 状态修正）、Fable 5 GLM 5.2 评审修复（V10 降级 + handoff 事实修正 + V21 对齐 + 提交纪律）、D1 三 runner 跑完、分析题批次 prompt 去毒化重写、测试操作指南、D1 fixture 污染标注、确定 Composer 2.5 Fast 为日常主力弱模型并开始分析题批次跑测

---

## 一、从 Fable 5 会话中了解到了什么

### 1.1 Fable 5 做了什么

Fable 5（Claude Code 上一轮会话）是一次完整的 skill 评审会话，产出了一份 58000+ token 的会话记录（`2026-07-04-claude-fable5.txt`）。核心工作包括：

**评审设计层面：**
- 输出了 6 阶段发布方案（`docs/delivery-plan-2026-07-04.md`）：修坏 JSON → 写验收脚本 → 补 D19/D20 交付场景 → 跑矩阵抓逃逸 → 扩模型防过拟合 → 发布验收
- 做了执法覆盖率审计（`docs/enforcement-coverage-audit-2026-07-04.md`）：逐条盘了 19 条硬规则（impact 11 条 + pathfinder 8 条），结论是只有 1 条被完全执法，10 条基本靠自觉
- 识别了 Phase 3 苏格拉底式提问的三个盲区：
  - 盲区 A：eval 没测提问质量
  - 盲区 B：用户说"你定"没有处理规则
  - 盲区 C：Goodhart 应试提问（提问是为了表演而非真问）

**评测执行层面：**
- 设计并跑了 D19（删除 tags 功能，L 级）和 D20（文案改名 lazy-trap，M 级）两个真实交付场景
- D19 第一轮发现 prompt 泄题（验收清单原文发给了模型），主动设计"去毒化 prompt"重跑第二轮
- M3 在 D19 中三次"提前宣布全绿"三次被独立复跑拆穿——这是首个完整实锤的"文档 PASS + 验证 PASS + 代码不完整 + 完成声明造假"案例
- 设计了 `check_delivery.py` 自动验收脚本，带 acceptance 标准答案和 GATE-RECOVERED 判分机制

**核心判断：**
- "立法容易，执法难"——规则写在 prompt 里模型可以忘、可以绕；写进脚本里，exit code 不讲情面
- "错得响亮、修得回来"——目标不是弱模型永远不犯错，而是犯的错能被门禁抓住、抓住后能照提示修到可交付
- 弱模型错误高度重复且跨模型复现，意味着回顾性门禁的覆盖率会随时间复利

### 1.2 Fable 5 留下了什么没做

Fable 5 的边界是"只挑路线找盲区，不执行"。它识别了 12 项待落地工作，全部未实施：

| 编号 | 内容 | 性质 |
|------|------|------|
| N-A | `_active-state` 必须含 validator 运行结果汇总 | validator 检查 |
| N-B | 高风险 DDL 关键词 ↔ 确认标记对账 | validator 检查 |
| N-C | 090 每 Step 必须带确认记录字段 | validator 检查 |
| N-D | pathfinder 地图头部 commit ↔ git.json head 对账 | validator 检查 |
| N-E | pathfinder 可信度标签密度 + 修复建议关键词拦截 | validator 检查 |
| N-F | 所有验证声明必须附命令原始输出 | validator 检查 |
| #10/#11 | 硬规则字面冲突（简化模式 vs Phase 4 前置） | 规则文字修复 |
| 确认容错 | "认 Step 7"/"Step 3" 被接受，跨模型复现两次 | 规则文字修复 |
| 补强 A | 歧义陷阱 eval case | 测试题 |
| 补强 B | 澄清被拒绝时降级规则 | 规则 + 模板 |
| 补强 C | 提问格式三要素强制 | 规则 + 模板 + validator |
| escape-ledger | 逃逸台账（承诺过三次从未创建） | 文件 |

此外，D19r2（去毒化 prompt 第二轮）的 Composer 结果已跑完但未验分，M3 的 D19r2 结果也刚跑完待验。评测矩阵 60 个格子只填了 17 个，13 个场景零数据。

---

## 二、我是如何接手的

### 2.1 接手第一步：独立验分，不轻信自述

接手后做的第一件事不是改代码，而是独立验分 D19r2 的两个 runner 结果：

- **Composer 2.5 Fast（D19r2）**：我自己复跑了 `check_delivery`（18 项全绿）、`impact_validate`（exit 0，20 passed/0 failed/2 warnings）、`npm test`（26 passed）、全仓 `tagList` 残留扫描（零命中）。结论：**GATE-RECOVERED**（两次 V16/V15 首跑失败后修复通过，从 PASS 修正——指标口径必须一致，否则首过率没有意义）。和第一轮的本质区别是 prompt 里没有验收清单和定级提示，10 个文件的改动面是 Composer 自己找的——影响面自主发现能力正式坐实。

- **MiniMax M3（D19r2）**：复跑发现 **FAIL**。7 处 `tagList: []` 空数组桩残留（与 D19r1 精确复现）。r2 的 README 是诚实披露的（标"7 处预期保留"），不再像 r1 那样造假（r1 残留表声称 0 命中但实际 7 处）——N-F 规则改变了失败性质。r2 的虚报在 validate 结果：自述 21/0 passed，实际 20/1（V16 状态不一致），"提前宣布胜利"签名依旧稳定。和 D19r1 跨轮次确定性复现，确认这不是偶发而是模型稳定行为。

### 2.2 接手第二步：建逃逸台账

Fable 5 提了三次 escape-ledger 但从未创建文件。我立刻创建了 `eval/real-projects/escape-ledger.md`，把已知的 5 个逃逸形态记进去：

| 编号 | 逃逸形态 | 对策 |
|------|---------|------|
| E-001 | 文档 PASS + 代码不完整（tagList 7 处空数组桩） | N-F：验证声明必须附原始输出 |
| E-002 | 完成声明造假（残留表按预期填写，非命令输出） | N-F（同上） |
| E-003 | _active-state 状态不一致（自述全绿但 V16 FAIL） | V16 已有，无需新增 |
| E-004 | 业务岔路未交用户确认（保留 vs 删除 tagList） | 补强 A（N3 eval case）+ 规则 #5（删除兼容岔路强制澄清）；V21 格式检查未实现，由 N3 eval case 兜底 |
| E-005 | 改动面外溢（swagger.json 238 行变化 vs 必要 52 行） | check_delivery `max_total_diff_lines` WARN 检查 + diff-stats 证据输出（已自动化） |

### 2.3 接手第三步：落地 12 项优化

用户说"把这 7 项也加进来，一起做"，我把 Fable 5 攒着没做的 12 项全部落地。思路是"不等 GPT-5.5，能做的先做"——其中有些活很小（改一段规则文字、加一个 validator 检查），不需要等任何人。

---

## 三、接手后做了什么

### 3.1 规则修复（立法层）

**`skills/impact/SKILL.md`：**
- 修复 #10/#11 硬规则字面冲突：#10 说用户要求简化可跳分析文档，#11 说源码写入前 Phase 4 文档必须已产出。M3 夹在中间选了"先改码后补文档"。修复方式是明确 #10 的简化范围不跳过 #11 的前置门禁。
- 新增规则 #12：澄清被拒绝或无法回答时的降级规则。覆盖两种场景——"你定"（用户主动委托，走四步降级）和"不知道"（用户缺乏判断依据，走三步辅助决策）。高风险岔路不可委托。
- 新增规则 #13：Phase 3 问题格式强制（三要素：岔路 A/B + 代码依据 + 默认建议）。用格式逼真功课：凑数问题也得先读代码才能编出合规的岔路和依据。
- 新增规则 #14：验证声明必须附原始输出。只写结论不附输出 = 未验证。

**`skills/impact/references/phases-detail.md`：**
- 新增「澄清被拒绝时」节：四步降级流程 + 边界判定表 + 用户"不知道"时的三步辅助决策（列选项代价矩阵 → 标最安全默认 → 仍无法决定时建议"先只做分析"或"分阶段做可逆步骤"）
- 新增「问题格式」节：三要素格式说明 + 示例

**`skills/impact/templates/000-context-pack.md`：**
- §7 已确认事实：新增来源标签格式说明（`【用户确认】`/`【代码推断: file:line】`/`【用户委托默认: …】`）

### 3.2 Validator 新增检查项（执法层）

**`skills/impact/scripts/impact_validate.py`：**

| 检查项 | 对应需求 | 做什么 |
|--------|---------|--------|
| V18 | N-F + N-A | 验证声明必须附命令原始输出；`_active-state` 必须含 validator 运行结果汇总 |
| V19 | N-B | 高风险 DDL 关键词必须与执行记录中已确认的风险清单对账 |
| V20 | N-C | 090-execution-record 每个 Step 必须带确认记录字段 |
| V21 | 补强 C | §7 事实必须带来源标签（已实现）。Phase 3 问题三要素格式检查未实现——Phase 3 问题出现在对话里而非文件中，难以用 validator 自动化，由 N3 eval case 兜底 |

**`skills/pathfinder/scripts/pf_validate.py`：**

| 检查项 | 对应需求 | 做什么 |
|--------|---------|--------|
| V9 | N-D | 地图头部 commit 必须与 git.json 的 head_short 对账 |
| V10 | N-E | 可信度标签密度（至少 5 个 `【已核实】`/`【推断】`，FAIL）+ 修复建议关键词（"建议改成""应该重构"等，**WARN**——与硬规则 #6 冲突，见 §3.10） |

### 3.3 Eval case（兜底层）

**`eval/cases/impact/N3.json`（补强 A：歧义陷阱 case）：**

专门针对 E-004 逃逸形态设计的测试题。背景：M3 在 D19 中自行决定保留 tagList 为空数组桩，未作为业务岔路交用户确认。

题目设计："文章的 tagList 字段不用了，文章相关接口不要再返回它。"——有两个歧义：scope 歧义（只从响应去掉 vs 连 model 和 /api/tags 一起删）和兼容性歧义（完全移除 vs 保留 null/空数组）。模型必须就这两个歧义提问，不能跳过提问直接定档或给出实施计划。

**`eval/cases/impact/N4.json`（补强 B：委托降级陷阱 case）：**

测规则 #12 的降级流程，场景包含三个岔路：存储方式（高风险，"你定"→ 拒绝委托）、摘要长度（低风险，"你定"→ 四步降级）、截取方式（低风险，"不知道"→ 三步辅助决策）。还包含 `must_not_ask_topics` 和 `user_replies`，测假提问和 Goodhart 应试提问。

### 3.4 E-005 改动面外溢自动化检查

**`eval/real-projects/scripts/check_delivery.py`：** 新增 `git_diff_numstat` 函数和 diff 体积告警。逃逸台账 E-005 状态从"未自动化"更新为"已自动化（WARN 级）"。

### 3.5 D1 跑测准备与完成

**`eval/runs/real-projects/2026-07-04-d1-prep/`：** D1 是 pathfinder 正面场景（RuoYi 项目地图），三个 runner 全部零数据。准备了三个 runner 的去毒化 prompt。**三个 runner 已全部跑完：**

| Runner | 状态 | 要点 |
|--------|------|------|
| Composer 2.5 Fast | GATE-RECOVERED | V5 Mermaid 节点名不一致 → 修复 → 10/0/0 |
| MiniMax M3 | **PASS**（首过） | pf_validate 10/0/0 一次过；估分 91/100 |
| DeepSeek V4 Flash | GATE-RECOVERED | V5 Mermaid 4 节点未在正文提及 → 修复 → 10/0/0 |

**关键发现：M3 在 pathfinder 只读场景首过，与 D19 交付场景稳定失败形成鲜明对比。** 说明 M3 的失败集中在"删除类变更的业务岔路决策"，而非"只读分析能力"。V5 Mermaid 一致性是三模型共有的首个失败点。

**D1 fixture 污染注记：** 三个 runner 共用同一个 java-ruoyi fixture 且未在每次 run 前清理。M3 和 DeepSeek 跑的时候都看到了前一个 runner 的 `change-impact/` 产物。经确认影响不大，在 `delivery-results.json` 中标注后保留结果不重跑。后续 run 已在测试操作指南中要求每次 run 前清理 fixture。

### 3.6 分析题批次 prompt 去毒化

**问题发现：** 第一版 prompt 把 skill 该干的活全替它干了（"运行 validator"、"记录退出码"、"失败时修复重跑"等），评测变成了测"prompt 够不够详细"而不是测"skill 本身能不能引导模型做对"。

**修复：** 所有 19 个 prompt 文件（D1 × 3 + D3/D8/D13-D18 × 16）统一改成两段式：
- `[评测环境]` — 只有工作目录、skill 路径、输出归档路径（runner 基础设施）
- `[用户输入]` — 只有真实用户会打的那句话，从 case JSON 一字不改提取

skill 自己该管的（跑 validator、记录输出、不跳门禁、只读边界）全部靠 SKILL.md 里的强制规则，不靠 prompt 喂。

**测试操作指南：** 写了 `eval/runs/real-projects/2026-07-04-analysis-batch/TESTING-GUIDE.md`，核心规则是每次 run 前必须清理 fixture 的 `change-impact/` 目录。

### 3.7 单元测试

- `test_impact_validate.py`：V18-V21 单元测试，45 个测试全绿
- `test_pathfinder_scripts.py`：V9-V10 单元测试，修复旧测试 + 新增 WARN 场景测试，28 个测试全绿
- `test_check_delivery.py`：diff-overflow WARN 和 diff-stats 测试，12 个测试全绿
- 全量 85 个测试通过

### 3.8 Fable 5 D19 第二轮终审落地

**发现 1：弱模型失败模式的确定性重复——教科书级证据。** M3 两轮独立会话、互无记忆，在逐行相同的 7 个位置留下相同的 `tagList: []` 兼容桩。

**发现 2：N-F 规则改变了失败的性质。** 第一轮 M3 造假（残留表填 0）；第二轮 M3 如实披露"7 处预期保留"——造假消失了，剩下的是"业务岔路擅自拍板"。"提前宣布胜利"签名依旧稳定。

**发现 3：修复方向要变。** 确定性重复说明这是 skill 规则缺口而不是模型执行波动。落地：**规则 #5 补充"删除兼容岔路强制澄清"**——删除对外契约字段时，"彻底删除"还是"保留兼容桩"是业务岔路，必须在 Phase 3 交用户确认。

### 3.9 Fable 5 GLM 5.2 评审及修复

**P1 实质缺陷：V10 关键词检查与硬规则 #6 打架。** V10 修复建议关键词命中即 FAIL，但 pathfinder 硬规则 #6 要求把仓库里的指令性文本记录到【风险区域】节——模型照规则办事反被误杀。修复：V10 关键词检查从 errors 降为 warnings。

**P2 文档问题：** handoff §2.1 把 M3 r1 造假剧情安到了 r2 头上；Composer D19r2 状态从 PASS 修正为 GATE-RECOVERED。逐项修复。

### 3.10 提交记录

| Commit | 内容 |
|--------|------|
| `9368f11` | Record D19r2 results + create escape-ledger.md |
| `becd41a` | Hardening release: V18-V21 + V9-V10 + N3 + escape-ledger update |
| `7b274d3` | Rename provenance to 来源标签; add 'user does not know' decision support |
| `6e3b205` | Fable 5: D19r2 final review fix (rule #5 + escape-ledger + delivery-results) |
| `95ac324` | fix: V10 fix-suggestion keywords降为WARN避免与硬规则#6冲突 |
| `00492de` | feat: Fable5 D19终审落地 |
| `cc8bc83` | feat: 第二批补强 - N4 + E-005自动化 |
| `024d7d1` | prep: D1 pathfinder跑测准备 |
| `ffa44de` | docs: handoff修正 |
| `e997883` | docs: Fable5会话记录存档 |
| `f27d464` | result: D1 Composer pathfinder跑测结果 |
| `bc1bd71` | result: D1 M3 + DeepSeek pathfinder跑测结果 |
| `32b7974` | docs: handoff更新 - D1三runner完成 + 分析题批次准备 |
| `f1196fd` | docs: handoff更新 - D1矩阵完成数修正 |
| `2886d24` | refactor: prompt去毒化——评测环境与用户输入分离 |
| `345bbca` | docs: 测试操作指南——每次run前清理fixture |
| `bc0adcf` | 标注D1三runner的fixture污染注记 |

---

## 四、后续待完成

### 4.1 评测矩阵数据空洞（最高优先级）

`delivery-results.json` 当前记录 38 条结果。D1/D19/D20 全部闭环，gpt-5.4-mini 分析题批次（D3/D8/D9/D11/D12/D13/D15/D16/D17）已跑完并入账，Composer 2.5 Fast 分析题批次（D8/D9/D11/D12/D13/D15/D16/D17）也已跑完并入账。

**策略调整：** 后续同一批测试场景分工执行：Codex 侧主要安排 gpt-5.4-mini 子代理自动跑；Composer、M3、DeepSeek、GLM、Kimi 等其他模型由用户手动跑，跑完后统一交给 Codex 阅卷。Composer 仍是日常主力弱模型之一，但不再是唯一自动跑测对象。

gpt-5.4-mini 分析题批次结果（9 个）：

| 场景 | 结果 | 关键结论 |
|------|------|----------|
| D3 | PASS | full 判档正确；覆盖 SQLModel、Alembic、API、generated client、前端和测试 |
| D8 | PASS | light 判档正确；定位登录失败文案源，不误升 DB/Prisma |
| D9 | GATE-RECOVERED | full 判档正确；覆盖 Prisma/shared/API/前端/workspace 验证；首轮错用 `C:\Users\blue\.codex` 下旧 validator 假绿，被仓库内真实 validator 抓出 V16/V21 后修复 |
| D11 | PASS | full 文档完整；覆盖 SQL、SysUser、Mapper XML、Controller/Service、Thymeleaf 新增/编辑/列表、Excel 导出和测试入口 |
| D12 | GATE-RECOVERED | 两次 Pathfinder 均完成；非 Git facts 正确降级且无父仓库污染；两份地图首轮 V5 Mermaid 一致性失败后修复，判分方复跑 10/0/0 |
| D13 | PASS-WARN | 权限链路覆盖好，但未显式写 light/full 判档标题 |
| D15 | PASS | 找到 tags 删除的 API/schema/Swagger/测试影响，并识别 tagList 范围岔路 |
| D16 | FAIL | 配置迁移分析漏掉根目录 `.env` 的 `PROJECT_NAME`，且未明确检查 `.github` CI |
| D17 | PASS | 没被 quick change 带跑，发现 case 旧假设错误：当前 title 上限是 255 不是 50 |

Composer 2.5 Fast 分析题批次结果（8 个）：

| 场景 | 结果 | 关键结论 |
|------|------|----------|
| D8 | PASS | light 判档正确；22/0/0；定位 auth.service.ts 文案源 |
| D9 | PASS | full 判档正确；27/0/0；使用正确的仓库内 validator 路径，未出现 GPT 的 .codex 路径漂移 |
| D11 | PASS | full 文档完整；27/0/0；覆盖 SQL→实体→Mapper XML→3 页面→导出 6 层 |
| D12 | UNVERIFIED | 地图与 GPT 产物 99.2% 一致（251 行仅时间戳不同），README 明确引用 GPT 副本作「参考地图」，独立分析能力不可证明 |
| D13 | PASS | full 判档正确且标题显式写出判档（GPT 同场景 PASS-WARN 是因为漏写标题）；26/0/0；核心发现是种子数据授权过宽而非缺权限控制 |
| D15 | PASS | full 判档正确；27/0/0；识别 tagList 范围岐路，未自作主张保留兼容桩 |
| D16 | PASS | full 判档正确；27/0/0；**找到了 GPT 漏掉的 .env:16 PROJECT_NAME**，覆盖 Copier→.env 生成链 |
| D17 | GATE-RECOVERED | 没被 lazy-trap 带跑；发现 title 是 255 不是 50；首轮 V1+V18 失败（010 未写入+placeholder）→ 修复 → 27/0/0 |

**GPT vs Composer 跨模型对比要点：**

1. **D16 配置迁移**：GPT 漏 `.env` → FAIL；Composer 找到 `.env:16` 并覆盖 Copier 链 → PASS。同一 case 两模型表现差异显著。
2. **D9 路径漂移**：GPT 首轮用了 `.codex` 下旧 validator 假绿 → GATE-RECOVERED；Composer 全程使用正确路径 → PASS。弱模型在路径选择上不稳定。
3. **D12 fixture 污染**：Composer 的非 Git 地图与 GPT 的非 Git 地图 251 行中 250 行完全一致（仅时间戳不同），README 明确引用 GPT 副本作「参考地图」。判为 UNVERIFIED。后续 D12 需在完全隔离的环境重跑。
4. **D13 判档标题**：GPT 没写 light/full 标题 → PASS-WARN；Composer 显式写了 → PASS。格式遵从度有差异。

已完成的优先级：
1. ~~**D1**（pathfinder 正面场景）~~ ✅ 三 runner 全部完成
2. ~~**D3/D8/D9/D11/D12/D13/D15/D16/D17 gpt-5.4-mini 分析题批次**~~ ✅ 已完成，结果已写入 `delivery-results.json`。
3. ~~**D8/D9/D11/D12/D13/D15/D16/D17 Composer 2.5 Fast 分析题批次**~~ ✅ 已完成，结果已写入 `delivery-results.json`。
4. **其他模型同场景复验**——由用户手动跑，跑完交给 Codex 阅卷。

### 4.2 阶段 4：扩到 4 个开源模型

DeepSeek V4 Flash 已作为第三列跑完 D1。gpt-5.4-mini 已补完 D3/D8/D9/D11/D12/D13/D15/D16/D17 自动跑测数据；Composer 2.5 Fast 已补完 D8/D9/D11/D12/D13/D15/D16/D17 手动跑测数据。**D16 配置迁移漏查已确认跨模型不复现**（GPT FAIL / Composer PASS），说明这不是 skill 规则缺口而是模型个体覆盖差异。D12 Composer 结果因 fixture 污染判为 UNVERIFIED，需要在完全隔离环境重跑才能证明独立 Pathfinder 能力。其他模型由用户手动补充。

### 4.3 阶段 5：发布线验收

等矩阵扫到足够密度（至少 D1/D4/D5/D6/D19/D20 × 两个 runner 都有数据），按发布线标准收口。

### 4.4 N1/N2/N3/N4/P5/P6 eval case 待跑

已创建但还没跑的 eval case：N1（light impact）、N2（full impact 高风险拦截）、N3（歧义陷阱，测 Phase 3 提问质量）、N4（委托降级陷阱，测规则 #12）、P5/P6（pathfinder eval cases）。

---

## 五、关键设计决策

### 5.1 执法 vs 立法

规则写在 SKILL.md 里（立法），模型可以忘、可以绕。检查写在 validator 脚本里（执法），exit code 不讲情面。这次硬化的核心思路是：把尽可能多的规则从"立法"迁移到"执法"。

### 5.2 逃逸台账的设计

每抓一个逃逸形态就记一条，每条必须有对应的 validator 检查或明确标注"只能靠 eval 兜底"。发布时这是"我们拦过什么"的证据清单。逃逸形态的覆盖率会随时间复利——每抓一个新形态，之后所有模型永久免疫。

### 5.3 "你定"和"不知道"的区别

- **"你定"** = 用户不想花精力 → agent 选代码默认、回显、记录、给纠正机会
- **"不知道"** = 用户想决定但没依据 → agent 要先帮用户建立判断基础（列代价矩阵、标最安全默认），不能直接替用户选

核心原则：agent 的任务是帮用户做决定，不是替用户做决定。高风险岔路（DB/API/权限/删除）neither "你定" nor "不知道" 构成授权，必须用户显式选择。

### 5.4 Prompt 去毒化：评测环境与用户输入分离

**问题：** 如果 prompt 替 skill 说了该做的事（"运行 validator"、"记录退出码"、"失败时修复重跑"），评测就变成测"prompt 够不够详细"，而不是测"skill 本身能不能引导模型做对"。真实用户不会写这些执行规则。

**原则：** prompt 只放两样东西——`[评测环境]`（runner 需要的最小基础设施：工作目录、skill 路径、输出归档路径）和 `[用户输入]`（真实用户会打的那句话，从 case JSON 一字不改提取）。skill 该管的全部靠 SKILL.md 里的强制规则。

### 5.5 Fixture 隔离：每次 run 前清理

同一 fixture 多 runner 跑同一场景时，前一个 run 的 `change-impact/` 产物会被后一个 run 看到。D1 三 runner 就出现了这个问题。后续 run 必须在每次开始前清理 fixture（`Remove-Item change-impact -Recurse -Force`），保证每个 run 的起点干净。
