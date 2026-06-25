# V7 并行执行指南 — 模糊需求盲测

> 本文件说明如何使用并行环境执行 V7 盲测。
> 6 个 cell 各有独立测试项目副本，可同时并行执行。

---

## 一、V7 核心目标

### 1.1 要回答的问题

V6 发现：精确 prompt 下 skill 增益微弱（+2 分），但耗时翻倍。这是否因为 prompt 过于精确，架空了 skill 的核心价值（澄清模糊需求）？

V7 假设：**模糊 prompt 下，skill 的澄清能力才能真正体现价值**。noskill 模型必须猜测缺失参数，容易过度设计或遗漏关键点；skill 模型应通过 Phase 3 提问识别模糊点，做出合理假设并标注。

### 1.2 与 V6 的唯一变量

| 维度 | V6 | V7 |
|------|-----|-----|
| 代码库 | 同 | 同（B1'/B2'/B3'） |
| 模型 | 同（GLM/Composer/Step） | 同 |
| Skill 版本 | 同 | 同 |
| **Prompt 精确度** | **精确**（含数值、状态码、技术细节） | **模糊**（只有业务意图 + 一句抱怨） |
| **Skill 组提问处理** | 自动"继续"跳过 | **自行假设并标注 [假设]** |

### 1.3 模糊 prompt 设计

每个 case 的模糊 prompt 删掉以下信息：

| Case | V6 精确版包含但 V7 删掉的信息 |
|------|---------------------------|
| B1' 踢人 | 踢人机制细节、双向覆盖、提示信息 |
| B2' 请求体 | 限制大小（1MB/10MB）、分级限制、状态码（413）、错误消息 |
| B3' 邮箱验证 | 拦截点（登录/接口）、提示语、状态码 |

V7 用户原话：

| Case | V7 模糊 prompt |
|------|---------------|
| B1' | "我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录" |
| B2' | "API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧" |
| B3' | "注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧" |

### 1.4 方案 C：假设标注规则

skill 组 prompt 中增加以下指令：

> 如果 skill 在 Phase 3 提出澄清问题，你不需要等待用户回答。请自行做出**合理假设**，并明确标注为 `[假设]`。例如："[假设] 限制大小为 1MB，文件上传为 10MB"。然后基于假设继续分析。

评审时重点考察：
1. skill 是否识别出了模糊点
2. skill 的假设是否合理
3. noskill 模型是否也做出了同样的假设（隐式地）
4. 假设遗漏导致的分析偏差

---

## 二、并行环境准备

### 2.1 目录结构

```
eval/runs/blind-2026-06-25-v7/
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
└── _v7-review-report.md        # 结论报告
```

### 2.2 准备步骤

```bash
# 1. 运行准备脚本（创建 6 个独立环境，复用 V5 干净源副本）
python eval/scripts/prepare_v7_parallel.py

# 2. 验证环境
ls eval/runs/blind-2026-06-25-v7/cell-C*/test-projects/
# 应该看到 6 个 cell，每个都有 prisma-express-ts 和 ruoyi-vue

# 3. 记录当前 git commit
git rev-parse HEAD
```

### 2.3 执行 6 个 cell

| Cell | Prompt 文件 | 发给谁 |
|------|------------|--------|
| C1 | `PROMPT-glm-v7-noskill.md` | GLM-5.2 |
| C2 | `PROMPT-glm-v7-skill.md` | GLM-5.2 |
| C3 | `PROMPT-composer-v7-noskill.md` | Composer 2.5 |
| C4 | `PROMPT-composer-v7-skill.md` | Composer 2.5 |
| C5 | `PROMPT-step-v7-noskill.md` | Step 3.7 Flash |
| C6 | `PROMPT-step-v7-skill.md` | Step 3.7 Flash |

---

## 三、评审重点

### 3.1 新增评审维度：假设质量

在 V6 评审维度基础上，V7 新增"假设质量"维度：

| 维度 | 分值 | 说明 |
|------|------|------|
| D1 上下文发现完整性 | 20 | 是否发现所有相关文件、配置、依赖链路 |
| D2 证据真实性 | 15 | 行号引用是否准确；是否有证据标签 |
| D3 分析深度 | 20 | 是否识别关键风险点；方案是否合理 |
| D4 判档准确性 | 10 | light/full 判断是否正确 |
| D5 假设质量（新增） | 15 | 模糊点的识别完整性；假设合理性；标注规范性 |
| D6 文档质量 | 10 | 结构是否清晰；是否覆盖关键信息 |
| D7 协议遵循/自发质量 | 10 | 有 skill 组：模板执行完整性；无 skill 组：自发工程素养 |

### 3.2 假设质量评分标准

| 分值 | 标准 |
|------|------|
| 15 | 识别出所有关键模糊点，假设合理，全部标注 [假设] |
| 10 | 识别出大部分模糊点，假设基本合理，部分标注 |
| 5 | 识别出少数模糊点，假设有偏差，标注不完整 |
| 0 | 未识别模糊点，直接猜测不标注，或假设明显不合理 |

### 3.3 预期结果

| 对比 | V6（精确 prompt） | V7（模糊 prompt）预期 |
|------|------------------|---------------------|
| skill vs noskill 增益 | +2 分（微弱） | **+10~15 分**（显著） |
| noskill 主要问题 | 无（prompt 太精确） | 过度设计 / 遗漏关键参数 / 假设不合理 |
| skill 主要优势 | 证据标签、结构化 | **模糊点识别、合理假设、防御性检查** |

如果 V7 结果符合预期，证明 skill 的核心价值在于"澄清模糊需求"而非"结构化精确需求"。
如果 V7 结果不符预期（skill 增益仍然微弱），则需要重新评估 skill 的定位。

---

## 四、完整执行流程

```
Step 0: 前置检查
  □ V6 skill 优化已实施（现状核查门禁 + 证据标签 + Out of Scope 约束 + 接口自检）
  □ skill_commit 记录（git HEAD）

Step 1: 准备并行环境
  □ 运行 prepare_v7_parallel.py
  □ 验证 6 个 cell 目录创建成功

Step 2: 并行执行 6 个 cell（同时发给 3 个模型）
  □ C1: 发 PROMPT-glm-v7-noskill.md 给 GLM-5.2
  □ C2: 发 PROMPT-glm-v7-skill.md 给 GLM-5.2
  □ C3: 发 PROMPT-composer-v7-noskill.md 给 Composer 2.5
  □ C4: 发 PROMPT-composer-v7-skill.md 给 Composer 2.5
  □ C5: 发 PROMPT-step-v7-noskill.md 给 Step 3.7 Flash
  □ C6: 发 PROMPT-step-v7-skill.md 给 Step 3.7 Flash

Step 3: 评审
  □ 逐份打分（3 case × 6 cell = 18 份）
  □ 重点考察假设质量
  □ 输出评分卡到 scorecards/

Step 4: 生成结论报告
  □ V6 vs V7 对比分析
  □ _v7-review-report.md
```
