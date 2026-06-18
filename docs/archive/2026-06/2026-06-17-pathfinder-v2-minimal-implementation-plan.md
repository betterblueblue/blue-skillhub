# Pathfinder v2 最小实施计划

> **状态**：待执行
> **前序文档**：[2026-06-17-pathfinder-session-research-and-v2-proposal.md](./2026-06-17-pathfinder-session-research-and-v2-proposal.md)（Cursor 调研 + v2 提案）
> **定位**：本计划是三方共识（Cursor 调研 → DeepSeek 剪裁 → GLM 评审）后的最小可行方案
> **核心原则**：不动架构，只加三层补强。不造 Nexus。

---

## 0. 解决的问题

以下三个真实存在、需要动：

| # | 问题 | 解法 | 复杂度 |
|---|------|------|--------|
| 1 | "有时不靠谱"（弱模型 61 分） | 3 个 stdlib 脚本做事实层 + 闸门 | 低（~200 行 Python） |
| 2 | "信息有了但不好用"（缺 onboarding） | 模板顶部加 30 秒导航区 | 极低（只改模板） |
| 3 | "深度不够 / 泛"（串行预算不足） | Phase 2 重写为 5 路并行专探 | 中（重写一个 phase） |

以下两个**不解决**：

| # | "问题" | 为什么不解决 |
|---|--------|-------------|
| 4 | "跑一次就完了" | 不是 Pathfinder 的问题。概览头部 commit hash 对比已经防过期 |
| 5 | "图不直观" | 已在修（工作区 SVG 预览增强），交互 HTML 过度设计 |

---

## 1. 改动范围总览

```
skills/pathfinder/
├── scripts/                         ← 新增目录（3 个脚本）
│   ├── pf_scan.py                   ← 新增：文件数、扩展名、目录树
│   ├── pf_git.py                    ← 新增：HEAD、toplevel、hotspots、模块变更频次
│   └── pf_validate.py               ← 新增：闸门（行号、凭证、SVG 安全）
├── SKILL.md                         ← 修改：引用脚本、Phase 2 改为并行、Script Gate
├── references/
│   ├── phase-2-explore-domains.md   ← 新增：替换原 phase-2-breadth-scan.md
│   ├── phase-2-breadth-scan.md      ← 删除（被 phase-2-explore-domains.md 替代）
│   └── phase-3-depth-fill.md        ← 修改：移出 Phase 4.5 自检（改由脚本执行）
├── templates/
│   └── project-map.md               ← 修改：顶部加 Executive Summary 区域
└── tests/
    └── scenarios/                   ← 追加：脚本输出 schema 校验
```

### 不改的文件（明确排除）

| 文件 | 原因 |
|------|------|
| `references/handoff-contract.md` | impact 读法不变，`_project-map.md` 章节编号保持 |
| `references/phase-1-sizing.md` | 体量测量逻辑不变，数字从脚本出但规则相同 |
| `references/stack-detection.md` | 栈探测规则不变 |
| `references/cross-platform-notes.md` | 约定不变，脚本兼容性在脚本内部处理 |
| `code-graph-adapters/generic-mcp.md` | 结构索引规则不变 |
| `README.md` | 暂不改；实施完成后统一更新 |
| `validation-runs/` | 实施完成后追加新验证记录 |

### impact 侧需要改的吗？

**不需要。** `_project-map.md` 章节编号和标签格式保持不变。新增的 Executive Summary 区域在【0】之前，impact 不受影响——impact 按章节号对号入座，不解析概览头部以上内容。

---

## 2. 脚本层详设

### 2.1 设计约束

- **Python 3.8+**，只使用标准库（`os`, `sys`, `json`, `subprocess`, `re`, `argparse`, `hashlib`, `datetime`, `pathlib`）
- 不引入任何第三方包（无 `pip install`）
- 命令行接口：`python pf_xxx.py <target_dir> [--output <file>]`
- 输出：`--output` 指定时写 JSON 文件到 `change-impact/_project-map/facts/` 目录，否则 stdout
- 退出码：成功 0，失败 1
- 路径统一正斜杠 `/`（与项目规范一致）
- 跨平台：Windows / Linux / macOS 均可用（用 `pathlib` 处理路径差异）

### 2.1.5 脚本产出消费路径（关键设计决策）

脚本产出文件写入目标项目的 `change-impact/_project-map/facts/`：

```
<project-root>/change-impact/_project-map/facts/
├── scan.json    ← pf_scan.py 输出
└── git.json     ← pf_git.py 输出
```

**主 agent 如何消费**：Phase 1.5 运行脚本后，主 agent 用 Read 工具读 facts JSON 文件，提取关键数据填入地图：

| 数据来源 | 提取字段 | 填入地图位置 |
|---------|---------|-------------|
| `scan.json` | `file_count`, `dir_count`, `budget_tier` | 【0】预算档位 |
| `scan.json` | `extensions` top 5, `manifest_files` | 【2】技术栈 |
| `scan.json` | `top_level_dirs` | 【3】模块目录列 |
| `git.json` | `head_short`, `is_independent_repo` | 【0】概览头部 |
| `git.json` | `hotspots`, `recent_commit_modules` | Phase 3 聚焦候选 |

**为什么是 JSON 而不是 stdout Markdown**：脚本产出是结构化事实数据（扩展名计数、hotspot 文件路径列表），主 agent 需要按字段提取。Markdown 适合人类阅读但不适合机器解析——agent 从 JSON 提取 `file_count` 比从 Markdown 表格解析更可靠、更少歧义。JSON 的 schema 也在测试中可验证。

**pf_validate.py 的输出不同**：闸门脚本不写文件，输出是 stdout 的 PASS/FAIL/WARN 行 + exit code。主 agent 读 stdout 判断闸门是否通过——不解析 JSON。

### 2.2 `pf_scan.py` — 项目体量扫描

**用途**：产出项目的确定性事实，替代模型自己数文件/猜目录。

**输入**：目标项目根目录路径

**输出 JSON schema**：

```json
{
  "scanned_at": "2026-06-17T12:00:00",
  "target_dir": "/path/to/project",
  "file_count": 142,
  "dir_count": 23,
  "top_level_dirs": [
    {"name": "src", "type": "directory", "file_count": 87, "subdirs": ["api", "services", "models"]},
    {"name": "config", "type": "directory", "file_count": 5, "subdirs": []}
  ],
  "extensions": {
    ".java": 45,
    ".ts": 32,
    ".json": 8,
    ".md": 6,
    ".xml": 4
  },
  "manifest_files": [
    {"path": "package.json", "type": "npm"},
    {"path": "tsconfig.json", "type": "typescript"}
  ],
  "budget_tier": "medium",
  "budget_tier_reason": "142 files, 23 dirs — falls in medium range (100-500 files)"
}
```

**关键行为**：

- 扫描深度 2 层（顶层目录 + 一层子目录），不递归全仓（对大仓安全）
- 排除 `.git`、`node_modules`、`vendor`、`__pycache__`、`*.pyc`、`target/`、`build/`、`dist/`、`.next/` 等标准忽略目录
- 扩展名统计基于文件扩展名（小写）
- 清单文件识别：「包管理文件 → 类型」映射表内置于脚本
- 预算分档逻辑与 `references/phase-1-sizing.md` 一致：
  - 小仓 <100 文件
  - 中仓 100–500 文件
  - 大仓 500–2000 文件
  - 超大仓 >2000 文件

### 2.3 `pf_git.py` — Git 元数据提取

**用途**：产出 git 相关确定性事实，替代模型自己跑 git 命令并可能截断/误读输出。

**输入**：目标项目根目录路径

**输出 JSON schema**：

```json
{
  "scanned_at": "2026-06-17T12:00:00",
  "is_git_repo": true,
  "is_independent_repo": true,
  "toplevel": "/path/to/repo",
  "head_short": "abc1234",
  "head_full": "abc1234567890def...",
  "branch": "main",
  "hotspots": [
    {"path": "src/api/orderController.ts", "recent_commits": 5, "total_commits": 23},
    {"path": "src/services/paymentService.ts", "recent_commits": 4, "total_commits": 18}
  ],
  "hotspot_limit": 10,
  "recent_commit_modules": ["src/api", "src/services"]
}
```

**关键行为**：

- 先 `git rev-parse --show-toplevel` 判断是否为独立仓库（对比 `target_dir`）
- `is_independent_repo: false` 时，`head_short` 不写父仓库 HEAD——写 `null`，由 SKILL.md 规则处理（标"非独立 Git 仓库"）
- `hotspots` 取最近 30 天内提交最频繁的 10 个文件（`git log --since="30 days ago" --name-only --pretty=format:` 聚合计数）
- `recent_commit_modules`：从 `hotspots` 的路径中提取唯一顶层目录
- 非 Git 项目（`git rev-parse` 失败）时输出 `{"is_git_repo": false, "is_independent_repo": false, "head_short": null, ...}`
- Git 仓库但无 30 天内提交时，`hotspots` 为空数组，`recent_commit_modules` 为空数组——不编造

### 2.4 `pf_validate.py` — 闸门验证

**用途**：在 Phase 4 写入 `_project-map.md` 之前执行，验证地图内容不违反硬性规则。是外部闸门，不是模型自查。

**输入**：`_project-map.md` 的路径（或 stdin）

**输出**：stdout 报告 + exit code（0 = 通过，1 = 不通过）

**检查项**：

| # | 检查 | 方法 | 不通过时 |
|---|------|------|----------|
| V1 | 行号真实性 | 提取所有 `【已核实: ...file:行号】`，逐条 grep 目标文件确认行号存在 | 列出虚假行号 |
| V2 | 凭证未泄露 | 模式扫描：`password=`、`secret=`、`token=`、`api_key`、`DSN`、`jdbc:`、`mongodb://.*@` 等。上下文允许在 `【已核实`/`风险` 等语义块中判断 | 列出泄露位置 |
| V3 | SVG 安全 | 若含 `<svg>`，扫描 `script`、`foreignObject`、`href=`、`http://`、`https://` | 列出违规标签 |
| V4 | 未覆盖项非空 | 提取【13】节，确认至少含 1 条非空条目 | 单一错误 |
| V5 | Mermaid/SVG 实线一致性 | 提取所有 Mermaid `-->`（实线）关系，对比正文中的【已核实】标签——不要求逐条匹配（复杂度太高），只检查所有画了实线的节点是否在正文中有提及 | 列出孤悬实线 |

**关键行为**：

- V1（行号真实性）：解析 `【已核实: ...xxx.xx:NNN】`，提取文件路径和行号。文件路径相对于目标项目根目录（从 `_project-map.md` 所在仓库的父路径推断，或通过 `--repo-root` 参数传入）
- V2（凭证脱敏）：正则模式匹配，返回 `line_number: matched_text_context`。**允许假阳性**（如注释中的 `password=`），报告为 WARNING 而非 ERROR；`***` 标注已脱敏则 PASS
- V3（SVG 安全）：只检查是否含禁止标签/属性，不验证 SVG 结构正确性
- V5（一致性）：**简化版**——只选取所有 Mermaid 实线箭头的源节点（`A --> B` 中的 A），检查正文中是否提及 A 模块。不区分 `[已核实]` vs `[推断]`——这是一致性的「存在性检查」，不是完整的可信度验证。完整一致性检查留给 L1 测评
- 输出格式：每行 `PASS|FAIL|WARN: V<N> <描述>`，末尾 `SUMMARY: N passed, M failed, K warnings`

**命令行接口**：

```bash
python pf_validate.py _project-map.md --repo-root /path/to/project
# 或从 stdin
cat _project-map.md | python pf_validate.py --repo-root /path/to/project --stdin
```

---

## 3. 模板改动：Executive Summary

### 3.1 改动位置

在 `templates/project-map.md` 的【0】基本信息之前，插入导航摘要区。

### 3.2 新增内容

```markdown
## Executive Summary（30 秒读懂）

> 本节为人类快速认知设计。impact 读取时跳过本节，从【0】开始。

### 一句话

[项目名] 是一个 [做什么的] 项目，使用 [主要语言/框架] 构建，面向 [谁用/什么场景]。

证据：【已核实: ...】或【推断: ...】

### Quick Start（5 步跑起来）

1. 克隆并安装依赖：
2. 配置环境变量：
3. 初始化数据库：
4. 启动开发服务：
5. 访问应用：

> 每步写**真实命令**，找不到真实入口写"未发现"。

### 从这 5 个文件开始读

| 文件 | 为什么重要 | 可信度 |
|------|-----------|--------|
| `src/main.ts` | 应用入口，启动逻辑 | 【已核实: ...】 |
| `src/routes/index.ts` | 所有路由注册在此 | 【已核实: ...】 |
| ... | ... | ... |

### Top 3 风险

1. [风险描述，无凭证值] — 【已核实: ...】
2. ...
3. ...

### 导航

- 想理解架构？→ 【3】架构分层
- 想理解数据？→ 【6】数据模型概览
- 想追踪一条请求？→ 【11】典型主流程
- 想了解还有哪些没挖深？→ 【13】没挖深的部分
- 交互架构图 → [打开 map.html](_project-map/map.html)（如已生成）

---

[从这里开始是原模板的【0】基本信息，不变]
```

### 3.3 约束

- Executive Summary 的总长度控制在 **15 行以内**（不含代码块）
- Quick Start 的每步如果找不到真实命令，写"未发现"
- 「从这 5 个文件开始读」的文件数不强制 5——可以是 3-7 个，核心约束是「每个文件注明为什么重要」
- 导航区的 map.html 链接为可选——当前版本不生成 map.html，写"（暂未生成）"

---

## 4. Phase 2 重写：并行专探

### 4.1 旧文件

`references/phase-2-breadth-scan.md` — 单 agent 串行 Glob/Grep/Read 的广度扫描。

### 4.2 新文件

`references/phase-2-explore-domains.md` — 5 路并行子 agent 专探。

### 4.3 并行模型

主 agent 在 Phase 2 发一条消息，spawn 5 个 explore 子 agent：

| Agent | 职责 | 产出 |
|-------|------|------|
| **A1 架构** | 模块边界、分层、目录结构、模块间依赖方向 | 对话内结构化报告（不是写文件） |
| **A2 数据** | schema / model / ORM 映射 / migration 文件 | 同上 |
| **A3 入口/API** | HTTP 路由、CLI 入口、MQ consumer、定时任务 | 同上 |
| **A4 权限** | authn 方式、authz 机制、中间件/守卫位置 | 同上 |
| **A5 运维** | 构建命令、运行命令、测试命令、部署配置、CI | 同上 |

### 4.4 每个子 agent 的设计

每个 explore agent 遵守：

1. **只读**：只用 Read/Grep/Glob/Bash(git)，不写任何文件
2. **输入**：主 agent 传入目标项目路径 + 关注重点 + `facts/` 脚本输出摘要（文件数、扩展名 top 5、栈类型、top_level_dirs、hotspots、recent_commit_modules）
3. **输出格式**：在对话中输出结构化报告，包含：
   - 发现的模块/实体/路由/权限等（含文件路径证据）
   - 推断项（标【推断】，注明依据）
   - 未确认项（声明「本域未覆盖」的部分）
   - `hypotheses_challenged`：至少尝试找 1 条「目录名假说 vs facts 矛盾」。找不到则写「未发现矛盾」——不强制编造
4. **信任纪律**：所有实线依赖/关系必须有证据，无证据标推断

**为什么按域分而不是按模块分**：5 个域（架构/数据/API/权限/运维）是正交切面——任何项目都有这五个维度。按模块分路（如"user 模块一个 agent、order 模块一个 agent"）会导致每个 agent 需要跨域扫描（既要看路由又要看数据又要看权限），子 agent 的输入上下文重复、产出难以合并。按域分路保证每路有独立上下文预算、产出不重叠、主 agent 合并无冲突。

### 4.5 Phase 2.5：Challenge 合并

取消独立的 Phase 2.5。challenge 逻辑进每个子 agent 的输出（`hypotheses_challenged` 字段）。主 agent 在 Phase 3 synthesis 时汇总并写入地图。

理由：独立的 Phase 2.5 需要再多一轮 agent 调度；并入子 agent 不增加轮次，且 challenge 的上下文在专探时已经拿到了。

### 4.6 降级策略

降级触发条件（按优先级检查）：

1. **Task 工具不在可用工具列表** → 完全降级为串行（5 路 → 1 路，等同于 v1 Phase 2）
2. **Task 可用但 spawn 子 agent 返回空/错误**（3 次重试后仍失败）→ 该路结果丢弃，其余路正常合并
3. **任意子 agent 超过 5 分钟未返回** → 该路超时丢弃，其余路正常合并
4. **3 路及以上超时/失败** → 完全降级为串行

降级后：
- 在概览头部或【13】未覆盖项中注明：`并行模式: N 路成功 / K 路降级 / 串行回退`
- 丢弃的子 agent 域标记为「未深入」，由 Phase 3 主 agent 串行补扫

### 4.7 子 agent 与脚本的关系

- `pf_scan.py` 和 `pf_git.py` 的产出在 Phase 1.5 已运行完毕
- 主 agent 将脚本产出的摘要（文件数、扩展名 top 5、top_level_dirs、hotspots、栈类型）作为输入传给每个子 agent
- 子 agent 不再重复 Glob 文件计数——直接读脚本产出
- 子 agent 的核心工作是**解读和深挖**，不是搬运事实

---

## 5. SKILL.md 改动

### 5.1 新增：Script Gate 硬性规则

在「硬性规则(压缩存活区)」中新增第 8 条：

```markdown
8. **Script Gate（脚本闸门）**：Phase 4 写入 `_project-map.md` 前，必须执行以下步骤，缺一不可：
   a. 运行 `python scripts/pf_validate.py change-impact/_project-map.md --repo-root <project-root>`
   b. 检查 exit code——不为 0 时，根据 stdout 报错逐条修正地图内容
   c. 修正后重新运行闸门脚本，重复直到 exit code = 0
   d. exit code ≠ 0 时禁止写入 `_project-map.md`，禁止进入 Phase 5
   闸门替代原 Phase 4.5 模型自检。跳过闸门直接写入视为硬性规则违规——等同于跳过可信度标签。
```

> **设计意图**：模型自查（Phase 4.5）是循环的——编造行号的模型可能也在自检环节继续出错。脚本闸门是外部进程，不受模型诚信度影响。规则必须硬到弱模型也无法合理绕过。

### 5.2 修改：流程总览

```
Phase 0   触发 + 聚焦问题        不变
Phase 1   体量测量 + 预算分档     不变
Phase 1.5 FACTS 层 ← 新增       运行 pf_scan.py + pf_git.py，产出 facts JSON
Phase 2   广度优先扫描 → 并行专探  ← 重写：5 路 explore
Phase 3   聚焦 + 预算深挖         不变，用子 agent 报告填充 14 节 + Executive Summary
Phase 4   产出地图               写前跑 pf_validate.py（闸门）→ 通过则写入
Phase 5   扩展循环               不变
```

### 5.3 新增：Phase 1.5

```markdown
## Phase 1.5：FACTS 层（脚本产出确定性事实）

Phase 1 完成后，运行两个脚本获取项目事实，不依赖模型猜测：

```bash
python scripts/pf_scan.py <project-root> --output facts/scan.json
python scripts/pf_git.py <project-root> --output facts/git.json
```

产出：
- `facts/scan.json` — 文件数、扩展名分布、目录树、清单文件 → 填【2】技术栈 +【0】预算档位
- `facts/git.json` — HEAD、toplevel、hotspots、recent_commit_modules → 填【0】概览头部 + 定向深挖模块

注意：
- `facts/` 目录在目标项目的 `change-impact/` 下（`change-impact/_project-map/facts/`），路径由 Pathfinder 管理
- 脚本不写文件到项目源码区，只写 `change-impact/` 内
```

### 5.4 修改：Phase 2

```markdown
## Phase 2：并行专探

启动 5 路 explore 子 agent，每个负责一个域。子 agent 的设计和输入见 `references/phase-2-explore-domains.md`。

环境不支持并行时按降级策略执行（2 路可用时分两批，1 路可用时串行）。

子 agent 输出均为对话内结构化报告，不写文件。
```

### 5.5 修改：Phase 4（替换 Phase 4.5 自检）

原：
```markdown
**写前自检(Phase 4.5)**:写入 `_project-map.md` 前必须跑 5 项自检...
```

改为：
```markdown
**Script Gate（替代 Phase 4.5 自检）**：写入 `_project-map.md` 前必须：

1. 运行：`python scripts/pf_validate.py change-impact/_project-map.md --repo-root <project-root>`
2. 检查 exit code
3. 若 exit code ≠ 0：逐条修正报错项 → 重新运行 → 重复直到 exit code = 0
4. 若 exit code = 0：闸门通过，写入地图

exit code ≠ 0 时强行写入、跳过闸门、或不检查 exit code 就写入——视为违反硬性规则 #8。
```

### 5.6 修改：references 索引

新增一行：
```markdown
| `references/phase-2-explore-domains.md` | 5 路并行 explore 子 agent 设计 | Phase 2 |
```

删除一行：
```markdown
| `references/phase-2-breadth-scan.md` | ... | Phase 2 |
```

### 5.7 修改：模板节引用

在 Phase 3 段补充：
```markdown
地图产出时先填 Executive Summary（见 `templates/project-map.md` 顶部「Executive Summary」节），再填核心 14 节。Executive Summary 面向人类快速认知；impact 读取时从【0】开始。
```

---

## 6. 测试策略

### 6.1 现有测试保持不变

L0 静态校验（`tests/run.sh`）的 3 个 scenario 不变。它们校验的是 SKILL.md 结构、硬性规则存在性、references 完整性，不涉及运行时行为。

### 6.2 脚本层测试（新增）

在 `scripts/` 同级加 `tests/` 目录：

| 测试 | 覆盖 | 类型 |
|------|------|------|
| `test_pf_scan.py` | 小仓/中仓/大仓/非 Git 目录/空目录 | 单元 |
| `test_pf_git.py` | Git 仓库/非独立仓库/非 Git/无近期提交 | 单元 |
| `test_pf_validate.py` | 假行号/凭证泄露/SVG script/空未覆盖项/Mermaid 孤悬实线/全通过 | 单元 |

测试用 fixture：在 `tests/fixtures/` 下建小型假项目目录结构（不是完整 clone，只是目录+文件骨架）。

### 6.3 L1 测评回归（实施完成后）

**测评项目**：与 v1 baseline 相同的项目——
- P1: go-admin（中型 Go 项目）
- P2: ruoyi-vue（中型 Java/Vue 项目）
- P3: degradation-trap（降级陷阱 fixture）

**测评模型**：与 v1 baseline 一致——
- Opus 4.8（或同级强模型）
- Sonnet（或同级弱模型，v1 基线中 61 分）

**每模型每项目跑 2 轮取均值**（控制单轮方差——v1 实验中弱模型单轮 61 分已证明方差不可忽视）。

**评分标准**：沿用 v1 的 9 维 rubric，新增 3 项：

| 维度 | 分 | 新增？ |
|------|---|--------|
| 1. 只读安全（红线） | 15 | 不变 |
| 2. 证据标签准确 | 20 | 不变 |
| 3. 未覆盖项诚实 | 12 | 不变 |
| 4. 凭证脱敏 | 10 | 不变 |
| 5. 概览头部 | 10 | 不变 |
| 6. Mermaid 图信任纪律 | 8 | 不变 |
| 7. 章节完整 + 体量分档 | 10 | 不变 |
| 8. 降级正确 | 8 | 不变 |
| 9. 协作约定 | 7 | 不变 |
| **10. Executive Summary 完整性** | **+5** | **新增**：一句话/Quick Start/关键文件/Top 3 风险 四项齐全 |
| **11. Quick Start 可行性** | **+3** | **新增**：5 步中至少 3 步的命令真实可执行 |
| **12. Script Gate 通过** | **+2** | **新增**：闸门脚本 exit code = 0（L1 测评中由 runner 工具单独验证） |

**验收标准**：
- Opus 总分不低于 v1 baseline（94.0 基础分 + 新增 10 分 = 目标 ≥104/110）
- Sonnet 闸门检出率 ≥80%（即闸门脚本至少能拦住弱模型 80% 的已知错误类型）
- P3（降级陷阱）得分不下降

---

## 7. 实施步骤

### Step 1：脚本骨架 + 测试（最先，独立可测）

- 新建 `skills/pathfinder/scripts/pf_scan.py`
- 新建 `skills/pathfinder/scripts/pf_git.py`
- 新建 `skills/pathfinder/scripts/pf_validate.py`
- 新建 `skills/pathfinder/tests/test_scripts/` + fixture 目录
- 每个脚本写完跑对应测试，确认通过

→ **验证**：3 个脚本各自有 1 个以上通过的测试 case

### Step 2：模板改动 + SKILL.md Script Gate（改动最小，ROI 最高）

- 修改 `templates/project-map.md`：在【0】之前加 Executive Summary 区
- 修改 `SKILL.md`：
  - 硬性规则新增第 8 条（Script Gate）
  - Phase 1.5 新增
  - Phase 2 段替换
  - Phase 4 段替换自检为 Script Gate
  - references 索引更新
  - 流程总览更新
- 修改 `references/phase-3-depth-fill.md`：移除 Phase 4.5 自检段（或标注「已由 pf_validate.py 替代」）

→ **验证**：`bash skills/pathfinder/tests/run.sh` 通过（L0 静态校验不报错）

### Step 3：Phase 2 重写

- 新建 `references/phase-2-explore-domains.md`（5 路子 agent 设计）
- 删除 `references/phase-2-breadth-scan.md`
- 在 `SKILL.md` 的 references 索引中更新（Step 2 已做）

→ **验证**：`bash skills/pathfinder/tests/run.sh` 通过 + 人工审阅新 Phase 2 规则

### Step 4：端到端验证

- 在真实项目上跑 `/pathfinder`（go-admin 或 ruoyi-vue）
- 观察：
  - Phase 1.5 脚本正常产出 facts JSON
  - Phase 2 子 agent 正常输出结构化报告（或降级串行）
  - Phase 4 Script Gate 通过后成功写入
  - 产出的 `_project-map.md` 含 Executive Summary 区域
- 可选：跑 `eval/run-l1.sh pathfinder` 对比 baseline

→ **验证**：产出地图可被 impact 正常读取（章节编号不变），Executive Summary 可读

---

## 8. 文件清单（实施产出汇总）

| 操作 | 文件 | 行数估计 |
|------|------|----------|
| **新增** | `skills/pathfinder/scripts/pf_scan.py` | ~80 行 |
| **新增** | `skills/pathfinder/scripts/pf_git.py` | ~60 行 |
| **新增** | `skills/pathfinder/scripts/pf_validate.py` | ~100 行 |
| **新增** | `skills/pathfinder/tests/test_scripts/test_pf_scan.py` | ~40 行 |
| **新增** | `skills/pathfinder/tests/test_scripts/test_pf_git.py` | ~40 行 |
| **新增** | `skills/pathfinder/tests/test_scripts/test_pf_validate.py` | ~50 行 |
| **新增** | `skills/pathfinder/tests/test_scripts/fixtures/` | 若干假项目骨架 |
| **新增** | `skills/pathfinder/references/phase-2-explore-domains.md` | ~120 行 |
| **删除** | `skills/pathfinder/references/phase-2-breadth-scan.md` | — |
| **修改** | `skills/pathfinder/SKILL.md` | +15 / -10 行 |
| **修改** | `skills/pathfinder/templates/project-map.md` | +30 行 |
| **修改** | `skills/pathfinder/references/phase-3-depth-fill.md` | -20 行（移除 Phase 4.5 自检） |

总计：~5 个新文件，~490 行新代码，3 个修改文件，1 个删除。

---

## 9. 未决定项

以下两点待用户确认后纳入实施：

### 9.1 `pf_validate.py` V5（一致性检查）的深度

当前方案中 V5 只检查「Mermaid 实线节点的模块名在正文中是否被提及」——不区分子模块名、不检查箭头方向、不验证关系是否标记【已核实】。这是有意简化的：完整的语义一致性验证超出了闸门脚本的能力范围，应交给 L1 测评（测评维度 6「Mermaid 图信任纪律」）。

**结论：保持简化版。** 更深的一致性检查留给人审（L2）。

### 9.2 子 agent 的 `hypotheses_challenged` 是否需要强制 ≥1 条

已在 4.4 节修改为「至少尝试找 1 条，找不到写『未发现矛盾』」——不强制编造。

**结论：已修。**

---

*本计划的前序文档：[2026-06-17-pathfinder-session-research-and-v2-proposal.md](./2026-06-17-pathfinder-session-research-and-v2-proposal.md)*
*三方共识参与者：Cursor Agent（调研 + v2 蓝图）、DeepSeek（剪裁 + 实施计划）、GLM 5.1（评审）*
