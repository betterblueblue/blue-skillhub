# Skill 优化验证（R2 → R3 → R4）：Composer 2.5 + Step 3.7 Flash

> 验证目标：确认 Skill 模板优化后，C25 和 S37 的产出质量是否提升。
> R2-R3 测试项目：`test-projects/realworld-express-prisma`（Node/Express/Prisma）
> R4 测试项目：`test-projects/realworld-springboot-java`（Java/Spring Boot/MyBatis）
>
> **R3 已完成。两模型均达 92 分，全部成功标准达成。**
> **R4 已完成。换栈 + 弱引导下 C25=83/B、S37=85/B，跨栈泛化成功但弱引导暴露模板引导力不足。**
> **R5 已完成。O10-O13 修复全面生效：C25=95/A（回到并超过 R3 水平），S37=87/A（§3.2 和 context-pack 修复，但设计解读偏差未解决）。**
> **R6 已完成。O16 完全修复（S37 C1 判 light），O14 部分修复（S37 找不到脚本路径），O13 意外修复（S37 默认 DRAFT）。C25=95/A 不退步，S37=90/A。**
> **R7 已完成。O18 完全修复（_active-state 跟模板），O14 路径修复但 S37 仍未实际执行脚本（"待执行"），O13 回退（S37 重新默认 PUBLISHED）。C25=95/A 不退步，S37=90/A 持平。**

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
├── PROMPT-composer-2.5-r4.md       ← R4 给 Composer 2.5 的执行指令（Java/Spring，口语化弱引导）
├── PROMPT-step-3.7-flash-r4.md     ← R4 给 Step 3.7 Flash 的执行指令（Java/Spring，口语化弱引导）
├── REVIEW.md                       ← R1 vs R2 对比评审手册
├── REVIEW-r3.md                    ← R2 vs R3 对比评审手册（已完成）
├── REVIEW-r4.md                    ← R4 跨栈评审手册（含 Ground Truth）
├── REVIEW-r5.md                    ← R5 O10-O13 修复验证评审手册
├── PROMPT-composer-2.5-r5.md       ← R5 给 Composer 2.5 的执行指令（弱引导，指向新干净环境）
├── PROMPT-step-3.7-flash-r5.md     ← R5 给 Step 3.7 Flash 的执行指令（弱引导，指向新干净环境）
├── PROMPT-composer-2.5-r6.md       ← R6 给 Composer 2.5 的执行指令（弱引导，O14+O16 验证）
├── PROMPT-step-3.7-flash-r6.md     ← R6 给 Step 3.7 Flash 的执行指令（弱引导，O14+O16 验证）
├── REVIEW-r5.md                    ← R5 O10-O13 修复验证评审手册
├── REVIEW-r6.md                    ← R6 O14+O16 修复验证评审手册
├── PROMPT-composer-2.5-r7.md       ← R7 给 Composer 2.5 的执行指令（弱引导，O14+O18 验证）
├── PROMPT-step-3.7-flash-r7.md     ← R7 给 Step 3.7 Flash 的执行指令（弱引导，O14+O18 验证）
└── REVIEW-r7.md                    ← R7 O14+O18 修复确认评审手册

test-projects/
├── realworld-express-prisma/                           ← R1-R3 原始项目（Node/Express/Prisma）
├── realworld-express-prisma-composer-2.5/              ← R1 产出（保留）
├── realworld-express-prisma-composer-2.5-r2/           ← R2 隔离环境
├── realworld-express-prisma-composer-2.5-r3/           ← R3 隔离环境
│   └── change-impact/                                  ← 产出目录（模型执行后生成）
├── realworld-express-prisma-step-3.7-flash/            ← R1 产出（保留）
├── realworld-express-prisma-step-3.7-flash-r2/         ← R2 隔离环境
├── realworld-express-prisma-step-3.7-flash-r3/         ← R3 隔离环境
│   └── change-impact/                                  ← 产出目录（模型执行后生成）
├── realworld-springboot-java/                          ← R4 原始项目（Java/Spring Boot/MyBatis）
├── realworld-springboot-java-composer-2.5/             ← R4 隔离环境
│   └── change-impact/                                  ← 产出目录（模型执行后生成）
└── realworld-springboot-java-step-3.7-flash/           ← R4 隔离环境
    └── change-impact/                                  ← 产出目录（模型执行后生成）
├── realworld-springboot-java-composer-2.5-r5/          ← R5 隔离环境（干净副本）
│   └── change-impact/                                  ← 产出目录（模型执行后生成）
└── realworld-springboot-java-step-3.7-flash-r5/        ← R5 隔离环境（干净副本）
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

---

## 七、第四轮（R4）：Java/Spring 跨栈 + 弱引导

### R4 设计动机

R1-R3 全部在 Node/Express/Prisma 栈上测试，存在两个未验证的问题：

1. **跨栈泛化**：Skill 的 profile（`java-spring-mybatis.md`）、dimensions、模板能否在 Java/Spring/MyBatis 栈上同样有效？
2. **弱引导下的自主性**：R3 的 prompt 给了大量提示（列 20+ skill 文件、提醒 §6/§3.2/_active-state.md、指出涉及哪些层）。去掉这些提示后，Skill 自身的流程能否引导模型完成全部产出？

### R4 测试项目

| 项 | 值 |
|---|---|
| 项目 | `gothinkster/spring-boot-realworld-example-app` |
| 栈 | Spring Boot 2.6.3 + MyBatis 2.2.2 + SQLite + JWT + Flyway + GraphQL (DGS) |
| 构建 | Gradle |
| Java | 11 |
| 架构 | DDD-lite（api → application → core → infrastructure） |
| 与 R1-R3 对比 | 同为 RealWorld (Conduit) API 规范，但技术栈完全不同 |

### R4 Prompt 设计

| 维度 | R3（强引导） | R4（弱引导） |
|---|---|---|
| Skill 文件列表 | 列出 20+ 个文件路径 | 只给 SKILL.md 入口，按索引自行读取 |
| 任务描述 | "涉及多层：Prisma schema 变更、注册流程改动…" | 纯用户口语，不提示涉及哪些层 |
| §6 横切表 | "强制要求…标题不得改名…19 行全部检查" | 不提，靠 Skill 流程 + V10 门禁 |
| §3.2 验证表 | "必须包含…标注【已核实: path:line】" | 不提，靠 Skill 流程 + V3 门禁 |
| _active-state.md | "必做…每次文档状态变化都更新" | 不提，靠 Skill 流程 + V1 门禁 |
| Light/Full 判断 | 明确标注"light"/"full" | 不标，让 Skill Phase 2.5 自行判断 |

### R4 测试场景

| 任务 | 需求原话 | 预期类型 | 涉及层 |
|---|---|---|---|
| Task 2 | "文章列表接口每次都返回完整正文，列表页加载特别慢，能不能列表不返回 body" | Light | MyBatis mapper SQL 片段 + DTO |
| Task 3 | "现在文章一创建就公开了，能不能加个草稿功能，让用户先存草稿，想好了再发布" | Full | Schema(Flyway) → Domain → Mapper(写/读) → DTO → Service → API(新端点) → 权限 → 向后兼容 |

### R4 执行环境

| 模型 | 测试项目路径 | 状态 |
|---|---|---|
| Composer 2.5 | `test-projects/realworld-springboot-java-composer-2.5` | ✅ 就绪 |
| Step 3.7 Flash | `test-projects/realworld-springboot-java-step-3.7-flash` | ✅ 就绪 |

### R4 成功标准

1. **跨栈不崩**：两模型 G1-G4 门禁全 PASS（Skill 能在新栈上运行）
2. **弱引导下自主完成**：§6 横切表、§3.2 验证表、_active-state.md 在无提示情况下被产出
3. **MyBatis 正确性**：识别 XML mapper 模式（非 JPA/注解），mapper 变更点准确
4. **质量不显著退步**：综合得分 ≥ 80（R3 为 92，允许换栈带来一定下降）
5. **两模型差距 ≤ 10 分**（R3 差距为 0，换栈后可能拉大但不应失控）

### R4 结果

| 模型 | R3（强引导） | R4（弱引导） | 降幅 | 等级 |
|------|------------|------------|------|------|
| Composer 2.5 | 92 | 83 | -9 | B |
| Step 3.7 Flash | 92 | 85 | -7 | B |
| 差距 | 0 | -2（S37 领先） | | |

### R4 成功标准达成情况

| # | 标准 | 结果 |
|---|------|------|
| 1 | 跨栈不崩（G1-G4 全 PASS） | ✅ 达成 |
| 2 | 弱引导下自主完成（§6/§3.2/_active-state） | ⚠️ 部分达成（_active-state 改善，§6 仅 S37 通过，§3.2 两模型都遗漏） |
| 3 | MyBatis 正确性（XML mapper 模式） | ✅ 达成 |
| 4 | 质量不显著退步（≥80） | ✅ 达成（C25=83, S37=85） |
| 5 | 两模型差距 ≤ 10 分 | ✅ 达成（差距 2 分） |

> 详细评审见 `REVIEW-r4.md`。

---

## 九、第五轮（R5）：O10-O13 修复验证

### R5 设计动机

R4 暴露的 §3.2 缺失、§6 缺失、context-pack 跳过、设计解读偏差四个问题，通过 O10-O13 修改了 Skill 框架（SKILL.md 强制规则、模板标题强化、references 明确化、phase-1 意图映射）。R5 在**相同弱引导 prompt + 全新干净测试项目副本**下验证修复效果。

### R5 测试环境

| 模型 | 测试项目路径 | 状态 |
|------|------------|------|
| Composer 2.5 | `test-projects/realworld-springboot-java-composer-2.5-r5` | ✅ 干净副本 |
| Step 3.7 Flash | `test-projects/realworld-springboot-java-step-3.7-flash-r5` | ✅ 干净副本 |

### R5 结果

| 模型 | R4 | R5 | 变化 | 等级 |
|------|-----|-----|------|------|
| Composer 2.5 | 83 | **95** | +12 | A |
| Step 3.7 Flash | 85 | **87** | +2 | A |
| 差距 | -2（S37 领先） | +8（C25 领先） | | |

### O10-O13 修复效果

| # | 优化项 | C25 R4→R5 | S37 R4→R5 | 结论 |
|---|--------|-----------|-----------|------|
| O10 | §3.2 API 验证表 | ❌→✅ | ❌→✅ | **两模型都修复** |
| O11 | §6 横切表 | ❌→✅ | ✅→✅ | **C25 修复** |
| O12 | context-pack | ✅→✅ | ❌→✅ | **S37 修复** |
| O13 | 设计意图解读 | ✅→✅ | ❌→❌ | **S37 未修复** |
| Rule 8 | 跑验证脚本 | ❌→✅ | ❌→❌ | **仅 C25 生效** |

### R5 核心发现

1. **C25 完全修复**：R4 暴露的三个问题（§6 缺失、§3.2 缺失、不跑脚本）全部解决，综合分 95，超过 R3 强引导水平（92）
2. **S37 部分修复**：§3.2 和 context-pack 修复，但 O13（设计意图）和 Rule 8（跑脚本）未生效
3. **S37 新问题**：C1 误判 full（R4 正确判 light），可能是模板章节结构强制规则导致模型理解为"必须产出完整四文档"
4. **验证脚本 bug 修复**：V10 regex 不兼容 `| ☑ |` 格式（标记两侧有空格），已修复为 `\|[^\|]*[☑☐]\s*\|`

### R5 成功标准达成情况

| # | 标准 | 结果 |
|---|------|------|
| 1 | O10 §3.2 两模型都修复 | ✅ 达成 |
| 2 | O11 §6 C25 修复 | ✅ 达成 |
| 3 | O12 context-pack S37 修复 | ✅ 达成 |
| 4 | O13 设计意图 S37 修复 | ❌ 未达成 |
| 5 | Rule 8 两模型都跑脚本 | ⚠️ 部分达成（仅 C25） |
| 6 | C25 回到 ≥90（A 级） | ✅ 达成（95） |
| 7 | S37 不低于 R4（≥85） | ✅ 达成（87） |

> 详细评审见 `REVIEW-r5.md`。

---

## 八、第四轮优化（O10-O13）：修复弱引导下的模板引导力

### R4 核心发现

R4 暴露的根本问题：**Skill 模板自身的引导力不足，之前靠 prompt 提示兜底。** 去掉 prompt 提示后：

1. **两模型都没跑 `impact_validate.py`** — SKILL.md 没把"跑脚本"做成强制门禁，只在 references 里提了一句
2. **C25 完全自创章节结构** — 没按模板的 `##` 级别节产出，§3.2 和 §6 都丢了
3. **S37 跟了模板但跳过 §3.2** — §3.2 在模板中位于 §3 和 §4 之间，看起来像可跳过的子节
4. **S37 跳过 000-context-pack.md** — 认为 Pathfinder 地图可以替代，phase-4-output.md 没说清 context-pack 是两模式必产出
5. **S37 设计解读偏差** — 用户说"先存草稿，想好了再发布"，S37 默认 PUBLISHED 而非 DRAFT

### 优化措施

| # | 问题 | 修改文件 | 修改内容 |
|---|------|---------|---------|
| O10 | §3.2 验证表弱引导下两模型都遗漏 | `SKILL.md` | 强制规则加第 8 条：Phase 4 输出后必须跑 `impact_validate.py`，有 FAIL 不得提交 |
| O10+ | 同上 | `templates/030-implementation.md` | §3.2 标题改为 `⚠️ 强制必做 — 缺此节 V3 FAIL 阻止提交`，§3 末尾加提醒 |
| O11 | C25 弱引导下遗漏 §6 横切表 | `SKILL.md` | 强制规则 8 + Phase 4 必产出清单明确列出 `## 6. 横切关注点` 为必含节 |
| O11+ | 同上 | `SKILL.md` | Phase 4 加"写每份文档前必须先 Read 对应模板，按模板章节结构产出，不得自创章节编号" |
| O12 | S37 跳过 000-context-pack.md | `references/phase-4-output.md` | context-pack 说明改为"light 和 full 模式均必产出" |
| O12+ | 同上 | `scripts/impact_validate.py` | V1 检查在 light 模式下对缺 context-pack 报 WARN |
| O13 | S37 设计解读偏差（默认 PUBLISHED） | `references/phase-1-intent.md` | 新增"用户意图→设计假设映射"节，列出常见口语化模式及正确推断 |

### 验证

用 R4 产出测试 `impact_validate.py`，确认门禁能捕获 R4 暴露的所有问题：

| 产出 | 门禁 | 结果 |
|------|------|------|
| C25 C2（缺 §6） | V10 | ✅ FAIL — "missing §6 横切关注点 section" |
| S37 C2（缺 §3.2） | V3 | ✅ FAIL — "no §3.2 API 方法验证 table" |
| S37 C2（缺 context-pack） | V1 | ✅ FAIL — "Missing required file: 000-context-pack.md" |
| S37 C1（light 缺 context-pack） | V1 | ✅ WARN — "context-pack is required for both modes" |
| 现有 17 个测试 | — | ✅ 全部通过 |

---

## 十、第六轮（R6）：O14+O16 修复验证

### R6 设计动机

R5 后实施了 O14（强制跑脚本门禁）和 O16（读路径 SQL 判 light 规则）。R6 在相同弱引导 prompt + 全新干净测试项目副本下验证修复效果。

### R6 结果

| 模型 | R5 | R6 | 变化 | 等级 |
|------|-----|-----|------|------|
| Composer 2.5 | 95 | **95** | 0 | A |
| Step 3.7 Flash | 87 | **90** | +3 | A |
| 差距 | +8（C25 领先） | +5（C25 领先） | | |

### O14+O16+O13 修复效果

| # | 优化项 | C25 | S37 | 结论 |
|---|--------|-----|-----|------|
| O14 | 跑验证脚本 | ✅→✅ | ❌→⚠️ | **部分修复**：S37 知道要跑了，但找不到脚本路径 |
| O16 | C1 判 light | ✅→✅ | ❌→✅ | **完全修复**：R5 误判 full，R6 正确判 light |
| O13 | 设计意图（DRAFT） | ✅→✅ | ❌→✅ | **意外修复**：可能是 LLM 非确定性 |

### R6 核心发现

1. **O16 完全修复**：S37 C1 正确判为 light，产出 040-light.md
2. **O14 部分修复**：S37 尝试跑脚本但找不到——SKILL.md 里 `scripts/impact_validate.py` 路径有歧义，S37 从 skill 目录理解，实际在仓库根目录
3. **O13 意外修复**：S37 R6 默认 DRAFT（R5 默认 PUBLISHED），但 R5→R6 间未修改 O13 相关文件，可能是非确定性
4. **C25 零退步**：O14+O16 未引入任何退步
5. **S37 剩余问题**：V7 覆盖分析缺失（C1 FAIL）、_active-state.md 不跟模板、GraphQL 仍排除

### R6 成功标准达成情况

| # | 标准 | 结果 |
|---|------|------|
| 1 | O16 S37 C1 判 light | ✅ 达成 |
| 2 | O14 S37 跑脚本 | ⚠️ 部分达成（知道要跑，但找不到脚本） |
| 3 | C25 不退步（≥95） | ✅ 达成（95） |
| 4 | S37 不低于 R5（≥87） | ✅ 达成（90） |
| 5 | 两模型差距缩小 | ✅ 达成（R5 差 8 分，R6 差 5 分） |

> 详细评审见 `REVIEW-r6.md`。

---

## 十一、第七轮（R7）：O14+O18 修复确认

### R7 设计动机

R6 后实施了 O14（脚本从根目录 `scripts/` 移到 `skills/impact/scripts/`，消除路径歧义）和 O18（_active-state.md 纳入模板结构强制规则）。R7 在相同弱引导 prompt + 全新干净测试项目副本下验证修复效果。

### R7 结果

| 模型 | R6 | R7 | 变化 | 等级 |
|------|-----|-----|------|------|
| Composer 2.5 | 95 | **95** | 0 | A |
| Step 3.7 Flash | 90 | **90** | 0 | A |
| 差距 | +5（C25 领先） | +5（C25 领先） | | |

### O14+O18+O13 修复效果

| # | 优化项 | C25 | S37 | 结论 |
|---|--------|-----|-----|------|
| O14 | 脚本路径+执行 | ✅→✅ | ⚠️→⚠️ | **路径修复，执行未修复**：S37 路径正确了但仍标"待执行" |
| O18 | _active-state 模板格式 | ✅→✅ | ⚠️→✅ | **完全修复**：R6 自创格式，R7 跟模板 |
| O16 | C1 判 light | ✅→✅ | ✅→✅ | 持续有效 |
| O13 | 设计意图（DRAFT） | ✅→✅ | ✅→❌ | **回退**：R6 默认 DRAFT，R7 回到 PUBLISHED |

### R7 核心发现

1. **O18 完全修复**：S37 的 _active-state.md 在 C1 和 C2 中都严格跟了模板格式
2. **O14 路径修复但执行未修复**：脚本移到 skill 目录后路径正确了，但 S37 标注"待执行"未实际运行。问题从"找不到"变成了"找得到但不跑"
3. **O13 回退**：S37 C2 重新默认 PUBLISHED，证实 R6 的 DRAFT 修复是非确定性的
4. **S37 C1 内容质量提升**：新增覆盖范围分析表（可能通过 V7）和判档决策表（可能通过 V4），但因未跑脚本无法确认
5. **C25 零退步**：O14+O18 未引入任何退步
6. **S37 C2 导航行错误**：所有 C2 文档导航行含不存在的 060/090 链接且标注"(light 模式)"，是模板复制粘贴错误

### R7 成功标准达成情况

| # | 标准 | 结果 |
|---|------|------|
| 1 | O18 S37 _active-state 跟模板 | ✅ 达成 |
| 2 | O14 S37 脚本路径正确 | ✅ 达成 |
| 3 | O14 S37 实际执行脚本 | ❌ 未达成（"待执行"） |
| 4 | C25 不退步（≥95） | ✅ 达成（95） |
| 5 | S37 不低于 R6（≥90） | ✅ 达成（90） |

### 后续优化建议

| # | 问题 | 建议措施 |
|---|------|---------|
| O19 | S37 脚本"待执行"未实际运行 | SKILL.md Phase 4 加"禁止写'待执行'"，_active-state 模板"最近验证"节加禁止值 |
| — | O13 非确定性 | 无法在 skill 层面解决，接受 |
| — | S37 C2 导航行错误 | 模板导航行加条件注释 |

> 详细评审见 `REVIEW-r7.md`。

---

## 十二、最终结论

### 优化 loop 收尾

R1-R7 共 7 轮验证，O1-O18 共 18 项优化措施。**主力模型 Composer 2.5 已稳定在 95/A，优化 loop 收尾。** Step 3.7 Flash 的剩余问题（脚本执行、O13 非确定性）不再投入。

### 全历程分数变化

| 轮次 | 栈 | 引导 | C25 | S37 | 差距 | 关键优化 |
|------|-----|------|-----|-----|------|---------|
| R1 | Node/Express | 强引导 | 86 | 90 | -4 | 基线建立 |
| R2 | Node/Express | 强引导 | 86 | 87 | -1 | O1-O4（§3.2/§6 门禁） |
| R3 | Node/Express | 强引导 | 92 | 92 | 0 | O5-O9（V10/_active-state/Prisma 参考） |
| R4 | Java/Spring | 弱引导 | 83 | 85 | -2 | 跨栈+弱引导，暴露模板引导力不足 |
| R5 | Java/Spring | 弱引导 | 95 | 87 | +8 | O10-O13（§3.2/§6/context-pack 强制规则） |
| R6 | Java/Spring | 弱引导 | 95 | 90 | +5 | O14-O16（脚本门禁/读路径 SQL 判 light） |
| R7 | Java/Spring | 弱引导 | 95 | 90 | +5 | O14+O18（脚本路径澄清/_active-state 模板强制） |

### Composer 2.5（主力模型）最终状态

- **综合分 95/A**，从 R1 的 86 提升 9 分
- R4 弱引导+跨栈一度降到 83，R5 后稳定在 95
- 所有门禁通过，脚本正常执行，设计方案稳定（DRAFT）
- **结论：Skill 优化对 C25 完全生效，弱引导下不依赖 prompt 提示即可高质量完成**

### Step 3.7 Flash 最终状态

- **综合分 90/A**，从 R1 的 90 持平
- O10-O12（§3.2/§6/context-pack）和 O16（判 light）和 O18（_active-state 模板）均已修复
- 剩余问题：脚本不实际执行（O19 未做）、O13 设计意图非确定性、GraphQL 排除偏好
- **结论：S37 有改善但剩余问题属 LLM 行为层面，skill 框架层面已做到能做的极限**

### 优化措施全览

| 阶段 | 优化项 | 影响文件 | 效果 |
|------|--------|---------|------|
| R2 | O1-O4 | 030 模板/020 模板/phase-4-output/impact_validate.py | §3.2 和 §6 门禁建立 |
| R3 | O5-O9 | impact_validate.py/phase-4-output/020 模板/PROMPT | V10 横切表 FAIL/_active-state 检查/Prisma 参考 |
| R5 | O10-O13 | SKILL.md/030 模板/phase-4-output/phase-1-intent | 弱引导下强制规则：§3.2/§6/context-pack/意图映射 |
| R6 | O14-O16 | SKILL.md/phases-detail/_active-state 模板 | 脚本门禁/读路径 SQL 判 light |
| R7 | O14+O18 | SKILL.md/scripts 路径迁移/_active-state 模板规则 | 脚本路径澄清/_active-state 模板强制 |

### 已接受的限制

| 问题 | 原因 | 接受理由 |
|------|------|---------|
| S37 脚本不执行 | LLM 对"Phase 4 当场跑完"理解不足 | O19 可修但不再投入 |
| S37 O13 设计意图非确定性 | LLM 非确定性，skill 层面无法解决 | C25 稳定 DRAFT 已够 |
| S37 GraphQL 排除 | 设计偏好，非错误 | 接受差异 |
| S37 C2 导航行错误 | 模板复制粘贴 | 低优先级 |
