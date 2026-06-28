# Skill 优化验证（第二轮 + 第三轮）：Composer 2.5 + Step 3.7 Flash

> 验证目标：确认 Skill 模板优化后，C25 和 S37 的产出质量是否提升。
> 测试项目：`test-projects/realworld-express-prisma`（多份干净副本，源码完全一致）
>
> **R3 已完成。两模型均达 92 分，全部成功标准达成。**

---

## 一、优化内容回顾

第一轮评审发现 C25 和 S37 的主要失分点集中在 Q2（设计方案深度）和 Q5（验证严谨性）：

| 维度 | C25 R1 | S37 R1 | G52 R1（标杆） | 原因 |
|------|--------|--------|--------------|------|
| Q2 设计方案深度 | 7 | 9 | 9 | C25 缺横切关注点表 |
| Q5 验证严谨性 | 6 | 7 | 9 | C25/S37 均缺方法存在性验证 |

### 优化措施

| # | 文件 | 优化内容 | 预期影响 |
|---|------|---------|---------|
| O1 | `templates/030-implementation.md` | 新增 §3.2「API 方法验证」表，要求记录每个已有方法的 grep 验证结果和异常行为 | Q5↑：方法验证从隐式变为显式强制 |
| O2 | `templates/020-design.md` | §6 横切关注点表加注释：跳过此表 = 提交不完整 | Q2↑：C25 不再遗漏横切表 |
| O3 | `references/phase-4-output.md` | 检查 1/2 措辞强化：验证结果必须写入 §3.2 表，跳过 = 提交不完整 | Q5↑：弱模型不会跳过方法验证 |
| O4 | `scripts/impact_validate.py` | V3 检查从 WARN 升级为 FAIL/WARN：缺 §3.2 表则阻止提交 | 脚本闸门强制拦截 |

---

## 二、已准备好的环境

### 测试项目副本（2 份，源码完全一致，无历史产出）

| 模型 | 测试项目路径 | 状态 |
|------|------------|------|
| Composer 2.5 | `test-projects/realworld-express-prisma-composer-2.5-r2` | ✅ 就绪 |
| Step 3.7 Flash | `test-projects/realworld-express-prisma-step-3.7-flash-r2` | ✅ 就绪 |

### PROMPT 文件

| 文件 | 用途 |
|------|------|
| `PROMPT-composer-2.5-r2.md` | 复制 `---` 之后内容发给 Composer 2.5 |
| `PROMPT-step-3.7-flash-r2.md` | 复制 `---` 之后内容发给 Step 3.7 Flash |

### 评审手册

| 文件 | 用途 |
|------|------|
| `REVIEW.md` | 两模型跑完后，用这份手册逐项评审并对比第一轮 |

---

## 三、执行步骤

### 第 1 步：分发 PROMPT（可并行）

分别在两个模型的对话窗口中，打开对应的 PROMPT 文件，复制 `---` 之后内容执行。

- **可以并行跑**：两个模型用各自独立的测试项目副本，互不干扰。
- **工作目录统一**：`e:\agent\blue-skillhub`，skill 文件共享（已含优化）。
- **预计耗时**：每个模型 30-60 分钟。

### 第 2 步：确认产出就位

```bash
# Composer 2.5
dir /s /b test-projects\realworld-express-prisma-composer-2.5-r2\change-impact

# Step 3.7 Flash
dir /s /b test-projects\realworld-express-prisma-step-3.7-flash-r2\change-impact
```

每个模型应产出：
- `_project-map.md` + `_project-map/facts/scan.json` + `_project-map/facts/git.json`（Pathfinder）
- `e2e/C1/` 下至少 3 个文件（Impact light）
- `e2e/C2/` 下至少 5 个文件（Impact full）

### 第 3 步：评审对比

打开 `REVIEW.md`，按以下顺序评审：

1. 硬性门禁（G1-G4）— 确认无 FAIL
2. 流程合规（G5-G9）— 确认合规不退步
3. 产出质量（Q1-Q6）— 重点对比 Q2 和 Q5 是否提升
4. 优化效果验证（O1-O4）— 逐项确认优化点是否被模型执行
5. Round 1 vs Round 2 对比表

---

## 四、目录结构

```
eval/runs/e2e-skill-optimization-2026-06-28/
├── README.md                       ← 本文件
├── PROMPT-composer-2.5-r2.md       ← R2 给 Composer 2.5 的执行指令
├── PROMPT-step-3.7-flash-r2.md     ← R2 给 Step 3.7 Flash 的执行指令
├── PROMPT-composer-2.5-r3.md       ← R3 给 Composer 2.5 的执行指令
├── PROMPT-step-3.7-flash-r3.md     ← R3 给 Step 3.7 Flash 的执行指令
├── REVIEW.md                       ← R1 vs R2 对比评审手册
└── REVIEW-r3.md                    ← R2 vs R3 对比评审手册（已完成）

test-projects/
├── realworld-express-prisma/                           ← 原始项目（保留不动）
├── realworld-express-prisma-composer-2.5/              ← R1 产出（保留）
├── realworld-express-prisma-composer-2.5-r2/           ← R2 隔离环境
├── realworld-express-prisma-composer-2.5-r3/           ← R3 隔离环境
│   └── change-impact/                                  ← 产出目录（模型执行后生成）
├── realworld-express-prisma-step-3.7-flash/            ← R1 产出（保留）
├── realworld-express-prisma-step-3.7-flash-r2/         ← R2 隔离环境
└── realworld-express-prisma-step-3.7-flash-r3/         ← R3 隔离环境
    └── change-impact/                                  ← 产出目录（模型执行后生成）
```

---

## 六、第三轮（R3）优化

### R2 遗留问题

| 问题 | 影响 | R2 结果 |
|------|------|---------|
| C25 横切表缺失（改名绕过） | Q2 停留在 7 | O2 未生效 |
| 两模型 _active-state.md 缺失 | G8 从 8→4 | 模型方差 |
| S37 §3.2 异常行为 3 处错误 | Q5 停留在 8 | 缺乏 ORM 参考 |

### R3 优化措施

| # | 文件 | 优化内容 | 解决问题 |
|---|------|---------|---------|
| O5 | `scripts/impact_validate.py` | 新增 V10 横切表检查（full 模式 FAIL 门禁） | C25 横切表缺失 |
| O6 | `scripts/impact_validate.py` | V1 新增 _active-state.md WARN 检查 | G8 退步 |
| O7 | `references/phase-4-output.md` | 新增 Prisma ORM 异常行为模式参考表 | S37 异常行为错误 |
| O8 | `templates/020-design.md` | §6 注释增加 ⚠️ 强制要求 + 脚本检查提示 | C25 改名绕过 |
| O9 | `PROMPT-*-r3.md` | 任务 2/3 显式列出 _active-state.md、§6、§3.2 必做 | 模型遗漏产出 |

### R3 结果

| 模型 | R1 | R2 | R3 | R3 变化 |
|------|-----|-----|-----|--------|
| Composer 2.5 | 86/A | 86/A | **92/A** | Q2 7→9, G8 4→8 |
| Step 3.7 Flash | 90/A | 87/A | **92/A** | Q5 8→9, G8 4→8 |

### R3 优化效果

| 优化 | 解决的 R2 问题 | R3 结果 |
|------|---------------|---------|
| O5 V10 横切表 FAIL 门禁 | C25 改名绕过横切表 | ✅ C25 产出 19 行完整表 |
| O6 V1 _active-state.md 检查 | 两模型 G8 退步 -4 | ✅ C1/C2 均产出，G8 恢复 8 |
| O7 Prisma ORM 异常行为参考 | S37 §3.2 有 3 处错误 | ✅ 3 处全部纠正 |
| O8 §6 标题防改名 | C25 改名绕过 | ✅ 标题保持原文 |
| O9 PROMPT 显式提醒 | 模型遗漏产出 | ✅ 全部按要求产出 |

### 三轮质量差距变化

| 模型 | R1 vs G52 | R2 vs G52 | R3 vs G52 |
|------|----------|----------|----------|
| C25 | -10 | -6 | **-4** |
| S37 | -6 | -5 | **-4** |

> 详细评审见 `REVIEW-r3.md`。11 项成功标准全部达成。

---

## 五、评审重点

### 5.1 核心问题

| # | 问题 | 看哪里 |
|---|------|--------|
| Q1 | §3.2 API 方法验证表是否被产出？ | C2 030-implementation.md §3.2 |
| Q2 | 横切关注点表是否被填写？ | C2 020-design.md §6 |
| Q3 | impact_validate.py V3 是否从 WARN 变成 PASS？ | 对话过程 + 脚本输出 |
| Q4 | C25 的 Q2/Q5 是否从 7/6 提升？ | REVIEW 评分对比表 |
| Q5 | S37 的 Q5 是否从 7 提升？ | REVIEW 评分对比表 |
| Q6 | 优化是否引入退步（合规分下降）？ | REVIEW G5-G9 对比 |

### 5.2 与第一轮的对照

第一轮评分基准（见 `eval/runs/e2e-model-comparison-2026-06-28/REVIEW.md` §8.1）：

| 模型 | 门禁 | 合规 (≤40) | 质量 (≤60) | 总分 (≤100) | 等级 |
|------|------|-----------|-----------|------------|------|
| C25 R1 | 全 PASS | 40 | 46 | 86 | A |
| S37 R1 | 全 PASS | 40 | 50 | 90 | A |
| G52 R1（标杆） | 全 PASS | 40 | 56 | 96 | S |

### 5.3 成功标准

- **C25**：总分 ≥ 90（Q2 从 7→≥9，Q5 从 6→≥8）→ 优化有效
- **S37**：总分 ≥ 92（Q5 从 7→≥9）→ 优化有效
- **不退步**：G5-G9 合规分维持 40/40，G1-G4 全 PASS
