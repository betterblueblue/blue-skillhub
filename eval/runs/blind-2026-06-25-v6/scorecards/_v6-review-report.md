# V6 盲测评审报告

> 评审时间：2026-06-25  
> 评审范围：6 cell × 3 case = 18 份产出  
> 测试矩阵：3 模型 × 2 条件（skill / noskill）× 3 场景

---

## 一、测试场景回顾

| Case | 项目 | 需求 | 预设状态 | 预期档位 |
|------|------|------|---------|---------|
| B1' | RuoYi-Vue (Java) | 并发登录限制（踢人） | 未实现 | Full |
| B2' | prisma-express-ts (Node) | 请求体大小限制 1MB/10MB | 未实现 | Light |
| B3' | prisma-express-ts (Node) | 邮箱验证强制检查 | 部分实现 | Full |

V5 的"全已实现"问题已解决：V6 三个场景均为"未实现"或"部分实现"，模型必须做真正的变更分析。

---

## 二、总览评分矩阵

### 档位判定

| Cell | 模型 | 条件 | B1' (Full) | B2' (Light) | B3' (Full) | 判档正确率 |
|------|------|------|-----------|------------|-----------|-----------|
| C1 | GLM-5.2 | noskill | N/A（自由格式） | N/A | N/A | — |
| C2 | GLM-5.2 | skill | Full ✅ | Light ✅ | Full ✅ | 3/3 |
| C3 | Composer 2.5 | noskill | N/A（自由格式） | N/A | N/A | — |
| C4 | Composer 2.5 | skill | Full ✅ | Light ✅ | Full ✅ | 3/3 |
| C5 | Step 3.7 Flash | noskill | N/A（自由格式） | N/A | N/A | — |
| C6 | Step 3.7 Flash | skill | Full ✅ | **Full ❌** | Full ✅ | 2/3 |

### 综合评分（百分制）

| 维度 | C1 GLM-ns | C2 GLM-sk | C3 Cmp-ns | C4 Cmp-sk | C5 Step-ns | C6 Step-sk |
|------|-----------|-----------|-----------|-----------|------------|------------|
| 现状核查准确性 | 90 | 95 | 90 | 95 | 85 | 80 |
| 证据质量 | 85 | 90 | 85 | 90 | 75 | 70 |
| 影响面完整性 | 90 | 85 | 90 | 85 | 80 | 65 |
| 方案正确性 | 85 | 80 | 85 | 85 | 70 | 60 |
| 档位判定 | — | 100 | — | 100 | — | 67 |
| 文档规范性 | — | 85 | — | 90 | — | 70 |
| **总分** | **87** | **89** | **87** | **89** | **77** | **69** |

> noskill 组不评档位和文档规范性（自由格式），总分按 4 维平均。

---

## 三、逐场景详细评审

### B1'：并发登录限制（RuoYi-Vue）

**源码事实**：`SecurityConfig.java:98` STATELESS；`TokenService.java:117` 每次登录生成新 UUID；Redis 无 user→token 反向映射；无 SessionRegistry / concurrentSessionControl。

#### C1 GLM noskill — ⭐ 优秀

- **现状核查**：✅ 正确识别"未实现"，列出 5 条关键证据，引用具体行号
- **影响面**：✅ TokenService、SysLoginService、CacheConstants、JwtAuthenticationTokenFilter、application.yml
- **方案**：✅ Redis user→token 映射 + 旧 token 删除，思路正确
- **亮点**：发现"无需修改 JwtAuthenticationTokenFilter"——旧 token Redis key 被删后 `getLoginUser()` 返回 null，请求自然 401
- **风险识别**：✅ TTL 同步、竞态、管理员强退兼容、Redis 故障降级
- **不足**：影响面表格提到修改 JwtAuthenticationTokenFilter，但方案部分又说无需修改，前后矛盾

#### C2 GLM skill — 良好

- **档位**：Full ✅
- **现状核查**：✅ "未实现"，有【已核实: file:line】证据标签
- **影响面**：TokenService、CacheConstants、LogoutSuccessHandler、SysUserOnlineController
- **方案**：4 步实施（常量→createToken 踢人→delLoginUser 清理→forceLogout 清理）
- **不足**：
  - ❌ 未处理 `refreshToken()` 时同步续期 user→token 映射 TTL 的问题（C1 noskill 识别了此风险）
  - ❌ 未处理并发登录竞态（C1 noskill 提出了 Lua 脚本方案）
  - `delLoginUser` 方法签名改了又改，先说改签名再说不改，犹豫不决

#### C3 Composer noskill — ⭐ 优秀

- **现状核查**：✅ 表格化呈现，证据充分
- **影响面**：✅ TokenService、CacheConstants、refreshPermissionByRoleId 兼容性
- **方案**：✅ Redis 映射，登录/登出/被踢检测流程清晰
- **亮点**：提出 admin 豁免问题（`refreshPermissionByRoleId` 第 252 行跳过 admin）
- **不足**：无明显问题

#### C4 Composer skill — 良好

- **档位**：Full ✅
- **现状核查**：✅ 有【已核实】证据标签
- **方案**：`kickOutPreviousSessions` + createToken 修改 + delLoginUser 修改
- **亮点**：`delLoginUser` 中只删除映射当 token 匹配时才删（`if (token.equals(activeToken))`），避免删错
- **不足**：
  - ❌ 未处理 TTL 同步问题
  - ❌ 未处理并发竞态问题

#### C5 Step noskill — 中等

- **现状核查**：✅ 正确识别"未实现"
- **方案**：使用 Redis Set（SADD/SREM）维护用户 token 集合
- **不足**：
  - ❌ **过度设计**：需求是"单会话"（只保留一个 token），用 String 就够，不需要 Set
  - ❌ `kickUserTokens` 方法中 `keepToken` 参数传 null，但逻辑用 `!tokenKey.equals(keepToken)` 判断，null equals 永远为 false，所有 token 都会被删（包括新创建的）
  - 提到 SCAN/KEYS `login_tokens:*` 和维护用户→token 集合两套方案混在一起

#### C6 Step skill — 中等

- **档位**：Full ✅
- **现状核查**：✅ 有现状核查表
- **方案**：`checkAndKickOldSession` + createToken 写入映射 + login 调用踢人
- **不足**：
  - ❌ 未处理 TTL 同步问题
  - ❌ 未处理并发竞态问题
  - ❌ 未处理 `delLoginUser` / `forceLogout` 的映射清理（C2、C4 都处理了）
  - ❌ 未创建 `_active-state.md`

---

### B2'：请求体大小限制（prisma-express-ts）

**源码事实**：`app.ts:27` `express.json()` 无 limit；`app.ts:30` `express.urlencoded({ extended: true })` 无 limit；无 multer；`error.ts` errorConverter 不识别 PayloadTooLargeError。

#### C1 GLM noskill — ⭐ 优秀

- **现状核查**：✅ 正确识别"未实现"，完整中间件链路图
- **影响面**：✅ app.ts、error.ts、config.ts、.env.example
- **方案**：✅ 全局 limit + errorConverter 413 处理 + multer 预留
- **亮点**：发现 Express 默认 100kb，改为 1MB 是"放宽"而非"新增限制"
- **不足**：提出方案二（自定义中间件）但自己否定了，略显冗余

#### C2 GLM skill — ⭐ 优秀

- **档位**：Light ✅ 正确
- **现状核查**：✅ "未实现"，有【已核实: file:line】标签
- **影响面**：app.ts、error.ts — 精准，只改 2 个文件
- **Out of Scope**：✅ 文件上传 10MB 列入"未确认项"而非 Out of Scope，符合门禁规则
- **方案**：硬编码 1mb + errorConverter 添加 413 处理
- **不足**：无明显问题，light 档非常精准

#### C3 Composer noskill — 优秀

- **现状核查**：✅ 正确识别"未实现"
- **影响面**：✅ app.ts、config.ts、error.ts、.env.example
- **方案**：✅ 配置化 limit + errorConverter 识别 entity.too.large
- **不足**：上传路由方案 A/B 选择不够明确

#### C4 Composer skill — ⭐ 优秀

- **档位**：Light ✅ 正确
- **现状核查**：✅ "未实现"，有【已核实】标签
- **影响面**：app.ts、config.ts、error.ts — 精准
- **Out of Scope**：✅ 正确处理文件上传
- **接口一致性检查**：✅ 有接口返回检查清单
- **不足**：无明显问题

#### C5 Step noskill — 中等

- **现状核查**：✅ 正确识别"未实现"
- **方案**：`express.json({ limit: '1mb' })`
- **不足**：
  - ❌ 误判"现有 error handler 已能正确处理 413"——errorConverter 用 `error.statusCode` 判断，413 确实会取到 413，但 message 会用 body-parser 的英文默认消息，不满足用户要求的"请求体过大"提示。C1（GLM noskill）正确识别了这个问题。
  - 提出自定义中间件方案 B 用 content-length 判断，但 chunked transfer encoding 时 content-length 不存在

#### C6 Step skill — ❌ 最差

- **档位**：**Full ❌ 应为 Light**
- **现状核查**：标为"部分实现"（因 Express 有默认 100kb），有争议但可接受
- **严重问题**：
  - ❌ **过度设计**：新建 `upload.route.ts`、`upload.controller.ts`、`bodySizeLimit.ts` 三个文件。用户要求"限制请求体大小"，不是"实现文件上传功能"。
  - ❌ **技术错误**：`express.raw({ type: 'multipart/form-data' })` 无法解析 multipart/form-data，需要 multer 或 busboy
  - ❌ 违反"简单优先"原则：3 个文件 + 新路由注册，而 light 档只需改 2 行代码 + 1 个错误分支
  - ❌ 未创建 `_active-state.md`

---

### B3'：邮箱验证强制检查（prisma-express-ts）

**源码事实**：`schema.prisma:20` `isEmailVerified Boolean @default(false)` ✅；`auth.service.ts:17-36` 查询了 `isEmailVerified`（第 27 行）但不检查；`passport.ts:16-23` select 只含 `id, email, name`，不含 `isEmailVerified`；`auth.ts` verifyCallback 不检查；`auth.service.ts:102-115` `verifyEmail()` 已实现。

#### C1 GLM noskill — ⭐ 最全面

- **现状核查**：✅ 正确识别"部分实现"，"已实现"vs"未实现"对比表
- **影响面**：✅ auth.service.ts、passport.ts、auth.ts、auth.controller.ts
- **方案**：✅ 登录拦截 + 中间件拦截 + passport select 修改 + 豁免处理
- **亮点**：
  - ⭐ 发现 `refreshAuth()` 也需要检查 `isEmailVerified`（其他多数组遗漏）
  - ⭐ 发现 `send-verification-email` 死锁问题（未验证用户无法发验证邮件）
  - 提出两种豁免方案（中间件参数 vs 独立中间件）
  - 识别注册后自动发验证邮件的需求
- **不足**：方案有点复杂，auth() 中间件签名改法不够优雅

#### C2 GLM skill — 良好

- **档位**：Full ✅
- **现状核查**：✅ "部分实现"，有【已核实: file:line】标签
- **方案**：4 步实施（passport select → 登录检查 → 中间件检查+allowUnverified → 路由豁免）
- **不足**：
  - ❌ **遗漏 refreshAuth 检查**：未验证用户可通过 refresh token 获取新 access token 绕过登录拦截
  - ❌ 未处理注册后自动发验证邮件
  - `auth()({ allowUnverified: true })` 调用方式不够优雅（柯里化嵌套）

#### C3 Composer noskill — ⭐ 优秀

- **现状核查**：✅ 正确识别"部分实现"，覆盖表非常详细
- **影响面**：✅ auth.service.ts、auth.ts、passport.ts、auth.controller.ts
- **方案**：✅ 登录拦截 + refreshAuth 拦截 + 中间件拦截
- **亮点**：
  - ⭐ 认证链路覆盖表（8 个环节逐一标注）
  - ⭐ 注册策略三种方案（A/B/C）让用户选择
  - 接口一致性表格
- **不足**：中间件豁免用 path 字符串匹配

#### C4 Composer skill — 良好

- **档位**：Full ✅
- **现状核查**：✅ "部分实现"，有【已核实】标签
- **方案**：5 步实施（passport → 登录 → refreshAuth → 中间件 → 测试）
- **亮点**：`getUserById` null 行为标注为【待核实】——诚实的知识边界
- **不足**：
  - ❌ refreshAuth 检查用 `getUserById(userId)` 但未确认是否 select 了 `isEmailVerified`
  - 中间件豁免用 path 字符串匹配
  - 未处理注册后自动发验证邮件

#### C5 Step noskill — 良好

- **现状核查**：✅ 正确识别"部分实现"——"字段存在但执行缺失"
- **影响面**：auth.service.ts、auth.ts、passport.ts
- **方案**：✅ 登录拦截 + 中间件拦截 + passport select 修改
- **亮点**：
  - ⭐ 发现 `send-verification-email` 死锁问题
  - ⭐ 接口一致性检查表，标注"逻辑冲突"
  - 推荐方案 A（去掉 auth 中间件）——虽可商榷但逻辑自洽
- **不足**：未处理 refreshAuth

#### C6 Step skill — ❌ 最差

- **档位**：Full ✅
- **现状核查**：✅ "部分实现"
- **严重问题**：
  - ❌ **遗漏 passport.ts 修改**（致命）：030-implementation.md 只有 3 步（auth.service.ts 登录检查 → auth.ts 中间件检查+白名单 → auth.route.ts 确认），完全没有修改 passport.ts 的 select。passport.ts 只查 `id, email, name`，不包含 `isEmailVerified`，导致中间件中 `user.isEmailVerified` 永远是 `undefined`（falsy），**所有已认证用户都会被 403 拦截**。
  - ❌ **回滚方案幻觉**：回滚表中出现"messages.properties 错误消息 | 删除两行"——这是 Java/Spring 项目的文件，prisma-express-ts 项目中不存在
  - ❌ 未处理 refreshAuth
  - ❌ 未处理注册后自动发验证邮件
  - ❌ 未创建 `_active-state.md`
- **讽刺**：Step noskill（C5）正确识别了 passport.ts 需要修改，Step skill（C6）反而遗漏了

---

## 四、横向对比分析

### 4.1 Skill vs Noskill 增益

| 模型 | noskill 总分 | skill 总分 | 增益 | 判定 |
|------|-------------|-----------|------|------|
| GLM-5.2 | 87 | 89 | +2 | 微正向（结构化提升，深度略降） |
| Composer 2.5 | 87 | 89 | +2 | 微正向（结构化提升，证据标签生效） |
| Step 3.7 Flash | 77 | 69 | **-8** | **负向**（判档错误 + 遗漏 + 幻觉） |

**结论**：Skill 对 GLM 和 Composer 有微正向增益（结构化、证据标签、档位判定），但对 Step 3.7 Flash 产生了负向效果——模型能力不足以正确执行 skill 流程，反而被流程引导出了更多错误。

### 4.2 现状核查门禁效果

| Cell | B1' 核查 | B2' 核查 | B3' 核查 | 门禁生效 |
|------|---------|---------|---------|---------|
| C2 GLM-sk | 未实现 ✅ | 未实现 ✅ | 部分实现 ✅ | ✅ |
| C4 Cmp-sk | 未实现 ✅ | 未实现 ✅ | 部分实现 ✅ | ✅ |
| C6 Step-sk | 未实现 ✅ | 部分实现 ⚠️ | 部分实现 ✅ | ⚠️ 部分 |

C6 B2' 标为"部分实现"（因 Express 默认 100kb），判定本身可接受，但后续走了 Full 档并新建 3 个文件，说明门禁的"部分实现→继续 Phase 3"逻辑被执行了，但 Phase 3 的范围控制失效了——文件上传路由的"缺口"被直接实现而非列为"待确认项"。

### 4.3 证据标签强制化效果

| Cell | 证据标签使用 | 标签格式 |
|------|------------|---------|
| C2 GLM-sk | ✅ 广泛使用 | 【已核实: file:line】 |
| C4 Cmp-sk | ✅ 广泛使用 | 【已核实: file:line】 |
| C6 Step-sk | ⚠️ 部分使用 | 格式不一致 |

### 4.4 _active-state.md 合规性

| Cell | B1' | B2' | B3' | 合规率 |
|------|-----|-----|-----|--------|
| C2 GLM-sk | ✅ | ✅ | ✅ | 3/3 |
| C4 Cmp-sk | ✅ | ✅ | ✅ | 3/3 |
| C6 Step-sk | ❌ | ❌ | ❌ | 0/3 |

### 4.5 关键遗漏汇总

| 遗漏项 | C1 | C2 | C3 | C4 | C5 | C6 | 严重性 |
|--------|----|----|----|----|----|----|--------|
| B1': TTL 同步 | ✅识别 | ❌ | ✅识别 | ❌ | — | ❌ | 中 |
| B1': 并发竞态 | ✅识别 | ❌ | ✅识别 | ❌ | ✅识别 | ❌ | 中 |
| B1': delLoginUser/forceLogout 清理 | ✅ | ✅ | ✅ | ✅ | — | ❌ | 高 |
| B2': 413 错误消息未自定义 | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | 中 |
| B3': passport.ts select 修改 | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | **致命** |
| B3': refreshAuth 检查 | ✅ | ❌ | ✅ | ⚠️ | ❌ | ❌ | 高 |
| B3': send-verification-email 死锁 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 高 |

> C6 B3' 遗漏 passport.ts 修改是本次测试中最严重的单项错误——会导致所有已认证用户被 403 拦截，系统完全不可用。

---

## 五、模型能力排名

### 综合排名

1. **Composer 2.5（skill）** = **GLM-5.2（skill）** — 并列第一（89 分）
   - 档位判定 3/3 正确
   - 证据标签广泛使用
   - 文档结构完整（_active-state.md 全部创建）
   - 差异：GLM 深度略优（B3' 发现 refreshAuth），Composer 结构化略优（接口一致性自检表）

2. **Composer 2.5（noskill）** = **GLM-5.2（noskill）** — 并列第二（87 分）
   - 现状核查准确
   - 影响面完整
   - 无 skill 约束时自由格式表现同样优秀

3. **Step 3.7 Flash（noskill）** — 第三（77 分）
   - 现状核查基本准确
   - 方案有过度设计倾向（B1' 用 Set）
   - B3' 正确识别 passport.ts 修改

4. **Step 3.7 Flash（skill）** — 第四（69 分）
   - B2' 判档错误（Full 应为 Light）
   - B3' 遗漏 passport.ts 修改（致命）
   - B3' 回滚方案出现 Java 项目幻觉
   - _active-state.md 全部缺失

### 模型特征

| 模型 | 优势 | 劣势 |
|------|------|------|
| GLM-5.2 | 深度分析强（TTL、竞态、refreshAuth），风险识别全面 | 方案有时犹豫（delLoginUser 签名改了又改） |
| Composer 2.5 | 结构化最好（覆盖表、接口一致性表），方案果断 | 深度略逊（遗漏 refreshAuth） |
| Step 3.7 Flash | 基本面可（现状核查、影响面） | 复杂场景容易出错（过度设计、遗漏、幻觉），skill 流程执行力不足 |

---

## 六、Skill 协议改进建议

### 6.1 现状核查门禁需增加"范围控制"

**问题**：C6 B2' 现状核查标为"部分实现"后，Phase 3 直接实现了文件上传路由（缺口），而非列为"待确认项"。

**建议**：在"部分实现"分支中增加约束：
```text
部分实现 → 继续 Phase 3，但：
  1. 缺口必须列入"待确认项"，由用户决定是否纳入
  2. 禁止在本次变更中直接实现缺口功能
  3. 如果缺口不影响主需求的核心路径，默认走 light 档
```

### 6.2 增加"依赖字段检查"规则

**问题**：C6 B3' 在 auth.ts 中检查 `user.isEmailVerified`，但 passport.ts 的 select 不含此字段，导致检查永远为 falsy。

**建议**：在实施文档生成前增加自检规则：
```text
字段依赖自检：如果代码中检查了字段 X（如 user.isEmailVerified），
必须确认该字段在数据来源（如 DB select、API response）中已被包含。
未包含则必须先修改数据来源。
```

### 6.3 _active-state.md 创建需强制化

**问题**：C6 三个 case 均未创建 _active-state.md。

**建议**：在 030-implementation.md 模板中增加前置检查项：
```text
- [ ] _active-state.md 已创建（强制）
```

### 6.4 回滚方案需项目上下文校验

**问题**：C6 B3' 回滚方案出现 `messages.properties`（Java 项目文件），但实际是 Node.js/TypeScript 项目。

**建议**：在回滚方案生成时增加校验：
```text
回滚方案中引用的文件必须与项目技术栈匹配。
如果出现不属于当前技术栈的文件名，标记为幻觉并删除。
```

---

## 七、结论

### V5 → V6 改进验证

| V5 问题 | V6 改进 | 验证结果 |
|---------|--------|---------|
| 四个 case 全是"已实现"场景 | 三个场景均为"未实现"或"部分实现" | ✅ 解决 |
| 有 skill 组在功能已实现时仍选 full 档 | 现状核查门禁强制检查 | ✅ GLM/Composer 生效，Step 部分失效 |
| 证据标签缺失 | 证据标签强制化 | ✅ GLM/Composer 生效，Step 部分 |

### 核心发现

1. **Skill 对强模型（GLM、Composer）有微正向增益**，主要体现在结构化、证据标签、档位判定三个方面。
2. **Skill 对弱模型（Step 3.7 Flash）产生负向效果**，模型能力不足以正确执行 skill 流程，反而被流程引导出更多错误（判档错误、遗漏、幻觉）。
3. **noskill 组的表现并不差**——GLM 和 Composer 在 noskill 条件下同样能产出高质量分析，说明这些模型本身具备良好的分析能力，skill 的主要价值在于结构化和可追溯性。
4. **Step noskill 反而比 Step skill 更好**（77 vs 69），这是一个重要信号：skill 流程对模型能力有下限要求，低于下限时 skill 反而成为负担。
5. **现状核查门禁**是 V6 最有效的新增机制，在 GLM 和 Composer 上完全生效，正确引导了档位判定。
6. **证据标签强制化**在 GLM 和 Composer 上生效，提高了可追溯性。
