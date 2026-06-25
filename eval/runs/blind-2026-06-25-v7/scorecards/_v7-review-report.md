# V7 盲测评审报告 — 模糊需求下的 Skill 增益验证

> 评审日期：2026-06-25
> 评审范围：6 cell × 3 case = 18 份产出
> 核心问题：模糊 prompt 下，skill 的澄清与假设能力是否产生显著增益？

---

## 一、结论摘要

| 指标 | V6（精确 prompt） | V7（模糊 prompt） |
|------|:---:|:---:|
| Skill 平均增益 | **+2 分** | **+12.1 分** |
| noskill 平均分 | 75.2 | 63.8 |
| skill 平均分 | 77.2 | 75.9 |
| 增益主要来源 | 结构化 | **假设标注 + 结构化 + 防御性检查** |

**结论：V7 验证了核心假设——模糊 prompt 下 skill 增益显著提升（从 +2 到 +12.1）。** skill 的核心价值确实在于"澄清模糊需求"而非"结构化精确需求"。

但增益分布不均匀，存在三个关键发现（详见第四节）。

---

## 二、评分总表

### 2.1 B1' 并发登录限制（RuoYi-Vue）

| 维度 | 满分 | C1 GLM noskill | C2 GLM skill | C3 Composer noskill | C4 Composer skill | C5 Step noskill | C6 Step skill |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D1 上下文发现 | 20 | 18 | 19 | 18 | 18 | 12 | 16 |
| D2 证据真实性 | 15 | 10 | 13 | 12 | 12 | 8 | 12 |
| D3 分析深度 | 20 | 16 | 18 | 16 | 16 | 12 | 14 |
| D4 判档准确性 | 10 | 7 | 8 | 8 | 8 | 5 | 7 |
| D5 假设质量 | 15 | 0 | 12 | 0 | 13 | 0 | 10 |
| D6 文档质量 | 10 | 8 | 9 | 8 | 8 | 6 | 8 |
| D7 协议/自发 | 10 | 8 | 9 | 8 | 9 | 6 | 8 |
| **小计** | **100** | **67** | **88** | **70** | **84** | **49** | **75** |
| **Skill 增益** | | — | **+21** | — | **+14** | — | **+26** |

### 2.2 B2' 请求体大小限制（Prisma-Express-TS）

| 维度 | 满分 | C1 GLM noskill | C2 GLM skill | C3 Composer noskill | C4 Composer skill | C5 Step noskill | C6 Step skill |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D1 上下文发现 | 20 | 19 | 16 | 18 | 17 | 14 | 14 |
| D2 证据真实性 | 15 | 12 | 12 | 12 | 12 | 10 | 10 |
| D3 分析深度 | 20 | 19 | 14 | 17 | 17 | 12 | 8 |
| D4 判档准确性 | 10 | 7 | 9 | 9 | 7 | 5 | 5 |
| D5 假设质量 | 15 | 0 | 12 | 0 | 13 | 0 | 8 |
| D6 文档质量 | 10 | 8 | 8 | 8 | 8 | 6 | 6 |
| D7 协议/自发 | 10 | 9 | 9 | 8 | 9 | 6 | 6 |
| **小计** | **100** | **74** | **80** | **72** | **83** | **53** | **57** |
| **Skill 增益** | | — | **+6** | — | **+11** | — | **+4** |

### 2.3 B3' 邮箱验证强制检查（Prisma-Express-TS）

| 维度 | 满分 | C1 GLM noskill | C2 GLM skill | C3 Composer noskill | C4 Composer skill | C5 Step noskill | C6 Step skill |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D1 上下文发现 | 20 | 19 | 18 | 18 | 18 | 12 | 8 |
| D2 证据真实性 | 15 | 12 | 14 | 12 | 12 | 8 | 10 |
| D3 分析深度 | 20 | 19 | 17 | 17 | 16 | 8 | 6 |
| D4 判档准确性 | 10 | 7 | 8 | 8 | 8 | 5 | 5 |
| D5 假设质量 | 15 | 0 | 10 | 0 | 13 | 0 | 8 |
| D6 文档质量 | 10 | 8 | 9 | 8 | 8 | 6 | 5 |
| D7 协议/自发 | 10 | 9 | 9 | 8 | 9 | 5 | 5 |
| **小计** | **100** | **74** | **85** | **71** | **84** | **44** | **47** |
| **Skill 增益** | | — | **+11** | — | **+13** | — | **+3** |

### 2.4 模型维度汇总

| 模型 | noskill 均分 | skill 均分 | 增益 |
|------|:---:|:---:|:---:|
| GLM-5.2 | 71.7 | 84.3 | **+12.7** |
| Composer 2.5 | 71.0 | 83.7 | **+12.7** |
| Step 3.7 Flash | 48.7 | 59.7 | **+11.0** |
| **总体** | **63.8** | **75.9** | **+12.1** |

---

## 三、逐 Case 详细评审

### 3.1 B1' 并发登录限制 — 增益最强 case

**模糊 prompt**："我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录"

#### 关键发现对比

| 发现点 | C1 noskill | C2 skill | C3 noskill | C4 skill | C5 noskill | C6 skill |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| Redis userId→token 映射 | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| refreshToken TTL 同步 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| forceLogout 同步清理 | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| delLoginUser 同步清理 | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| Redis 操作原子性 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 假设标注 | ❌ | ✅ 3项 | ❌ | ✅ 5项 | ❌ | ✅ |
| 具体代码实现 | ❌ | ✅ | 伪代码 | ✅ | ❌ | ✅ |

**点评**：

- **C2 GLM skill 的独有贡献**：发现了 `refreshToken()` 需要同步刷新 userId→token 映射的 TTL。这是所有其他 5 份产出都遗漏的关键点——如果不刷新映射 TTL，映射会先于 token 过期，导致单会话逻辑失效。这是 skill 结构化分析流程的直接收益。

- **C5 Step noskill 的致命缺陷**：提出了用 SCAN 遍历 `login_tokens:*` 的方案，在大用户量下有严重性能问题。且没有识别 forceLogout 同步需求。

- **C6 Step skill 的增益最大（+26）**：从 49 分提升到 75 分。skill 帮助 Step 模型发现了 LogoutSuccessHandlerImpl 清理映射、给出了 4 个完整 Step。

#### B1' 评分卡

| Cell | D1 | D2 | D3 | D4 | D5 | D6 | D7 | 总分 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 GLM noskill | 18 | 10 | 16 | 7 | 0 | 8 | 8 | **67** |
| C2 GLM skill | 19 | 13 | 18 | 8 | 12 | 9 | 9 | **88** |
| C3 Comp noskill | 18 | 12 | 16 | 8 | 0 | 8 | 8 | **70** |
| C4 Comp skill | 18 | 12 | 16 | 8 | 13 | 8 | 9 | **84** |
| C5 Step noskill | 12 | 8 | 12 | 5 | 0 | 6 | 6 | **49** |
| C6 Step skill | 16 | 12 | 14 | 7 | 10 | 8 | 8 | **75** |

---

### 3.2 B2' 请求体大小限制 — 增益最弱 case

**模糊 prompt**："API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

#### 关键发现对比

| 发现点 | C1 noskill | C2 skill | C3 noskill | C4 skill | C5 noskill | C6 skill |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| Express 默认 100kb 限制 | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| errorConverter isOperational 问题 | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| XSS 中间件内存放大 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| chunked encoding 处理 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 配置化（环境变量） | ✅可选 | ✅ | ✅ | ✅ | ✅可选 | ❌ |
| 假设标注 | ❌ | ✅ 3项 | ❌ | ✅ 4项 | ❌ | ✅ |
| error.ts 修改 | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |

**点评**：

- **C1 GLM noskill 的意外亮点**：发现了 `errorConverter` 中 `PayloadTooLargeError` 的 `isOperational = false` 问题——在 production 环境下 413 会被改为 500。这是全部 6 份产出中最深入的分析。同时识别了 XSS 中间件的 `JSON.stringify → inHTMLData → JSON.parse` 内存放大效应。

- **C2 GLM skill 的遗憾**：选择了 light 模式，分析深度反而不如 C1 noskill。light 模式跳过了 error.ts 的深入检查，遗漏了 isOperational 问题。这说明 **skill 的 light/full 判档有时反而限制了分析深度**。

- **C6 Step skill 的严重遗漏**：只有 1 个 Step（只改 `app.ts`），完全遗漏了 `error.ts` 需要处理 413。且 JSON 1MB / urlencoded 100KB 的不一致假设没有解释原因。

#### B2' 评分卡

| Cell | D1 | D2 | D3 | D4 | D5 | D6 | D7 | 总分 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 GLM noskill | 19 | 12 | 19 | 7 | 0 | 8 | 9 | **74** |
| C2 GLM skill | 16 | 12 | 14 | 9 | 12 | 8 | 9 | **80** |
| C3 Comp noskill | 18 | 12 | 17 | 9 | 0 | 8 | 8 | **72** |
| C4 Comp skill | 17 | 12 | 17 | 7 | 13 | 8 | 9 | **83** |
| C5 Step noskill | 14 | 10 | 12 | 5 | 0 | 6 | 6 | **53** |
| C6 Step skill | 14 | 10 | 8 | 5 | 8 | 6 | 6 | **57** |

---

### 3.3 B3' 邮箱验证强制检查 — 增益分化最大 case

**模糊 prompt**："注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

#### 关键发现对比

| 发现点 | C1 noskill | C2 skill | C3 noskill | C4 skill | C5 noskill | C6 skill |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| 注册时自动发验证邮件 | ✅ | ✅ | ✅可选 | ✅ | ✅推荐 | ❌ |
| 登录拦截 isEmailVerified | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| auth middleware 拦截 | ✅方案B | ❌(仅登录) | ✅ | ✅ | ❌ | ❌ |
| passport.ts select 增加 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| send-verification-email 鸡生蛋 | ✅ | ✅改公开 | ✅白名单 | ✅新端点 | ❌ | ❌ |
| refreshAuth 检查 | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| 测试更新方案 | ✅概述 | ✅详细 | ✅概述 | ✅详细 | ✅概述 | ❌ |
| 假设标注 | ❌ | ✅ 2项 | ❌ | ✅ 5项 | ❌ | ✅ |

**点评**：

- **C1 GLM noskill 的分析深度冠绝全场**：识别了 send-verification-email 的"鸡生蛋"问题（未验证用户被拦截后无法重新发送验证邮件），提出了两种方案（拒绝登录 vs 允许登录但限制功能），并分析了每种方案的连锁影响。分析深度甚至超过 skill 组。

- **C6 Step skill 的严重不完整**：只有 1 个 Step（在 `loginUserWithEmailAndPassword` 中加一行 `if (!user.isEmailVerified)` 检查）。完全没有：注册时自动发邮件、send-verification-email 改公开、auth middleware 拦截、passport.ts 改 select、测试更新。**skill 的结构化流程反而让 Step 模型"过早收敛"**，只做了最表面的改动。

- **C2 GLM skill 的设计决策**：选择"只在登录时拦截"而非"auth middleware 也拦截"，是有意的范围控制（在 010-requirements 中明确写了"不在 API 中间件层检查"）。这个决策是否合理取决于业务需求，但至少是显式标注的。

- **C4 Composer skill 的亮点**：提出了 ADMIN 豁免假设、新增 `resend-verification-email` 公开端点（与 C2 改造现有端点的方案不同）。假设覆盖面最广（5 项）。

#### B3' 评分卡

| Cell | D1 | D2 | D3 | D4 | D5 | D6 | D7 | 总分 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 GLM noskill | 19 | 12 | 19 | 7 | 0 | 8 | 9 | **74** |
| C2 GLM skill | 18 | 14 | 17 | 8 | 10 | 9 | 9 | **85** |
| C3 Comp noskill | 18 | 12 | 17 | 8 | 0 | 8 | 8 | **71** |
| C4 Comp skill | 18 | 12 | 16 | 8 | 13 | 8 | 9 | **84** |
| C5 Step noskill | 12 | 8 | 8 | 5 | 0 | 6 | 5 | **44** |
| C6 Step skill | 8 | 10 | 6 | 5 | 8 | 5 | 5 | **47** |

---

## 四、关键发现

### 发现 1：假设标注能力是 skill 的核心增量

| 模型 | noskill 假设标注 | skill 假设标注 |
|------|:---:|:---:|
| GLM | 0/3 | 3/3 ✅ |
| Composer | 0/3 | 3/3 ✅ |
| Step | 0/3 | 3/3 ✅ |

**所有 skill 组都识别了模糊点并标注了 [假设]，所有 noskill 组都没有。** 这是 V7 的核心验证目标，结果明确。

noskill 组并非没有做假设——它们隐式地做了同样的假设（如"限制 1MB"、"踢人模式"），但没有显式标注，用户无法区分哪些是确定的、哪些是猜的。

### 发现 2：增益因模型能力而异，强模型增益来自结构化，弱模型增益来自分析框架

| 模型 | noskill 基础分 | skill 增益 | 增益来源 |
|------|:---:|:---:|------|
| GLM | 71.7 | +12.7 | 结构化 + 假设标注（B1' 的 refreshToken TTL 是独有发现） |
| Composer | 71.0 | +12.7 | 假设标注 + 方案完整性（ADMIN 豁免、resend 端点） |
| Step | 48.7 | +11.0 | 分析框架（B1' +26，但 B2'/B3' 增益微弱） |

**Step 模型的 skill 增益极不均匀**：B1' +26（skill 帮助发现了 LogoutSuccessHandlerImpl），但 B2' +4、B3' +3。原因：Step 模型在 skill 的结构化流程中"过早收敛"，B2' 只做了 1 个 Step（改 app.ts），B3' 也只做了 1 个 Step（改 auth.service.ts），遗漏了大量关键改动。

### 发现 3：noskill 强模型偶有超越 skill 的深度分析

| 场景 | noskill 发现 | skill 是否发现 |
|------|------|:---:|
| B2' errorConverter isOperational | C1 GLM 发现 413 在 production 会被改为 500 | C2 ❌（light 模式跳过） |
| B2' XSS 中间件内存放大 | C1 GLM 发现 stringify→inHTMLData→parse 放大 | C2 ❌ |
| B2' chunked encoding | C1 GLM 分析了 body-parser 流式检查 | C2 ❌ |
| B3' 鸡生蛋问题 | C1 GLM 识别了 send-verification-email 依赖矛盾 | C2 ✅（但方案不同） |
| B3' refreshAuth 检查 | C3 Composer 识别了刷新 token 也需检查 | C4 ❌ |

这说明 **skill 的结构化流程有时反而限制了探索深度**。light 模式尤其明显——C2 GLM skill 在 B2' 中选择 light 模式后，分析深度显著低于 C1 noskill。

### 发现 4：Skill 的结构化价值不可否认

即使 noskill 强模型在分析深度上偶有超越，skill 组在以下维度始终优于 noskill：

| 结构化要素 | noskill 组 | skill 组 |
|------|:---:|:---:|
| 前置检查清单 | ❌ | ✅ |
| 回滚方案 | 偶尔提及 | ✅ 逐步骤 |
| 验证步骤（正向+错误用例） | 偶尔提及 | ✅ 系统性 |
| 方法名存在性验证 | ❌ | ✅ |
| 环境备选路径 | ❌ | ✅（C2） |
| 跨会话恢复状态 | ❌ | ✅ |
| 风格约束引用 | ❌ | ✅ [已核实] |

---

## 五、V6 vs V7 对比

| 维度 | V6（精确 prompt） | V7（模糊 prompt） |
|------|------|------|
| Skill 增益 | +2 分 | **+12.1 分** |
| noskill 分数 | 75.2 | 63.8（-11.4，模糊 prompt 拉低了 noskill） |
| skill 分数 | 77.2 | 75.9（-1.3，模糊 prompt 对 skill 影响极小） |
| 增益来源 | 结构化 | **假设标注（D5 贡献 ~10 分）+ 结构化** |
| noskill 主要问题 | 无（prompt 太精确） | 隐式假设不标注、偶发过度设计 |
| skill 主要优势 | 证据标签 | **模糊点识别、合理假设、防御性检查** |

**核心结论**：模糊 prompt 拉低了 noskill 组 11.4 分（因为缺少显式假设标注和结构化保障），但对 skill 组仅拉低 1.3 分（因为 skill 的澄清流程弥补了 prompt 的模糊性）。这证明 **skill 的核心价值在于"处理模糊需求"**。

---

## 六、对 Skill 改进的建议

### 6.1 light 模式需要增加"深度检查"门禁

C2 GLM skill 在 B2' 中选择 light 模式后，遗漏了 errorConverter 的 isOperational 问题。建议：light 模式在跳过详细设计前，仍需执行"关键风险点扫描"——至少检查错误处理链路是否兼容新增的错误类型。

### 6.2 防止"过早收敛"

C6 Step skill 在 B2'/B3' 中只做了 1 个 Step，遗漏大量关键改动。建议：在 030-implementation 的前置检查中增加"改动完整性自检"——对照 010-requirements 中的验收标准，确认每个验收点都有对应的实施 Step。

### 6.3 假设清单的"覆盖率"自检

当前 skill 组的假设标注质量参差不齐（C2 的 B3' 只有 2 项假设，而 C4 有 5 项）。建议：在 Phase 3 增加假设覆盖率自检——对照需求中的每个模糊表述，确认是否都产生了对应的假设项。

### 6.4 保留 noskill 的"探索深度"优势

C1 GLM noskill 在 B2' 中的深度分析（isOperational、XSS 放大、chunked encoding）超过了 skill 组。skill 的结构化流程不应取代这种探索性分析。建议：在 000-context-pack 或 020-design 阶段，增加"深入检查"环节，鼓励对中间件链路、错误处理链路做追踪式分析。

---

## 七、最终判定

| 问题 | 结论 |
|------|------|
| V7 是否验证了核心假设？ | ✅ **是**。模糊 prompt 下 skill 增益从 +2 提升到 +12.1 |
| skill 的核心价值是什么？ | **澄清模糊需求**（假设标注 + 防御性检查），而非结构化精确需求 |
| 增益是否稳定？ | ⚠️ **不完全稳定**。因模型能力和 case 复杂度而异（+3 ~ +26） |
| skill 是否有副作用？ | ⚠️ **有**。light 模式可能跳过深入检查；弱模型可能"过早收敛" |
| 是否值得使用 skill？ | ✅ **值得**。特别是对于模糊需求场景，skill 的假设标注和结构化保障有明确价值 |

---

## 附录：各 Cell 产出文件清单

| Cell | B1' 文件数 | B2' 文件数 | B3' 文件数 |
|------|:---:|:---:|:---:|
| C1 GLM noskill | 1 (analysis.md) | 1 (analysis.md) | 1 (analysis.md) |
| C2 GLM skill | 3 (010/020/030) | 3 (000/005/040-light) | 8 (000-090) |
| C3 Comp noskill | 1 (impact-analysis.md) | 1 (impact-analysis.md) | 1 (impact-analysis.md) |
| C4 Comp skill | 5 (000-030+state) | 5 (000-030+state) | 5 (000-030+state) |
| C5 Step noskill | 1 (impact-analysis.md) | 1 (impact-analysis.md) | 1 (impact-analysis.md) |
| C6 Step skill | 8 (000-090) | 5 (000-030+state) | 8 (000-090) |
