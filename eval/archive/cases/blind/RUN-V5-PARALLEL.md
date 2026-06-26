# V5 并行执行指南

> 本文件说明如何使用并行环境执行 V5 盲测。
> 6 个 cell 各有独立测试项目副本，可同时并行执行。

---

## 一、场景分布分析

### 1.1 四个 Case 的复杂度梯度

| Case | Skill | 技术栈 | 复杂度 | 关键挑战 | Skill 增益点 |
|------|-------|--------|--------|---------|-------------|
| B3 | impact-pro | Node/Prisma | **低** | phone 字段在 schema.prisma 中**已存在**（`phone String? @unique`）；真正考验是现状核查——模型是否发现字段已经有了 | Phase 2 现状核查；避免重复造轮子 |
| B6 | pathfinder | Node/Prisma | **中** | JWT 认证链路跨 5+ 文件（controller → service → token.service → middleware/auth → config/passport） | 证据标签诚实性；盲区标注；Mermaid 图准确性 |
| B1 | impact | Java/Spring | **中高** | "每次接口请求"听起来全覆盖，实际 `@Log` 注解只覆盖标注的 Controller；耗时需在过滤器/拦截器层记录而非 AOP；Excel 导出也要加字段 | Phase 2.5 全量词核查；引用链反查；判档 light/full |
| B2 | impact | Java/Spring | **高** | 安全敏感变更；需确认实际加密方式（可能不是纯 MD5）；存量 MD5 用户兼容方案；登录流程改动 | 安全约束；凭证脱敏；存量数据处理；回滚方案 |

### 1.2 分布评估

**是否有简单复杂高低搭配？** 有，但"简单"端偏弱。

- B3 是最接近"简单"的 case，但它不是单纯的简单任务——phone 字段已存在这个事实让它变成了一个**现状核查测试**。无 skill 的模型可能直接提"新增字段"方案而不发现字段已经有了；有 skill 的模型通过 Phase 2 现状核查应该能发现。
- B2 是最复杂的 case，安全 + 兼容性双重挑战。
- B1 和 B6 在中间，分别测不同维度（覆盖范围缺口 vs 认证链路 trace）。

**覆盖的维度**：

| 维度 | 覆盖情况 |
|------|---------|
| Skill 类型 | impact ×2, impact-pro ×1, pathfinder ×1 — 均衡 |
| 技术栈 | Java/Spring ×2, Node/Prisma ×2 — 均衡 |
| 复杂度梯度 | 低(B3) → 中(B6) → 中高(B1) → 高(B2) — 有梯度 |
| 场景类型 | 现状核查(B3) + 认知地图(B6) + 功能增强(B1) + 安全变更(B2) — 类型多样 |
| 隐藏陷阱 | 已有字段(B3) + 链路分散(B6) + 覆盖范围缺口(B1) + 加密方式待确认(B2) — 各不相同 |

**缺失的场景类型**：
- ❌ 纯简单场景（如"改一个文案"或"加一个配置项"）—— V5 不包含，因为 skill 在这类场景的增益预期最小，对核心假设的验证贡献不大
- ❌ 前端主导变更 —— V5 不包含，因为现有 case 都以后端为主

**结论**：当前 4 个 case 的分布合理，复杂度梯度从低到高覆盖，每个 case 测的维度不重复。如果后续想补充"skill 是否在简单场景过度设计"的对比，可以另开一组小规模测试。

---

## 二、并行环境准备

### 2.1 目录结构

```
eval/runs/blind-2026-06-25-v5/
├── cell-C1/                    # Opus 4.6 无 skill
│   └── test-projects/
│       ├── prisma-express-ts/  # 独立副本（~800KB）
│       └── ruoyi-vue/          # 独立副本（~8MB）
├── cell-C2/                    # Opus 4.6 有 skill
│   └── test-projects/
│       ├── prisma-express-ts/
│       └── ruoyi-vue/
├── cell-C3/                    # Composer 2.5 无 skill
│   └── test-projects/...
├── cell-C4/                    # Composer 2.5 有 skill
│   └── test-projects/...
├── cell-C5/                    # GLM-5.2 无 skill
│   └── test-projects/...
├── cell-C6/                    # GLM-5.2 有 skill
│   └── test-projects/...
├── scorecards/                 # 24 张评审评分卡
└── _summary.md                 # 结论报告
```

每个 cell 的 test-projects 是独立副本，6 个 cell 可以同时跑，互不干扰。

Skill 文件（`skills/` 目录）是共享的，所有有 skill 组都从同一位置 Read，保证协议版本一致。

### 2.2 准备步骤

```bash
# 1. 运行准备脚本（创建 6 个独立环境）
./eval/scripts/prepare-v5-parallel.sh

# 2. 验证环境
ls eval/runs/blind-2026-06-25-v5/cell-C*/test-projects/
# 应该看到 6 个 cell，每个都有 prisma-express-ts 和 ruoyi-vue

# 3. 记录当前 git commit（用于评分卡的 skill_commit 字段）
git rev-parse HEAD
```

### 2.3 执行 6 个 cell

6 个 prompt 文件可以同时发给对应模型，并行执行：

| Cell | Prompt 文件 | 发给谁 |
|------|------------|--------|
| C1 | `PROMPT-opus-v5-noskill.md` | Opus 4.6 |
| C2 | `PROMPT-opus-v5-skill.md` | Opus 4.6 |
| C3 | `PROMPT-composer-v5-noskill.md` | Composer 2.5 |
| C4 | `PROMPT-composer-v5-skill.md` | Composer 2.5 |
| C5 | `PROMPT-glm-v5-noskill.md` | GLM-5.2 |
| C6 | `PROMPT-glm-v5-skill.md` | GLM-5.2 |

每个 prompt 包含：
- 4 个 case（B6 → B1 → B2 → B3）
- cell 专属的测试项目路径
- 有 skill 组：Read SKILL.md + 完整 Phase 流程 + 归档步骤
- 无 skill 组：极简指令，直接分析源码 + 输出文档

### 2.4 跑完后

```bash
# 检查所有 cell 的产出
for cell in C1 C2 C3 C4 C5 C6; do
  echo "=== cell-$cell ==="
  find "eval/runs/blind-2026-06-25-v5/cell-$cell/test-projects/*/change-impact/v5-*/" -type f 2>/dev/null | head -20
done
```

---

## 三、盲评准备

### 3.1 重命名为匿名 cell

跑分完成后，把 6 个 cell 的产出目录重命名为随机字母：

```bash
# 生成随机映射（示例，实际映射随机且不透露）
# cell-C1 → cell-A
# cell-C2 → cell-F
# cell-C3 → cell-C
# cell-C4 → cell-D
# cell-C5 → cell-B
# cell-C6 → cell-E

# 记录映射关系到本地文件（评审完成后才揭晓）
echo "C1=A" > eval/runs/blind-2026-06-25-v5/.cell-mapping.txt
echo "C2=F" >> eval/runs/blind-2026-06-25-v5/.cell-mapping.txt
# ...
```

### 3.2 生成评审 prompt

对每个 case × 每个 cell = 24 份评审任务，用 `PROMPT-judge-v5.md` 模板生成。

评审者（GLM-5.2）在独立会话中逐份打分，输出评分卡 JSON 到 `eval/runs/blind-2026-06-25-v5/scorecards/`。

---

## 四、完整执行流程

```
Step 0: 前置检查
  □ E1-E4 + S1-S3 + Q1-Q18 优化已全部实施 ✅
  □ sync_templates.py --check 通过 ✅
  □ skill_commit 记录（git HEAD）

Step 1: 准备并行环境
  □ 运行 prepare-v5-parallel.sh
  □ 验证 6 个 cell 目录创建成功

Step 2: 并行执行 6 个 cell（同时发给 3 个模型）
  □ C1: 发 PROMPT-opus-v5-noskill.md 给 Opus 4.6
  □ C2: 发 PROMPT-opus-v5-skill.md 给 Opus 4.6
  □ C3: 发 PROMPT-composer-v5-noskill.md 给 Composer 2.5
  □ C4: 发 PROMPT-composer-v5-skill.md 给 Composer 2.5
  □ C5: 发 PROMPT-glm-v5-noskill.md 给 GLM-5.2
  □ C6: 发 PROMPT-glm-v5-skill.md 给 GLM-5.2

Step 3: 盲评准备
  □ 把 6 个 cell 的产出目录重命名为 cell-A 到 cell-F（随机映射）
  □ 记录映射关系（评审完成后揭晓）

Step 4: 评审
  □ 用 PROMPT-judge-v5.md 模板生成 24 份评审 prompt
  □ GLM-5.2 在独立会话中逐份打分
  □ 输出 24 张评分卡 JSON 到 scorecards/

Step 5: 揭盲与统计
  □ 揭晓 cell 字母映射
  □ 填写评分卡的 runner_model / skill_condition / dim6_used
  □ 计算 pairwise 对比（见 BLIND-TEST-V5-DESIGN.md §6.1）
  □ 生成结论报告 _summary.md
```
