# Skill 改进方案：基于盲测发现的协议优化

> 日期：2026-06-24
> 作者：Opus 4.8（基于 Composer 2.5 + Step 3.7 Flash 双模型盲测评审结果）

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

- 复测用和盲测相同的 6 个 case（B1-B6），不重新出题
- 复测用和盲测相同的两个模型（Composer 2.5 + Step 3.7 Flash）
- 评审用和盲测相同的标准（JUDGE-RUBRIC.md）
- 改进前后的分数对比是核心指标

### 5.2 复测步骤

```
Step 1: 实施改进
  - 按改进项汇总表修改 5 个文件
  - 确保修改不破坏现有 L1 评测

Step 2: 回归测试
  - 跑现有 L1 评测（3 个 Skill 各自的 baselines）
  - 确认改进没有导致已有 case 分数下降

Step 3: 盲测复跑
  - 用 Composer 2.5 跑 B1-B6（改进后的协议）
  - 用 Step 3.7 Flash 跑 B1-B6（改进后的协议）
  - 产出目录带 -postfix 标记：blind-2026-XX-XX-composer25-v2/

Step 4: 评审对比
  - 评审者拿源码逐条核实（和盲测相同流程）
  - 重点检查：
    a. B6 facts 文件是否正确（验证 P1-A）
    b. B6 是否发现 passport.ts select bug（验证 P1-B）
    c. B2 实施文档是否还有编造方法名（验证 I1-A）
    d. B1 实施代码是否正确处理 getLoginUser 异常（验证 I2-A）
    e. B3 是否包含注册流程（验证 IP1-A）
  - 输出改进前后分数对比表

Step 5: 判定
  - 每个改进项对应的盲测问题是否被修复
  - 改进前后平均分是否提升
  - 安全门禁 FAIL 数是否减少
```

### 5.3 成功标准

| 改进 ID | 复测验证点 | 成功标准 |
|---------|-----------|---------|
| P1-A | B6 的 facts 文件内容 | scan.json file_count > 0，git.json head_short 非 null |
| P1-B | B6 的【10】权限模型节 | 地图中提到 passport.ts select 与 auth.ts role 检查的字段不一致 |
| I1-A | B2 的实施文档 | 不再出现 `updateUserPassword`，改为 `resetPwd` 或标注待确认 |
| I2-A | B1 的实施代码 | getLoginUser 调用使用 try-catch，不做 null 检查 |
| IP1-A | B3 的 context-pack | auth.controller.ts 和 auth.validation.ts 在变更范围内 |

### 5.4 复测时间线

| 阶段 | 预计工时 | 产出 |
|------|---------|------|
| 实施改进 | 2-3 小时 | 5 个文件修改完成 |
| 回归测试 | 1 小时 | L1 评测分数无下降 |
| 盲测复跑 | 2 小时（两个模型各 1 小时） | 12 份产出文件 |
| 评审对比 | 3-4 小时 | 改进前后分数对比报告 |
| **总计** | **8-10 小时** | |

---

## 六、附录：盲测评分文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/JUDGE-RUBRIC.md` | 盲测评审标准（6 维度 100 分 + 4 项安全门禁） |
| `eval/cases/blind/B1-B6` | 6 个盲测 case（含 prompt） |
| `eval/runs/blind-2026-06-24-composer25/` | Composer 2.5 评审结果（6 份评分卡 + 总报告） |
| `eval/runs/blind-2026-06-24-step37flash/` | Step 3.7 Flash 评审结果（6 份评分卡 + 总报告） |
| `eval/runs/BLIND-TEST-FINAL-CONCLUSION.md` | 最终结论：两个模型能不能用、怎么用 |
