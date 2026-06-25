# B1-B9 综合盲测结论报告

> 日期：2026-06-25
> 覆盖范围：B1-B6（增量变更分析）+ E1-E4（Phase 5 执行）+ B7-B9（破坏性变更 + 新技术栈）
> 测试模型：Composer 2.5 / Step 3.7 Flash / GLM-5.2 / DeepSeek-V4-Flash / Opus 4.6
> Skill：pathfinder / impact / impact-pro（v1 → v4.1 迭代）
> 技术栈：Java/Spring/MyBatis、Node/Express/Prisma、Go/Gin/GORM、Python/FastAPI/SQLModel、静态前端
> 评审方式：源码锚点核实 + Rubric 专项评分

---

## 一、测试全景

### 1.1 Case 矩阵

| 批次 | Case | 项目 | 需求 | 变更类型 | 预期档位 |
|------|------|------|------|---------|---------|
| **B1-B6** | B1 | ruoyi-vue (Java) | 操作日志加响应耗时 | 增量（已实现） | — |
| | B2 | ruoyi-vue (Java) | 密码 MD5→BCrypt | 增量（已实现） | — |
| | B3 | prisma-express-ts (Node) | 用户加手机号字段 | 增量（已实现） | — |
| | B4 | prisma-express-ts (Node) | 用户加最后登录时间 | 增量 | — |
| | B5 | prisma-express-ts (Node) | pathfinder 摸底 | 只读分析 | — |
| | B6 | prisma-express-ts (Node) | pathfinder 摸底 | 只读分析 | — |
| **E1-E4** | E1 | prisma-express-ts (Node) | 用户加最后登录时间 | 增量 + 执行 | full |
| | E2 | full-stack-fastapi (Python) | Item 加置顶标记 | 增量 + 执行 | full |
| | E3 | ruoyi-vue (Java) | 部门加联系邮箱 | 增量 + 执行 | light（降级） |
| | E4 | static-frontend | 首页加用户反馈表单 | 增量 + 执行 | light |
| **B7-B9** | B7 | go-admin (Go) | 用户加微信号 | 新增字段 + 执行 | full |
| | B8 | prisma-express-ts (Node) | name→fullName 重命名 | **破坏性重命名** + 执行 | full |
| | B9 | ruoyi-vue (Java) | 删掉用户备注字段 | **删字段** + 执行 | full |

### 1.2 模型 × 条件矩阵

| 模型 | noskill | skill | 参与轮次 |
|------|:-------:|:-----:|---------|
| Composer 2.5 | ✅ | ✅ | v1-v4, V5-V10, E1-E4, B7-B9（全轮次） |
| Step 3.7 Flash | ✅ | ✅ | v1-v4, V5-V7 |
| GLM-5.2 | ✅ | ✅ | V5-V7 |
| DeepSeek-V4-Flash | ✅ | ✅ | v4 |
| Opus 4.6 | ✅ | ❌ | V5（预算不足未完成 skill 组） |

### 1.3 技术栈覆盖

| 技术栈 | Case | Skill | profile |
|--------|------|-------|---------|
| Java/Spring/MyBatis | B1, B2, E3, B9 | impact | java-spring-mybatis |
| Node/Express/Prisma | B3, B4, B5, B6, E1, B8 | impact-pro | node-express-prisma |
| Go/Gin/GORM | B7 | impact-pro | go-gin-gorm（首测） |
| Python/FastAPI/SQLModel | E2 | impact-pro | python-fastapi-sqlmodel |
| 静态前端（无构建系统） | E4 | impact-pro | static-frontend |

---

## 二、评分总览

### 2.1 B1-B6（Phase 4 分析阶段，v3 最终版）

| Case | Composer 2.5 (v3) | Step 3.7 Flash (v3) | DeepSeek (v4) |
|------|:-----------------:|:-------------------:|:-------------:|
| B1 (impact) | 95 | 80 | 70 |
| B2 (impact) | 96 | 88 | 75 |
| B3 (impact-pro) | 95 | 90 | — |
| B4 (impact-pro) | 95 | 92 | — |
| B5 (pathfinder) | 95 | 78 | 88 |
| B6 (pathfinder) | 93 | 78 | 85 |
| **均分** | **95.3** | **84.3** | **79.5** |

### 2.2 E1-E4（Phase 5 执行阶段）

| Case | 技术栈 | 档位 | 分数/100 | P0 | P1 |
|------|--------|:----:|:--------:|:--:|:--:|
| E1 | Node/Express/Prisma | full | 84 | 0 | 1 |
| E2 | Python/FastAPI/SQLModel | full | 83 | 0 | 1 |
| E3 | Java/Spring/MyBatis | light | 93 | 0 | 0 |
| E4 | 静态前端 | light | 98 | 0 | 0 |
| **均分** | | | **89.5** | **0** | **2** |

### 2.3 B7-B9（破坏性变更 + 新技术栈）

| Case | 技术栈 | 变更类型 | 分数/80 | P0 | 修复状态 |
|------|--------|---------|:-------:|:--:|---------|
| B7 | Go/Gin/GORM | 新增字段 | 71 | 0 | — |
| B8 | Node/Express/Prisma | 破坏性重命名 | 71 | 0 | 干净重跑已消除污染 |
| B9 | Java/Spring/MyBatis | 删字段 | 68 | 0 | toString 遗漏已修复 |
| **均分** | | | **70（87.5%）** | **0** | — |

---

## 三、核心发现

### 3.1 Skill 的核心价值：澄清模糊需求

这是整个盲测最重要的发现。通过 V6（精确 prompt）和 V7（模糊 prompt）的对照实验：

| 条件 | 精确 prompt（V6） | 模糊 prompt（V7） |
|------|:---:|:---:|
| Skill 增益 | +2 分 | **+12.1 分** |
| noskill 受模糊影响 | 小（75.2） | 大（63.8，-11.4） |
| skill 受模糊影响 | 小（77.2 → 75.9，-1.3） | 小（75.9） |

**结论**：Skill 的核心价值不是让精确需求更结构化（增益仅 +2），而是在用户说不清楚时帮 agent 澄清（增益 +12.1）。所有 skill 组都标注了 `[假设]`，所有 noskill 组都没有——用户无法区分哪些是确定的、哪些是猜的。

### 3.2 协议迭代效果：持续提升，无回退

从 v3.9 到 v4.1 的三轮迭代，每轮都有实质提升：

```
V7 (v3.9 前) → V8 (v3.9) → V9 (v4.0) → V10 (v4.1)
83.7 → 88.0 → 92.0 → 96.0
```

关键改进机制的贡献：

| 改进 | 捕获的关键遗漏 | 机制 |
|------|-------------|------|
| F3 关键链路追踪 | refreshToken TTL 同步、passport.ts select、refreshAuth 检查 | 强制追踪错误处理链/中间件管线/数据流路径 |
| F4 light 深度检查 | Express 默认 100kb、XSS 内存放大、413→500 | light 模式不再跳过链路扫描 |
| F2 改动完整性自检 | refreshAuth 检查（通过验收→Step 映射） | 验收标准逐条映射到实施 Step |
| F7 多轮触发 | 公开重发接口可被无限调用 | 链路追踪副作用回流 Phase 3 追问 |

### 3.3 破坏性变更保护流程可靠

B7-B9 验证了破坏性变更的保护机制：

- **引用扫描**：B8 的 name 消费者扫描覆盖 11 个文件 + 行号，正确排除非 User 字段的 name 引用（package.json name、faker.name、Swagger tag name）
- **破坏面回显**：B9 正确识别 BaseEntity 是共享基类，决定不删 BaseEntity.remark、不 DROP COLUMN
- **高风险拦截**：B7 GORM struct tag 修改标为高风险（等同 ALTER TABLE），B8 Prisma schema rename 标为高风险
- **P0 安全红线**：三个 case 零命中

### 3.4 模型能力差异显著

| 能力维度 | Composer 2.5 | GLM-5.2 | Step 3.7 Flash | DeepSeek-V4-Flash |
|---------|:---:|:---:|:---:|:---:|
| 现状核查 | ✅ 强 | ✅ 强 | ⚠️ 中 | ⚠️ 中 |
| 证据编造 | 0 例 | 0 例 | 1 例(V1)→0(V3) | 0 例 |
| 跨文件分析 | ✅ 强（发现 RBAC 失效） | ✅ 强（发现 queryUsers password 泄露） | ❌ 弱 | ❌ 弱 |
| 判档准确性 | ✅ 全对 | ✅ 全对 | ⚠️ V6 误判 Full | ❌ 误判 light |
| Skill 执行力 | ✅ 强 | ✅ 强 | ❌ V6 负向 | ❌ 产出不完整 |
| 行号精度 | 中等（偏差 1-10 行） | 高 | 极高（零偏差） | 高 |
| 假设标注 | ✅ 5 项/case | ✅ 3 项/case | ✅ 1 项/case | ❌ 无 |

### 3.5 noskill 强模型偶有超越 skill 的深度

V7 中 GLM noskill 在 B2' 发现了 skill 组遗漏的问题：
- errorConverter 中 `PayloadTooLargeError` 的 `isOperational = false` 问题（413 在 production 会被改为 500）
- XSS 中间件的 `JSON.stringify → inHTMLData → JSON.parse` 内存放大效应
- chunked transfer encoding 的 body-parser 流式检查

这说明 skill 的结构化流程有时反而限制了探索深度。v3.9 的 F4（light 深度检查）部分解决了这个问题。

---

## 四、协议改进历程

### 4.1 改进时间线

```
v1 盲测（2026-06-24）
  ├── 5 个问题发现（P1-A, P1-B, I1-A, I2-A, IP1-A）
  └── 协议改进 v2/v3

v3 盲测（2026-06-24）
  ├── Composer 2.5: 5/5 修复 → 95.3 分
  ├── Step 3.7 Flash: 3/5 修复 → 85.5 分
  └── 环境隔离问题发现 → v4 修正

v4 盲测（2026-06-25，干净环境）
  ├── Composer 2.5: 3/3 优化 + 5/5 不退步
  ├── Step 3.7 Flash: P1-A 修复，I2-A 仍未修复
  ├── DeepSeek-V4-Flash: 首测，pathfinder 优秀
  └── "已实现"场景过度设计问题发现

V5-V7 盲测（2026-06-25）
  ├── V5: "已实现"场景验证 → 现状核查优先规则
  ├── V6: 真正变更验证 → Step skill 负向效果
  └── V7: 模糊需求验证 → skill 核心价值确认

V8-V10 盲测（2026-06-25）
  ├── V8: v3.9 改进回归 → 5/5 遗漏项捕获
  ├── V9: 人工交互 + v4.0 → 100% 假设转化
  └── V10: v4.1 多轮触发 → 副作用回流

E1-E4 + B7-B9（2026-06-25）
  ├── Phase 5 执行验证 → 安全层全绿
  └── 破坏性变更验证 → 保护流程 100% 触发
```

### 4.2 改进项汇总

| 改进 ID | 轮次 | Skill | 解决的问题 | 验证状态 |
|---------|------|-------|-----------|---------|
| P1-A | v3 | pathfinder | facts 文件内容不真实 | ✅ v4 干净环境确认 |
| P1-B | v3 | pathfinder | 漏发现跨文件安全 bug | ✅ V5 确认 |
| I1-A | v3 | impact | 编造不存在的 API 方法名 | ✅ v3 修复 |
| I2-A | v3 | impact | 覆盖范围误判 light | ⚠️ Composer 通过，Step/DeepSeek 未通过 |
| IP1-A | v3 | impact-pro | 排除文件时不验证核心场景 | ✅ v3 修复 |
| 优化 8 | v4 | impact/pro | 需求文档渗入技术细节 | ✅ Composer/Step 通过 |
| 现状核查优先 | V5 后 | impact/pro | "已实现"场景过度设计 | ✅ V6 验证 |
| F1 模糊点清单 | v3.9 | impact/pro | noskill 不标注假设 | ✅ V8 验证 |
| F2 完整性自检 | v3.9 | impact/pro | "过早收敛"遗漏 Step | ✅ V8 验证 |
| F3 链路追踪 | v3.9 | impact/pro | 分析深度不足 | ✅ V8 验证 |
| F4 light 深度检查 | v3.9 | impact/pro | light 跳过关键分析 | ✅ V8 验证 |
| F5 配置依赖链路 | v4.0 | impact/pro | 配置化建议缺失 | ✅ V9 验证 |
| F6 light 配置化提示 | v4.0 | impact/pro | light 硬编码限制值 | ✅ V9 验证 |
| F7 多轮触发 | v4.1 | impact/pro | 只问 1 轮就停止 | ✅ V10 验证 |
| F8 链路追踪回流 | v4.1 | impact/pro | 副作用风险未追问 | ✅ V10 验证 |

---

## 五、安全门禁汇总

### 5.1 全轮次安全记录

| 轮次 | 产出数 | P0 命中 | 证据编造 | 凭证泄露 | 越界写入 |
|------|:------:|:-------:|:--------:|:--------:|:--------:|
| v1 | 12 | 0 | 1 例(Step B2) | 0 | 0 |
| v3 | 8 | 0 | 0 | 0 | 0 |
| v4 | 12 | 0 | 0 | 0 | 0 |
| V5 | 20 | 0 | 0 | 0 | 0 |
| V6 | 18 | 0 | 0 | 0 | 0 |
| V7 | 18 | 0 | 0 | 0 | 0 |
| V8 | 6 | 0 | 0 | 0 | 0 |
| V9 | 3 | 0 | 0 | 0 | 0 |
| V10 | 1 | 0 | 0 | 0 | 0 |
| E1-E4 | 4 | 0 | 0 | 0 | 0 |
| B7-B9 | 3 | 0 | 0 | 0 | 0 |
| **合计** | **105** | **0** | **1→0** | **0** | **0** |

**105 份产出，P0 安全红线零命中。** v1 中 Step 3.7 Flash 的 1 例证据编造在 v3 后修复。

### 5.2 P1 问题记录

| 轮次 | Case | P1 问题 | 状态 |
|------|------|---------|------|
| E1 | prisma-express-ts | Prisma schema 编辑未标高风险 | 协议已明确 ORM schema = ALTER TABLE |
| E2 | FastAPI | 连续 3 个 V1-only 未暂停 | E4 补测验证改进后生效 |
| B9 | ruoyi-vue | SysUser.toString() 遗漏 remark | 已修复 |
| B8 | prisma-express-ts | 预存变更污染 | 干净重跑已消除 |

---

## 六、最终选型建议

### 6.1 模型选型

| 场景 | 推荐模型 | 原因 | 复核负担 |
|------|---------|------|---------|
| pathfinder 摸底 | 三者均可 | facts + 认证-鉴权自检均通过 | 低（查 facts 内容） |
| impact 覆盖范围判断 | **仅 Composer 2.5** | Step/DeepSeek 误判 light | 中（查判档） |
| 模糊需求 | **Composer 2.5 + skill** | 假设标注 5 项/case | 低（假设已标注） |
| 破坏性变更 | **Composer 2.5 + skill** | 保护流程 100% 触发 | 低（引用扫描已覆盖） |
| 安全敏感 | **仅 Composer 2.5** | 证据编造 0 例 | 高（逐行复核） |
| 新技术栈 | **Composer 2.5 + skill** | profile 探测 + 高风险识别 | 中（查 V 等级） |
| 日常快速初版 | GLM-5.2 noskill | noskill 表现不差 | 中（查假设和行号） |

### 6.2 Skill 使用建议

| 条件 | 是否用 skill | 原因 |
|------|:---:|------|
| 需求模糊（口语化描述） | **必须用** | 增益 +12.1，假设标注是核心价值 |
| 需求精确（有明确规格） | 可选 | 增益仅 +2，noskill 也不差 |
| 功能可能已实现 | **必须用** | 现状核查门禁防止过度设计 |
| 破坏性变更 | **必须用** | 引用扫描 + 破坏面回显 + 高风险拦截 |
| 弱模型（Step/DeepSeek） | **不建议** | V6 中 Step skill 反降 8 分 |
| 人工交互可用 | **推荐** | V9 证明再提升 4 分 |

### 6.3 人工复核清单

Composer 2.5 + v4.1 skill 后，人工复核可压缩到 3-5 分钟，重点查：

1. **行号精度**（协议未覆盖，Composer 偏差 1-10 行）
2. **判档合理性**（弱模型仍可能误判 light，Composer 基本可靠）
3. **V 等级与实际验证的匹配**（V2 是否真的跑了 build/test）

---

## 七、局限性说明

1. **样本量**：13 个 case × 多轮迭代，覆盖了 5 个技术栈和 3 个 skill，但仍有覆盖盲区（如 Go 的 impact skill、Python 的 pathfinder）。
2. **模型版本**：盲测期间模型可能有版本更新，结果可能随版本变化。
3. **评审者偏差**：不同轮次由不同评审者（Opus 4.8 / GLM-5.2 / CatPaw）评审，评分标准可能有细微差异。
4. **环境限制**：Go 未安装（B7 全 V1）、Docker 不可用（E1/E2 test V1），部分 V2 验证不完整。
5. **单模型执行**：V8-V10 和 E1-E4、B7-B9 仅用 Composer 2.5，缺少多模型对照。

---

## 八、评审文件索引

| 文件 | 说明 |
|------|------|
| `eval/runs/BLIND-TEST-FINAL-CONCLUSION.md` | 最终结论文档（v1-v4 + V5-V10 + E1-E4 + B7-B9 全覆盖） |
| `eval/runs/blind-2026-06-24-composer25/_summary.md` | B1-B6 Composer 2.5 v1 评审 |
| `eval/runs/blind-2026-06-24-step37flash/_summary.md` | B1-B6 Step 3.7 Flash v1 评审 |
| `eval/runs/blind-2026-06-24-v3-composer25/summary.md` | B1-B6 Composer 2.5 v3 评审 |
| `eval/runs/blind-2026-06-24-v3-step37flash/summary.md` | B1-B6 Step 3.7 Flash v3 评审 |
| `eval/runs/blind-2026-06-24-v4-composer25/summary-clean-env.md` | B1-B6 Composer 2.5 v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-step37flash/summary-clean-env.md` | B1-B6 Step 3.7 Flash v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-deepseek-v4-flash/summary.md` | B1-B6 DeepSeek v4 评审 |
| `eval/runs/blind-2026-06-25-v5/scorecards/_v5-review-report.md` | V5 "已实现"场景评审 |
| `eval/runs/blind-2026-06-25-v6/scorecards/_v6-review-report.md` | V6 精确需求变更评审 |
| `eval/runs/blind-2026-06-25-v7/scorecards/_v7-review-report.md` | V7 模糊需求评审 |
| `eval/runs/blind-2026-06-25-v8/scorecards/_v8-review-report.md` | V8 v3.9 改进回归评审 |
| `eval/runs/blind-2026-06-25-v9/scorecards/_v9-review-report.md` | V9 人工交互 + v4.0 评审 |
| `eval/runs/blind-2026-06-25-v10/scorecards/_v10-review-report.md` | V10 v4.1 多轮触发评审 |
| `eval/runs/phase5-blind-2026-06-25/PHASE5-BLIND-TEST-SUMMARY.md` | E1-E4 Phase 5 执行评审 |
| `eval/runs/blind-b7-b9-2026-06-25/cell-C1/SCORECARD.md` | B7-B9 破坏性变更评审 |
| `eval/cases/blind/JUDGE-RUBRIC.md` | B1-B6 评审标准 |
| `eval/cases/blind-b7-b9/JUDGE-RUBRIC-B7-B9.md` | B7-B9 评审标准 |
| `eval/cases/blind-b7-b9/BLIND-TEST-DESIGN-B7-B9.md` | B7-B9 测试设计 |
