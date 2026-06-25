# Blue SkillHub 认知地图

> 本地图由 Pathfinder(领航)生成,供 impact/impact-pro 当 L1 导航上下文。
> 地图是**导航图不是权威源**:`【推断】`项动手前必须重新取证。
> 特殊说明:本地图是 Pathfinder 对**自身仓库**的反身摸底(自检样本),目标项目 = skill 仓库本身。

## 【0】元信息(信任契约)

```
生成时间: 2026-06-15 16:40:26 +0800
基于 commit: 006ffde0bcf3bed25f16995e29a52ffabc7812de (master)
预算档位: 中仓(tracked 文件 355 / 目录 73)
聚焦信号: 整体摸个底(均匀全景)
探测覆盖度:
  已深入: skills/(4 skill 结构 + 三 skill 的 SKILL.md/铁律/profiles/templates)
           ruleblade、eval(三层体系 + L1 runner)、mcp/web-search-mcp、README、gitignore、hooks
  未深入: web-search-mcp/src 源码细节(只看了 dist 清单 + package.json)
           docs/archive/(历史文档,只列名未读内容)、mcps/(工具 schema 镜像未逐个读)
           根目录大体积会话日志 *.txt(132–139KB,未读——可能含敏感对话内容)
结构索引:
  status: unavailable
  tool: none
  coverage: 未知(无 codegraph 索引)
```

## 【1】一句话概述

- **这是个什么项目**:作者(blue / betterblueblue)的个人 AI 编码工具箱,把日常用 AI 写代码时反复出现的痛点(模型会猜、会多改、不主动查资料、看不了图、接手陌生项目慢、在已有系统里做变更不稳)收敛成一组可单独使用的**规则 + Skill + MCP + 测评体系**。 【已核实: README.md L3-L7】

- **给谁用**:自己为主,也面向可复用安装的他人(`Copy-Item` 到 `.claude/skills` 或 `.codex/skills`)。【已核实: README L13-L33, L215-L235】

- **关键边界**:不是单一可编译应用。根目录无 `package.json`/`go.mod` 等应用清单——它是**多语言/多形态的混合内容仓库**(规则=Markdown、MCP=TypeScript、VL=Python、eval=bash+python、skill=Markdown)。【已核实: 项目根 `ls` + gitignore】

## 【2】技术栈

| 维度 | 内容 | 标签 |
|------|------|------|
| 语言 1 | 规则/Skill 文档:Markdown(主体) | 【已核实: 4 个 SKILL.md + ruleblade/CLAUDE.md】 |
| 语言 2 | web-search-mcp:TypeScript / Node.js(ESM, `type: module`) | 【已核实: mcp/web-search-mcp/package.json】 |
| 语言 3 | vl-vision:Python 3(脚本式 CLI) | 【已核实: skills/vl-vision/vl_vision.py】 |
| 语言 4 | eval 测评:POSIX bash + Python(json 解析/控制变量裁决) | 【已核实: eval/run-l1.sh, eval/scripts/*.py】 |
| 数据库 | 无应用数据库;有 DB 适配**规则文件**(impact-pro 的 db-adapters:mysql/postgresql/generic-sql),是给目标项目用的 | 【已核实: skills/impact-pro/db-adapters/】 |
| 关键依赖 | @modelcontextprotocol/sdk ^1.15.0、playwright-core(浏览器搜索)、axios(MCP);requests(vl-vision) | 【已核实: package.json deps + vl-vision 调用方式】 |
| 协议/标准 | MCP(Model Context Protocol)server、Claude Code Skill 格式(frontmatter: name/description/allowed-tools) | 【已核实: SKILL.md frontmatter + README MCP 配置示例】 |

## 【3】架构分层 / 模块地图  ← 喂 impact L1

仓库分四大块 + 两块支撑。`git ls-files` 一级分布:skills(171) / docs(67) / eval(64) / mcp(37) / 其余。

```mermaid
flowchart TD
    subgraph tools["工具箱四大件(各自独立,可单独使用)"]
        RB["律刃 RuleBlade<br/>claudecode行为规范/ruleblade/<br/>8条通用行为规则(CLAUDE.md)"]
        SK["Skills skills/<br/>pathfinder + impact + impact-pro + vl-vision"]
        MCP["网搜 MCP<br/>mcp/web-search-mcp/<br/>TS/Node MCP server"]
        VL["VL 识图<br/>skills/vl-vision/<br/>Python 视觉模型 CLI"]
    end
    subgraph qa["质量支撑(横切三 skill)"]
        EVAL["eval/<br/>L0/L1/L2 三层测评<br/>case + scorecard 时间序列 + 基线 diff"]
        DOCS["docs/<br/>设计复盘 + 复验手册 + 研究记录"]
    end
    RB -.约束.-> SK
    SK -->|产出 change-impact/_project-map.md| HANDOFF["拉取式交接<br/>(零硬依赖)"]
    HANDOFF -.impact 主动读.-> SK
    SK -.改完跑.-> EVAL
    EVAL -->|红线阻断<br/>PASS→FAIL/掉档≥3/新增P0| SK
    classDef def fill:#eef,stroke:#448
    class RB,SK,MCP,VL,EVAL,DOCS def
```

> 图中实线 = 【已核实】的产物流转/依赖;虚线(`-.推断/约束.->`)= 软耦合(规则约束是"可搭配"非硬依赖)。

| 模块 / 目录 | 推断职责 | 相关性 | 标签 |
|---|---|---|---|
| `claudecode行为规范/ruleblade/` | 通用 AI 行为规则(先思考/上下文先行/简单优先/精准修改…),8 条 + 中文表达要求;可复制进任意项目的 CLAUDE.md | 高(所有 skill 的行为底座) | 【已核实: CLAUDE.md L1-L60】 |
| `skills/pathfinder/` | 陌生项目只读认知地图,产 `_project-map.md` | 高(本 Skill 自身) | 【已核实: SKILL.md + references/7 文件 + templates/】 |
| `skills/impact/` | Java/Spring/MyBatis/RuoYi 类现有系统变更影响分析 + 受监督执行 | 高 | 【已核实: SKILL.md 铁律 7 条 + 7 Phase 流程】 |
| `skills/impact-pro/` | impact 的多栈版(内核栈无关 + profiles/ 按栈加载) | 高 | 【已核实: profiles/ 10 文件 + db-adapters/ 3 文件】 |
| `skills/vl-vision/` | 调视觉模型 API 给纯文本 LLM 补"看图"能力 | 中(独立工具) | 【已核实: SKILL.md + providers/siliconflow.py】 |
| `mcp/web-search-mcp/` | 联网搜索 MCP server(Google/Bing/Brave/DuckDuckGo),可提正文 | 中(独立工具) | 【已核实: README + package.json name=web-search-mcp-server v0.3.1】 |
| `eval/` | 统一测评体系:case 定义 + 评分卡时间序列 + 基线指针 + 控制变量裁决脚本 | 高(防漂移) | 【已核实: run-l1.sh + baselines/ + cases/ + scripts/】 |
| `docs/` | 设计复盘 + 复验手册 + not-ace 研究 + 归档 | 中 | 【已核实: skill-eval/README.md + 文件清单】 |
| `.claude/hooks/` | 可选 PreToolUse 写门禁 hook(`确认 Step N` 补强) | 低(可选,需放 `.impact-protected` 启用) | 【已核实: hooks/README.md + settings.example.json】 |
| `mcps/` | playwright/sequential-thinking 的工具 schema 镜像(gitignored,不入库) | 低 | 【已核实: gitignore L4 `mcps/`】 |
| `test-projects/` | 测评夹具(go-admin/ruoyi-vue/full-stack-fastapi-template 克隆 + degradation-trap) | 低(gitignored) | 【已核实: gitignore + 目录】 |
| `sessions/`、`.eval-tmp/` | 本地会话日志 / 控制变量实验临时产物 | 低(gitignored,不入库) | 【已核实: gitignore】 |

## 【4】核心功能

1. **律刃(RuleBlade)** — 8 条通用编码行为规则,让 AI 少猜、少乱改、先取证、说人话。【已核实: ruleblade/CLAUDE.md + README L45-L53】
2. **Pathfinder(领航)** — 对陌生项目做只读全景观测,产认知地图(技术栈/架构/数据模型/雷区/主链路),带信任标签 + git HEAD 防过期。【已核实: pathfinder/SKILL.md】
3. **ImpactRadar(impact)** — Java/RuoYi 类现有系统的苏格拉底式变更澄清 → 证据化影响分析 → light/full 两档文档 → 受监督执行(逐 Step 确认)。【已核实: impact/SKILL.md 流程总览】
4. **ImpactRadar Pro(impact-pro)** — impact 的多栈版,内核栈无关,profiles/ 按栈加载(已含 10 栈:dotnet/go-gin/node-express/python-fastapi/3 个前端/java-spring/generic)。【已核实: impact-pro/profiles/ 目录】
5. **VL 识图** — 调硅基流动等视觉模型 API,10 个预置模板(describe/ocr/scene…),给纯文本 LLM 补视觉。【已核实: vl-vision/SKILL.md + providers/】
6. **网搜 MCP** — 多搜索引擎聚合 + 正文提取 MCP server。【已核实: mcp/web-search-mcp/README.md】
7. **统一测评体系** — L0 静态自洽 / L1 行为契约(便宜模型 subagent 跑 case) / L2 人审;防漂移靠"基线评分卡时间序列 + 红线 diff"。【已核实: docs/skill-eval/README.md 三层表】

## 【5】关键入口

| 入口 | 类型 | 作用 | 标签 |
|---|---|---|---|
| `README.md` | 文档 | 唯一对外门面:3 分钟 quickstart + 各工具定位 + 安装路径 + 边界纪律 | 【已核实: 已读全文】 |
| `skills/*/SKILL.md` | Skill 触发器 | 各 skill 的主文件(frontmatter `name`+`description`+`allowed-tools`,被客户端按触发词加载) | 【已核实: 4 个 SKILL.md frontmatter】 |
| `mcp/web-search-mcp/dist/index.js` | 进程入口 | MCP server 启动点(`node ./dist/index.js`,启动后等 MCP 消息) | 【已核实: package.json `main` + README 启动说明】 |
| `skills/vl-vision/vl_vision.py` | CLI 入口 | `python vl_vision.py <图> [--template] [--prompt] [--json]` | 【已核实: SKILL.md 调用方式】 |
| `eval/run-l1.sh <skill>` | 测评入口 | L1 行为契约测试编排:跑 case → 收 scorecard → diff 基线 | 【已核实: run-l1.sh 头部】 |
| `skills/<skill>/tests/run.sh` | L0 入口 | 静态自洽校验(铁律存在/引用完整/fixture 锁定) | 【已核实: pathfinder/tests/run.sh】 |
| `.claude/hooks/impact-write-gate.*` | 可选门禁 | PreToolUse hook,把 `确认 Step N` 补强到工具执行前 | 【已核实: hooks/README.md】 |

## 【6】数据模型概览

本项目**无应用数据库**——它是规则/工具仓库,不持久化业务数据。

但有两条"数据形态"值得记:

1. **测评数据流(结构化)** — 这是仓库里唯一的"数据模型",是文件而非 DB:
   - `eval/cases/<skill>/<id>.json` → case 定义(id/title/stack/tier/prompt/expected/trap_for/files_to_inspect)【已核实: eval/cases/pathfinder/P1.json】
   - `eval/runs/<date>-<skill>@<commit>/<id>.scorecard.json` → 评分卡(dims 9 维 + base_total + behavior + p_level + contracts 5 项 PASS/FAIL + runner_model)【已核实: P1.scorecard.json 样本】
   - `eval/baselines/<skill>.json` → 基线指针(skill_commit + average_score + p0_count + contracts_all_pass + frozen_at)【已核实: baselines/pathfinder.json】
   - 关系:`case → scorecard(每次 run 产一张)→ baseline(指向某次 run 做红线 diff 基准)`

```mermaid
erDiagram
    CASE ||--o{ SCORECARD : "每次 run 产一张评分卡"
    BASELINE ||--|| SCORECARD : "指向基准 run 的聚合"
    CASE {
      string id PK
      string skill
      string stack
      string tier "full/light/degradation"
      string prompt
      json expected
    }
    SCORECARD {
      string case_id FK
      string skill_commit
      string run_date
      string runner_model "跨run归因关键"
      json dims "9维分"
      string p_level "none/P0/P1"
      json contracts "5项PASS/FAIL"
    }
    BASELINE {
      string skill PK
      string skill_commit
      float average_base_score
      int p0_count
      bool contracts_all_pass
    }
```

2. **Pathfinder 产出物** — `change-impact/_project-map.md`(本项目首次产出即本文件);impact 产出 `change-impact/{需求名}/` 下多份编号文档(000-context-pack…090-execution-record)+ `_active-state.md` 跨会话恢复检查点。【已核实: templates/000-context-pack.md + 090-execution-record.md + _active-state.md 均存在】

## 【7】外部依赖与集成

| 外部系统 | 用途 | 凭证/配置键(仅记键名) | 标签 |
|---|---|---|---|
| 硅基流动(SiliconFlow)平台 | vl-vision 调视觉模型;另:DeepSeek V4 Pro/Flash 经此接入(README 注明不代表官方能力) | `SILICONFLOW_API_KEY`(env,来源 skills/vl-vision/config.py L7) | 【已核实: config.py + README L142】 |
| 搜索引擎(Google/Bing/Brave/DuckDuckGo) | web-search-mcp 聚合搜索 | 各引擎 API key(env,详见 mcp/web-search-mcp/README.md,未读) | 【推断: 未读该 README 配置段】 |
| Playwright / Chromium | web-search-mcp 浏览器正文提取 | 需 `npx playwright install chromium`(README L172) | 【已核实: package.json playwright-core 依赖】 |
| AI 客户端(Claude Code / Codex / Cursor 等) | skill 安装载体;通过 `Copy-Item` 到 `.claude/skills` 或 `.codex/skills` | 无凭证,文件复制 | 【已核实: README L15-L33, L215-L235】 |
| MCP 客户端配置 | 注册 web-search-mcp,`args` 需本机绝对路径 | 无凭证,JSON 配置 | 【已核实: README L186-L195 配置示例】 |
| DB MCP(dbhub / database)(可选) | impact/impact-pro 的 schema 发现场景(本仓库不内置,目标项目才用) | 由目标项目提供,本仓库无 | 【已核实: SKILL.md allowed-tools 列出但标注"运行时探测为准"】 |

## 【8】构建·运行·测试

| 动作 | 命令 | 标签 |
|---|---|---|
| L0 静态校验(每次改动必跑,免费) | `bash skills/<skill>/tests/run.sh` | 【已核实: docs/skill-eval/README.md L9 + pathfinder/tests/run.sh】 |
| L1 行为契约(便宜模型跑 case) | `bash eval/run-l1.sh <skill> [评委模型]` | 【已核实: eval/run-l1.sh 头部】 |
| 基线 diff(防漂移红线) | `bash eval/diff-baseline.sh` 或 `python eval/scripts/diff_baseline.py` | 【已核实: eval/diff-baseline.sh + scripts/diff_baseline.py 存在】 |
| 控制变量裁决(同模型重跑归因) | `python eval/scripts/analyze_control.py` | 【已核实: scripts/analyze_control.py 存在】 |
| web-search-mcp 构建 | `npm run build`(tsc → dist/)| 【已核实: package.json scripts.build】 |
| web-search-mcp 启动 | `node ./dist/index.js`(看到 "Web Search MCP Server started") | 【已核实: README L177-L182】 |
| web-search-mcp 依赖安装 | `npm install` + `npx playwright install chromium` | 【已核实: README L170-L173】 |
| vl-vision 运行 | `python skills/vl-vision/vl_vision.py <图> [--template]`(需先 `pip install requests`) | 【已核实: README L199-L213】 |
| 安装 skill | `Copy-Item skills/<skill> ~/.claude/skills/<skill> -Recurse -Force` | 【已核实: README L230-L232】 |

> **无 CI 配置文件**:仓库内未见 `.github/workflows` 或同类——L0/L1 靠本地手动跑。【已核实: Glob 无 CI 文件 → 推断 CI 缺失】`【推断: 待验证,可能在 .gitignore 外的远程配置】`

## 【9】雷区 / 风险区

> 只如实记录,不开药方。

1. **根目录散落大体积会话日志** — `2026-06-14-222723-*.txt`(139KB)、`mcp/web-search-mcp/崩溃日志.txt`(132KB)在根/MCP 目录,**未被 .gitignore 排除**(根目录那个在 git status 里是 `??` 未跟踪状态)。会话日志可能含敏感对话/凭证,入库风险。【已核实: git status `??` + ls -la 文件大小】
2. **明文 `.env` 散布** — `.env` 在 gitignore 里(`.env`),但 `test-projects/`、`skills/pathfinder/tests/fixtures/degradation-trap/` 下存在 `.env` 文件。其中 degradation-trap 的 `.env` 是**故意放凭证的测评夹具**(测脱敏),真实项目 .env 不得入库。【已核实: gitignore + find .env 结果】
3. **嵌套 git 仓库** — `skills/impact/tests/e2e/workdirs/*`、`skills/impact-pro/tests/e2e/workdirs/*`、`test-projects/{go-admin,ruoyi-vue,full-stack-fastapi-template}/` 各有 `.git`。子模块/克隆仓库,易在父仓 `git add` 时误纳或状态混乱。【已核实: find .git -type d 结果,共 6 个嵌套 .git】
4. **`.eval-tmp/` 下有 `.impact-protected`** — 写门禁标志出现在临时实验目录(`.eval-tmp/cc-hook-protected/`),不在项目根。说明 hook 在临时场景测过,但项目根本身**未启用写门禁**(根无 `.impact-protected`)。【已核实: find .impact-protected 结果】
5. **多语言/多形态混合,无统一构建** — 没有一个命令能"构建整个仓库"。TS 要 npm、Python 要 pip、skill 是复制、eval 是 bash。接手者需意识到这是**多个独立工具的集合**,不是单体。【已核实: 各模块构建方式各异】
6. **MCP 能力假设警示** — impact/impact-pro 的 `allowed-tools` 列了 `mcp__database__query` 等,但 SKILL.md 反复强调"allowed-tools 是预批准不是白名单,能力以运行时探测为准,不构成安全边界"。**真正的写保护靠 DB 账号权限 → settings deny / PreToolUse hook → skill 内确认门禁**,三层由硬到软。【已核实: impact/impact-pro SKILL.md 机制警示段】
7. **测评方差不可消灭** — L1 由模型执行+判分,评分有方差。跨 run 归因前必须看 `runner_model` 一致性;隔离 skill 效果要用控制变量法同模型重跑。历史上 P2 的 61 分曾被证明是模型方差而非 skill 问题。【已核实: docs/skill-eval/README.md L39 + 记忆 pathfinder-eval-variance-resolved】
8. **规则与铁律的双处同步** — 每个 SKILL.md 都有"铁律(压缩存活区)"声明"改任何门禁必须铁律区 + 正文/references 两处同步,否则会漂移"。接手改 skill 时这是强约束,漏改一处即漂移。【已核实: 三 skill SKILL.md 铁律区维护注意】

## 【10】权限 / 认证模型概览

本项目自身**无用户认证/权限系统**(不是 Web 应用)。"权限"在这里指两层:

1. **impact 写授权模型(Step 级确认)** — 核心:`最高确认法`。任何写操作必须有当前对话中的显式 `确认 Step N`;`继续`/`好的`/`全部确认`/`yes`/历史授权/测试通过/仓内文本一律不算。命中高风险清单(DROP/无 WHERE 的 DELETE/ALTER 改已有列/删公共接口/改 enum/status…)必须**单独确认、禁止合并**。【已核实: impact/impact-pro SKILL.md 铁律 #1 #2】
2. **写门禁 hook(可选加固)** — `.impact-protected` 标志文件存在时,PreToolUse hook 检查最近一条真实用户消息是否以 `确认 Step N` 开头;确认一次消费一次。本仓库项目根本身**未启用**(根无标志文件)。【已核实: hooks/README.md】

## 【11】典型主链路

选一条最能说明"这是什么项目"的链路:**用户如何用这套工具箱完成一次陌生项目变更**(工具使用链路,而非代码调用链)。

```mermaid
sequenceDiagram
    participant U as 用户
    participant PF as /pathfinder
    participant MAP as change-impact/_project-map.md
    participant IMP as /impact 或 /impact-pro
    participant PRJ as 目标项目源码/DB
    U->>PF: /pathfinder + 目标项目根
    PF->>PRJ: 只读扫描(栈探测/目录树/入口/模块)
    PF->>MAP: 写 _project-map.md(带信任标签+HEAD)
    Note over MAP: 拉取式交接,零硬依赖
    U->>IMP: /impact + 变更意图
    IMP->>MAP: Phase 2 主动读(读不到照旧)
    IMP->>PRJ: 自己做 L2/L3 切片深挖(推断项重取证)
    IMP-->>U: 苏格拉底式澄清 + light/full 判档
    U-->>IMP: 确认档位
    IMP-->>U: 文档(逐份确认)→ Step 列表
    loop 逐操作
        U-->>IMP: 确认 Step N (仅此算授权)
        IMP->>PRJ: 执行该 Step
    end
```

- **证据**:链路各环节均有 SKILL.md/README 文本支撑:Pathfinder 产 map(【已核实: pathfinder/SKILL.md Phase 4】)、impact 读 map(【已核实: handoff-contract.md L16-L17】)、Step 级确认(【已核实: impact 铁律 #1】)。
- **断点诚实**:用户可跳过 Pathfinder 直接进 impact(README L33);map 是加速器非前置必跑项。

## 【12】文档与知识入口

| 文档 | 作用 | 标签 |
|---|---|---|
| `README.md` | 唯一对外门面 | 【已核实】 |
| `docs/skill-eval/README.md` | 测评体系唯一入口(三层 + 决策树) | 【已核实】 |
| `docs/skill-eval/REVALIDATION.md` | 复验体系单一权威入口(含 §6 生产就绪判定) | 【已核实: commit 769868d】 |
| `docs/archive/2026-06/impact-context-pack-design.md` | context-pack 设计复盘 | 【已核实: 文件存在】 |
| `docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md` | Pathfinder 设计复盘 | 【已核实: 文件存在,未读内容】 |
| 各 skill 的 `README.md` + `VALIDATION.md` | skill 自述 + 验证记录 | 【已核实: 三 skill 均有 validation-runs/INDEX.md】 |
| `mcp/web-search-mcp/web-search-mcp修复记录.md` | MCP 修复历史(18KB) | 【已核实: 文件存在,未读】 |

## 【13】没挖深的部分(盲区 + 续挖锚点)

> 盲区诚实清单。下面这些本次没深入,需要时可「再挖 X」续扫。

- **web-search-mcp 源码(src/)** — 只看了 dist 编译产物清单 + package.json,没读 `src/*.ts` 实现细节(content-extractor / rate-limiter / browser-pool / search-engine 的内部逻辑)。`【推断: dist 文件名映射出模块职责,但实现未核】`
- **根目录会话日志 / 崩溃日志** — `2026-06-14-*.txt`(139KB)、`mcp/web-search-mcp/崩溃日志.txt`(132KB)未读。可能含敏感对话内容,且有入库风险(见【9】雷区 1)。
- **docs/archive/ 大量历史文档** — 只列了文件名,没读内容(如 agent-iteration-conclusions.md、skill-gap-* 系列、not-ace-exploration/ 全部)。这些是"怎么迭代到今天"的决策史。
- **mcps/ 工具 schema 镜像** — playwright 22 个 + sequential-thinking 1 个工具的 JSON 定义,只确认存在未逐个读(gitignored,本地镜像)。
- **ruleblade 完整 8 条规则** — 只读了 CLAUDE.md 前 60 行(规则 1-4),规则 5-8 + 中文表达要求 + RUN_TASK_A 稳定性测试脚本未读。
- **impact/impact-pro 的 references/ 正文** — 只确认了文件清单(phase-2/phase-3/phase-5/schema-discovery/dimensions/style-analysis),没读各 phase 的完整执行规则。
- **eval 各 case 的 expected/trap_for 细节** — 只精读了 P1,其他 case(P2/P3D/impact R1-R3N/impact-pro F1-G2)未逐个读。
- **CI / 自动化部署** — 未见 CI 配置文件,是否在远程(GitHub Actions 等)有未读。

续挖示例指令:`再挖 web-search-mcp 源码` / `再挖 ruleblade 完整规则` / `把 eval 三个 skill 的 case 全读一遍`。
