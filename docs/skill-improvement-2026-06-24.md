# Skill 改进方案：基于盲测发现的协议优化

> 日期：2026-06-24
> 方案作者：Opus 4.8（基于 Composer 2.5 + Step 3.7 Flash 双模型盲测评审结果）
> 实施者：GLM-5.2（按本方案修改 5 个文件 + sibling 同步 + 测试验证）

---

## 一、背景

### 1.1 为什么要做这次改进

我们设计了三个 Skill（pathfinder、impact、impact-pro）来辅助 AI 在现有项目上做变更影响分析。之前用 Opus 做过 L1 评测，分数 89-93，看起来不错。但 L1 评测有两个问题：

1. **出题人知道答案**：case 是 skill 作者写的，预期命中文件和 trap 都是预设的，等于开卷考试。
2. **评判者和出题者是同一个模型**：自己考自己，分数虚高。

为了拿到"骗不了人"的证据，我们做了一轮盲测：用 6 个真实开发场景（不预设答案、不写 trap），让两个低成本模型（Composer 2.5 和 Step 3.7 Flash）分别执行，然后由 Opus 4.8 拿着源码逐条核实。

### 1.2 盲测结果概述

| 模型 | 平均分 | 安全门禁 | 证据编造 | 可直接 approve |
|------|--------|---------|---------|---------------|
| Composer 2.5 | 87.0 | 全 PASS | 0 例 | 3/6 |
| Step 3.7 Flash | 85.2 | 1 FAIL | 1 例 | 2/6 |

两个模型都能用，但暴露了 Skill 协议本身的若干问题。这些问题不是模型能力不够，而是协议没有要求模型做某些检查——即使 Opus 跑也可能在同样的地方翻车。

### 1.3 核心需求

改进的目标不是"让模型更聪明"，而是"让协议更防错"：通过在 Skill 协议中增加检查步骤，使任何模型（包括低成本模型）执行时都能避免盲测中暴露的问题。

改进遵循以下原则：
- **最小改动**：只在盲测暴露问题的地方加步骤，不做推测性设计
- **可验证**：每个改进项都有对应的复测 case
- **不增加用户负担**：新增的检查步骤在 agent 内部静默执行，不需要用户额外确认

---

## 二、盲测暴露的问题

### 2.1 Pathfinder 的问题

#### 问题 P1：Script Gate 不验证 facts 文件内容

**现象**：Step 3.7 Flash 在 B6（prisma-express-ts）中，`scan.json` 的 `file_count` 为 0（实际约 74 个文件），`git.json` 的 `head_short` 为 null（实际有 commit 346d60f），`git.json` 的 `toplevel` 指向了另一个项目（full-stack-fastapi-template）。但 Script Gate 5/5 通过了。

**根因**：`pf_validate.py` 只检查 `_project-map.md` 的内容（行号是否存在、凭证是否脱敏、SVG 是否安全、Section 13 是否非空、Mermaid 一致性），完全不检查 `facts/scan.json` 和 `facts/git.json` 的内容是否合理。Script Gate 通过只说明地图文档结构合规，不说明底层数据准确。

**影响**：地图的【0】基本信息节写"基于 commit 346d60f"和"小仓(跟踪文件 ~74)"——这两个数值本身是对的（agent 可能绕过 facts 文件自行获取了正确信息），但 facts 文件不实意味着 Script Gate 没有发挥应有的数据校验作用。如果 agent 没有自行纠正，地图就会基于错误的 facts 生成。

**证据**：
- `eval/runs/blind-2026-06-24-step37flash/B6.scorecard.json` — facts 文件严重错误
- `skills/pathfinder/scripts/pf_validate.py` — 只检查 map 文档，不检查 facts JSON

#### 问题 P2：缺少跨文件逻辑一致性检查

**现象**：Step 3.7 Flash 在 B6 中没有发现 `passport.ts` 的 select 只取 `id/email/name`，不包含 `role`，但 `auth.ts` 用 `user.role` 做 RBAC 权限检查。这意味着所有需要权限的端点，`roleRights.get(undefined)` 返回空数组，RBAC 实际失效。这是项目自身的一个真实安全 bug，Composer 2.5 发现了，Step 3.7 Flash 没有。

**根因**：Pathfinder 的 Phase 3（聚焦 + 预算深挖）中有【10】权限/认证模型概览节，要求"authn 方式"和"authz 方式"各写一条。但协议没有要求 agent 验证"认证链路中 JWT payload 选取的字段"与"鉴权链路中实际使用的字段"是否一致。agent 可以分别描述认证和鉴权，但不交叉验证两者之间的数据流是否完整。

**影响**：Pathfinder 的定位是"导航图不是权威源"，不要求发现所有 bug。但如果导航图在权限模型这一节遗漏了关键的安全缺陷，下游 impact 拿到这张图做变更分析时就会基于不完整的安全认知做判断。

**证据**：
- `test-projects/prisma-express-ts/src/config/passport.ts:16-21` — select 只有 id/email/name
- `test-projects/prisma-express-ts/src/middlewares/auth.ts:22` — 用 user.role 做 RBAC
- `eval/runs/blind-2026-06-24-step37flash/B6.scorecard.json` — 未发现 passport.ts select bug

---

### 2.2 Impact 的问题

#### 问题 I1：实施文档不验证引用的 API 方法名是否存在

**现象**：Step 3.7 Flash 在 B2（密码 MD5→BCrypt）的实施文档中写了 `userService.updateUserPassword(user.getUserId(), bcryptPassword)`，但这个方法在 ruoyi-vue 代码库中不存在。正确方法是 `userService.resetPwd(SysUser user)`，需要先 `user.setPassword(bcryptPassword)` 再调用。一个开发者照着实施文档写代码会直接编译报错。

**根因**：Impact 的 Phase 4 文档输出阶段，实施文档（`030-implementation.md`）的生成没有"验证引用的 API 方法名在代码库中真实存在"这一步。Phase 2 的上下文发现阶段虽然做了引用检查（反查调用方），但那是检查"谁调用了待修改的方法"，不是检查"实施文档中引用的方法是否存在"。模型在写实施代码时可能凭训练数据中的常见命名模式（`updateUserPassword`）编造方法名，而不是基于实际代码。

**影响**：实施文档是开发者照着写代码的依据。如果引用了不存在的方法名，开发者要么编译报错后自行查找（浪费时间），要么直接照抄导致 bug。

**证据**：
- `eval/runs/blind-2026-06-24-step37flash/B2.scorecard.json` — 编造 API 方法名
- `skills/impact/SKILL.md` Phase 4 — 无 API 方法名验证步骤
- `skills/impact/references/phase-2-context-discovery.md` — 引用检查只做反向引用，不做正向方法名验证

#### 问题 I2：实施代码缺少异常流分析

**现象**：Step 3.7 Flash 在 B1（操作日志加耗时）的实施代码中，`recordBasicOperLog` 方法调用 `SecurityUtils.getLoginUser()` 并做了 null 检查（`if (loginUser != null)`）。但 `SecurityUtils.getLoginUser()` 不返回 null，而是在用户未认证时抛出 `ServiceException`。这意味着对于登录接口（无认证用户），这段代码会抛异常被 catch 吞掉，导致 operlog 不被记录——恰恰是最核心的使用场景。

**根因**：Impact 的行为准则检查第 5 条要求"改前确认语义约定"——修改 status/enum/常量前先回看原定义。但这条规则没有覆盖"调用已有方法前确认其异常行为"。模型在写实施代码时，只看了方法签名（返回类型），没有看方法实现（何时抛异常），导致异常处理逻辑错误。

**影响**：实施代码的逻辑缺陷可能不会在编译时暴露，只在运行时才出问题。如果开发者照着实施文档写代码但不做异常流分析，就会在核心场景上踩坑。

**证据**：
- `eval/runs/blind-2026-06-24-step37flash/B1.scorecard.json` — getLoginUser 异常处理逻辑缺陷
- `test-projects/ruoyi-vue/ruoyi-common/.../SecurityUtils.java:72-82` — getLoginUser 抛异常不返回 null

---

### 2.3 Impact-pro 的问题

#### 问题 IP1：排除文件时不验证用户核心场景是否被覆盖

**现象**：Step 3.7 Flash 在 B3（用户加手机号）的 context-pack 中，将 `auth.route.ts` 排除在变更范围外，理由是"注册路由不直接涉及 phone，由 controller 透传"。但实际 `auth.controller.ts:8` 只解构 `email, password`，根本不透传 phone。用户的核心场景是"注册时填手机号"，注册走的是 `POST /v1/auth/register` → `auth.controller.ts` → `userService.createUser`，不走 `user.controller.ts`。排除 auth 路由后，用户的核心场景无法实现。

**根因**：Impact-pro 的 Phase 2 上下文发现阶段有"暂不纳入范围"的表格，要求写出排除原因。但协议没有要求 agent 在排除文件后验证"用户原话中描述的场景是否仍被剩余文件完全覆盖"。agent 可以基于一个错误假设（"controller 透传"）排除文件，而不检查这个假设是否成立。

**影响**：用户拿到 context-pack 后，以为影响面已经分析完整。但实际上用户最关心的入口（注册）被排除了，导致后续的设计文档和实施文档都缺少了关键修改点。

**证据**：
- `eval/runs/blind-2026-06-24-step37flash/B3.scorecard.json` — 排除了注册流程
- `test-projects/prisma-express-ts/src/controllers/auth.controller.ts:8` — 只解构 email+password
- `skills/impact-pro/SKILL.md` Phase 2 — 排除文件时不验证场景覆盖

---

## 三、改进方案

### 3.1 Pathfinder 改进

#### 改进 P1-A：Script Gate 增加 facts 文件内容校验

**改哪里**：`skills/pathfinder/scripts/pf_validate.py`

**改什么**：增加 V6 检查项，验证 `facts/scan.json` 和 `facts/git.json` 的关键字段非空且合理。

```
V6: facts 文件内容校验
  - scan.json 的 file_count > 0
  - scan.json 的 dir_tree 至少包含根目录 "/"
  - git.json 的 head_short 不为 null（如果是 Git 仓库）
  - git.json 的 toplevel 与 --repo-root 参数一致
```

**具体实现**：在 `pf_validate.py` 的 `validate()` 函数中，新增 `check_facts_content()` 函数，读取 facts 目录下的 JSON 文件并校验关键字段。

**预期效果**：如果 facts 文件的 file_count 为 0 或 git.json 的 commit 为 null，Script Gate 会报 FAIL，阻止写入地图，迫使 agent 修正 facts 文件。

#### 改进 P1-B：Phase 3 权限模型节增加"认证-鉴权字段一致性"自检

**改哪里**：`skills/pathfinder/references/phase-3-depth-fill.md`（【10】权限/认证模型概览节的填充方法）

**改什么**：在【10】节的填充步骤中，新增一个自检项：

```markdown
### 认证-鉴权字段一致性自检

在填写【10】权限/认证模型概览后，做以下检查：

1. 找到认证链路中 JWT payload 选取的字段（如 passport.js 的 select、JWT decode 后取的字段）
2. 找到鉴权链路中实际使用的字段（如 RBAC 检查中用的 user.role）
3. 对比两者：鉴权使用的字段是否都在认证链路中选取了？
4. 如果不一致 → 记录到【9】风险区域，标注"认证 payload 缺少鉴权所需字段"

注意：这个自检只用于发现明显的字段缺失，不要求做完整的跨文件逻辑审计。
```

**预期效果**：agent 在填权限模型节时，会主动检查 JWT payload 字段和 RBAC 使用字段是否一致，从而发现类似 passport.ts select bug 的问题。

---

### 3.2 Impact 改进

#### 改进 I1-A：Phase 4 实施文档增加"API 方法名存在性验证"步骤

**改哪里**：`skills/impact/SKILL.md` Phase 4 文档输出段 + `skills/impact/references/phase-5-execution.md`（实施文档生成后、用户确认前的检查）

**改什么**：在实施文档生成后、提交用户确认前，新增一个静默验证步骤：

```markdown
### API 方法名存在性验证（实施文档生成后执行）

实施文档中引用的所有"已有代码库中的方法名"必须经过 grep 验证存在。

检查范围：实施文档中 `xxxService.xxxMethod()` 格式的方法调用（排除本次新增的方法）。

验证方式：
1. 从实施文档中提取所有形如 `对象.方法名(` 的调用
2. 排除标注为"新增"的方法
3. 对每个方法名执行 grep 搜索，确认在代码库中存在定义
4. 如果找到不存在的方法名 → 修正实施文档，替换为正确的方法名
5. 如果无法确定正确方法名 → 在实施文档中标注"待确认：xxxMethod 是否存在"

这个步骤在 agent 内部静默执行，不需要用户确认。
```

**预期效果**：Step 3.7 Flash 在 B2 中写 `userService.updateUserPassword()` 时，这个步骤会 grep 搜索 `updateUserPassword`，发现代码库中没有这个方法名，从而迫使 agent 改为搜索正确的 `resetPwd` 方法。

#### 改进 I2-A：Phase 4 实施文档增加"被调方法异常行为确认"步骤

**改哪里**：`skills/impact/references/phase-5-execution.md`（实施文档生成后的检查清单）

**改什么**：在实施文档中引用已有方法时，如果该方法的返回值被用于条件判断（如 `if (result != null)`），必须确认该方法是否会在某些情况下抛异常而不是返回 null。

```markdown
### 被调方法异常行为确认

实施文档中，如果调用了已有方法并将其返回值用于条件判断（null 检查、空值检查等），
必须确认该方法的实际行为：

1. 打开方法定义，检查是否有 throw 语句
2. 如果方法在异常情况下抛异常而不是返回 null → 修正实施代码，使用 try-catch 替代 null 检查
3. 如果方法确实返回 null → 保持不变

常见模式：
- getXxxUser() 方法通常在用户不存在时抛异常，不返回 null
- findXxx() 方法通常在找不到时返回 null
- matchXxx() 方法通常返回 boolean，不抛异常

这个步骤在 agent 内部静默执行，不需要用户确认。
```

**预期效果**：Step 3.7 Flash 在 B1 中写 `if (loginUser != null)` 时，这个步骤会打开 `SecurityUtils.getLoginUser()` 的定义，发现它抛异常不返回 null，从而修正为 try-catch 结构。

---

### 3.3 Impact-pro 改进

#### 改进 IP1-A：Phase 2 排除文件时增加"用户场景覆盖验证"步骤

**改哪里**：`skills/impact-pro/references/phase-2-context-discovery.md`（上下文发现阶段的"暂不纳入范围"步骤）

**改什么**：在 agent 决定将某个文件列入"暂不纳入范围"时，必须验证用户的原始需求场景是否仍被剩余文件完全覆盖。

```markdown
### 用户场景覆盖验证（排除文件时执行）

当 agent 决定将某个文件/模块列入"暂不纳入范围"时，执行以下检查：

1. 回顾用户的原始需求原话（从 context-pack 第 1 节"变更意图"提取）
2. 识别用户描述的核心场景（如"注册时填手机号"→ 注册是入口场景）
3. 检查被排除的文件是否是该入口场景的必经路径
4. 如果被排除的文件是入口场景的必经路径 → 不得排除，纳入变更范围

验证方式：从用户场景的入口（如 POST /v1/auth/register）开始 trace，
确认到目标修改点（如 User model）的完整路径上，所有文件都在变更范围内。

这个步骤在 agent 内部静默执行，不需要用户确认。
```

**预期效果**：Step 3.7 Flash 在 B3 中准备排除 `auth.route.ts` 时，这个步骤会 trace "注册时填手机号"的路径：`POST /v1/auth/register` → `auth.controller.ts` → `userService.createUser`。发现 `auth.controller.ts` 是注册场景的必经路径，且它只解构 `email, password` 不透传 phone，因此不能排除。

---

## 四、改进项汇总

| # | 改进 ID | Skill | 改哪里 | 解决的盲测问题 |
|---|---------|-------|--------|--------------|
| 1 | P1-A | pathfinder | `scripts/pf_validate.py` 增加 V6 | B6 facts 文件内容全错但 Gate 通过 |
| 2 | P1-B | pathfinder | `references/phase-3-depth-fill.md` 【10】节 | B6 漏 passport.ts select bug |
| 3 | I1-A | impact | `SKILL.md` Phase 4 + `references/phase-5-execution.md` | B2 编造 `updateUserPassword` 方法名 |
| 4 | I2-A | impact | `references/phase-5-execution.md` | B1 getLoginUser 异常处理逻辑缺陷 |
| 5 | IP1-A | impact-pro | `references/phase-2-context-discovery.md` | B3 排除注册流程导致核心场景无法实现 |

---

## 五、复测计划

### 5.1 复测原则

- 跑分模型：Composer 2.5 + Step 3.7 Flash（回归和盲测复跑都用它们）
- 评审模型：GLM-5.2
- 盲测复跑用和盲测相同的 6 个 case（B1-B6），不重新出题
- 回归测试用 L1 case 中的 3 个（P1/R1/F1），每个对应一条改进链路
- 评审用和盲测相同的标准（JUDGE-RUBRIC.md）
- 改进前后的分数对比是核心指标

> **评审者变更说明**：盲测评审者是 Opus 4.8，复测评审者是 GLM-5.2（当前实施改进的模型）。评审标准（JUDGE-RUBRIC.md）不变，但评审者换了，分数对比会引入评审者差异这个变量——分数变化可能部分来自评审者不同，而非纯改进效果。因此判定时以「5 个改进项对应的盲测问题是否被修复」（定性验证点）为主要依据，分数变化为辅。

### 5.2 复测步骤

```
Step 1: 实施改进
  - 按改进项汇总表修改 5 个文件
  - 确保修改不破坏现有 L1 评测

Step 2: 回归测试
  - 跑分模型：Composer 2.5 + Step 3.7 Flash（和盲测相同）
  - 评审模型：GLM-5.2
  - 从 L1 全部 13 个 case 中选 3 个（P1/R1/F1），每个对应一条改进链路
  - prompt 文件：eval/cases/l1-regression/PROMPT-{composer25,step37flash}-regression.md
  - 评审标准：L1 case 的 expected 字段（must_hit_files、iron_rules、trap_for）
  - 定位：盲测是主验证（有改进前后对比），L1 回归是补充（确认没破坏盲测没覆盖的 case 类型）
  - 注意：L1 基线 runner 是 kimi/opus，不是这两个模型，分数不要和基线直接比

Step 3: 盲测复跑
  - 用 Composer 2.5 跑 B1-B6（改进后的协议）
  - 用 Step 3.7 Flash 跑 B1-B6（改进后的协议）
  - 产出目录带 -postfix 标记：blind-2026-XX-XX-composer25-v2/

Step 4: 评审对比
  - 评审者：GLM-5.2（拿源码逐条核实，流程和盲测相同，但评审者从 Opus 4.8 换为 GLM-5.2）
  - 重点检查：
    a. B6 facts 文件是否正确（验证 P1-A）
    b. B6 是否发现 passport.ts select bug（验证 P1-B）
    c. B2 实施文档是否还有编造方法名（验证 I1-A）
    d. B1 实施代码是否正确处理 getLoginUser 异常（验证 I2-A）
    e. B3 是否包含注册流程（验证 IP1-A）
  - 输出改进前后分数对比表（注意：评审者变更，分数对比含评审者差异变量，定性验证点为主）

Step 5: 判定
  - 每个改进项对应的盲测问题是否被修复
  - 改进前后平均分是否提升
  - 安全门禁 FAIL 数是否减少
```

### 5.3 成功标准

#### 盲测复跑验证点（主验证，有改进前后对比）

| 改进 ID | 复测验证点 | 成功标准 |
|---------|-----------|---------|
| P1-A | B6 的 facts 文件内容 | scan.json file_count > 0，git.json head_short 非 null |
| P1-B | B6 的【10】权限模型节 | 地图中提到 passport.ts select 与 auth.ts role 检查的字段不一致 |
| I1-A | B2 的实施文档 | 不再出现 `updateUserPassword`，改为 `resetPwd` 或标注待确认 |
| I2-A | B1 的实施代码 | getLoginUser 调用使用 try-catch，不做 null 检查 |
| IP1-A | B3 的 context-pack | auth.controller.ts 和 auth.validation.ts 在变更范围内 |

#### L1 回归验证点（补充，验证没破坏既有能力）

| Case | 对应改进 | 额外检查 |
|------|---------|---------|
| P1 | P1-A + P1-B | Script Gate 输出含 V6；facts 内容合理；【10】节做了认证-鉴权字段自检 |
| R1 | I1-A + I2-A | 实施文档方法名经 grep 验证；对已有方法调用确认了异常行为 |
| F1 | IP1-A | context-pack 排除文件附 trace 证据；做了用户场景覆盖验证 |

### 5.4 L1 回归结果（2026-06-24）

> 评审者：GLM-5.2
> 评分卡归档：`eval/runs/l1-regression-2026-06-24-{composer25,step37flash}/`
> 综合报告：`eval/runs/l1-regression-2026-06-24-summary.md`

#### 结果速览

| Case | Skill | 改进项 | Composer 2.5 | Step 3.7 Flash |
|------|-------|--------|:------------:|:--------------:|
| P1 | pathfinder | P1-A + P1-B | ✅ PASS | ❌ FAIL |
| R1 | impact | I1-A + I2-A | ✅ PASS | ❌ FAIL |
| F1 | impact-pro | IP1-A | ✅ PASS | ❌ FAIL |

#### 既有能力是否破坏

**否。** 两个 Runner 的 L1 基础 expected（must_hit_files、forbidden_claims、iron_rules、trap_for）全部通过，五项改进的加入没有破坏 skill 的既有分析能力。

#### 改进项触发情况

- **Composer 2.5**：5/5 改进项全部正确触发。P1 产出含 facts/scan.json + facts/git.json（V6 通过），【10】节有认证-鉴权字段一致性自检表；R1 实施文档有方法名 grep 预检表 + checkUserAllowed 异常行为确认；F1 context-pack 有用户场景覆盖验证表（5 项排除各附 trace 证据）。
- **Step 3.7 Flash**：0/5 改进项触发。P1 疑似复用了 06-14 的旧地图（无 facts/、无 P1-B 自检）；R1 无方法名预检和异常行为确认；F1 无 context-pack 导致 IP1-A 无法执行。Runner 自报「Script Gate 6/6 PASS」和「IP1-A 完成」与实际产出不符。

#### 结论

改进协议本身设计正确——Composer 2.5 证明协议可被执行且产出质量高。Step 3.7 Flash 的问题出在执行层（疑似加载旧版协议或复用旧产出），而非协议设计缺陷。盲测复跑（Step 3）可继续推进。

### 5.5 盲测复跑结果（2026-06-24）

> 评审者：GLM-5.2
> 评分卡归档：`eval/runs/blind-2026-06-24-v2-{composer25,step37flash}/`
> 综合报告：`eval/runs/blind-2026-06-24-v2-summary.md`

#### 五项改进验证总览

| 改进 ID | 验证 Case | 验证点 | Composer 2.5 | Step 3.7 Flash |
|---------|-----------|--------|:------------:|:--------------:|
| P1-A | B6 | facts 文件内容正确 | ✅ 修复 | ❌ 未修复（与改进前完全相同错误） |
| P1-B | B6 | 发现 passport.ts select bug | ❌ 退步（改进前发现，改进后不发现） | ❌ 未变 |
| I1-A | B2 | 不再编造方法名 | ✅ 修复 | ❌ 未修复（仍编造 updateUserPassword） |
| I2-A | B1 | 正确处理 getLoginUser 异常 | ✅ 修复（换 Filter 方案规避） | ❌ 未修复（仍做 null 检查） |
| IP1-A | B3 | 包含注册流程 | ❌ 未修复 | ❌ 未修复 |

#### Composer 2.5 改进效果

- **3/5 修复**：P1-A（facts 正确）、I1-A（不再编造方法名）、I2-A（换 Filter 方案规避 getLoginUser 问题）
- **1 项退步**：P1-B（改进前发现了 passport.ts select bug，改进后反而不发现，地图中无认证-鉴权一致性自检）
- **1 项未修复**：IP1-A（B3 仍排除注册流程，context-pack 无用户场景覆盖验证表）

#### Step 3.7 Flash 改进效果

- **0/5 修复**：5 项原始问题全部原样存在。与 L1 回归结论一致——Step 3.7 Flash 疑似未加载改进后的协议。B6 facts 文件与改进前完全相同错误（file_count=0, head_short=null, wrong toplevel），B2 仍编造 updateUserPassword，B1 仍做 null 检查，B3 仍排除注册流程。

#### 根因分析

1. **P1-B 退步**：P1-B 改进在 L1 回归（明确调用 `/pathfinder`）中被 Composer 2.5 正确触发，但在盲测（自然语言驱动）中未触发。模型可能未按 Phase 3 参考文件执行深度填充步骤。
2. **IP1-A 未生效**：与 P1-B 类似，盲测中模型未按 Phase 2 参考文件执行场景覆盖验证。两个 Runner 的 B3 context-pack 内容几乎完全相同。
3. **Step 3.7 Flash 零改进**：疑似使用了缓存的旧版 skill 协议或未读取更新后的参考文件。
4. **协议改进的局限性**：在明确调用 skill 的场景（L1 回归）中改进有效，在自然语言驱动的盲测场景中可能不生效。建议将 P1-B 和 IP1-A 从 `references/` 提升到 `SKILL.md` 主入口。

#### 结论

改进协议在 L1 回归中证明设计正确，但在盲测场景中可靠性不足。Composer 2.5 在 3 项改进上有效果（P1-A/I1-A/I2-A），但 P1-B 退步和 IP1-A 未生效需要进一步优化协议触发方式。Step 3.7 Flash 的问题在执行层而非协议设计——疑似未加载改进后的协议。

### 5.6 复测时间线

| 阶段 | 预计工时 | 产出 |
|------|---------|------|
| 实施改进 | 2-3 小时 | 5 个文件修改完成 |
| 回归测试 | 1 小时 | L1 定向回归（3 个 case × 2 模型 = 6 份产出） |
| 盲测复跑 | 2 小时（两个模型各 1 小时） | 12 份产出文件 |
| 评审对比 | 3-4 小时 | 改进前后分数对比报告 |
| **总计** | **8-10 小时** | |

---

## 六、v2 优化与 v3 测试计划

### 6.1 v2 盲测复跑后的根因分析

v2 盲测复跑暴露了协议触发率问题：**放在 `references/` 参考文件中的改进项，在自然语言驱动的盲测场景下不被模型读取**。只有 SKILL.md 主入口的内容才会被可靠加载。

具体表现：

| 改进项 | v2 状态 | 根因 |
|--------|---------|------|
| P1-B | Composer 退步（v1 发现 bug，v2 不发现） | 自检写在 `references/phase-3-depth-fill.md`，盲测不读；且"填表"式自检替代了深度分析 |
| IP1-A | 两个 Runner 都未触发 | 验证写在 `references/phase-2-context-discovery.md`，盲测不读 |
| I1-A/I2-A | Composer 部分修复（靠避开问题而非执行预检） | 已在 SKILL.md 但描述太简略，模型不执行具体步骤 |
| P1-A | Composer 修复 / Step 未修复 | Step 疑似使用缓存旧协议 |

### 6.2 v2 到 v3 的协议优化

针对触发率问题做了以下优化：

#### 优化 1：P1-B 提升到 pathfinder SKILL.md Phase 3 主入口

**改哪里**：`skills/pathfinder/SKILL.md` Phase 3 段

**改什么**：将"认证-鉴权字段一致性自检"从 `references/phase-3-depth-fill.md` 提升到 SKILL.md 正文，并强调"先 Read 源码再比对"，防止模型把自检当成"填表"而不做深度分析。

**解决的问题**：v2 中 Composer 2.5 的 P1-B 退步——改进前能自然发现 passport.ts bug，改进后反而只填比对表不读源码。

#### 优化 2：IP1-A 提升到 impact/impact-pro SKILL.md Phase 2 主入口

**改哪里**：`skills/impact/SKILL.md` Phase 2 段 + `skills/impact-pro/SKILL.md` Phase 2 段

**改什么**：将"用户场景覆盖验证"从 `references/phase-2-context-discovery.md` 提升到两个 skill 的 SKILL.md 正文，作为排除文件的前置必做步骤。

**解决的问题**：v2 中两个 Runner 的 B3 都排除了注册流程，IP1-A 完全未触发。

#### 优化 3：I1-A/I2-A 强化可操作性

**改哪里**：`skills/impact/SKILL.md` Phase 4 段 + `skills/impact-pro/SKILL.md` Phase 4 段

**改什么**：将"实施文档代码引用预检"从简略 bullet 扩展为带编号步骤的可操作清单，明确每一步做什么（提取方法名 → grep 验证 → 打开源码检查 throw）。

**解决的目的**：v2 中 Composer 2.5 靠"避开问题"（不引用具体方法、换 Filter 方案）而非"执行预检"修复。v3 希望模型真正执行预检步骤。

#### 优化 4：Step 3.7 Flash prompt 加固

**改哪里**：`eval/cases/blind/PROMPT-step37flash-v3.md`

**改什么**：在每个任务前显式要求 Read 对应 skill 的 SKILL.md 文件，确保使用最新版协议，不使用缓存。

**解决的目的**：v2 中 Step 3.7 Flash 0/5 改进，疑似使用缓存旧协议。

#### 优化 5：references 同步更新

**改哪里**：`skills/pathfinder/references/phase-3-depth-fill.md`

**改什么**：P1-B 自检步骤同步强调"先读源码再比对"，保持 SKILL.md 和 references 一致。

### 6.3 v3 测试计划

#### 测试范围

v3 只跑 4 个 case（B6/B1/B2/B3），聚焦 v2 中有问题的改进项。跳过 B4 和 B5——B4 没有对应改进项问题，B5 没有已知的 authn-authz bug 可验证 P1-B。

| Case | Skill | 对应改进 | v2 状态 | v3 验证目标 |
|------|-------|---------|---------|------------|
| B6 | pathfinder | P1-A + P1-B | P1-A 修复 / P1-B 退步 | P1-A 保持 / **P1-B 退步修复** |
| B1 | impact | I2-A | Composer 修复 / Step 未修复 | Composer 保持 / **Step 是否修复** |
| B2 | impact | I1-A | Composer 修复 / Step 未修复 | Composer 保持 / **Step 是否修复** |
| B3 | impact-pro | IP1-A | 两个 Runner 都未修复 | **两个 Runner 是否修复** |

#### 成功标准

| 改进 ID | Case | v3 成功标准 |
|---------|------|------------|
| P1-A | B6 | Composer 保持 ✅ / Step 需确认 |
| P1-B | B6 | **Composer 重新发现 passport.ts select bug** / Step 需确认 |
| I1-A | B2 | Composer 保持 ✅ / **Step 不再编造方法名** |
| I2-A | B1 | Composer 保持 ✅ / **Step 修正 null 检查** |
| IP1-A | B3 | **两个 Runner 都包含注册流程** |

#### 文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/PROMPT-composer25-v3.md` | Composer 2.5 v3 一键执行 prompt（4 个 case） |
| `eval/cases/blind/PROMPT-step37flash-v3.md` | Step 3.7 Flash v3 一键执行 prompt（含 Read SKILL.md 前置步骤） |
| `eval/cases/blind/BLIND-TEST-V3-DESIGN.md` | v3 测试设计文档（完整验证点和判定标准） |

#### 修改的 skill 文件

| 文件 | 改动 |
|------|------|
| `skills/pathfinder/SKILL.md` | Phase 3 新增"认证-鉴权字段一致性自检"（P1-B 提升主入口） |
| `skills/pathfinder/references/phase-3-depth-fill.md` | P1-B 自检同步强调"先读源码再比对" |
| `skills/impact/SKILL.md` | Phase 2 新增"用户场景覆盖验证"（IP1-A）+ Phase 4 强化 I1-A/I2-A 可操作性 |
| `skills/impact-pro/SKILL.md` | Phase 2 新增"用户场景覆盖验证"（IP1-A）+ Phase 4 强化 I1-A/I2-A 可操作性 |

### 6.4 v3 测试结果（2026-06-24）

> 评审者：GLM-5.2
> 评分卡归档：`eval/runs/blind-2026-06-24-v3-{composer25,step37flash}/`
> 综合报告：各自目录下的 `summary.md`

#### 五项改进验证总览（双模型 v3 对比）

| 改进 ID | 验证 Case | 验证点 | Composer 2.5 v3 | Step 3.7 Flash v3 |
|---------|-----------|--------|:---------------:|:-----------------:|
| P1-A | B6 | facts 文件内容正确 | ✅ 保持 | ❌ 仍 FAIL（未产出 facts 文件） |
| P1-B | B6 | 发现 passport.ts select bug | ✅ **退步修复** | ✅ **新修复** |
| I1-A | B2 | 不再编造方法名 | ✅ 保持（有显式预检节） | ✅ **新修复**（双表格预检） |
| I2-A | B1 | 正确处理 getLoginUser 异常 | ✅ 保持（Filter 方案） | ⚠️ PARTIAL（判档偏松绕过） |
| IP1-A | B3 | 包含注册流程 | ✅ **新修复** | ✅ **新修复** |

#### Composer 2.5 v3：5/5 全通过

详见 `eval/runs/blind-2026-06-24-v3-composer25/summary.md`。v2 的两个失败项（P1-B 退步 + IP1-A 未触发）全部修复，平均分 95.3，全部 would_approve: yes。

#### Step 3.7 Flash v3：3/5 修复 + 1/5 部分改善 + 1/5 仍 FAIL

详见 `eval/runs/blind-2026-06-24-v3-step37flash/summary.md`。相比 v2 的 0/5 全 FAIL，"强制 Read SKILL.md"步骤效果显著。

| Case | Skill | v3 分数 | 改进项 |
|------|-------|---------|--------|
| B6 | pathfinder | 83 | P1-A ❌ + P1-B ✅ |
| B1 | impact | 74 | I2-A ⚠️ PARTIAL |
| B2 | impact | 90 | I1-A ✅ |
| B3 | impact-pro | 95 | IP1-A ✅ |
| **平均** | | **85.5** | **3✅ + 1⚠️ + 1❌** |

#### v2 → v3 关键变化

1. **"强制 Read SKILL.md" 是 Step 3.7 Flash v3 突破的关键**：v2 中 0/5 全 FAIL（疑似未加载改进后协议），v3 在 prompt 中加入"每个任务前必须 Read 对应 SKILL.md"后，3 项直接修复（P1-B、I1-A、IP1-A），确认 v2 失败根因是协议未加载。
2. **P1-B 修复**：v2 无自检小节，v3 地图【10】节有完整 4 步「认证-鉴权字段一致性自检」，正确发现 passport.ts:17 未 select role 导致 RBAC 失效。
3. **I1-A 修复**：v2 编造 updateUserPassword，v3 有完整「实施前代码引用预检」双表格（方法存在性 + 异常行为），改用真实方法 resetUserPwd。
4. **IP1-A 修复**：v2 排除注册流程，v3 从需求→设计→实施三阶段完整覆盖 register。
5. **P1-A 仍 FAIL**：v2 是 facts 内容全错，v3 是根本未产出 facts 文件。模型读了 SKILL.md 但未运行 Script Gate 产出 facts。
6. **I2-A 部分改善**：v2 有 null 检查死代码，v3 定级 light 无实施代码故无缺陷，但根因是判档偏松（用户说"每次接口请求"，LogAspect 仅覆盖 @Log 注解接口，应 full），而非执行 I2-A 预检。

#### v3 结论

- **Composer 2.5**：协议优化完全成功，5/5 全通过，可作为生产级 Runner 使用。
- **Step 3.7 Flash**："强制 Read SKILL.md"策略验证成功，从 0/5 提升到 3/5 修复。B2/B3 产出质量接近 Composer 2.5。剩余两项需针对性优化：P1-A 需在 SKILL.md 中进一步强化 Script Gate 强制性；I2-A 需增加"覆盖范围语义核查"指引，提醒注意用户表述中的全量词与现有实现覆盖范围的差距。

### 6.5 v3 后续优化（P1-A 脚本强化 / I2-A 覆盖范围核查 / 需求文档去技术化）

基于 v3 测试结果中 Step 3.7 Flash 的两项未完全修复问题（P1-A 仍 FAIL、I2-A 判档偏松），以及盲测中发现的需求文档混入技术内容问题，做以下优化。

#### 优化 6：P1-A 脚本层强化——facts 文件缺失从 WARN 改为 FAIL

**问题**：v3 中 Step 3.7 Flash 跳过 Phase 1.5，未产出 facts 文件，但 `pf_validate.py` 对 facts 缺失只报 WARN（不影响 exit code），Script Gate 仍通过，地图写入成功。

**根因**：`pf_validate.py` 的 V6 检查中，facts 文件缺失走 warnings 分支，而 warnings 不影响 exit code（`sys.exit(1 if fails else 0)` 只有 fails 决定退出码）。模型跳过 Phase 1.5 后 Script Gate 不会拦截。

**改动**：
- `skills/pathfinder/scripts/pf_validate.py`：facts 文件缺失从 `warnings.append` 改为 `errors.append`（4 处：两文件都不存在、scan.json 单独不存在、git.json 单独不存在、docstring 注释）
- `skills/pathfinder/SKILL.md`：Phase 1.5 标题加"必做不可跳过" + 硬性规则 #8 新增 facts 前置检查步骤 + Phase 4 Script Gate 新增 facts 存在性确认步骤

**验证**：`check_facts_content(ruoyi-vue)` 返回 `errors` 非空（`warnings` 为空），facts 缺失现在会阻止 Script Gate 通过 ✅

#### 优化 7：I2-A 覆盖范围语义核查

**问题**：v3 中 Step 3.7 Flash 对 B1 判档偏松——用户说"每次接口请求都要记录"，LogAspect 通过 `@Log` 注解只覆盖部分接口，模型判 light（零改动确认），未识别覆盖范围缺口。

**改动**：
- `skills/impact/SKILL.md` Phase 2.5：增加"覆盖范围语义核查（定级前必做）"
- `skills/impact-pro/SKILL.md` Phase 2.5：增加"覆盖范围语义核查（定级前必做）"

**内容**：用户表述中出现"每次/所有/全部/任何/一律/每个"等全量词时，必须打开现有实现代码确认实际覆盖范围（如 AOP 切面 `@annotation(xxx)` 只覆盖注解接口），与用户要求的范围比对。有缺口 → 标记"倾向 full"，不是"零改动确认"。

#### 优化 8：需求文档去技术化

**问题**：v3 中 Composer 2.5 和 Step 3.7 Flash 的 `010-requirements.md` 都混入了技术内容（表名 `sys_user`、类名/方法名 `SecurityUtils.matchesPassword`、文件路径 `src/config/passport.ts`、代码片段、数据库字段定义 `varchar(100)`、依赖注入方式、日志框架等）。模板已有"不出现表名、类名、文件路径"约束，但 SKILL.md 主入口未强调，模型未遵守。

**改动**：
- `skills/impact/SKILL.md` Phase 4：增加"需求文档内容边界（010-requirements.md，生成后自检）"
- `skills/impact-pro/SKILL.md` Phase 4：增加"需求文档内容边界（010-requirements.md，生成后自检）"

**内容**：明确需求文档禁止出现的技术细节清单（表名、类名/方法名、文件路径、代码片段、字段类型定义、schema 变更方案、API 契约细节、依赖注入方式、ORM 用法等）+ 应该出现的业务内容（业务场景、功能需求、非功能需求业务指标、业务约束、验收标准）+ 生成后自检步骤（发现技术细节 → 移到 `020-design.md`，需求文档只留业务描述）。

#### 已知问题（已修复）

`pf_validate.py` 的 V6 toplevel 检查在 Windows 上因盘符大小写不匹配（git 输出 `E:/agent/...` vs 命令行参数 `e:\agent\...`）误报 FAIL。

**根因**：原代码用 `os.path.abspath(path).replace("\\", "/").rstrip("/")` 规范化路径，但 `os.path.abspath` 在 Windows 上不统一盘符大小写，导致字符串比较时 `E:/...` != `e:/...`。

**修复**：改用 `os.path.normcase(os.path.abspath(path))`。`os.path.normcase` 在 Windows 上统一盘符大小写 + 分隔符，在 Unix 上是 no-op（保留大小写敏感），是 Python 标准库的跨平台方案。同时去掉了多余的 `.replace("\\", "/").rstrip("/")`（`abspath` 内部 `normpath` 已统一分隔符并去尾部）。

**验证**：用之前误报 FAIL 的命令重跑，6/6 全 PASS，exit code 0。`os.path.normcase` 对 `E:/...` 和 `e:\...` 均规范化为 `e:\...`，比较结果 `equal: True`。

#### 本轮修改文件清单

| 文件 | 改动 |
|------|------|
| `skills/pathfinder/scripts/pf_validate.py` | V6 facts 缺失 WARN→FAIL（4 处） + V6 toplevel 大小写修复（`os.path.normcase`） |
| `skills/pathfinder/SKILL.md` | Phase 1.5 强化"必做不可跳过" + 硬性规则 #8 加 facts 前置 + Phase 4 Script Gate 加 facts 存在性 |
| `skills/impact/SKILL.md` | Phase 2.5 增加覆盖范围语义核查 + Phase 4 增加需求文档内容边界与自检 |
| `skills/impact-pro/SKILL.md` | Phase 2.5 增加覆盖范围语义核查 + Phase 4 增加需求文档内容边界与自检 |

---

## 七、附录：盲测评分文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/JUDGE-RUBRIC.md` | 盲测评审标准（6 维度 100 分 + 4 项安全门禁） |
| `eval/cases/blind/B1-B6` | 6 个盲测 case（含 prompt） |
| `eval/cases/blind/PROMPT-composer25.md` | Composer 2.5 盲测一键执行 prompt |
| `eval/cases/blind/PROMPT-step37flash.md` | Step 3.7 Flash 盲测一键执行 prompt |
| `eval/cases/blind/PROMPT-composer25-v3.md` | Composer 2.5 v3 盲测 prompt（4 个 case，聚焦改进项） |
| `eval/cases/blind/PROMPT-step37flash-v3.md` | Step 3.7 Flash v3 盲测 prompt（含 Read SKILL.md 前置步骤） |
| `eval/cases/blind/BLIND-TEST-V3-DESIGN.md` | v3 测试设计文档 |
| `eval/cases/blind/PROMPT-composer25-v4.md` | Composer 2.5 v4 盲测 prompt（含 Read SKILL.md，验证优化 6-8） |
| `eval/cases/blind/PROMPT-step37flash-v4.md` | Step 3.7 Flash v4 盲测 prompt（含 Read SKILL.md，验证优化 6-8） |
| `eval/cases/blind/BLIND-TEST-V4-DESIGN.md` | v4 测试设计文档（验证优化 6-8） |
| `eval/cases/l1-regression/PROMPT-composer25-regression.md` | Composer 2.5 L1 回归一键执行 prompt（P1/R1/F1） |
| `eval/cases/l1-regression/PROMPT-step37flash-regression.md` | Step 3.7 Flash L1 回归一键执行 prompt（P1/R1/F1） |
| `eval/cases/l1-regression/README.md` | L1 回归说明（case 选择、评审标准、和盲测的区别） |
| `eval/runs/blind-2026-06-24-composer25/` | Composer 2.5 v1 评审结果（6 份评分卡 + 总报告） |
| `eval/runs/blind-2026-06-24-step37flash/` | Step 3.7 Flash v1 评审结果（6 份评分卡 + 总报告） |
| `eval/runs/blind-2026-06-24-v2-composer25/` | Composer 2.5 v2 评审结果（改进后复跑） |
| `eval/runs/blind-2026-06-24-v2-step37flash/` | Step 3.7 Flash v2 评审结果（改进后复跑） |
| `eval/runs/blind-2026-06-24-v2-summary.md` | v2 盲测复跑综合报告 |
| `eval/runs/blind-2026-06-24-v3-composer25/` | Composer 2.5 v3 评审结果（4 份评分卡 + summary） |
| `eval/runs/blind-2026-06-24-v3-step37flash/` | Step 3.7 Flash v3 评审结果（4 份评分卡 + summary） |
| `eval/runs/blind-2026-06-24-v4-composer25/summary.md` | Composer 2.5 v4 评审总报告（源码级核实，验证优化 6-8） |
| `eval/runs/blind-2026-06-24-v4-step37flash/summary.md` | Step 3.7 Flash v4 评审总报告（源码级核实，验证优化 6-8） |
| `eval/runs/l1-regression-2026-06-24-composer25/` | Composer 2.5 L1 回归评审结果 |
| `eval/runs/l1-regression-2026-06-24-step37flash/` | Step 3.7 Flash L1 回归评审结果 |
| `eval/runs/l1-regression-2026-06-24-summary.md` | L1 回归综合报告 |
| `eval/runs/BLIND-TEST-FINAL-CONCLUSION.md` | 最终结论：两个模型能不能用、怎么用 |
