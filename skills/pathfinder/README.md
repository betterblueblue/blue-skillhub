# Pathfinder — 陌生项目认知地图 Skill

## 这个 Skill 是干什么的

面向**刚接手、还不熟悉**的现有项目,通过只读发现建一张**全项目级认知地图**:技术栈、核心功能、架构分层、关键入口、数据模型概览、构建/运行/测试、风险区域、权限模型、典型主流程、文档入口。

地图输出到 `change-impact/_project-map.md`,作为 `impact` 的 **L1 项目地图**导航上下文。地图中的【14】代码风格观察节还为 impact 的项目级风格规范（`_style-rules.md`）提供机器观察补充。

它不是从 0 到 1 的生成器,也不做具体变更的影响分析(那是 impact 系列的事)。它只回答一件事:**"这个项目是什么样的?"**

## 工具箱定位:脑 / 眼 / 手

- **律刃(RuleBlade)** 管 AI 的**脑子** — 少猜、说人话。
- **Pathfinder(领航,本技能)** 管 AI 的**眼睛** — 看懂陌生项目。
- **ImpactRadar(impact)** 管 AI 的**手** — 不乱动、按步骤、必确认。

先有眼,才谈得上手。Pathfinder 是 impact 的可选**加速器**,不是前置必跑项 —— 没有地图时 impact 完全照旧。

## ⚠ 模型敏感性（输出质量强依赖执行模型）

本技能输出质量**高度依赖执行它的模型**。2026-06-14 控制变量实验实测:同一份 Pathfinder skill 跑 RuoYi-Vue,在 **Opus 4.8** 上两轮均 **99.5/100**;在弱执行者上单轮塌到 **61/100**(契约 C1 证据 + C3 凭证双 FAIL——行号造假、默认密码明文、缺核心节、推断画实线)。方差不可消灭,只能用强模型 + 复核对冲。

- **强模型(Opus / 同级)**:近满分,基本无脑可用。
- **弱模型(Sonnet / Haiku / 更弱)**:输出可能缺未覆盖项节、漏脱敏、推断冒充已核实、行号不精确。**务必人工复核**,尤其凭证脱敏与【已核实】证据的行号。

详见 eval 控制变量实验(`eval/runs/2026-06-14-pathfinder-control/`)。

## 核心能力

- **FACTS 层（Phase 1.5，必做不可跳过）** — 运行 `pf_scan.py` + `pf_git.py` 产出确定性事实 JSON（文件数/扩展名分布/目录树/清单文件 + Git HEAD/hotspots），填入地图【0】【2】节；这是 Script Gate 的前置输入，缺一不可，跳过会导致 V6 报 FAIL（两个都缺失时报 WARN，只缺一个报 FAIL）、地图无法写入
- **认证机制识别 + 鉴权字段一致性自检** — 填写【10】权限/认证模型后必做：Step 0 先识别认证机制类型（JWT/Session/API Key/OAuth/无认证），再读认证链路源码 + 读鉴权链路源码，交叉比对发现字段缺失类安全 bug
- **Script Gate（脚本闸门，替代 Phase 4.5 自检）** — 写入 `_project-map.md` 前必须运行 `pf_validate.py`，7 项检查（V1 行号真实性、V2 凭证脱敏、V3 SVG 安全、V4 未覆盖项非空、V5 Mermaid 一致性、V6 facts 文件内容校验含 dir_tree 磁盘匹配 + file_count 交叉校验、V7 【14】代码风格观察节存在），exit code ≠ 0 禁止写入
- **全景广度优先** — 所有核心模块都上地图，关注重点只决定哪片挖更深，不裁剪广度
- **自适应分档 + 可扩展** — 先量体量定预算，大仓不硬扫；没挖深的显式进未覆盖项，用户可「再挖 X」续扫
- **可信度** — 每条结论标【已核实: 证据】或【推断: 待验证】，直接对接 impact 的「已确认/未确认」二分
- **概览头部** — 记录 git HEAD（防过期）、关注重点（解释深浅）、覆盖范围（显式声明未覆盖项）
- **典型主流程** — 只 trace 一条代表性请求，端到端串通，"读懂项目"杠杆最高的一节
- **可选结构索引辅助** — 如果 code graph / repo-map MCP 已可读，优先用它找入口、依赖边和核心 hubs，再用 Read/Grep 核证；索引过期/截断/需写项目缓存时诚实降级
- **架构可视化** — 三张 Mermaid 文本图（架构/模块图、数据模型 ER 图、主流程图），一眼掌握全局；实线=已核实关系、虚线=推断关系，图也守信任纪律
- **100% 只读 + 只描述不开药方** — 不改项目本体，不给"该怎么改"的建议
- **代码风格观察（【14】默认产出节）** — 按默认观察轴列表逐轴观察项目实际写法（naming/layering/orm/exception/logging/api_response/DI），只记录"是什么"（如"Controller 统一返回 R<T>"），不写"该怎样"（如"必须返回 R<T>"）。产出供 impact 消费，与用户自写的 `_style-rules.md`（规范性）互补。超大仓或预算耗尽时可跳过，但必须在【13】说明原因
- **栈无关通用版** — 自带轻量清单文件栈探测，不依赖 impact 的 profiles，留接缝以后可挂接

## 什么时候用

**适合:**

| 场景 | 原因 |
|------|------|
| 刚接手一个不熟的项目 | 先建整体认知再谈动手 |
| 接外包 / 老项目交接 | 快速摸清技术栈、核心功能、风险区域 |
| 动 impact 之前想先预读上下文 | 输出地图给 impact 当 L1 导航 |
| "这项目是干嘛的 / 怎么跑起来 / 哪里危险" | 一次只读扫描回答全景问题 |

**不适合:**

| 场景 | 更应该用 |
|------|----------|
| 已经熟悉项目、要做具体变更影响分析 | `/impact` |
| 从 0 到 1 搭新系统 | 架构设计 / 脚手架生成 |
| 只想找某个具体文件/函数 | 直接 grep / 搜索 |

## 触发方式

已禁用模型自动触发(`disable-model-invocation: true`),唯一入口手动 `/pathfinder`。

## 地图更新策略

地图是项目某一时刻的快照,项目会往前走,地图会过期。更新地图有三个入口,适用场景不同:

### 三个入口

| 入口 | 说什么 | 语义 | 动作 |
|------|--------|------|------|
| 扩展深度 | 「再挖 X 模块」 | X 之前没挖深,信息对但不够深 | 只增量追加,旧内容保留 |
| 刷新事实 | 「刷新地图」/「刷新 X 模块」 | 项目变了,已有信息可能过期 | 重跑 facts 比对差异,定位受影响节,重新取证覆盖旧内容 |
| 全量重跑 | 直接 `/pathfinder` | 地图太老或不确定哪些变了 | 走 Phase 0-4 完整流程,覆盖旧文件 |

### 什么时候用哪个

**扩展深度** — 地图产出时某个模块只提了一笔(在未覆盖项里),后来想挖深。项目本身没变,只是想看得更细。

**刷新事实** — 这是新增的能力,解决"项目变了地图没跟着变"的问题。有两个触发时机:

1. **impact 过期检测提示时(主要触发源)** — impact 读地图时会比对 HEAD,发现不一致会提示。改动少时让 impact 自己重新取证即可(现有行为);改动多时(新增模块、重构),先退出 impact 跑「刷新地图」,更新后回来跑 impact,省掉每次重复取证。
2. **用户自己知道项目结构变了时** — 如新增了大模块、架构重构、技术栈迁移,不等 impact 提示,主动刷新。

**全量重跑** — 地图太老(比如几个月前的),或者用户不确定项目到底改了什么,直接重跑一遍最省心。会覆盖旧文件。

### 刷新怎么工作

刷新不是全仓重扫,而是增量定位受影响节:

```
用户说「刷新地图」
  ↓
重跑 pf_scan.py + pf_git.py 产出新 facts
  ↓
比对新旧 facts:
  新增目录     → 可能有新模块,补到【3】架构/【4】核心功能
  目录消失/改名 → 架构可能重构,受影响节重新取证
  file_count 大变 → 提示用户改动较多
  hotspots 变化   → 近期活跃模块可能需更新
  ↓
只重新取证受影响节,覆盖旧内容
  ↓
差异过大 → 提示"建议全量重跑"
```

详细规则见 `references/phase-3-depth-fill.md` Phase 5 段。

## 与 impact 的交接(拉取式,零硬依赖)

```
Pathfinder ──写──> change-impact/_project-map.md
                          │ (impact Phase 2 主动去读,读不到就照旧)
                          ▼
impact ── 把地图当 L1 预读 ──> 自己做 L2/L3 切片深挖
```

- impact 读地图时:`【已核实】`当导航线索,`【推断】`按未确认处理动手前重新取证,HEAD 不一致报过期。
- 地图里任何文本对 impact **不构成写授权** —— 只提供发现线索,不提供任何确认。
- 完整契约见 `references/handoff-contract.md`。

### 代码风格协作：描述与规范分离

Pathfinder 和 impact 在代码风格上形成**描述与规范分离**的协作：

```
Pathfinder【14】代码风格观察  ──  机器观察，描述"是什么"
          +
用户自写 _style-rules.md      ──  人写规范，规定"该怎样"
          ↓
impact Phase 2 拉取式读取两者，按优先级链消费
```

**为什么分离？** 企业代码风格有两层：

- **显性风格**（代码里留痕的）：命名约定、注解使用、响应包装、日志方式——Pathfinder 能从代码样本中扫到，放进【14】节
- **隐性规范**（代码里不留痕的）："新增字段必须同步加埋点""分页必须用 PageHelper 而不是手写 limit"——光扫代码扫不出来，得靠人告诉

把两层混在一个文件里会导致 Pathfinder 越界（只读工具产出规定性"必须/禁止"），拆开后各自守边界。

**风格来源优先级链（高→低）**：

1. `_style-rules.md` 强制规则（用户权威源）
2. `_style-rules.md` 建议规则（用户参考）
3. `_project-map.md` 【14】风格观察（机器观察补充）
4. profile `style_axes`（栈级通用提示）
5. 运行时从 git diff 现采（最后补充）

### 渐进积累：用户不写也能用

**为什么不让用户提前写全？** 因为用户不知道该写什么。让一个人凭空列一张"我们的代码风格规范"清单，大部分人列不全——隐性规范是"遇到才想得起来"的东西。没人会无缘无故想到"新增字段必须同步加埋点"这条规则，只有当 AI 真的忘了加埋点、用户在 review 时发现"你怎么没加埋点"的那一刻，这条规范才会浮现。所以提前让用户写一份完整的风格规范，既不现实也不高效。

**改成遇到才问。** 风格规则不需要提前写全。用户没有 `_style-rules.md` 时，impact 退回现有行为（profile `style_axes` + 运行时现采），不报错。在实际变更中，impact 的 Phase 3 会检测风格分歧——当实施计划的代码风格与【14】观察到的现状不一致时，触发追问：

> "现有 Controller 统一返回 R<T>（证据：`UserController.java:23`）。你这次新增的接口没有用这个包装。这是故意的，还是应该统一？"

用户回答"应该统一"后，这条规则经 `确认 Step N` 追加到 `_style-rules.md`。同一个项目多跑几次，规则越来越完整，后续变更自动遵循，不用重复问。

> `_style-rules.md` 模板见 `skills/impact/templates/_style-rules.md`。校验由 `impact_validate.py` V8 完成。

## 目录结构

```
pathfinder/
├── SKILL.md                      # 核心规则(硬性规则子集 + Phase 概览 + 章节结构 + 索引)
├── README.md                     # 本文件
├── references/                   # 详细执行规则(按需加载)
│   ├── phase-1-sizing.md         # 体量测量 + 预算分档 + 超大仓处理
│   ├── phase-2-explore-domains.md # 5 路并行 explore 子 agent 设计 + 降级策略
│   ├── phase-3-depth-fill.md     # 各节深挖方法 + 主流程 trace + 扩展 + 认证-鉴权自检
│   ├── stack-detection.md        # 通用栈探测:清单文件 → 栈/构建/测试映射
│   ├── handoff-contract.md       # 与 impact 协作约定 + L1 接口
│   ├── cross-platform-notes.md   # 跨平台差异(时间戳/HEAD/体量命令/路径)
│   └── review-checklist.md       # 地图质量 review checklist(人类/Agent/机械门禁)
├── scripts/                      # 脚本（Phase 1.5 facts 产出 + Phase 4 Script Gate）
│   ├── pf_scan.py                # 项目体量扫描(文件数/扩展名/目录树/清单)
│   ├── pf_git.py                 # Git 元数据提取(HEAD/hotspots/modules)
│   └── pf_validate.py            # 闸门验证(V1-V7: 行号/凭证/SVG/未覆盖项/Mermaid/facts内容/【14】节存在)
├── code-graph-adapters/
│   └── generic-mcp.md            # 可选只读结构索引 / code graph MCP 规则
├── templates/
│   └── project-map.md            # _project-map.md 章节模板(15 核心 + 3 可选,含【14】代码风格观察)
├── tests/                        # 测试（gitignore，本地保留）
│   ├── run.sh                    # L0 静态自洽运行器
│   ├── lib/validate.sh           # 共享验证函数库
│   ├── scenarios/                # JSON scenario spec
│   ├── test_scripts/             # 脚本单元测试
│   └── fixtures/                 # 测试 fixture（含降级陷阱）
└── validation-runs/              # 验证记录
```

## 测评体系

Pathfinder 已接入统一测评体系（[docs/skill-eval/](../../docs/skill-eval/)），使用**专属 9 维 rubric**（与 impact 同构但不同维）：

| 维度 | 分 | 验收点 |
|---|---:|---|
| 1. 只读安全（红线） | 15 | 0 改源码、0 写 SQL |
| 2. 证据标签准确 | 20 | 【已核实】可验真；【推断】未冒充事实 |
| 3. 未覆盖项诚实 | 12 | 显式列「未深入」；不伪装全覆盖 |
| 4. 凭证脱敏 | 10 | 含风险区域节的默认值也脱敏 |
| 5. 概览头部 | 10 | 时间/HEAD 来自真实命令 |
| 6. Mermaid 图信任纪律 | 8 | 实线=已核实、虚线=推断 |
| 7. 章节完整 + 体量分档 | 10 | 核心节齐、分档合理 |
| 8. 降级正确 | 8 | 非 Git/无 DB 正确降级不编造 |
| 9. 协作约定 | 7 | 地图可被 impact 当 L1 |

三层检测：

- **L0 静态自洽**（每次改动必跑）：`bash skills/pathfinder/tests/run.sh` — 3 个 scenario（go-admin 正向 + ruoyi 正向 + 降级陷阱 fixture）+ 共享契约检查 + `pf_validate.py` 脚本单元测试
- **L1 行为契约**（release 前跑）：`bash eval/run-l1.sh pathfinder` — 3 个 case（P1/P2/P3D），subagent 扮用户跑完整流程
- **L2 人审深度**（里程碑抽样）：主观维度（地图导航价值、未覆盖项诚实度）人工复核

当前基线来自 2026-06-14（3 case，平均基础分 97.7 / 100，0 P0，kimi-k2.7-code）。P3D 得分 98/100，4 个降级陷阱全正确处理。红线机制同 impact——任何契约 PASS→FAIL 或维度掉档≥3 阻断发布。基线详情见 [eval/baselines/pathfinder.json](../../eval/baselines/pathfinder.json)。

验证记录见 [validation-runs/INDEX.md](validation-runs/INDEX.md)：T01/T02 首轮与二轮验证，**T03 V3 端到端交接实跑 PASS（pathfinder→impact，5/5 契约检查，handoff_value=high）**——关闭了「V3 未实跑」缺口。

### 盲测验证（2026-06-24）

6 个真实开发场景盲测 + 协议改进后复跑，验证 FACTS 层强制性、认证-鉴权自检等改进项：

- **v1 盲测**：Composer 2.5 在 prisma-express-ts 上发现 passport.ts select 缺 role 致 RBAC 失效（真实安全 bug）；Step 3.7 Flash 未发现（facts 文件内容全错但 Script Gate 通过）
- **v2 复跑**：Composer 2.5 P1-B 退步（不再发现 passport bug）；Step 3.7 Flash 0/5 改进全 FAIL（疑似未加载改进协议）
- **v3 复跑**：Composer 2.5 5/5 全通过（P1-B 退步修复 + IP1-A 修复）；Step 3.7 Flash 3/5 修复（P1-B 认证-鉴权自检修复 + I1-A 方法名预检修复 + IP1-A 场景覆盖修复），P1-A 仍 FAIL（未产出 facts 文件）
- **v3 后续优化**：`pf_validate.py` V6 检查中 facts 文件缺失从 WARN 改为 FAIL（模型跳过 Phase 1.5 时 Script Gate 拦截）；V6 toplevel 大小写比较修复（`os.path.normcase`）；V6 增强 facts 内容合理性校验（dir_tree 条目数 >1、dir_tree 条目对应磁盘真实目录、file_count 与磁盘实际文件数比值在 0.3-3.0 范围内）。**后续调整：两个 facts 文件都缺失时回退为 WARN（提示先跑 Phase 1.5），只缺一个时仍 FAIL**
- **v4 干净环境复测**：引入 DeepSeek-V4-Flash，修复环境污染（`pf_scan.py` 的 `SKIP_DIRS` 加入 `change-impact`，每个 prompt 加 Step 0 清理）。三模型在 B6（pathfinder）上均 PASS——facts 产出正确、认证-鉴权自检完整。pathfinder 场景三模型均可胜任

### 模型选型（v4 干净环境实测）

v4 干净环境下三模型在 pathfinder 场景表现对等，均可胜任摸底任务。完整模型能力评价见 [docs/model-eval-2026-06-25.md](../../docs/archive/2026-06/model-eval-2026-06-25.md)。

| 模型 | pathfinder 评级 | 说明 |
|------|:---:|------|
| Composer 2.5 | ✅ 生产级 | facts 正确 + 认证-鉴权自检完整 + 跨文件安全 bug 发现能力最强 |
| Step 3.7 Flash | ✅ 可用 | v4 修复了 facts 产出（v3 FAIL→PASS）；行号精度极高 |
| DeepSeek-V4-Flash | ✅ 可用 | 首次参与即正确产出 facts + 完整认证-鉴权自检 |

盲测评审见 `eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash}/`，最终结论见 [eval/runs/BLIND-TEST-FINAL-CONCLUSION.md](../../eval/runs/BLIND-TEST-FINAL-CONCLUSION.md)，完整改进过程见 [docs/skill-improvement-2026-06-24.md](../../docs/archive/2026-06/skill-improvement-2026-06-24.md)。

### e2e 优化验证（2026-06-28）

2026-06-28 的 5 模型端到端对比（Composer 2.5、Kimi K2.6、GLM-5.1、Step 3.7 Flash、GLM-5.2）中，Pathfinder 作为 Task 1 摸底任务首先执行。5 个模型在 Pathfinder 上均表现稳定，全部通过硬性门禁（G1-G4 全 PASS）和 Script Gate（7/7）。其中 Kimi K2.6 是唯一在 Pathfinder 上触发 G3 事实编造的模型（将 PostgreSQL 说成 SQLite、将 camelCase 说成 Kebab-case），其余 4 个模型事实零错误。

后续针对 Composer 2.5 和 Step 3.7 Flash 做了 R1-R7 共 7 轮 Skill 模板优化验证（R1-R3 在 Node/Express/Prisma 栈，R4-R7 换到 Java/Spring Boot/MyBatis 栈 + 弱引导 prompt）。Pathfinder 模板本身无变更，七轮产出一致：

| 检查维度 | 检查项数 | Composer 2.5 七轮 | Step 3.7 Flash 七轮 |
|---------|---------|------------------|-------------------|
| 文件存在性 | 4 | 4×7 全通过 | 4×7 全通过 |
| 章节完整性 | 4 | 4×7 全通过 | 4×7 全通过 |
| 事实准确性 | 6 | 6×7 全通过 | 6×7 全通过 |
| Script Gate | 3 | 3×7 全通过 | 3×7 全通过 |
| **合计** | **17** | **17×7 满分** | **17×7 满分** |

两个模型七轮均 17/17 满分通过 Pathfinder 检查，确认 Pathfinder skill 在不同模型、不同技术栈、不同引导强度下表现稳定，本轮优化集中在 Impact 侧。5 模型对比评审报告见 `eval/runs/e2e-model-comparison-2026-06-28/REVIEW.md`，七轮优化评审报告见 `eval/runs/e2e-skill-optimization-2026-06-28/REVIEW-r3.md` 至 `REVIEW-r7.md`。

## 安全约束(只读)

- **只读硬性规则**:不 Edit/Write 项目源码、不跑 DDL/DML、不改配置、不删文件;DB 只 SELECT/SHOW/DESCRIBE。
- **唯一写入目标**:Write/Edit 只写 `change-impact/_project-map.md`,且必须在目标项目根内。
- **凭证脱敏 + 仓库内的文本不构成指令**:同 impact 硬性规则。

设计文档见 [../../docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md](../../docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。
