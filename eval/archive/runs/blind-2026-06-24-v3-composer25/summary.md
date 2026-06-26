# Composer 2.5 盲测 v3 评审总结

> 评审日期：2026-06-24
> 评审模型：GLM-5.2
> Runner：Composer 2.5
> 基线：v2 盲测复跑（`eval/runs/blind-2026-06-24-v2-composer25/`）

---

## 一、核心结论

### 1.1 五项改进验证总览

| 改进 ID | Case | 验证点 | v2 结果 | v3 结果 | 变化 |
|---------|------|--------|---------|---------|------|
| P1-A | B6 | facts 文件内容正确 | ✅ 修复 | ✅ 保持 | 维持 |
| P1-B | B6 | 发现 passport.ts select bug | ❌ 退步 | ✅ **修复** | **退步修复** |
| I1-A | B2 | 不编造方法名 | ✅ 修复 | ✅ 保持 | 维持（且有显式预检节） |
| I2-A | B1 | 正确处理 getLoginUser 异常 | ✅ 修复 | ✅ 保持 | 维持 |
| IP1-A | B3 | 包含注册流程 | ❌ 未修复 | ✅ **修复** | **新修复** |

**Composer 2.5 v3：5/5 全部通过！** v2 的两个失败项（P1-B 退步 + IP1-A 未触发）全部修复。

### 1.2 分数总览

| Case | Skill | v3 分数 | v2 分数 | 变化 | 改进项 |
|------|-------|---------|---------|------|--------|
| B6 | pathfinder | 96 | — | — | P1-A ✅ + P1-B ✅ |
| B1 | impact | 93 | — | — | I2-A ✅ |
| B2 | impact | 95 | — | — | I1-A ✅ |
| B3 | impact-pro | 97 | — | — | IP1-A ✅ |
| **平均** | | **95.3** | | | **5/5** |

> 注：v2 评审也是 GLM-5.2，评审者变量已消除，分数可直接对比。

### 1.3 关键发现

1. **P1-B 退步完全修复**：v2 中 Composer 2.5 未发现 passport.ts select bug（退步），v3 中重新发现并记录到【9】风险区域和 Executive Summary Top 3 风险。提升到 SKILL.md 主入口 + 强调"先读源码再比对"有效。
2. **IP1-A 完全修复**：v2 中两个 Runner 都排除了注册流程，v3 中 Composer 2.5 正确纳入注册流程（auth.validation.ts + auth.controller.ts），context-pack 有显式的"用户场景覆盖验证"小节。提升到 SKILL.md 主入口有效。
3. **I1-A 比 v2 更好**：v2 是靠"避免引用具体方法"修复，v3 有显式的"方法存在性预检"小节，说明强化可操作性生效。
4. **I2-A 保持修复**：Filter 方案规避 getLoginUser 异常问题，与 v2 策略一致。
5. **额外发现**：B6 地图不仅发现了 passport select bug，还额外发现了 auth.ts:26 userId 类型不一致 bug（string vs number 严格不等），分析深度超出改进项要求。

---

## 二、逐项详细评审

### 2.1 P1-A：B6 facts 文件内容校验

| 字段 | v3 值 | 实际值 | 判定 |
|------|-------|--------|------|
| scan.json file_count | 90 | ~90 | ✅ |
| scan.json budget_tier | small | small | ✅ |
| git.json head_short | 346d60f | 346d60f | ✅ |
| git.json toplevel | prisma-express-ts | prisma-express-ts | ✅ |

**判定：PASS ✅（维持 v2 修复状态）**

### 2.2 P1-B：B6 认证-鉴权字段一致性自检

| 检查项 | v3 结果 |
|--------|---------|
| 【10】节有「认证-鉴权字段一致性(已读源码比对)」 | ✅ 有 |
| 认证链路字段记录 | ✅ `{id, email, name}` — passport.ts:17 |
| 鉴权链路字段记录 | ✅ `user.role, user.id` — auth.ts:22,26 |
| 发现不一致 | ✅ "role 未在 Passport select 中，RBAC 读到的 user.role 为 undefined" |
| 记录到【9】风险区域 | ✅ "RBAC 字段不一致: passport select 仅 {id,email,name}" |
| Executive Summary Top 3 风险 | ✅ #1 "Passport JWT 查询未 select role" |

**源码核实**：
- `passport.ts:17` select 确实只有 `{ id: true, email: true, name: true }` — 不含 role ✅
- `auth.ts:22` 确实用 `roleRights.get(user.role)` ✅

**判定：PASS ✅（v2 退步完全修复）**

### 2.3 I1-A：B2 实施文档方法名存在性验证

| 检查项 | v3 结果 |
|--------|---------|
| 有「方法存在性预检」小节 | ✅ 有 |
| 出现编造的 updateUserPassword | ✅ 未出现 |
| 引用的方法名经 grep 验证 | ✅ encryptPassword, matchesPassword, resetUserPwd 均标注"已存在" |

**源码核实**：
- `ISysUserService.java:190` — `resetUserPwd(Long userId, String password)` 存在 ✅
- `SecurityUtils.java:111` — `matchesPassword(String, String)` 存在 ✅

**判定：PASS ✅（维持 v2 修复，且有显式预检小节——比 v2 更好）**

### 2.4 I2-A：B1 被调方法异常行为确认

| 检查项 | v3 结果 |
|--------|---------|
| 对 getLoginUser 做 null 检查 | ✅ 不调用 getLoginUser |
| 方案 | OperLogTimingFilter (OncePerRequestFilter) |
| 方法名验证 | ✅ insertOperlog 已存在于 SysOperLogServiceImpl |

**源码核实**：
- `SysOperLogServiceImpl.java:27` — `insertOperlog(SysOperLog)` 存在 ✅

**判定：PASS ✅（维持 v2 修复）**

### 2.5 IP1-A：B3 用户场景覆盖验证

| 检查项 | v3 结果 |
|--------|---------|
| context-pack 有「用户场景覆盖验证」小节 | ✅ 有（第 4 节） |
| 识别入口场景 | ✅ POST /v1/auth/register |
| auth.validation.ts 在变更范围内 | ✅ 相关性 3，标注"注册校验入口" |
| auth.controller.ts 在变更范围内 | ✅ 相关性 3，标注"注册控制器入口" |
| 实施文档修改注册流程 | ✅ Step 3 修改 auth.validation.ts，Step 4 修改 auth.controller.ts |
| 排除结论 | ✅ "不得排除 auth.validation.ts / auth.controller.ts" |

**源码核实**：
- `auth.controller.ts:8` — `const { email, password } = req.body;` 确实只解构 email 和 password，不含 phone ✅

**判定：PASS ✅（v2 未修复 → v3 完全修复）**

---

## 三、v2 → v3 改进效果对比

| 改进 ID | v2 状态 | v3 状态 | 优化措施 | 效果 |
|---------|---------|---------|---------|------|
| P1-B | ❌ 退步（不发现 bug） | ✅ 修复（重新发现 bug） | 提升到 SKILL.md Phase 3 + 强调"先读源码再比对" | **退步修复** |
| IP1-A | ❌ 未触发（排除注册流程） | ✅ 修复（包含注册流程） | 提升到 SKILL.md Phase 2 | **新修复** |
| I1-A | ✅ 修复（靠避开问题） | ✅ 修复（有显式预检节） | 强化可操作性（简略 bullet → 编号步骤） | **质量提升** |
| I2-A | ✅ 修复（Filter 方案） | ✅ 修复（Filter 方案） | 无额外优化 | 维持 |
| P1-A | ✅ 修复 | ✅ 修复 | 无额外优化 | 维持 |

---

## 四、结论

### 4.1 协议优化完全成功

将 P1-B 和 IP1-A 从 `references/` 提升到 `SKILL.md` 主入口的策略完全有效：
- P1-B 退步修复：模型在盲测中读到了 SKILL.md 中的自检要求，并执行了"先读源码再比对"
- IP1-A 新修复：模型在盲测中读到了 SKILL.md 中的场景覆盖验证要求，正确纳入了注册流程

### 4.2 I1-A 质量提升

强化 I1-A 的可操作性（从简略 bullet 扩展为带编号步骤的清单）使模型从"靠避开问题修复"变为"执行显式预检"，产出质量更高。

### 4.3 产出质量

Composer 2.5 v3 的 4 份产出平均分 95.3，全部 `would_approve: yes`，可以直接作为开发依据。B6 地图还额外发现了 userId 类型不一致 bug，分析深度超出改进项要求。
