# 盲测复跑评审报告（改进后 v2）

> 评审日期：2026-06-24
> 评审模型：GLM-5.2（Judge）
> Runner 模型：Composer 2.5 / Step 3.7 Flash
> 基线：`eval/runs/blind-2026-06-24-{composer25,step37flash}/`（改进前，Opus 4.8 评审）
> 本次：`eval/runs/blind-2026-06-24-v2-{composer25,step37flash}/`（改进后，GLM-5.2 评审）

> **评审者变更说明**：基线由 Opus 4.8 评审，本次由 GLM-5.2 评审。分数差异含评审者变量。以下分析以**定性验证点**（5 个改进项对应的盲测问题是否被修复）为主要依据，分数对比为辅。

---

## 一、核心结论

### 1.1 五项改进验证总览

| 改进 ID | 验证 Case | 验证点 | Composer 2.5 | Step 3.7 Flash |
|---------|-----------|--------|:------------:|:--------------:|
| P1-A | B6 | facts 文件内容正确 | ✅ **修复** | ❌ **未修复** |
| P1-B | B6 | 发现 passport.ts select bug | ❌ **退步** | ❌ 未变（原就未发现） |
| I1-A | B2 | 不再编造方法名 | ✅ **修复** | ❌ **未修复** |
| I2-A | B1 | 正确处理 getLoginUser 异常 | ✅ **修复** | ❌ **未修复** |
| IP1-A | B3 | 包含注册流程 | ❌ **未修复** | ❌ **未修复** |

**Composer 2.5：3/5 修复（P1-A、I1-A、I2-A），1 项退步（P1-B），1 项未修复（IP1-A）**
**Step 3.7 Flash：0/5 修复，全部原始问题依然存在**

### 1.2 关键发现

1. **Composer 2.5 在 3 项改进上有效果**：P1-A facts 文件内容正确了；I1-A 不再编造方法名；I2-A 通过换方案（Filter 替代 LogAspect @Around）规避了 getLoginUser 异常问题。
2. **P1-B 出现退步**：改进前的盲测中 Composer 2.5 发现了 passport.ts select bug；改进后复跑中两个 Runner 都没发现。P1-B 改进项（认证-鉴权字段一致性自检）在盲测中未被触发。
3. **IP1-A 在两个 Runner 上都未生效**：两个 B3 context-pack 都排除了注册流程（auth.route.ts / auth.controller.ts），都缺少「用户场景覆盖验证」表。两个 context-pack 内容几乎完全相同。
4. **Step 3.7 Flash 零改进**：5 项原始问题全部原样存在——facts 文件仍全错、仍编造 updateUserPassword、仍对 getLoginUser 做 null 检查、仍排除注册流程。与 L1 回归结论一致：Step 3.7 Flash 疑似未加载改进后的协议。

---

## 二、逐项详细评审

### 2.1 P1-A：B6 facts 文件内容校验

**原始问题（改进前）**：Step 3.7 Flash 的 B6 facts 文件严重错误——scan.json file_count=0（实际 ~74），git.json head_short=null（实际 346d60f），git.json toplevel 指向错误项目（full-stack-fastapi-template）。

**改进后复跑结果**：

| 字段 | Composer 2.5 | Step 3.7 Flash | 实际值 |
|------|:------------:|:--------------:|:------:|
| scan.json file_count | 87 ✅ | 0 ❌ | ~87 |
| scan.json budget_tier | small ✅ | tiny ❌ | small |
| git.json head_short | 346d60f ✅ | null ❌ | 346d60f |
| git.json toplevel | prisma-express-ts ✅ | full-stack-fastapi-template ❌ | prisma-express-ts |

**判定**：
- **Composer 2.5：修复** ✅ — facts 文件内容完全正确，V6 能通过
- **Step 3.7 Flash：未修复** ❌ — facts 文件与改进前完全一样错误。V6 应报 FAIL 但 Runner 自报通过，说明 Script Gate 可能未实际执行

---

### 2.2 P1-B：B6 认证-鉴权字段一致性自检

**原始问题（改进前）**：Step 3.7 Flash 未发现 passport.ts select bug——passport.ts:16-21 只 select `id/email/name`，不含 `role`，但 auth.ts:22 用 `user.role` 做 RBAC 检查，导致 JWT 路径上 `role=undefined`，RBAC 实际失效。Composer 2.5 在改进前**发现了**这个 bug。

**源码确认**（本轮独立核实）：
- `src/config/passport.ts:16-21`：`select: { id: true, email: true, name: true }` — 确实不含 role
- `src/middlewares/auth.ts:22`：`roleRights.get(user.role) ?? []` — 确实用 user.role
- 结论：bug 真实存在，passport select 缺 role 导致 RBAC 失效

**改进后复跑结果**：

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| 【10】节有「认证-鉴权字段一致性自检」小节 | ❌ 无 | ❌ 无 |
| 提到 passport.ts select 缺 role | ❌ 未提 | ❌ 未提 |
| 提到 RBAC 失效风险 | ❌ 未提 | ❌ 未提 |

**判定**：
- **Composer 2.5：退步** ❌ — 改进前发现了 bug，改进后反而不发现了。P1-B 改进项在盲测中未被触发
- **Step 3.7 Flash：未变** ❌ — 改进前后都没发现

**退步原因分析**：P1-B 改进在 L1 回归（go-admin P1 case）中被 Composer 2.5 正确触发，但在盲测中未触发。可能原因：(1) 盲测 prompt 的措辞与 L1 case 不同，模型未按 Phase 3 深度填充流程执行；(2) P1-B 改进写在 `references/phase-3-depth-fill.md` 中，模型可能未读取该参考文件。

---

### 2.3 I1-A：B2 实施文档方法名存在性验证

**原始问题（改进前）**：Step 3.7 Flash 在 B2 实施文档中写了 `userService.updateUserPassword(user.getUserId(), bcryptPassword)`，该方法在代码库中不存在。正确方法是 `userService.resetPwd(SysUser user)` 或 `userService.resetUserPwd(Long userId, String password)`。

**源码确认**（本轮独立核实）：
- `ISysUserService.java:181`：`public int resetPwd(SysUser user)` — 存在
- `ISysUserService.java:190`：`public int resetUserPwd(Long userId, String password)` — 存在
- `SysUserMapper.java:106`：`public int resetUserPwd(...)` — Mapper 层存在
- `updateUserPassword` — grep 全局确认**不存在**

**改进后复跑结果**：

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| 实施文档引用的方法名是否存在 | ✅ 不引用不存在的方法 | ❌ 仍使用 `userService.updateUserPassword()` |
| 有「方法名存在性预检」小节 | ❌ 无显式预检节 | ❌ 无 |
| grep 验证痕迹 | ❌ 无 | ❌ 无 |

**Composer 2.5 详情**：200-实施文档.md 较为简略（31 行），Step 2 提到 `upgradeLegacyPassword` 作为新增方法，引用的 `SecurityUtils.matchesPassword` 和 `Md5Utils.hash` 均存在。未编造方法名，但也未做显式预检。

**Step 3.7 Flash 详情**：implementation.md 第 79 行仍然写 `userService.updateUserPassword(user.getUserId(), bcryptPassword)` — 与改进前完全相同的编造。无方法名预检。

**判定**：
- **Composer 2.5：修复** ✅ — 不再编造方法名（通过避免引用具体已有方法而非通过 grep 预检）
- **Step 3.7 Flash：未修复** ❌ — 仍然编造相同的方法名

---

### 2.4 I2-A：B1 被调方法异常行为确认

**原始问题（改进前）**：Step 3.7 Flash 在 B1 实施代码中对 `SecurityUtils.getLoginUser()` 做 null 检查（`if (loginUser != null)`），但该方法在用户未认证时抛出 `ServiceException`，不返回 null。导致登录接口（无认证用户）的 operlog 不会被记录——恰恰是最核心的使用场景。

**源码确认**（本轮独立核实）：
- `SecurityUtils.java:72-82`：`getLoginUser()` 方法 catch Exception 后 `throw new ServiceException("获取用户信息异常", HttpStatus.UNAUTHORIZED)` — 确认抛异常不返回 null

**改进后复跑结果**：

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| 实施代码是否对 getLoginUser 做 null 检查 | ✅ 不调用 getLoginUser | ❌ 仍做 `if (loginUser != null)` |
| 有「被调方法异常行为确认」小节 | ❌ 无显式确认节 | ❌ 无 |

**Composer 2.5 详情**：200-实施文档.md 使用 Filter 方案（OperLogTimingFilter），不调用 `SecurityUtils.getLoginUser()`，从架构上规避了异常处理问题。但未做显式的异常行为确认。

**Step 3.7 Flash 详情**：implementation.md 第 62-63 行仍然写 `LoginUser loginUser = SecurityUtils.getLoginUser(); if (loginUser != null)` — 与改进前完全相同的逻辑缺陷。

**判定**：
- **Composer 2.5：修复** ✅ — 通过换方案规避了问题（虽非通过 I2-A 预检流程）
- **Step 3.7 Flash：未修复** ❌ — 仍然存在相同的 null 检查逻辑缺陷

---

### 2.5 IP1-A：B3 用户场景覆盖验证

**原始问题（改进前）**：Step 3.7 Flash 在 B3 context-pack 中排除了 `auth.route.ts`，理由是"由 controller 透传"。实际 `auth.controller.ts:8` 只解构 `{ email, password }`，不透传 phone。用户的核心场景"注册时填手机号"需要改 `auth.controller.ts` + `auth.validation.ts`。排除后核心场景无法实现。

**源码确认**（本轮独立核实）：
- `src/controllers/auth.controller.ts:8`：`const { email, password } = req.body` — 确认只解构 email 和 password，**不含 name 也不含 phone**
- `src/controllers/auth.controller.ts:9`：`userService.createUser(email, password)` — 只传 2 个参数
- 注册流程：`POST /v1/auth/register` → `auth.controller.ts:register` → `userService.createUser(email, password)`

**改进后复跑结果**：

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| context-pack 有「用户场景覆盖验证」表 | ❌ 无 | ❌ 无 |
| auth.route.ts 是否排除 | ❌ 排除 | ❌ 排除 |
| auth.controller.ts 是否纳入变更范围 | ❌ 未纳入 | ❌ 未纳入 |
| 排除理由 | "由 controller 透传" | "由 controller 透传" |
| 实施文档修改了注册流程 | ❌ 只改 user.controller.ts | ❌ 只改 user.controller.ts |

**关键发现**：两个 Runner 的 B3 context-pack 内容**几乎完全相同**——同样的排除理由、同样的文件清单、同样的实施步骤。两个 Runner 都只修改了 `user.controller.ts`（管理员创建用户端点 `POST /v1/users`），没有修改 `auth.controller.ts`（注册端点 `POST /v1/auth/register`）。用户的核心场景"注册时填手机号"无法实现。

**判定**：
- **Composer 2.5：未修复** ❌ — IP1-A 改进项未触发，注册流程仍被排除
- **Step 3.7 Flash：未修复** ❌ — 同上

**未生效原因分析**：IP1-A 改进写在 `references/phase-2-context-discovery.md` 中，要求在「暂不纳入范围」节附用户场景覆盖验证表。两个 Runner 都没有添加这个验证表。可能原因：(1) 模型未读取该参考文件；(2) 模型读取了但未执行该步骤。

---

## 三、改进前后对比汇总

### 3.1 定性验证点对比

| 改进 ID | Case | 验证点 | 改进前 Composer | 改进后 Composer | 改进前 Step | 改进后 Step |
|---------|------|--------|:---------------:|:---------------:|:-----------:|:-----------:|
| P1-A | B6 | facts 文件正确 | ✅ 本就正确 | ✅ 正确 | ❌ 全错 | ❌ 全错 |
| P1-B | B6 | 发现 passport bug | ✅ **发现了** | ❌ **退步** | ❌ 未发现 | ❌ 未发现 |
| I1-A | B2 | 不编造方法名 | ✅ 本就正确 | ✅ 正确 | ❌ 编造 | ❌ 仍编造 |
| I2-A | B1 | 正确处理异常 | ⚠️ 方案有缺陷 | ✅ **修复** | ❌ null 检查 | ❌ 仍 null 检查 |
| IP1-A | B3 | 包含注册流程 | ⚠️ 排除了但链断了 | ❌ 仍排除 | ❌ 排除了 | ❌ 仍排除 |

### 3.2 Composer 2.5 改进效果

| 改进 ID | 效果 | 说明 |
|---------|------|------|
| P1-A | ✅ 保持正确 | 改进前后都正确 |
| P1-B | ❌ 退步 | 改进前发现 bug，改进后不发现 |
| I1-A | ✅ 保持正确 | 改进前后都正确 |
| I2-A | ✅ 修复 | 改进前有缺陷，改进后通过换方案修复 |
| IP1-A | ❌ 未修复 | 改进前后都排除注册流程 |

### 3.3 Step 3.7 Flash 改进效果

| 改进 ID | 效果 | 说明 |
|---------|------|------|
| P1-A | ❌ 未修复 | facts 文件与改进前完全相同错误 |
| P1-B | ❌ 未变 | 改进前后都未发现 bug |
| I1-A | ❌ 未修复 | 仍然编造 updateUserPassword |
| I2-A | ❌ 未修复 | 仍然对 getLoginUser 做 null 检查 |
| IP1-A | ❌ 未修复 | 仍然排除注册流程 |

---

## 四、根因分析

### 4.1 为什么 Composer 2.5 的 P1-B 退步了？

P1-B 改进项要求在 pathfinder Phase 3 的【10】权限/认证模型概览节增加「认证-鉴权字段一致性自检」。在 L1 回归测试中（go-admin P1 case），Composer 2.5 正确执行了这个自检。但在盲测中，Composer 2.5 的 B6 地图没有这个自检小节。

**最可能的原因**：盲测中模型可能未严格按照 pathfinder 的 Phase 3 参考文件执行。L1 回归测试使用的是明确的 skill 调用（`/pathfinder`），而盲测 prompt 是自然语言描述任务，模型可能直接生成了地图而没有逐条执行 Phase 3 的深度填充步骤。

### 4.2 为什么 IP1-A 在两个 Runner 上都未生效？

IP1-A 改进项要求在 impact-pro Phase 2 的「暂不纳入范围」节增加用户场景覆盖验证表。在 L1 回归测试中（FastAPI F1 case），Composer 2.5 正确执行了这个验证。但在盲测中，两个 Runner 的 B3 context-pack 都没有这个验证表。

**最可能的原因**：与 P1-B 类似，盲测中模型未严格按 impact-pro 的 Phase 2 参考文件执行。此外，两个 B3 context-pack 内容几乎完全相同，可能存在模型间的产出趋同现象。

### 4.3 为什么 Step 3.7 Flash 零改进？

这与 L1 回归的结论一致：Step 3.7 Flash 疑似未加载改进后的 skill 协议。证据：
- B6 facts 文件与改进前完全相同错误（file_count=0, head_short=null, wrong toplevel）
- B2 仍然编造相同的方法名（updateUserPassword）
- B1 仍然有相同的 null 检查逻辑缺陷
- B3 仍然排除注册流程
- 文档命名混合新旧规范（B1/B2 同时有 040-light.md 和 context-pack.md）

**最可能的原因**：Step 3.7 Flash 可能使用了缓存的旧版 skill 协议，或者模型未正确读取更新后的参考文件。

### 4.4 改进协议的局限性

从本轮复跑可以看出，skill 协议改进的效果取决于模型是否严格执行协议步骤：

1. **在明确调用 skill 的场景（L1 回归）中**，Composer 2.5 能正确执行所有 5 项改进
2. **在自然语言驱动的盲测场景中**，模型可能跳过参考文件中的步骤，导致改进不生效
3. **对于 Step 3.7 Flash**，无论哪种场景，改进都未生效——这不是协议设计问题，而是模型执行能力问题

这意味着：**协议改进的可靠性不仅取决于协议内容是否正确，还取决于模型是否严格按照协议执行**。对于低成本模型，可能需要在 skill 的主入口（SKILL.md）而非参考文件中放置关键检查步骤，以增加模型执行的概率。

---

## 五、结论与建议

### 5.1 总体判定

| 维度 | 结论 |
|------|------|
| 改进是否让 Composer 2.5 变好 | **部分是** — I2-A 修复，P1-A/I1-A 保持正确；但 P1-B 退步，IP1-A 未修复 |
| 改进是否让 Step 3.7 Flash 变好 | **否** — 5 项原始问题全部原样存在 |
| 改进协议本身设计是否正确 | **是** — L1 回归证明 Composer 2.5 能正确执行全部 5 项改进 |
| 改进在盲测场景是否可靠生效 | **部分** — P1-A/I1-A/I2-A 在 Composer 2.5 上生效；P1-B/IP1-A 未生效 |

### 5.2 建议后续行动

1. **P1-B 和 IP1-A 需要提升触发率**：将这两项改进从 `references/` 参考文件提升到 `SKILL.md` 主入口，或者在 skill 流程中增加强制检查点，确保模型在盲测场景也能执行。

2. **Step 3.7 Flash 需要排查协议加载问题**：确认是缓存问题还是模型能力限制。如果是缓存问题，清理缓存后重跑；如果是能力限制，需要在 prompt 中更明确地引导模型执行关键步骤。

3. **P1-B 退步需排查原因**：Composer 2.5 在改进前能发现 passport.ts bug，改进后反而不发现。检查是否 P1-B 改进的加入改变了模型在【10】节的填充行为，导致模型只填写自检表而不做深度分析。建议在 P1-B 自检步骤中明确要求"先逐行读 passport.ts 和 auth.ts 源码，再做字段比对"。

4. **IP1-A 的触发方式需重新设计**：当前写在 context-pack 的「暂不纳入范围」节，但模型在盲测中可能不生成完整的 context-pack。考虑将场景覆盖验证提前到上下文发现阶段的最开始，作为排除文件的前置条件而非事后验证。
