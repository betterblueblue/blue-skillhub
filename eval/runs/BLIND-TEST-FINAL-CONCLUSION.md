# 低成本模型盲测最终结论

> 日期：2026-06-24
> 测试模型：Composer 2.5、Step 3.7 Flash
> 评审模型：Opus 4.8（独立评审，拿源码逐条核实）
> 测试范围：6 个真实开发场景（Java/Go/Node/Python 四个技术栈），覆盖 pathfinder、impact、impact-pro 三个 Skill

---

## 一、结论：能不能日常用？

**能。两个模型都可以作为三个 Skill 的主力模型，但必须带人工复核。**

| 指标 | Composer 2.5 | Step 3.7 Flash |
|------|-------------|----------------|
| 平均分 | 87.0 / 100 | 85.2 / 100 |
| 安全门禁 | 全 PASS | 1 FAIL（B2 编造 API 方法名） |
| 证据编造 | 0 例 | 1 例 |
| 最高分 case | B5 pathfinder 93 分 | B4 impact-pro 92 分 |
| 最低分 case | B1 impact 83 分 | B6 pathfinder 78 分 |
| 可直接 approve | 3/6（B2, B4, B5） | 2/6（B4, B5） |

---

## 二、两个模型各自的画像

### Composer 2.5：深度分析型选手

**强在哪：**
- 能发现跨文件的逻辑 bug。在 prisma-express-ts 项目中发现 passport.ts 的 select 只取了 id/email/name，没取 role，但 auth.ts 用 user.role 做 RBAC 检查——这意味着 RBAC 实际失效。还发现了 userId 旁路漏洞。这两个是真实的安全问题，Step 3.7 Flash 完全没发现。
- 影响面识别更全。在"用户加手机号"的 case 中，Composer 2.5 包含了注册流程（auth.validation + auth.controller），Step 3.7 Flash 错误地排除了。
- 证据不编造。修正 B5 的评审误判后，6 个 case 中 0 例编造。

**弱在哪：**
- 行号精度一般。B4 的 apis 行号偏了 10 行，service 行号偏了 1 行。
- 影响链偶尔断在中间。B3 知道要加 getUserByPhone，但没说在 createUser 里调用它做查重——逻辑链断了。
- 验证脚本质量参差。B2 的 seed SQL 是注释掉的占位符，不能直接运行。

### Step 3.7 Flash：行号精准型选手

**强在哪：**
- 行号精度极高。B1、B2、B4 三个 case 中所有抽检行号全部零偏差，在低成本模型中非常少见。
- 现状核查能力强。3/3 正确，不会盲目相信用户的假设（B2 发现密码已用 BCrypt，纠正了用户的错误前提）。
- B3 实施链比 Composer 2.5 更完整——在 createUser 中明确调用 getUserByPhone 做查重，逻辑链没断。

**弱在哪：**
- 会编造 API 方法名。B2 的实施文档写了 `userService.updateUserPassword(userId, password)`，这个方法在代码库中不存在。正确方法是 `userService.resetPwd(SysUser user)`。
- 深度代码分析弱。B6 没有发现 passport.ts select bug（RBAC 失效）和 userId 旁路。
- facts 文件可能不实。B6 的 scan.json 显示 file_count=0（实际约 74 个文件），git.json 显示 commit=null（实际有 commit），但 Script Gate 5/5 通过了——说明 Script Gate 只检查文件结构不检查内容。
- 实施代码有逻辑缺陷。B1 的 `SecurityUtils.getLoginUser()` 不返回 null 而是抛异常，导致登录接口的 operlog 实际不会被记录——恰恰是最核心的使用场景。

---

## 三、具体怎么用：推荐工作流

### 日常开发场景（非安全敏感）

```
用户提需求 → Skill + 低成本模型出初版 → 人工复核 5-10 分钟 → approve
```

**人工复核必须查的 5 个点：**

| # | 复核项 | 为什么 | 怎么查 |
|---|--------|--------|--------|
| 1 | 实施文档中的 API 方法名是否存在 | Step 3.7 Flash 在 B2 编造了 `updateUserPassword` | grep 方法名，确认在代码库中真实存在 |
| 2 | 影响链是否覆盖用户的核心场景 | Step 3.7 Flash 在 B3 排除了注册流程 | 对照用户原话，确认"注册时填手机号"的入口在哪 |
| 3 | 行号是否准确 | Composer 2.5 在 B4 偏差了 10 行 | 抽查 3-5 条关键行号，打开文件确认 |
| 4 | facts 文件内容是否真实 | Step 3.7 Flash 在 B6 facts 全错但 Gate 通过 | 检查 scan.json 的 file_count 和 git.json 的 commit 是否非空 |
| 5 | 跨文件逻辑一致性 | 两个模型都没在 B6 发现 passport select bug | 重点查认证链路：JWT payload 取了哪些字段，下游用了哪些字段 |

### 安全敏感场景（认证、权限、密码、支付）

```
用户提需求 → Skill + Composer 2.5 出初版 → 人工逐行复核 → approve
```

**为什么安全敏感场景推荐 Composer 2.5：**
- 它在 B6 中发现了两个真实安全漏洞（RBAC 失效 + userId 旁路），Step 3.7 Flash 都没发现。
- 安全敏感场景不能接受编造，Composer 2.5 证据编造 0 例。

**但即使选了 Composer 2.5，仍然必须人工逐行复核。** 两个模型的安全门禁都不够硬——Step 3.7 Flash 编造了方法名，Composer 2.5 的行号有偏差。

---

## 四、模型选择速查

| 你的场景 | 推荐模型 | 复核重点 |
|---------|---------|---------|
| 需要精准行号定位 | Step 3.7 Flash | 行号不用查，查 API 方法名 |
| 需要深度安全分析 | Composer 2.5 | 行号抽查 3-5 条 |
| 跨栈变更分析（impact-pro） | 两者均可 | 影响链是否覆盖核心场景 |
| 日常快速初版 | Step 3.7 Flash | 行号可信度高，减少复核成本 |
| 认证/权限/密码相关 | Composer 2.5 | 逐行复核，重点查跨文件逻辑一致性 |
| 新项目摸底（pathfinder） | 两者均可 | facts 文件内容是否真实 |

---

## 五、和 Opus 基线的差距

| 维度 | Composer 2.5 | Step 3.7 Flash | Opus（L1 基线） |
|------|-------------|----------------|----------------|
| 平均分 | 87.0 | 85.2 | 89-93 |
| 行号精度 | 中等（偏差 1-10 行） | 极高（零偏差） | 高 |
| 影响链完整性 | 中等 | 中等 | 高 |
| 证据编造 | 0 例 | 1 例 | 0 例 |
| 安全门禁 | 全 PASS | 1 FAIL | 全 PASS |
| 深度 bug 发现 | 强 | 弱 | 强 |

**差距约 2-8 分，主要在影响链完整性和深度分析上。安全门禁方面 Composer 2.5 与 Opus 无差距。**

实际使用中，5-10 分钟的人工复核可以补上大部分差距。对于非安全敏感的日常开发，低成本模型 + 人工复核的工作流已经可以替代 Opus。

---

## 六、本次盲测的局限性

1. **只有 6 个 case**：覆盖了 4 个技术栈和 3 个 Skill，但样本量小，不能完全代表两个模型在所有场景下的表现。
2. **评审者只有一个**（Opus 4.8）：虽然拿源码逐条核实，但不同评审者可能得出不同结论。B5 的评审误判就说明了这一点。
3. **只测了两个低成本模型**：市场上还有其他选择，后续可以扩展。
4. **没有测"修改后"的效果**：盲测只测了"分析"阶段，没测"执行修改"阶段。

---

## 评分文件索引

| 文件 | 说明 |
|------|------|
| `eval/runs/blind-2026-06-24-composer25/_summary.md` | Composer 2.5 评审总报告 |
| `eval/runs/blind-2026-06-24-composer25/B*.scorecard.json` | Composer 2.5 逐 case 评分卡 |
| `eval/runs/blind-2026-06-24-step37flash/_summary.md` | Step 3.7 Flash 评审总报告 |
| `eval/runs/blind-2026-06-24-step37flash/B*.scorecard.json` | Step 3.7 Flash 逐 case 评分卡 |
| `eval/cases/blind/JUDGE-RUBRIC.md` | 盲测评审标准 |

---

## 七、协议改进后的更新（v3，2026-06-24）

> 本节为协议改进后的补充结论。上述一至六节基于 v1 盲测（Opus 4.8 评审），本节基于 v2/v3 复跑（GLM-5.2 评审）。
> 完整改进过程见 `docs/skill-improvement-2026-06-24.md`。

### 7.1 协议改进做了什么

基于 v1 盲测暴露的 5 个问题，在三个 Skill 的协议中增加了 5 项检查步骤：

| 改进 ID | Skill | 解决的问题 |
|---------|-------|-----------|
| P1-A | pathfinder | Script Gate 不验证 facts 文件内容（file_count=0 但 Gate 通过） |
| P1-B | pathfinder | 漏发现跨文件安全 bug（passport select 缺 role 致 RBAC 失效） |
| I1-A | impact | 实施文档编造不存在的 API 方法名（updateUserPassword） |
| I2-A | impact | 实施代码对抛异常的方法做 null 检查（getLoginUser 死代码） |
| IP1-A | impact-pro | 排除文件时不验证用户核心场景是否被覆盖（排除注册流程） |

v2 复跑发现这些改进放在 `references/` 参考文件中时，盲测场景下不被模型读取。v3 将 P1-B、IP1-A 提升到 SKILL.md 主入口，并为 Step 3.7 Flash 的 prompt 加入"强制 Read SKILL.md"步骤。

### 7.2 v3 最新结果

| 指标 | Composer 2.5 v3 | Step 3.7 Flash v3 |
|------|:---------------:|:-----------------:|
| 改进项通过数 | **5/5 全通过** | 3/5 修复 + 1/5 部分改善 + 1/5 仍 FAIL |
| 平均分 | 95.3 | 85.5 |
| would_approve yes | 4/4 | 2/4 |
| 证据编造 | 0 例 | 0 例 |

**Composer 2.5**：v1 的 87.0 → v3 的 95.3，5 项改进全部通过，可作为生产级 Runner。v1 中发现的跨文件安全 bug 能力保持（P1-B 退步后修复），影响面识别更全（IP1-A 修复，包含注册流程）。

**Step 3.7 Flash**：v1/v2 的 0/5 改进 → v3 的 3/5 修复。"强制 Read SKILL.md"步骤确认了 v2 失败根因是协议未加载。B2（I1-A 不再编造方法名）、B3（IP1-A 包含注册流程）产出质量接近 Composer 2.5。剩余两项：P1-A 仍未产出 facts 文件；I2-A 因判档偏松（light）绕过了实施代码编写。

### 7.3 更新后的模型画像

#### Composer 2.5：协议改进后全面达标

v1 时的短板在 v3 中已修复：
- 影响链不再断在中间（B3 的 createUser 中明确调用 getUserByPhone 查重）
- P1-B 退步修复，重新发现 passport select bug
- IP1-A 修复，完整纳入注册流程
- 实施文档有显式的「方法存在性预检」节

#### Step 3.7 Flash：协议加载问题解决，剩余两项待优化

v1/v2 时"疑似未加载改进后协议"的问题在 v3 中通过"强制 Read SKILL.md"解决：
- I1-A 修复：不再编造 updateUserPassword，有完整双表格预检（方法存在性 + 异常行为）
- IP1-A 修复：从需求→设计→实施三阶段完整覆盖注册流程
- P1-B 修复：地图【10】节有完整 4 步认证-鉴权字段一致性自检
- 行号精度高的优势保持

剩余两项：
- P1-A：读了 SKILL.md 但未运行 Script Gate 产出 facts 文件，需进一步强化脚本执行的强制性
- I2-A：判档偏松（用户说"每次接口请求"，LogAspect 仅覆盖 @Log 注解接口，应 full），因定级 light 无实施代码而技术规避了 null 检查缺陷，但未执行 I2-A 预检

### 7.4 更新后的推荐工作流

协议改进后，人工复核的 5 个点中第 1、2、5 项已被协议内置检查覆盖（Composer 2.5 全通过，Step 3.7 Flash 3/5 修复），复核负担下降：

| # | 复核项 | v1 时谁会出问题 | v3 后状态 |
|---|--------|----------------|----------|
| 1 | API 方法名是否存在 | Step 3.7 Flash（I1-A） | 协议内置预检，v3 双模型均通过 |
| 2 | 影响链是否覆盖核心场景 | Step 3.7 Flash（IP1-A） | 协议内置场景覆盖验证，v3 双模型均通过 |
| 3 | 行号是否准确 | Composer 2.5 | 仍需抽查（协议未覆盖） |
| 4 | facts 文件内容是否真实 | Step 3.7 Flash（P1-A） | Step 3.7 Flash v3 仍 FAIL，Composer 通过 |
| 5 | 跨文件逻辑一致性 | 两个模型（P1-B） | 协议内置自检，v3 双模型均通过 |

**更新后的结论**：Composer 2.5 v3 可作为生产级 Runner（5/5 全通过），日常开发场景人工复核可压缩到 3-5 分钟（重点查行号）。Step 3.7 Flash v3 适合非 pathfinder 场景（B2/B3 质量接近 Composer 2.5），pathfinder 场景仍需人工补查 facts 文件。

### 7.5 v3 评分文件索引

| 文件 | 说明 |
|------|------|
| `eval/runs/blind-2026-06-24-v3-composer25/summary.md` | Composer 2.5 v3 评审总报告 |
| `eval/runs/blind-2026-06-24-v3-composer25/B*.scorecard.json` | Composer 2.5 v3 逐 case 评分卡 |
| `eval/runs/blind-2026-06-24-v3-step37flash/summary.md` | Step 3.7 Flash v3 评审总报告 |
| `eval/runs/blind-2026-06-24-v3-step37flash/B*.scorecard.json` | Step 3.7 Flash v3 逐 case 评分卡 |
