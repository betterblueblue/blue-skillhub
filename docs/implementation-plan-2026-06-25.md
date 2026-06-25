# 三个 Skill 综合优化实施计划

> 日期：2026-06-25
> 基线：v3.8.1 协议 + v4 干净环境盲测结论
> 关联文档：
> - [skill-optimization-roadmap-2026-06-25.md](skill-optimization-roadmap-2026-06-25.md)（工程严谨性路线图）
> - [output-quality-review-2026-06-25.md](output-quality-review-2026-06-25.md)（产出质量评估）
> 状态：待审阅

---

## 一、背景

三个 skill（pathfinder、impact、impact-pro）经过 v1-v4 四轮盲测，协议层面已比较扎实。但还有三个维度的改进空间：

1. **工程严谨性**：impact 系列缺脚本闸门、判档推理不透明、执行阶段未盲测
2. **产出质量**：模板混入 agent 语言、编号 bug、内容冗余、受众不分
3. **结构治理**：impact 和 impact-pro 模板已分叉、090 模板硬编码栈特定命令、handoff-contract 规则未落地

### 核心目标：用 skill 驾驭性价比模型

顶尖模型不需要太多约束就能做好，但价格高。开发这些 skill 的目的是：**通过 skill 约束，让 Composer 2.5 这类性价比模型尽可能接近顶尖模型的产出水平，既省钱又保证质量不太差。**

这个目标决定了优化项的优先级标准——不是按绝对质量排，而是按"对普通模型的杠杆效应"排。skill 的收益和模型能力成反比：顶尖模型用 skill 是锦上添花，普通模型用 skill 是雪中送炭。

从 v4 盲测数据看，顶尖模型和普通模型的差距集中在三类：

| 差距类型 | 顶尖模型 | 普通模型 | skill 能否补 |
|---------|---------|---------|:---:|
| 推理深度 | 看到覆盖缺口会改判 full | 能识别但不关联，仍判 light | 补不了推理本身，能暴露给人审（E2） |
| 产出完整度 | 自觉产出完整链路 | DeepSeek 产出 1 个文件就停 | ✅ 能补（E1 强制拦截） |
| 证据精度 | 行号准确 | Composer 偏差 1-10 行 | ✅ 部分能补（E1 抽查） |

**关键边界**：skill 能补"模型不自觉"的短板，补不了"模型不会"的短板。所以优化后的效果是——用 Composer 2.5 + skill，在大多数场景接近顶尖模型水平；在覆盖范围判断等少数推理密集场景，仍需人工兜底或换模型。

本文档把两份评估文档的所有优化项 + 结构治理问题整合成一份可执行的实施计划，按三个板块组织，每项标注涉及文件、验证方式、预估难度和对普通模型的杠杆效应。

---

## 二、优化项总览

"杠杆效应"列说明优化项对驾驭普通模型的直接帮助程度：

- **★★★ 直接补短板**：用脚本/协议强制普通模型做它不自觉做的事（产出完整、脱敏、方法名验证等）
- **★★ 暴露给人审**：把普通模型的推理过程写出来让人兜底（不能让模型变聪明，但能防漏判）
- **★ 防误导 / 减出错**：减少普通模型被错误信息带偏或填错的概率
- **— 不直接影响模型表现**：改善人类可读性或维护成本，不直接影响"普通模型能不能完成任务"

| 板块 | 编号 | 优化项 | 严重度 | 难度 | 杠杆效应 | 依赖 |
|------|------|--------|:------:|:----:|:--------:|------|
| 工程严谨性 | E1 | impact/impact-pro 脚本闸门 | 高 | 中低 | ★★★ | 无 |
| 工程严谨性 | E2 | 判档决策证据化 | 高 | 低 | ★★ | 可选配合 E1 |
| 工程严谨性 | E3 | 弱模型降级策略 | 中 | 低 | ★★★ | 配合 E1 |
| 工程严谨性 | E4 | 行号精度抽查 | 中 | 低 | ★★★ | 配合 E1 |
| 结构治理 | S3 | handoff-contract 地图过期检测落地 | 中 | 低 | ★ | 无 |
| 结构治理 | S1 | 模板同步机制（方案 B） | 高 | 低 | — | 无（基础设施，优先做） |
| 结构治理 | S2 | 090-execution-record 去栈特定命令 | 中 | 低 | — | S1 |
| 产出质量 | Q1 | 020-design.md 编号 bug 修复 | 高 | 低 | ★ | S1 |
| 产出质量 | Q8 | 19 维度 checklist 化 | 中 | 低 | ★ | S1 |
| 产出质量 | Q7 | 三段冗余合并为变更明细表 | 中 | 中 | ★ | S1 |
| 产出质量 | Q11 | 占位符指引 HTML 注释化 | 中 | 低 | ★ | S1 |
| 产出质量 | Q5 | 030-implementation.md 清理 agent 行为指令 | 中 | 低 | ★ | S1 |
| 产出质量 | Q6 | context-pack / design 内容去重 | 中 | 低 | ★ | S1 |
| 产出质量 | Q2 | 040-light.md 拆分人类摘要与 agent 自检 | 高 | 中 | — | S1 |
| 产出质量 | Q3 | 060-preflight.md P0/P1 分表 | 高 | 中 | — | S1 |
| 产出质量 | Q4 | 凭证脱敏警告从模板头部移除 | 中 | 低 | — | S1 |
| 产出质量 | Q9 | 验证等级汇总视图 | 中 | 低 | — | S1 |
| 产出质量 | Q10 | 文档间导航索引 | 中 | 低 | — | S1 |
| 产出质量 | Q12 | 005-change-summary.md 新增 | 中 | 中 | — | S1 |
| 产出质量 | Q13 | _active-state.md 中文化 | 低 | 低 | — | S1 |
| 产出质量 | Q14 | 030 语义约定字段补全 | 低 | 低 | ★ | S1 |
| 产出质量 | Q15 | 上下文预算规则明确化 | 低 | 低 | ★ | S1 |
| 产出质量 | Q16 | pathfinder SVG 预览图删除 | 低 | 低 | — | 无 |
| 产出质量 | Q17 | 非功能需求举例业务化 | 低 | 低 | ★ | S1 |
| 产出质量 | Q18 | 代码风格报告自然语言化 | 低 | 中 | — | S1 |
| 工程严谨性 | E5 | Phase 5 执行阶段盲测 | 高 | 中 | —（验证手段） | E1-E4 |
| 工程严谨性 | E6 | 扩大盲测覆盖面 | 中 | 中 | —（验证手段） | E5 |

**建议执行顺序（按杠杆效应优先）**：

```
第一批（基础设施，为后续铺路）：S1 → S2
  虽然不直接补模型短板，但所有模板改动依赖它

第二批（直接补短板，最高杠杆）：E1 → E2 → E3 → E4
  E1 脚本闸门是核心中的核心，pathfinder 已证明收益
  E2/E3/E4 挂在 E1 上，一起做

第三批（防误导 + 减出错）：S3 → Q1 → Q8 → Q7 → Q11 → Q5 → Q6 → Q14 → Q15 → Q17
  减少普通模型被模板结构带偏或填错的概率

第四批（可读性，不直接影响模型表现）：
  Q2 → Q3 → Q4 → Q9 → Q10 → Q12 → Q13 → Q16 → Q18

第五批（验证效果）：E5 → E6
  E5 以 Composer 2.5 为首要验证模型
```

---

## 三、板块一：结构治理

### S1. 模板同步机制（方案 B）

**现状**：impact 和 impact-pro 的共享模板（000/010/020/030/040/060/090/\_active-state）已经分叉，内容有差异。跨 skill 相对路径引用（`../impact-pro/templates/`）在 Claude Code / Cursor 中不可靠——agent 解析路径时可能相对于用户工作目录而非 skill 目录，且用户可能只装一个 skill。

**做什么**：

1. **建立同步脚本** `scripts/sync_templates.py`（Python，跨平台）：
   - 以 `impact-pro/templates/` 为唯一源
   - 把 8 个共享模板同步到 `impact/templates/`
   - 支持 `--check` 模式：只比对不修改，供 L0 测试调用
   - 同步时自动记录文件 hash 到 `scripts/.template-sync-hash.json`，便于检测手动修改

2. **L0 一致性检查**：在 `skills/impact/tests/run.sh` 和 `skills/impact-pro/tests/run.sh` 中加一步：
   ```bash
   python scripts/sync_templates.py --check
   ```
   不一致时报 FAIL，提示跑同步脚本。

3. **README 补充说明**：在两个 skill 的 README 中注明"共享模板以 impact-pro 为源，修改后跑 `python scripts/sync_templates.py` 同步"。

**涉及文件**：
- `scripts/sync_templates.py`（新建）
- `skills/impact/tests/run.sh`（加检查步）
- `skills/impact-pro/tests/run.sh`（加检查步）
- `skills/impact/README.md`（补同步说明）
- `skills/impact-pro/README.md`（补同步说明）

**验证方式**：
- 跑 `python scripts/sync_templates.py`，确认 impact/templates/ 下 8 个文件和 impact-pro 一致
- 跑 `python scripts/sync_templates.py --check`，确认 exit code = 0
- 手动改 impact 侧一个模板，跑 `--check`，确认报 FAIL
- 跑 L0 测试 `bash skills/impact/tests/run.sh`，确认一致性检查生效

**预估难度**：低。脚本逻辑简单，参考已有 `pf_validate.py` 的结构。

---

### S2. 090-execution-record.md 去栈特定命令

**现状**：`090-execution-record.md` 模板中硬编码了栈特定命令——impact 版本写 `mvn test` / `gradle test` / Flyway / Liquibase，impact-pro 版本写 `ty check` / `alembic`。这和 impact-pro 的栈无关设计矛盾，且模板改一次要同步两处。

**做什么**：

1. 模板中移除所有栈特定命令，改为占位符：
   ```markdown
   | 构建验证 | [项目自带构建命令，如 mvn test / npm test / go test] | |
   | 迁移工具 | [项目迁移工具，如 Flyway / Alembic / Prisma migrate] | |
   ```

2. 栈特定命令的推荐值移到各 skill 的 SKILL.md 或 references：
   - impact：在 `references/phase-5-execution.md` 中列 Java 栈推荐命令
   - impact-pro：在 `profiles/<stack>.md` 中列各栈推荐命令（已有部分，补全即可）

3. 用 S1 同步脚本统一模板。

**涉及文件**：
- `skills/impact-pro/templates/090-execution-record.md`
- `skills/impact/references/phase-5-execution.md`
- `skills/impact-pro/profiles/*.md`（按需补全）

**验证方式**：
- 模板中 grep `mvn`、`ty check`、`alembic`，确认无硬编码
- L0 测试通过

**预估难度**：低。

---

### S3. handoff-contract 地图过期检测落地

**现状**：`skills/pathfinder/references/handoff-contract.md` 定义了地图过期检查规则（对比地图头部 git HEAD 和当前 HEAD），但 impact / impact-pro 的 Phase 2 流程中没有落地这个检查。模型可能用过期地图做分析。

**做什么**：

在 impact / impact-pro 的 Phase 2（项目背景构建）中，如果读取了 `_project-map.md`，强制执行 `check_map_freshness` 步骤：

1. 读取地图头部的 `git HEAD`（或 `facts/git.json` 的 `head_short`）
2. 运行 `git rev-parse --short HEAD` 获取当前 HEAD
3. 如果不一致，在 context-pack 中标注"地图已过期（地图: xxx，当前: yyy）"
4. 提示用户："项目地图可能已过期，建议重新运行 `/pathfinder` 更新，或确认过期部分不影响本次分析"

**涉及文件**：
- `skills/impact/SKILL.md`（Phase 2 加检查步骤）
- `skills/impact-pro/SKILL.md`（同上）
- `skills/impact/references/phase-2-context-discovery.md`（详细规则）
- `skills/impact-pro/references/phase-2-context-discovery.md`（同上）

**验证方式**：
- 在一个项目跑 `/pathfinder` 生成地图，然后 `git commit` 改动 HEAD，再跑 `/impact`，确认 context-pack 中出现过期标注

**预估难度**：低。纯协议改动。

---

## 四、板块二：工程严谨性

### E1. impact / impact-pro 脚本闸门

**现状**：pathfinder 有 `pf_validate.py`（V1-V6 六项检查），在写入 `_project-map.md` 前必须运行，exit code ≠ 0 禁止写入。这是 v4 中最有效的改进之一。但 impact 和 impact-pro 没有类似的输出验证脚本——模型判 light 还是 full、产出文件够不够、需求文档有没有混入技术细节，完全靠模型自觉。DeepSeek 在 B3 产出 1 个混合内容的 context-pack 就交差了，没有任何机制拦截。

**做什么**：

新建 `scripts/impact_validate.py`（两个 skill 共用一份，放 `scripts/` 下），在 Phase 4 文档输出后、提交用户确认前运行。检查项：

| 检查项 | 编号 | 检查内容 | 失败动作 |
|--------|------|---------|---------|
| 文件完整性 | V1 | full 场景产出 000/010/020/030 四个文件；light 场景产出 040-light.md | FAIL，阻止提交 |
| 需求文档边界 | V2 | 010-requirements.md 不含表名、类名、文件路径、代码片段（正则匹配） | WARN，提示移到 020 |
| 方法名标记 | V3 | 030-implementation.md 中引用的已有方法名有 grep 验证标记 | WARN，提示补预检 |
| 判档决策表 | V4 | light/full 定级附了判档决策表（配合 E2） | WARN，提示补表 |
| 凭证脱敏 | V5 | 扫描所有产出文件中的 token/key/password/连接串，确认已脱敏 | FAIL，阻止提交 |
| 行号抽查 | V6 | 从 context-pack / design 中随机抽 3 条行号引用，用 `sed -n 'Xp' file` 验证（配合 E4） | WARN，偏差 > 3 行报 WARN |

脚本调用方式：
```bash
python scripts/impact_validate.py <change-impact/需求名称/> [--mode light|full]
```

在 SKILL.md Phase 4 中加入：
```markdown
### 输出验证（Phase 4 文档输出后、提交用户确认前必须运行）

运行 `python scripts/impact_validate.py <需求目录>` 完成输出验证。
- 任何 FAIL 项：必须修复后重新运行，不得提交用户确认
- 任何 WARN 项：在提交确认时向用户说明，由用户决定是否接受
```

**涉及文件**：
- `scripts/impact_validate.py`（新建）
- `skills/impact/SKILL.md`（Phase 4 加脚本闸门）
- `skills/impact-pro/SKILL.md`（同上）

**验证方式**：
- 在 DeepSeek B3 的产出上跑脚本，确认 V1 报 FAIL（文件不完整）
- 在 Composer B3 的产出上跑脚本，确认全 PASS
- L1 评测中用脚本替代部分人工检查

**预估难度**：中低。pathfinder 的 `pf_validate.py` 已有成熟实现可参考。主要工作量在确定 V2 的正则阈值和 V6 的行号抽查逻辑。

---

### E2. 判档决策证据化

**现状**：优化 7（覆盖范围语义核查）对弱模型不生效——Step 3.7 Flash 和 DeepSeek 都能识别覆盖缺口，但都不会因此改变判档。v4 确认这是模型推理能力的硬限制，协议无法强制模型"推理正确"。

**做什么**：

换思路：不要求模型"推理正确"，而是要求模型"把推理过程写出来让人审查"。在 light/full 定级时强制输出判档决策表：

```markdown
### 判档决策表

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|--------------|---------------|------|---------|
| "每次接口请求" | LogAspect 仅覆盖 @Log 注解接口（grep 确认 N 处） | 约 63 个端点未覆盖 | full |
| "所有用户" | sys_user 表全量查询，无分页限制 | 无分页保护 | full |
```

规则：
- 每行对应用户原话中的一个关键需求描述
- "现有实现覆盖范围"必须基于代码核查填写，不能写"全部覆盖"了事
- "缺口"无缺口写"无"，有缺口必须量化
- 如果"缺口"非空但判 light，表后必须附理由

**涉及文件**：
- `skills/impact/SKILL.md`（Phase 2.5 / 3.5 加表格要求）
- `skills/impact-pro/SKILL.md`（同上）
- `skills/impact/references/phase-3-questioning.md`（详细模板）
- `skills/impact-pro/references/phases-detail.md`（同上）

**验证方式**：
- 跑一个全量词场景（如 B6 的"每次接口请求"），确认产出了判档决策表
- E1 的 V4 检查能拦截缺失的决策表

**预估难度**：低。纯协议改动。

---

### E3. 弱模型降级策略

**现状**：DeepSeek 在 impact/impact-pro 上产出严重不足（B3 只产出 1 个混合内容的文件），但协议没有"产出不足时怎么办"的机制。模型产出 1 个文件就当完成任务了。

**做什么**：

在 Phase 4 文档输出后加产出完整性自检步骤（由 E1 的 V1 检查强制执行）：

```
### 产出完整性自检（Phase 4 文档输出后执行）

如果本次定级为 full，检查以下文件是否都已产出：
- 000-context-pack.md
- 010-requirements.md
- 020-design.md
- 030-implementation.md

如果缺少任一文件：
1. 不得提交用户确认
2. 在已有产出的文件头部标注"产出不完整"
3. 输出提示："本次分析产出不完整，缺少 [文件列表]。
   可能原因：执行模型产出能力有限。
   建议：换更强模型重跑，或人工补齐缺失文档。"
```

**涉及文件**：
- `skills/impact/SKILL.md`（Phase 4 加自检步骤）
- `skills/impact-pro/SKILL.md`（同上）

**验证方式**：
- 用弱模型跑一个 full 场景，确认不完整产出被 E1 V1 拦截

**预估难度**：低。纯协议改动，配合 E1 脚本闸门。

---

### E4. 行号精度抽查

**现状**：Composer 2.5 的行号偏差（1-10 行）是 v4 中唯一未被协议覆盖的人工复核点。Step 3.7 Flash 行号精度极高（零偏差），但 Composer 2.5 仍有偏差。

**做什么**：

在 E1 的 `impact_validate.py` 中加 V6 检查——从 context-pack 或 design 文档中随机抽取 3 条行号引用，用 `sed -n 'Xp' file` 验证行内容是否和文档描述匹配。偏差超过 3 行报 WARN。

行号引用的格式约定（在 SKILL.md 中明确）：
```
【已核实: path/to/file.py:L42】
```
脚本用正则提取 `path:L数字` 模式，随机抽 3 条验证。

**涉及文件**：
- `scripts/impact_validate.py`（V6 检查，随 E1 一起实现）
- `skills/impact/SKILL.md`（明确行号引用格式）
- `skills/impact-pro/SKILL.md`（同上）

**验证方式**：
- 在 Composer B3 产出上跑脚本，确认 V6 能检出偏差行号
- 在 Step B3 产出上跑脚本，确认 V6 零 WARN

**预估难度**：低。随 E1 一起实现。

---

### E5. Phase 5 执行阶段盲测

**现状**：6 个盲测 case（B1-B6）全部只测到 Phase 4（文档输出），Phase 5 实际写操作完全没在盲测中验证。Phase 5 的安全闸在 L1 e2e 中验证过（T07/T09 负向测试 7/7 PASS），但盲测场景下"模型自己判 light 然后就不写代码"的路径没被验证——如果模型错误判 light，Phase 5 的安全闸根本没有机会触发。

**核心验证目标**：验证 **Composer 2.5 + skill 能否在执行阶段也不翻车**。Composer 2.5 是日常想用的性价比模型，盲测要回答的问题是"skill 能不能让它在 Phase 5 也安全执行"，而不是泛泛地测三个模型。Step 3.7 Flash 和 DeepSeek 作为对照组，验证 skill 对不同能力层次模型的兜底效果。

**做什么**：

设计 2-3 个 full 场景的盲测 case，让模型走到实际执行（写代码、跑测试），验证：
- 逐 Step 确认（`确认 Step N`）是否严格执行
- V1-only 连续计数是否触发
- 高风险拦截清单（10 类不可逆操作）是否命中
- 执行记录（`090-execution-record.md`）是否随 Step 补齐
- 模型在 full 场景下是否会"判 full 但偷懒不执行"
- E1 脚本闸门在执行阶段是否生效（产出完整性、凭证脱敏等检查在执行后也要过）

**模型选择**：
- **首要验证**：Composer 2.5（日常主力性价比模型）
- **对照组**：Step 3.7 Flash（验证更弱模型在执行阶段的边界）、DeepSeek-V4-Flash（验证"链路弱"模型在执行阶段是否被 E1 拦截）

case 设计要点：
- 不能太简单（否则判 light 不走 Phase 5）
- 不能太复杂（否则模型跑不完）
- 要有可写操作的测试项目（复用已有 test-projects）

**涉及文件**：
- `eval/cases/` 下的新 case 定义（B7-B9）
- `eval/runs/` 下的跑分记录
- 评审方式从"读产出文件"升级为"读代码改动 + 跑测试"

**验证方式**：
- Composer 2.5 跑完 2-3 个 case，评审代码改动和测试结果
- 确认 `确认 Step N` 严格执行、执行记录随 Step 补齐、E1 脚本闸门在执行后通过
- 对照组验证 skill 兜底效果的分层

**预估难度**：中。需要设计能走到 Phase 5 的 case，准备可写操作的测试项目。

---

### E6. 扩大盲测覆盖面

**现状**：6 个盲测 case，4 个技术栈。impact-pro 的 8 个 Level 1 profile 只有 node-express-prisma（B3）被盲测过。而且 6 个 case 全是"加"场景（加手机号、加耗时、改密码），没有测试过破坏性变更。

**做什么**：

**补技术栈覆盖**：

| 新 case | 技术栈 | 验证目标 |
|---------|-------|---------|
| B7 | Java/Spring/MyBatis（RuoYi） | impact-pro 的 java-spring-mybatis profile 在盲测下的表现 |
| B8 | Go/Gin/GORM | go-gin-gorm profile 在盲测下的表现 |
| B9 | FastAPI/SQLModel | python-fastapi-sqlmodel profile 在盲测下的表现 |

**补变更类型覆盖**：

| 新 case | 变更类型 | 验证目标 |
|---------|---------|---------|
| B10 | 删字段（破坏性变更） | 反向引用检查是否覆盖所有消费者；破坏性请求保护是否触发 |
| B11 | 改 API 契约（重命名字段） | generated client / OpenAPI / SDK 同步检查；消费者协调 |
| B12 | 改状态机（订单状态流转） | 状态机变更影响面分析；跨模块联动 |

**涉及文件**：
- `eval/cases/` 下的新 case 定义
- `eval/runs/` 下的跑分记录

**验证方式**：
- 每个 case 跑完产出评分卡
- 破坏性变更 case 重点关注反向引用检查和破坏性请求保护是否触发

**预估难度**：中。需要找合适的测试项目，设计不预设答案的 case prompt。

---

## 五、板块三：产出结果质量

> 以下所有模板改动遵循 S1 同步机制：先改 `impact-pro/templates/`，再跑 `python scripts/sync_templates.py` 同步到 `impact/templates/`。pathfinder 的模板改动（Q16）不受此机制约束。

### Q1. 020-design.md 编号 bug 修复

**现状**：impact 和 impact-pro 的 `020-design.md` 模板都有两个 `## 2.`：
```
## 2. 当前状态
  ### 数据库 / 代码 / 配置
## 2. 目标状态       ← 编号重复
  ### 数据库 / 代码 / 配置
## 3. 变更细则
```

**做什么**：改为 `## 2. 当前状态` / `## 3. 目标状态` / `## 4. 变更细则`，后续编号顺延。

**涉及文件**：`skills/impact-pro/templates/020-design.md`

**验证方式**：grep `## 2.` 确认只出现一次；L0 测试加编号唯一性检查。

**预估难度**：低。

---

### Q2. 040-light.md 拆分人类摘要与 agent 自检

**现状**：`040-light.md` 定位是"简单改动，一页摘要"，主要读者是人类。但实际混入了大量 agent 语言：定级证据、接口返回检查清单、验证等级 V0-V3 等。非技术 PM 看到这份"摘要"会很困惑。

**做什么**：拆成两部分，用分隔线标注：

```markdown
## 变更摘要（人类阅读）

### 变更概述
[一句话说清楚改了什么]

### 影响范围
[影响哪些系统/模块/用户]

### 回滚方案
[出问题怎么回退]

### 验证结果
[测了什么，过了没]

---
<!-- 以下为 agent 执行检查项，人类读者可跳过 -->

## Agent 自检区

### 定级证据
### 接口返回检查清单
### 验证等级
```

**涉及文件**：`skills/impact-pro/templates/040-light.md`

**验证方式**：人工阅读拆分后的模板，确认上半部分纯业务语言、下半部分 agent 自检。

**预估难度**：中。

---

### Q3. 060-preflight.md P0/P1 分表

**现状**：15 行核对表格全是 `git status --short --branch`、`_active-state.md`、`确认 Step N` 这类术语。主要读者是人类（执行前最后确认），但表达方式完全没考虑人类阅读体验，像一份 ops runbook。

**做什么**：

1. P0 项（必须满足）和 P1 项（建议满足）分成两个表
2. P0 表用人类语言描述，命令放"验证方式"列：

```markdown
## P0 必须满足

| 检查项 | 人类语言描述 | 验证方式 | 结果 |
|--------|------------|---------|------|
| 仓库干净 | 确认代码仓库干净，没有无关改动 | `git status --short --branch` | |
| 写入目标 | 所有写入在目标项目根目录内 | 确认路径在项目根下 | |
| 确认机制 | 当前会话有有效的 Step 确认 | 最近一条用户消息含 `确认 Step N` | |

## P1 建议满足

| 检查项 | 描述 | 验证方式 | 结果 |
|--------|------|---------|------|
| ... | ... | ... | |
```

**涉及文件**：`skills/impact-pro/templates/060-preflight.md`

**验证方式**：人工阅读，确认 P0 表项有人类语言描述。

**预估难度**：中。

---

### Q4. 凭证脱敏警告从模板头部移除

**现状**：`010`、`020`、`030`、`040`、`090` 模板头部都有凭证脱敏警告。对人类读者是噪音——这是协议规则，不是文档内容。

**做什么**：
1. 从所有共享模板头部移除凭证脱敏警告
2. 确认 SKILL.md 强制规则区已有此规则（已有，无需新增）
3. 模板头部只保留 `生成时间 | 版本 | 生成者`

**涉及文件**：`skills/impact-pro/templates/` 下的 010/020/030/040/090

**验证方式**：grep `凭证脱敏` 确认模板中无残留；SKILL.md 中保留。

**预估难度**：低。

---

### Q5. 030-implementation.md 清理 agent 行为指令

**现状**：`030-implementation.md` 混入了 agent 行为指令，如"确认提示：执行前必须逐项询问 `确认执行 Step N？`"和"状态更新：询问确认前更新 `_active-state.md`"。这些是 agent 行为规则，应该在 SKILL.md 里，不应该出现在产出文档模板里。

**做什么**：
1. 从模板中移除"确认提示"和"状态更新"字段
2. Step 模板只保留：维度、文件、操作、影响范围、回滚方式、语义约定、验证方式
3. 确认 SKILL.md 的强制规则区和 Phase 5 执行规则中已有这些行为规则（已有）

**涉及文件**：`skills/impact-pro/templates/030-implementation.md`

**验证方式**：grep `确认提示`、`状态更新` 确认模板中无残留。

**预估难度**：低。

---

### Q6. context-pack / design 内容去重

**现状**：`000-context-pack.md` 的"项目背景摘要"和 `020-design.md` 的"项目背景摘要"/"Context Pack 摘要"几乎是同一份内容的两次拷贝。agent 不清楚以哪个为准，人类也不知道为什么要看两遍。

**做什么**：
1. `020-design.md` 不再重复 context-pack 的文件清单
2. 只写"详见 `000-context-pack.md` 第 4 节"，然后直接进入设计概览和变更细则

**涉及文件**：`skills/impact-pro/templates/020-design.md`

**验证方式**：对比两份模板，确认 design 不再重复 context-pack 的文件清单。

**预估难度**：低。

---

### Q7. 三段冗余合并为变更明细表

**现状**：`020-design.md` 中同一个字段变更出现了三次——当前状态列了表结构，目标状态列了变更后的表结构，变更细则又写了"字段变更：ADD/ALTER/DROP"。读者要在三个地方对照才能理解一个字段变更。

**做什么**：合并为一个变更明细表：

```markdown
### 变更明细

| 表名 | 字段名 | 当前定义 | 变更类型 | 目标定义 | 影响说明 |
|------|--------|---------|---------|---------|---------|
| sys_user | phone | 不存在 | ADD | varchar(20) | 新增字段，无存量数据 |
| sys_user | status | tinyint(4) | ALTER | varchar(20) | 类型变更，需数据迁移 |
```

一行展示一个字段的完整生命周期，消除三段冗余。

对于非 DB 维度的变更（如 API 契约、配置项），同样用明细表格式。

**涉及文件**：`skills/impact-pro/templates/020-design.md`

**验证方式**：人工阅读，确认一个变更只在一处描述。

**预估难度**：中。需要重构模板的变更描述结构。

---

### Q8. 19 维度 checklist 化

**现状**：`020-design.md` 的"横切关注点"节只列了 6 项（安全/缓存/日志/消息队列/事务/国际化），而 `references/dimensions.md` 有 19 项。模型可能只填了 6 项就认为"按需"够了，漏掉缓存、消息队列、事务等维度。

**做什么**：

在"横切关注点"节列出全部 19 维度 checklist，让模型逐项判断：

```markdown
### 横切关注点（逐项判断涉及/不涉及，不涉及的写"不涉及"）

| 维度 | 是否涉及 | 说明 |
|------|---------|------|
| 数据库 | | |
| 代码 | | |
| 接口/契约 | | |
| 配置 | | |
| 凭证/密钥 | | |
| 安全/权限 | | |
| 缓存 | | |
| 存储/文件 | | |
| 消息队列/事件 | | |
| 事务 | | |
| 日志 | | |
| 国际化 | | |
| 监控/告警 | | |
| 文档 | | |
| 测试 | | |
| CI/CD | | |
| 依赖/版本 | | |
| 性能 | | |
| 兼容性 | | |
```

**涉及文件**：`skills/impact-pro/templates/020-design.md`

**验证方式**：确认模板中列出 19 项；E1 的 V2 可加检查"横切关注点是否有遗漏维度"。

**预估难度**：低。

---

### Q9. 验证等级汇总视图

**现状**：验证等级分散在 `030-implementation.md`（每个 Step）、`040-light.md`（整体）、`090-execution-record.md`（每步）中，没有汇总视图。评审者要自己翻三个文档拼图。

**做什么**：

在 `090-execution-record.md` 的收尾检查中增加整体验证等级汇总表：

```markdown
### 整体验证等级汇总

| Step | 验证等级 | 未达 V2/V3 原因 |
|------|---------|----------------|
| Step 1 | V2 | — |
| Step 2 | V1 | DB 环境缺失 |
| Step 3 | V2 | — |
| **整体** | **V1** | **Step 2 仅静态验证** |
```

**涉及文件**：`skills/impact-pro/templates/090-execution-record.md`

**验证方式**：人工阅读，确认有一个汇总表。

**预估难度**：低。

---

### Q10. 文档间导航索引

**现状**：模板里没有"下一步"指引。agent 在长会话中上下文压缩后，只读到产出文件就不知道流程到哪了。`_active-state.md` 的 `current_phase` 字量只对恢复场景有效，不对首次消费有效。

**做什么**：每份文档头部加一个"文档流"小节：

```markdown
> 文档流：000-context-pack → 010-requirements → 020-design → 030-implementation → 060-preflight → 执行
> 当前位置：010-requirements → 下一步：确认本文档后进入 020-design.md
```

**涉及文件**：`skills/impact-pro/templates/` 下的 000/010/020/030/040/060/090

**验证方式**：确认每份模板头部有文档流导航。

**预估难度**：低。

---

### Q11. 占位符指引 HTML 注释化

**现状**：模板里的方括号占位符指引（如 `[用业务语言把要做的功能讲明白...]`）如果模型没删掉，人类读到的就是混着方括号指引的半成品。弱模型很可能不删。

**做什么**：模板中的填写指引用 HTML 注释包裹：

```markdown
<!-- 填写指引：用业务语言把要做的功能讲明白。读的人应该能一句话转述给同事听，不出现表名、类名、文件路径。 -->

## 变更需求
（在这里写）
```

人类在渲染后的 Markdown 中看不到注释，agent 在读取源文件时能看到。

**涉及文件**：`skills/impact-pro/templates/` 下所有含占位符指引的模板

**验证方式**：在 Markdown 渲染器中预览，确认指引不显示；在源文件中确认指引可见。

**预估难度**：低。批量替换即可。

---

### Q12. 005-change-summary.md 新增

**现状**：full 场景下团队 lead 拿到 4 个文档（000/010/020/030），没有一个地方能 30 秒看完变更全貌。没有面向"非技术决策者"的文档。

**做什么**：

新增 `005-change-summary.md`（一页纸变更摘要），纯业务语言，不出现命令、路径、方法名：

```markdown
# 变更摘要

> 生成时间 | 版本 | 生成者

## 变更做了什么
[一段话，业务语言]

## 影响哪些系统
[列出受影响的系统/模块/用户群体]

## 风险是什么
[主要风险，如：需要停服、需要数据迁移、影响线上用户]

## 需要谁配合
[如：需要 DBA 执行迁移脚本、需要前端同步发版]

## 回滚方案
[出问题怎么回退]

## 验证方式
[怎么确认变更成功]
```

在 SKILL.md Phase 4 中，full 场景产出顺序改为：000 → 005 → 010 → 020 → 030。005 在 010 之前产出（基于 context-pack 写摘要，不需要等需求文档）。

**涉及文件**：
- `skills/impact-pro/templates/005-change-summary.md`（新建）
- `skills/impact/SKILL.md`（Phase 4 产出顺序加 005）
- `skills/impact-pro/SKILL.md`（同上）

**验证方式**：full 场景产出含 005；人工阅读确认纯业务语言。

**预估难度**：中。需要新建模板并在 SKILL.md 中调整产出顺序。

---

### Q13. \_active-state.md 中文化

**现状**：`_active-state.md` 是唯一用英文写的模板（头部"Cross-session recovery state"，字段名全英文），和其他中文模板不一致。

**做什么**：
- 头部改为中文："跨会话恢复状态"
- 字段名改为中文：updated_at → 更新时间、pending_step → 待执行步骤、target_project_root → 目标项目根目录
- 或至少在头部加中文说明

注意：`current_phase`、`v1_only_count` 等已被 E1 脚本闸门可能引用的字段名，如果改了中文，需同步更新脚本中的字段引用。建议保留字段名英文、描述中文的折中方案。

**涉及文件**：`skills/impact-pro/templates/_active-state.md`

**验证方式**：人工阅读确认中文化；E1 脚本如引用字段名确认同步。

**预估难度**：低。

---

### Q14. 030 语义约定字段补全

**现状**：`030-implementation.md` 的"语义约定"字段写"已确认定义 / 不涉及 / 未确认"，但没说什么定义。实际含义是"status/enum/常量/错误码/权限名/配置键的语义约定"。

**做什么**：改为"语义约定确认（status/enum/常量/错误码/权限名/配置键）：已确认定义 / 不涉及 / 未确认"

**涉及文件**：`skills/impact-pro/templates/030-implementation.md`

**验证方式**：人工阅读确认字段名补全。

**预估难度**：低。

---

### Q15. 上下文预算规则明确化

**现状**：`000-context-pack.md` 的"上下文预算"写"L1 已查看 N 个文件，L2 保留 N 个候选，L3 深入阅读 N 个文件"，但没说预算上限是多少、超过怎么办。模型填这个字段时大概率随便写个数。

**做什么**：

两个选择：
- **方案 A（推荐）**：删除"上下文预算"节——它对 agent 执行没有实际指导意义，pathfinder 的分层扫描已经管了这个
- **方案 B**：明确预算规则（如"小仓 ≤20 文件，中仓 ≤50 文件，大仓按模块采样"）

建议方案 A，减少模板噪音。

**涉及文件**：`skills/impact-pro/templates/000-context-pack.md`

**验证方式**：确认预算节已删除或有明确规则。

**预估难度**：低。

---

### Q16. pathfinder SVG 预览图删除

**现状**：`project-map.md` 模板里每个 Mermaid 图后都跟一段手写的 SVG 代码（约 30-50 行）。307 行模板中约 120 行是 SVG 代码。大多数 Markdown 渲染器都能渲染 Mermaid，SVG 是冗余的。

**做什么**：
1. 从 `project-map.md` 模板中删除所有 SVG 代码段
2. Mermaid 是图的唯一 canonical source
3. 同步更新 `pf_validate.py` 的 V3（SVG 安全检查）——改为检查"无 SVG"或直接移除 V3

**涉及文件**：
- `skills/pathfinder/templates/project-map.md`（删除 SVG 段）
- `skills/pathfinder/scripts/pf_validate.py`（V3 调整或移除）
- `skills/pathfinder/SKILL.md`（如有 SVG 相关规则，同步删除）

**验证方式**：模板行数显著减少；`pf_validate.py` V3 调整后通过；L0 测试通过。

**预估难度**：低。

---

### Q17. 非功能需求举例业务化

**现状**：`010-requirements.md` 的"非功能需求"模板用技术指标举例——"安全：如'冻结操作需要 system:user:freeze 权限'"。后者已经是技术实现（权限标识），不是业务需求。

**做什么**：

举例改为业务语言：
```markdown
### 非功能需求

| 维度 | 要求 | 说明 |
|------|------|------|
| 性能 | 如"冻结操作用户不能感觉到卡顿" | 技术指标见 020-design.md |
| 安全 | 如"只有管理员能执行冻结操作" | 技术指标见 020-design.md |
| 可用性 | 如"冻结期间其他用户操作不受影响" | |
```

**涉及文件**：`skills/impact-pro/templates/010-requirements.md`

**验证方式**：人工阅读确认举例为业务语言。

**预估难度**：低。

---

### Q18. 代码风格报告自然语言化

**现状**：`020-design.md` 的"代码风格报告"用 `[Java-实体]` / `[DI]` / `[日志]` / `[SQL]` 标签引用风格约束（impact-pro 用 `style_axes` 轴名）。这是给 agent 执行时用的速记符号，但设计文档的主要读者是人类开发者。

**做什么**：

代码风格报告用自然语言段落描述，标签作为括号附注：

```markdown
### 代码风格报告

本项目 Entity 类使用 Lombok @Data 注解，不手写 getter/setter（[Java-实体]）。
Service 层用 @Transactional 标注事务边界，异常时回滚（[事务]）。
日志统一用 SLF4J + Lombok @Slf4j，关键操作记 INFO 级别（[日志]）。
SQL 用 MyBatis XML 映射，不写注解 SQL（[SQL]）。
```

标签保留供 agent 实施时参考，但主体是自然语言。

**涉及文件**：
- `skills/impact-pro/templates/020-design.md`
- `skills/impact/templates/020-design.md`（通过 S1 同步）

**验证方式**：人工阅读确认风格报告以自然语言段落为主。

**预估难度**：中。需要改模板结构。

---

## 六、实施顺序与依赖

按杠杆效应排优先级，不按传统依赖顺序：

```
第一批（基础设施，为后续铺路，1-2 小时）
  S1 模板同步机制
  S2 090 去栈特定命令
  虽然不直接补模型短板，但所有模板改动依赖它

第二批（直接补短板，最高杠杆，2-3 小时）
  E1  脚本闸门（含 V1-V6）——核心中的核心
  E2  判档决策证据化
  E3  弱模型降级策略
  E4  行号精度抽查（随 E1）
  这批直接补普通模型的短板，收益最大

第三批（防误导 + 减出错，2-3 小时）
  S3  handoff-contract 地图过期检测落地
  Q1  编号 bug 修复
  Q8  19 维度 checklist 化
  Q7  三段冗余合并为变更明细表
  Q11 占位符 HTML 注释化
  Q5  030 清理 agent 行为指令
  Q6  context-pack/design 去重
  Q14 语义约定字段补全
  Q15 上下文预算规则明确化
  Q17 非功能需求举例业务化
  先改 impact-pro/templates/，每改完一项跑 S1 同步
  减少普通模型被模板结构带偏或填错的概率

第四批（可读性，不直接影响模型表现，2-3 小时）
  Q4  凭证脱敏警告移除
  Q9  验证等级汇总视图
  Q10 文档间导航索引
  Q13 _active-state.md 中文化
  Q16 pathfinder SVG 删除（独立于同步机制）
  Q2  040-light.md 拆分
  Q3  060-preflight.md P0/P1 分表
  Q12 005-change-summary.md 新增
  Q18 代码风格报告自然语言化

第五批（验证效果，1-2 天）
  E5  Phase 5 执行阶段盲测（以 Composer 2.5 为首要模型）
  E6  扩大盲测覆盖面
```

**依赖说明**：
- S1 是所有 Q 项的前提：共享模板以 impact-pro 为源，改完同步到 impact
- E1 是 E3、E4 的前提：弱模型降级和行号抽查都依赖脚本闸门
- E5 依赖 E1-E4：先补强协议再盲测执行阶段
- E6 依赖 E5：先验证执行阶段再扩大覆盖面

**为什么把 E1-E4 提前到模板修复之前**：因为核心目标是驾驭普通模型，E1-E4 是直接补模型短板的高杠杆项，模板可读性改善不直接影响模型表现。先做 E1-E4 能尽早拿到"普通模型 + skill"的产出验证。

---

## 七、验证方式

### 每项改动的即时验证

| 改动类型 | 验证方式 |
|---------|---------|
| 模板改动 | 跑 `python scripts/sync_templates.py --check` 确认一致；L0 测试通过 |
| SKILL.md 协议改动 | L0 测试通过（铁律存在性、引用完整性、共享契约） |
| 脚本改动 | 在已有产出上跑脚本，确认检查项生效 |

### 批次完成后的回归验证

| 批次 | 回归验证 |
|------|---------|
| 第一批（基础设施） | L0 全绿 |
| 第二批（直接补短板） | L0 全绿 + L1 评测（跑 R1/R2/R3 确认无退步）+ E1 脚本在 v4 盲测产出上验证 |
| 第三批（防误导） | L0 全绿 + 人工阅读模板确认结构改善 |
| 第四批（可读性） | L0 全绿 + 人工阅读所有模板确认可读性改善 |
| 第五批（验证效果） | 新盲测 case 跑分 + 和 v4 基线 diff |

### 红线机制

- L1 评测任何契约 PASS→FAIL 或维度掉档 ≥ 3 → 阻断，回滚改动
- E1 脚本在 Composer B3（已知 PASS 产出）上必须全 PASS
- E1 脚本在 DeepSeek B3（已知不完整产出）上必须 V1 报 FAIL

### 对普通模型效果的专项验证

第二批完成后，用 Composer 2.5 重跑 v4 的 B1-B6，和 v4 基线 diff，验证：
- E1 脚本闸门是否拦截了 Composer 的产出问题（行号偏差、文件不完整等）
- E2 判档决策表是否在 B6（覆盖范围场景）产出
- E3 弱模型降级是否在 Composer 产出不完整时触发

第五批 E5 以 Composer 2.5 为首要模型，验证执行阶段不翻车。

---

## 附录：v4 后仍需人工复核的点（优化后预期变化）

| # | 复核项 | 优化前 | 优化后预期 |
|---|--------|--------|-----------|
| 1 | 判档是否正确 | 纯人工 | E2 判档决策表降低负担（表在就能一眼看出矛盾） |
| 2 | 行号是否准确 | 纯人工 | E4 行号抽查部分自动化 |
| 3 | API 方法名是否存在 | 纯人工 | E1 V3 检查标记 |
| 4 | 影响链是否覆盖核心场景 | 纯人工 | 仍需人工（协议补不了） |
| 5 | 需求文档渗入技术细节 | 纯人工 | E1 V2 自动拦截 |
| 6 | 跨文件逻辑一致性 | 纯人工 | 仍需人工（仅 pathfinder 认证链有自检） |
| 7 | Phase 5 执行是否按 Step 确认 | 未盲测 | E5 盲测覆盖 |

## 附录二：不同模型的预期收益

优化对三类性价比模型的预期效果不同，这决定了日常使用时的模型选择策略：

| 模型 | 短板 | 优化后预期收益 | 日常定位 |
|------|------|---------------|---------|
| Composer 2.5 | 行号偏差 1-10 行；偶发覆盖范围误判 | E1 V6 补行号，E2 决策表补覆盖范围。补完后大多数场景接近顶尖模型水平 | **日常主力**，安全敏感和覆盖范围场景除外 |
| Step 3.7 Flash | 推理弱，能识别缺口但不关联 | E2 决策表让推理可见但改不了推理。判 light 倾向仍在，错误只能被人工兜住 | 简单场景可用，复杂场景需人工复核判档 |
| DeepSeek-V4-Flash | 链路弱，产出严重不足 | E1 V1 拦截不完整产出，E3 提示换模型。**skill 拦得住它做不好，不能让它做好** | 不推荐日常使用，skill 价值是"快速暴露问题让你换模型" |

**覆盖范围判断（全量词场景）**：三类模型都过不了——E2 只是把推理暴露给人审，不是让模型推理正确。这类场景只能换更强模型或人工兜底。

**成本效益参考**：如果 Composer 2.5 + skill 能覆盖 80% 的日常场景，而顶尖模型只用于剩余 20% 的推理密集和安全敏感场景，整体成本可大幅下降。这正是开发这些 skill 的经济意义。
