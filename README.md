# Blue SkillHub

Blue SkillHub 是一套面向 AI 编码助手的工作流工具。无论是把一个模糊想法说清楚、快速看懂陌生项目，还是修改已有系统，都有对应的工具可以使用。

开源模型已经能完成不少编码任务，但在长任务和高风险变更中仍不够稳定：它可能理解错需求、漏掉调用方、跳过验证，或者把尚未完成的工作说成已经完成。这个仓库不试图让模型变得更聪明，而是把容易丢失的意图、项目事实和执行状态写进文件，再让脚本检查其中能够自动验证的部分。

仓库里的三项核心 Skill 可以独立使用，也可以按需配合。

## 项目定位

| Skill | 什么时候用 | 主要作用 |
|---|---|---|
| **IntentAnchor** | 只有一个模糊想法，还没形成 PRD；也适用于系统转换和已有系统新增能力 | 把要做什么、不做什么和不可妥协项整理成 `INTENT.md` |
| **Pathfinder** | 刚接手一个不熟悉的现有项目 | 只读梳理技术栈、模块、入口、数据和风险区域，产出项目地图 |
| **ImpactRadar** | 准备修改已有系统 | 分析改动会影响哪些代码、接口、数据和测试，并按步骤执行 |

这套工具不负责一键搭建完整系统。对于 0→1 项目，IntentAnchor 先帮你把方向说清楚；面对已有代码时，可以用 Pathfinder 摸清项目，再由 ImpactRadar 分析并执行改动。

ImpactRadar 会根据任务风险选择流程。简单改动使用 `light` 模式，只保留必要检查；复杂或高风险改动使用 `full` 模式，补齐需求、设计、实施和验证文档。

你不必先写一份复杂的 Prompt。模糊想法可以通过 IntentAnchor 的三重锚定逐步说清楚；分析已有项目时，则以代码、配置和命令结果为准。ImpactRadar 到了实际写入阶段，仍需用 `确认 Step N` 明确授权。

Pathfinder 和 ImpactRadar 完成一次任务后，会在回复中附上一段简短记录，包括所用模型、运行模式、验证结果、是否被检查拦下过，以及最后的结果。这段记录默认只留在对话中，不会自动写入仓库。

如果三项核心 Skill 在运行中发现了一个可能值得改进自身的问题，会在收尾时用一句话询问是否记录。你只需要回复“记录”或“不用”；内部编号、复现和回归由维护流程处理，不要求普通用户了解。

## 3 分钟上手

按你的场景选择最短路径。

1. 安装需要的 Skill。

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\intent-anchor" "$env:USERPROFILE\.claude\skills\intent-anchor" -Recurse -Force
```

Codex 用户把 `.claude\skills` 换成 `.codex\skills` 即可。其他安装方式见 [安装与验证清单](docs/install-and-verify-checklist.md)。

2. 根据任务选择入口。

如果还在构思 0→1 新产品，或者需求比较模糊：

```text
/intent-anchor
我想做一个帮助开发者整理跨会话工作进度的工具，但还没想清楚具体功能。
```

如果已经进入现有项目，需要先摸底或分析变更：

```text
/pathfinder
这个项目我刚接手，先帮我只读摸底。

/impact
我想删除 sys_user.remark 字段，先做影响分析，不要直接改代码。
```

`/intent-anchor` 不生成代码，只负责在头脑风暴或 PRD 之前产出 `INTENT.md`。`/impact` 支持 Java、Node.js、Python、Go 和前端项目等多种技术栈。如果已经熟悉项目结构，可以跳过 `/pathfinder`，直接使用 `/impact`。

3. 使用 ImpactRadar 改代码时，按步骤确认。

```text
确认 Step 2
```

只有明确回复 `确认 Step N` 才算授权。`继续`、`好的`、`全部确认` 都不算。Claude Code 用户可以启用 `.claude/hooks/impact-write-gate.*`，在工具执行前再次检查授权。

## 里面有什么

### Prompt 工具箱

[prompt/](prompt/)

这里放的不是大而全的流程，而是遇到某个具体麻烦时，可以直接发给 AI 的指令：

- [开工前调研开源项目](prompt/open-source-project-research.md)：脑子里已经有个项目想法，但不想让 AI 凭空搭架子：先找几个真正做过类似事情的开源项目，看清哪些值得借、哪些坑别踩，再拿方案回来确认。
- [跨会话交接](prompt/session-handoff.md)：今天做到这里，明天还要接着干：把目标、进度、卡点和踩过的坑写进 `HANDOFF.md`，下次不用从头解释。
- [无交接恢复现场](prompt/workspace-recovery.md)：上个会话突然没了，又没来得及交接：从 Git、diff 和项目文件里尽量还原做到哪一步。
- [卡住时重新梳理](prompt/stuck-reassessment.md)：同一个报错越改越乱：先停手，分清事实和猜测，只做一个最能缩小范围的验证。
- [找外援排障](prompt/expert-escalation.md)：当前模型绕了几轮仍没解出来：把复现方法、失败尝试和代码现场整理好，交给更擅长的模型直接接手。
- [需求变更对账](prompt/requirement-change-reconciliation.md)：需求前后改了几轮，怕新旧说法一起执行：重新整理当前有效要求，并找出已经过时的实现。
- [提交前整理改动](prompt/pre-commit-cleanup.md)：准备提交，却发现 diff 里什么都有：把正式修改、调试残留和用户原有改动分开，再决定怎样清理和暂存。
- [生成独立验收指令](prompt/independent-review-request.md)：实现会话说“已经完成”还不够：生成一份完整验收指令，交给新会话按原始需求从头核实。

使用“开工前调研开源项目”时，把 Prompt 里的占位内容换成项目想法，或者填入现有 `INTENT.md` 的路径，再整段发给能够访问 GitHub 的 AI。它会先交付项目对比和实现方案；你确认方案前，不会创建项目或写代码。想法还很模糊时，先用 IntentAnchor 把“要做什么”说清楚，再进入开源调研。

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

律刃是一组写给 AI 编码助手的通用行为规则，共 8 条编码规则和 1 条中文表达要求。它要求模型先弄清目标和上下文，再动手修改；遇到不确定的地方要明确说明，不能靠猜。

这套规则既适用于新项目，也适用于已有项目。可以放进 `CLAUDE.md`，也可以按需复制成 Codex 项目的 `AGENTS.md`。它不绑定具体开发流程，修复 Bug、重构、补测试和普通开发都能使用。

律刃最初参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后来结合中文编码任务和复杂变更持续调整。

v3.2 通过了 Claude Code + MiniMax M3 的两轮稳定性复测；v3.3 新增的五条规则也通过了 Step 3.7 Flash 的 6 个场景测试。详细记录见 [律刃 README](claudecode行为规范/ruleblade/README.md)。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

为支持 MCP 的 AI 客户端提供网页搜索。它支持 Google、Bing、Brave 和 DuckDuckGo，既可以只返回搜索摘要，也可以继续打开网页提取正文。Cursor、CodeBuddy 和 Claude Desktop 等客户端都能接入。

### Pathfinder 领航

[skills/pathfinder/](skills/pathfinder/)

**先把项目看懂，再决定怎么改。** Pathfinder 适合刚接手、还不熟悉的现有项目。它不会修改代码，而是通读项目后生成一份项目地图，内容包括技术栈、核心功能、架构分层、关键入口、主要数据模型、运行方式、权限流程和风险区域。

Pathfinder 最重要的约束是不能把猜测写成事实。每条结论都要标成 `【已核实: 证据】` 或 `【推断: 待验证】`；如果当前目录不是独立 Git 仓库，它不会误用父目录仓库的提交信息；没有深入查看的部分也会明确列出。

项目地图保存在 `change-impact/_project-map.md`。ImpactRadar 启动时会先读取这份地图，用它定位可能相关的文件；其中标为推断的内容仍需回到源码核实。没有地图时，ImpactRadar 也能照常工作，因此 Pathfinder 不是强制的前置步骤。

项目变化后，可以继续深入某个模块、对照当前代码更新地图，或者重新生成整份地图。更新时会比较地图记录的 Git HEAD 与当前 HEAD，替换已经过期的内容。

如果客户端提供只读的 code graph 或 repo-map MCP，Pathfinder 会先用索引查找入口和依赖关系，再回到源码核实。索引不可用、结果不完整或需要在项目里写缓存时，就改用普通文件扫描。

Pathfinder 只会写自己管理的项目地图和 `facts` 文件，不会修改项目源码、配置或业务数据。设计复盘见 [Pathfinder 设计记录](docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。

### ImpactRadar

[skills/impact/](skills/impact/)

ImpactRadar 用于修改已有系统。新增功能、调整字段或接口、修改权限与配置、重构旧代码，都可以先用它查清影响范围，再决定怎么实施。它支持 Java、Node.js、Python、Go 和前端项目等多种技术栈；Phase 2 会识别当前项目使用的技术栈，并从 `profiles/` 加载对应规则。

简单改动使用 `light` 模式，只生成一页摘要；复杂或高风险改动使用 `full` 模式，补齐需求、设计和实施文档。分析过程中，能从代码确认的事实由 AI 自行查证，涉及产品取舍、兼容策略或数据风险的决定则交给用户。

进入实施阶段后，每一步写操作都需要当前会话中的 `确认 Step N`。删除公开接口、修改数据库结构、调整权限等高风险操作必须单独确认，不能和其他步骤一起授权。Claude Code 用户建议启用 `.claude/hooks/impact-write-gate.*`，在工具真正执行前再检查一次授权。

`impact_validate.py` 提供 V1–V22 共 22 项自动检查，用来发现文档缺失、执行记录不完整、状态不一致和改动遗漏等问题。在 D19 真实交付测试中，MiniMax M3 三次提前声称已经完成，三次都被不同的检查拦下，修正后才通过验收。

长任务的当前状态保存在 `change-impact/{需求名称}/_active-state.md`。这个文件只记录待执行步骤、文档状态和未确认事项，不能代替用户授权。团队还可以把代码规范写进 `change-impact/_style-rules.md`，供后续分析和校验使用。

如果客户端提供 code graph MCP，也可以先用它查找定义和引用；没有时就使用普通代码搜索。

当前版本为 v5.8。完整机制、版本记录和评测数据见 [ImpactRadar README](skills/impact/README.md)。

### IntentAnchor 意图锚定

[skills/intent-anchor/](skills/intent-anchor/)

IntentAnchor 解决的是开发前的需求理解问题。当你只有一个模糊想法，还没写 PRD 或拆任务时，它会通过对话把想法整理成一份 `INTENT.md`，明确要保留什么、推迟什么、放弃什么，以及每个决定究竟来自用户确认还是模型受托选择。

它不依赖现成代码。构思 0→1 新产品、把一个系统转换成另一个系统，或者给已有系统增加能力，只要方向还不够清楚，都可以先使用 IntentAnchor。

它会从三个角度提问：

- **类比**：有没有类似的产品或做法？哪些部分值得参考？
- **反面**：现在怎么解决？最不满意的地方是什么？
- **场景**：如果已经做好，第一次打开时会先做什么？

这三个角度按信息缺口选用，不要求机械完成固定数量。系统转换会完整盘点源系统能力；0→1 项目即使没有类比物，也可以从现有做法和使用场景出发。能力清单会记录 `保留 / 推迟 / 放弃 / 待确认`，并区分“用户明确确认”“用户授权模型决定”和“模型建议”。写入前还会执行 S1-S5 语义复核，把证据和中间判断留给用户检查。

`intent_validate.py` 运行 9 项结构与交叉引用检查，用来发现未确认能力、决策来源冲突、统计不一致和缺少全文确认等问题。它不能判断语义是否正确；PASS 只表示文件满足当前结构契约。

IntentAnchor 负责在开发前把意图说清楚，ImpactRadar 负责在开发中让改动符合已经确认的要求。两者可以衔接，也可以单独使用。详细设计见 [IntentAnchor README](skills/intent-anchor/README.md)。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用的图片理解工具。提供图片和分析模板后，它会调用视觉模型返回结构化结果，适合为只支持文本的 AI 补充图片分析能力。

### 统一测评体系

[docs/skill-eval/](docs/skill-eval/) + [eval/](eval/)

Pathfinder 和 ImpactRadar 共用一套真实项目回归测试；IntentAnchor 单独测试校验脚本的实际行为，并已接入 CI。这里不采信模型自己报告的结果，而是重新运行检查脚本和交付测试，以实际文件和命令结果为准。

测试分为三层：

| 层 | 测什么 | 怎么跑 | 成本 |
|---|---|---|---|
| L0 静态检查 | 强制规则、文件引用、共享约定、测试副本和风格规则 | `bash skills/<skill>/tests/run.sh` | 无模型费用 |
| L1 行为测试 | 让另一个 AI 扮演用户执行用例，再自动评分并检查安全规则 | `bash eval/run-l1.sh <skill>` | 低成本模型 |
| L2 人工抽查 | 提问质量、文档可读性和项目地图质量 | 人工检查，可选多模型复核 | 较高 |

每次修改 Skill 后，L1 都会生成评分卡，并和上一版基线逐个用例比较。只要出现原本通过的规则变为失败、任一维度下降 3 分及以上，或新增 P0/P1 问题，这一版就不能发布。

详细设计见 [测评体系设计](docs/archive/2026-06/2026-06-13-skill-eval-system-design.md)，运行方法见 [测评手册](docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md)。

真实项目测试放在 [eval/real-projects/](eval/real-projects/)，覆盖 Java 后端、Node API、Python 全栈、前端以及 monorepo/非 Git 共 5 类项目。测试会让模型在隔离副本中运行 Pathfinder 和 ImpactRadar，记录实际改动、验证命令、执行过程，以及检查失败后的修正结果。

目的不是证明模型不会出错，而是确认错误能否被及时发现。

目前记录了 E-001 到 E-010 共 10 类绕过流程或检查的情况。每一类都有对应的自动检查，或者明确说明了工具无法保证的边界，详见 [问题记录](eval/real-projects/escape-ledger.md)。

[真实项目测试手册](eval/real-projects/runbook.md) 规定：评分必须以独立重跑检查脚本的结果为准，不能引用执行模型自己写的总结；每次运行也必须使用独立的项目副本。

后续待处理的问题统一记录在 [Skill 改进清单](docs/skill-iteration-backlog.md)，并按优先级说明当前状态和处理条件。

截至 2026-07-04，在当时的模型版本和 56 条测试结果中，**Composer 2.5 Fast 是 Pathfinder 与 ImpactRadar 表现最稳定的低成本模型**。它共有 22 条结果：9 条 PASS、7 条 GATE-RECOVERED、3 条 PASS-WARN、2 条 FAIL、1 条 UNVERIFIED。

这个结论只代表当时的测试范围，不应视为长期不变的模型排名。详细数据见 [2026-07-04 测评汇总](docs/handoff-summary-2026-07-04.md)。

## 研究与实验记录

### Not ACE 上下文检索探索

2026 年 6 月，项目针对 [Not ACE](https://not-ace.ame.rip/) 做了一轮上下文检索实验。这部分内容不是可安装的 Skill，而是律刃和 ImpactRadar 的研究资料，完整记录保存在 [docs/not-ace-exploration/](docs/not-ace-exploration/)。

这轮实验的结论是：Not ACE 不能代替 `rg`，更适合先按语义找出可能相关的上下文，再回到源码核实。

在这轮测试中，它让 MiniMax M3 的表现更稳定，也减少了 GLM-5.1 的耗时和费用；但在 Kimi K2.6、GLM-5 和 DeepSeek V4 系列上没有得到稳定收益。DeepSeek V4 Pro 和 Flash 通过硅基流动接入，因此结果不能代表官方渠道的模型表现。

其他研究和测试记录：

- [ImpactRadar 真实案例复盘](docs/archive/2026-06/impact-real-case-study.md)：长会话和多步骤变更中发现的问题。
- [MiniMax M3 复测计划](docs/archive/2026-06/impact-m3-next-regression-plan.md)：下一轮回归测试的范围和方法。
- [多会话写入授权测试方案](docs/archive/2026-06/impact-multisession-write-gate-test-plan.md)：检查中断和恢复后是否仍需重新授权。
- [律刃与 ImpactRadar 边界检查](docs/archive/2026-06/release-positioning-check-2026-06-08.md)：核对两者的职责是否冲突或遗漏。
- [Not ACE 多模型测试](docs/archive/2026-06/not-ace-benchmark-research.md)：记录不同模型使用 Not ACE 时的表现。
- [三项核心 Skill 的改进依据](docs/archive/2026-06/agent-iteration-conclusions.md)：从测试结果中整理出的后续调整方向。
- [ImpactRadar 回归测试约定](docs/skill-eval/regression.md)：修改 Skill 后如何复测。
- [历史测试材料](docs/archive/2026-06/benchmarks/)：2026-06-09 之前的写入授权测试和模型能力测试，现已归档。

## 致谢

律刃最初参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后来根据中文编码任务和复杂变更测试不断调整。

“改代码前先查调用方和引用方，找到后再判断哪些必须同步修改”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提交的 GitHub issue。律刃和 ImpactRadar 都采纳了这项建议，以减少遗漏接口、生成文件、测试或注册位置的情况。

ImpactRadar 的长期任务、暂停后恢复、接口返回检查、验证等级、多会话授权和写入路径限制，也参考了 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实案例。这些案例帮助发现了长会话、多步骤迁移、非 Git 项目和延迟确认中的问题。

## 快速验证

克隆仓库后，可以按下面的步骤做一次基本检查。

### 1. 使用律刃规则

把规则文件复制到目标项目根目录：

```powershell
Copy-Item "claudecode行为规范/ruleblade/CLAUDE.md" "你的项目路径/CLAUDE.md"
```

然后在目标项目中启动 Claude Code，确认它能读取根目录的 `CLAUDE.md`。Codex 用户可以把同一份内容放进 `AGENTS.md`。

### 2. 启动网搜 MCP

先安装依赖和浏览器：

```powershell
cd mcp/web-search-mcp
npm install
npx playwright install chromium
node ./dist/index.js
```

出现下面两行，说明服务已经启动：

```text
Web Search MCP Server started
Waiting for MCP messages...
```

配置 MCP 客户端时，`args` 必须使用本机绝对路径。例如，仓库位于 `E:\agent\blue-skillhub` 时可以这样写：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\blue-skillhub\\mcp\\web-search-mcp\\dist\\index.js"]
    }
  }
}
```

代理、搜索引擎和环境变量的配置方法见 [网搜 MCP README](mcp/web-search-mcp/README.md)。

### 3. 运行 VL 识图

先列出可用模板：

```powershell
pip install requests
python skills/vl-vision/vl_vision.py --list-templates
```

配置 `SILICONFLOW_API_KEY` 后，选择一张图片进行测试：

```powershell
$env:SILICONFLOW_API_KEY="sk-your-key"
python skills/vl-vision/vl_vision.py path/to/image.png
```

### 4. 安装三项核心 Skill

安装命令见上文 [3 分钟上手](#3-分钟上手)。使用时需要注意以下边界：

- `intent-anchor` 只负责澄清意图并生成 `INTENT.md`，不会直接编写代码。
- `pathfinder` 只读查看项目源码、配置和 Git 信息。它只会写自己管理的项目地图和 `facts` 文件。
- `impact` 用于修改已有系统，Phase 2 会识别技术栈并加载对应规则。
- 使用 `impact` 写文件、改代码、执行 DDL/DML、修改配置、删除内容或修复测试前，都必须由用户明确回复 `确认 Step N`。
- `yes`、`继续` 和 `全部确认` 都不能代替某个步骤的明确确认。
- 会话中断后，`_active-state.md` 只能帮助恢复进度，不能作为新的写入授权。

中断后的正常交互如下：

```text
用户：继续
AI：我先读取 change-impact/删除用户备注/_active-state.md、030-implementation.md、
060-preflight.md 和 090-execution-record.md，并复核当前 Git/磁盘状态。
当前待执行的是 Step 2，但“继续”不代表授权。Step 2 将修改
E:\project\ruoyi-system\src\main\resources\mapper\system\SysUserMapper.xml，
回滚方式是恢复该文件的字段映射，验证方式是检查 Mapper 引用并运行对应测试。
请回复：确认 Step 2

用户：确认 Step 2
AI：现在执行 Step 2。完成后会更新 090-execution-record.md 和 _active-state.md。
```

## 常见问题（FAQ）

- **Codegraph MCP 显示已连接，但没有可用工具（No tools）**：通常是因为直接运行全局 `serve --mcp` 时，没有找到项目根目录中的 `.codegraph/` 索引。项目级启动脚本、`--path` 参数和 4 个工具的检查方法见 [Codegraph 排查说明](docs/install-and-verify-checklist.md#codegraph-mcp-显示已连接但没有工具no-tools)。

  即使 MCP 不可用，Pathfinder 和 ImpactRadar 也会改用普通的文件读取和搜索工具，基本流程不受影响。

## 目录速览

```text
blue-skillhub/
├── .claude/
│   └── hooks/                # 推荐启用的 Claude Code 写入前检查
├── claudecode行为规范/
│   └── ruleblade/
├── prompt/                   # 可直接复制使用的 Prompt
├── docs/
│   ├── skill-eval/          # 测评体系说明
│   ├── not-ace-exploration/
│   ├── archive/2026-06/     # 历史文档
│   ├── install-and-verify-checklist.md
│   ├── output-quality-review-2026-06-25.md
│   └── skill-optimization-roadmap-2026-06-25.md
├── eval/                     # 测试用例、历史结果和评分基线
│   ├── cases/<skill>/        # 可重复运行的测试用例
│   ├── runs/<date>-<skill>@<commit>/  # 各次运行的评分卡
│   ├── baselines/<skill>.json         # 当前基线指针
│   ├── schemas/              # 测试用例和评分卡格式
│   └── scripts/              # 评分与基线对比脚本
├── mcp/
│   └── web-search-mcp/
└── skills/
    ├── pathfinder/
    ├── impact/
    ├── intent-anchor/
    └── vl-vision/
```
