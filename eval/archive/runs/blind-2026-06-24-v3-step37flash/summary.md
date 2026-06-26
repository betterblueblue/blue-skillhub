# Step 3.7 Flash 盲测 v3 评审总结

> 评审日期：2026-06-24
> 评审模型：GLM-5.2
> Runner：Step 3.7 Flash
> 基线：v2 盲测复跑（`eval/runs/blind-2026-06-24-v2-step37flash/`）
> 对照：Composer 2.5 v3（`eval/runs/blind-2026-06-24-v3-composer25/`）

---

## 一、核心结论

### 1.1 五项改进验证总览

| 改进 ID | Case | 验证点 | v2 结果 | v3 结果 | 变化 |
|---------|------|--------|---------|---------|------|
| P1-A | B6 | facts 文件内容正确 | ❌ FAIL（内容全错） | ❌ FAIL（未产出） | 维持 FAIL（性质变化） |
| P1-B | B6 | 发现 passport.ts select bug | ❌ FAIL（无自检） | ✅ **修复** | **新修复** |
| I1-A | B2 | 不编造方法名 | ❌ FAIL（编造 updateUserPassword） | ✅ **修复** | **新修复** |
| I2-A | B1 | 正确处理 getLoginUser 异常 | ❌ FAIL（null 检查死代码） | ⚠️ PARTIAL（判档偏松绕过） | 部分改善 |
| IP1-A | B3 | 包含注册流程 | ❌ FAIL（排除注册） | ✅ **修复** | **新修复** |

**Step 3.7 Flash v3：3/5 修复 + 1/5 部分改善 + 1/5 仍 FAIL。** 相比 v2 的 0/5 全 FAIL，"强制 Read SKILL.md"步骤效果显著——3 项直接修复，1 项间接改善。

### 1.2 分数总览

| Case | Skill | v3 分数 | v2 状态 | 改进项 |
|------|-------|---------|---------|--------|
| B6 | pathfinder | 83 | 全 FAIL | P1-A ❌ + P1-B ✅ |
| B1 | impact | 74 | 全 FAIL | I2-A ⚠️ PARTIAL |
| B2 | impact | 90 | 全 FAIL | I1-A ✅ |
| B3 | impact-pro | 95 | 全 FAIL | IP1-A ✅ |
| **平均** | | **85.5** | | **3✅ + 1⚠️ + 1❌** |

> 对照 Composer 2.5 v3 平均 95.3（5/5 全通过），Step 3.7 Flash v3 平均 85.5，差距 9.8 分，主要来自 B6（P1-A facts 缺失）和 B1（判档偏松）。

### 1.3 关键发现

1. **"强制 Read SKILL.md" 是 v3 突破的关键**：v2 中 Step 3.7 Flash 0/5 全 FAIL，疑似未加载改进后的 skill 协议（产出与改进前完全相同）。v3 在 prompt 中加入"每个任务前必须 Read 对应 SKILL.md"步骤后，3 项直接修复（P1-B、I1-A、IP1-A），证明 v2 的失败根因确实是协议未加载。
2. **P1-B 修复**：v2 无自检小节，v3 地图【10】节有完整 4 步「认证-鉴权字段一致性自检」，正确发现 passport.ts:17 未 select role 导致 RBAC 失效。
3. **I1-A 修复**：v2 编造 updateUserPassword，v3 有完整「实施前代码引用预检」双表格（方法存在性 + 异常行为），改用真实方法 resetUserPwd 并标注行号。
4. **IP1-A 修复**：v2 排除注册流程（核心场景无法实现），v3 从需求→设计→实施三阶段完整覆盖 register（R2 需求 + register schema/controller/test）。
5. **P1-A 仍 FAIL**：v2 是 facts 文件内容全错（file_count=0, head_short=null），v3 是根本未产出 facts 文件（B6 目录仅有 _project-map.md）。地图通过其他方式获取了正确 commit（346d60f）和文件数（~92），但未按协议保存为 facts 文件。
6. **I2-A 部分改善**：v2 有 null 检查死代码，v3 定级 light 无实施代码故无缺陷，但根因是判档偏松（用户说"每次接口请求"，LogAspect 仅覆盖 @Log 注解接口，应 full），而非执行了 I2-A 预检。

---

## 二、逐项详细评审

### 2.1 P1-A：B6 facts 文件内容校验

| 字段 | v3 情况 | 判定 |
|------|---------|------|
| facts/ 目录存在 | ❌ 不存在（B6 目录仅 _project-map.md） | FAIL |
| scan.json | ❌ 未产出 | FAIL |
| git.json | ❌ 未产出 | FAIL |
| 地图内 commit | 346d60f（正确，但来源非 facts） | — |
| 地图内文件数 | ~92（正确，但来源非 facts） | — |

**v2→v3 变化**：v2 有 facts 文件但内容全错（file_count=0, head_short=null, toplevel=full-stack-fastapi-template），v3 根本未产出 facts 文件。两种均为 FAIL，但 v3 性质更严重——连文件都没生成，Script Gate V6 直接报 FAIL。

**判定：FAIL ❌（维持 FAIL，性质从"内容错"变为"未产出"）**

### 2.2 P1-B：B6 认证-鉴权字段一致性自检

| 检查项 | v3 结果 |
|--------|---------|
| 【10】节有「认证-鉴权字段一致性自检」 | ✅ 有（4 个编号步骤） |
| 认证链路字段记录 | ✅ `select: { id, email, name }` — passport.ts:17-21 |
| 鉴权链路字段记录 | ✅ `roleRights.get(user.role)` — auth.ts:22 |
| 比对结果 | ✅ `user.role` 不在 select 中，运行时 undefined，RBAC 完全失效 |
| 不一致记录 | ✅ "认证 payload 缺少鉴权所需字段" |
| 记录到【9】风险区域 | ✅ "RBAC 权限系统实质失效" |
| Executive Summary Top 3 风险 | ✅ #1 "RBAC 权限系统实质失效" |

**源码核实**：
- `passport.ts:17` select 确实只有 `{ id: true, email: true, name: true }` — 不含 role ✅
- `auth.ts:22` 确实用 `roleRights.get(user.role)` ✅

**判定：PASS ✅（v2 FAIL → v3 修复）**

### 2.3 I1-A：B2 实施文档方法名存在性验证

| 检查项 | v3 结果 |
|--------|---------|
| 有「实施前代码引用预检」小节 | ✅ 有（双表格：方法存在性 + 异常行为） |
| 出现编造的 updateUserPassword | ✅ 未出现 |
| 引用的方法名经 grep 验证 | ✅ matchesPassword/encryptPassword/Md5Utils.hash/resetUserPwd 均标注行号 + "✅ 已存在" |
| 被调方法异常行为确认 | ✅ BCrypt.matches(返回 boolean)、Md5Utils.hash(异常返回 null 需检查)、resetUserPwd(返回 int) |

**源码核实**：
- `ISysUserService.java:190` — `resetUserPwd(Long userId, String password)` 存在 ✅
- `SecurityUtils.java:111` — `matchesPassword(String, String)` 存在 ✅

**判定：PASS ✅（v2 FAIL → v3 修复）**

### 2.4 I2-A：B1 被调方法异常行为确认

| 检查项 | v3 结果 |
|--------|---------|
| 产出中有 getLoginUser null 检查缺陷 | ✅ 无（定级 light，无 030-implementation.md） |
| 定级合理性 | ❌ light 偏松（应 full） |
| 执行 I2-A 异常行为预检 | ❌ 未执行（因无实施代码） |
| 识别覆盖范围缺口 | ❌ 未识别（用户说"每次请求"，LogAspect 仅覆盖 @Log） |

**对比 Composer 2.5**：Composer 2.5 正确定级 full，设计 OperLogTimingFilter (OncePerRequestFilter) 覆盖全局，完全不调用 getLoginUser，从架构规避异常问题。Step 3.7 Flash 误判为"已完整实现"定级 light，因无实施代码而技术规避了 null 检查缺陷，但未执行 I2-A 预检，且判档有误。

**判定：PARTIAL ⚠️（v2 FAIL → v3 部分改善：缺陷消失但非预检功劳，判档偏松）**

### 2.5 IP1-A：B3 用户场景覆盖验证

| 检查项 | v3 结果 |
|--------|---------|
| 需求阶段纳入注册 | ✅ R2「注册接口接受可选 phone」(P0) + 4.1 接口契约变更 |
| 设计阶段纳入注册 | ✅ register schema + register controller + register 测试用例 |
| 实施阶段纳入注册 | ✅ Step 3 auth.validation.ts + Step 8 auth.controller.ts + Step 11.2 register 测试 |
| 排除注册流程 | ✅ 未排除（v2 排除了 auth.route.ts/auth.controller.ts） |
| 测试覆盖注册 | ✅ 3 个用例（成功带 phone/格式错误/唯一性冲突） |

**源码核实**：
- `auth.controller.ts:8` — `const { email, password } = req.body;` 确实只解构 email 和 password，不含 phone ✅

**判定：PASS ✅（v2 FAIL → v3 完全修复）**

---

## 三、v2 → v3 改进效果对比

| 改进 ID | v2 状态 | v3 状态 | 优化措施 | 效果 |
|---------|---------|---------|---------|------|
| P1-B | ❌ FAIL（无自检） | ✅ PASS（4 步自检） | 强制 Read SKILL.md + P1-B 提升到 SKILL.md Phase 3 | **新修复** |
| I1-A | ❌ FAIL（编造方法） | ✅ PASS（双表格预检） | 强制 Read SKILL.md + I1-A 强化可操作性 | **新修复** |
| IP1-A | ❌ FAIL（排除注册） | ✅ PASS（三阶段覆盖） | 强制 Read SKILL.md + IP1-A 提升到 SKILL.md Phase 2 | **新修复** |
| I2-A | ❌ FAIL（null 检查死代码） | ⚠️ PARTIAL（判档偏松绕过） | 强制 Read SKILL.md（但模型选择定 light 规避） | 部分改善 |
| P1-A | ❌ FAIL（内容全错） | ❌ FAIL（未产出） | 强制 Read SKILL.md（但模型未运行 Script Gate 产出 facts） | 维持 FAIL |

### 3.1 v2 失败根因确认

v2 中 Step 3.7 Flash 0/5 全 FAIL，评分卡多次记录"疑似未加载改进后的 skill 协议"（产出与改进前完全相同）。v3 在 prompt 中加入"每个任务前必须 Read 对应 SKILL.md"步骤后，3 项直接修复，**确认 v2 失败根因是协议未加载**，而非协议本身无效。

### 3.2 v3 仍未解决的两项

1. **P1-A（facts 文件）**：模型读了 SKILL.md 但未运行 Script Gate 产出 facts 文件。可能是模型理解为"读地图模板"而跳过了脚本执行步骤，或脚本执行环境问题。需进一步排查 pathfinder SKILL.md 中 Script Gate 的强制描述是否足够。
2. **I2-A（判档偏松）**：模型读了 SKILL.md 但对 B1 判档为 light（"零改动确认"），未识别"每次接口请求"vs"@Log 注解"的覆盖范围差距。这是分析深度问题，而非协议加载问题。

---

## 四、与 Composer 2.5 v3 对比

| 维度 | Composer 2.5 v3 | Step 3.7 Flash v3 | 差距 |
|------|-----------------|-------------------|------|
| 改进项通过数 | 5/5 | 3/5（+1 PARTIAL） | -2 |
| 平均分 | 95.3 | 85.5 | -9.8 |
| B6 (pathfinder) | 96 | 83 | -13（P1-A facts 缺失） |
| B1 (impact) | 93 | 74 | -19（判档偏松 light） |
| B2 (impact) | 95 | 90 | -5 |
| B3 (impact-pro) | 97 | 95 | -2 |
| would_approve yes 数 | 4/4 | 2/4 | -2 |

**分析**：
- B2、B3 两项差距很小（-5、-2），Step 3.7 Flash 在 impact/impact-pro 的 full 档实施文档质量接近 Composer 2.5。
- B6 差距大（-13），主因是 P1-A facts 文件未产出（protocol_compliance 4 vs 9）。
- B1 差距最大（-19），主因是判档偏松（tier_judgment 8 vs 15）——Composer 2.5 正确定 full 设计 Filter，Step 3.7 Flash 误判 light。

---

## 五、结论

### 5.1 "强制 Read SKILL.md" 策略验证成功

v3 的核心优化是在 prompt 中强制要求"每个任务前必须 Read 对应 SKILL.md"。这一策略对 Step 3.7 Flash 效果显著：
- v2：0/5 全 FAIL（协议未加载）
- v3：3/5 修复 + 1/5 部分改善 + 1/5 仍 FAIL

3 项直接修复（P1-B、I1-A、IP1-A）证明：只要模型读到了改进后的协议，就能执行相应的预检和自检步骤。

### 5.2 剩余问题需针对性优化

1. **P1-A facts 文件产出**：需在 pathfinder SKILL.md 中进一步强化 Script Gate 的强制性，明确"必须运行 pf_validate.py 并产出 facts/scan.json + facts/git.json"，否则地图视为不合规。
2. **I2-A 判档深度**：需在 impact SKILL.md 中增加"覆盖范围语义核查"指引，提醒模型注意用户表述中的"每次/所有/全部"等全量词与现有实现覆盖范围的差距。

### 5.3 产出质量

Step 3.7 Flash v3 的 B2（90 分）和 B3（95 分）产出质量接近 Composer 2.5，可作为开发依据。B6 地图内容质量高（发现 RBAC bug + 类型不一致），但 facts 文件缺失影响合规性。B1 现状核查扎实但判档偏松，需用户复核。
