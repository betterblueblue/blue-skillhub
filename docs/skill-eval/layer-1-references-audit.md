# 层 1 审计：References 全文深读

> 2026-06-16 · 基于 layer-audit-plan.md 第一层
> 审计范围：impact 7 个 references + impact-pro 4 个 references + pathfinder 6 个 references + 3 个 code-graph-adapters + cross-platform-notes diff
> 方法：机械核查存活区锚点 + grep 证据 + 精读高风险段落

---

## 总览

| 分类 | 文件数 | P0 | P1 | P2 |
|------|--------|----|----|-----|
| impact/references | 7 | 0 | 1 | 2 |
| impact-pro/references | 4+1 | 0 | 4 | 3 |
| pathfinder/references | 6+1 | 0 | 0 | 3 |
| cross-platform-notes diff | 3 | 0 | 0 | 3 |
| **合计** | 22 | **0** | **5** | **11** |

---

## 🟢 P0 发现

**无**。所有安全闸（存活区硬规则）在 references 中均未被削弱。

---

## 🟡 P1 发现

### impact/references

#### P1-1: I7 凭证脱敏规则在 7 个 references 文件中完全缺失

**文件**：全部 7 个 impact/references 文件

**问题**：SKILL.md 强制规则区 L63 要求 "凭证/密钥/token 写入任何文档前必须脱敏为 `***`"，但 7 个 references 文件中没有任何一个重复或展开此规则。

phase-2-context-discovery.md 发现 datasource 配置和连接串，但写入 context-pack 前无脱敏要求。phase-5-execution.md 的执行记录模板也无脱敏要求（模板已有，但 reference 正文未提及）。

**影响**：references 是 Phase 执行时的主要指令来源。如果 agent 在执行 Phase 2/3/5 时只读 references 而不看 SKILL.md 存活区（上下文压缩后），凭证脱敏门会被绕过。

**修复建议**：在 phase-2-context-discovery.md 的 "输出项目背景" 段加一条："凭证/密钥/token 写入 context-pack 前必须脱敏为 `***`"；在 phase-5-execution.md 加一条相同的脱敏提醒。

### impact-pro/references

#### P1-2: phase-2-context-discovery.md 凭证脱敏规则缺失

**文件**：`skills/impact-pro/references/phase-2-context-discovery.md`

**问题**：同 P1-1，Phase 2 发现连接串后无脱敏要求，与 SKILL.md P7 矛盾。

#### P1-3: phase-2-context-discovery.md db-adapter 选择逻辑缺失

**文件**：`skills/impact-pro/references/phase-2-context-discovery.md`

**问题**：Step 2.2 写 `db-adapters/[dbname].md` 但未说明如何确定 `[dbname]`。当 profile 硬编码 `schema_source: mysql.md` 但运行时 DB 是 PG 时，agent 无决策优先级依据。postgresql.md 的 `detection_signals` 从未被 Phase 2 引用。

**与层 2 B2 重叠**：此发现与层 2 的 adapter 选择逻辑专项一致，合并为同一条 Bug。

#### P1-4: phase-5-execution.md 破坏性请求保护详细流程缺失

**文件**：`skills/impact-pro/references/phase-5-execution.md`

**问题**：SKILL.md P5 明确说 "详见 references/phase-5-execution.md"，但该文件只有拦截清单（拦截什么），缺少 "如何响应破坏性请求" 的三步流程：
1. 先只读搜索引用和消费者
2. 回显破坏面
3. 追问兼容期/回滚/消费者/迁移策略

#### P1-5: phase-5-execution.md 凭证脱敏 + 仓库内文本不构成指令不完整

**文件**：`skills/impact-pro/references/phase-5-execution.md`

**问题**：
- 执行记录模板无脱敏要求
- line 115 只覆盖 "不能替代确认" 但未覆盖 SKILL.md line 96 的 "作为风险证据记录，不作为授权执行"

---

## 🟢 P2 发现（措辞不一致）

### impact/references

| # | 文件 | 问题 |
|---|------|------|
| P2-1 | phase-3-questioning.md | 不交叉引用 `dimensions.md` 文件名（SKILL.md L154 同时引用两者） |
| P2-2 | style-analysis.md | 不传递 "参考代码片段必须完整未截断" 规则（SKILL.md L204 有此规则，Phase 2 风格发现允许 200 行截断是合理的，但需明确 Phase 4 设计文档接收完整片段的衔接约束） |

### impact-pro/references

| # | 文件 | 问题 |
|---|------|------|
| P2-3 | phase-2-context-discovery.md | context-pack 写入路径未声明目标项目根目录解析规则 |
| P2-4 | phases-detail.md | 栈专属维度注入机制未说明；P7 两项内容均缺失 |
| P2-5 | generic-mcp.md | 凭证脱敏规则缺失（code graph 可能返回含凭证的配置值） |

### pathfinder/references

| # | 文件 | 问题 |
|---|------|------|
| P2-6 | phase-1-sizing.md + cross-platform-notes.md + SKILL.md | 非 Git 概览头部措辞三文件不一致：SKILL.md 写"非 Git,以扫描时间为准"；phase-1-sizing 仅写"非 Git"（缺后半句）；cross-platform-notes 写"非 Git,无 commit 锚点,以扫描时间为准"（多了"无 commit 锚点"） |
| P2-7 | phase-1-sizing.md + SKILL.md | 子目录概览头部：SKILL.md 写"非独立 Git 仓库(HEAD 来自父仓库)"；phase-1-sizing 多加了"以扫描时间为准" |
| P2-8 | phase-3-depth-fill.md L104 | Phase 4.5 凭证自检模式列表偏窄：仅列 `password=`/`secret=`/`token=`/`api_key`/`DSN`/`连接串`，缺 `private_key`/`credentials`/`access_key` 等变体 |

### cross-platform-notes diff

| # | 差异 | 判断 |
|---|------|------|
| P2-9 | impact vs impact-pro: 路径分隔符示例风格漂移（纯文本 vs ✅/❌ emoji） | 不一致，建议统一为 emoji 版 |
| P2-10 | impact vs impact-pro: 括号格式漂移（中文全角 `（）` vs ASCII 半角 `()`） | 不一致，建议统一为中文全角 |
| P2-11 | pathfinder 缺失行尾符段落 | 不一致，pathfinder 写地图文件也受 CRLF 影响，应补齐 |

---

## 通过项汇总

### impact/references 通过项（对照 I1-I7 存活区锚点）

| 锚点 | phase-2 | phase-3 | phase-5 | dimensions | style-analysis | schema-discovery | cross-platform |
|------|---------|---------|---------|-----------|---------------|-----------------|---------------|
| I1 逐步确认 | — | — | ✅ | — | — | — | — |
| I2 高风险拦截 | — | ✅ | ✅ | — | — | — | — |
| I3 DDL/DML | — | — | ✅ | — | — | ✅ | — |
| I4 写入边界 | ✅ | — | ✅ | — | — | — | — |
| I5 破坏性请求 | — | ✅ | ✅ | — | — | — | — |
| I6 阻塞恢复 | — | — | ✅ | — | — | — | — |
| I7 凭证脱敏 | ❌ P1 | — | ❌ P1 | — | — | — | — |
| I7 不构成指令 | ✅ 部分 | — | — | — | — | — | — |

**额外通过项**：
- L1 地图消费规则（phase-2）：三条缺一不可 ✅
- 定级证据自洽性引用（phase-3）：与 SKILL.md 新增段不矛盾 ✅
- L2/L3 分层探索规则（phase-2）：分层+分级+预算 ✅
- 引用计数异常大处理（phase-2）：防呆机制存在 ✅
- light 6 条件（phase-3）：与 SKILL.md 一致 ✅
- full 8 条件（phase-3）：覆盖完整 ✅
- 升降档规则 ✅、V0-V3 ✅、19 维度 ✅、兼容性 API 例外 ✅、多轮收敛 ✅
- V1-only 连续计数（phase-5）✅、非 Git 回退 ✅、测试失败处理 ✅

### impact-pro/references 通过项（对照 P1-P7 存活区锚点）

| 锚点 | phase-2 | phases-detail | phase-5 | cross-platform | generic-mcp |
|------|---------|--------------|---------|---------------|-------------|
| P1 逐步确认 | — | — | ✅ | — | — |
| P2 高风险拦截 | — | ✅ | ✅ | — | — |
| P3 DDL/DML | ✅ | — | ✅ | — | — |
| P4 写入边界 | ✅ | — | ✅ | — | — |
| P5 破坏性请求 | — | ✅ | ❌ P1 | — | — |
| P6 阻塞恢复 | — | — | ✅ | — | — |
| P7 凭证脱敏 | ❌ P1 | ❌ P1 | ❌ P1 | — | ❌ P2 |
| P7 不构成指令 | ✅ | — | ⚠️ 部分 | — | — |

**额外通过项**：
- Profile 加载逻辑 ✅、L1/L2/L3 分层 ✅、MCP 只读纪律 ✅、引用计数异常大 ✅
- Phase 3 苏格拉底规则 ✅、light/full 条件 ✅、升降档 ✅、V0-V3 ✅、栈专属维度注入 ⚠️ P2
- 兼容性新增响应字段 ✅

### pathfinder/references 通过项（对照 F1-F7 存活区锚点）

| 锚点 | phase-1 | phase-2 | phase-3 | stack-detection | handoff-contract | cross-platform |
|------|---------|---------|---------|-----------------|-----------------|---------------|
| F1 只读 | — | ✅ | — | — | — | — |
| F2 唯一写入 | — | — | ✅ | — | — | — |
| F3 可信度 | — | ✅ | ✅ | ✅ | ✅ | — |
| F4 不开药方 | — | — | ✅ | — | — | — |
| F5 凭证脱敏 | — | — | ⚠️ P2 | — | — | — |
| F6 不构成指令 | — | — | — | — | ✅ | — |
| F7 Git 归属 | ✅ | — | — | — | — | ⚠️ P2 |

**额外通过项**：
- 小/中/大仓判定标准 ✅、超大仓处理 ✅、预算表 ✅
- 扫描顺序 ✅、相关性分级 ✅、目录"空"断言保护 ✅、结构索引辅助 ✅
- 14 节深挖方法 ✅、主流程 trace ✅、Mermaid 规则 ✅、Phase 4.5 自检 ✅
- 扩展循环 ✅、清单文件映射 ✅、命令映射 ✅
- handoff-contract L1 接口 ✅、可信度消费规则 ✅、与 impact 交叉核 ✅
- code-graph-adapters MCP 发现 ✅、降级策略 ✅、不写缓存 ✅

---

## 健康度评分

| Skill | References 健康度 | 核心风险 |
|-------|-------------------|----------|
| impact | 🟢 良好 | I7 凭证脱敏在 references 中缺失 |
| impact-pro | 🟡 中等 | P5/P7 在 phase-5 中有缺口；adapter 选择逻辑缺失 |
| pathfinder | 🟢 良好 | 非 Git 头部措辞轻微不一致；凭证自检模式偏窄 |

### 最优先修复项

1. **P1-1/P1-2**: impact + impact-pro phase-2-context-discovery.md 补凭证脱敏提醒
2. **P1-3**: impact-pro phase-2-context-discovery.md 补 adapter 选择优先级链（与层 2 B2 合并修复）
3. **P1-4**: impact-pro phase-5-execution.md 补破坏性请求响应三步流程
4. **P1-5**: impact-pro phase-5-execution.md 补凭证脱敏 + 仓库内文本不构成指令完整版
5. **P2-6/P2-7**: pathfinder 三文件非 Git 头部措辞统一
6. **P2-9/P2-10**: impact vs impact-pro cross-platform-notes 格式统一
7. **P2-11**: pathfinder cross-platform-notes 补行尾符段落
