# 三核心 Skill 问题审计（2026-07-10）

## 背景

### 这个项目是怎么来的

作者是一名 Java 开发，2025 年开始深度使用 AI 编码 agent 完成日常工作。在使用过程中发现一个反复出现的问题：**AI 能写代码，但不够稳——会跳步骤、漏上下文、提前宣布完成、在恢复会话时把旧确认当成新授权。** 弱模型尤其明显，但强模型也不总是可靠。

GitHub 上已有不少面向 0→1 新项目的 agent skill，但**"在已有系统上安全地做增量变更"** 这个场景少有人系统化解决。存量代码的变更风险跟新项目完全不同：字段/API/权限/配置的变化会不会漏引用、破坏兼容、影响数据，这些在已有代码库里才是真正高频的问题。

所以这个仓库的定位是：面向已有项目的需求迭代，给 AI coding agent 配一套"工头 + 安检门"。核心产出是三个 skill：

- **IntentAnchor**：变更之前，先把模糊意图变成结构化的能力清单和不可妥协项，防止后续阶段偏离
- **Pathfinder**：动手之前，先只读摸底陌生项目，产出项目结构总览，防止 agent 凭幻觉改代码
- **ImpactRadar**：改的时候，做基于证据的影响分析，按步骤确认，防止 agent 跳过分析直接写

三个 skill 可独立使用，也可串成链路：意图锚定 → 项目摸底 → 影响分析 + 执行。每个 skill 都有 validator 脚本做格式门禁；hook（目前主要属于 Impact，且只覆盖特定宿主和操作类型）做事中拦截（可选）；使用记录做过程可追溯。

### 为什么要做这次审计

三个 skill 的方法论和分工看起来成立，但作者对它们的实际可靠性不够自信——不确定有没有逻辑 bug、暗坑或结构性的设计缺陷。于是请 GPT-5.6 做了一轮审查，拿到了一份问题清单。

这份文档的目的是：**逐条核实 GPT-5.6 的问题清单是否属实，不盲信也不盲疑。** 对每个问题，读取被引用的实际代码行，对照逻辑判断，给出"属实/部分属实/不属实"的结论，并区分哪些是能修的 bug、哪些是架构天花板。

这次审计的意义不是"找出 bug 然后修掉"这么简单。更重要的是：**搞清楚"prompt 约束 + 文本格式校验"这套架构的天花板到底在哪。** 哪些问题改代码就能解决，哪些问题从结构上就不可能靠文件 validator 解决、需要换架构（从事后检查变为事中拦截），这些区别直接决定了后续投入精力的方向。

> 来源：GPT-5.6 提出的问题清单，逐条核实代码后确认。
> 核实方法：读取每个被引用的文件和代码行，对照实际逻辑验证。

## 总体结论

三个 skill 的核心分工和方法论成立，但存在多处确定性 bug 和规则冲突。当前适合有人监督使用，不适合把"门禁一定拦得住"当成事实。

- 8 个 P1 问题：7 个完全属实，1 个部分属实
- 5 个次要问题：全部属实
- GPT-5.6 二次评审提出 7 处修复计划修正和 5 处审计遗漏，经核实全部属实，已纳入下方修复计划
- **修复状态：P1-1 至 P1-7 + 4 项审计遗漏已全部修复（P1-8 和次要问题 1-4 待后续处理）。经 GPT-5.6 后续复核发现的残留问题已完成三轮修复，当前 138 个测试全部通过。**

---

## P1 问题

### P1-1 写入安全仍主要依赖模型自觉

**状态：属实（部分可修复，剩余为设计权衡）— ✅ 已修复可修复部分**

- `pathfinder/SKILL.md:4` 和 `impact/SKILL.md:4` 的 `allowed-tools` 都预批准了可执行任意 SQL 的工具（`mcp__dbhub__execute_sql`、`mcp__database__query`）
- `.claude/hooks/README.md:7`：写前 Hook 是可选的，项目只有放置 `.impact-protected` 文件才受保护，默认不自动启用
- 两个 skill 正文都显式声明了这是设计权衡（Pathfinder 写"allowed-tools 是预批准不是白名单"，Impact 写"真正的写保护由硬到软依次是：DB 账号权限 → settings deny / PreToolUse hook → skill 内确认检查点"）
- 但在没有配置只读 DB 账号、没有放 `.impact-protected` 的情况下，弱模型跳过"确认 Step N"时只剩 prompt 约束

**GPT-5.6 二次评审修正（属实）**：Pathfinder 是纯只读 skill，没有必要预批准 `execute_sql`/`query`。把任意 SQL 工具移出 Pathfinder 的 `allowed-tools`，至少能恢复客户端权限提示这一层保护。当前 hook 主要保护 Claude Code 的文件/Bash 写入，不能自然覆盖 Codex，也不能保护所有 MCP SQL 调用。因此 P1-1 应归为"部分可修复 + 剩余架构风险"，不是纯设计权衡。

---

### P1-2 Impact 把用户原有 Git 改动算到当前需求里

**状态：属实（确定性 bug）— ✅ 已修复**

- `impact/scripts/impact_validate.py:1434` `_changed_source_paths()` 直接运行 `git status --porcelain --untracked-files=all`，没有保存 Impact 启动时的基线
- `impact_validate.py:1540` 错误提示写着"或如果该改动不在本需求范围内，用 git checkout 还原文件"——可能误删用户修改
- 影响场景：用户在启动 Impact 前就有未提交的改动，Impact 会把这些改动算到当前需求里

---

### P1-3 Impact 的几个"门禁"可以被自填文本绕过

**状态：属实（三个子项均确认）— ✅ V18/V20/V22 已修复**

**V20（用户确认可写"未确认"通过）：**
- `impact_validate.py:2025`：`re.search(r"Step\s*\d+|未确认", confirm_val, re.I)` —— 写"用户确认：未确认"就能通过，不检查 Step 是否真正执行过

**V22（"无地图"声明不验证地图是否真不存在）：**
- `impact_validate.py:2135`：`if any(marker in status for marker in NO_MAP_MARKERS)` 其中 `NO_MAP_MARKERS = ("无地图", "不存在", "未发现")` —— 只信 Context Pack 自己写的声明，不去检查 `_project-map.md` 是否真的不存在

**V18（验证结果可手写，首次运行有鸡生蛋问题）：**
- `impact_validate.py:1842`：只匹配文本格式 `N passed, M failed`，无法验证是否来自真实运行。手写 "49 passed, 0 failed" 就能通过
- 首次创建 `_active-state.md` 时模板占位值会被拦截报 FAIL，必须先跑一次 validator 拿到真实输出填进去再跑一次才能通过——这个"两次运行"流程在 SKILL.md 和 reference 里没有显式说明

---

### P1-4 IntentAnchor validator 存在确定性错误放行

**状态：属实（确定性 bug）— ✅ V4/V6 已修复**

**V4（不可妥协项不交叉校验能力清单）：**
- `intent-anchor/scripts/intent_validate.py:104`：只数编号条目数量（3-5 条），不检查这些条目是否在能力清单里标记为"保留"
- 文件头注释（第 12 行）声称检查"每条在能力清单里标记为'保留'"，但代码没做这个检查
- 5 个完全编造的名称也能 PASS

**V6（❌ 被当成有效确认标记）：**
- `intent_validate.py:141`：`unconfirmed = [r for r in abandon_report_rows if "✅" not in r and "❌" not in r]` —— 只检查行里有没有 ✅ 或 ❌，不区分含义
- 全部标 ❌（表示"未确认"）的行不会被计入 `unconfirmed`，V6 报告"全部 N 条放弃项已逐条报告且有用户确认"

---

### P1-5 Pathfinder 的仓库体量扫描会严重误判

**状态：属实 — ✅ 已修复**

**不读 .gitignore：**
- `pathfinder/scripts/pf_scan.py:55` `scan_files()` 使用 `os.walk()` 物理遍历，有 `SKIP_DIRS` 集合但不读 `.gitignore`
- `pf_scan.py:113` `classify_budget` 的 docstring 自己承认："actual file count may be higher because pf_scan counts all physical files via os.walk (including untracked)"
- `phase-1-sizing.md:37` 要求"优先使用 `git ls-files`"，与实际实现矛盾

**manifest 只扫一层目录：**
- `pf_scan.py:94` `find_manifests()` 的 `if depth > 1: dirnames.clear()` 只扫描 depth 0-1
- `apps/foo/package.json`（depth 2）会漏掉

---

### P1-6 Pathfinder 的刷新规则存在死路和错误的新鲜度标记

**状态：属实 — ✅ 已修复（死路问题）**

**死路：**
- `pf_validate.py:610-616` V11 检查 facts/map 的 HEAD 是否匹配当前 HEAD，不匹配报 FAIL
- `phase-3-depth-fill.md:229` 刷新规则要求"刷新前先运行 Script Gate 确认旧地图格式合法"
- 矛盾：用户要刷新正是因为 HEAD 变了，但 V11 会在 Script Gate 阶段就因为旧 HEAD 拒绝通过

**新鲜度标记错误：**
- `phase-3-depth-fill.md:193` "再挖 X"只更新一个章节，却允许在 HEAD 变化时更新整个地图的 commit
- 未重新检查的旧章节会看起来像基于新 commit 生成

---

### P1-7 Impact 内部仍有互相冲突的规则

**状态：属实 — ✅ 已修复**

**残留写入例外：**
- `impact/references/phase-4-output.md:8`：context-pack "写入前必须获得用户确认（批量执行模式下自行假设并标注 `[假设]`）"——这个"批量执行模式下自行假设"与 SKILL.md 强制规则 #1"任何写操作必须有当前对话中的显式 `确认 Step N`"直接冲突

**确认粒度不统一：**
- `impact/SKILL.md:123` 写"full：三文档逐份确认"
- `impact/SKILL.md:226` 实际 Step 把所有文档（000/010/020/030 + `_active-state.md`）放在一个 Step 里批量确认
- "三文档"不准确：full 模式实际产出 4 份分析文档 + 1 个状态文件，不是 3 份

---

### P1-8 Impact 可能把业务决策误判成代码事实

**状态：部分属实（GPT-5.6 描述略有夸大）— ⏳ 待后续处理**

**冲突确实存在：**
- `impact/SKILL.md:23`：把"唯一约束"列为业务决策
- `impact/references/phases-detail.md:14`：也把"是否加唯一约束"列为业务需决策项
- 但 `phases-detail.md:35`："如果代码中无先例，但常见默认做法明确 → 代码可推断（用默认值 + 标注依据）"
- `phases-detail.md:44`：把"phone 是否唯一"的默认建议设为"不加"

**修正：**
- phases-detail.md:44 说的不是"Agent 自己决定不加"，而是"问用户时附上默认建议'不加'"，用户仍需确认
- 但默认建议本身确实偏向一个特定业务选择，在 DB 约束这种可能有安全影响的场景下不够安全
- SKILL.md:55 规则 #12 说"高风险岔路不可委托"，DB 约束属于规则 #2 高风险拦截清单，存在张力

---

## 次要问题

| # | 问题 | 状态 | 证据 |
|---|------|------|------|
| 1 | IntentAnchor 缺 WebSearch/WebFetch | 属实 | `SKILL.md:4` allowed-tools 只有 `Read, Grep, Glob, Write, Bash`；`anchoring-methods.md:48` 要求"用 Web 搜索找文档" |
| 2 | IntentAnchor Phase 1 就创建目录 | 属实 | `SKILL.md:90` 在 Phase 1 创建目录；写入确认在 Phase 3 |
| 3 | D4/D5 混入特定产品假设 | 属实 | `drift-patterns.md:60` D4 检测"后端是否有命令调度器"；`:72` D5 检测"AI 语音输出在全程传输"——来自语音交互产品 |
| 4 | IntentAnchor 缺 agents/openai.yaml 和 tests | 属实 | Impact 和 Pathfinder 都有 `agents/openai.yaml`；IntentAnchor 没有。IntentAnchor 也没有 `tests/` 目录 |
| 5 | CI 没跑全部测试 | 属实 — ✅ 已修复 | `eval-checks.yml` 只跑 impact validator、pathfinder validator、delivery checker。没跑 IntentAnchor 测试、没跑 `tests/run.sh` |

---

## 可修复性分类

文本 validator 的能力有一条结构性天花板：**当文本描述的是一个"事件"（用户说了什么、命令跑过没有），而文件本身是唯一信息来源时，校验文件无法验证事件是否真的发生过。** 这类问题需要换成 hook 架构（拦截执行、读对话上下文）才能真正拦住。

据此把所有问题分为三类：

### A 类：能修好（逻辑 bug 或有独立信息源可交叉校验）

| 问题 | 为什么能修 | 修复方向 |
|------|-----------|---------|
| P1-2 Git 基线 | 有独立信息源：启动时记录 git status 快照作为基线 | `_changed_source_paths` 增加基线 diff（**不能只保存路径集合**——见修复计划修正） |
| P1-4 V4 不可妥协项不交叉校验 | 两个节在同一文件内，可以做交叉校验 | V4 检查不可妥协项是否在能力清单中标记为"保留" |
| P1-4 V6 ❌ 被当成有效确认 | 逻辑错误，改判定条件即可 | 只认 ✅，不认 ❌ |
| P1-5 体量误判 | 有独立信息源：`git ls-files --cached --others --exclude-standard` | `pf_scan.py` 改用 `git ls-files --cached --others --exclude-standard`（既排除 .gitignore 又保留未跟踪真实文件）；manifest 从文件列表中提取而非限制深度（见修复计划修正） |
| P1-6 刷新死路 | 逻辑 bug，检查时机冲突 | V9 和 V11 在刷新流程中同时放宽（**不能只调 V11**——见修复计划修正）；或拆分"结构合法性检查"和"新鲜度检查" |
| P1-7 规则冲突 | 残留文本冲突，删掉即可 | 删除 phase-4-output.md 中的"批量执行模式"例外；统一确认粒度描述 |
| P1-3 V22 "无地图"不验证 | 有独立信息源：`_project-map.md` 是否存在可查询 | V22 增加文件系统检查，不只信文本声明 |
| P1-8 业务决策默认倾向 | 规则层面调整 | DB 约束类岔路不走"代码可推断默认"，强制走高风险确认流程 |
| 次要问题 1-5 | 工程完善 | 补工具、补配置、补测试、补 CI |

### B 类：文本 validator 修不到"真正拦住"，需要 hook 架构

| 问题 | 为什么文本 validator 做不到 | hook 架构怎么解 |
|------|---------------------------|----------------|
| P1-3 V20 用户确认可伪造 | 文件是唯一信息源，validator 无法知道用户是否真的说了"确认 Step N" | validator 检查"执行状态和确认字段是否自洽"（Step 状态为"成功/已执行"时"用户确认：未确认"必须 FAIL）；hook 检查"确认是否真来自用户"（已有 impact-write-gate 实现了这个） |
| P1-3 V18 验证结果可手写 | 文件是唯一信息源，validator 无法知道"49 passed"是否真的来自执行 | hook 在 Write/Edit `_active-state.md` 时拦截，只允许 validator 脚本写入"最近验证"节；或 hook 在写源码后自动触发 validator 并写入结果 |

### C 类：设计权衡，不存在"修好"的概念

| 问题 | 性质 | 可做的事 |
|------|------|---------|
| P1-1 写入安全依赖模型自觉 | 部分可修复：Pathfinder 是纯只读 skill，可移除 `execute_sql`/`query`；剩余为设计权衡 | Pathfinder `allowed-tools` 移除任意 SQL 工具；Impact 保留但标注风险；引导用户配置只读 DB 账号 + 启用 hook |

---

## 修复计划（三批，按可修复性 + 紧急度排序）

### 第一批：确定能修好、影响正确性的 bug

> 都是 A 类问题，改 validator 代码即可，无需换架构。

#### 1. P1-4 V4：不可妥协项不交叉校验能力清单 ✅ 已修复

- **文件**：`skills/intent-anchor/scripts/intent_validate.py`
- **问题**：V4 只数不可妥协项的条目数量（3-5 条），不检查这些条目是否在能力清单（§4）中标记为"保留"。5 个编造的名称也能 PASS。
- **修复方向**：
  1. 在 V4 检查中，结构化解析 §4 能力清单表格，提取每行的能力名称（第二列），建立"保留"能力名称的规范化集合
  2. 结构化解析 §5 不可妥协项的每条内容
  3. 逐条检查不可妥协项是否能在"保留"能力集合中找到精确匹配（**不用子串匹配**——子串匹配会导致"权限"误匹配"权限管理"等假通过）
  4. 最好给能力清单每条分配稳定 ID（如表格第一列序号），不可妥协项引用 ID 而非名称
  5. 找不到对应的 → FAIL，报"不可妥协项 'X' 不在能力清单的保留项中"
- **验证方式**：构造反例——5 个不存在于能力清单的名称写成不可妥协项，V4 应 FAIL
- **实际修复**：新增 `_normalize_name()` 函数做规范化精确匹配（去 markdown 格式、压缩空白、小写）；V4 解析 §4 表格提取“保留”项能力名，与 §5 不可妥协项逐条交叉校验。模板 INTENT.md 测试确认 V4 正确 FAIL（占位符不在保留项中）

#### 2. P1-4 V6：❌ 被当成有效确认标记 ✅ 已修复

- **文件**：`skills/intent-anchor/scripts/intent_validate.py`
- **问题**：第 141 行 `if "✅" not in r and "❌" not in r` 把 ✅ 和 ❌ 都当成有效确认标记。全部标 ❌ 的行不算 unconfirmed，V6 报告"已逐条报告且有用户确认"。
- **修复方向**：把判定条件改为只认 ✅。`unconfirmed = [r for r in abandon_report_rows if "✅" not in r]`，有 ❌ 的行算未确认。
- **验证方式**：构造反例——全部放弃项的确认标记改为 ❌，V6 应 FAIL
- **实际修复**：判定条件从 `"✅" not in r and "❌" not in r` 改为 `"✅" not in r`。❌ 表示未确认，仍计入 unconfirmed

#### 3. P1-2：Impact 把用户原有 Git 改动算到当前需求里 ✅ 已修复

- **文件**：`skills/impact/scripts/impact_validate.py`
- **问题**：`_changed_source_paths()`（第 1434 行）直接运行 `git status`，没有保存 Impact 启动时的基线。用户启动 Impact 前已有的未提交改动会被算到当前需求里。
- **修复方向**：
  1. Impact 流程启动时（Phase 1 或首次创建需求目录时），运行一次 `git status --porcelain --untracked-files=all` 保存为基线快照，写入需求目录下的 `.git-baseline.txt`
  2. **基线不能只保存路径集合**——如果某个文件启动前已经 dirty，Impact 后来又修改了同一个文件，该路径会被整个减掉，V15 仍然看不到本次增量。基线至少要保存每个文件的初始内容状态（或初始 diff/hash），V15 检查时比较的是文件内容是否相对于基线有新变化
  3. 第 1540 行的错误提示"用 git checkout 还原文件"改为"如果该改动不在本需求范围内，在执行记录中标注'非本次需求改动'"——不引导用户 `git checkout`，避免误删已有修改
  4. **不能允许模型事后自行标注"非本需求改动"**，否则只是换一种自填绕过。标注必须由用户确认或由 git diff 证据支撑
- **验证方式**：在有未提交改动的仓库中启动 Impact，V15 只应检查增量改动，不应报告基线中已有的改动
- **实际修复**：`_changed_source_paths` 新增 `req_dir` 参数，读取需求目录下的 `.git-baseline.json`（内容哈希快照）。对每个 git status 中的脏文件，比对当前内容哈希与基线哈希：相同则跳过（启动前已存在），不同则计入（Impact 产生的新改动）。错误提示从“用 git checkout 还原文件”改为“在执行记录中标注‘非本次需求改动’（需用户确认或 git diff 证据支撑）”。SKILL.md Phase 2 开头新增基线快照指令

#### 4. P1-3 V22："无地图"声明不验证地图是否真不存在 ✅ 已修复

- **文件**：`skills/impact/scripts/impact_validate.py`
- **问题**：第 2135 行只信 Context Pack 自己写的"无地图"声明，不检查 `_project-map.md` 是否真的不存在。模型可以撒谎。
- **修复方向**：
  1. 在 V22 中，当 Context Pack 声明"无地图"时，额外检查 `{repo_root}/change-impact/_project-map.md` 是否存在
  2. 文件存在但声明"无地图" → FAIL，报"Context Pack 声明无地图，但 `_project-map.md` 实际存在——请如实声明地图状态并记录消费记录"
  3. 文件不存在且声明"无地图" → PASS（声明与事实一致）
- **验证方式**：创建 `_project-map.md`，在 Context Pack 写"无地图"，V22 应 FAIL
- **实际修复**：V22 函数新增 `repo_root` 参数。声明“无地图”时，物理检查 `{repo_root}/change-impact/_project-map.md` 是否存在；文件存在但声明“无地图” → FAIL

---

### 第二批：影响判断准确性

> 都是 A 类问题，改脚本逻辑或删冲突文本，无需换架构。

#### 5. P1-5：Pathfinder 仓库体量扫描严重误判 ✅ 已修复

- **文件**：`skills/pathfinder/scripts/pf_scan.py`、`skills/pathfinder/references/phase-1-sizing.md`
- **问题 A（不读 .gitignore）**：`scan_files()`（第 55 行）用 `os.walk()` 物理遍历，物理文件数远大于 Git 跟踪文件数（本仓库实测 22,682 vs 728），导致预算档位误判为"超大仓"。`phase-1-sizing.md:37` 要求"优先使用 `git ls-files`"，与实际实现矛盾。
- **修复方向 A**：
  1. `scan_files()` 优先尝试 `git ls-files --cached --others --exclude-standard` 统计文件数，作为 `tracked_file_count`
  2. 这个命令既排除 .gitignore 内容，又保留未跟踪但真实属于项目的新文件（比单纯 `git ls-files` 更完整）
  3. `os.walk()` 的物理遍历结果保留为 `physical_file_count`，但 `classify_budget` 改用 `tracked_file_count` 分档
  4. 非 Git 仓库回退到 `physical_file_count`，在 facts JSON 中标注 `file_count_source: "physical"` 或 `"git-tracked"`
  5. docstring 中删除"actual file count may be higher"的免责声明——修好了就不需要它了
- **问题 B（manifest 只扫一层）**：`find_manifests()`（第 94 行）的 `if depth > 1: dirnames.clear()` 只扫 depth 0-1，`apps/foo/package.json`（depth 2）会漏掉。注意 `MAX_DIRS` 实际没有参与 `find_manifests()`。
- **修复方向 B**：不再用 `os.walk` + depth 限制找 manifest，改为从 `git ls-files --cached --others --exclude-standard` 的文件列表中筛选 manifest 文件名。这样不遗漏任意深度的 manifest，也不需要选一个任意的 depth 上限。
- **验证方式**：在本仓库运行 `pf_scan.py`，`budget_tier` 应为"中仓"（728 跟踪文件）；`manifest_files` 应包含 `mcp/web-search-mcp/package.json`
- **实际修复**：新增 `_git_ls_files()` 函数调用 `git ls-files --cached --others --exclude-standard`；`scan_files` 优先用 git ls-files 统计（返回 `tracked_file_count` + `physical_file_count` + `file_count_source`），非 Git 或 git 返回空时回退 os.walk；`find_manifests` 改为从 git 文件列表筛选（不限深度）；`classify_budget` docstring 删除“actual file count may be higher”免责声明

#### 6. P1-6：Pathfinder 刷新规则存在死路和错误新鲜度标记 ✅ 已修复（死路问题）

- **文件**：`skills/pathfinder/scripts/pf_validate.py`、`skills/pathfinder/references/phase-3-depth-fill.md`
- **问题 A（刷新死路）**：V11（第 610-616 行）检查 facts/map 的 HEAD 是否匹配当前 HEAD，不匹配报 FAIL。但刷新流程要求先跑 Script Gate（第 229 行），而用户要刷新正是因为 HEAD 变了——V11 会在 Script Gate 阶段就拒绝通过。
- **修复方向 A**：
  - **关键修正：不能只调 V11，V9 也必须同时处理。** V9 检查地图头部 commit 和 git.json `head_short` 是否一致。刷新流程如果先更新 git.json（新 HEAD），旧地图头部还是旧 commit，V9 会直接 FAIL。
  - 推荐方案：把"结构合法性检查"和"新鲜度检查"拆开。Script Gate 只跑结构合法性检查（V1-V8、V10），V9 和 V11 归为"新鲜度检查"，在刷新流程中降级为 WARN。刷新内容并更新地图头部 commit 后，再跑完整 Script Gate 确认新鲜度也通过。
  - 备选方案：V9 和 V11 在检测到处于刷新流程时（可通过命令行参数 `--refresh` 或检查旧 facts 文件是否存在判断）同时跳过 FAIL，改为 WARN。
- **问题 B（新鲜度标记错误）**：第 193 行"再挖 X"只更新一个章节，却允许在 HEAD 变化时更新整个地图的 commit 标记。未重新检查的旧章节看起来像基于新 commit 生成。
- **修复方向 B**：
  1. "再挖 X"时，如果 HEAD 变化，不允许直接更新地图头部的 commit
  2. 改为在概览头部增加"部分更新"标记，如 `基于 commit: <old>（部分更新于 <new>）`
  3. 或者更简单：HEAD 变化时只更新生成时间，不更新 commit，并在未覆盖项节标注"以下内容基于旧 commit <old>，可能过期"
- **验证方式**：模拟 HEAD 变化后触发刷新流程，Script Gate 应能通过（不再死路）；"再挖 X"后地图头部 commit 不应变为新 HEAD
- **实际修复**：V9 `check_commit_crosscheck` 和 V11 `check_current_head_freshness` 新增 `refresh_mode` 参数，降级为 WARN；CLI 新增 `--refresh` 参数；`phase-3-depth-fill.md` 刷新规则更新为先 `pf_validate.py --refresh` 后不带 `--refresh`。新鲜度标记问题（问题 B）待后续处理

#### 7. P1-7：Impact 内部互相冲突的规则 ✅ 已修复

- **文件**：`skills/impact/references/phase-4-output.md`、`skills/impact/SKILL.md`
- **问题 A（残留写入例外）**：`phase-4-output.md:8` 写"批量执行模式下自行假设并标注 `[假设]`"，与 SKILL.md 强制规则 #1"任何写操作必须有当前对话中的显式 `确认 Step N`"直接冲突。
- **修复方向 A**：删除 `phase-4-output.md:8` 中的"（批量执行模式下自行假设并标注 `[假设]`）"这段例外文本。Phase 4 文档写入和其他写操作一样，必须走 `确认 Step N`。
- **问题 B（确认粒度不统一）**：SKILL.md:123 写"full：三文档逐份确认"，但 SKILL.md:226 实际把所有文档（000/010/020/030 + `_active-state.md`）放在一个 Step 里批量确认。"三文档"也不准确——full 模式实际产出 4 份分析文档 + 1 个状态文件。
- **修复方向 B**：
  1. SKILL.md:123 的"三文档逐份确认"改为"四份文档 + 状态文件批量确认"，与实际 Step 一致
  2. 或反过来：改为真正的逐份确认（每份文档单独一个 Step），但这会增加交互轮次，需权衡
  3. 建议选方案 1（统一为批量确认），因为逐份确认在实操中交互成本过高
- **验证方式**：通读 SKILL.md 和 phase-4-output.md，确认无"批量执行模式""自行假设"等例外文本；确认粒度描述与实际 Step 一致
- **实际修复**：删除 `phase-4-output.md` 中的“（批量执行模式下自行假设并标注 `[假设]`）”；SKILL.md 流程图从“三文档逐份确认”改为“四份文档 + 状态文件批量确认”

---

### 第三批：架构层面——hook 从可选改为推荐启用

> B 类问题。文本 validator 从结构上验不了"事件是否真的发生过"，需要 hook 架构补位。项目已有 `impact-write-gate` hook 实现，当前设为可选。

#### 8. P1-3 V20/V18：validator 降级为格式校验，注明真实性依赖 hook

**背景**：什么是 hook？

hook 是 AI 执行操作之前自动触发的一段拦截代码。项目已有的 `impact-write-gate` hook（在 `.claude/hooks/` 目录下）做的事情是：

1. 检查项目根目录有没有 `.impact-protected` 文件（没有就不管）
2. 如果有，AI 每次 Write/Edit/Bash 写操作前，检查对话里最近一条**真实用户消息**是不是以 `确认 Step N` 开头
3. 不是就拦住，AI 根本写不了文件

与 validator 的区别：validator 是**事后**读文件检查内容（AI 已经写完了，发现格式不对再报错）；hook 是**事中**拦截（AI 还没写进去就被挡回来）。模型改不了对话历史，所以 hook 拦得住 validator 拦不住的问题。

**涉及文件和修改：**

**8a. `.claude/hooks/README.md` — 把 hook 从"可选"改为"推荐启用" ✅ 已修复**

- 当前措辞（第 2 行）："Optional Claude Code `PreToolUse` hook for impact / impact-pro Phase 5."
- 改为："Recommended `PreToolUse` hook for impact / impact-pro Phase 5. Enables write protection that text validators cannot provide."
- 补充一段说明：未启用时，V20/V18 等"事件真实性"检查仅靠 prompt 约束，弱模型可能绕过。启用后，写操作必须匹配对话中的真实 `确认 Step N`。

**8b. `skills/impact/scripts/impact_validate.py` — V20 增加内部一致性检查 + 降级注明 ✅ 已修复**

- V20 当前检查"用户确认"字段是否存在且含 Step 编号或"未确认"——这只验格式
- **不能只降级为格式说明，仍可增加可执行的一致性检查**：`_active-state.md` 的 Step 台账有状态字段（计划 / 待确认 / 已确认 / 成功 / 失败 / 跳过）。如果 Step 状态为"成功"或"已执行"，但执行记录中该 Step 的"用户确认"写"未确认"，V20 应 FAIL——这是内部自洽性检查，不依赖外部信息源
- 在 V20 的 PASS 消息中增加提示：`"V20: Step confirmation field format OK (真实性依赖 impact-write-gate hook)"`
- 在 V20 的 FAIL 消息中增加提示：`"注意：V20 校验格式和内部一致性，但无法验证用户是否真的确认。启用 impact-write-gate hook 可获得事中拦截。"`
- 正确分层：validator 检查"执行状态和确认字段是否自洽"，hook 检查"确认是否真来自用户"

**8c. `skills/impact/scripts/impact_validate.py` — V18 降级并注明 + 首次校验模式 ✅ 已修复**

- V18 当前检查"最近验证"结果是否匹配 `N passed, M failed` 格式——这只验格式
- **"两次运行"方案实际走不通**：第一次运行必然包含 V18 自己的失败（如 `N passed, 1 failed`），写回后第二次仍会因 `failed != 0` 被拒绝（代码第 1906-1907 行 `if failed_count != 0: fails.append(...)`）。需要正式的首次校验模式：
  - 方案一：validator 增加 `--bootstrap` 参数，跳过 V18 检查，其他检查全部通过后由 validator 自己写入真实结果到 `_active-state.md`
  - 方案二：validator 在其他检查全部通过后，自动写入"最近验证"节（不需要人工或模型手动填）
- 在 V18 的 PASS 消息中增加提示：`"V18: Verification result format OK (真实性依赖 impact-write-gate hook 或人工复核)"`

**8d. `skills/impact/SKILL.md` — 在强制规则区增加 hook 推荐说明 ✅ 已修复**

- 在规则 #1（逐步确认）或机制警示中，增加一句："推荐启用 `impact-write-gate` hook（`.claude/hooks/`）。hook 在 AI 执行写操作前拦截，检查对话中的真实用户确认消息，是 validator 无法替代的事中保护层。"
- 不改为强制（不同部署环境信任边界不同），但明确标注"未启用时安全边界仅靠 prompt"

---

### 未列入三批的后续事项

> C 类（设计权衡）和次要问题，不影响核心可用性，按需处理。

| 问题 | 处理方式 |
|------|---------|
| P1-1 写入安全依赖模型自觉 | **部分可修复**：Pathfinder `allowed-tools` 移除 `execute_sql`/`query`（纯只读 skill 不需要）；Impact 保留但标注风险；引导用户配置只读 DB 账号 + 启用 hook（与第三批合并）— ✅ 已修复 |
| P1-8 业务决策默认倾向 | DB 约束类岔路不走"代码可推断默认"，强制走高风险确认流程；调整 `phases-detail.md` 的边界判定原则 |
| 次要问题 1：IntentAnchor 缺 WebSearch/WebFetch | `SKILL.md` allowed-tools 增加 `WebSearch, WebFetch` |
| 次要问题 2：IntentAnchor Phase 1 就创建目录 | 延迟到 Phase 3 写入确认后再创建目录 |
| 次要问题 3：D4/D5 混入特定产品假设 | 改写为通用描述，去掉"命令调度器""AI 语音输出"等特定假设 |
| 次要问题 4：IntentAnchor 缺 agents/openai.yaml 和 tests | 补 `agents/openai.yaml`；补 `tests/` 目录和测试用例 |
| 次要问题 5：CI 没跑全部测试 | `eval-checks.yml` 增加 IntentAnchor 测试、`tests/run.sh`、`sync_templates.py --check` 与三个 skill 的元数据校验 — ✅ 已修复 |

---

## 审计遗漏（GPT-5.6 二次评审发现，经核实全部属实）

以下问题在首轮审计中遗漏，由 GPT-5.6 二次评审提出，经代码核实确认。

### 遗漏 1：仓库自身的项目地图已损坏 ✅ 已修复（隔离）

- **证据**：运行 `python skills/pathfinder/scripts/pf_validate.py change-impact/_project-map.md --repo-root .`，退出码 1，结果为 7 passed, 13 failed
- **根因**：facts 文件实际来自 `test-projects/prisma-express-ts`，`toplevel` 指向 `E:/agent/blue-skillhub/test-projects/prisma-express-ts` 而非本仓库；`schema_version`、`generator`、`source_path`、`observed_at` 均为 None（facts 格式不符合 schema）
- **影响**：Impact 消费该地图时会读到错误信息；当前 Impact 只检查 commit，不运行 Pathfinder validator，不会发现地图无效
- **处理**：隔离或刷新该地图；Impact 消费前应检查地图有效性（不只是 commit 一致性）
- **实际修复**：将损坏的 `change-impact/_project-map.md` 重命名为 `_project-map.md.broken` 隔离，避免下游 Impact 消费错误信息

### 遗漏 2：V7 无条件要求【14】节存在，与超大仓跳过规则矛盾 ✅ 已修复

- **证据**：`pf_validate.py:430` V7 `check_section_14()` 只检查【14】节是否存在且有内容，不检查【13】是否已声明"超大仓跳过"
- **矛盾**：SKILL.md 第 209 行写"超大仓或预算耗尽时可跳过【14】，但必须在【13】说明原因"，但 V7 无条件 FAIL，不会看【13】的声明
- **处理**：V7 应先检查【13】是否有"跳过【14】"的声明，有则降级为 WARN 或 PASS
- **实际修复**：V7 `check_section_14` 返回类型从 `list[str]` 改为 `tuple[list[str], list[str]]`。当 §13 声明跳过 §14 时，V7 降级为 WARN

### 遗漏 3：IntentAnchor 章节数量契约不一致 ✅ 已修复

- **证据**：`intent_validate.py:28` `REQUIRED_SECTIONS` 列表有 11 个条目（§1-§11），但 `SKILL.md:186` "INTENT.md 必须包含的章节"只列了 10 个（§1-§10，缺少 §11 三重锚定原始记录）
- **影响**：validator 要求 11 节，SKILL.md 告诉模型只需 10 节，模型按 SKILL.md 产出会 V2 FAIL
- **处理**：SKILL.md 章节列表补上第 11 节
- **实际修复**：SKILL.md 章节列表补上“11. 三重锚定原始记录”；`intent_validate.py` V2 消息从“全部 10 个章节”改为“全部 11 个章节”

### 遗漏 4：CI 应补充 sync_templates.py --check 和元数据校验 ✅ 已修复

- **证据**：`eval-checks.yml` 没有 `sync_templates.py --check` 步骤，也没有三个 skill 的 frontmatter 元数据校验
- **影响**：模板不同步或元数据不合规不会被 CI 拦截
- **处理**：CI 增加 `sync_templates.py --check` 和 skill frontmatter 校验步骤
- **实际修复**：`eval-checks.yml` 新增 4 个 CI step：IntentAnchor validator 测试、`tests/run.sh` 脚本、`sync_templates.py --check`、skill frontmatter 元数据校验（检查 name/description/allowed-tools 字段）

### 遗漏 5：背景描述不准确 ✅ 已修复

- **证据**：原文写"三个 skill 串成一条链路、每个都有 hook"——实际三个 skill 可独立使用，hook 目前主要属于 Impact，且只覆盖特定宿主和操作类型
- **处理**：已在本次更新中修正

---

## 修复执行结果总览（2026-07-10）

### 已修复项（15 项）

#### 第一批：确定性 Bug（4 项）

| 编号 | 修改文件 | 修改内容 |
|------|----------|----------|
| P1-4 V4 | `intent_validate.py` | 新增 `_normalize_name()` 函数；V4 解析 §4 表格提取"保留"项能力名，与 §5 不可妥协项做规范化精确匹配（非子串匹配），找不到对应 → FAIL |
| P1-4 V6 | `intent_validate.py` | 确认标记判定从 `"✅" not in r and "❌" not in r` 改为 `"✅" not in r`，❌ 表示未确认 |
| P1-2 | `impact_validate.py` + `SKILL.md` | `_changed_source_paths` 新增 `req_dir` 参数，读取 `.git-baseline.json` 做内容哈希比对，区分启动前脏文件和 Impact 增量改动；错误提示不再引导 `git checkout`；SKILL.md Phase 2 新增基线快照指令 |
| P1-3 V22 | `impact_validate.py` | V22 声明"无地图"时物理检查 `_project-map.md` 是否存在，文件存在但声明无地图 → FAIL |

#### 第二批：影响判断准确性（3 项）

| 编号 | 修改文件 | 修改内容 |
|------|----------|----------|
| P1-5 | `pf_scan.py` | 新增 `_git_ls_files()` 函数；`scan_files` 优先用 `git ls-files --cached --others --exclude-standard` 统计，非 Git 或空时回退 os.walk；新增 `file_count_source`/`physical_file_count` 字段；`find_manifests` 改为从 git 文件列表筛选不限深度 |
| P1-6 | `pf_validate.py` + `phase-3-depth-fill.md` | V9/V11 新增 `refresh_mode` 参数降级为 WARN；CLI 新增 `--refresh` 参数；刷新规则文档更新为先 `--refresh` 后不带 `--refresh` |
| P1-7 | `phase-4-output.md` + `SKILL.md` | 删除"批量执行模式下自行假设"例外文本；流程图从"三文档逐份确认"改为"四份文档 + 状态文件批量确认" |

#### 第三批：Hook 架构补充（4 项）

| 编号 | 修改文件 | 修改内容 |
|------|----------|----------|
| P1-3 V20 | `impact_validate.py` | V20 新增内部一致性检查：解析 `_active-state.md` Step 台账状态，Step 状态为"成功"/"已执行"但 用户确认为"未确认" → FAIL；PASS 消息注明真实性依赖 hook |
| P1-3 V18 | `impact_validate.py` | 新增 `--bootstrap` 参数：跳过 V18 检查，其他全过后自动写入结果到 `_active-state.md`；新增 `_bootstrap_write_result()` 辅助函数 |
| P1-1 | `pathfinder/SKILL.md` | 从 `allowed-tools` 移除 `mcp__database__query` 和 `mcp__dbhub__execute_sql` |
| Hook 推荐 | `hooks/README.md` + `impact/SKILL.md` | README 标题从"Optional"改为"Recommended"，添加推荐理由；SKILL.md 机制警示后添加 hook 推荐说明 |

#### 审计遗漏修复（4 项）

| 编号 | 修改内容 |
|------|----------|
| 遗漏 1 | 损坏的 `change-impact/_project-map.md` 重命名为 `_project-map.md.broken` 隔离 |
| 遗漏 2 | V7 `check_section_14` 返回类型改为 `tuple[list, list]`，§13 声明跳过 §14 时降级为 WARN |
| 遗漏 3 | SKILL.md 章节列表补上"11. 三重锚定原始记录"；V2 消息从"10 个章节"改为"11 个章节" |
| 遗漏 4 | `eval-checks.yml` 新增 4 个 CI step：IntentAnchor validator 测试、`tests/run.sh`、`sync_templates.py --check`、skill frontmatter 元数据校验 |

### 待后续处理项

| 编号 | 原因 |
|------|------|
| P1-8 业务决策默认倾向 | 需调整 `phases-detail.md` 的边界判定原则，涉及方法论层面调整 |
| P1-6 问题 B（新鲜度标记错误） | "再挖 X"时 HEAD 变化的处理方式需进一步设计，当前只修了死路问题 |
| 次要问题 1-4 | 工程完善项（补工具、补配置、补测试），不影响核心可用性 |

### 测试结果

| 测试套件 | 测试数 | 结果 |
|----------|--------|------|
| `test_impact_validate.py` | 54 | ✅ 全部通过 |
| `test_pathfinder_scripts.py` | 35 | ✅ 全部通过 |
| `test_intent_validate.py` | 8 | ✅ 全部通过 |
| delivery checker tests | 41 | ✅ 全部通过 |
| **合计** | **138** | **✅ 全部通过** |

- 全部修改文件通过 `py_compile` 编译检查
- 全部修改文件无 linter 错误
- `intent_validate.py` 对模板 INTENT.md 的冒烟测试确认 V4 交叉校验和 V2 章节数检查正常工作

### 修改文件清单

| 文件 | 修改类型 |
|------|----------|
| `skills/intent-anchor/scripts/intent_validate.py` | 逻辑修复（V4 交叉校验 + V6 确认标记 + V2 章节数） |
| `skills/intent-anchor/SKILL.md` | 文档修复（章节数 10 → 11） |
| `skills/impact/scripts/impact_validate.py` | 逻辑修复（V18 bootstrap + V20 一致性 + V22 物理检查 + Git 基线 + import 补充） |
| `skills/impact/references/phase-4-output.md` | 文本修复（删除批量执行模式例外） |
| `skills/impact/SKILL.md` | 文档修复（确认粒度 + hook 推荐 + Git 基线指令） |
| `skills/pathfinder/scripts/pf_scan.py` | 逻辑修复（git ls-files + manifest 不限深度 + subprocess import） |
| `skills/pathfinder/scripts/pf_validate.py` | 逻辑修复（V7 超大仓跳过 + V9/V11 refresh_mode + CLI --refresh） |
| `skills/pathfinder/references/phase-3-depth-fill.md` | 文档修复（刷新规则更新） |
| `skills/pathfinder/SKILL.md` | 配置修复（移除 SQL 写工具） |
| `.claude/hooks/README.md` | 文档修复（Optional → Recommended） |
| `.github/workflows/eval-checks.yml` | CI 补充（4 个新 step） |
| `skills/impact/tests/test_scripts/test_impact_validate.py` | V18、V20、V22 与 Git 基线回归测试 |
| `skills/intent-anchor/tests/test_intent_validate.py` | V3、V4、V6 行为回归测试 |
| `skills/pathfinder/tests/test_scripts/test_pathfinder_scripts.py` | 测试适配（scan_facts 新字段 + file_count 断言放宽 + V7 预算回归 + V6 口径回归） |

---

## 第二轮修复记录（2026-07-10，GPT-5.6 二次复核后）

### 修复项（7 项）

| # | 严重度 | 发现 | 修复 | 文件 |
|---|--------|------|------|------|
| R1 | P1 | bootstrap 写入失败仍返回 0 | `_bootstrap_write_result` 返回 bool，写入失败时 main 退出 1 | `impact_validate.py` |
| R2 | P1 | IntentAnchor 决策列子串判断，"不保留"被误认为"保留" | V3 新增 `VALID_DECISIONS` 集合严格校验；V4/V5 改为 `==` 精确匹配 | `intent_validate.py` |
| R3 | P2 | V7 "预算充足"被当成"预算耗尽" | 匹配关键词从单独"预算"改为"预算耗尽/预算不足/超出预算"等明确语义 | `pf_validate.py` |
| R4 | P2 | V6 交叉检查用 os.walk 物理遍历，与 pf_scan 口径不一致 | `_count_files_quick` 改为优先用 `git ls-files`，非 Git 回退 os.walk | `pf_validate.py` |
| R5 | P2 | V18 `--bootstrap` 未文档化 | `phase-4-output.md` 补充首次运行使用 `--bootstrap` 的说明 | `phase-4-output.md` |
| R6 | P2 | phase-4-output.md "每份确认后再出下一份"与 SKILL.md 矛盾 | 改为"四份文档 + 状态文件批量确认" | `phase-4-output.md` |
| R7 | P2 | V20 `step_num in label` 子串匹配，Step 1 匹配 Step 10 | 改为 `re.search(rf"Step\s+{step_num}(?!\d)")` 精确匹配 | `impact_validate.py` |

### 新增回归测试

| 测试 | 覆盖的修复 | 文件 |
|------|-----------|------|
| `test_step1_does_not_match_step10_success` | V20 Step 1 vs 10 | `test_impact_validate.py` |
| `test_bootstrap_missing_section_exits_nonzero` | Bootstrap 写入失败退出码 | `test_impact_validate.py` |
| `test_deleted_untracked_file_detected` | Git 基线删除检测 | `test_impact_validate.py` |
| `test_skip_with_budget_sufficient_fails` | V7 预算充足不放行 | `test_pathfinder_scripts.py` |
| `test_skip_with_budget_exhausted_passes` | V7 预算耗尽放行 | `test_pathfinder_scripts.py` |
| `test_skip_with_super_large_repo_passes` | V7 超大仓放行 | `test_pathfinder_scripts.py` |
| `test_count_files_uses_git_ls_files` | V6 统计口径一致 | `test_pathfinder_scripts.py` |
| `test_invalid_decision_fails` | V3 决策列非法值 | `test_intent_validate.py` |
| `test_empty_decision_fails` | V3 决策列空值 | `test_intent_validate.py` |
| `test_non_retained_name_fails` | V4 不可妥协项交叉校验 | `test_intent_validate.py` |
| `test_wrong_name_in_report_fails` | V6 放弃项名称核对 | `test_intent_validate.py` |
| `test_rejected_confirmation_fails` | V6 只接受 ✅ 确认 | `test_intent_validate.py` |
| `test_declared_no_map_but_repo_map_exists_fails` | V22 从 repo root 检查地图 | `test_impact_validate.py` |
| `test_skip_text_outside_section_13_does_not_authorize_skip` | V7 只接受 §13 跳过声明 | `test_pathfinder_scripts.py` |

### CI 更新

- IntentAnchor 从 `py_compile` 语法检查改为跑 `test_intent_validate.py` 行为测试
- `sync_templates.py` 路径修正为 `scripts/sync_templates.py`
- 新增 `pip install pyyaml pytest` 步骤

---

## 第三轮修复记录（2026-07-10，最终复核）

| # | 发现 | 修复 |
|---|------|------|
| R8 | IntentAnchor V6 在人工重放修改时恢复了旧的 `✅/❌` 双放行逻辑 | 恢复为只接受 `✅`，补 `❌` 反例测试 |
| R9 | 新增 IntentAnchor 测试被 `skills/*/tests/` 忽略 | 为测试目录和测试文件增加 `.gitignore` 例外 |
| R10 | V22 通过需求目录层级推算项目地图位置 | 改为使用 `--repo-root/change-impact/_project-map.md` |
| R11 | V7 在整份地图中查找跳过声明 | 限定只读取 §13 正文 |
| R12 | V20 Step 1/10 测试无法区分旧子串实现 | 改为只有 Step 10 是终态，并断言 Step 1 不继承其状态 |
| R13 | 总览与测试表数量不一致 | 统一更新为 138 项 |
