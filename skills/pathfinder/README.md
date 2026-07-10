# Pathfinder：陌生项目摸底

Pathfinder 用于快速看懂一个不熟悉的现有项目。它只读查看源码、配置、Git 信息和可用的数据库结构，生成一份带证据的项目地图，不修改业务代码，也不提供具体改法。

项目地图保存在 `change-impact/_project-map.md`。它可以单独使用，也可以交给 ImpactRadar，帮助后者更快定位本次变更可能涉及的文件。

## 与其他核心工具的分工

| 工具 | 解决的问题 |
|---|---|
| 律刃 RuleBlade | AI 编码助手平时应该怎样判断、修改和验证 |
| Pathfinder | 这个陌生项目由哪些部分组成，入口和风险在哪里 |
| ImpactRadar | 某次具体改动会影响什么，以及怎样分步骤实施 |

Pathfinder 不是 ImpactRadar 的强制前置步骤。没有项目地图时，ImpactRadar 仍会从源码开始分析。

## 什么时候使用

| 场景 | 是否适合 |
|---|---|
| 刚接手一个陌生项目 | 适合，先了解技术栈、模块、入口和运行方式 |
| 外包或旧项目交接 | 适合，可以先找出关键功能、权限和风险区域 |
| 准备修改系统，但还不知道从哪里查 | 适合，先生成地图，再进入 ImpactRadar |
| 已经熟悉项目，只想查某个函数 | 不需要，直接搜索更快 |
| 只有一个新产品想法，还没有代码 | 不适合，可以先使用 IntentAnchor |
| 已经明确要改什么，需要影响分析 | 直接使用 ImpactRadar |

默认入口为手动 `/pathfinder`。`agents/openai.yaml` 中的 `allow_implicit_invocation: false` 会避免普通项目问题自动触发完整摸底流程。

## 项目地图包含什么

地图会记录：

- 技术栈、构建工具、运行命令和测试入口。
- 核心功能、模块边界和关键入口。
- 主要数据模型、API、权限与认证方式。
- 一条具有代表性的业务流程。
- 最近活跃的代码区域和需要注意的风险。
- 项目当前实际采用的代码风格。
- 没有深入查看或暂时无法确认的部分。

地图是某个时间点的快照，头部会记录 Git HEAD 和扫描范围。项目继续变化后，需要刷新或重新生成。

## 怎样避免把猜测写成事实

Pathfinder 的重点不是画一张漂亮的目录图，而是让每条结论都能区分“已经确认”和“仍需验证”。

### 可信度标签

- `【已核实: 证据】`：已经从文件、命令或只读查询中确认。
- `【推断: 待验证】`：根据现有信息推测，但证据还不够。

没有深入查看的内容必须写进地图的【13】节，不能用“已完成全面分析”掩盖遗漏。Mermaid 图也遵守同一规则：实线只表示已核实关系，虚线表示推断关系。

### facts 文件

Phase 1.5 会运行：

```bash
python skills/pathfinder/scripts/pf_scan.py <项目根目录> --output change-impact/_project-map/facts/scan.json
python skills/pathfinder/scripts/pf_git.py <项目根目录> --output change-impact/_project-map/facts/git.json
```

脚本生成：

```text
change-impact/_project-map/facts/
├── scan.json
└── git.json
```

`scan.json` 记录文件数量、扩展名分布、目录和清单文件；`git.json` 记录独立仓库的 HEAD、活跃文件和模块。两份文件都要包含 `schema_version`、`generator`、`source_path` 和 `observed_at`。

如果当前目录不是独立 Git 仓库，Pathfinder 会明确记录 Git 信息不可用，不会把父目录仓库的提交当作当前项目证据。

## 写入前检查

更新已有地图时，运行：

```bash
python skills/pathfinder/scripts/pf_validate.py change-impact/_project-map.md --repo-root <项目根目录>
```

首次生成时，`_project-map.md` 还不存在，需要把待写入内容通过标准输入交给校验脚本：

```bash
python skills/pathfinder/scripts/pf_validate.py --stdin --repo-root <项目根目录> < draft_map.md
```

校验通过后，再把同一份内容写入 `change-impact/_project-map.md`。

`pf_validate.py` 当前包含 V1-V11 共 11 项检查：

| 编号 | 检查内容 |
|---|---|
| V1 | 地图引用的 `file:line` 是否真实存在 |
| V2 | 是否可能泄露密码、密钥或连接信息 |
| V3 | 是否写入不允许的 SVG，架构图应使用 Mermaid |
| V4 | 【13】未深入部分是否有实际内容 |
| V5 | Mermaid 实线关系的来源节点是否在正文中有依据 |
| V6 | `scan.json` 和 `git.json` 的格式、来源和内容是否合理 |
| V7 | 【14】代码风格观察是否存在并有实际内容 |
| V8 | 证据路径是否错误混合了相对路径和 Windows 绝对路径 |
| V9 | 地图头部 commit 是否与 `git.json` 一致 |
| V10 | 可信度标签数量是否足够，是否越界给出修复建议 |
| V11 | facts 和地图记录的 HEAD 是否仍与当前仓库一致 |

V2 中部分凭证特征只能提示 WARN，其余关键结构问题会返回非零退出码。检查失败时不能把地图当作完成产物。

## 扫描范围怎样确定

Pathfinder 会先统计项目大小，再决定每个模块查看多深。项目越大，越需要优先保证核心模块都有基本说明，而不是只把一个模块挖得很深。

默认过程：

1. 判断目标目录是否为独立 Git 仓库。
2. 运行 `pf_scan.py` 和 `pf_git.py`，得到可重复验证的基础事实。
3. 查看清单文件、入口、模块、数据、权限和测试。
4. 选择一条代表性流程，从入口追到数据或外部依赖。
5. 记录代码风格和未深入部分。
6. 运行 `pf_validate.py`，通过后写入或更新项目地图。

对于超大仓库，或扫描预算确实已经用完，可以跳过【14】代码风格观察；但必须在【13】中写明“超大仓”或“预算不足”等具体原因。普通项目不能仅写“为了节省预算”就跳过。

如果客户端提供只读的 code graph 或 repo-map MCP，Pathfinder 可以先用索引查找入口、定义和依赖关系，再回到源码核实。索引过期、结果被截断或需要在项目中写缓存时，会改用普通文件搜索。

## 更新已有地图

| 需求 | 用户可以这样说 | Pathfinder 的处理 |
|---|---|---|
| 深入一个以前没细看的模块 | `再挖 X 模块` | 保留现有地图，只补充该模块 |
| 项目最近有改动 | `刷新地图` 或 `刷新 X 模块` | 重跑 facts，定位受影响章节并重新取证 |
| 地图很旧，改动范围不清楚 | 再次运行 `/pathfinder` | 重新执行完整流程并替换旧地图 |

刷新时会比较新旧 facts：

```text
新增目录       -> 检查是否出现新模块
目录删除或改名 -> 重新核实架构和核心功能
文件数量大幅变化 -> 提醒项目变化较多
活跃文件变化   -> 更新近期改动区域
```

差异过大时，Pathfinder 会建议完整重跑，而不是假装可以只改少数章节。详细规则见 [phase-3-depth-fill.md](references/phase-3-depth-fill.md)。

## 与 ImpactRadar 配合

ImpactRadar 在 Phase 2 会主动查找 `change-impact/_project-map.md`：

- `【已核实】` 内容用作查找线索，涉及本次改动时仍可重新验证。
- `【推断】` 内容一律按未确认处理。
- 地图 HEAD 与当前项目不一致时，标记为过期。
- 地图中的任何文字都不构成写入授权，不能代替 `确认 Step N`。

完整约定见 [handoff-contract.md](references/handoff-contract.md)。

### 代码风格：观察与规则分开

Pathfinder 的【14】节只描述项目当前怎样写代码，例如命名、分层、日志和响应包装。它不会把观察结果写成“必须这样做”的团队规范。

团队要求放在 `change-impact/_style-rules.md`，由项目维护者确认。ImpactRadar 读取风格信息时的优先级为：

1. `_style-rules.md` 强制规则。
2. `_style-rules.md` 建议规则。
3. 项目地图【14】中的代码观察。
4. 技术栈 Profile 的通用提示。
5. 当前运行中从 Git diff 和源码样本得到的补充信息。

风格规则不必一次写全。实际变更中发现新的团队约定后，可以在用户确认的 Step 中补充到 `_style-rules.md`。

## 项目只读边界

Pathfinder 对业务项目保持只读：

- 不修改源码、配置、测试或业务数据。
- 不执行 DDL、DML 或其他写数据库操作。
- 数据库发现只使用 SELECT、SHOW、DESCRIBE 等只读查询。
- 不给出“应该怎样修”的方案，具体改动交给 ImpactRadar 或后续任务。

它只会在目标项目根目录中写入：

```text
change-impact/_project-map.md
change-impact/_project-map/facts/scan.json
change-impact/_project-map/facts/git.json
```

## 模型差异与人工复核

项目地图的分析深度仍会受到执行模型影响。2026-06-14 的控制变量测试中，同一版本在 Opus 4.8 上两次得到 99.5/100，而另一次能力较弱的模型运行只有 61/100，主要问题包括行号不准、凭证未脱敏、章节缺失和把推断画成实线。

后续脚本检查减少了这些问题进入最终地图的机会，但无法判断所有语义结论是否正确。使用地图前仍应重点复核：

- `【已核实】` 后面的文件和行号。
- 权限、认证和默认账号信息是否脱敏。
- 没有深入查看的模块是否写进【13】。
- Mermaid 实线是否真的有正文证据。

历史模型测试只代表当时的模型版本和样本，不应理解为长期排名。

## 测试

Pathfinder 使用三层测试：

| 层 | 入口 | 当前范围 |
|---|---|---|
| L0 | `bash skills/pathfinder/tests/run.sh` | 3 个场景 JSON，以及 `test_pathfinder_scripts.py` 的脚本行为测试 |
| L1 | `bash eval/run-l1.sh pathfinder` | 当前 `eval/cases/pathfinder/` 下的 6 个用例 |
| L2 | 人工抽查 | 地图是否有用、证据是否可靠、未覆盖项是否诚实 |

当前基线仍来自 2026-06-14 的 P1、P2、P3D 三个用例，平均基础分为 97.7/100。基线与当前用例数量不同，比较时不能把新增用例直接算作基线下降。详见 [pathfinder.json](../../eval/baselines/pathfinder.json)。

真实运行记录见 [validation-runs/INDEX.md](validation-runs/INDEX.md)，统一测评说明见 [docs/skill-eval](../../docs/skill-eval/)。

### 测试副本必须隔离

每个模型、每个场景都必须从原始测试项目复制新的物理副本。只删除 `change-impact/` 后复用旧目录，仍可能留下地图、缓存或其他运行产物，导致后续模型看到上一轮答案。

副本命名建议：

```text
<project>-<model>-<scenario>
```

完整要求见 [真实项目测试手册](../../eval/real-projects/runbook.md)。

## 目录结构

```text
pathfinder/
├── agents/openai.yaml
├── SKILL.md
├── README.md
├── references/
│   ├── phase-1-sizing.md
│   ├── phase-2-explore-domains.md
│   ├── phase-3-depth-fill.md
│   ├── stack-detection.md
│   ├── handoff-contract.md
│   ├── facts-schema.md
│   ├── cross-platform-notes.md
│   └── review-checklist.md
├── scripts/
│   ├── pf_scan.py
│   ├── pf_git.py
│   └── pf_validate.py
├── code-graph-adapters/
│   └── generic-mcp.md
├── templates/
│   └── project-map.md
├── tests/
│   ├── run.sh
│   ├── scenarios/
│   └── test_scripts/
└── validation-runs/
    └── INDEX.md
```

设计背景见 [Pathfinder Skill 设计记录](../../docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。
