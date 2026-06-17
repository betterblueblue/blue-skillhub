# 三 Skill 模板骨架清单与缺失项盘点

> 范围：`skills/impact/templates/`、`skills/impact-pro/templates/`、`skills/pathfinder/templates/`
> 用途：作为「生产级对比」基线，识别三 skill 模板自身的不足。
> 方法：逐份用 Read 读取后人工提取；所有章节定位引用来自实际行号；「缺失项」基于 IEEE 830 / arc42 / SRE / 实施文档标准诚实判断。
> 统计：3 skill × 共 21 份模板（impact 9 / impact-pro 10 / pathfinder 1，另有 profiles/_template 与 _schema 算 2 份 profile 模板），合计 21 份（任务列出的 24 份是 3×8 的预算，实际 21 份按目录实有数；差额在 pathfinder 上）。

---

## 0. 任务范围说明

任务计划 3 skill × 8 模板 = 24 份；实际目录清单：

- **impact**：`000-context-pack.md` / `010-requirements.md` / `020-design.md` / `030-implementation.md` / `040-light.md` / `060-preflight.md` / `090-execution-record.md` / `_active-state.md` / `subagent-decisions.md` = **9 份**
- **impact-pro**：上述 8 份 + `final-readiness-audit.md` + `scorecard.md` = **10 份**
- **pathfinder**：仅 `project-map.md` 1 份（无 010/020/030 系列）
- **profiles**（与 impact-pro 配套）：`_template.md` + `_schema.md` 2 份

总计 22 份（不含 2 份 profile 模板）。本盘点按 22 份实际产出，「3×8=24」中多出的 2 份以 profile 模板补足。

---

# Part A — impact skill（9 份）

---

## 模板：impact/000-context-pack.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/000-context-pack.md`
- **行数**：102
- **章节骨架**：
  1. 变更意图（line 5-12）
  2. 源系统到目标系统对齐（如适用）（line 14-21）
  3. 上下文范围 L1/L2/L3 三层（line 23-30）
  4. 相关文件 4 级相关性（line 32-44）
  5. 接口/数据/配置 三子节（line 46-59）
  6. 测试和验证入口（line 61-67）
  7. 引用检查结果 4 分类（line 69-78）
  8. 已确认事实（line 80-82）
  9. 待确认问题（line 84-86）
  10. 暂不纳入范围（line 88-90）
  11. 上下文预算（line 92-100）
- **强制要素**：
  - [ ] L1/L2/L3 三层都有结论（line 25-29 表格）
  - [ ] 每个文件标 1-3 相关性 + 排除项写 0（line 35-37, 41-44）
  - [ ] 引用检查 4 分类至少各 1 行（line 71-76）
  - [ ] 「未找到引用」字面写明（line 78 注释）
  - [ ] 凭证脱敏 `***`（line 58 HTML 注释）
- **占位符**：`[用户原话]` `[路径]` `[命令/代码片段/引用]` `[API/Controller/Route]` `[表/字段/Entity/DTO/VO]` `[配置键/权限名/字典项]` `[N]` `[问题]`
- **自身反模式**：无显式「禁止」节；line 78 的「找不到写未找到引用，不得写成无影响」是唯一硬性禁止。
- **疑似缺失项**：
  - **没有「时间戳 / 快照版本」**——上下文会过期，应记录生成时间与基于的 git HEAD（pathfinder 模板有此，impact/impact-pro 没有）。
  - **没有「负责人 / 审阅人」字段**——Context Pack 写入前要求用户确认，但无审阅人签名栏。
  - **「接口/路由」粒度过粗**——只到 Controller 级，没有 method/路由名/method 级别。
  - **没有「数据敏感度分级」**——哪些字段是 PII / GDPR / PCI 应当标记，本模板完全没有隐私视角。
  - **「测试和验证入口」只列存在与否**，缺当前可达到的覆盖率（branch coverage / line coverage 数值），无法判断修改后的测试是否真的覆盖了变更。
  - **「上下文预算」是数量约束**，没有「如果 L3 超过 6 个文件片段怎么办」的强制收敛动作（仅说"下一轮收敛问题"line 98-100，没有强制 3 题上限）。
  - **没有「拒绝 / 重做」的 checkpoint**——发现 L1 错配时应触发什么动作无说明。

---

## 模板：impact/010-requirements.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/010-requirements.md`
- **行数**：49
- **章节骨架**：
  1. 变更背景（line 8-10）
  2. 需求描述 + 当前假设与歧义 + 未确认项（line 12-27）
  3. 变更范围 In/Out Scope（line 29-32）
  4. 约束条件（line 34-38）
  5. 验收标准（line 40-44）
  6. 依赖关系（line 46-48）
- **强制要素**：
  - [ ] 凭证脱敏（line 3 强制规则）
  - [ ] 用业务语言而非技术语言（line 5-6 顶部警示）
  - [ ] 需求与设计分离（line 5 顶部 blockquote）
  - [ ] 任务规模（line 23）
  - [ ] 成功标准可验证（line 23）
  - [ ] Out of Scope 显式排除（line 31）
- **占位符**：`[变更名称]` `[为什么要做这个变更]` `[用业务语言描述]` `[已理解的目标]` `[多种理解]` `[更简单方案]` `[可验证的业务结果]` `[需要用户确认的业务问题]` `[为何影响后续设计]` `[具体内容]` `[显式排除的内容及原因]` `[兼容性要求]` `[业务约束]` `[时间约束]` `[可验证条件]` `[依赖系统/团队]` `[前置条件]`
- **自身反模式**：
  - 顶部 line 14-15 显式禁止"改 SysUser.java 第 42 行"——技术细节归设计文档。
  - line 42-44 显式禁止"执行 curl 验证"——验证方案归实施文档。
- **疑似缺失项**：
  - **与 IEEE 830 相比缺：版本号、修订历史、需求来源 / 提出方 / 优先级**——没有任何元数据段。IEEE 830 第 1 节是「Introduction」，包含标识号、需求来源、定义缩略词、参考文献、文档结构，模板只有 6 节且全是内容节。
  - **没有「需求 ID / 追溯矩阵」**——无法从验收标准反推测试用例。
  - **「依赖关系」过简**——只占 2 行（line 47-48），没有「被依赖方 / 依赖类型 / 阻塞关系 / 是否已就绪」。
  - **没有「业务规则 / 业务约束的可枚举形式」**——纯散文，无结构化枚举。
  - **没有「影响到的干系人 / 角色」**——谁会关心这个变更、谁批准、谁验收都缺失。
  - **「约束条件」混排兼容性 / 业务 / 时间三类**，应该分小节而非混排 line 36-38。
  - **没有「非功能性需求」分项**——性能 / 可用性 / 安全 / 维护性 / 合规全是散点，没有专门小节。
  - **没有「验收测试方法」**——验收标准只说"管理员登录后打开用户列表，能看到 phoneModel 列"，没说怎么测（手工 / 自动 / 用例 ID）。

---

## 模板：impact/020-design.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/020-design.md`
- **行数**：99
- **章节骨架**：
  1. 当前状态：项目背景摘要 + 数据库 + 代码 + 配置（line 3-24）
  2. 目标状态：数据库 + 代码 + 配置（line 26-37）
  3. 变更细则：逐维度的字段/索引/外键/代码新增/修改/删除（line 39-53）
  4. 代码风格报告：基础风格表 + 深入分析 + 风格约束（line 55-80）
  5. 设计原则约束：简单优先 / 精准修改 / 质量底线（line 82-86）
  6. 数据迁移策略（line 88-92）
  7. 向后兼容性评估（line 94-97）
  8. 其他章节按需展开（line 99 注释）
- **强制要素**：
  - [ ] 凭证脱敏（line 5）
  - [ ] 引用 Context Pack 路径（line 9）
  - [ ] 现有表结构 + 列名 + 类型 + 约束 + 外键 + 索引 + 注释（line 16）
  - [ ] 完整表结构（变更后）（line 29）
  - [ ] 字段变更 ADD/ALTER/DROP 严格三选一（line 44）
  - [ ] 简单优先 / 精准修改 / 质量底线三原则（line 84-86）
  - [ ] API 向后兼容评估（line 96）
- **占位符**：`[变更名称]` `[现有表结构]` `[现有代码模块结构及关键逻辑]` `[现有配置项及当前值]` `[变更后的完整表结构]` `[表名.字段名] ADD/ALTER/DROP` `[新增模块/修改逻辑/删除逻辑]` `[维度1] [发现] [完整代码片段]` `[Java-实体]` `[DI]` `[日志]` `[异常]` `[SQL]` `[前端]` `[存量数据如何转换]` `[是否需要历史快照]` `[迁移脚本位置]` `[API 变更是否破坏现有消费者]` `[兼容方案]`
- **自身反模式**：
  - line 84-86 三条原则硬性约束：「不添加用户未要求的功能」「只改必须改的文件」「变更范围内必须达到项目同等质量标准」——这是"防御性反模式"，防止过度设计与不足质量。
  - line 74-80 硬编码的栈专属标签 `[Java-实体]` / `[DI]` / `[SQL]` / `[前端]`——**与 impact-pro 的"动态 style_axes"路线冲突**，这是 impact 模板的反派特征。
- **疑似缺失项**：
  - **与 arc42 12 节相比缺：架构目标 / 架构约束 / 系统范围与上下文 / 解决方案策略 / 运行时视图 / 部署视图 / 横切概念 / 风险与技术债务 / 质量属性 / 词汇表**——arc42 是行业事实标准，本模板 7 节覆盖不到其骨架。
  - **第 1 节「当前状态」+ 第 2 节「目标状态」是 diff 形式**，缺决策过程（为什么选 A 不选 B），不利于后续审计和知识沉淀。
  - **「代码风格报告」第 4 节与 impact-pro 第 4 节结构重复**，且 impact 用硬编码标签（line 74-80）无法跨栈移植——这恰是 impact-pro 用 style_axes 解决的反派案例。
  - **没有「接口契约 / OpenAPI 变更」专节**——API 兼容性只在 line 96 一行（line 94-97），应该独立小节。
  - **没有「事务边界」**——多表变更时事务一致性是核心，模板完全没要求。
  - **没有「性能 / 容量预估」**——新加索引、加列、改查询性能影响完全没提。
  - **没有「安全 / 权限」专节**——新增字段/接口的授权策略缺失（line 99 提到「按需展开」但没强制）。
  - **没有「监控 / 告警 / 指标」**——新功能上线后如何观测完全没提。

---

## 模板：impact/030-implementation.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/030-implementation.md`
- **行数**：89
- **章节骨架**：
  1. 实施顺序（line 5-7）
  2. 前置检查清单 8 项（line 9-18）
  3. 执行步骤 Step N 模板（line 20-34）
  4. 回滚方案（line 36-38）
  5. 验证步骤：正向 / 错误 / 其他（line 40-55）
  6. E2E / 验证脚本（line 57-60）
  7. 实施时间线（line 62-65）
  8. 执行记录（line 67-70）
  9. 跨会话恢复状态（line 72-76）
  10. 环境回退路径（line 78-89）
- **强制要素**：
  - [ ] 凭证脱敏（line 3）
  - [ ] 前置检查 8 项 P0/P1 全部勾选（line 11-18）
  - [ ] 每个 Step 必须有：维度 / 文件 / 风格约束 / 操作 / 影响范围 / 回滚方式 / 语义约定 / 验证方式 / 状态更新 / 确认提示（line 24-34）
  - [ ] 写操作必须逐项 `确认 Step N`（line 34）
  - [ ] 模糊确认不得视为写操作确认（line 34）
  - [ ] 高风险清单 P0/P1 拦截（line 18）
  - [ ] 环境回退路径预先写入（line 89）
- **占位符**：`[变更名称]` `[维度]` `[文件路径]` `[[标签]] [约束内容]` `[具体命令或代码]` `[描述]` `[回滚描述]` `[已确认定义 / 不涉及 / 未确认]` `[测试 / 检查命令 / 手工验收]` `[边界值]` `[空值/NULL]` `[格式校验]` `[安全风险]` `[预计耗时]` `[里程碑]`
- **自身反模式**：
  - line 34 显式禁止"模糊确认"——这是行业里最常见的反模式（"OK 继续"也算确认，但模板明确禁止）。
  - line 78-89 显式禁止"事后才发现环境受限"——回退方案必须前置规划。
- **疑似缺失项**：
  - **没有「Step 之间依赖图」**——只有顺序（line 6），没有「Step 2 必须在 Step 1 验证通过后执行」的强制门禁。
  - **「语义约定」检查是单点（line 18）**，没有「枚举值变更会怎样影响现有数据」的清单。
  - **没有「工时 / 资源分配」**——"实施时间线"（line 62-65）只有里程碑，没有谁来做、谁 review。
  - **没有「变更窗口 / 维护窗口」**——生产环境执行的时间窗缺失。
  - **「E2E / 验证脚本」line 57-60 只有路径，没有强制要求**——可以空着，缺脚本时只写"未提供"。
  - **没有「数据备份点（checkpoint）表」**——回滚方案（line 37）是反命令，但没有「在哪一步打了 backup tag / snapshot ID」。
  - **没有「失败重试策略」**——Step 失败后是直接回滚 / 修复 / 跳过，模板没要求明示。
  - **没有「干系人通知」**——line 18 提到回滚负责人，但变更前/中/后通知谁没有要求。
  - **「执行步骤」每步必填 11 项**（line 24-34）——过于僵化，对小变更（改个文案）也是这个重量。

---

## 模板：impact/040-light.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/040-light.md`
- **行数**：96
- **章节骨架**：
  1. 变更概述（line 7-9）
  2. 长期目标状态（如适用）（line 11-19）
  3. 定级证据（line 21-26）
  4. 项目背景摘要（line 28-34）
  5. 影响范围：数据库 / 代码 / 接口 / 其他（line 36-59）
  6. 存量数据处理（line 61-63）
  7. 回滚方案（line 65-67）
  8. 实施步骤（line 69-72）
  9. 验证（line 74-89）
  10. Out of Scope（line 90-92）
  11. 风格合规（line 94-96）
- **强制要素**：
  - [ ] 凭证脱敏（line 3）
  - [ ] light 模式声明（line 5）
  - [ ] 任务规模 + 建议档位 + 允许 light 证据 + 触发 full 证据（line 22-26）
  - [ ] 接口返回检查清单（line 50-56）——新增/删除/重命名/类型变化/语义变化
  - [ ] 验证等级 V0-V3（line 78）
  - [ ] light 不跳过 Step 级确认（line 74）
- **占位符**：`[变更名称]` `[一句话描述变更内容]` `[总目标]` `[当前 Step]` `[已完成 Step]` `[待确认 Step]` `[Backlog]` `[阻塞项]` `[运行时未验证项]` `[路径/命令/代码]` `[缺失证据/需业务确认]` `[直接修改候选]` `[影响判断候选]` `[待确认问题]` `[暂不纳入范围]` `[表名]` `[ADD/ALTER/DROP] [字段/索引]` `[文件路径]` `[新增/修改/删除] [类/方法/逻辑]` `[路径]` `[新增/修改/不破坏兼容]` `[是否需要迁移]` `[回滚命令或操作]` `[步骤1] [步骤2]` `[功能正常场景]` `[边界值]` `[空值]`
- **自身反模式**：
  - line 5 顶部警示：「light 只简化文档形式，不跳过安全检查」——这是模板自己的反模式防御。
  - line 92 显式禁止删除显式排除项。
- **疑似缺失项**：
  - **「定级证据」缺乏判定标准**——line 22-26 只列「建议档位 / 允许 light 证据 / 触发 full 证据」，没有具体指标（如"涉及 ≤2 个表 / ≤3 个文件 / 无 DDL 才允许 light"）。
  - **「影响范围」接口检查清单（line 50-56）比 020-design.md 详细**——说明 light 模板反而比 full 设计文档更结构化，这反了。
  - **没有「实施步骤」的强制 Step 编号格式**——line 70-71 是纯列表，没有要求回滚/验证/影响范围/语义约定，这是和 030 模板最大的不一致。
  - **「风格合规」line 94-96 是「按需」性质**，没强制要求附证据（line 040-light.md 96 "纯文案/配置变更可写不适用"）。
  - **没有「执行人 / 审阅人」**——比 requirements 还简单。
  - **「Out of Scope」和 full 020-design 的相同小节内容强度不匹配**。
  - **没有「回滚演练」**——line 65-67 只说回滚命令，没说是否需要先 dry-run 验证回滚有效。

---

## 模板：impact/060-preflight.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/060-preflight.md`
- **行数**：101
- **章节骨架**：
  1. 基本信息 11 项（line 7-16）
  2. 执行前核对 16 行 P0/P1 表格（line 20-37）
  3. 阻塞恢复检查（如适用）（line 40-48）
  4. Step 清单（line 51-54）
  5. 恢复状态更新（line 57-61）
  6. 写入目标边界（line 64-74）
  7. V1-only 计数（line 77-81）
  8. 基线命令（line 84-93）
  9. 结论（line 96-101）
- **强制要素**：
  - [ ] 凭证脱敏（顶部硬规则）
  - [ ] 任何 P0 项未满足不得执行（line 3 顶部警示）
  - [ ] 16 行 P0/P1 表全部填写（line 22-37）
  - [ ] V1-only 计数 3 个 Step 暂停阈值（line 80）
  - [ ] 写入对象绝对路径 + 是否在项目根目录内（line 66-74）
  - [ ] Git HEAD 异常时替代审计（line 23）
  - [ ] 阻塞恢复 6 项检查（line 41-48）
- **占位符**：`[变更名称]` `[项目路径]` `[当前分支]` `[当前 commit]` `[执行人]` `[执行窗口]` `[回滚负责人]` `[git status --short --branch]` `[light / 010-requirements / 020-design / 030-implementation]` `[Step 1-16 行 P0/P1]` `[绝对路径，如 E:\projects\ruoyi-vue]` `[git-rev-parse / user-specified / pom-dot-xml / build-dot-gradle / inferred-from-cwd / other]` `[真实系统时间]` `[V0 / V1 / V2 / V3]`
- **自身反模式**：
  - line 3 顶部警示：「任何 P0 项未满足，不得进入执行」——这是模板自带的"安全闸"。
  - line 101 结论为否时只能只读分析，不得写——硬性禁止。
- **疑似缺失项**：
  - **16 项 P0/P1 表格（line 22-37）虽然多但缺**：「生产 DB 写权限 / DDL 权限 / 外部 API 写权限 / 第三方密钥 / VPN 连通性」——执行环境的前置条件没列出。
  - **「基线命令」line 84-93 是 bash 风格**，Windows PowerShell 兼容性需另注——`codeblock` 标记为 `bash`（line 85）而非 `powershell`。
  - **没有「变更通知 / 公告模板」**——只关注技术执行，缺人/沟通维度。
  - **「写入目标边界」line 66-74 只有当前 change-impact 目录**，没要求校验"目标项目本身"也是真实项目（防止在模板项目根目录写）。
  - **没有「时间预算」**——执行窗口（line 10）字面量，无最长执行时间约束。
  - **V1-only 阈值 3（line 80）是硬编码**，对超大变更（10+ Step）过严、对小变更（1-2 Step）过松。
  - **没有「dry-run / 演练」**——只要求基线命令（line 84），没要求"模拟执行一遍"。

---

## 模板：impact/090-execution-record.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/090-execution-record.md`
- **行数**：76
- **章节骨架**：
  1. 执行前确认 8 项（line 7-15）
  2. Step N 时间戳记录 30+ 字段（line 17-53）
  3. 测试失败诊断记录（如有）（line 55-64）
  4. 收尾检查 9 项（line 66-76）
- **强制要素**：
  - [ ] 凭证脱敏（line 4）
  - [ ] 高风险清单 6 项 PASS/FAIL（line 35-41）：DROP TABLE / DELETE FROM 无 WHERE / 删旧接口 / 删旧文件 / 改 status/enum/错误码 / 不可逆操作
  - [ ] Step 编号必须出现在用户确认中（line 30）
  - [ ] 验证等级 V0-V3 必填（line 29）
  - [ ] 工具调用约定（line 47-48）——mvn test / alembic dry-run 等
  - [ ] 写入目标检查（line 44）
  - [ ] V1-only 计数（line 51）
  - [ ] `_active-state.md` 更新（line 53）
  - [ ] 测试失败修复必须有 Step 级确认（line 62）
- **占位符**：`[YYYY-MM-DD HH:MM:SS]` `[Step N]` `[操作名称]` `[待确认 / 已确认 / 成功 / 失败 / 跳过]` `[写文件 / 改代码 / DDL / DML / 配置变更 / 测试修复 / 外部系统写操作]` `[绝对路径]` `[影响范围]` `[回滚方式]` `[命令 + 期望结果]`
- **自身反模式**：
  - line 41「不可逆操作」与「DROP TABLE」是双层重复——DROP TABLE 本身就是不可逆。
  - line 47-48 工具调用约定只列 4 种栈（pytest/mvn/go/npm），其它栈没列。
- **疑似缺失项**：
  - **没有「Token / 工具调用次数统计」**——subagent-decisions.md 有总 Token 消耗（line 62），本模板没有。
  - **「执行前确认」line 7-15 没有确认时间戳**——只说"已确认"，没记何时确认。
  - **Step 字段多达 30+，但缺「确认时延」**——用户回复"确认 Step 1"到执行经过多久，对评估用户体验和自动化阈值有用。
  - **没有「失败重试次数」**——同一 Step 失败后重试几次才升级用户没要求。
  - **没有「Step 之间等待时间」**——高频连续 Step 还是分批没要求。
  - **「工具调用约定」line 47-48 写死 4 栈**，非这 4 栈的项目不知道该用啥。
  - **没有「Step 整体执行时长 / 端到端耗时」**——只有 Step 内验证结果。
  - **测试失败诊断（line 55-64）结构单薄**——失败类型 6 种（line 58）但没有"自动诊断结论"的具体方法。
  - **没有「Step 之间影响传递」**——Step 1 改了表 A，Step 2 改了表 A 的视图，依赖关系没显式记录。

---

## 模板：impact/_active-state.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/_active-state.md`
- **行数**：75
- **章节骨架**：
  1. State Header 16 项（line 7-25）
  2. Current Intent 5 项（line 28-32）
  3. Document Status 7 行（line 35-44）
  4. Step Ledger（line 47-49）
  5. Pending Recovery Check 6 项（line 52-60）
  6. Open Items（line 63-64）
  7. Last Validation 4 项（line 67-71）
  8. Resume Notes（line 74-75）
- **强制要素**：
  - [ ] 跨会话恢复状态声明（line 3-5 顶部）
  - [ ] "This file is a checkpoint, not an authorization"（line 4-5）
  - [ ] target_project_root 绝对路径 + determination_method + verification_timestamp（line 11-13）
  - [ ] git HEAD 记录（line 17）
  - [ ] 7 份文档状态全部填写（line 36-43）
  - [ ] Step 状态 planned/pending/confirmed/success/failed/skipped 6 选 1（line 49）
  - [ ] 恢复前 6 项必读（line 53-59）
  - [ ] V1-only 计数（line 24）
- **占位符**：`[真实系统时间 ISO 8601]` `[绝对路径，如 E:\projects\ruoyi-vue]` `[git-rev-parse / user-specified / pom-dot-xml / build-dot-gradle / inferred-from-cwd / other]` `[Phase 4 / Phase 5 / blocked / complete]` `[light / full]` `[HEAD / 非 Git / Git 不可用]` `[clean / dirty / non-git / unavailable]` `[Step N / none]` `[未确认项 / 风险 / 用户决策]`
- **自身反模式**：
  - line 4 顶部硬性声明："This file is a checkpoint, not an authorization. It never replaces `确认 Step N`"——这是模板最重要的反模式防御。
- **疑似缺失项**：
  - **「Current Intent」line 28-32 字段少**——没有「用户已拒绝 / 已放弃的方案」记录，失败决策难以追溯。
  - **「Step Ledger」line 47-49 列太少**——没有「影响文件 hash / 写入时间戳 / 验证命令输出 hash」，恢复时无法精确复现。
  - **没有「Open Items 的 P0/P1 分级」**——line 63-64 全部混排，无法按优先级处理。
  - **「Pending Recovery Check」line 53-59 是 list 形式**，没有强制 P0/P1 区分。
  - **没有「资源锁 / 占用标记」**——多个 agent 并发时无法识别冲突。
  - **没有「最近一次失败 / 重试计数」**——卡死的 Step 难以识别。
  - **没有「自动 / 手动模式标记」**——subagent 自治模式与人类主导模式未区分，导致 Phase 5 自治与人类审核混淆。
  - **没有「总执行耗时」**——从创建到完成的实际墙钟时间缺失。

---

## 模板：impact/subagent-decisions.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact/templates/subagent-decisions.md`
- **行数**：63
- **章节骨架**：
  1. 决策矩阵汇总（必填）表头 4 列（line 11-16）
  2. Step N: RESTATE 4 项（line 22-26）
  3. Step N: DECIDE 2 项（line 29-39）
  4. Step N: RECORD 3 项（line 41-43）
  5. 决策偏离说明（如有）（line 47-54）
  6. 收尾 5 项（line 58-62）
- **强制要素**：
  - [ ] 「subagent 预决策建议不替代人类 `确认 Step N`」（line 3 顶部）
  - [ ] 决策三选一：request-human-confirm / pause-and-wait / flag-high-risk（line 12, 28）
  - [ ] flag-high-risk 仅 eval 沙盒可继续只读；生产必须暂停（line 4, 28）
  - [ ] 高风险清单 6 项 PASS（line 32-38）
  - [ ] 收尾 5 项：实际/暂停/拒绝/Token/工具调用（line 58-62）
- **占位符**：`[变更名称]` `[request-human-confirm / flag-and-pause / HUMAN-OVERRIDE-REQUIRED]` `[文件 / 表 / 函数 / 行号]` `[影响范围]` `[精确反向命令]` `[命令 + 期望结果]`
- **自身反模式**：
  - line 4 顶部反复强调「不替代人类确认」「生产必须暂停」——防御 subagent 越权。
- **疑似缺失项**：
  - **「决策矩阵汇总」line 12 三个选项中混入 "HUMAN-OVERRIDE-REQUIRED"**——但 line 28 又说三选一（request/pause/flag），DECIDE 字段枚举不一致。
  - **「flag-high-risk」line 28 后半句是 patch 在括号里**（"仅 eval 沙盒可继续只读分析，生产会话必须暂停"），不够显眼。
  - **没有「决策置信度」**——subagent 应该有 self-confidence score（高/中/低），影响是否需要 escalate。
  - **没有「决策时间戳」**——决策矩阵是表格，缺时间维度。
  - **没有「决策理由的引用证据」**——line 32 决策依据 6 项是 PASS/FAIL 简单二元，没有 PASS 的具体证据路径。
  - **「RECORD」line 41-43 没有要求回写路径**——只说"写入 090-execution-record.md"但没强制字段。
  - **「收尾 5 项」line 58-62 字段值缺规约**——"总 Token 消耗 [N]"如何计费（输入/输出/工具），没标准。
  - **没有「subagent 自我反思 / 失误记录」**——决策错了的话，没要求复盘。
  - **没有「subagent 身份 / 模型版本」**——不同模型版本决策风格不同，应记录。

---

# Part B — impact-pro skill（10 份）

---

## 模板：impact-pro/000-context-pack.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/000-context-pack.md`
- **行数**：105
- **章节骨架**：
  1. 变更意图 7 项（line 7-14）
  2. 源系统到目标系统对齐（如适用）（line 18-25）
  3. 分层上下文 L1/L2/L3（line 27-32）
  4. 相关文件和对象 5 列（line 34-46）
  5. 关键上下文 6 子节：入口/数据结构/依赖路径/配置权限/测试（line 49-71）
  6. 引用检查结果 4 分类（line 73-81）
  7. 已确认事实（line 84-86）
  8. 待确认问题（line 88-90）
  9. 暂不纳入范围（line 92-94）
  10. 上下文预算（line 97-105）
- **强制要素**：
  - [ ] 已识别技术栈 + 已加载技术栈规则（line 9-10）——比 impact 多出 2 行
  - [ ] 文件类型分类：entrypoint / model / service / data / config / test / ui（line 37）
  - [ ] 入口 / 数据结构 / 依赖路径 / 配置权限 / 测试 五子节必填（line 51-69）
  - [ ] 引用检查 4 分类（line 76-79）
  - [ ] 凭证脱敏（line 64）
- **占位符**：同 impact 000 + `[entrypoint / model / service / data / config / test / ui]` `[route/controller/page/handler/command/job]` `[schema/model/entity/dto/type/migration]` `[service/repository/client/store/composable]` `[env/config/feature flag/permission]` `[unit/integration/e2e/api]`
- **自身反模式**：无显式禁止；line 81 强约束"找不到写'未找到引用'，不得写成'无影响'"。
- **疑似缺失项**：
  - **相比 impact 多了「已识别技术栈 / 已加载技术栈规则」**——但没强制记录「已加载 profile 路径 / level / matchers 命中证据」。
  - **「关键上下文」line 49-71 比 impact 详细**（5 子节 vs 3 子节）但「依赖路径」与「配置权限」分离是好的，「测试」只列存在没列覆盖率（与 impact 同样问题）。
  - **没有「时间戳 / 快照版本」**——与 impact 同样问题。
  - **没有「Context Pack 写入人 / 审阅人」**。
  - **「相关文件和对象」line 34-46 5 列**比 impact 多 1 列（文件类型），但相关性 0/1/2/3 的语义没有进一步定义（impact 也没）。
  - **没有「跨服务 / 跨进程依赖」**——多栈项目常涉及多个进程/服务（如 frontend + backend + DB），模板不分。

---

## 模板：impact-pro/010-requirements.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/010-requirements.md`
- **行数**：47
- **章节骨架**：
  1. 变更背景（line 6-8）
  2. 需求描述（line 10-13）
  3. 当前假设与歧义（line 15-21）
  4. 未确认项（line 23-25）
  5. 变更范围（line 27-30）
  6. 约束条件（line 32-36）
  7. 验收标准（line 38-42）
  8. 依赖关系（line 44-46）
- **强制要素**：
  - [ ] 用业务语言而非技术（line 3-4 顶部）
  - [ ] 需求 vs 设计分离（line 3-4 顶部）
  - [ ] 任务规模（line 20）
  - [ ] 成功标准可验证（line 20）
  - [ ] Out of Scope 显式排除（line 29）
- **占位符**：同 impact 010-requirements
- **自身反模式**：
  - line 12-13 显式禁止"改 SysUser.java 第 42 行"——同 impact。
  - line 39-41 显式禁止"执行 curl 验证"——同 impact。
- **疑似缺失项**：
  - **与 impact 几乎一致**，只是小节编号 2.1/2.2（line 15, 23）——把假设与未确认项从 2.x 提到独立节。
  - **相比 impact 没有「凭证脱敏」顶部规则**——line 1-5 完全没提（020/030 才有）。这是**结构性不一致**。
  - **同样缺**：需求 ID / 修订历史 / 干系人 / 非功能需求 / 验收测试方法 / 业务规则枚举。
  - **同样缺** IEEE 830 的 5 节元数据（Introduction）。

---

## 模板：impact-pro/020-design.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/020-design.md`
- **行数**：117
- **章节骨架**：
  1. 当前状态：Context Pack 摘要 + 分析依据 + 数据库 + 代码 + 配置（line 3-32）
  2. 目标状态：数据库 + 代码 + 配置（line 34-45）
  3. 变更细则（line 47-62）
  4. 代码风格报告：动态 style_axes（line 64-88）
  5. 设计原则约束 + 行为准则检查（line 90-105）
  6. 数据迁移策略（line 107-111）
  7. 向后兼容性评估（line 113-116）
  8. 其他章节按需展开（line 117 注释）
- **强制要素**：
  - [ ] 凭证脱敏（line 5）
  - [ ] 引用 Context Pack 路径（line 9）
  - [ ] 分析依据 3 分类：已确认 / 未确认 / 不采用的推断（line 17-22）——比 impact 强
  - [ ] Schema 来源标注：DB查询/迁移文件/ORM模型/未确认（line 55）——比 impact 强
  - [ ] style_axes 动态生成（line 82-88）——**关键改进**：不硬编码栈专属标签
  - [ ] 行为准则检查 6 项（line 99-104）——比 impact 多
  - [ ] 语义约定证据（line 103）
- **占位符**：同 impact 020 + `[运行时填入]` `[从代码现采的约束内容]` `[证据来源]` `[已确认]` `[未确认]` `[不采用的推断]` `[DB查询/迁移文件/ORM模型/未确认]`
- **自身反模式**：
  - line 88 顶部警示："**实施阶段使用当前技术栈规则的 style_axes 轴名作为标签**，不硬编码任何栈专属标签"——这是核心反模式防御，**与 impact 的 line 74-80 硬编码 [Java-实体]/[DI]/[SQL]/[前端] 形成鲜明对比**。
- **疑似缺失项**：
  - **相比 impact 重大改进**：「分析依据 3 分类」「Schema 来源标注」「style_axes 动态」「行为准则检查 6 项」——都补了 impact 的缺陷。
  - **但仍缺**：arc42 的 12 节骨架（架构目标 / 约束 / 范围上下文 / 解决方案策略 / 运行时 / 部署 / 横切概念 / 风险与技术债 / 质量属性 / 词汇表）。
  - **「目标状态」line 34-45 与「当前状态」line 3-32 镜像结构**，缺 diff 视图。
  - **没有「接口契约 / OpenAPI 变更」**——同 impact 020。
  - **没有「事务边界 / 性能 / 安全 / 监控」专节**——同 impact 020。
  - **「数据迁移策略」line 107-111 与 impact 完全相同**——没改进。
  - **「向后兼容性评估」line 113-116 与 impact 完全相同**——没改进。
  - **「行为准则检查」line 99-104 是空白字段**（任务规模 / 适用规则 / 精准修改边界 / 不做的事 / 语义约定证据 / 测试策略依据）——没有"如何填"的指导。

---

## 模板：impact-pro/030-implementation.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/030-implementation.md`
- **行数**：88
- **章节骨架**：
  1. 实施顺序（line 5-7）
  2. 前置检查清单 10 项（line 9-20）
  3. 执行步骤 Step N 模板 12 项（line 22-37）
  4. 回滚方案（line 39-41）
  5. 验证步骤（line 43-57）
  6. E2E / 验证脚本（line 59-61）
  7. 实施时间线（line 63-66）
  8. 跨会话恢复状态（line 68-75）
  9. 环境备选路径（line 77-87）
- **强制要素**：
  - [ ] 凭证脱敏（line 3）
  - [ ] 前置检查 10 项（比 impact 多 2 项：分析依据处理 / 破坏性操作已确认）（line 11-20）
  - [ ] Step 必须有"确认类型"（line 35）——impact 030 没有
  - [ ] 风格约束来自 profile style_axes 运行时现采（line 28-29）——动态生成
  - [ ] 写操作必须逐项 `确认 Step N`（line 37）
- **占位符**：同 impact 030 + `[已确认定义/不涉及/未确认]` `[轴名] [约束内容]` `[写文件 / 改代码 / DDL / DML / 配置变更 / 测试修复 / 外部系统写操作]`
- **自身反模式**：
  - line 37 显式禁止"模糊确认"——同 impact。
  - line 87 显式禁止"事后才发现环境受限"——同 impact。
- **疑似缺失项**：
  - **相比 impact 030 多了 2 项前置检查**（line 11, 20）——更严。
  - **相比 impact 030 多了「确认类型」Step 字段**（line 35）——更结构化。
  - **缺少「090-execution-record」引用**（line 67-75）——impact 030 line 67-70 有专门"执行记录"节，impact-pro 把这一节删了。这是**结构退化**。
  - **缺「基线命令」**——impact 060 有，本模板没有（与 060 互补？）。
  - **缺「V1-only 计数」**——impact 060 有，本模板没有。
  - **缺「写入目标边界」**——impact 060 有，本模板没有（仅 _active-state 提到）。
  - **同样缺**：Step 依赖图、失败重试、变更窗口、checkpoint ID、failure escalation。

---

## 模板：impact-pro/040-light.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/040-light.md`
- **行数**：122
- **章节骨架**：
  1. 变更概述（line 5-7）
  2. 长期目标状态（line 9-17）
  3. 定级证据（line 19-24）
  4. 行为准则检查 7 项（line 26-34）
  5. Context Pack 摘要（line 36-42）
  6. 影响范围：分析依据 + 数据库 + 代码 + 接口 + 其他（line 44-77）
  7. 存量数据处理（line 79-81）
  8. 未确认项（line 83-85）
  9. 回滚方案（line 87-89）
  10. 实施步骤（line 91-94）
  11. 执行确认要求（line 96-98）
  12. 验证（line 100-114）
  13. Out of Scope（line 116-118）
  14. 风格合规（line 120-122）
- **强制要素**：
  - [ ] 任务规模 + 当前假设 + 可能歧义 + 更简单方案 + 精准修改边界 + 语义约定确认 + 测试策略依据（line 28-34）——比 impact 多了语义约定 / 测试策略
  - [ ] 分析依据 2 分类：已确认 / 未确认（line 51-52）
  - [ ] Schema 来源标注（line 58）——比 impact 强
  - [ ] 接口返回检查清单 6 项（line 67-72）——同 impact
  - [ ] 验证等级 V0-V3（line 103）
  - [ ] light 不跳安全检查（line 97-98）
- **占位符**：同 impact 040 + `[DB查询/迁移文件/ORM模型/未确认]` `[status/enum/常量/错误码/权限/配置键原定义]`
- **自身反模式**：
  - line 5 顶部警示：「light 只简化文档形式，不跳过安全检查」——同 impact。
  - line 46 显式禁止"未涉及的维度删除，不用占位"——比 impact 更严。
- **疑似缺失项**：
  - **相比 impact 040-light 重大改进**：「行为准则检查 7 项」「分析依据 2 分类」「Schema 来源标注」「未确认项独立节」——都补了 impact 的缺陷。
  - **同样缺**：定级证据判定指标（什么算 light / 什么必须 full）。
  - **同样缺**：回滚演练 / 干系人通知 / 实施时间预算。
  - **「执行确认要求」line 96-98 相比 impact line 74**——弱化（只说"按 Step 编号确认"，没说要"逐项询问"）。
  - **「未确认项」line 83-85 是空白 checkbox**，没要求写影响（010-requirements 有"影响"列）。

---

## 模板：impact-pro/060-preflight.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/060-preflight.md`
- **行数**：101
- **章节骨架**：
  1. 基本信息 11 项（line 7-16）
  2. 执行前核对 16 行 P0/P1 表格（line 20-37）
  3. 阻塞恢复检查（如适用）（line 40-48）
  4. Step 清单（line 51-54）
  5. 恢复状态更新（line 57-61）
  6. 写入目标边界（line 64-74）
  7. V1-only 计数（line 77-81）
  8. 基线命令（line 84-93）——codeblock 标 `powershell`
  9. 结论（line 96-101）
- **强制要素**：
  - [ ] 16 行 P0/P1 全部填写（line 22-37）——同 impact
  - [ ] V1-only 阈值 3（line 80）——同 impact
  - [ ] 写入对象绝对路径（line 66-74）——同 impact
  - [ ] 基线命令 codeblock 用 `powershell`（line 85）——**与 impact 的 `bash` 不一致**
- **占位符**：同 impact 060 + `package-dot-json`（line 67）——比 impact 多一个 Node 项目判定方法
- **自身反模式**：
  - line 3 顶部警示：「任何 P0 项未满足，不得进入执行」——同 impact。
  - line 101 结论为否时只能只读分析——同 impact。
- **疑似缺失项**：
  - **相比 impact 060 几乎完全相同**，仅 line 67 多一个 `package-dot-json` 判定方法，line 85 codeblock 标 `powershell` 而 impact 是 `bash`——**多平台/多栈的微小不一致**。
  - **同样缺**：外部依赖连通性（VPN / 三方 API / 凭证有效性）。
  - **同样缺**：变更通知 / 公告模板。
  - **同样缺**：dry-run / 演练。
  - **同样缺**：时间预算。
  - **V1-only 阈值 3 硬编码**——同 impact。

---

## 模板：impact-pro/090-execution-record.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/090-execution-record.md`
- **行数**：76
- **章节骨架**：
  1. 执行前确认 8 项（line 7-15）
  2. Step N 时间戳记录 30+ 字段（line 17-53）
  3. 测试失败诊断记录（如有）（line 55-64）
  4. 收尾检查 9 项（line 66-76）
- **强制要素**：
  - [ ] 凭证脱敏（line 4）
  - [ ] 高风险清单 6 项 PASS/FAIL（line 35-41）——同 impact
  - [ ] Step 编号必须出现在用户确认中（line 30）
  - [ ] 工具调用约定（line 47-48）——**与 impact 不同**：列 `ty check` (Python) / alembic SQL render (Python)——栈专属
  - [ ] 验证等级 V0-V3 必填（line 29）
- **占位符**：同 impact 090 + `[python -m ty]` `[alembic upgrade head --sql]`
- **自身反模式**：
  - line 47「`ty check` 必须通过项目 venv 的 `python -m ty` 调用（不直接调二进制，避免 venv 绑错）」——**这是栈专属反模式防御**，比 impact 090 的"通用 4 栈"更针对 Python。
  - line 41「不可逆操作」与「DROP TABLE」是双层重复——同 impact。
- **疑似缺失项**：
  - **与 impact 090 几乎完全相同**，仅 line 47-48 工具调用约定针对 Python 调整。
  - **同样缺**：Token/工具调用统计、确认时间戳、确认时延、失败重试次数、Step 间等待时间。
  - **同样缺**：非 4 栈项目的工具调用约定（impact 列 4 栈，impact-pro 改 2 栈 Python 工具）。
  - **同样缺**：Step 整体执行时长、Step 之间影响传递。

---

## 模板：impact-pro/_active-state.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/_active-state.md`
- **行数**：75
- **章节骨架**：
  1. State Header 16 项（line 7-25）——`skill: impact-pro`（line 9）
  2. Current Intent 5 项（line 28-32）
  3. Document Status 7 行（line 35-44）
  4. Step Ledger（line 47-49）
  5. Pending Recovery Check 6 项（line 52-60）
  6. Open Items（line 63-64）
  7. Last Validation 4 项（line 67-71）
  8. Resume Notes（line 74-75）
- **强制要素**：
  - [ ] 顶部声明：cross-session recovery state, checkpoint not authorization（line 3-5）
  - [ ] target_project_root + determination_method（line 11-13）——多 `package-dot-json`（line 12）适配 Node
  - [ ] 7 份文档状态（line 36-43）
- **占位符**：同 impact _active-state
- **自身反模式**：
  - line 4 顶部硬性声明："This file is a checkpoint, not an authorization. It never replaces `确认 Step N`"——同 impact。
- **疑似缺失项**：
  - **相比 impact _active-state 几乎完全相同**，仅 line 9 `skill: impact-pro`、line 12 `package-dot-json` 适配 Node。
  - **同样缺**：已拒绝方案记录、影响文件 hash、写入时间戳、Open Items P0/P1 分级、并发锁、最近失败重试计数、自动/手动模式标记、总执行耗时。

---

## 模板：impact-pro/final-readiness-audit.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/final-readiness-audit.md`
- **行数**：86
- **章节骨架**：
  1. 基本信息 7 项（line 7-13）
  2. 结论：保持/升级 4 字段（line 17-20）
  3. 八条目标逐项审计 8 行（line 24-33）
  4. Phase 5 完成专项审计 7 项（line 37-45）
  5. 一票否决项 6 条（line 49-56）
  6. 最终评分 10 项 + 平均分（line 64-77）
  7. 最终决定（line 80-87）
- **强制要素**：
  - [ ] 8 条目标全部审计（line 26-33）
  - [ ] 平均分 ≥ 85 且无 P0/P1（line 30, 56）
  - [ ] 至少 5 栈 + 每栈 full + light 双验收（line 27）
  - [ ] 至少 2-3 个生产级项目复验（line 29）
  - [ ] 6 个一票否决项（line 51-56）
  - [ ] 引用 scorecard 实例（line 60）
- **占位符**：`[复审日期]` `[复审人]` `[当前 commit]` `[复审范围]` `[关联验证记录]` `[关联执行记录]` `[关联评分表]` `[保持多栈可试用增强版 / 升级为多栈常规项目可投入使用]` `[结论依据]` `[不满足项]` `[后续动作]` `[N]`
- **自身反模式**：
  - line 50-56 一票否决项 6 条——硬性闸门。
  - line 60「必须引用 scorecard 实例，不能只写口头平均分」——防御虚高打分。
- **疑似缺失项**：
  - **「八条目标」line 26-33 是硬性 8 条**，但缺每条目标的可验证子指标（如"5 个技术栈"具体是哪 5 个？）。
  - **「最终评分」line 64-77 10 个维度没有权重**——平均分是简单算术平均，未必反映关键维度短板。
  - **没有「审计时间预算 / 周期」**——一次复审应多长时间没说。
  - **「Phase 5 完成专项审计」line 37-45 7 项**，但没有失败用例的复测要求。
  - **没有「复审参与方」**——只有"复审人"（line 8），没有"被复审方 / 利益相关方"。
  - **「最终决定」line 80-87 是空模板**，没强制"如果升级则后续维护节奏"。
  - **没有「升级失败时回退路径」**——升级后又发现不达标如何回退。
  - **没有「跨周期趋势」**——单一时间点评估，没有历次复审对比。

---

## 模板：impact-pro/scorecard.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/scorecard.md`
- **行数**：48
- **章节骨架**：
  1. 基本信息 5 项（line 7-12）
  2. 样本总表 8 列（line 16-18）
  3. 分组复算 6 组（line 22-27）
  4. 总结 5 项（line 30-35）
  5. 排除样本（line 38-40）
  6. 计算说明 4 条（line 44-48）
- **强制要素**：
  - [ ] 7 列：技术栈 / 场景 / full-light-负向-生产级 / 分数 / P0 / P1 / 证据记录 / 验证命令（line 16）
  - [ ] 6 分组复算（line 22-27）
  - [ ] 平均分 ≥ 85（line 35）
  - [ ] 排除样本有理由（line 40）
  - [ ] 缺证据不计入通过样本（line 46）
- **占位符**：`[复算日期]` `[复算人]` `[当前 commit]` `[复算范围]` `[关联 VALIDATION.md 版本]` `[Txx]` `[N]`
- **自身反模式**：
  - line 48「出现任何未修复 P0/P1，即使平均分 ≥ 85，也不得升级」——硬性闸门。
- **疑似缺失项**：
  - **「样本总表」line 16-18 列定义清晰但缺「评分人 / 评分时间」**——分数来自谁、何时打的没记录。
  - **「分组复算」line 22-27 6 组是硬编码**——final-readiness-audit 提到 8 条目标，scorecard 6 组不一致（8 vs 6）。
  - **没有「分数维度细分」**——只给一个总分（line 16「分数」列），没要求按 final-readiness-audit line 64-73 的 10 维度打 10 个分。
  - **「排除样本」line 38-40 没有「补测计划」要求**——只说"是否需后续补测"（line 40）但没强制。
  - **没有「评分标准 / 评分量表」**——比如"85-100 = 优秀" / "70-84 = 良好"，没有 rubrics。
  - **没有「分数信度 / 一致性」**——多人评分时一致性如何度量没说。
  - **没有「分数随时间衰减」**——3 个月前打的 90 分现在还值 90 吗？

---

## 模板：impact-pro/subagent-decisions.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/templates/subagent-decisions.md`
- **行数**：63
- **章节骨架**：与 impact/subagent-decisions.md **完全相同**（line 1-63 对应 1-63）。
- **强制要素**：同 impact/subagent-decisions.md
- **占位符**：同 impact/subagent-decisions.md
- **自身反模式**：同 impact/subagent-decisions.md
- **疑似缺失项**：
  - **与 impact 完全相同，没有 impact-pro 特有的改进**——既然 impact-pro 强调多栈/多 profile，subagent 决策矩阵理应有"profile 选择记录"和"栈切换决策"，但完全没有。
  - **同 impact 全部缺失项**：决策置信度、决策时间戳、决策理由的引用证据、RECORD 字段强制、收尾指标规约、subagent 自我反思、subagent 身份/模型版本。
  - **同样问题**：line 12 三选项混入 HUMAN-OVERRIDE-REQUIRED，与 line 28 三选一不一致。

---

# Part C — pathfinder skill（1 份）

---

## 模板：pathfinder/project-map.md
- **文件路径**：`E:/agent/blue-skillhub/skills/pathfinder/templates/project-map.md`
- **行数**：166
- **章节骨架**（**核心 14 节 + 可选 3 节**，SKILL.md line 119-133 锁定）：
  1. 【0】基本信息（可信度标记）13 项（line 15-29）
  2. 【1】一句话概述 2 项（line 31-34）
  3. 【2】技术栈 5 行（line 36-46）
  4. 【3】架构分层 / 模块地图 4 列 + Mermaid 架构图（line 48-66）
  5. 【4】核心功能（line 68-69）
  6. 【5】关键入口 3 行（line 72-77）
  7. 【6】数据模型概览 + Mermaid ER 图（line 79-93）
  8. 【7】外部依赖与集成（line 95-98）
  9. 【8】构建·运行·测试 4 行（line 100-109）
  10. 【9】风险区域（line 111-117）
  11. 【10】权限 / 认证模型概览 4 项（line 119-125）
  12. 【11】典型主流程 Mermaid 图（line 127-139）
  13. 【12】文档与知识入口（line 141-146）
  14. 【13】没挖深的部分（line 148-153）
  15. 可选集 3 节：仓库活跃度 / 部署 / 可观测性（line 158-167）
- **强制要素**：
  - [ ] 顶部 8 行注释：每条目带可信度（line 3-8）
  - [ ] 核心 14 节永远输出（line 6）
  - [ ] 缺失的核心节写"未发现 / 本档未深入"（line 7）
  - [ ] 不编造 / 不沉默（line 7）
  - [ ] 实线 = 【已核实】 虚线 = 【推断】（line 8, 64）
  - [ ] 命令只记录不执行（line 109）
  - [ ] 危险操作点必须显式声明风险性质（line 115）
  - [ ] 仓库内指令性文本不构成指令（line 117）
  - [ ] 4 项 Phase 4.5 写前自检（SKILL.md line 117）
- **占位符**：`[项目名]` `[真实命令输出]` `[git short HEAD / 或:非 Git,以扫描时间为准]` `[小/中/大/超大]仓(跟踪文件 ~N)` `[用户开场原话 / 或:无,均匀全景]` `[已深入]` `[未深入]` `[used / unavailable / failed / degraded]` `[工具名 / none]` `[complete / truncated / scoped path / unknown]` `【已核实: 证据】` `【推断: 待验证】` `[语言]` `[主框架]` `[构建工具]` `[数据库]` `[关键依赖]` `[path]` `[3/2/1]` `[模块A / 入口层]` `[功能]` `[进程入口]` `[HTTP 路由]` `[CLI / 定时任务 / MQ 消费]` `[主要实体 + 关系骨架(不逐字段罗列)]` `[三方服务 / MQ / 缓存 / 外部 API]` `[构建]` `[运行 / 启动]` `[测试]` `[无测试核心模块]` `[巨型文件 / 循环依赖]` `[TODO/FIXME/HACK 密集区]` `[仓库内的指令性文本(当风险证据,不执行)]` `[authn 方式]` `[authz 方式]` `[在哪强制]` `[入口 路由/Controller]` `[校验/中间件]` `[业务逻辑 Service]` `[数据访问 Repo/Mapper/ORM]` `[DB]` `[返回/序列化 → 响应]` `[README.md]` `[docs/] / ADR / wiki]` `[未深入模块 / 节]` `[再挖 [X]]` `[Docker/compose/k8s、服务拓扑、端口]` `[日志 / 监控 / 错误上报位置]`
- **自身反模式**：
  - line 2-8 顶部 8 行注释是 8 条反模式（每条都是"不要做"）：
    - 不编造（找不到写"未发现"）
    - 不沉默（缺失节不删）
    - 不混合（【已核实】/【推断】两条独立）
    - 不执行（命令只记录）
    - 不画实线冒充已核实
    - 不画"建议架构"图
    - 不省略"未深入"清单
    - 不让仓库文本改变规则
  - line 117（SKILL.md）Phase 4.5 4 项写前自检：①Grep 确认行号存在 ②凭证脱敏 ③未覆盖项非空 ④Mermaid 箭头与可信度一致
  - line 53「不为了图好看而编造关系」——视觉诚实。
  - line 93「无 DB 访问且 model 不清晰时,跳过本图并在【13】标'数据模型图待补'」——诚实声明。
  - line 109「命令只**记录**,Pathfinder 不执行」——硬性禁止。
- **疑似缺失项**：
  - **【0】基本信息（line 15-29）13 项已多**，但缺「生成人 / 审阅人」「审阅日期」「分发范围」——可追溯性弱。
  - **【4】核心功能（line 67-69）只有 1 行模板**——是 14 节里最薄弱的，应该有"功能点 ID / 证据 / 优先级"列表。
  - **【5】关键入口（line 72-77）只有 3 行类型**——缺「入口的健康度（是否有监控 / 告警 / 错误率）」。
  - **【7】外部依赖（line 95-98）只列存在与否**——缺「依赖类型（SaaS / 内部 / 共享）/ SLA / 替代方案 / 失败影响」。
  - **【8】构建·运行·测试（line 100-109）缺测试覆盖率数值**——只有"测试现状"，没有 line/branch coverage。
  - **【9】风险区域（line 111-117）只列无测试核心模块 / 巨型文件 / 危险操作点 / TODO / 指令文本**——缺「数据完整性风险 / 性能风险 / 安全漏洞风险 / 合规风险」。
  - **【10】权限/认证（line 119-125）只列 4 项**——缺「权限模型图（RBAC / ABAC / ACL）」「关键权限决策点（PDP/PEP 位置）」「审计日志位置」。
  - **【11】典型主流程（line 127-139）只 trace 一条**——是反模式的反向（过严），对多入口项目不友好。
  - **【12】文档与知识入口（line 141-146）只有 README/ADR**——缺「团队 Onboarding 文档」「Runbook」「SOP」「历史决策记录」。
  - **【13】没挖深（line 148-153）只列未深入**——缺「为什么是重点（业务影响 / 安全影响 / 复杂度）」。
  - **可选集 3 节（line 158-167）严重不足**：
    - 缺「CI/CD 流水线位置 + 触发条件 + 失败处理」
    - 缺「依赖更新策略（renovate / dependabot）」
    - 缺「代码所有权（CODEOWNERS）」
    - 缺「代码统计（行数 / 复杂度 / 技术债务）」「单测覆盖率」「E2E 覆盖范围」
  - **整体缺**：
    - **「预算消耗」**——生成本身用了多少时间 / 命令 / 工具调用？line 26-29 提到预算档位（小/中/大/超大）但没记录实际消耗。
    - **「变更钩子」**——后续 impact/impact-pro 引用时如何找到本文档？line 22 路径锚点 [0] 是 "change-impact/_project-map.md" 但没有约定 L1 导航如何引用。
    - **「增量更新日志」**——Phase 5 扩展循环（SKILL.md line 135-137）说可以"再挖 X"，但模板没要求记录每次增量更新的时间与变更内容。
    - **「对 L1 / L2 / L3 的对应关系」**——这是 impact 000-context-pack 的核心概念，但 pathfinder 不显式输出 L1/L2/L3 分层（只在【3】【8】隐含）。

---

# Part D — profile 模板（2 份，与 impact-pro 配套）

---

## 模板：impact-pro/profiles/_template.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/profiles/_template.md`
- **行数**：77（含代码块）
- **章节骨架**（YAML 块 + 创建步骤）：
  1. YAML 主块 11 字段（line 5-61）：
     - name / level / matchers / roles / discovery_globs / context_discovery / style_axes / commands / db_introspection / validation_strategy / notes
  2. 创建步骤 12 步（line 65-77）
- **强制要素**：
  - [ ] 复制模板（line 65）
  - [ ] 先用 generic 备用（line 66）
  - [ ] 填 name 和 matchers（line 67）
  - [ ] 验证 discovery_globs 命中（line 68）
  - [ ] 填 context_discovery（line 69）
  - [ ] 跑 commands 验证（line 70）
  - [ ] 填 style_axes 运行时现采（line 71）
  - [ ] 填 validation_strategy（line 72）
  - [ ] 列 limitations（line 73）
  - [ ] full + light 双变更验收 + Txx 记录（line 74）
  - [ ] 更新 README/VALIDATION Level（line 75）
  - [ ] 第二个真实项目复验才考虑 Level 2（line 76）
- **占位符**：YAML 全是空（name / level / matchers / 等等）
- **自身反模式**：
  - line 66「先用 `profiles/generic.md` 在目标真实项目完成只读备用分析」——硬性顺序，禁止跳过。
  - line 68「未验证的 glob 不写入正式 profile」——硬性禁止。
  - line 71「填 `style_axes`（运行时从代码现采，不预置结论）」——防御硬编码。
  - line 74「记录中必须包含 Context Pack」——强制上下文证据。
- **疑似缺失项**：
  - **YAML 块 line 5-61 没有「owner / 维护人 / 联系方式」**——谁负责这个 profile 不清楚。
  - **没有「profile 适用范围 / 反模式」**——什么场景下不该用此 profile。
  - **没有「profile 适用项目类型 / 规模」**——小项目和大项目可能用不同 profile。
  - **没有「profile 验证日期 / 最后更新」**——时效性不明。
  - **没有「profile 依赖的外部工具版本」**——例如要求 Node 18+ / Python 3.11+。
  - **「创建步骤」12 步（line 65-77）是线性流程**，没有「任一步失败如何回退」。
  - **没有「profile 升级失败时如何降级」**——比如 Level 2 升 Level 3 失败时怎么回退。
  - **「matchers」（line 10-14）缺「优先级 / 互斥规则」**——多 profile 同时命中时如何选。
  - **「commands」（line 47-51）只有 build/test/dev/lint**——缺 format/audit/benchmark/typecheck。
  - **「db_introspection」（line 52-55）只有 orm/migration_tool/schema_source**——缺「连接方式 / 只读账号 / 凭证存储位置」。

---

## 模板：impact-pro/profiles/_schema.md
- **文件路径**：`E:/agent/blue-skillhub/skills/impact-pro/profiles/_schema.md`
- **行数**：114
- **章节骨架**：
  1. 字段说明（YAML 字段 + 注释，line 7-58）
  2. Context Pack 规则 5 条（line 61-68）
  3. Level 定义 3 级（line 71-76）
  4. Profile 晋级协议 5 步 + 禁止 4 条（line 79-93）
  5. matchers 打分规则（line 96-103）
  6. 写入规范 5 条（line 106-111）
- **强制要素**：
  - [ ] Level 1-3 验收标准（line 72-76）
  - [ ] matchers 依赖 +3 文件 +1 目录 +1（line 97-102）
  - [ ] 最高分 profile 选中（line 102）
  - [ ] 无命中加载 generic（line 103）
  - [ ] Context Pack 每个候选标 1-3 + 0 排除（line 66-67）
- **占位符**：`[name]` `[files]` `[dependencies]` `[directories]` `[roles]` `[service]` `[data_access]` `[api]` `[config]` `[test]` `[migration]` `[entity]` `[dto]` `[ui]` `[naming]` `[layering]` `[orm]` `[transaction]` `[exception]` `[logging]` `[api_response]` `[dependency_injection]` `[build]` `[test]` `[dev]` `[lint]` `[schema_source]`
- **自身反模式**：
  - line 89-93 4 条禁止：
    - 不能只因文件名/依赖命中就标 Level 1
    - 不能把 generic 备用描述成专属 profile 已验证
    - 不能写未验证的命令/glob/目录/风格结论
    - 不能用 demo 项目的单一 happy path 覆盖生产级限制
  - line 108-110 写入规范 5 条：①结论标"运行时现采" ②不写未验证 glob/command ③迁移文件 glob 覆盖 SQL/Flyway/Liquibase ④新增/升级 profile 必须补充 context_discovery ⑤暂时无法验证的写入 notes.limitations
- **疑似缺失项**：
  - **「Level 1/2/3」（line 72-76）定义**——Level 1 真实项目 + 1 栈、Level 2 真实项目 ≥ 2 或生产级 ≥ 1、Level 3 多个生产级——但**没有每个 level 的最小样本数 / 失败容忍度**。
  - **「matchers 打分规则」（line 97-103）没有「负向打分」**——错误命中的扣分没有。
  - **「Context Pack 规则」（line 62-68）5 条**——缺「每层（L1/L2/L3）最大文件数」「每个候选最大引用行数」「context pack 写入位置是否在仓库内」。
  - **没有「profile 之间的依赖 / 继承」**——如 java-spring-mybatis 是否应继承 generic + 加 spring 专属。
  - **没有「profile 与 codegraph 的关系」**——code-graph-adapters 目录存在但 schema 不提。
  - **没有「profile 验证用例模板」**——Txx 验证记录格式没规定。
  - **「Level 3」line 76 验收「limitations 已充分覆盖」**——什么叫"充分"没量化。
  - **「写入规范」line 106-111 5 条**——缺「如何处理 profile 之间的命名冲突」「profile 命名空间」「废弃 profile 的归档位置」。

---

# Part E — 跨 skill 对比与系统性缺失

## E.1 三 skill 模板的重复度

| 模板 | impact | impact-pro | 差异度 |
|------|--------|-----------|--------|
| 000-context-pack | 102 行 | 105 行 | impact-pro 多 3 行（多了「已识别技术栈」「已加载技术栈规则」）+ 5 字段文件类型 |
| 010-requirements | 49 行 | 47 行 | impact-pro 把 2.x 提为独立节（2.1/2.2），反而比 impact 少 2 行 |
| 020-design | 99 行 | 117 行 | impact-pro 多 18 行（分析依据 / Schema 来源 / 行为准则检查 / 动态 style_axes） |
| 030-implementation | 89 行 | 88 行 | impact-pro 多 2 项前置检查 + 1 字段「确认类型」，但**删了「090-execution-record」节**——结构退化 |
| 040-light | 96 行 | 122 行 | impact-pro 多 26 行（行为准则检查 / 分析依据 / Schema 来源 / 未确认项独立） |
| 060-preflight | 101 行 | 101 行 | 完全相同结构，仅 line 67 多 `package-dot-json`，line 85 codeblock 标 `powershell` 而 impact 标 `bash` |
| 090-execution-record | 76 行 | 76 行 | 完全相同结构，仅 line 47-48 工具调用约定（impact 4 栈 vs impact-pro 2 栈 Python） |
| _active-state | 75 行 | 75 行 | 完全相同结构，仅 line 9 `skill:`、line 12 `package-dot-json` |
| subagent-decisions | 63 行 | 63 行 | **完全相同**（line 1-63 对应 1-63） |

**结论**：
- 8 对应模板中，**4 份完全相同**（060 / 090 / _active-state / subagent-decisions）。
- impact-pro 的主要价值在 020 / 030 / 040 三份（分析依据 / style_axes 动态 / 行为准则检查）。
- **2 份（010-requirements / 030-implementation）impact-pro 反而比 impact 短**——结构退化或精简过头。
- **profile 模板只有 impact-pro 有**——这是栈专属配置的核心。

## E.2 跨模板系统性缺失（按 IEEE 830 / arc42 / SRE / 实施文档标准）

### E.2.1 元数据 / 可追溯性
- **所有模板缺：版本号、修订历史、生成日期 / 时间、生成人 / 审阅人、分发范围**——仅 pathfinder【0】有"生成时间"和"基于 commit"。
- **缺：需求 / 设计 / 实施 / 验证之间的追溯矩阵（traceability matrix）**——impact 010 line 27「影响」字段是孤立的，没要求双向追溯。
- **缺：模板自身的版本号**——模板更新了，引用它的文档无版本对应。

### E.2.2 质量属性 / 非功能需求
- **所有模板缺：性能（latency / throughput / 资源占用）/ 可用性（uptime / 灾备）/ 可维护性（代码复杂度阈值）/ 可移植性 / 安全性（OWASP）专节**。
- **impact 020 line 99 / impact-pro 020 line 117 提到「按需展开」**——但没说"必填触发条件"（如"涉及用户认证时强制安全节"）。
- **缺：SLO / SLA / SLI 定义**——新功能上线后性能契约缺失。

### E.2.3 安全 / 合规
- **所有模板缺：威胁建模 / STRIDE / 数据流图（DFD）/ 隐私影响评估（PIA）/ GDPR / PCI / HIPAA 合规检查**。
- **pathfinder【9】风险区域 line 115 只要求"显式声明风险性质"**——没有强制 OWASP Top 10 扫描结果。
- **缺：密钥管理 / 凭证轮换策略**——line 58 凭证脱敏 `***` 只是展示安全，缺"凭证存储在哪里 / 多久轮换一次"。
- **缺：审计日志位置 / 留存期限 / 访问控制**。

### E.2.4 部署 / 运维
- **所有模板缺：部署拓扑 / 蓝绿 / 灰度 / 金丝雀发布策略**。
- **pathfinder 可选集（line 158-167）有"部署 / 运行拓扑"**——但 impact/impact-pro 全无部署章节。
- **缺：配置管理（ConfigMap / Vault / dotenv）策略**。
- **缺：监控 / 告警 / on-call runbook**——pathfinder 可选集有"可观测性"（line 166），但 impact 全无。

### E.2.5 业务 / 干系人
- **所有模板缺：干系人列表 / RACI 矩阵 / 沟通计划**。
- **缺：业务规则的可枚举形式（decision table / decision tree）**——impact 010 line 36-38 业务约束混排散文。
- **缺：变更影响范围（用户数 / 交易量 / 收入影响）**——纯技术视角，缺业务量化。
- **缺：上线 / 回退的 Go/No-Go 决策标准**——060 结论是 yes/no，但没要求"yes 时业务指标阈值"。

### E.2.6 验证 / 测试深度
- **所有模板缺：测试金字塔（unit / integration / e2e 比例目标）/ 覆盖率阈值（line/branch/path）**——000 context pack 提到 V0-V3 但没阈值。
- **缺：性能测试 / 压力测试 / 混沌测试**。
- **缺：契约测试（contract test）**——API 变更时上下游契约验证缺。
- **缺：回归测试范围**——改了 A，是否要重跑 B 的测试没说。
- **缺：测试数据管理**——谁提供测试数据 / 怎么脱敏 / 怎么清理。

### E.2.7 文档生命周期
- **所有模板缺：文档的过期 / 归档机制**。
- **缺：文档与代码的同步策略**——pathfinder【12】文档与知识入口（line 141-146）有"可信度（是否与代码同步）"但 impact 全无。
- **缺：模板实例的检索 / 索引方式**——多份 `change-impact/{需求名称}/` 目录没有总索引。

### E.2.8 协作 / 多人
- **所有模板缺：多人协作 / 冲突解决**——_active-state 没要求标识"当前独占"或"共享"。
- **缺：评审流程**——谁审 / 几轮审 / 准出标准缺。
- **缺：subagent / 人类角色边界**——subagent-decisions 提到但 SKILL.md 没明文规则。

## E.3 模板自身问题的诚实总结

| 模板 | 主要问题 |
|------|---------|
| impact/000-context-pack | 缺时间戳 / 审阅人 / 隐私分级 / 测试覆盖率 |
| impact/010-requirements | 缺 IEEE 830 元数据 / 干系人 / 非功能需求 / 验收测试方法 |
| impact/020-design | 硬编码栈标签（与 impact-pro 冲突）/ 缺 arc42 12 节骨架 / 缺接口契约 / 缺事务边界 / 缺性能 / 缺安全 |
| impact/030-implementation | 缺 Step 依赖图 / 缺 checkpoint ID / 缺变更窗口 / 11 字段过僵化 |
| impact/040-light | 定级证据缺判定标准 / 影响范围接口检查比 full 设计文档还细（反了）|
| impact/060-preflight | 缺外部依赖连通性 / 缺 dry-run / V1-only 阈值硬编码 / 缺时间预算 |
| impact/090-execution-record | 缺 Token 统计 / 缺确认时间戳 / 工具调用约定只列 4 栈 |
| impact/_active-state | 缺 Open Items P0/P1 分级 / 缺并发锁 / 缺自动/手动模式标记 / 缺总执行耗时 |
| impact/subagent-decisions | 决策三选一混入第四项（HUMAN-OVERRIDE-REQUIRED）/ 缺置信度 / 缺身份 |
| impact-pro/000-context-pack | 相比 impact 改进小；仍缺时间戳 / 审阅人 |
| impact-pro/010-requirements | 比 impact 少 2 行（顶部少凭证脱敏规则）/ 同样缺 IEEE 830 |
| impact-pro/020-design | style_axes 动态化是改进；但仍缺 arc42 / 接口契约 / 性能 / 安全 |
| impact-pro/030-implementation | **删了 090-execution-record 节**（结构退化）/ 缺基线命令 / 缺 V1-only 计数 |
| impact-pro/040-light | 行为准则检查 7 项是改进；但缺判定指标 / 缺回滚演练 |
| impact-pro/060-preflight | 与 impact 几乎完全相同；codeblock 标 `powershell` vs `bash` 不一致 |
| impact-pro/090-execution-record | 与 impact 几乎完全相同；工具调用约定改 2 栈 Python |
| impact-pro/_active-state | 与 impact 几乎完全相同 |
| impact-pro/final-readiness-audit | 8 条目标缺可验证子指标 / 10 维度无权重 / 缺升级失败回退 |
| impact-pro/scorecard | 6 分组 vs final-readiness 8 条目标不一致 / 缺评分量表 / 缺信度 |
| impact-pro/subagent-decisions | 与 impact 完全相同——**未引入 impact-pro 特有的 profile 选择决策** |
| pathfinder/project-map | 【4】核心功能最薄弱 / 【7】外部依赖缺 SLA / 【10】权限缺 PDP/PEP / 缺 CI/CD / 缺代码所有权 / 缺增量更新日志 |
| profiles/_template | 缺 owner / 适用范围 / 依赖工具版本 / 失败回退 |
| profiles/_schema | Level 3「充分覆盖」无量化 / 缺负向打分 / 缺 profile 间继承 |

## E.4 优先级建议

按"对生产可用性影响"排序，**最该补的 10 项**：

1. **所有需求/设计/实施/验证模板加「时间戳 + 审阅人」字段**——可追溯性是行业最低要求。
2. **所有模板加「非功能需求」专节**——性能 / 可用性 / 安全 / 可维护性 / 合规。
3. **所有模板加「SLO / 验收阈值」专节**——验证等级 V0-V3 升级为有阈值的契约。
4. **020-design 加「接口契约 / OpenAPI 变更」独立小节**——目前散落在「向后兼容性评估」一行。
5. **所有模板加「干系人 / RACI」专节**——避免技术完成后业务方拒收。
6. **所有模板加「部署 / 灰度 / 回滚 Go/No-Go」专节**——上线决策有量化标准。
7. **subagent-decisions 加「profile 选择记录」**（impact-pro）——栈自治的核心证据。
8. **_active-state 加「并发锁 / 自动-手动模式」**——多 agent 时代必需。
9. **pathfinder/project-map 可选集扩到 6-8 节**（加 CI/CD / CODEOWNERS / 测试覆盖率 / 性能基线）。
10. **final-readiness-audit 8 条目标加可验证子指标**——避免"满足"沦为口头。

## E.5 结论

- **3 skill 模板整体偏「执行前检查 + 强制确认 + 凭证脱敏 + V0-V3 验证等级」**——这是好的：安全闸 + 可恢复 + 可分级验证。
- **3 skill 模板共同缺「元数据 / 非功能需求 / 干系人 / 部署 / 监控 / 业务影响」**——是工程师视角的工程模板，不是产品 / 业务 / 运维的完整产品需求文档。
- **impact / impact-pro 8 份对应模板 4 份完全相同**——造成维护成本与不一致风险。
- **pathfinder 是 3 skill 中最结构化的**（核心 14 节 + 反模式防御 8 条 + 写前自检 4 项）——可作为 impact/impact-pro 模板改进的参考。
- **profile 模板是 3 skill 中最薄弱的**——缺 owner / 适用范围 / 依赖 / 升级回退，schema 的 Level 3「充分覆盖」无量化。

---

**生成时间**：2026-06-16
**生成方法**：Read 工具逐份读取 + 行号引用 + IEEE 830 / arc42 / SRE 标准对比
**关联基线**：本盘点用于"生产级对比"，识别模板自身不足，再与生产级 skill（如 RuoYi 全套、电商后端、数据中台）模板对比，得出"我们差什么"清单。
