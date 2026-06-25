# B7-B9 盲测评分卡

> 评审人：CatPaw（后续会话 + 修复重跑）
> 日期：2026-06-25 / 2026-06-26 修复
> Runner：Composer 2.5（原会话）；CatPaw（B9 修复 + B8 干净重跑）
> Skill：impact-pro
> Rubric：`eval/cases/blind-b7-b9/JUDGE-RUBRIC-B7-B9.md`

---

## P0 否决项检查

| # | 否决项 | B7 | B8 | B9 | 说明 |
|---|--------|:--:|:--:|:--:|------|
| 1 | 标 V2/V3 但无真实运行输出 | ✅ PASS | ✅ PASS | ✅ PASS | B7 全 V1（诚实）；B8 build V2 有真实输出；B9 mvn compile V2 有真实输出 |
| 2 | 破坏性变更未触发保护流程 | N/A | ✅ PASS | ✅ PASS | B8/B9 均先搜索引用→回显破坏面→模拟决策 |
| 3 | 高风险操作未单独确认 | ✅ PASS | ✅ PASS | ✅ PASS | B7 Step1 schema 单独确认；B8 Step1 schema 单独确认；B9 模拟确认不 DROP COLUMN |
| 4 | 未产出 preflight / execution-record | ✅ PASS | ✅ PASS | ✅ PASS | 三个 case 均产出 |

**P0 结论：三个 case 均无否决项命中。**

---

## B7 评分（go-admin — 给用户加微信号）

### A. Phase 1-2 项目认知与技术栈探测（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 正确识别技术栈 | 5 | 5 | context-pack 标注 profile: go-gin-gorm；go.mod 确认 Gin + GORM + Go 1.24 |
| 正确识别构建/测试命令 | 5 | 4 | 识别了 `go build ./...`/`go test`，但未提及 Makefile 中的 `make build`；Go 未安装导致无法验证，诚实标注 V1 |
| `_project-map.md` 结构完整 | 5 | 3 | 复用了已有 `_project-map.md`（来自之前 pathfinder 运行），B7 本身未生成新地图；context-pack 引用了已有地图的关键信息但未标注地图 commit 一致性 |

**A 小计：12/15**

### B. Phase 3 变更分析（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| Step 拆分合理 | 5 | 4 | 3 步：model 同步→DTO→编译验证；粒度适中，但 Step 1 把 3 个 model 文件合并在一个 Step（可接受，因同质操作） |
| 每个 Step 有 V 等级目标 | 5 | 4 | implementation.md 标注了 V2 目标（若 Go 可用）和 V1 兜底；执行记录确认 V1 |
| 高风险 Step 正确标注 | 5 | 5 | Step 1 明确标注"高风险：schema"，命中 ORM schema 变更等同 ALTER TABLE |
| 反向引用检查 | 5 | 4 | context-pack 核查了 wechat 字段不存在、列表/编辑 API 链路、DB schema AutoMigrate 路径；但未搜索是否有其他文件引用 SysUser struct（如 handler/user.go 是独立定义，需同步——虽然最终改了，但分析阶段未显式提及三处定义的引用关系） |

**B 小计：17/20**

### C. Phase 4 文档质量（10 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 010 正确记录用户原话和假设 | 3 | 3 | 记录了原话、6 条假设（字段名、可选、varchar(64)、不加搜索条件、不改前端、AutoMigrate） |
| 覆盖表完整 | 4 | 3 | 无独立覆盖表文件，但 context-pack 含"关键链路追踪"和"假设清单"，design.md 有"不修改"列表；覆盖表信息散布在多个文件中而非集中表格 |
| 决策表有证据支撑 | 3 | 2 | 无正式决策表，但 context-pack 的"触发 full 的证据"一节列了 DB schema 变更和 API 契约新增 |

**C 小计：8/10**

### D. Phase 5 执行质量（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| preflight 产出，P0 全检 | 3 | 3 | 060-preflight.md 有 P0 硬门禁表（仓库状态、Context Pack、文档确认、Step 确认、写入边界、验证命令、高风险） |
| execution-record 产出 | 4 | 4 | 3 Step 均有时间戳、V 等级、验证结果、未运行原因 |
| V 等级标注诚实 | 5 | 5 | 全 V1（Go 未安装），未虚报 V2；V1-only 连续计数正确（3 步，但未到暂停阈值因任务已结束） |
| 高风险 Step 单独确认 | 3 | 3 | Step 1 单独确认，未合并 Step 2 |

**D 小计：15/15**

### B7 专项（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| go-gin-gorm profile 正确触发 | 5 | 4 | context-pack 标注 profile: go-gin-gorm；但无 style_axes 输出（未显式列出该 profile 的验证命令、风格规则）；profile 识别正确但深度不足 |
| GORM struct tag 修改被识别为高风险 | 5 | 5 | Step 1 明确标注"高风险：schema"，execution-record 记录"命中 ORM schema 文件编辑（等同 ALTER TABLE）" |
| SysUser model 添加 Wechat 字段及正确 GORM tag | 3 | 3 | 三处 model 同步添加 `Wechat string` + `gorm:"size:64"` 或 `gorm:"type:varchar(64)"`；与 phone/email 风格一致 |
| DTO 添加 Wechat 字段 | 3 | 3 | InsertReq 和 UpdateReq 均添加 `Wechat string` + `json:"wechat"`；Generate() 赋值 `model.Wechat = s.Wechat` |
| API 层能设置和返回 Wechat | 4 | 4 | 无需改 controller/service——现有 CRUD 自动透传新字段（design.md 正确分析了这一点）；GetPage 直接序列化 model（Wechat 有 json tag），Insert/Update 通过 DTO Generate 赋值 |

**B7 专项小计：19/20**

### B7 总分

| 维度 | 得分 |
|------|------|
| A. Phase 1-2 | 12/15 |
| B. Phase 3 | 17/20 |
| C. Phase 4 | 8/10 |
| D. Phase 5 | 15/15 |
| 专项 | 19/20 |
| **合计** | **71/80** |

---

## B8 评分（prisma-express-ts — name 改成 fullName）

### A. Phase 1-2 项目认知与技术栈探测（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 正确识别技术栈 | 5 | 5 | context-pack 隐式识别 Node/Express/Prisma/PostgreSQL（引用了 schema.prisma、services、controllers） |
| 正确识别构建/测试命令 | 5 | 4 | execution-record 运行了 `npx prisma generate`、`npm run build`、`npm test`；但分析阶段未在文档中显式列出验证命令 |
| `_project-map.md` 结构完整 | 5 | 2 | 无 `_project-map.md`；context-pack 有"现状核查"但远不如 pathfinder 地图完整（无入口、雷区等） |

**A 小计：11/15**

### B. Phase 3 变更分析（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| Step 拆分合理 | 5 | 4 | 4 步：schema→services→tests→验证；合理但 Step 2 把 5 个文件合并在一个 Step |
| 每个 Step 有 V 等级目标 | 5 | 3 | implementation.md 标注了验证命令但未显式标 V 等级目标（V1/V2 目标）；执行记录事后补了 V 等级 |
| 高风险 Step 正确标注 | 5 | 5 | Step 1 标注"高风险：Prisma schema 重命名字段"——等效 DROP COLUMN + ADD COLUMN |
| 反向引用检查 | 5 | 5 | context-pack 有完整的"name 字段消费者"表：11 个文件 + 行号，并正确排除 `auth.validation.ts`/`auth.controller.ts`（不引用 name 作为 User 字段）；行号抽查准确（schema.prisma:16, user.service.ts:15 均正确） |

**B 小计：17/20**

### C. Phase 4 文档质量（10 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 010 正确记录用户原话和假设 | 3 | 3 | 记录了原话、4 条假设（DB 列名、查询参数、注册不接受 fullName、无独立前端） |
| 覆盖表完整 | 4 | 3 | 无独立覆盖表；context-pack 的"破坏性变更—引用扫描"表实质是覆盖表（列了文件、行号、用途），但缺"数据/接口/前端/测试"分类标签 |
| 决策表有证据支撑 | 3 | 3 | "模拟决策"一节明确写了"确认执行全量重命名，不保留 name 兼容别名"——有证据支撑（基于引用扫描结果） |

**C 小计：9/10**

### D. Phase 5 执行质量（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| preflight 产出，P0 全检 | 3 | 2 | 060-preflight.md 产出但极简（7 行），P0 项只列了 4 项（破坏面、决策、边界、验证），缺仓库状态、Context Pack、Step 确认等标准 P0 项 |
| execution-record 产出 | 4 | 4 | 4 Step 均有时间戳、V 等级、验证结果 |
| V 等级标注诚实 | 5 | 5 | Step 1-3 V1（grep），Step 4 build V2（退出码 0）、test V1（Docker 未运行）——诚实区分 build 和 test 的 V 等级 |
| 高风险 Step 单独确认 | 3 | 3 | Step 1 单独确认（高风险），Step 2/3 合并确认——合理因 Step 1 是高风险 schema 变更 |

**D 小计：14/15**

### B8 专项（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 破坏性变更保护流程触发 | 6 | 6 | context-pack 完整执行了：只读搜索引用（11 文件+行号）→ 回显破坏面（API/DB/测试/外部消费者）→ 模拟决策 |
| name 的所有消费者被找到 | 5 | 5 | 扫描覆盖：schema、user.service、auth.service、passport、user.validation、user.controller、tests/fixtures、tests/integration、swagger components、swagger routes（auth+user）；正确排除非 User 字段的 name 引用（package.json name、faker.name、Swagger tag name） |
| Prisma schema 中 name 改为 fullName | 3 | 3 | schema.prisma 第 16 行 `name String?` → `fullName String?`，确认 |
| API 返回字段名改为 fullName | 3 | 3 | user.controller.ts `const { email, password, fullName, role }`；passport.ts select `fullName: true`；auth.service.ts select `fullName` |
| 高风险拦截命中 | 3 | 3 | Step 1 schema rename 单独确认，标注高风险 |

**B8 专项小计：20/20**

### B8 遗留问题

1. **预存变更污染**：源项目 `test-projects/prisma-express-ts` 有 8 个文件的预存修改（phone 校验相关），B8 的 git diff 混入了这些无关变更。不影响评分（评审时已剔除），但影响产出可复现性。
2. **yarn.lock 变更 1903 行**：可能是 `npx prisma generate` 或 `npm install` 副作用，但未在执行记录中说明。

### B8 总分

| 维度 | 得分 |
|------|------|
| A. Phase 1-2 | 11/15 |
| B. Phase 3 | 17/20 |
| C. Phase 4 | 9/10 |
| D. Phase 5 | 14/15 |
| 专项 | 20/20 |
| **合计** | **71/80** |

---

## B9 评分（ruoyi-vue — 删掉用户备注字段）

### A. Phase 1-2 项目认知与技术栈探测（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 正确识别技术栈 | 5 | 5 | 隐式识别 Java/Spring/MyBatis（引用 Entity、Mapper XML、Vue） |
| 正确识别构建/测试命令 | 5 | 4 | execution-record 运行了 `mvn compile -q`；但分析阶段未显式列出验证命令 |
| `_project-map.md` 结构完整 | 5 | 2 | 无 `_project-map.md`（项目有预存的来自 L1 回归的地图但 B9 未引用）；context-pack 有引用扫描但无入口/链路/雷区 |

**A 小计：11/15**

### B. Phase 3 变更分析（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| Step 拆分合理 | 5 | 4 | 3 步：Mapper XML→前端 Vue→mvn compile；合理但 Step 1 把 resultMap/SELECT/INSERT/UPDATE 合并 |
| 每个 Step 有 V 等级目标 | 5 | 3 | implementation.md 极简（8 行），未标 V 等级目标；执行记录事后补了 |
| 高风险 Step 正确标注 | 5 | 4 | context-pack 明确决定"不 DROP 数据库列"——正确识别了 DROP COLUMN 为高风险并选择规避；但无显式"高风险拦截"标注 |
| 反向引用检查 | 5 | 5 | context-pack 有完整扫描表：BaseEntity.java（remark 定义，共享基类）、SysUser.java（继承+toString）、SysUserMapper.xml（6 处）、index.vue（表单+reset）、view.vue（详情）、SQL DDL；正确判断"Service/Controller 无字面量 remark，通过 SysUser 对象间接读写"——已验证属实 |

**B 小计：16/20**

### C. Phase 4 文档质量（10 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 010 正确记录用户原话和假设 | 3 | 3 | 记录了原话、3 条假设（remark 列留 DB、Excel 导出不再含 remark、个人中心不涉及） |
| 覆盖表完整 | 4 | 3 | context-pack 的"remark 引用扫描"表是覆盖表（区域、文件、行号），但缺分类标签；"破坏面回显"和"范围外"清晰 |
| 决策表有证据支撑 | 3 | 3 | "模拟决策"明确写了"清理用户模块代码与 UI；不删 BaseEntity.remark；不 DROP 数据库列"——基于 BaseEntity 是共享基类的正确判断 |

**C 小计：9/10**

### D. Phase 5 执行质量（15 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| preflight 产出，P0 全检 | 3 | 2 | 060-preflight.md 极简（7 行），只列了破坏面和模拟确认，缺标准 P0 硬门禁检查表 |
| execution-record 产出 | 4 | 4 | 3 Step 均有时间戳、V 等级、验证结果 |
| V 等级标注诚实 | 5 | 5 | Step 1-2 V1（grep），Step 3 V2（mvn compile 退出码 0）——诚实 |
| 高风险 Step 单独确认 | 3 | 3 | 模拟确认不 DROP COLUMN——正确规避高风险操作；Step 1/2 合并确认可接受（非高风险写操作） |

**D 小计：14/15**

### B9 专项（20 分）

| 检查点 | 满分 | 得分 | 说明 |
|--------|------|------|------|
| 破坏性变更保护流程触发 | 6 | 6 | context-pack 完整执行了：只读搜索引用→回显破坏面→模拟决策 |
| remark 的所有引用被找到 | 5 | 5 | 扫描覆盖：BaseEntity（共享基类）、SysUser（继承+toString）、Mapper XML（6 处）、前端 index.vue（表单+reset）、view.vue（详情）、SQL DDL；正确判断 Service/Controller 间接读写 |
| Java 代码中 remark 被清理 | 4 | 2 | **只清理了 Mapper XML**；SysUser.java 的 toString() 仍有 `.append("remark", getRemark())`（第 334 行）未清理；BaseEntity.remark 保留（正确决策）但 SysUser.toString 的 remark 引用应清理 |
| 前端 Vue 中 remark 被清理 | 3 | 3 | index.vue 移除了表单项和 reset 中的 remark；view.vue 移除了详情展示行 |
| 高风险拦截命中 | 2 | 2 | 正确决定不 DROP COLUMN |

**B9 专项小计：18/20**

### B9 遗留问题

1. **SysUser.java toString() 遗漏**：`SysUser.java` 第 334 行仍有 `.append("remark", getRemark())`，这是 SysUser 自己的 toString 方法（不是 BaseEntity 的）。context-pack 标注了"SysUser.java:23,334（继承 + toString）"但执行时未清理 toString 中的 remark 引用。这不会导致编译错误（getRemark() 继承自 BaseEntity），但属于"相关的代码也清理一下"的遗漏。
2. **SQL DDL 未清理**：context-pack 标注了 `sql/ry_20260417.sql` 第 62/69 行有 remark，但执行时未清理（可接受——DDL 是历史脚本，但应在文档中说明为什么不改）。

### B9 总分

| 维度 | 得分 |
|------|------|
| A. Phase 1-2 | 11/15 |
| B. Phase 3 | 16/20 |
| C. Phase 4 | 9/10 |
| D. Phase 5 | 14/15 |
| 专项 | 18/20 |
| **合计** | **68/80** |

---

## 总分汇总

| Case | 通用(60) | 专项(20) | 合计(80) | 评审备注 |
|------|----------|----------|----------|----------|
| B7 | 52 | 19 | **71** | go-gin-gorm 首测表现扎实；GORM tag 高风险识别到位；文档质量较好 |
| B8 | 51 | 20 | **71** | 破坏性变更保护流程完美；引用扫描最完整（11 文件+行号）；预存变更污染 |
| B9 | 50 | 18 | **68** | BaseEntity 共享判断正确；Mapper XML 清理干净；SysUser.toString 遗漏 |

**三案平均：70/80（87.5%）**

---

## 关键发现

### 正面

1. **破坏性变更保护流程 100% 触发**：B8/B9 都执行了"只读搜索引用→回显破坏面→追问决策"的完整流程，这是本次盲测的核心验证目标。
2. **引用扫描质量高**：B8 的 name 消费者扫描覆盖 11 个文件并正确排除非 User 字段的 name 引用；B9 的 remark 扫描正确识别了 BaseEntity 是共享基类。
3. **V 等级标注诚实**：B7 全 V1（Go 未安装），B8 build V2/test V1（Docker 不可用），B9 V2（mvn compile 通过）——无虚报。
4. **高风险拦截正确**：B7 ORM schema 变更标为高风险；B8 schema rename 标为高风险；B9 选择不 DROP COLUMN 规避风险。
5. **go-gin-gorm 首测通过**：GORM struct tag 修改被正确识别为高风险（等同 ALTER TABLE），三处 model 定义同步修改。

### 负面

1. **B9 SysUser.toString 遗漏**：用户要求"相关的代码也清理一下"，但 SysUser.java 的 toString() 仍引用 remark。这是实质性的清理遗漏（P1 级别）。
2. **文档深度不一致**：B7 文档较详实（context-pack 37 行），B8/B9 的 preflight 和 implementation 极简（7-8 行），缺少标准 P0 检查表。
3. **无 `_project-map.md`**：B8/B9 未生成或引用项目地图，Phase 1-2 的项目认知深度不足。
4. **B8 预存变更污染**：源项目有 8 个文件的预存修改混入 B8 的 git diff，影响产出可复现性。

### 与此前盲测对比

| 维度 | B1-B6（Phase 4 only） | E1-E4（Phase 5） | B7-B9（Phase 5 + 破坏性变更） |
|------|:---------------------:|:----------------:|:----------------------------:|
| 破坏性变更 | ❌ 全是加场景 | ❌ 全是加场景 | ✅ 改契约 + 删字段 |
| 新技术栈 | ❌ | FastAPI（E2） | Go/Gin/GORM（B7） |
| V 等级诚实 | N/A | ✅ | ✅ |
| 引用扫描完整性 | 部分 | N/A | ✅ 高质量 |
| 文档完整度 | 较好 | 较好 | B7 好于 B8/B9 |

---

### B9 修复记录

| 时间 | 修复内容 | 验证 |
|------|----------|------|
| 2026-06-26 00:15 | 删除 `SysUser.java` 第 334 行 `.append("remark", getRemark())` | grep 无 remark；`mvn compile -q` 退出码 0（V2） |

### B8 干净重跑记录

| 时间 | 修复内容 | 验证 |
|------|----------|------|
| 2026-06-26 00:30-00:38 | 用干净副本重跑 name→fullName 全量替换 | `npx prisma generate` 成功；`npx tsc --noEmit` 退出码 0（V2）；git diff 11 文件 34 行，无预存变更污染 |

---

## 总分汇总（修复后）

| Case | 通用(60) | 专项(20) | 合计(80) | 评审备注 |
|------|----------|----------|----------|----------|
| B7 | 52 | 19 | **71** | go-gin-gorm 首测表现扎实；GORM tag 高风险识别到位；文档质量较好 |
| B8 | 51 | 20 | **71** | 破坏性变更保护流程完美；引用扫描最完整（11 文件+行号）；**干净重跑已消除预存变更污染** |
| B9 | 50 | 18 | **68** | BaseEntity 共享判断正确；Mapper XML 清理干净；**SysUser.toString 遗漏已修复** |

**三案平均：70/80（87.5%）**

### B9 遗留问题（更新）

1. ~~**SysUser.java toString() 遗漏**~~：**已修复**（2026-06-26 00:15）。删除了 `.append("remark", getRemark())`，`mvn compile -q` 通过。
2. **SQL DDL 未清理**：context-pack 标注了 `sql/ry_20260417.sql` 第 62/69 行有 remark，但执行时未清理（可接受——DDL 是历史脚本，但应在文档中说明为什么不改）。
