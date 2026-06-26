# Step 3.7 Flash 盲测 v4 评审总结

> 评审日期：2026-06-25
> 评审方式：源码级核实（读取实际产出文件，非仅凭自报）
> Runner：Step 3.7 Flash
> 基线：v3 盲测（`eval/runs/blind-2026-06-24-v3-step37flash/summary.md`）

---

## 一、核心结论

### 1.1 三项优化验证总览

| 优化 ID | Case | 验证点 | v3 状态 | v4 结果 | 判定 |
|---------|------|--------|---------|---------|------|
| 优化 6（P1-A） | B6 | facts 文件存在且内容真实 | ❌ 未产出 | ✅ file_count=113，head=346d60f，toplevel 正确 | **PASS（修复）** |
| 优化 7（I2-A） | B1 | 识别"每次"全量词→倾向 full | ⚠️ PARTIAL（判 light） | ✅ 识别覆盖缺口，定级 full | **PASS（修复）** |
| 优化 8（需求文档） | B1/B2/B3 | 无表名/类名/路径/代码片段 | 有技术细节 | ✅ 三份均为纯业务描述 | **PASS（修复）** |

### 1.2 v3 五项改进回归检查

| 改进 ID | Case | v3 结果 | v4 结果 | 判定 |
|---------|------|---------|---------|------|
| P1-A | B6 | ❌ FAIL | ✅ **修复** | 改进 |
| P1-B | B6 | ✅ | ✅ 保持（【10】节有完整自检表） | 不退步 |
| I1-A | B2 | ✅ | ✅ 保持（5 方法名+行号+异常行为标注） | 不退步 |
| I2-A | B1 | ⚠️ PARTIAL | ✅ **修复** | 改进 |
| IP1-A | B3 | ✅ | ✅ 保持（context-pack 有场景覆盖验证） | 不退步 |

**Step 3.7 Flash v4：3 项优化全通过 + 5 项改进全 PASS（v3 剩余 2 项失败修复）。**

---

## 二、逐项详细评审

### 2.1 优化 6：B6 facts 文件校验（v3 FAIL → v4 修复）

**源码核实**（读取 `B6/facts/scan.json` + `B6/facts/git.json`）：

| 字段 | 值 | 判定 |
|------|-----|------|
| scan.json file_count | 113 | ✅ >0 |
| scan.json budget_tier | small | ✅ |
| scan.json manifest_files | package.json | ✅ |
| git.json head_short | 346d60f | ✅ 正确 |
| git.json toplevel | E:/agent/.../prisma-express-ts | ✅ 正确 |
| git.json is_git_repo | true | ✅ |

**v3→v4 变化**：v3 根本未产出 facts 文件（B6 目录仅 _project-map.md），v4 产出了完整的 facts/scan.json + facts/git.json，内容真实有效。优化 6（pf_validate.py V6 facts 缺失 WARN→FAIL）+ Phase 1.5 强化"必做不可跳过"生效。

**判定：PASS ✅（v3 FAIL → v4 修复）**

> 注：file_count 113 vs Composer 106，差异因 Composer 先跑产出文件被 Step 的 scan 扫到（.md 文件 38 vs 31）。同一 commit 源码树未变，不影响 PASS。

### 2.2 优化 7：B1 覆盖范围语义核查（v3 PARTIAL → v4 修复）

**源码核实**（读取 `B1/000-context-pack.md` + `B1/020-design.md`）：

- ✅ context-pack 有「Coverage Gap: Controllers WITHOUT @Log」专节
- ✅ 列出 8 个未覆盖 controller（SysLoginController/CaptchaController/SysRegisterController 等）
- ✅ LogAspect pointcut `@annotation(controllerLog)` 只覆盖 @Log 方法 — LogAspect.java:59
- ✅ design 文档明确"Verdict: Cannot be light. Must be full."
- ✅ 识别"每次接口请求"全量词与 @Log 局部覆盖的缺口
- ✅ 定级 full，有 030-implementation.md（v3 light 档无此文件）

**v3→v4 变化**：v3 判 light（"零改动确认"，74 分，tier_judgment 8/15）导致 I2-A PARTIAL；v4 识别全量词→核实覆盖范围→定级 full。优化 7（Phase 2.5 覆盖范围语义核查）生效。

**判定：PASS ✅（v3 PARTIAL → v4 修复）**

### 2.3 优化 8：B1/B2/B3 需求文档内容边界（v3 有技术细节 → v4 修复）

**源码核实**（读取三份 `010-requirements.md`）：

| 文件 | 表名 | 类名 | 文件路径 | 代码片段 | 判定 |
|------|------|------|---------|---------|------|
| B1 | 无 | 无 | 无 | 无 | ✅ |
| B2 | 无 | 无 | 无 | 无 | ✅（注：提到 `varchar(100)` 和 `$2a$`/MD5 格式，属业务约束上下文，非技术实现渗入） |
| B3 | 无 | 无 | 无 | 无 | ✅ |

**判定：PASS ✅（v3 有技术细节 → v4 修复）**

> B2 的 `varchar(100)` 出现在"密码字段容量"业务约束中，说明字段无需变更，属于边界情况。比 v3 大量混入表名/类名/路径已大幅改善，不构成 FAIL。

### 2.4 P1-B 回归：B6 认证-鉴权自检

**源码核实**（读取 `B6/_project-map.md`）：

- ✅ 【10】节标题"Auth / Permission Model WITH Auth-Consistency Self-Check"
- ✅ 完整字段比对表（id/email/name/password/role/...，标注 selected by passport vs used by auth）
- ✅ 认证链路：select `{ id, email, name }` — passport.ts:17-21
- ✅ 鉴权链路：`roleRights.get(user.role)` — auth.ts:22
- ✅ 不一致结论：role 未在 select 中，所有 RBAC 检查静默失败
- ✅ 【9】风险区域 #1"Auth consistency bug"标注 HIGH
- ✅ Executive Summary 含修复建议（select 加 role: true）

**判定：PASS ✅（不退步）**

### 2.5 I1-A 回归：B2 方法名存在性验证

**源码核实**（读取 `B2/030-implementation.md`）：

| 方法 | 文件 | 行号 | 状态 |
|------|------|------|------|
| SecurityUtils.matchesPassword | SecurityUtils.java | 111 | ✅ 存在 |
| SecurityUtils.encryptPassword | SecurityUtils.java | 98 | ✅ 存在 |
| SysUserServiceImpl.resetUserPwd | SysUserServiceImpl.java | 391 | ✅ 存在 |
| Md5Utils.hash | Md5Utils.java | 55 | ✅ 存在 |
| getLoginUser | SecurityUtils.java | 72-81 | ✅ 存在，标注"抛 ServiceException 非返回 null" |

- ✅ 有「PRE-CHECK：方法存在性验证」小节
- ✅ 未出现编造的 updateUserPassword
- ✅ 5 个方法名全部 grep 验证附行号
- ✅ getLoginUser 异常行为确认（I2-A 相关）

**判定：PASS ✅（不退步）**

### 2.6 IP1-A 回归：B3 用户场景覆盖验证

**源码核实**（读取 `B3/000-context-pack.md`）：

- ✅ 「Current Auth Flow (Registration)」trace：POST /v1/auth/register → authController.register → userService.createUser
- ✅ auth.validation.ts 标注"register/login/password-reset validators"
- ✅ auth.controller.ts 在注册流程中
- ✅ 未排除注册流程（v3 修复保持）

**判定：PASS ✅（不退步）**

---

## 三、产出文件清单

| Case | 文件数 | 文件列表 |
|------|--------|---------|
| B6 | 3 | _project-map.md, facts/scan.json, facts/git.json |
| B1 | 4 | 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md |
| B2 | 4 | 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md |
| B3 | 4 | 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md |

共 15 个文件。

**与 Composer 2.5 的差异**：Step 产出少 9 个文件，主要是缺 _active-state.md（跨会话状态）、060-preflight.md（Phase 4 预检）、050-validation/（验证脚本）。这些不在优化 6-8 验证范围内，但影响整体产出完整度。

---

## 四、v3 → v4 改进效果对比

| 改进 ID | v3 状态 | v4 状态 | 优化措施 | 效果 |
|---------|---------|---------|---------|------|
| P1-A | ❌ FAIL（未产出 facts） | ✅ PASS | 优化 6：pf_validate V6 WARN→FAIL + Phase 1.5 强化 | **修复** |
| P1-B | ✅ PASS | ✅ PASS | — | 保持 |
| I1-A | ✅ PASS | ✅ PASS | — | 保持 |
| I2-A | ⚠️ PARTIAL（判 light） | ✅ PASS | 优化 7：Phase 2.5 覆盖范围语义核查 | **修复** |
| IP1-A | ✅ PASS | ✅ PASS | — | 保持 |

**两项遗留 FAIL 全部修复。** v3 的结论"需进一步强化 Script Gate 强制性"和"需增加覆盖范围语义核查指引"在 v4 中均验证生效。

---

## 五、结论

Step 3.7 Flash v4 验证完全通过：

- **3 项优化全 PASS**：优化 6（facts 强制）修复、优化 7（覆盖范围核查）修复、优化 8（需求文档去技术化）修复
- **5 项改进全 PASS**：v3 剩余 2 项失败（P1-A、I2-A）全部修复，其余 3 项不退步
- **v3.8 协议对 Step 3.7 Flash 完全生效**

**Step 3.7 Flash 在"强制 Read SKILL.md"+ 优化 6-8 联合作用下，从 v3 的 3/5 提升到 v4 的 5/5，可作为 v3.8 协议的 Runner。** 产出完整度（缺 _active-state/060-preflight/050-validation）是后续可优化项，但不影响改进项验证结论。
