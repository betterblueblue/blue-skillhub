# 多模型对比 E2E 验证：执行说明

> 验证 Composer 2.5、Kimi K2.6、GLM 5.1、Step 3.7 Flash 四个模型在 Pathfinder + Impact Skill 上的执行质量。
> 产出路径：`eval/runs/e2e-model-comparison-2026-06-28/`

---

## 一、已准备好的环境

### 测试项目副本（4 份，源码完全一致）

| 模型 | 测试项目路径 | 状态 |
|------|------------|------|
| Composer 2.5 | `test-projects/realworld-express-prisma-composer-2.5` | ✅ 就绪（无 node_modules，无历史产出） |
| Kimi K2.6 | `test-projects/realworld-express-prisma-kimi-k2.6` | ✅ 就绪 |
| GLM 5.1 | `test-projects/realworld-express-prisma-glm-5.1` | ✅ 就绪 |
| Step 3.7 Flash | `test-projects/realworld-express-prisma-step-3.7-flash` | ✅ 就绪 |

> 原始项目 `test-projects/realworld-express-prisma` 保留不动，作为参照基线。

### PROMPT 文件（4 份，内容除路径外完全一致）

| 文件 | 用途 |
|------|------|
| `PROMPT-composer-2.5.md` | 复制 `---` 之后内容发给 Composer 2.5 |
| `PROMPT-kimi-k2.6.md` | 复制 `---` 之后内容发给 Kimi K2.6 |
| `PROMPT-glm-5.1.md` | 复制 `---` 之后内容发给 GLM 5.1 |
| `PROMPT-step-3.7-flash.md` | 复制 `---` 之后内容发给 Step 3.7 Flash |

### 评审手册

| 文件 | 用途 |
|------|------|
| `REVIEW.md` | 四个模型都跑完后，用这份手册逐项评审对比 |

---

## 二、执行步骤

### 第 1 步：分发 PROMPT（可并行）

分别在四个模型的对话窗口中，打开对应的 PROMPT 文件，复制 `---` 分隔线之后的全部内容，粘贴给模型执行。

- **可以并行跑**：四个模型用各自独立的测试项目副本，互不干扰。
- **工作目录统一**：四个 PROMPT 的工作目录都是 `e:\agent\blue-skillhub`，skill 文件共享。
- **预计耗时**：每个模型需要执行 3 个任务（Pathfinder 摸底 + 2 个 Impact 分析），强模型预计 30-60 分钟，弱模型可能更长或中途失败。

### 第 2 步：确认产出就位

每个模型跑完后，检查产出文件是否齐全：

```bash
# Composer 2.5
dir /s /b test-projects\realworld-express-prisma-composer-2.5\change-impact

# Kimi K2.6
dir /s /b test-projects\realworld-express-prisma-kimi-k2.6\change-impact

# GLM 5.1
dir /s /b test-projects\realworld-express-prisma-glm-5.1\change-impact

# Step 3.7 Flash
dir /s /b test-projects\realworld-express-prisma-step-3.7-flash\change-impact
```

每个模型应产出：
- `_project-map.md` + `_project-map/facts/scan.json` + `_project-map/facts/git.json`（Pathfinder）
- `e2e/C1/` 下至少 3 个文件（Impact light）
- `e2e/C2/` 下至少 5 个文件（Impact full）

> **注意**：弱模型可能无法完成全部 3 个任务，或产出不完整。这本身就是评审数据——记录它在哪一步失败、失败原因，用于评估 Skill 闸门对弱模型的拦截效果。

### 第 3 步：评审对比

打开 `REVIEW.md`，按第十章「评审执行流程」逐步执行：

1. 对每个模型逐项检查（文件存在性 → Ground Truth 对照 → 不确定项分类 → L1 交接 → 文档一致性）
2. 填写各模型的评分汇总表
3. 填写跨模型对比矩阵（8.1 综合评级矩阵）
4. 逐维度对比分析（8.2.1~8.2.7）
5. 给出最佳模型推荐（8.3）
6. 按「评审报告模板」输出最终报告

---

## 三、目录结构总览

```
eval/runs/e2e-model-comparison-2026-06-28/
├── README.md                    ← 本文件（执行说明）
├── PROMPT-composer-2.5.md       ← 给 Composer 2.5 的执行指令
├── PROMPT-kimi-k2.6.md          ← 给 Kimi K2.6 的执行指令
├── PROMPT-glm-5.1.md            ← 给 GLM 5.1 的执行指令
├── PROMPT-step-3.7-flash.md     ← 给 Step 3.7 Flash 的执行指令
└── REVIEW.md                    ← 跨模型对比评审手册

test-projects/
├── realworld-express-prisma/                    ← 原始项目（保留不动）
├── realworld-express-prisma-composer-2.5/       ← Composer 2.5 的隔离环境
│   └── change-impact/                           ← 产出目录（模型执行后生成）
├── realworld-express-prisma-kimi-k2.6/          ← Kimi K2.6 的隔离环境
│   └── change-impact/
├── realworld-express-prisma-glm-5.1/            ← GLM 5.1 的隔离环境
│   └── change-impact/
└── realworld-express-prisma-step-3.7-flash/     ← Step 3.7 Flash 的隔离环境
    └── change-impact/
```

---

## 四、评审重点说明

### 4.1 为什么四份 PROMPT 内容几乎一样

为了公平对比，四个模型收到的指令完全一致，只有测试项目路径不同。这样差异完全来自模型自身能力，而非指令偏差。

### 4.2 为什么不共享一份测试项目

如果四个模型写同一个 `change-impact/` 目录，产出会互相覆盖。隔离副本确保每个模型的产出独立可查。

### 4.3 为什么不需要 node_modules

PROMPT 明确要求"只读分析，不修改源代码，不进入 Phase 5 执行"。模型只需要读源码和跑扫描脚本，不需要 `npm install` 或启动服务。`pf_scan.py` 本身也跳过 `node_modules`。

### 4.4 Ground Truth 在哪里

`REVIEW.md` 第三章是 Ground Truth，直接从源码提取的确定性事实。四个副本源码完全一致，所以用同一份 Ground Truth 评审四个模型。第三章 3.6 节「负向事实表」列出了当前项目中不存在的依赖（无邮件、无队列、无缓存、无 RBAC），专门用来检查模型是否编造了不存在的功能。

### 4.5 评审能回答什么问题

| 问题 | 看哪里 |
|------|--------|
| 哪个模型 Pathfinder 摸底最准？ | REVIEW 8.1 任务 1 行 + 8.2.1 事实准确性 |
| 哪个模型 Impact 分析最全？ | REVIEW 8.1 任务 3 行 + 8.2.3 影响覆盖 |
| 哪个模型不确定项分类最规范？ | REVIEW 8.2.4 |
| 哪个模型 L1 交接做得最好？ | REVIEW 8.2.5 |
| 哪个模型脚本闸门执行最严格？ | REVIEW 8.2.6 |
| 是否存在"适合 A 不适合 B"的分化？ | REVIEW 8.3 是否存在分化表 |
| 能不能混合编排（A 摸底 + B 分析）？ | REVIEW 8.3 混合编排行 |
| **弱模型与强模型差距多大？** | REVIEW 8.3 S37 能力下限行 + 8.4 差异亮点 |
| **Skill 闸门能否拦截弱模型的错误产出？** | REVIEW 9.4 S37 能力下限 + P-V1~V3 |

---

## 五、注意事项

1. **skill 文件来源**：PROMPT 要求模型从仓库目录 `skills/` 读取 skill 文件，不使用已安装副本。四个模型共享同一份 skill 文件，保证 skill 版本一致。

2. **Python 环境**：`pf_scan.py`、`pf_git.py`、`pf_validate.py` 需要 Python 3。确认执行环境中 Python 可用。

3. **Git 元数据**：测试项目副本不是独立 git 仓库（在 blue-skillhub 仓库内）。`pf_git.py` 会检测到这一点，产出 `is_independent_repo: false`，不会泄漏父仓库 HEAD。这是预期行为，四个模型一致。

4. **产出清理**：如需重跑某个模型，删除其 `change-impact/` 目录后重新发送 PROMPT 即可：
   ```bash
   rmdir /s /q test-projects\realworld-express-prisma-composer-2.5\change-impact
   ```

5. **评审独立性**：建议评审由未参与执行的 agent 或人工完成，避免"自己改自己评"。

6. **弱模型预期**：Step 3.7 Flash 是四个模型中能力最弱的。它可能在中途失败、产出不完整、或事实错误较多。这些都是有价值的评审数据，不要因为产出不完整就跳过评审——它的失败模式本身就是 Skill 健壮性的测试结果。
