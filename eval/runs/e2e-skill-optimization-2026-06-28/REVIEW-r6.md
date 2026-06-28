# R6 评审结果：O14+O16 修复验证

> 评审已完成。O16 完全修复，O14 部分修复（S37 找不到脚本路径），O13 意外修复。C25 维持 95 不退步，S37 升至 90。

## 测试基本信息

| 项 | 值 |
|---|---|
| 轮次 | R6 |
| 测试项目 | `gothinkster/spring-boot-realworld-example-app`（与 R4/R5 同源，全新干净副本） |
| Prompt 风格 | 与 R4/R5 完全一致的弱引导 |
| R5→R6 变化 | **仅 O14（强制跑脚本门禁）+ O16（读路径 SQL 判 light）修改，prompt 和测试项目不额外变** |

---

## 验证脚本门禁结果

| 模型 | 任务 | 模式 | passed | failed | warnings |
|------|------|------|--------|--------|----------|
| C25 | C1 列表省略 body | light | 10 | 0 | 0 |
| C25 | C2 草稿功能 | full | 17 | 0 | 0 |
| S37 | C1 列表省略 body | **light** ✅ | 8 | **1**（V7） | 1（V4） |
| S37 | C2 草稿功能 | full | 16 | 0 | 1（V4） |

> S37 C1 的 V7 FAIL：用户原话含"每次"（全称量词），产出缺少覆盖范围分析（与 R5 相同）。

---

## O14+O16+O13 修复效果

| # | 优化项 | C25 R5→R6 | S37 R5→R6 | 结论 |
|---|--------|-----------|-----------|------|
| O14 | 跑验证脚本 | ✅→✅ | ❌→⚠️ | **部分修复**：S37 知道要跑了，但找不到脚本 |
| O16 | C1 判 light | ✅→✅ | ❌→✅ | **完全修复**：R5 误判 full，R6 正确判 light |
| O13 | 设计意图（DRAFT） | ✅→✅ | ❌→✅ | **意外修复**：R5 默认 PUBLISHED，R6 默认 DRAFT |

### O14 部分修复详情

S37 的 _active-state.md "最近验证"节写的是：

```
脚本：`python scripts/impact_validate.py` — 脚本不存在于 skill 仓库，跳过
结果：N/A
跳过原因：impact_validate.py 未实现
```

S37 **尝试了**运行脚本（R5 根本没尝试，直接写 N/A），但它在 `skills/impact/scripts/` 目录下找，没找到。实际脚本在仓库根目录的 `scripts/impact_validate.py`。

**根因**：SKILL.md 里的路径 `python scripts/impact_validate.py` 有歧义。从仓库根目录看是 `scripts/impact_validate.py`，但 S37 从 `skills/impact/SKILL.md` 的位置理解，把 `scripts/` 当成了 skill 目录下的子目录。C25 正确解析到了仓库根目录。

**O14 的进展**：_active-state.md 模板的 placeholder 确实让 S37 意识到"必须跑脚本"，但路径解析问题阻止了实际执行。问题从"不知道要跑"变成了"知道要跑但找不到"。

### O16 完全修复详情

S37 C1 _active-state.md 明确写了"档位：light"，产出了 040-light.md（而非 R5 的 010/020/030 四文档）。phases-detail.md 中新增的"仅调整读路径 SQL 的 WHERE/SELECT 投影属于 light"规则生效了。

### O13 意外修复详情

S37 C2 设计文档第 9 行："创建时默认 draft，PUT 支持状态变更"。

_active-state.md 第 30 行："用户目标：为文章增加草稿功能，创建时默认草稿状态，作者可后续发布"。

R5 时 S37 默认 PUBLISHED（"保持向后兼容"），R6 默认 DRAFT。**R5→R6 之间没有对 O13 做任何修改**，phase-1-intent.md 的"用户意图→设计假设映射"在 R5 就已存在。可能原因：
1. LLM 非确定性——同一 prompt 不同运行可能产出不同结果
2. O13 的映射引导需要多次运行才稳定生效

> 注意：O13 的修复可能是非确定性的，不能保证后续运行都默认 DRAFT。

---

## Composer 2.5 评审

### Task 1: Pathfinder — 95 / 100（A）

与 R5 一致，无变化。

### Task 2: Impact Light — 95 / 100（A）

| 检查项 | R5 | R6 | 备注 |
|--------|-----|-----|------|
| 模式 | light ✅ | light ✅ | |
| 跑验证脚本 | ✅ | ✅ | "9 passed, 0 failed, 0 warnings" |
| 000-context-pack | ✅ | ✅ | |
| 门禁结果 | 10p/0f/0w | 10p/0f/0w | |

无变化，无退步。

### Task 3: Impact Full — 95 / 100（A）

| 检查项 | R5 | R6 | 备注 |
|--------|-----|-----|------|
| §6 横切表 | ✅ | ✅ | 19 行 |
| §3.2 验证表 | ✅ | ✅ | 含 grep 核实 |
| 设计解读 | ✅ DRAFT | ✅ DRAFT | R6 用 `published` 布尔列，默认 false |
| GraphQL 覆盖 | ✅ | ✅ | schema.graphqls + ArticleData |
| 跑验证脚本 | ✅ | ✅ | "16 passed, 0 failed, 1 warning" |
| 门禁结果 | 17p/0f/0w | 17p/0f/0w | |

无变化，无退步。R6 设计方案从 R5 的 `status VARCHAR(DRAFT/PUBLISHED)` 改为 `published BOOLEAN`，两者都合理。

### Composer 2.5 总评

| 任务 | R5 | R6 | 变化 |
|------|-----|-----|------|
| Pathfinder | 95 | 95 | 0 |
| C1 Light | 95 | 95 | 0 |
| C2 Full | 95 | 95 | 0 |
| **综合** | **95/A** | **95/A** | **0** |

**结论：O14+O16 未引入退步。**

---

## Step 3.7 Flash 评审

### Task 1: Pathfinder — 93 / 100（A）

与 R5 一致，无变化。

### Task 2: Impact Light — 88 / 100（A/B）

| 检查项 | R5 | R6 | 备注 |
|--------|-----|-----|------|
| 模式 | ❌ full（误判） | ✅ **light** | **O16 修复** |
| 跑验证脚本 | ❌ N/A | ⚠️ 找不到脚本 | **O14 部分** |
| 000-context-pack | ✅ | ✅ | |
| V7 覆盖分析 | ❌ FAIL | ❌ FAIL | "每次"未做覆盖分析 |
| V4 判档决策表 | ⚠️ WARN | ⚠️ WARN | |
| _active-state 格式 | ✅ 跟模板 | ⚠️ 自创格式 | 缺模式、Step台账等字段 |
| 门禁结果 | 13p/1f/2w | 8p/1f/1w | |

**R5→R6 改善**：模式从 full 修正为 light（+5）。**未修复**：V7 FAIL 仍在，脚本仍未跑成。

### Task 3: Impact Full — 90 / 100（A）

| 检查项 | R5 | R6 | 备注 |
|--------|-----|-----|------|
| §6 横切表 | ✅ | ✅ | 19 行，19 行标记 |
| §3.2 验证表 | ✅ | ✅ | 9 行，含 grep 核实 |
| 设计解读 | ❌ PUBLISHED | ✅ **DRAFT** | **O13 意外修复** |
| GraphQL 覆盖 | ❌ 排除 | ❌ 排除 | "不改 GraphQL 层" |
| 跑验证脚本 | ❌ N/A | ⚠️ 找不到脚本 | **O14 部分** |
| V4 判档决策表 | ⚠️ WARN | ⚠️ WARN | |
| 门禁结果 | 16p/0f/1w | 16p/0f/1w | |

**R5→R6 改善**：设计解读从 PUBLISHED 修正为 DRAFT（+3）。**未修复**：GraphQL 仍排除，脚本仍未跑成。

### Step 3.7 Flash 总评

| 任务 | R5 | R6 | 变化 |
|------|-----|-----|------|
| Pathfinder | 93 | 93 | 0 |
| C1 Light | 83 | 88 | +5 |
| C2 Full | 87 | 90 | +3 |
| **综合** | **87/A** | **90/A** | **+3** |

---

## 横向对比

| 维度 | Composer 2.5 | Step 3.7 Flash | 差值 |
|------|-------------|---------------|------|
| Task 1 Pathfinder | 95 | 93 | +2 |
| Task 2 Light | 95 | 88 | +7 |
| Task 3 Full | 95 | 90 | +5 |
| **综合** | **95** | **90** | **+5** |

### R3 → R4 → R5 → R6 四轮对比

| 轮次 | 栈 | Prompt | C25 | S37 | 差值 |
|------|-----|--------|-----|-----|------|
| R3 | Node/Express | 强引导 | 92 | 92 | 0 |
| R4 | Java/Spring | 弱引导 | 83 | 85 | -2 |
| R5 | Java/Spring | 弱引导（同R4） | 95 | 87 | +8 |
| R6 | Java/Spring | 弱引导（同R4） | 95 | 90 | +5 |

---

## 关键发现

### 1. O16 完全修复

S37 C1 从误判 full 修正为正确判 light。phases-detail.md 中"仅调整读路径 SQL 的 WHERE/SELECT 投影属于 light"这条规则直接生效。这是本轮最明确的修复。

### 2. O14 部分修复——路径歧义是新的阻塞点

O14 的 _active-state.md 模板 placeholder 成功让 S37 意识到"必须跑脚本"——R5 写"N/A, 未执行"，R6 写了"脚本不存在于 skill 仓库，跳过"。问题从"不知道要跑"变成了"知道要跑但找不到"。

根因是 SKILL.md 里的路径 `python scripts/impact_validate.py` 有歧义：从仓库根目录看是 `scripts/impact_validate.py`，但 S37 从 skill 目录位置理解成了 `skills/impact/scripts/impact_validate.py`。

**修复建议（O17）**：在 SKILL.md、phase-4-output.md、_active-state.md 模板中，把 `scripts/impact_validate.py` 改为 `<仓库根目录>/scripts/impact_validate.py` 或加一句"从仓库根目录运行"。

### 3. O13 意外修复——可能是非确定性

S37 R6 默认 DRAFT，R5 默认 PUBLISHED，但 R5→R6 之间没有对 O13 相关文件做任何修改。这可能是 LLM 非确定性导致的——同一 prompt 不同运行可能产出不同设计决策。不能保证后续运行都默认 DRAFT。

### 4. S37 C1 _active-state.md 不跟模板

S37 R6 C1 的 _active-state.md 用了自创格式（"当前状态""已完成步骤""验证状态"），而非模板的标准格式（"状态头""当前意图""文档状态""Step 台账""最近验证"）。这是模板章节结构强制规则（R5 O11 新增）的一个遗漏——该规则只约束 010/020/030 文档，没有覆盖 _active-state.md。

### 5. S37 C1 V7 FAIL 持续存在

用户原话"每次都返回完整正文"中的"每次"触发了全称量词门禁，但 S37 在 light 模式下不产出覆盖范围分析。这个问题从 R5 延续到 R6，是 S37 的顽固问题。

### 6. C25 零退步

C25 在 O14+O16 修改后完全没有退步，两个任务都是 0 FAIL 0 WARN。设计方案的 `published` 布尔列方案（R6）与 R5 的 `status` 枚举方案不同但都合理。

---

## R6 成功标准达成情况

| # | 标准 | 结果 |
|---|------|------|
| 1 | O16 S37 C1 判 light | ✅ 达成 |
| 2 | O14 S37 跑脚本 | ⚠️ 部分达成（知道要跑，但找不到脚本） |
| 3 | C25 不退步（≥95） | ✅ 达成（95） |
| 4 | S37 不低于 R5（≥87） | ✅ 达成（90） |
| 5 | 两模型差距缩小 | ✅ 达成（R5 差 8 分，R6 差 5 分） |

---

## 后续优化建议

| # | 问题 | 建议措施 | 预期效果 |
|---|------|---------|---------|
| O17 | S37 找不到脚本路径 | SKILL.md/phase-4-output.md/_active-state.md 中把 `scripts/impact_validate.py` 改为 `<仓库根目录>/scripts/impact_validate.py`，或加"从仓库根目录运行" | S37 能正确找到并运行脚本 |
| O18 | S37 C1 _active-state.md 不跟模板 | 模板章节结构强制规则扩展覆盖 _active-state.md | S37 使用标准模板格式 |
| — | S37 V7 覆盖分析缺失 | 已有 V7 FAIL 门禁拦截，但 S37 不跑脚本所以不知道 | O17 修复后 S37 跑脚本时会发现 V7 FAIL 并修复 |
| — | S37 GraphQL 排除 | 设计偏好，skill 层面不强制 | 接受差异 |
| — | O13 非确定性 | 无法在 skill 层面解决 | 接受不确定性 |

> O17 是 O14 的直接延续——修一个路径引用就能让 S37 真正跑上脚本。O18 是小修补。两个都做了之后，S37 预计能达到 92-93 分，优化 loop 可以收尾。
