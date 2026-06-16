# 层 3 审计：Templates 逐行内容审

> 2026-06-16 · 基于 layer-audit-plan.md 第三层
> 审计范围：impact 9 模板 + impact-pro 11 模板 + pathfinder 1 模板 = 21 个文件

---

## 总览

| 分类 | 文件数 | P0 | P1 | P2 |
|------|--------|----|----|-----|
| impact templates | 9 | 2 | 4 | 5 |
| impact-pro templates | 11 | 2 | 4 | 5 |
| pathfinder templates | 1 | 0 | 1 | 2 |
| **合计** | 21 | **4** | **9** | **12** |

---

## 🔴 P0 发现（安全闸被削弱）

### P0-1 & P0-2: impact subagent-decisions.md — subagent 自主执行逃生通道

**文件**：`skills/impact/templates/subagent-decisions.md`

**问题 1**：L4 "由 subagent 自主决策：执行" 可被弱模型理解为不经用户确认直接执行写操作。

**问题 2**：L29 DECIDE 选项 "execute" 无限定词，可被误解为自动执行。

### P0-3 & P0-4: impact-pro subagent-decisions.md — 同样问题

**文件**：`skills/impact-pro/templates/subagent-decisions.md`

**问题 1**："标风险(沙盒里可继续)" — "沙盒"未定义，弱模型可将其解读为"标记风险后仍可执行真实写操作"，构成绕过 Step 级确认的逃生通道。

**问题 2**："subagent-confirm" DECIDE 选项 — 选项名暗示 subagent 可自行授权执行，弱模型可解读为"subagent 确认 = 无需人类确认"，扩大了自动执行范围。

**修复建议**：
1. subagent-decisions.md 所有执行选项加限定词："execute (需人类 `确认 Step N` 后)"
2. "沙盒"改为"eval 沙盒（subagent-as-user 协议），生产会话禁止"
3. DECIDE 选项改名为 "request-human-confirm" 而非 "subagent-confirm"

---

## 🟡 P1 发现

### impact 模板

| # | 文件 | 问题 |
|---|------|------|
| P1-1 | 010-requirements.md | 无脱敏提示（有配置节，可能粘贴含密码内容） |
| P1-2 | 030-implementation.md | 无脱敏提示（有命令/代码字段，最可能含凭证） |
| P1-3 | 040-light.md | 无脱敏提示（有命令字段） |
| P1-4 | subagent-decisions.md | 无 "确认 Step N" 格式引用 |

### impact-pro 模板

| # | 文件 | 问题 |
|---|------|------|
| P1-5 | 030-implementation.md | 缺失脱敏提示（最可能包含 DB 连接串/API key 的模板） |
| P1-6 | subagent-decisions.md | 缺失 `确认 Step N` 格式 |
| P1-7 | _active-state.md | target_project_root 缺失子字段（impact 版有 absolute_path/determination_method/verification_timestamp，impact-pro 版仅 `[绝对路径]`） |
| P1-8 | 060-preflight.md | 目标项目根目录部分缺失子字段（同上） |

### pathfinder 模板

| # | 文件 | 问题 |
|---|------|------|
| P1-9 | project-map.md | Section 【9】line 115 的脱敏标签仅写 "(脱敏)"，缺少 SKILL.md 硬性规则 #5 要求的"必须显式声明风险性质"提示。SKILL.md 明确禁止"只写已脱敏"模式。 |

---

## 🟢 P2 发现（措辞不一致）

### impact 模板

| # | 文件 | 问题 |
|---|------|------|
| P2-1 | 000-context-pack.md | 脱敏提示仅覆盖 section 5，非全文 |
| P2-2 | 030-implementation.md L32 | 确认格式缺 `: [操作名称]` |
| P2-3 | 040-light.md | 无确切 "确认 Step N" 格式示例 |
| P2-4 | _active-state.md | "not an authorization" 弱于 SKILL.md 的枚举式措辞 |
| P2-5 | _active-state.md | 命令字段无脱敏提醒 |

### impact-pro 模板

| # | 文件 | 问题 |
|---|------|------|
| P2-6 | 000/020/090 脱敏格式不一致 | 000 用 `***` (无反引号), 020/090 用 `` `***` `` (有反引号) |
| P2-7 | 040-light.md | 缺少完整确认格式示例（仅写"按 Step 编号确认"） |
| P2-8 | 060-preflight.md | Step 确认用缩写格式（无响应选项） |
| P2-9 | _active-state.md | 英文 header 与中文 body 混合 |
| P2-10 | 090-execution-record.md | 缺少完整确认格式示例 |

### pathfinder 模板

| # | 文件 | 问题 |
|---|------|------|
| P2-11 | project-map.md L34, L124 | 可信度标记用合并简写 "【已核实/推断: ...】"，与 SKILL.md 定义的独立格式 "【已核实: 证据】" / "【推断: 待验证】" 不一致 |
| P2-12 | project-map.md | 弱模型可能就近模仿输出字面量合并形式 |

---

## 通过项汇总

### impact 模板通过项

| 模板 | 逐项确认 | Step格式 | 自动未扩大 | 脱敏提示 | 弱模型风险 | 占位符 |
|------|---------|---------|-----------|---------|-----------|--------|
| 000-context-pack | ✅ | — | ✅ | ⚠️ 部分 | ✅ | ✅ |
| 010-requirements | ✅ | — | ✅ | ❌ 缺失 | ✅ | ✅ |
| 020-design | ✅ | — | ✅ | ✅ 已补 | ✅ | ✅ |
| 030-implementation | ✅ | ⚠️ 格式 | ✅ | ❌ 缺失 | ✅ | ✅ |
| 040-light | ✅ | ⚠️ 缺示例 | ✅ | ❌ 缺失 | ✅ | ✅ |
| 060-preflight | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| 090-execution-record | ✅ | ⚠️ 格式 | ✅ | ✅ 已补 | ✅ | ✅ |
| _active-state | ✅ | — | ✅ | ⚠️ 部分 | ⚠️ 英文 | ✅ |
| subagent-decisions | ❌ P0 | ❌ P1 | ⚠️ 扩大 | ❌ P1 | ❌ P0 | ✅ |

### impact-pro 模板通过项

| 模板 | 逐项确认 | Step格式 | 自动未扩大 | 脱敏提示 | 弱模型风险 | 占位符 |
|------|---------|---------|-----------|---------|-----------|--------|
| 000-context-pack | ✅ | — | ✅ | ⚠️ 部分 | ✅ | ✅ |
| 010-requirements | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| 020-design | ✅ | — | ✅ | ✅ 已补 | ✅ | ✅ |
| 030-implementation | ✅ | ⚠️ 格式 | ✅ | ❌ P1 | ✅ | ✅ |
| 040-light | ✅ | ⚠️ 缺示例 | ✅ | ✅ | ✅ | ✅ |
| 060-preflight | ✅ | ⚠️ 格式 | ✅ | ✅ | ⚠️ 子字段 | ✅ |
| 090-execution-record | ✅ | ⚠️ 格式 | ✅ | ✅ 已补 | ✅ | ✅ |
| _active-state | ✅ | — | ✅ | ⚠️ 部分 | ⚠️ 子字段 | ✅ |
| final-readiness-audit | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| scorecard | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| subagent-decisions | ❌ P0 | ❌ P1 | ⚠️ 扩大 | ❌ P1 | ❌ P0 | ✅ |

### pathfinder 模板通过项

| 模板 | 只读提示 | 可信度格式 | 脱敏提示 | 不开药方 | 14节一致 | 弱模型风险 |
|------|---------|-----------|---------|---------|---------|-----------|
| project-map | ✅ | ⚠️ 合并格式 | ⚠️ P1 | ✅ | ✅ | ⚠️ P2 |

---

## 最优先修复项

1. **P0**: subagent-decisions.md（impact + impact-pro）执行选项加限定词，改"沙盒"为"eval 沙盒"，DECIDE 选项改名
2. **P1**: 030-implementation.md（impact + impact-pro）补脱敏提示
3. **P1**: 010-requirements.md + 040-light.md（impact）补脱敏提示
4. **P1**: pathfinder project-map.md 脱敏标签加风险性质声明
5. **P1**: _active-state.md + 060-preflight.md（impact-pro）补 target_project_root 子字段

---

## 弱模型误解风险评估

| 风险等级 | 模板 | 风险描述 |
|----------|------|----------|
| 🔴 高 | subagent-decisions.md | "subagent 自主决策：执行" / "subagent-confirm" 可能被解读为绕过人类确认 |
| 🟡 中 | _active-state.md | "not an authorization" 英文措辞弱于 SKILL.md 中文枚举式 |
| 🟡 中 | project-map.md | 合并可信度标记可能被弱模型模仿输出 |
| 🟢 低 | 030-implementation.md | 确认格式缺操作名称，弱模型可能省略 |
