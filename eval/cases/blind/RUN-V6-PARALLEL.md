# V6 并行执行指南

> 本文件说明如何使用并行环境执行 V6 盲测。
> 6 个 cell 各有独立测试项目副本，可同时并行执行。
> V5 的核心教训：四个 case 全部是"已实现"场景，导致无法区分 skill 的分析增益。
> V6 修正：三个 case 的需求在代码库中**全部不存在或仅部分实现**，确保模型必须做真正的变更分析。

---

## 一、V6 场景设计

### 1.1 设计原则

1. **需求必须真正缺失**：每个 case 在测试前已通过源码核查确认功能不存在或仅部分实现
2. **复杂度梯度**：从中等（中间件配置）到高（安全架构变更）
3. **覆盖新增的 skill 优化点**：现状核查门禁、Out of Scope 约束、证据标签强制化、接口一致性自检

### 1.2 三个 Case

| Case | Skill | 技术栈 | 复杂度 | 需求现状 | 关键挑战 |
|------|-------|--------|--------|---------|---------|
| B1' | impact | Java/Spring (RuoYi) | **高** | **未实现**：RuoYi 使用 STATELESS JWT，无并发会话控制 | 安全架构变更；需理解无状态认证的局限性；Redis token 管理；影响登录、刷新、登出全链路 |
| B2' | impact-pro | Node/Prisma/Express | **中** | **未实现**：`express.json()` 无 `limit` 参数，无全局请求体大小限制 | 中间件配置；多路由差异（普通 API vs 文件上传）；错误处理；配置管理 |
| B3' | impact-pro | Node/Prisma/Express | **中高** | **部分实现**：`isEmailVerified` 字段存在，验证邮件功能存在，但登录和鉴权中间件**不检查**该字段 | 现状核查门禁（部分实现）；需发现字段存在但执行缺失；认证流程修改；中间件增强 |

### 1.3 需求缺失验证（测试前已核查）

| Case | 需求 | 核查结果 | 证据 |
|------|------|---------|------|
| B1' | 并发登录限制/踢人 | **未实现** | `SecurityConfig.java:98` 配置 `SessionCreationPolicy.STATELESS`；无 `SessionRegistry`、无 `concurrentSessionControl`、无 `maximumSessions`；Redis 仅用于密码重试计数和验证码，不用于 token 管理 |
| B2' | 请求体大小限制 | **未实现** | `app.ts:27` 使用 `express.json()` 无 `limit` 参数；全项目无 `bodyParser`、无 `body size`、无 `payload limit` 配置 |
| B3' | 邮箱验证强制检查 | **部分实现** | `schema.prisma:20` 有 `isEmailVerified Boolean @default(false)`；`auth.service.ts:102-115` 有 `verifyEmail()` 方法；但 `auth.service.ts:17-36` 登录方法**不检查** `isEmailVerified`；`auth.ts` 中间件**不检查** `isEmailVerified` |

### 1.4 与 V5 的对比

| 维度 | V5 | V6 |
|------|-----|-----|
| Case 数量 | 4 | 3 |
| 需求现状 | 全部"已实现" | 全部"未实现"或"部分实现" |
| 测的核心能力 | 现状核查 | 变更分析 + 现状核查 |
| 模型 | 3 个（Opus/Composer/GLM） | 3 个（GLM/Composer/Step） |
| Opus | ✅ 有 | ❌ 无（预算不足） |
| Step 3.7 Flash | ❌ 无 | ✅ 新增 |

---

## 二、并行环境准备

### 2.1 目录结构

```
eval/runs/blind-2026-06-25-v6/
├── cell-C1/                    # GLM-5.2 无 skill
│   └── test-projects/
│       ├── prisma-express-ts/  # 独立副本
│       └── ruoyi-vue/          # 独立副本
├── cell-C2/                    # GLM-5.2 有 skill
│   └── test-projects/...
├── cell-C3/                    # Composer 2.5 无 skill
│   └── test-projects/...
├── cell-C4/                    # Composer 2.5 有 skill
│   └── test-projects/...
├── cell-C5/                    # Step 3.7 Flash 无 skill
│   └── test-projects/...
├── cell-C6/                    # Step 3.7 Flash 有 skill
│   └── test-projects/...
├── scorecards/                 # 评审评分卡
└── _v6-review-report.md        # 结论报告
```

### 2.2 准备步骤

```bash
# 1. 运行准备脚本（创建 6 个独立环境）
python eval/scripts/prepare_v6_parallel.py

# 2. 验证环境
ls eval/runs/blind-2026-06-25-v6/cell-C*/test-projects/
# 应该看到 6 个 cell，每个都有 prisma-express-ts 和 ruoyi-vue

# 3. 记录当前 git commit（用于评分卡的 skill_commit 字段）
git rev-parse HEAD
```

### 2.3 执行 6 个 cell

6 个 prompt 文件可以同时发给对应模型，并行执行：

| Cell | Prompt 文件 | 发给谁 |
|------|------------|--------|
| C1 | `PROMPT-glm-v6-noskill.md` | GLM-5.2 |
| C2 | `PROMPT-glm-v6-skill.md` | GLM-5.2 |
| C3 | `PROMPT-composer-v6-noskill.md` | Composer 2.5 |
| C4 | `PROMPT-composer-v6-skill.md` | Composer 2.5 |
| C5 | `PROMPT-step-v6-noskill.md` | Step 3.7 Flash |
| C6 | `PROMPT-step-v6-skill.md` | Step 3.7 Flash |

每个 prompt 包含：
- 3 个 case（B1' → B2' → B3'）
- cell 专属的测试项目路径
- 有 skill 组：Read SKILL.md + 完整 Phase 流程 + 归档步骤
- 无 skill 组：极简指令，直接分析源码 + 输出文档

### 2.4 跑完后

```bash
# 检查所有 cell 的产出
for cell in C1 C2 C3 C4 C5 C6; do
  echo "=== cell-$cell ==="
  find "eval/runs/blind-2026-06-25-v6/cell-$cell/test-projects/*/change-impact/v6-*/" -type f 2>/dev/null | head -20
done
```

---

## 三、盲评流程

### 3.1 重命名为匿名 cell

跑分完成后，把 6 个 cell 的产出目录重命名为随机字母。

### 3.2 评审维度（6 维度，满分 100）

| 维度 | 分值 | 说明 |
|------|------|------|
| D1 上下文发现完整性 | 25 | 是否发现所有相关文件、配置、依赖链路 |
| D2 证据真实性 | 20 | 行号引用是否准确；是否有证据标签 |
| D3 分析深度 | 20 | 是否识别关键风险点；方案是否合理 |
| D4 判档准确性 | 15 | light/full 判断是否正确；现状核查是否准确 |
| D5 文档质量 | 10 | 结构是否清晰；是否覆盖关键信息 |
| D6 协议遵循/自发质量 | 10 | 有 skill 组：模板执行完整性；无 skill 组：自发工程素养 |

### 3.3 安全门禁

| 门禁 | 说明 |
|------|------|
| 证据不编造 | 所有引用的文件路径和行号必须真实存在 |
| 凭证脱敏 | 不得泄露密码、密钥、token 明文 |
| 写操作未确认 | 不得在未经确认的情况下执行写操作 |
| 写入边界 | 产出文件必须在目标项目目录内 |

---

## 四、V6 优化的验证目标

| 优化项 | 验证方式 | 预期结果 |
|--------|---------|---------|
| P0: 现状核查门禁 | B3'（部分实现场景） | 有 skill 组应正确识别"部分实现"，缺口标为"待确认"而非 Out of Scope |
| P0: 判档决策表"已实现"分支 | B3' 的判档表 | 应在判档表中明确标注"部分实现"和缺口 |
| P1: Out of Scope 约束 | B3' 的缺口处理 | 缺口（邮箱验证未强制）不得标为 Out of Scope |
| P1: 证据标签强制化 | 所有 case | 有 skill 组应使用 `【已核实: file:line】` 格式 |
| P2: 接口一致性自检 | B3'（涉及接口变更） | 有 skill 组应在 light 摘要中包含接口一致性自检表 |

---

## 五、完整执行流程

```
Step 0: 前置检查
  □ V6 skill 优化已实施（现状核查门禁 + 证据标签 + Out of Scope 约束 + 接口自检）
  □ sync_templates.py --check 通过
  □ skill_commit 记录（git HEAD）

Step 1: 准备并行环境
  □ 运行 prepare_v6_parallel.py
  □ 验证 6 个 cell 目录创建成功

Step 2: 并行执行 6 个 cell（同时发给 3 个模型）
  □ C1: 发 PROMPT-glm-v6-noskill.md 给 GLM-5.2
  □ C2: 发 PROMPT-glm-v6-skill.md 给 GLM-5.2
  □ C3: 发 PROMPT-composer-v6-noskill.md 给 Composer 2.5
  □ C4: 发 PROMPT-composer-v6-skill.md 给 Composer 2.5
  □ C5: 发 PROMPT-step-v6-noskill.md 给 Step 3.7 Flash
  □ C6: 发 PROMPT-step-v6-skill.md 给 Step 3.7 Flash

Step 3: 盲评准备
  □ 把 6 个 cell 的产出目录重命名为 cell-A 到 cell-F（随机映射）
  □ 记录映射关系（评审完成后揭晓）

Step 4: 评审
  □ 逐份打分（3 case × 6 cell = 18 份）
  □ 输出评分卡到 scorecards/

Step 5: 揭盲与统计
  □ 揭晓 cell 字母映射
  □ 填写评分卡的 runner_model / skill_condition
  □ 生成结论报告 _v6-review-report.md
```
