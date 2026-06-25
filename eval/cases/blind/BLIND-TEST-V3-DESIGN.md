# 盲测 v3 测试设计

> 日期：2026-06-24
> 设计者：GLM-5.2
> 基线：v2 盲测复跑结果（`eval/runs/blind-2026-06-24-v2-summary.md`）

---

## 一、为什么需要 v3

### 1.1 v2 盲测暴露的问题

v2 盲测复跑结果显示：5 项改进中只有 3 项在 Composer 2.5 上生效（P1-A/I1-A/I2-A），2 项未生效（P1-B/IP1-A），1 项退步（P1-B）。Step 3.7 Flash 则 0/5 改进。

根因分析发现：**P1-B 和 IP1-A 的改进写在 `references/` 参考文件中，在自然语言驱动的盲测场景下模型不读参考文件，导致改进不触发。** 只有 SKILL.md 主入口的内容才会被可靠加载。

### 1.2 v2 到 v3 的协议优化

针对 v2 暴露的触发率问题，做了以下优化：

| 优化项 | 改哪里 | 改什么 | 解决的问题 |
|--------|--------|--------|-----------|
| P1-B 提升主入口 | `pathfinder/SKILL.md` Phase 3 | 认证-鉴权字段一致性自检从 `references/` 提升到 SKILL.md 正文，强调"先 Read 源码再比对" | v2 中 P1-B 退步：模型不读 references，自检不触发 |
| IP1-A 提升主入口 | `impact/SKILL.md` Phase 2 + `impact-pro/SKILL.md` Phase 2 | 用户场景覆盖验证从 `references/` 提升到 SKILL.md 正文 | v2 中 IP1-A 两个 Runner 都未触发 |
| I1-A/I2-A 强化 | `impact/SKILL.md` Phase 4 + `impact-pro/SKILL.md` Phase 4 | 从简略 bullet 扩展为带编号步骤的可操作清单 | v2 中 Composer 2.5 靠"避开问题"而非"执行预检"修复 |
| P1-B references 同步 | `pathfinder/references/phase-3-depth-fill.md` | 同步强调"先读源码再比对" | 保持 SKILL.md 和 references 一致 |
| Step 3.7 Flash prompt 加固 | `PROMPT-step37flash-v3.md` | 每个任务前显式要求 Read SKILL.md | v2 中 Step 3.7 Flash 疑似使用缓存旧协议 |

### 1.3 v3 的核心假设

**如果 P1-B 和 IP1-A 的改进放在 SKILL.md 主入口，模型在盲测中就能可靠触发这些检查。**

验证方式：用和 v2 相同的 4 个 case（B6/B1/B2/B3）重新跑，对比 v2 结果。

---

## 二、测试范围

### 2.1 Case 选择

v3 只跑 4 个 case，聚焦 v2 中有问题的改进项：

| Case | Skill | 对应改进 | v2 状态 | v3 验证目标 |
|------|-------|---------|---------|------------|
| B6 | pathfinder | P1-A + P1-B | P1-A 修复 / P1-B 退步 | P1-A 保持修复 / **P1-B 退步修复** |
| B1 | impact | I2-A | Composer 修复 / Step 未修复 | Composer 保持修复 / **Step 是否修复** |
| B2 | impact | I1-A | Composer 修复 / Step 未修复 | Composer 保持修复 / **Step 是否修复** |
| B3 | impact-pro | IP1-A | 两个 Runner 都未修复 | **两个 Runner 是否修复** |

跳过 B4 和 B5：B4 没有对应的改进项问题，B5 虽然是 pathfinder case 但没有已知的 authn-authz bug 可验证 P1-B。

### 2.2 Runner 模型

- Composer 2.5（v2 中 3/5 修复，1 退步，1 未修复）
- Step 3.7 Flash（v2 中 0/5 修复，疑似使用缓存旧协议）

### 2.3 评审模型

GLM-5.2（与 v2 相同，消除评审者变量）

---

## 三、验证点和成功标准

### 3.1 五项改进验证矩阵

| 改进 ID | Case | 验证点 | v2 结果 | v3 成功标准 |
|---------|------|--------|---------|------------|
| P1-A | B6 | facts 文件内容正确 | Composer ✅ / Step ❌ | Composer 保持 ✅ / Step 需确认 |
| P1-B | B6 | 发现 passport.ts select bug | Composer ❌退步 / Step ❌ | **Composer 重新发现 bug** / Step 需确认 |
| I1-A | B2 | 不编造方法名 | Composer ✅ / Step ❌ | Composer 保持 ✅ / **Step 不再编造** |
| I2-A | B1 | 正确处理 getLoginUser 异常 | Composer ✅ / Step ❌ | Composer 保持 ✅ / **Step 修正 null 检查** |
| IP1-A | B3 | 包含注册流程 | 两个 Runner ❌ | **两个 Runner 都包含注册流程** |

### 3.2 逐项验证细则

#### P1-A：B6 facts 文件内容校验

- 检查 `facts/scan.json` 的 `file_count > 0`（实际约 87）
- 检查 `facts/git.json` 的 `head_short` 非 null（实际 346d60f）
- 检查 `facts/git.json` 的 `toplevel` 指向 prisma-express-ts
- **Composer 2.5**：v2 已修复，v3 只需确认不退步
- **Step 3.7 Flash**：v2 未修复，v3 需确认是否修复（如果 prompt 加固有效）

#### P1-B：B6 认证-鉴权字段一致性自检

- 检查地图【10】权限模型节是否有"认证-鉴权字段一致性自检"
- 检查是否提到 `passport.ts:16` select 缺 role
- 检查是否提到 `auth.ts:22` RBAC 用 `user.role`
- 检查【9】风险区域是否记录了"认证 payload 缺少鉴权所需字段"
- **Composer 2.5**：v2 退步（v1 发现了 bug，v2 没发现），v3 必须重新发现 bug
- **Step 3.7 Flash**：v2 未发现，v3 需确认是否发现

**关键验证**：自检不能只是填一张比对表，必须有 Read 源码的痕迹（地图中引用了 `passport.ts` 和 `auth.ts` 的具体行号）。

#### I1-A：B2 实施文档方法名存在性验证

- 检查实施文档中是否出现 `updateUserPassword`（不存在的方法）
- 检查实施文档引用的方法名是否经 grep 验证
- 正确方法：`resetPwd(SysUser user)` 或 `resetUserPwd(Long userId, String password)`
- **Composer 2.5**：v2 已修复，v3 只需确认不退步
- **Step 3.7 Flash**：v2 仍编造 `updateUserPassword`，v3 必须不再编造

#### I2-A：B1 被调方法异常行为确认

- 检查实施代码是否对 `SecurityUtils.getLoginUser()` 做 null 检查
- `getLoginUser()` 抛 `ServiceException` 不返回 null，null 检查是逻辑缺陷
- 正确做法：try-catch 或换方案规避
- **Composer 2.5**：v2 已修复（换 Filter 方案），v3 只需确认不退步
- **Step 3.7 Flash**：v2 仍做 null 检查，v3 必须修正

#### IP1-A：B3 用户场景覆盖验证

- 检查 context-pack 是否有"用户场景覆盖验证"表或步骤
- 检查 `auth.route.ts` 和 `auth.controller.ts` 是否在变更范围内
- 检查实施文档是否修改了注册流程（`POST /v1/auth/register`）
- **两个 Runner**：v2 都未触发，v3 必须触发

**关键验证**：用户原话"注册的时候可以选填"——"注册"是入口场景。注册走 `POST /v1/auth/register` → `auth.controller.ts:register` → `userService.createUser(email, password)`。`auth.controller.ts:8` 只解构 `{ email, password }`，不含 phone，必须修改才能实现"注册时填手机号"。

---

## 四、执行流程

```
Step 1: 协议优化（已完成）
  - P1-B 提升到 pathfinder SKILL.md Phase 3
  - IP1-A 提升到 impact/impact-pro SKILL.md Phase 2
  - I1-A/I2-A 强化 impact/impact-pro SKILL.md Phase 4
  - references 同步更新

Step 2: 盲测 v3 执行
  - Composer 2.5 跑 B6/B1/B2/B3（4 个 case）
  - Step 3.7 Flash 跑 B6/B1/B2/B3（4 个 case，含 Read SKILL.md 前置步骤）
  - prompt 文件：
    - eval/cases/blind/PROMPT-composer25-v3.md
    - eval/cases/blind/PROMPT-step37flash-v3.md
  - 产出目录：blind-v3-{composer25,step37flash}/

Step 3: 评审
  - 评审者：GLM-5.2
  - 评审标准：JUDGE-RUBRIC.md（6 维度 100 分 + 4 项安全门禁）
  - 额外检查：5 个改进验证点（见上文 3.2）
  - 产出评分卡：eval/runs/blind-2026-06-24-v3-{composer25,step37flash}/

Step 4: 对比判定
  - v3 vs v2 对比：每个改进点是修复/保持/退步
  - v3 vs v1 对比：P1-B 是否恢复到 v1 水平（v1 发现了 bug）
  - 整体判定：5 个改进项中多少个在两个 Runner 上都通过
```

---

## 五、判定标准

### 5.1 单项判定

每个改进项的判定分为三档：

| 判定 | 含义 |
|------|------|
| ✅ PASS | 改进项触发且产出正确 |
| ❌ FAIL | 改进项未触发或产出有错 |
| ⚠️ PARTIAL | 改进项触发但产出有瑕疵（如自检做了但没发现 bug） |

### 5.2 整体判定

| 场景 | 判定 |
|------|------|
| 5/5 改进项在 Composer 2.5 上 PASS | 协议优化完全成功 |
| P1-B 和 IP1-A 在 Composer 2.5 上 PASS（v2 的两个失败项修复） | 协议优化主要目标达成 |
| P1-B 或 IP1-A 仍然 FAIL | 需要进一步排查模型执行问题 |
| Step 3.7 Flash 有改善（≥2/5 PASS） | prompt 加固有效 |
| Step 3.7 Flash 仍然 0/5 | 确认为模型能力限制，非协议问题 |

### 5.3 不需要重新跑的情况

如果 v3 结果和 v2 完全相同（Composer 2.5 仍然 P1-B 退步、IP1-A 未触发），说明提升到 SKILL.md 主入口也不够，需要考虑：
1. 在 SKILL.md 硬性规则区增加强制检查点
2. 在 Script Gate（pf_validate.py）中增加 P1-B 的自动检测
3. 在 prompt 中更明确地引导模型执行关键步骤

---

## 六、文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/PROMPT-composer25-v3.md` | Composer 2.5 v3 一键执行 prompt |
| `eval/cases/blind/PROMPT-step37flash-v3.md` | Step 3.7 Flash v3 一键执行 prompt（含 Read SKILL.md 前置步骤） |
| `eval/cases/blind/JUDGE-RUBRIC.md` | 评审标准（v3 复用，不变） |
| `eval/runs/blind-2026-06-24-v2-summary.md` | v2 盲测复跑报告（v3 基线） |
| `docs/archive/2026-06/skill-improvement-2026-06-24.md` | 改进方案文档（含 v2 结果和 v3 计划） |
