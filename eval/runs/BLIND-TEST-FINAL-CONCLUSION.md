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
> 完整改进过程见 `docs/archive/2026-06/skill-improvement-2026-06-24.md`。

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

---

## 八、v3 后续优化验证（v4，2026-06-25）

> 本节验证 v3 后实施的优化 6-8 是否生效。v4 评审方式为源码级核实（读取实际产出文件逐项核对，非仅凭模型自报）。
> 完整 v4 设计见 `eval/cases/blind/BLIND-TEST-V4-DESIGN.md`。

### 8.0 v4 环境隔离修正（重要）

v4 初版在污染环境下执行（多个模型的产出堆积在同一个 `change-impact/` 目录），导致三个问题：
1. `pf_scan.py` 把残留文件计入项目文件数（file_count 虚高 106 而非 65）
2. `pf_validate.py` V6 因旧 facts 残留假 PASS
3. 后跑的模型能读到先跑模型的产出，破坏测试独立性

修正方案（三项联动）：
- `pf_scan.py` 的 `SKIP_DIRS` 永久加入 `change-impact`
- 每个 prompt 新增 Step 0：跑前清理 `change-impact/`
- 改用默认输出路径，跑完后统一归档到模型子目录

**关键影响**：v4 初版中 Step 3.7 Flash 的 I2-A "修复"结论不可信——它在污染环境下可能读到了 Composer 的 full 分析才判了 full。干净环境重跑后 I2-A 仍未修复（见 8.2）。

### 8.1 v3 后续做了什么（优化 6-8）

v3 盲测跑完后，针对 Step 3.7 Flash 剩余 2 项失败（P1-A、I2-A）和两模型共有的需求文档技术细节渗入问题，又做了 3 项优化：

| 优化 | 改哪里 | 解决的问题 |
|------|--------|-----------|
| 优化 6（P1-A 加固） | `pf_validate.py` + `pathfinder/SKILL.md` | v3 中 Step 跳过 Phase 1.5 不产出 facts，Script Gate 仍放行（V6 当时是 WARN） |
| 优化 7（I2-A 新增） | `impact/SKILL.md` Phase 2.5 + `impact-pro/SKILL.md` Phase 2.5 | v3 中 Step 把"每次接口请求"误判 light（LogAspect 只覆盖 @Log 注解接口） |
| 优化 8（需求文档边界） | `impact/SKILL.md` Phase 4 + `impact-pro/SKILL.md` Phase 4 | v3 中两模型的 `010-requirements.md` 都混入了表名、类名、文件路径、代码片段 |

### 8.2 v4 结果（干净环境）

| 指标 | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|------|:------------:|:--------------:|:-----------------:|
| 优化 6（P1-A） | ✅ PASS | ✅ **PASS**（v3 FAIL→修复） | ✅ PASS |
| 优化 7（I2-A） | ✅ PASS | ❌ **FAIL**（v3 FAIL→仍未修复） | ❌ FAIL |
| 优化 8（需求文档） | ⚠️ 2/3 PASS（B2 残留 1 处表名） | ✅ PASS（B3） | N/A（未产出需求文档） |
| v3 五项回归 | 5/5 不退步 | 4/5（I1-A 轻微退步） | — |
| 评审方式 | 源码级核实 | 源码级核实 | 源码级核实 |

**Composer 2.5**：优化 6、7 保持 v3 修复状态。优化 8 在 B1/B3 完全干净，B2 残留 1 处 `sys_user` 表名（在依赖关系节，非需求主体）。5 项改进全部不退步。16 个产出文件，文档结构完整。

**Step 3.7 Flash**：
- **P1-A 修复**：v3 未产出 facts → v4 干净环境产出 scan.json（file_count=65）+ git.json（head=346d60f），内容真实。优化 6 生效。
- **I2-A 仍未修复**：v4 初版（污染环境）中看似修复了（判 full），但干净环境重跑后仍然判 **light**——light.md 直接说"功能已完整实现，无需改动"，连覆盖缺口都没识别到。**v4 初版的"修复"是污染环境下读到 Composer 产出导致的假阳性。**
- 优化 8 PASS：B3 的 `010-requirements.md` 纯业务语言。
- I1-A 轻微退步：B2 判 light，未做方法名 grep 验证（v3 有）。

**DeepSeek-V4-Flash**（首次参与盲测）：
- B6（pathfinder）表现优秀：facts 产出正确、认证-鉴权自检完整、主流程链路追踪到位。
- B1（impact）优化 7 FAIL：识别到了覆盖缺口（写了"约 63 个端点未覆盖"），但仍然判 light。
- B2（impact）判 light，认为"无需迁移"。
- B3（impact-pro）产出严重不足：只有 1 个混合内容的 context-pack，没有独立的 010/020/030 文档。

### 8.3 最终定版结论

**v3.8 协议优化部分成功，模型能力差异显著：**

| 模型 | v1 | v3 | v4（干净环境） | 定版状态 |
|------|:--:|:--:|:--:|---------|
| Composer 2.5 | 87.0（5 项问题） | 95.3（5/5 修复） | 3/3 优化 + 5/5 不退步 | **生产级 Runner** |
| Step 3.7 Flash | 85.2（5 项问题） | 85.5（3/5 修复） | 2/3 优化 + 4/5 回归 | **Runner（有限场景）** |
| DeepSeek-V4-Flash | — | — | 1/3 优化 + P1-B PASS | **Pathfinder Runner** |

**关键结论修正**：

1. **优化 6（P1-A facts 强制）**：✅ 对所有模型生效。Step 3.7 Flash 从 v3 的 FAIL 修复为 PASS，这是真实的——干净环境下确实产出了 facts。

2. **优化 7（I2-A 覆盖范围核查）**：❌ 对 Step 3.7 Flash 和 DeepSeek 均不生效。两个模型都识别到了覆盖缺口（DeepSeek 甚至量化了"约 63 个端点未覆盖"），但都没有因此触发 full。这说明优化 7 的规则对这些模型来说还不够强——它们能"看到"缺口，但不会把缺口和全量词关联起来改变判档。只有 Composer 2.5 能做到。

3. **优化 8（需求文档边界）**：✅ 对 Composer 和 Step 生效（B3 需求文档干净），但 DeepSeek 未产出标准需求文档无法验证。

**人工复核负担最终状态**：

| # | 复核项 | v1 时 | v4 后 |
|---|--------|-------|-------|
| 1 | API 方法名是否存在 | Step 会编造 | 协议内置预检，Composer 通过；Step 轻微退步（B2 判 light 未做 grep） |
| 2 | 影响链是否覆盖核心场景 | Step 会排除 | 协议内置验证，Composer 通过；Step/DeepSeek 仍可能在覆盖范围判断上出错 |
| 3 | 行号是否准确 | Composer 有偏差 | 仍需抽查（协议未覆盖） |
| 4 | facts 文件内容是否真实 | Step 全错 | 协议内置强制 + Gate 拦截，三模型均通过 |
| 5 | 跨文件逻辑一致性 | 两模型都漏 | 协议内置自检，三模型均通过 |
| 6 | 需求文档是否渗入技术细节 | 两模型都有 | 协议内置自检，Composer/Step 通过 |
| 7 | **判档是否正确**（新增） | — | **Step/DeepSeek 在覆盖范围场景仍可能误判 light，需人工复核** |

**新增第 7 项**是 v4 干净环境暴露的问题：优化 7 对弱模型不生效，判档正确性无法靠协议保证，只能靠人工复核或换更强的模型。

### 8.4 模型选型建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| pathfinder 摸底 | 三者均可 | 都能正确产出 facts + 认证-鉴权自检 |
| impact 涉及覆盖范围判断 | **仅 Composer 2.5** | Step/DeepSeek 会误判 light |
| impact 不涉及覆盖范围 | Composer 2.5 或 Step 3.7 Flash | Step 的 B2/B3 质量合格 |
| impact-pro 简单场景 | Composer 2.5 或 Step 3.7 Flash | Step 的 B3 设计文档质量高 |
| impact-pro 复杂场景 | **仅 Composer 2.5** | DeepSeek 产出不完整；Step 缺 context-pack/preflight |
| 安全敏感场景 | **仅 Composer 2.5** | 证据编造 0 例 + 跨文件分析最强 |

### 8.5 v4 评审文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/BLIND-TEST-V4-DESIGN.md` | v4 测试设计文档（含环境隔离修正记录） |
| `eval/cases/blind/PROMPT-composer25-v4.md` | Composer 2.5 v4 一键执行 prompt（含 Step 0 清理 + 归档） |
| `eval/cases/blind/PROMPT-step37flash-v4.md` | Step 3.7 Flash v4 一键执行 prompt（同上） |
| `eval/cases/blind/PROMPT-deepseek-v4-flash-v4.md` | DeepSeek-V4-Flash v4 一键执行 prompt（同上） |
| `eval/scripts/clean-before-run.sh` | 测试前清理脚本 |
| `eval/runs/blind-2026-06-24-v4-composer25/summary-clean-env.md` | Composer 2.5 v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-step37flash/summary-clean-env.md` | Step 3.7 Flash v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-deepseek-v4-flash/summary.md` | DeepSeek-V4-Flash v4 评审 |
| `skills/pathfinder/scripts/pf_scan.py` | 项目扫描器（v4 修正：SKIP_DIRS 加入 change-impact） |

---

## 九、V5-V7：模型横向对比与 Skill 增益验证

> 本节覆盖 V5（"已实现"场景）、V6（真正变更场景）、V7（模糊需求场景）三轮盲测。
> 测试矩阵：3 模型（GLM-5.2 / Composer 2.5 / Step 3.7 Flash）× 2 条件（skill / noskill）× 3 场景。
> 评审方式：源码锚点核实。

### 9.1 V5 — "已实现"场景验证（5 cell × 4 case = 20 份产出）

**核心发现**：四个 case（B1 操作日志、B2 密码 BCrypt、B3 手机号字段、B6 pathfinder 摸底）在代码库中**全部已实现**。所有 5 个 cell 都正确发现了这一点，没有盲目提方案。

| 模型 | 条件 | 均分 | 安全门禁 |
|------|------|:----:|:--------:|
| Opus 4.6 | noskill | 85.5 | PASS |
| Composer 2.5 | noskill | **89.0** | PASS |
| Composer 2.5 | skill | 83.8 | PASS |
| GLM-5.2 | noskill | 85.5 | PASS |
| GLM-5.2 | skill | **88.0** | PASS |

**Skill 增益分化**：
- GLM：+10 分（pathfinder 场景 +15，模板结构化帮助大）
- Composer：**-21 分**（"已实现"场景选了 full 档提出不必要方案，过度设计）

**结论**：当功能已存在时，skill 模板可能引导模型走 full 流程提出不必要方案。无 skill 组凭直觉判断"不需要改"反而更准确。这直接催生了"现状核查优先"规则。

### 9.2 V6 — 真正变更场景验证（6 cell × 3 case = 18 份产出）

三个场景均为"未实现"或"部分实现"：B1' 并发登录限制（Full）、B2' 请求体大小限制（Light）、B3' 邮箱验证强制检查（Full）。

| 模型 | noskill 均分 | skill 均分 | 增益 | 判定 |
|------|:---:|:---:|:---:|------|
| GLM-5.2 | 87 | 89 | +2 | 微正向 |
| Composer 2.5 | 87 | 89 | +2 | 微正向 |
| Step 3.7 Flash | 77 | **69** | **-8** | **负向** |

**关键发现**：
1. Skill 对 GLM 和 Composer 有微正向增益（结构化、证据标签、档位判定）。
2. **Skill 对 Step 3.7 Flash 产生负向效果**——模型能力不足以正确执行 skill 流程，反而被流程引导出更多错误（B2' 判档 Full 应为 Light、B3' 遗漏 passport.ts select 修改导致所有用户被 403 拦截、回滚方案出现 Java 项目幻觉）。
3. 现状核查门禁在 GLM/Composer 上完全生效，在 Step 上部分失效。

### 9.3 V7 — 模糊需求场景验证（6 cell × 3 case = 18 份产出）

使用口语化模糊 prompt 测试 skill 的澄清能力。

| 指标 | V6（精确 prompt） | V7（模糊 prompt） |
|------|:---:|:---:|
| Skill 平均增益 | +2 分 | **+12.1 分** |
| noskill 平均分 | 75.2 | 63.8 |
| skill 平均分 | 77.2 | 75.9 |
| 增益来源 | 结构化 | **假设标注 + 结构化 + 防御性检查** |

**核心结论**：模糊 prompt 拉低了 noskill 组 11.4 分，但对 skill 组仅拉低 1.3 分。**Skill 的核心价值在于"处理模糊需求"而非"结构化精确需求"。** 所有 skill 组都标注了 `[假设]`，所有 noskill 组都没有。

**副作用发现**：
- Light 模式可能跳过深入检查（GLM skill 在 B2' 遗漏了 errorConverter 413→500 问题）
- 弱模型在 skill 流程中"过早收敛"（Step skill 在 B2'/B3' 只做了 1 个 Step，遗漏大量关键改动）

### 9.4 V5-V7 综合结论

| 问题 | 结论 |
|------|------|
| Skill 的核心价值是什么？ | **澄清模糊需求**（假设标注 + 防御性检查），而非结构化精确需求 |
| Skill 增益是否稳定？ | 不完全稳定，因模型能力和需求模糊度而异（+2 ~ +12.1） |
| Skill 有副作用吗？ | 有：light 模式跳过深入检查；弱模型"过早收敛"；"已实现"场景过度设计 |
| 哪些模型适合用 skill？ | GLM-5.2 和 Composer 2.5 适合；Step 3.7 Flash 在 V6 中 skill 反而拉低 8 分 |

---

## 十、V8-V10：协议迭代验证（v3.9 → v4.0 → v4.1）

> 本节验证针对 V7 发现的问题所做的三轮协议改进是否生效。
> 测试模型：Composer 2.5（单模型回归验证）。

### 10.1 v3.9 改进回归（V8）

V7 发现 4 个问题 → v3.9 增加 4 项改进：

| 改进 | 解决的问题 | V8 验证 |
|------|-----------|---------|
| F1 模糊点处理清单 | noskill 组不标注假设 | ✅ 2/2 |
| F2 改动完整性自检 | Step "过早收敛"遗漏 Step | ✅ 2/2 无缺失 |
| F3 关键链路追踪 | 分析深度不足 | ✅ 2/2，3 条链路/case |
| F4 light 深度检查 | light 模式跳过关键分析 | ✅ 1/1 |

**V7 遗漏项捕获率：5/5**（目标 ≥3/5）。V7 中 Composer skill 遗漏的 5 个关键问题（refreshToken TTL、Express 默认 100kb、XSS 内存放大、passport.ts select、refreshAuth 检查）全部被 v3.9 改进捕获。

| 指标 | V7 | V8 | 变化 |
|------|:--:|:--:|:----:|
| skill 均分 | 83.7 | **88.0** | +4.3 |
| D3 分析深度 | 16.3 | **18.3** | +2.0 |
| skill 增益 | +12.7 | **+14.3** | +1.6 |
| 无维度回退 | — | ✅ | 最大回退 0 |

### 10.2 v4.0 人工交互 + 配置化（V9）

V8 中 8 项 `[假设]` 都是 agent 自问自答 → V9 引入人工交互，全部转为用户确认。

| 指标 | V8 | V9 | 变化 |
|------|:--:|:--:|:----:|
| skill 均分 | 88.0 | **92.0** | +4.0 |
| D5 需求澄清质量 | 13.3 | **15.0** | +1.7 |
| [假设]→用户确认转化率 | 0% | **100%** | — |
| skill 优势 | +14.3 | **+18.3** | +4.0 |

v4.0 新增两项改进（配置依赖链路追踪 F5、light 配置化提示 F6）均生效。

### 10.3 v4.1 多轮触发 + 链路追踪回流（V10）

V9 只问 1 轮 3 题就停止 → v4.1 增加多轮触发条件，链路追踪发现的副作用风险回流 Phase 3 追问。

| 指标 | V9 | V10 | 变化 |
|------|:--:|:--:|:----:|
| 提问轮数 | 1 | **2** | +1 |
| 提问总数 | 3 | **5** | +2 |
| 实施 Step 数 | 6 | **7** | +1（+限流） |
| B3' 总分 | 92 | **96** | +4 |
| skill 优势 | +18.3 | **+22.3** | +4.0 |

v4.1 让 agent 不再止步于"3 题就够了"，链路追踪发现的"公开重发接口可被无限调用"风险被带回 Phase 3 确认，并转化为具体的限流设计。

### 10.4 V8-V10 综合结论

协议从 v3.9 到 v4.1 的三轮迭代验证了：**结构性改进可以持续提升分析质量，且不引入回退。** skill 相对 noskill 的优势从 +12.7 分（V7）扩大到 +22.3 分（V10，B3' 单 case）。

---

## 十一、Phase 5 执行阶段盲测（E1-E4）

> 测试模型：Composer 2.5 | Skill 版本：v4.1 | 评审模型：GLM-5.2

| Case | Skill | 技术栈 | 档位 | 分数 | P0 | P1 |
|------|-------|--------|:----:|:----:|:--:|:--:|
| E1 | impact-pro | Node/Express/Prisma | full | 84 | 0 | 1 |
| E2 | impact-pro | Python/FastAPI/SQLModel | full | 83 | 0 | 1 |
| E3 | impact | Java/Spring/MyBatis | **light** | 93 | 0 | 0 |
| E4 | impact-pro | 静态前端（无构建系统） | light | **98** | 0 | 0 |
| **合计** | | | | **89.5** | **0** | **2** |

**红线检查**：无 P0 命中。2 个 P1：E1 Prisma schema 编辑未标高风险（等同 ALTER TABLE）；E2 连续 3 个 V1-only 写入未暂停。E4 补测验证了 V1-only 计数机制在改进后正确生效。

**关键发现**：
1. 安全层全绿——每个写操作都有确认，V 等级诚实报告，实际修改了源代码。
2. E3 的 light 降级是正面表现——模型正确发现 `SysDept.email` 已存在，降级为 UI-only 变更。
3. 高风险拦截有灰色地带——ORM schema 编辑是否等同 ALTER TABLE 需要协议明确。

---

## 十二、B7-B9：破坏性变更与新技术栈首测

> 测试模型：Composer 2.5 | Skill：impact-pro | Rubric 专项评审

| Case | 项目 | 需求 | 变更类型 | 合计/80 | P0 |
|------|------|------|---------|:-------:|:--:|
| B7 | go-admin（Go/Gin/GORM） | 用户加微信号 | 新增字段 | **71** | 0 |
| B8 | prisma-express-ts（Node） | name→fullName 重命名 | 破坏性重命名 | **71** | 0 |
| B9 | ruoyi-vue（Java/Spring） | 删掉用户备注字段 | 删字段 | **68** | 0 |
| **平均** | | | | **70（87.5%）** | **0** |

**核心验证目标——破坏性变更保护流程 100% 触发**：
- B8/B9 都执行了"只读搜索引用 → 回显破坏面 → 追问决策"的完整流程
- B8 的 name 消费者扫描覆盖 11 个文件 + 行号，正确排除非 User 字段的 name 引用
- B9 正确识别 BaseEntity 是共享基类，选择不 DROP COLUMN 规避风险

**新技术栈首测——Go/Gin/GORM 通过**：
- GORM struct tag 修改被正确识别为高风险（等同 ALTER TABLE）
- 三处 model 定义同步修改，DTO 自动透传

**修复记录**：
- B9 SysUser.java toString() 遗漏已修复（删除 `.append("remark", getRemark())`，mvn compile 通过）
- B8 干净重跑已消除预存变更污染（git diff 11 文件 34 行，无无关变更）

---

## 十三、综合结论与最终选型建议

### 13.1 全景数据汇总

| 轮次 | 测试维度 | 模型 | skill 均分 | noskill 均分 | 增益 |
|------|---------|------|:---:|:---:|:---:|
| v1-v4 | 基础分析能力 | Composer 2.5 | 95.3(v3) | 87.0(v1) | +8.3 |
| v1-v4 | 基础分析能力 | Step 3.7 Flash | 85.5(v3) | 85.2(v1) | +0.3 |
| V5 | "已实现"场景 | Composer 2.5 | 83.8 | 89.0 | **-5.2** |
| V5 | "已实现"场景 | GLM-5.2 | 88.0 | 85.5 | +2.5 |
| V6 | 精确需求变更 | GLM/Composer 均值 | 89.0 | 87.0 | +2.0 |
| V6 | 精确需求变更 | Step 3.7 Flash | 69.0 | 77.0 | **-8.0** |
| V7 | 模糊需求变更 | 三模型均值 | 75.9 | 63.8 | **+12.1** |
| V8 | v3.9 改进回归 | Composer 2.5 | 88.0 | 73.7 | +14.3 |
| V9 | 人工交互 + v4.0 | Composer 2.5 | 92.0 | 73.7 | +18.3 |
| V10 | v4.1 多轮触发 | Composer 2.5 (B3') | 96.0 | 73.7 | +22.3 |
| E1-E4 | Phase 5 执行 | Composer 2.5 | 89.5 | — | — |
| B7-B9 | 破坏性变更 | Composer 2.5 | 87.5% | — | — |

### 13.2 最终模型选型建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| pathfinder 摸底 | 三者均可（含 DeepSeek） | 都能正确产出 facts + 认证-鉴权自检 |
| impact 涉及覆盖范围判断 | **仅 Composer 2.5** | Step/DeepSeek 会误判 light |
| 模糊需求场景 | **Composer 2.5 + skill** | 假设标注能力最强（5 项/case） |
| 破坏性变更 | **Composer 2.5 + skill** | 破坏性变更保护流程 100% 触发 |
| 安全敏感场景 | **仅 Composer 2.5** | 证据编造 0 例 + 跨文件分析最强 |
| 新技术栈（Go/Python） | **Composer 2.5 + skill** | profile 探测正确，GORM/Alembic 高风险识别到位 |
| 日常快速初版 | GLM-5.2 或 Step 3.7 Flash（noskill） | noskill 表现不差，减少 skill 开销 |

### 13.3 Skill 价值最终判定

| 问题 | 结论 |
|------|------|
| Skill 值得用吗？ | **值得**。模糊需求场景增益 +12.1，v4.1 后达到 +22.3 |
| Skill 的核心价值是什么？ | 澄清模糊需求（假设标注 + 多轮追问 + 链路追踪副作用回流） |
| Skill 有副作用吗？ | 有但可控：v3.9-v4.1 已修复 light 深度不足、过早收敛、过度设计三个问题 |
| 哪些模型不适合用 skill？ | Step 3.7 Flash 在精确需求场景 skill 反降 8 分（V6） |
| 人工交互有必要吗？ | **有**。V9 证明人工交互比自问自答再提升 4 分，用户回答触发更精确的设计 |

### 13.4 人工复核负担最终状态

| # | 复核项 | v1 时 | v4.1 后 |
|---|--------|-------|---------|
| 1 | API 方法名是否存在 | Step 会编造 | 协议内置预检，Composer 通过 |
| 2 | 影响链是否覆盖核心场景 | Step 会排除 | 协议内置场景覆盖验证 |
| 3 | 行号是否准确 | Composer 有偏差 | 仍需抽查（协议未覆盖） |
| 4 | facts 文件内容是否真实 | Step 全错 | 协议内置强制 + Gate 拦截 |
| 5 | 跨文件逻辑一致性 | 两模型都漏 | 协议内置自检（链路追踪） |
| 6 | 需求文档渗入技术细节 | 两模型都有 | 协议内置自检 |
| 7 | 判档是否正确 | — | Step/DeepSeek 仍可能误判 light |
| 8 | 破坏性变更引用扫描 | — | 协议内置保护流程（B7-B9 验证） |
| 9 | 链路追踪副作用 | — | 协议内置多轮触发 + 回流（V10 验证） |

**Composer 2.5 + v4.1 skill 的人工复核可压缩到 3-5 分钟**（重点查行号精度和判档合理性）。

### 13.5 评审文件索引（V5-V10 + E1-E4 + B7-B9）

| 文件 | 说明 |
|------|------|
| `eval/runs/blind-2026-06-25-v5/scorecards/_v5-review-report.md` | V5 "已实现"场景评审 |
| `eval/runs/blind-2026-06-25-v6/scorecards/_v6-review-report.md` | V6 精确需求变更评审 |
| `eval/runs/blind-2026-06-25-v7/scorecards/_v7-review-report.md` | V7 模糊需求评审 |
| `eval/runs/blind-2026-06-25-v8/scorecards/_v8-review-report.md` | V8 v3.9 改进回归评审 |
| `eval/runs/blind-2026-06-25-v9/scorecards/_v9-review-report.md` | V9 人工交互 + v4.0 评审 |
| `eval/runs/blind-2026-06-25-v10/scorecards/_v10-review-report.md` | V10 v4.1 多轮触发评审 |
| `eval/runs/phase5-blind-2026-06-25/PHASE5-BLIND-TEST-SUMMARY.md` | E1-E4 Phase 5 执行评审 |
| `eval/runs/blind-b7-b9-2026-06-25/cell-C1/SCORECARD.md` | B7-B9 破坏性变更评审 |
| `eval/cases/blind-b7-b9/BLIND-TEST-DESIGN-B7-B9.md` | B7-B9 测试设计 |
| `eval/cases/blind-b7-b9/JUDGE-RUBRIC-B7-B9.md` | B7-B9 评审标准 |
