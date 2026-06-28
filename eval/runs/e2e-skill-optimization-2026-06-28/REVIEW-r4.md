# R4 评审结果：Java/Spring 跨栈 + 弱引导

> 评审已完成。两模型在换栈 + 弱引导下均有降分，但 Skill 跨栈泛化能力得到验证。

## 测试基本信息

| 项 | 值 |
|---|---|
| 轮次 | R4 |
| 测试项目 | `gothinkster/spring-boot-realworld-example-app`（Spring Boot 2.6.3 + MyBatis + SQLite） |
| 测试栈 | Java 11 / Spring Boot / MyBatis / Flyway / JWT / GraphQL (DGS) |
| 构建工具 | Gradle |
| 模型 | Composer 2.5 vs Step 3.7 Flash |
| Prompt 风格 | 口语化，不给实现提示，不列文件清单，不提醒 §6/§3.2/_active-state.md |
| R3→R4 变化 | 换栈（Node/Express/Prisma → Java/Spring/MyBatis）、减弱 prompt 引导 |

---

## Ground Truth

### 项目摸底（Task 1）

| 维度 | 正确值 |
|---|---|
| 技术栈 | Spring Boot 2.6.3, MyBatis 2.2.2, SQLite (dev.db), JWT (jjwt 0.11.2), Flyway, GraphQL (DGS 4.9.21), Lombok, Joda-Time 2.10.13 |
| 构建工具 | Gradle（build.gradle，非 Maven/pom.xml） |
| Java 版本 | 11 |
| 架构分层 | api/ → application/ → core/ → infrastructure/（DDD-lite 风格） |
| 入口 | `io.spring.RealWorldApplication` |
| 数据库表 | users, articles, article_favorites, follows, tags, article_tags, comments（7 张表） |
| 认证 | JWT via `JwtTokenFilter`，Spring Security `WebSecurityConfig`，BCrypt 密码加密 |
| MyBatis 配置 | XML mapper（`resources/mapper/*.xml`），`map-underscore-to-camel-case=true` |
| DB 迁移 | Flyway，`V1__create_tables.sql` |
| 代码风格 | Lombok 注解驱动（@Getter/@Data/@AllArgsConstructor），Joda-Time 而非 java.time，javax.validation |

### Task 2（Light — 列表不返回 body）

| 维度 | Ground Truth |
|---|---|
| 影响类型 | Light（读路径调整，无 schema 变更） |
| 核心文件 | `ArticleReadService.xml` `selectArticleData` SQL 片段含 `A.body articleBody` |
| 关联文件 | `ArticleData.java`、`TransferData.xml`、`ArticlesApi.java`、`ArticleQueryService` |
| 风险点 | 详情接口仍需返回 body |

### Task 3（Full — 草稿功能）

| 层 | Ground Truth |
|---|---|
| Schema | `articles` 新增 `status` 列，Flyway `V2__add_article_status.sql` |
| Domain | `Article.java` 新增 status，构造函数默认值 |
| Mapper (写) | `ArticleMapper.xml` insert/update 含 status |
| Mapper (读) | `ArticleReadService.xml` 列表查询加 `WHERE status='PUBLISHED'` |
| Service | `ArticleCommandService.createArticle()` 默认状态 |
| API | 新增 publish 端点或 status 参数 |
| 向后兼容 | V2 迁移 DEFAULT 'PUBLISHED' |
| GraphQL | 查询也应过滤 status（加分项） |

---

## Composer 2.5 评审

### Task 1: Pathfinder

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G1 脚本执行 | ✅ PASS | 0 | scan.json + git.json 均存在 |
| G2 Script Gate | ✅ PASS | 0 | 15 节齐全，三张 Mermaid 图 |
| G3 事实准确 | ✅ PASS | 0 | 栈/版本/架构全部正确，无事实错误 |
| G4 文件完整 | ✅ PASS | 0 | _project-map.md + facts/ 齐全 |
| G5 15 节齐全 | ✅ PASS | 0 | 【0】~【14】+ Executive Summary 全部产出 |
| 三张 Mermaid 图 | ✅ 有 | 0 | 架构图 + ER 图 + 主流程图 |
| 【14】代码风格 | ✅ 有 | 0 | 8 个观察轴，全部带证据 |

**亮点**：识别了 CQRS 读写分离、DDD-lite 分层、GraphQL DGS 与 REST 共用读模型、JWT HS512 签名算法。Executive Summary 的 Top 3 风险和 Gotchas 非常精准（jwt.secret 硬编码、CORS *、列表 SQL 含 body）。

**Task 1 得分**：95 / 100（A）

### Task 2: Impact Light

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G4 文件完整 | ✅ PASS | 0 | 000-context-pack.md + 040-light.md + _active-state.md |
| G6 拉取 L1 | ✅ PASS | 0 | 引用 _project-map.md【9】风险区域 |
| G7 不确定项分类 | ✅ PASS | 0 | 代码推断 + [假设] 分离 |
| G8 _active-state.md | ✅ PASS | 0 | 存在 |
| G9 假设标注 | ✅ PASS | 0 | 4 条假设集中列出 |
| Q3 Mapper 识别 | ✅ PASS | 0 | selectArticleData SQL 片段 + TransferData.xml resultMap |
| Q4 跨层覆盖 | ✅ PASS | 0 | XML mapper + DTO + QueryService + ArticlesApi + GraphQL Datafetcher |
| Q6 文档可读性 | ✅ 好 | 0 | 结构清晰，实施步骤可执行 |

**亮点**：识别了 GraphQL `ArticleDatafetcher.buildArticleResult` 也需要改动，这是跨栈分析中容易被遗漏的点。提出了 `selectArticleDataLite` 独立 SQL 片段方案，并考虑了 `@JsonView` 替代方案。

**Task 2 得分**：93 / 100（A）

### Task 3: Impact Full

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G4 文件完整（四文档+状态） | ✅ PASS | 0 | 000 + 010 + 020 + 030 + _active-state |
| G6 拉取 L1 | ✅ PASS | 0 | 引用 _project-map.md CQRS 分层与【14】风格 |
| G7 不确定项分类 | ✅ PASS | 0 | 代码推断（V1__create_tables.sql）+ [假设] 分离 |
| G8 _active-state.md | ✅ PASS | 0 | 存在，4 条假设待确认 |
| G9 假设标注 | ✅ PASS | 0 | 6 条假设集中列出 |
| Q1 横切表 19 行 | ❌ FAIL | -15 | **§6 为"回滚方案"，横切关注点表完全缺失** |
| Q2 §3.2 API 验证表 | ❌ FAIL | -10 | **030-implementation.md 无 §3.2 API 方法验证表** |
| Q3 MyBatis mapper 变更 | ✅ PASS | 0 | INSERT/UPDATE 加 status、读查询加 WHERE status 过滤 |
| Q4 跨层覆盖 | ✅ PASS | 0 | Schema→Domain→Mapper(写/读)→Service→API→GraphQL，含 GraphQL schema 变更 |
| Q5 向后兼容 | ✅ PASS | 0 | V2 DEFAULT 'PUBLISHED' + 存量回填 |
| Q6 文档可读性 | ✅ 好 | 0 | 9 个 Step 清晰，引用变更矩阵完整 |

**关键问题**：设计文档 §6 标题为"回滚方案"而非"横切关注点"。在 R3 强引导下 C25 能产出横切表（92 分），但 R4 弱引导下完全遗漏。说明 C25 对 prompt 提示依赖度较高，Skill 模板本身的引导力不足。

**设计亮点**：默认 DRAFT + `POST /articles/{slug}/publish` 发布端点，更贴合用户原话"先存草稿，想好了再发布"。包含了 GraphQL schema 变更（ArticleStatus enum）。

**Task 3 得分**：75 / 100（B）

### Composer 2.5 总评

| 任务 | 得分 | 等级 |
|---|---|---|
| Task 1 Pathfinder | 95 | A |
| Task 2 Light | 93 | A |
| Task 3 Full | 75 | B |
| **综合** | **83** | **B** |

---

## Step 3.7 Flash 评审

### Task 1: Pathfinder

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G1 脚本执行 | ✅ PASS | 0 | scan.json + git.json 均存在 |
| G2 Script Gate | ✅ PASS | 0 | 15 节齐全，三张 Mermaid 图 |
| G3 事实准确 | ⚠️ 小瑕疵 | -2 | "MyBatis XML + 注解混用"表述不准确——项目全部 SQL 在 XML 中，@Mapper 只是接口标注 |
| G4 文件完整 | ✅ PASS | 0 | _project-map.md + facts/ 齐全 |
| G5 15 节齐全 | ✅ PASS | 0 | 【0】~【14】+ Executive Summary + 可选集 |
| 三张 Mermaid 图 | ✅ 有 | 0 | 架构图（subgraph 分层）+ ER 图 + 主流程图 |
| 【14】代码风格 | ✅ 有 | 0 | 11 个观察轴（比 C25 多 3 个），含 entity/dto/validation |

**亮点**：Pathfinder 地图 414 行，是两模型中最详细的。包含完整 REST API 路由汇总表（19 条路由 + 认证标注）、认证-鉴权字段一致性自检三步法、可选集（部署拓扑/可观测性/CI-CD）。主流程选了 POST /articles（创建文章），比 C25 的 GET /articles 更有代表性。

**Task 1 得分**：93 / 100（A）

### Task 2: Impact Light

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G4 文件完整 | ❌ FAIL | -3 | **缺 000-context-pack.md** |
| G6 拉取 L1 | ⚠️ 部分 | -2 | _active-state.md 提到"使用 Pathfinder 地图"，但 040-light.md 未显式引用 |
| G7 不确定项分类 | ✅ PASS | 0 | 代码推断 + [假设] 分离 |
| G8 _active-state.md | ✅ PASS | 0 | 存在 |
| G9 假设标注 | ✅ PASS | 0 | 2 条假设列出 |
| Q3 Mapper 识别 | ✅ PASS | 0 | selectArticleData + TransferData.xml resultMap |
| Q4 跨层覆盖 | ✅ PASS | 0 | XML mapper + DTO + Controller + GraphQL |
| Q6 文档可读性 | ✅ 好 | 0 | 含接口一致性自检表，是加分项 |

**亮点**：040-light.md 包含"接口一致性自检"表，检查写入路径与读取路径的 body 字段一致性，这是 C25 没有的。

**Task 2 得分**：85 / 100（A）

### Task 3: Impact Full

| 检查项 | 结果 | 扣分 | 备注 |
|---|---|---|---|
| G4 文件完整（四文档+状态） | ❌ FAIL | -3 | **缺 000-context-pack.md** |
| G6 拉取 L1 | ⚠️ 部分 | -2 | _active-state.md 提到"使用 Pathfinder 地图" |
| G7 不确定项分类 | ✅ PASS | 0 | 代码推断 + [假设] 分离 |
| G8 _active-state.md | ✅ PASS | 0 | 存在，86 行，非常详细（含 Step 台账、恢复检查） |
| G9 假设标注 | ✅ PASS | 0 | 5 条假设集中列出 |
| Q1 横切表 19 行 | ✅ PASS | 0 | **19 行全部产出，☑/☐ 明确标记** |
| Q2 §3.2 API 验证表 | ❌ FAIL | -10 | **030-implementation.md 无 §3.2 API 方法验证表** |
| Q3 MyBatis mapper 变更 | ✅ PASS | 0 | insert 加 status、新增 queryArticlesWithStatus 方法 |
| Q4 跨层覆盖 | ⚠️ 部分 | -3 | Schema→Entity→Mapper→ReadService→Service→Controller，**但明确排除 GraphQL** |
| Q5 向后兼容 | ✅ PASS | 0 | V2 DEFAULT 'PUBLISHED' + 索引 |
| Q6 文档可读性 | ✅ 好 | 0 | 030-implementation 299 行，含代码示例、时间线、环境备选 |

**关键优势**：**在无 prompt 提醒的情况下自主产出了 §6 横切关注点表**（19 行全部标记）。这是 C25 没做到的，说明 S37 更忠实地跟随了 Skill 模板流程。

**关键问题**：
1. 设计解读偏差——默认 PUBLISHED 而非 DRAFT，用户说"先存草稿，想好了再发布"暗示创建时应为草稿
2. 明确排除 GraphQL 层——"本次不做 GraphQL 层草稿支持"，而 C25 将其纳入分析
3. 无 publish 端点——只在创建时指定 status，不支持后续 DRAFT→PUBLISHED 流转

**Task 3 得分**：82 / 100（B）

### Step 3.7 Flash 总评

| 任务 | 得分 | 等级 |
|---|---|---|
| Task 1 Pathfinder | 93 | A |
| Task 2 Light | 85 | A |
| Task 3 Full | 82 | B |
| **综合** | **85** | **B** |

---

## 横向对比

| 维度 | Composer 2.5 | Step 3.7 Flash | 差值 |
|---|---|---|---|
| Task 1 Pathfinder | 95 | 93 | +2 |
| Task 2 Light | 93 | 85 | +8 |
| Task 3 Full | 75 | 82 | -7 |
| **综合** | **83** | **85** | **-2** |
| 等级 | B | B | |

### R3 → R4 对比

| 轮次 | 栈 | Prompt 风格 | Composer 2.5 | Step 3.7 Flash | 差值 |
|---|---|---|---|---|---|
| R3 | Node/Express/Prisma | 强引导（列文件、提要求） | 92 | 92 | 0 |
| R4 | Java/Spring/MyBatis | 弱引导（口语化、不给提示） | 83 | 85 | -2 |
| **降幅** | | | **-9** | **-7** | |

---

## 关键发现

### 1. 跨栈泛化：✅ 成功

两个模型都正确识别了 Java/Spring/MyBatis 栈的核心特征：
- **MyBatis XML mapper 模式**：无一混淆为 JPA/注解模式
- **Gradle 构建**：都注意到 build.gradle 而非 pom.xml
- **DDD-lite 分层**：都识别了 api → application → core → infrastructure 四层
- **Flyway 迁移**：都提出 V2 迁移脚本方案
- **CQRS 读写分离**：都注意到读走 ReadService + XML，写走 Repository + Mapper

**结论**：Skill 的 `java-spring-mybatis.md` profile 和 dimensions 在新栈上有效。

### 2. 弱引导下的自主性：部分退化

| 产出项 | R3（强引导） | R4 C25 | R4 S37 | 说明 |
|---|---|---|---|---|
| §6 横切关注点表 | 两模型都产出 | ❌ 缺失 | ✅ 产出 | C25 依赖 prompt 提醒；S37 跟随模板 |
| §3.2 API 方法验证表 | 两模型都产出 | ❌ 缺失 | ❌ 缺失 | 两模型都遗漏，模板引导力不足 |
| _active-state.md | 两模型都遗漏 | ✅ 产出 | ✅ 产出 | R3→R4 反而改善（V1 检查生效） |
| 000-context-pack.md | 两模型都产出 | ✅ 产出 | ❌ 缺失 | S37 认为light/full不需要，主动跳过 |

**核心发现**：§3.2 API 方法验证表在弱引导下两模型都遗漏。说明 Skill 模板中 §3.2 的强制力不够——模板里有占位但模型不填。需要将 V3 检查从 WARN 升级为 FAIL，或在模板中加更强的提示。

### 3. 模型特性差异

| 维度 | Composer 2.5 | Step 3.7 Flash |
|---|---|---|
| 设计解读 | 更贴合用户意图（默认 DRAFT + publish 端点） | 更保守（默认 PUBLISHED，无流转端点） |
| GraphQL 覆盖 | ✅ 纳入分析 | ❌ 明确排除 |
| 横切表自主性 | ❌ 依赖 prompt | ✅ 跟随模板 |
| context-pack | ✅ 产出 | ❌ 跳过 |
| 实施文档详细度 | 107 行（精炼） | 299 行（含代码示例、时间线） |
| Pathfinder 详细度 | 276 行（精准） | 414 行（最全面，含路由表） |

### 4. 质量降分归因

| 降分项 | C25 降分 | S37 降分 | 根因 |
|---|---|---|---|
| §6 横切表缺失 | -15 | 0 | C25 对 prompt 依赖度高 |
| §3.2 验证表缺失 | -10 | -10 | 模板引导力不足（两模型共同问题） |
| 000-context-pack 缺失 | 0 | -6 | S37 主观判断不需要 |
| GraphQL 排除 | 0 | -3 | S37 主动缩小范围 |
| 设计解读偏差 | 0 | -5 | S37 默认 PUBLISHED 不太贴合"先存草稿" |
| 事实小瑕疵 | 0 | -2 | S37 "XML + 注解混用"表述 |
| **合计降分** | **-25** | **-26** | |

> 两模型降分接近（-25 vs -26），但降分结构不同：C25 集中在横切表缺失（模板依从性），S37 分散在多个小项（范围判断 + 表述精度）。

### 5. R4 成功标准达成情况

| # | 标准 | 结果 |
|---|---|---|
| 1 | 跨栈不崩（G1-G4 全 PASS） | ✅ 达成（两模型门禁基本通过） |
| 2 | 弱引导下自主完成（§6/§3.2/_active-state） | ⚠️ 部分达成（_active-state 改善，§6 仅 S37 通过，§3.2 两模型都遗漏） |
| 3 | MyBatis 正确性（XML mapper 模式） | ✅ 达成（两模型都正确识别） |
| 4 | 质量不显著退步（≥80） | ✅ 达成（C25=83, S37=85） |
| 5 | 两模型差距 ≤ 10 分 | ✅ 达成（差距 2 分） |

---

## R4 后续优化建议

| # | 问题 | 建议措施 |
|---|---|---|
| O10 | §3.2 API 方法验证表在弱引导下被两模型遗漏 | `impact_validate.py` V3 检查从 WARN 升级为 FAIL |
| O11 | C25 在弱引导下遗漏 §6 横切表 | V10 检查在所有模式下生效（当前仅 full），或在模板 §6 标题注释中加更强提示 |
| O12 | S37 跳过 000-context-pack.md | 在 SKILL.md 或 phase-4-output.md 中明确 context-pack 为必产出文件 |
| O13 | S37 设计解读偏差（默认 PUBLISHED） | 在 phase-1-intent.md 中增加"用户原话→设计假设"的映射引导 |

---

## R4 优化实施记录（O10-O13 已完成）

### 根因分析

R4 暴露的根本问题不是 Skill 理念有误，而是**模板自身的引导力不足，之前靠 prompt 提示兜底**。具体表现：

1. **两模型都没跑 `impact_validate.py`** — SKILL.md 的 Phase 4 节只在 references 里提了脚本，没有像"逐步确认"那样做成强制规则。弱引导下模型不读 references 或读了不跟。
2. **C25 完全自创章节结构** — 030-implementation.md 用"## 1. 实施概览""## 2. Step 清单"替代模板的"## 1. 实施顺序""## 2. 前置检查清单""## 3. 执行步骤""## 3.2 API 方法验证"。SKILL.md 没说"必须按模板章节结构产出"。
3. **S37 跟了模板但跳过 §3.2** — §3.2 位于 §3（执行步骤）和 §4（回滚方案）之间，编号"3.2"让它看起来像可跳过的子节。
4. **S37 跳过 000-context-pack.md** — _active-state.md 写"不适用，使用 Pathfinder 地图作为 L1 上下文"。phase-4-output.md 只说"context-pack → 写入前必须获得用户确认"，没说两模式都必产出。
5. **S37 设计解读偏差** — 用户说"先存草稿，想好了再发布"，S37 默认 PUBLISHED + 无发布端点。phase-1-intent.md 缺少"用户原话→设计假设"的映射引导。

### 实施的修改

| # | 修改文件 | 修改内容 | 解决的根因 |
|---|---------|---------|-----------|
| O10a | `skills/impact/SKILL.md` | 强制规则加第 8 条：Phase 4 输出后必须跑 `impact_validate.py`，有 FAIL 不得提交。脚本结果须记入 _active-state.md | 模型不跑脚本 |
| O10b | `skills/impact/SKILL.md` | Phase 4 节加"必产出清单"表格：列出 full/light 各模式的必产出文件和必含节 | 模型不知道哪些是必产出 |
| O10c | `skills/impact/templates/030-implementation.md` | §3.2 标题改为"⚠️ 强制必做 — 缺此节 V3 FAIL 阻止提交"；§3 末尾加"⚠️ §3 写完后必须填写 §3.2"提醒 | S37 跳过 §3.2 |
| O11a | `skills/impact/SKILL.md` | Phase 4 节加"写每份文档前必须先 Read 对应模板，按模板章节结构产出，不得自创章节编号或跳过 ## 级别节" | C25 自创章节结构 |
| O11b | `skills/impact/SKILL.md` | 必产出清单明确列出 020 必含 `## 6. 横切关注点`、030 必含 `## 3.2 API 方法验证` | 两模型遗漏关键节 |
| O12a | `skills/impact/references/phase-4-output.md` | context-pack 说明改为"light 和 full 模式均必产出" | S37 认为 context-pack 不需要 |
| O12b | `scripts/impact_validate.py` | V1 检查在 light 模式下对缺 context-pack 报 WARN | 脚本没检查 light 模式 context-pack |
| O12c | `skills/impact/references/phase-4-output.md` | 输出验证节加"此步骤为 Phase 4 最后一步，跳过 = Phase 4 未完成" | 模型跳过脚本运行 |
| O13 | `skills/impact/references/phase-1-intent.md` | 新增"用户意图→设计假设映射"节，列出 4 种常见口语化模式及正确/错误推断 | S37 设计解读偏差 |

### 验证结果

用 R4 实际产出测试修改后的 `impact_validate.py`，确认门禁能捕获所有 R4 暴露的问题：

| 测试对象 | 门禁 | 预期 | 实际 |
|---------|------|------|------|
| C25 C2（020 缺 §6 横切表） | V10 | FAIL | ✅ FAIL — "missing §6 横切关注点 section" |
| S37 C2（030 缺 §3.2 验证表） | V3 | FAIL | ✅ FAIL — "no §3.2 API 方法验证 table" |
| S37 C2（缺 000-context-pack.md） | V1 | FAIL | ✅ FAIL — "Missing required file: 000-context-pack.md" |
| S37 C1（light 缺 context-pack） | V1 | WARN | ✅ WARN — "context-pack is required for both modes" |
| 现有 17 个单元测试 | — | 全通过 | ✅ 17/17 通过 |

### 设计原则

本次修复遵循的核心原则：**Skill 必须自给自足，不依赖外部 prompt 提示。** 具体体现为：

1. **关键要求上提到 SKILL.md 强制规则**（压缩存活区）— 不再只藏在 references 里
2. **必产出项用表格明示** — 不让模型自己猜哪些是必须的
3. **模板章节结构强制** — 不允许自创章节编号
4. **验证脚本运行强制** — 和"逐步确认"同级，不是可选项
