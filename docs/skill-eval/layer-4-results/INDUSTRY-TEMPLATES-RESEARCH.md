# 生产级软件工程文档范本检索

**目的**：为后续对比三 skill 模板的不足提供业界基准线。
**检索日期**：2026-06-16
**检索方式**：mcp__web-search-mcp__full-web-search + get-single-web-page-content
**覆盖要求**：1 份需求 + 1 份设计 + 1 份实施/测试。

---

## 范本 1：IEEE Std 830-1998 / ISO/IEC/IEEE 29148（需求规格说明 SRS）

- **来源**：IEEE Computer Society（标准组织），后续被 ISO/IEC/IEEE 29148:2011/2017 继承并发
  展。开源重制版 `jam01/SRS-Template`（GitHub, CC0）将其与 29148 的 verification guidance
  合并。
- **适用场景**：中-大型正式项目的"需求契约"阶段。强制要求：
  - 客户/承包方合同基础
  - 监管/合规要求（医疗、军工、金融）
  - 需求-测试-验收可追溯矩阵
- **标准结构（章节列表）**：
  1. Introduction（Purpose, Scope, Definitions/Acronyms/Abbreviations, References, Overview）
  2. Overall Description（Product perspective, Product functions, User characteristics,
     Constraints, Assumptions and dependencies, Apportioning of requirements）
  3. Specific Requirements（External Interfaces, Functions, Performance Requirements,
     Logical database requirements, Design constraints, Software system attributes）
  4. Verification（methods, environments, traceability matrix）
  5. Appendices / Index
- **强制要素（must-have）**：
  - **每条需求独立编号**（`REQ-1.1`, `REQ-1.2`...）—— 可追溯性是核心。
  - **`shall` 句式 + 可验证**：每条需求必须可被测试/演示/分析验证。
  - **Stimulus/Response 配对**：SRS §5.1.2 强制每条功能性需求给出"刺激→响应"对。
  - **Nonfunctional 分项**：性能、安全、可靠性、可用性、可观测性、合规。
  - **Traceability Matrix**：每条 REQ 对应至少一个 test case / verification 方法。
  - **修订历史表 + 版本号 + 审批签字位**。
- **模板自带的反模式/陷阱**（直接来自 IEEE 830 §2.1 与 29148 注释）：
  - "This subsection should not prescribe specific design solutions or design constraints on
    the solution." —— 需求层禁止混入"如何实现"。
  - "Assumptions and dependencies: acceptance of this specification means acceptance of
    the risks associated with these issues." —— 假设/依赖未声明 = 风险未转移。
  - "Apportioning of requirements... specify the procedure and justification that will
    allow modification of the requirements." —— 未说清变更流程 = 范围蠕变黑洞。
  - "Requirements should be concise, complete, unambiguous, verifiable, and necessary."
    —— 五性铁律（CCVTN）。
  - "When requirements are unstable or the project uses agile, fall back to per-requirement
    files instead of a monolithic SRS."（jam01 重制版明示）
- **与三 skill 场景的映射**：**需求**（light/full 输出中的"现状分析 + 范围 + 用户故事 +
  AC"等价于 IEEE 830 的 §1-§3 子集）。
- **来源 URL**：
  - https://standards.ieee.org/ieee/830/3497/（IEEE 官方摘要）
  - https://press.rebus.community/requirementsengineering/back-matter/appendix-c-ieee-830-template/
    （Rebus Community 完整模板 + 示例）
  - https://github.com/jam01/SRS-Template（现代 markdown 版 + 29148 验证指引）
  - https://www.scribd.com/document/162781460/SRS-Format（带注释的 IEEE 830-1998 TOC）

---

## 范本 2：arc42（架构文档）

- **来源**：Dr. Gernot Starke & Dr. Peter Hruschka（2005 至今），CC 开源，
  https://arc42.org/ 。已发布 v9.0（2025-07）；提供 EN/DE/ZH/ES/FR/IT/NL/PT/RU/UK 等
  10 种语言。中文版 9.0 由 Chris Y 杨 2025-10 贡献。
- **适用场景**：
  - **中-大型系统**的架构基线（持续维护的"活文档"）
  - **架构决策记录（ADR）**与系统全貌的合并载体
  - 适合敏捷/精益/正式项目；不适合"小变更"——会过度文档化
- **标准结构（12 个固定章节，顺序强约束）**：
  1. **Introduction & Goals** —— 需求摘要 + Top 3-5 质量目标 + 利益相关者表
  2. **Architecture Constraints** —— 任何限制设计选择的外部/内部约束
  3. **System Scope & Context** —— 外部接口（业务视角必须，技术视角可选）
  4. **Solution Strategy** —— 核心方案思路（技术、顶层分解、达到质量目标的途径）
  5. **Building Block View** —— 源码/模块静态分解（白盒/黑盒嵌套层次）
  6. **Runtime View** —— 关键运行时场景（用例/特性/错误/异常）
  7. **Deployment View** —— 硬件基础设施 + 软件到基础设施的映射
  8. **Crosscutting Concepts** —— 横切关注点（领域模型、架构模式、持久化、日志、异常
     处理、安全、构建/部署规则）
  9. **Architectural Decisions** —— 重要决策 + 理由（轻量 ADR）
  10. **Quality Requirements** —— 质量树 + 质量场景（与 §1.2 顶级质量目标呼应）
  11. **Risks & Technical Debt** —— 已知风险与技术债（"团队最不爽的是什么"）
  12. **Glossary** —— 通用语言/术语表（多语言项目含翻译对照）
- **强制要素（must-have）**：
  - **§1 利益相关者表**（stakeholder × expectation）—— 缺失则无法做 trade-off
  - **§4 Solution Strategy 段落**（不只列技术，要给"为什么"）
  - **§5 Building Block 至少两级**（黑盒顶层 + 至少一个白盒展开）
  - **§9 决策与理由**（decision + rationale，必配）
  - **§10 质量场景以"刺激→响应→可度量"格式写出**
  - **§11 风险登记**（不只是列，还需 owner + 缓解措施）
  - 章节编号严格固定 —— 不允许插入 1.5 或 2a，新增内容用 sub-numbering（1.2.1）"塞入"
- **模板自带的反模式/陷阱**（来自 docs.arc42.org FAQ + Florian Lenz "practical series"）：
  - "Write the smallest amount of documentation that prevents expensive misunderstandings."
    —— 反对"营销材料式"和"小说式"大部头。
  - "Do not invent details you do not know yet and do not pretend you will get it right on
    the first try." —— 反对"伪确定性"：宁标 TBD，不要硬编。
  - "If you get way beyond [20 pages], split the problem into manageable sub problems."
    —— 长度上限的硬约束。
  - "If the boundaries [context and scope] are unclear, integrations and expectations will
    break first." —— 上下文未明 = 集成先爆。
  - "Arc42 docs are not a deliverable. They are a feedback loop." —— 反对"一次性写完
    永不更新"。
  - "Group chapters into themes (Why & where / How is it built / Reusables / Reality) to
    avoid 'why does this chapter exist' confusion." —— 反对孤立看待 12 个章节。
- **与三 skill 场景的映射**：**设计**。尤其 §4-§7 直接对应"如何改 / 改哪里 / 怎么动 /
  怎么部署"；§9 + §11 对应 impact 输出的"决策理由 + 风险/技术债"。
- **来源 URL**：
  - https://arc42.org/overview（官方章节速览）
  - https://arc42.org/documentation/（完整文档站点）
  - https://github.com/arc42/arc42-template（AsciiDoc 源 + 多语言）
  - https://blog.hompus.nl/2026/02/01/arc42-practical-series/（2026 实践指南，含
    "Done-when checklist"）
  - https://dev.to/florianlenz/arc42-for-your-software-architecture-the-best-choice-for-sustainable-documentation-383p

---

## 范本 3a：Google Design Doc（实施/设计衔接）

- **来源**：Google 工程文化（由 `industrialempathy.com` 2020-07 整理，被视为 Google 内部
  实践的非官方对外权威解释）。
- **适用场景**：
  - **中等规模**的设计澄清文档（10-20 页 sweet spot；1-3 页 mini-doc 也可）
  - 编码"前"的探索性设计
  - 适合需要 senior review 与组织共识的设计决策
  - **不适合**纯实现手册（无 trade-off 的）、纯原型迭代、trivial bug fix
- **标准结构（章节列表）**：
  1. **Context and Scope**（1-2 段；"这不是需求文档"—— 保持精简）
  2. **Goals and Non-Goals**（bullet list；非目标是"explicitly chosen not to be a goal"，
     不是"negated goal"）
  3. **The Actual Design**（先 overview 再 detail；含 System-context-diagram, API
     sketches, Data storage, Code/pseudo-code 可选, Degree of constraint 分析）
  4. **Alternatives Considered**（每个备选方案给出 trade-off；本节是文档最重要的之一）
  5. **Cross-cutting Concerns**（observability/security/privacy 等，每团队应统一列表）
  6. （可选）Open Questions / Follow-ups
- **强制要素（must-have）**：
  - **Goals + Non-Goals 分明**（"ACID compliance" 是经典 non-goal 例子）
  - **Alternatives Considered 章节**（不写 = "自吹自擂"，失去 review 价值）
  - **Trade-offs 显式记录**（context → goals → design 的因果链）
  - **Cross-cutting concerns 必含**（Google 强制 privacy + security review）
  - **10-20 页 sweet spot**；超长 = 应拆分
- **模板自带的反模式/陷阱**（来自原文显式警告）：
  - "Design docs are informal documents... don't follow a strict guideline. Rule #1 is:
    Write them in whatever form makes the most sense for the particular project." ——
    **反"僵硬套模板"**。
  - "This isn't a requirements doc. Keep it succinct!" —— 反对把 SRS 内容抄进设计文档。
  - "In most cases, one should withstand the temptation to copy-paste formal interface or
    data definitions into the doc as these are often verbose, contain unnecessary detail
    and quickly get out of date." —— 反对贴完整 IDL/Schema。
  - "Design docs should rarely contain code, or pseudo-code except in situations where
    novel algorithms are described." —— 反对"用设计文档当代码注释"。
  - "A clear indicator that a doc might not be necessary are design docs that are really
    implementation manuals." —— **反对"伪设计 doc"**：无 trade-off = 不必写。
  - "Subscribing to agile methodologies is not an excuse for not taking the time to get
    solutions to actually known problems right." —— 反对以"敏捷"为由跳过设计澄清。
  - "If the designed system hasn't shipped yet, then definitely update the doc." ——
    反对"doc 与现实漂移"。
- **与三 skill 场景的映射**：**实施前置设计**（impact 输出的"替代方案对比 + 决策理由"直
  接对应 §4 + §5）。1-3 页 mini-doc 对应"小变更"场景。
- **来源 URL**：
  - https://www.industrialempathy.com/posts/design-docs-at-google/（主源）
  - https://www.industrialempathy.com/posts/design-docs-a-design-doc/（示例 doc）

---

## 范本 3b：Microsoft Security Development Lifecycle（SDL）—— 实施/验证/发布

> 备注：选 3a（Google Design Doc）覆盖**实施前**的设计；选 3b（Microsoft SDL）覆盖
> **实施中+实施后**的验证与发布。两者合并 = "实施/测试"完整覆盖。

- **来源**：Microsoft Security Engineering，自 2004 年起系统化。官方页面
  `microsoft.com/securityengineering/sdl`；实践细节
  `learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle`。
- **适用场景**：
  - 任何对安全/合规有要求的中大型项目（默认必选）
  - 不适合"一行脚本 fix"型变更
  - 与 SDLC 平行运行（**SDL ⊇ SDLC，不替代 SDLC**）
- **标准结构（5+1 阶段）**：
  1. **Training**（基础）—— 开发者必须懂安全基础、攻击者视角
  2. **Requirements** —— 与业务需求**并行**定义安全需求（NIST SSDF / PCI DSS 4.0 / OWASP
     对齐）；设定"最低可接受安全水平" + bug bar（按 severity 强制修复时限）
  3. **Design** —— 威胁建模（STRIDE / DFD）；定义加密标准；第三方组件清单 + 漏洞响应计划
  4. **Implementation** —— 安全编码标准 + peer review（安全焦点）+ 白盒源码扫描
     （SAST/IDE 插件）+ 已批准工具集
  5. **Verification** —— SAST + DAST + 渗透测试 + SCA（软件成分分析）+ Fuzz
  6. **Release** —— 最终安全审查 + 配置验证 + 事件响应（IR）计划就位
  7. **Response**（持续）—— 监控 + 事件响应 + 度量反馈到下个周期
- **强制要素（must-have）**：
  - **Bug bar**（按 severity 分类的修复时限 + 责任人）
  - **Threat model**（STRIDE 或等价方法；组件/应用/系统三级）
  - **加密标准**（避免"自选算法"；库要可替换）
  - **第三方组件清单**（SBOM）+ 漏洞响应计划
  - **SAST/DAST 集成 CI/CD**（"shift-left"）
  - **IR 计划 + PSIRT 协调**（必须**测试过**才能上线）
  - **KPI 跟踪**（漏洞密度、MTTR、培训完成率）
  - **每阶段都有可交付物**（见下表）：
    | 阶段 | 输出 |
    |------|------|
    | Requirements | Security requirements doc, compliance checklist |
    | Design | Threat model, security architecture review |
    | Implementation | Secure code review checklist, code scanning results |
    | Verification | Security test results, vulnerability backlog |
    | Release | Security sign-off, deployment config review |
    | Response | Incident reports, vulnerability remediation metrics |
- **模板自带的反模式/陷阱**（来自多篇 SDL 实践指南 + GitHub 资料汇总）：
  - "Considering security the last phase before releasing the product" —— **反"后置安全"**
    ；安全是平行过程。
  - "Security requirements must be continually updated" —— 反对"安全需求一次性写定"。
  - "Data must be encrypted when transmitted or stored. Incorrect choice of cryptography
    can be catastrophic." —— 反"自选加密"。
  - "It is best to have or develop a encryption standards. Encryption libraries must be
    implemented in a way that can be replaced easily when needed." —— 反"加密硬编码"。
  - "Analyzing source code before compilation: is a highly scalable method" —— SAST 必须前
    置到 IDE / commit 阶段，不能只在 release 前跑。
  - "Preparing an Incident Response (IR) Plan is essential... IR Plan should be tested
    before it is needed !" —— 反"未测试的 IR 计划 = 没计划"。
  - "Set a Bug Bar (Bug Level or Severity)... All bug levels must fix in a specified
    time" —— 反"无限期挂起的高危漏洞"。
- **与三 skill 场景的映射**：**实施 + 验证 + 发布**。尤其对应"反模式/陷阱"清单的设计——
  这正是三 skill 当前模板最缺的（详见后续对照报告）。
- **来源 URL**：
  - https://learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle
  - https://www.microsoft.com/en-us/securityengineering/sdl/practices
  - https://github.com/nxenon/DevSecOps/blob/main/Design/Development-Lifecycle/SDL-by-Microsoft.md
    （GitHub 镜像版，含 Threat Modeling 详解）
  - https://www.securityjourney.com/post/security-development-lifecycle-sdl-definition-best-practices
    （2026 实践综述，SDLC × SDL 关系表）

---

## 跨范本共同特征（用于三 skill 模板对照）

| 维度 | IEEE 830 | arc42 | Google Design Doc | Microsoft SDL |
|------|----------|-------|-------------------|----------------|
| 唯一编号/可追溯 | REQ-N.N | §n.n | （doc-as-code） | Bug bar / work item |
| 利益相关者表 | 隐式（intended audience） | **显式 §1** | 隐式（goals/non-goals） | 隐式 |
| Goals vs Non-Goals | 隐式 | §1.2 质量目标 | **显式 + 强调** | 安全需求/非安全需求 |
| 替代方案 + 理由 | 隐式 | §9 决策 | **§4 Alternatives Considered 必填** | Threat model |
| 跨切面关注点 | 隐式 | **§8 Crosscutting** | **显式必含** | privacy/security/IR |
| 反模式自检 | 散落注释 | docs.arc42.org FAQ | **原文 6+ 显式禁令** | **"shift-left" 4+ 禁令** |
| 长度上限 | 无硬限 | ~20 页 | **10-20 页 sweet spot** | 阶段交付物制 |
| 修订/版本控制 | 强制 | version.properties | "doc 与现实漂移"警告 | 持续 response 循环 |
| 验证/可追溯矩阵 | §4 verification | §10 质量场景 | review rounds | SAST/DAST/SCA/pen-test |

**总结**：四份范本的**共同最小集**：

1. 唯一编号 + 可追溯矩阵
2. Goals / Non-Goals 分明
3. 替代方案 + trade-off 显式
4. Cross-cutting 必含（安全/隐私/可观测）
5. 反模式自检（"避免 X"清单）
6. 长度/范围约束（反对大部头 + 反对无 trade-off 的伪设计）
7. 修订历史 + 持续维护承诺

这些是后续对照三 skill 模板"缺什么"时的基准线。
