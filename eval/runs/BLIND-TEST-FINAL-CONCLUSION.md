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
