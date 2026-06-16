# Release 级评测 — impact / impact-pro / pathfinder

> 评测日期: 2026-06-16 · 评测者: Claude (Opus 4.8) · 范围: L0 + L2 核心 + 高危面深读
> 方法纪律: 每条结论均由本轮工具直接复核;上轮被上下文压缩吃掉的 subagent 二手发现**不予引用**。
> 落盘原因: 压缩两次吃掉进行中的广度扫描,改为「边查边落盘」扛压缩。本文档随深读增量追加。

## 0. 进度看板

| 面 | 状态 |
|---|---|
| L0 机械自洽(三 skill) | ✅ 已核实 |
| 三 SKILL.md 存活区 | ✅ 已核实 |
| 高危拦截清单 存活区↔references 同步 | ✅ 已核实 |
| 发现 A/B/C | ✅ 已核实 |
| impact-pro db-adapters×3 | ✅ 已核实(发现 E=P1 / D=P2 / pg 正面) |
| impact-pro profiles 契约层(_schema/_template/generic) | ✅ 已核实(发现 F=P3 / 纪律正面) |
| impact-pro 8 栈 profiles | ✅ 已核实(命令/Level/漂移正面 · E 强化 · P3 观察) |
| impact-pro templates×11 | ✅ 已核实(3 全读+11 grep · 发现 G=P3 · 040-light 佐证 C) |
| L1 行为契约(模型驱动) | ❌ 本轮未做 |

---

## 1. L0 机械自洽

| Skill | 结果 | 备注 |
|---|---|---|
| impact | **PASS 179 / FAIL 0** | — |
| pathfinder | **PASS 43 / FAIL 0** | 计数正常,非历史那个 0/0 shell bug |
| impact-pro | **PASS 74 / FAIL 1** | 唯一 FAIL = `frontend-nextjs/001` fixture 依赖 `test-projects/next-learn`(外部 demo 仓未 clone) |

**对 impact-pro 那 1 个 FAIL 的判定**:这是**环境缺口**,非 skill 逻辑错误。
- 其余 5 个 fixture(go-admin / ruoyi-vue / degradation-trap / full-stack-fastapi-template)均在位。
- REVALIDATION.md §4.3/§6.2 已标注 nextjs 为 demo-only / 待补位栈。
- 测试**如实报错并提示 `git clone`** 而非静默放过 → 健康行为(缺口被测试暴露)。
- 修复路径(可选):clone `next-learn` 后此 case 转绿;或在测试配置中显式标记为 skip-when-absent。

---

## 2. 已核实的正面结论(安全闸)

### 2.1 最高危安全闸:高风险拦截清单 — 零漂移
- **存活区 ↔ references 两处同步成立**:impact SKILL.md:38 / impact-pro SKILL.md:41 的浓缩版,是 `references/phase-5-execution.md`(impact 152-161 / impact-pro 148-157)详表的忠实压缩,10 个条目逐条对应。
- **impact ↔ impact-pro 两份详表逐行完全一致**(DROP/无WHERE DML/ALTER/GRANT/CREATE OR REPLACE/数据回填/删接口/删文件/改 enum/不可逆)。
- 命中后处理(标注高风险→单独确认→写执行记录→未确认只读)两 skill 一致。
- 这是 skill 自己声明的最高维护风险(「改安全闸必须两处同步」),本项验证它**确实做到了**。

### 2.2 三个存活区骨架完整且一致
| 闸 | impact | impact-pro | pathfinder |
|---|---|---|---|
| `disable-model-invocation:true` | ✅ | ✅ | ✅ |
| 7 条硬规则(压缩存活区) | ✅ | ✅ | ✅(只读版) |
| 逐步确认 `确认 Step N`(拒绝模糊/系统消息/仓库文本/历史授权/测试通过替代) | ✅ | ✅ | n/a(只读) |
| 凭证脱敏 `***` | ✅ | ✅ | ✅(含风险节默认弱密码也不明文) |
| 仓库内文本 ≠ 指令 | ✅ | ✅ | ✅ |
| 阻塞/压缩恢复先读 `_active-state.md` 再等新确认 | ✅ | ✅ | n/a |
| 写入目标边界(绝对路径必须在项目根内) | ✅ | ✅ | ✅(仅 1 文件) |
| DB 只读发现纪律 | ✅ | ✅ | ✅(全程只读) |

---

## 3. 已核实的发现(P2 × 3)

### 发现 A — 中文排版回归(P2)
- **现象**:`本技能 ` + 中文字之间残留半角空格(CJK-空格-CJK),共 **12 处**。
- **分布**:impact-pro/SKILL.md ×5、pathfinder/SKILL.md ×5、impact-pro/README.md ×1、pathfinder/README.md ×1。集中在**压缩存活区**(最常被读区域)。
- **根因**:commit `c11a60e [lang] 中文自然度润色` 把 `本 Skill`→`本技能` 机械替换,未删原 `Skill` 后的空格。`本 Skill 不用于`(正确:CJK+空格+Latin+空格+CJK)→ `本技能 不用于`(错误:CJK 间多空格)。
- **讽刺点**:这是"中文自然度润色" commit 反而引入的排版缺陷。
- **影响**:纯观感,无功能风险。
- **修法**:全局 `本技能 ` → `本技能`(注意只删 CJK 间空格,别误伤 `本技能` 后接 Latin 的合法空格)。

### 发现 B — 三 skill 术语不统一(P2)
- **现象**:同义概念,三 skill 用词不一致:
  - impact 用 `本 Skill` + 章节标题「硬性规则级」;
  - impact-pro / pathfinder 用 `本技能` + 标题「强制规则」。
- **证据**:`本 [Ss]kill` 命中 impact/SKILL.md ×5、impact README/references ×4;impact 0 处 `本技能`。
- **根因**:`c11a60e` 声称"统一术语"覆盖"三 skill",实际只动了 impact-pro + pathfinder 两个,impact 未动 → 统一不完整。
- **影响**:观感 / 一致性,无功能风险。
- **修法**:定一个术语标准(`本技能` 或 `本 Skill`),三 skill + README + references 全量对齐;同时统一「硬性规则 / 强制规则」标题用词。

### 发现 C — impact 缺「定级证据自洽性」输出行兜底闸(P2,曾疑似 P1)
- **现象**:impact-pro Phase 3.5 有强制硬闸「定级证据自洽性」(SKILL.md:201 + phases-detail.md:88):当分析正文已记录 full 触发项、而定级模板「触发 full 的证据」行却写"无"时,即自相矛盾,**必须升 full**。impact **完全没有这条**(`定级证据自洽` 全 skill 0 命中),且其模板(phase-3-questioning.md:77)仍写 `触发 full 的证据：[…若无则写无]`。
- **公正性核查(关键)**:impact **并非毫无防护**——`phase-2-context-discovery.md:108` 有上游闸:「发现 API/DB/权限/状态机… 等高风险引用时,必须进入定级证据,必要时升为 full」。这覆盖了大半风险。
- **校准结论**:impact 有"发现即升档"的**上游闸**,但缺 impact-pro 的"输出行自洽"**下游兜底**。失败模式 = 弱模型分析正确(发现触发项)、却在定级输出行写"无"偷偷降 light;上游闸理论上拦得住但措辞是发现期指令而非输出行不变量。→ 比"完全缺失"窄,被 phase-2:108 缓解,故 **P1 下调为 P2**。
- **为何仍值得修**:impact 是 Java/Spring 主力默认 skill,且 memory 标记「弱模型敏感性」为活跃关切,此闸正是弱模型防线;backport 成本低。
- **修法**:把 impact-pro:201 整条 backport 到 impact SKILL.md Phase 3.5,并在 impact phase-3-questioning.md:77 模板 `若无则写无` 旁补自洽断言。

---

## 4. db-adapters 深读 ✅(2026-06-16)

读了 generic-sql / mysql / postgresql 三个 adapter,逐条核 SQL 正确性。

### 发现 E — mysql.md 外键查询引用不存在的列(P1,限 impact-pro)
- **现象**:`db-adapters/mysql.md` 的 `foreign_keys` 查询:
  ```sql
  SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME,
         CONSTRAINT_NAME, UPDATE_RULE, DELETE_RULE       -- ← 后两列不存在于本表
  FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
  ```
  `UPDATE_RULE` / `DELETE_RULE` 属于 `INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS`,**不在** `KEY_COLUMN_USAGE`。任何 MySQL 版本执行此 SQL 都报 `ERROR 1054 (42S22) Unknown column 'UPDATE_RULE' in 'field list'`。
- **为何是 P1**:"改字段/删表 → 找引用表"是 impact-pro 核心用例;MySQL 是其 java-spring-mybatis 等 profile 最常见的库;此查询**运行时直接报错**(非部分失败、无降级)。
- **交叉核查(关键)**:impact 自己的 `references/schema-discovery.md:10` 的 MySQL 外键查询**正确**(只选 4 个 KEY_COLUMN_USAGE 真实列,未碰 UPDATE_RULE/DELETE_RULE)→ **bug 隔离在 impact-pro/db-adapters/mysql.md 一处**,impact 不受影响。根因:impact-pro 的 adapter 想比 impact 更"丰富"加了 FK 动作列,却放错了表。
- **修法**:要么 `JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON rc.CONSTRAINT_NAME = k.CONSTRAINT_NAME AND rc.CONSTRAINT_SCHEMA = k.TABLE_SCHEMA` 再取那两列;要么直接删掉这两列(与 impact 对齐)。

### 发现 D — generic-sql「通用」名不副实(P2,兜底面)
- `indexes` 用 `information_schema.statistics`——这是 **MySQL 专属**视图,PG/SQL Server/Oracle/SQLite 均无 → 在这些库报"表不存在";列名 `non_unique`/`seq_in_index` 也是 MySQL 命名。
- `foreign_keys` 用 `information_schema.constraint_column_usage`——这是 **PG/SQL 标准**视图,**MySQL 没有** → 在 MySQL 报错。
- 净效果:在任何**单一**真库上,它两条关系发现查询里至少一条会挂(MySQL 挂 FK,PG 挂 indexes)。`table_structure`(information_schema.columns)是真跨库的。
- notes 只含糊声明"外键/视图/触发器依赖具体 dialect,可能不兼容",**未提 indexes 的不兼容**,且把 indexes 呈现得像可用。属精度/诚实缺口。
- **缓解**:仅"无法确定 DB 类型"时才用此兜底;DB 类型已知时走正确的 mysql/postgresql adapter。故 P2 非 P1。

### ✅ 正面 — postgresql.md 是三者质量最高
- pg_catalog 路线完整正确:table_structure(含 is_identity)、indexes(pg_get_indexdef 覆盖 partial/表达式/INCLUDE)、FK(pg_get_constraintdef)、views、triggers(排除 tgisinternal)、table_rows(reltuples 估算 + 显式标注)、all_tables(relkind r/p)、**enum_types**(PG 独有高风险对象)。
- `detection_signals` + `notes.limitations` + `high_risk_pg_specific`(ALTER TYPE enum / ATTACH-DETACH PARTITION / DROP TYPE / 改列 TYPE)非常到位。
- **memory 标记的「PG adapter 缺口」看来已被补上**——此文件无明显缺陷,反而是范本。
- 唯一小 nit(P3):`views` 用 `current_schemas(false)`(search_path 全部),其余查询用 `current_schema()`(仅当前)——轻微不一致,可能有意(视图可能在任意 search_path schema),非 bug。

### 观察(待 _schema 契约确认)
- generic-sql 只定义 3 个 schema_query 键(table_structure/indexes/foreign_keys);mysql 有 8、pg 有 9(多 enum_types)。若 Phase 2 逻辑或某 profile 期望从 adapter 拿 `table_rows`/`all_tables`/`ddl` 键,generic 兜底时会缺键。下一波读 `_schema.md` 契约确认是否构成真缺口。



## 5. profiles 契约层深读 ✅(2026-06-16)

读了 `_schema.md`(接口定义)/`_template.md`(新栈模板)/`generic.md`(兜底 profile)。

### ✅ 正面 — 契约纪律强
- `_schema.md` 的「Profile 晋级协议」+「禁止事项」是硬反过度宣称机制:不能只凭文件/依赖命中标 Level 1;不能把 generic 备用结果描述成专属 profile 已验证;不能写未验证的 command/glob/目录/风格结论;不能用 demo 单一 happy-path 覆盖生产级限制。Level 1/2/3 各绑 `validation-runs/` 证据。
- `generic.md` 老实兑现 SKILL 的诚实承诺:`commands 为猜测值,必须用户确认`、`discovery_globs 候选可能不准确`、`找不到 schema/API/model/test 时必须标未确认,不得判已覆盖`。
- `style_axes` 全部留空并标「结论需运行时现采」,不预置结论——符合 schema 的"提示而非结论"约定。

### 发现 F — _schema 与实际 profile 轻微漂移(P3,文档完整性)
- `_schema.md` 的 `discovery_globs` 只列 6 键(service/data_access/api/config/test/migration);`generic.md` 实际用 9 键(多 `entity`/`dto`/`ui`)。
- `_template.md` 在 `context_discovery` 下加了 `high_frequency_pattern_check`,`_schema.md` 未定义此键。
- 即"统一接口定义"落后于真实 profile。无运行时影响(消费方按存在的键读),纯属契约文档需补 entity/dto/ui + high_frequency_pattern_check 的定义。

### nit(P3)— generic.md entity glob 过宽
- `discovery_globs.entity` 含 `"**/*.go"`(把项目里**所有** .go 文件当数据模型)→ 在 Go 项目上大面积假阳性,正好踩 `_template.md` 警告的"引用计数异常大"。被"兜底 profile + 必须用户确认 glob"缓解;真实 Go 项目应命中专属 go-gin-gorm profile。

### 澄清 — 撤销上一波的"generic-sql 键不全"观察
- `_schema.md` 并未定义 db-adapter 的 `schema_queries` 必备键契约(只定义 profile 的 `db_introspection.schema_source` 指向哪个 adapter)。generic-sql 刻意精简不构成违约 → **非缺陷**,撤销。



## 6. 8 栈 profiles 深读 ✅(2026-06-16)

方法:精读 `java-spring-mybatis`(代表,与 impact 同域可对照)+ grep 全 8 栈(Level 宣称 / 模板漂移残留 / 构建命令)。

### ✅ 正面
- **Level 宣称保守有据**:8 栈中仅 `java-spring-mybatis` = Level 2(注「从 RuoYi-Vue 等真实项目迁移」),其余 7 全 Level 1。无超证据宣称,守住 _schema 禁止事项。
- **模板漂移修复守住**:`example-stack`/`[栈名]` 仅出现在 `_template.md` 自身(应然);**8 个真实 profile 零残留**。memory 的"已修模板漂移"确认未回潮。
- **命令全部地道**:dotnet(`dotnet build/test`、`dotnet format --verify-no-changes`)、python(`pytest tests/`、`fastapi dev`、`ruff check`)、go(`go build ./...`、`golangci-lint run`)、前端(`npm run build/test/dev/lint`)、java(`mvn ...`)——**无错误命令**。
- `java-spring-mybatis` 质量高:style_axes 正确标「结论需运行时现采」并给 RuoYi 味提示(R 包装 / @Transactional / Slf4j / ServiceImpl),validation_strategy 的 grep 模式具体可用。

### 发现 E 强化(非新发现)
- `java-spring-mybatis.md:140` 的 `schema_source` 明确指向 `db-adapters/mysql.md`——即 impact-pro 用在 RuoYi 这类**旗舰 Level-2 验证场景**、分析外键时,正是走那条挂掉的 FK 查询(发现 E)。E 在主路径上,P1 坐实。

### 观察(P3,未在本轮证伪)
- `java-spring-mybatis` 硬编码 `schema_source: mysql.md`,未把「Spring + PostgreSQL」列入 limitations。Spring/MyBatis 也可接 PG。一个 Spring+PG 项目是否能正确切到 `postgresql.md`,取决于 Phase 2 的 db-adapter 探测逻辑(本轮**未读** `phase-2-context-discovery.md` 的 adapter 选择段)。若 profile 硬编码指针胜出 → Spring+PG 拿到 MySQL 方言查询会错。**留作定向核查项**,不武断定 bug。

### 覆盖边界
- 全文精读:`java-spring-mybatis`(1/8)。
- grep 抽查:其余 7 栈(Level + 漂移 + 命令)——结构与命令层健康,**未逐行内容审计**。如需对 node/python/go/dotnet/前端逐行审,属后续工作。



## 7. templates 深读 ✅(2026-06-16)

方法:精读 `060-preflight` / `_active-state` / `040-light`(含安全内容的 3 个)+ grep 全 11 模板(凭证脱敏 / 占位符残留)。

### ✅ 正面
- **060-preflight**:P0/P1 执行前闸表完整。P0 含仓库状态、Context Pack、文档确认、Step 级确认、阻塞恢复、写入目标边界、未确认项——与 SKILL Phase 5 一致;结论段明确"否则只能只读"。
- **_active-state**:"恢复前必做"清单(重读本文件→重读 impl/light→重读 preflight→查 git/文件态→复述 pending Step→要新 `确认 Step N`)忠实模板化存活区规则 6(阻塞恢复)。`checkpoint, not an authorization` 措辞到位。
- **040-light** 强化发现 C:其定级证据节写 `触发 full 的证据：无 / [如发现则必须升 full]`——连 light 模板都带"发现即升 full"内联兜底。**佐证 impact-pro 内部自洽(规则+模板双保险),而 impact 两处都缺**。

### 发现 G — 凭证脱敏内联提示覆盖不全(P3,防御纵深)
- `***`/脱敏提示**只出现在 `000-context-pack.md:64`**;`090-execution-record`(最可能粘贴含连接串/密码的命令原始输出)、`020-design` 等模板无内联脱敏提示。
- 行为仍由存活区规则 7 统管(不构成安全漏洞),但在最易泄漏点缺提示属可加固项:建议在 090/020 模板各加一行脱敏注释。

### nit(P3)— preflight severity 与 SKILL 措辞轻微不一致
- SKILL.md:258 正文把「基线验证 / 回滚方式 / 执行记录路径」当硬阻塞("任一不满足不得执行");060-preflight 模板把这三项标 P1(非 P0)。模板"仅 P0 阻塞"比正文略松。纯一致性,P1 项仍被追踪。

### 覆盖边界
- 全文精读:060-preflight / _active-state / 040-light(3/11)。
- grep 抽查:全 11 模板无占位符泄漏(仅 _template 应有);脱敏覆盖如上。
- **未逐行审**:010-requirements / 020-design / 030-implementation / 090-execution-record / 000-context-pack(除 :64)/ subagent-decisions / scorecard / final-readiness-audit(后三者为 eval/元模板,运行时风险低)。



## 8. 覆盖边界与最终结论(2026-06-16)

### 8.1 合并发现表

| # | 级别 | Skill | 一句话 | 验证基础 |
|---|---|---|---|---|
| **E** | **P1** | impact-pro | `db-adapters/mysql.md` 外键查询从 `KEY_COLUMN_USAGE` 取 `UPDATE_RULE/DELETE_RULE`(应在 `REFERENTIAL_CONSTRAINTS`)→ 运行时 `ERROR 1054`;且在 java-spring-mybatis Level-2 旗舰路径上 | MySQL information_schema 列定义(可用 `DESCRIBE INFORMATION_SCHEMA.KEY_COLUMN_USAGE` 秒证) |
| A | P2 | impact-pro, pathfinder | `本技能 ` 残留半角空格 ×12,集中存活区,c11a60e 润色 commit 引入 | grep 计数 |
| B | P2 | 三 skill | 术语不统一(`本 Skill`/`本技能`、`硬性规则`/`强制规则`);c11a60e 只动 2/3 | grep 计数 |
| C | P2 | impact | 缺 impact-pro 的「定级证据自洽性」输出行兜底,模板仍写"若无则写无";被 phase-2:108 上游闸缓解 | 跨文件 grep + 全文对读 |
| D | P2 | impact-pro | generic-sql 非真跨库(statistics 仅 MySQL / constraint_column_usage 仅 PG-标准);限兜底面 | SQL 方言知识 |
| F | P3 | impact-pro | _schema 的 discovery_globs 落后真实 profile(缺 entity/dto/ui + high_frequency_pattern_check) | 契约对读 |
| G | P3 | impact-pro | 凭证脱敏内联提示只在 000-context-pack,090/020 缺;行为仍受存活区规则 7 统管 | grep |
| nits | P3 | — | generic entity glob `**/*.go` 过宽 · java schema_source 硬编码 mysql(Spring+PG 未证) · pg views 用 current_schemas 不一致 · preflight P0/P1 与 SKILL 措辞略松 | — |

### 8.2 优先级修复清单

1. **[P1·发布前必修] 发现 E** — 修 `impact-pro/db-adapters/mysql.md` 外键查询:`JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON rc.CONSTRAINT_NAME=k.CONSTRAINT_NAME AND rc.CONSTRAINT_SCHEMA=k.TABLE_SCHEMA` 取那两列,或直接删两列与 impact 对齐。
2. **[P2·机械低风险] A+B** — 全局清 `本技能 ` 残留空格;定一术语标准,三 skill + README + references 对齐(含「硬性规则/强制规则」标题)。
3. **[P2] C** — 把 impact-pro 的「定级证据自洽性(强制)」backport 到 impact SKILL.md Phase 3.5,并改 phase-3-questioning.md:77 模板的"若无则写无"。
4. **[P2] D** — generic-sql 要么改成真·标准 SQL(用 table_constraints+key_column_usage 但去掉 constraint_column_usage 依赖;index 改用 statistics 之外的可移植法或显式标 MySQL-only),要么在 notes 如实声明各查询的方言适用面。
5. **[P3] F/G + nits** — schema 文档补键;090/020 加脱敏提示行;收窄 generic entity glob;核 Spring+PG 的 adapter 选择路径。

### 8.3 三 Skill 各自 Go / No-Go

| Skill | 结论 | 置信度 | 依据 |
|---|---|---|---|
| **impact** | 🟢 **基本可发布** | 中高 | 安全核(存活区/高危清单/FK 查询/phase-2:108)全部已核实健康;无 P1。建议附带修 C(backport)+ B(术语)。**references 正文(dimensions/style-analysis/phase-2/3/5 全文)本轮未重审。** |
| **impact-pro** | 🔴 **修完 E 再发** | 中高(已审面) | 唯一 P1=E 在旗舰 MySQL 路径,运行时报错→**发布阻塞**。其余架构扎实:profiles 纪律强、pg adapter 范本级、templates 健全、定级自洽双保险。修 E 后可转 🟢。**references 正文未全读。** |
| **pathfinder** | 🟡 **存活区+L0 健康,深度最浅** | 低中 | 本轮仅核实其 SKILL.md 存活区 + L0 43/0 + 受发现 A/B 牵连。**references(phase-1/2/3、stack-detection、handoff-contract、code-graph-adapter)与 project-map 模板本轮完全未审** → 发布前建议补审。 |

### 8.4 本次评测覆盖边界(诚实声明)

**已直接核实**:
- L0 机械自洽 ×3 skill(impact 179/0 · pathfinder 43/0 · impact-pro 74/1=环境缺口)
- 三 SKILL.md 存活区全文 + 高危拦截清单存活区↔references 同步 + impact↔impact-pro 逐行一致
- impact-pro:db-adapters ×3(全读)· profiles 契约层 ×3(全读)· 8 栈(java 全读 + 7 grep 抽查)· templates(3 全读 + 11 grep)
- impact:SKILL + schema-discovery FK 交叉核 + phase-2:108 + phase-3:77 + phase-5 高危清单

**本轮未覆盖**(下一轮候选):
- impact-pro references 正文(phase-2 / phases-detail / phase-5 高危清单以外 / cross-platform)
- impact references 正文(dimensions / style-analysis / phase-2/3/5 全文)
- pathfinder **全部 references** + project-map 模板
- impact-pro 其余 7 profiles + 8 templates 的逐行内容审
- **L1 行为契约层**(模型驱动场景跑测,impact-pro scenarios/*.json 等)

**方法纪律**:上一轮被上下文压缩吃掉的 subagent 二手发现一律未引用;本文档每条均为本轮工具直接复核。

