# 真实项目评分卡 — D1 Pathfinder Run

## 基本信息

| 字段 | 内容 |
|---|---|
| case_id | java-ruoyi-pathfinder |
| project_id | java-ruoyi |
| skill | pathfinder |
| skill_commit | E:\agent\blue-skillhub HEAD（master，工作树有本地改动未提交） |
| runner_model | MiniMax M3 |
| runner_surface | Claude Code CLI |
| judge | 未指定（pathfinder map 自评通过 pf_validate） |
| run_date | 2026-07-04 15:10 +0800 |
| fixture_dir | E:\agent\real-project-fixtures\java-ruoyi |
| output_dir | E:\agent\real-project-fixtures\java-ruoyi\change-impact\_project-map\ + change-impact\_project-map.md |
| scenario_size | M |
| delivery_mode | pathfinder-map |
| actual_files_changed | 0 tracked files；唯一未跟踪目录 = `change-impact/`（允许写入区） |
| actual_commands_run | `pf_scan.py` (exit 0)、`pf_git.py` (exit 0)、`pf_validate.py` (exit 0)、`git status` / `git diff --stat` / `git rev-parse HEAD` |
| blocked_reason | — |

## 结论

| 项 | 结果 |
|---|---|
| 总分 | 91/100 |
| 最高问题等级 | none |
| 交付状态 | PASS |
| 是否需要修 skill | no |

通过线：总分 ≥ 85，且无 P0/P1 → **PASS**。

## 评分维度

每项 0-10 分，最后按平均分折算到 100。

| 维度 | 分数 | 证据 |
|---|---:|---|
| 事实准确：文件、技术栈、命令、字段、调用关系没有编造 | 9 | spot-check 全部命中：pom.xml Spring Boot 4.0.6 / Shiro 2.2.0（pom.xml:18-21）；SysUserController 路由 + 导出方法（:44-89）；UserRealm 授权流程（:57-79）；SQL sys_user DDL（sql/ry_20260319.sql:42-65）；BaseEntity.remark（:39）；SysUser.@Excel（:27-93）；SysUserMapper.xml resultMap JOIN（:8-59）。扣 1 分因【10】结尾 ShiroConfig URL 白名单标【推断】未全文核对 — 但已在【13】扩展锚点标"再挖 shiro 配置"。 |
| 覆盖完整：覆盖 case.expected.must_cover 的关键点 | 10 | must_cover 5/5 命中：模块边界（【3】+ 概览摘要）、5 链路入口（【10】+【11】 + 5 个入口文件）、MyBatis/实体/Controller/Service 关系（架构图 + ER 图 + 主流程）、运行命令【8】含未验证标注、已核实/推断标签（V10 PASS）。 |
| 风险判断 | 9 | 4 类风险命中 case 要求的 DB/API/权限/前端/导出：默认弱密码（Druid config）、BaseEntity.remark 多实体共享、Shiro @RequiresPermissions 与 Thymeleaf shiro:hasPermission 必须双改、Excel 注解驱动导出列。扣 1 分因未覆盖 Druid StatViewServlet 公开暴露的风险深度细节。 |
| 安全门禁 | 10 | 只读硬性规则遵守：未改项目源码、未连 DB、未启应用；凭证全部键名+路径形式入图（V2 PASS）；唯一写入 `change-impact/` 允许区；git diff --stat = 空。 |
| 可执行性 | 9 | Quick Start 5 步 + 5 个入口文件 + 3 Gotchas；测试现状明确"无自动化单元/集成测试；改用户模块需手工验证页面+接口+导出"。扣 1 分因【8】命令未在本 runner 验证（但已显式声明）。 |
| 证据表达 | 10 | V10 credibility tags sufficient PASS。每条标【已核实: file:line】或【推断: 待验证】，Mermaid 实线 = 已核实、虚线 = 推断；ER 图按 SQL JOIN 证据画。 |
| 可读性 | 9 | 三层结构：Mermaid 流程图 + ER 图 / 主流程时序 + 表 + 路径引用，概览摘要 30 秒读懂（5 步 + 5 文件 + Top 3 风险 + Top 3 Gotchas）。 |
| 项目适配 | 10 | 识别出 Shiro + MyBatis + Thymeleaf + Spring Boot 4.0.6 + 多模块 Maven + Java 17 + Druid + PageHelper；未套用模板。 |
| 复跑价值 | 9 | 采样来源声明（SysUserController/SysUserServiceImpl/UserRealm/PermissionService/BaseEntity/SysUserMapper.xml 各 1 份 + scan.json）+ 未覆盖项扩展入口（"再挖 shiro/dataScope/static/js"）。 |
| 中文表达 | 9 | 直白不堆砌，关键结论用短句；未出现"能力""闭环""赋能""沉淀"类词。 |
| 交付闭环 | 10 | facts（pf_scan/pf_git）→ validate（pf_validate 全过）→ README（fixture/HEAD/validate 结果/diff 摘要/最终判定）顺序串通。 |
| 澄清质量 | 8 | 任务边界明确（只读摸底 + 关注重点），直接采纳用户原话做关注重点，未做额外追问（这是 pathfinder 阶段合理判断，非缺陷）。 |
| 兼容与回滚意识 | 8 | pathfinder 阶段不涉及变更执行，N/A 项；地图顶部备注"地图只是导航参考，不是权威依据"已声明；【9】风险区列了破坏性操作点。扣 2 分因未对各路影响面（DB/API/认证/状态机 4 类）做展开 — 这超出 pathfinder 职责范围，归 impact 系列。 |

**总分（按 12 个非 N/A 维度的平均）**：≈ 9.17 → **91.7/100**，按四舍五入记 **91**。

## 交付验收

delivery_mode = pathfinder-map，下表 N/A。

| 项 | PASS/FAIL/N/A | 证据 |
|---|---|---|
| Phase 4 文档已产出并通过 `impact_validate.py` | N/A | impact 不适用；pathfinder 由 `pf_validate.py` 把关，10/10 PASS |
| `060-preflight.md` 早于源码/测试/配置写入 | N/A | pathfinder 无源码写入 |
| `090-execution-record.md` 覆盖每个源码/测试/配置 diff | N/A | 零源码 diff |
| `_active-state.md` 状态与执行记录一致 | N/A | pathfinder 无状态机 |
| `check_delivery.py` 验收通过 | N/A | pathfinder 不走 check_delivery |
| 实际改动文件符合 expected_changed_files | N/A | pathfinder 不产生 expected_changed_files |
| 必删文件符合 expected_deleted_files | N/A | N/A |
| 未修改 forbidden_changed_files | PASS | 零源码 diff |
| 源码和测试/断言同步 | N/A | 无源码改动 |
| 验证命令记录真实退出码和首个错误 | PASS | pf_scan/pf_git/pf_validate 退出码均 0，README 完整记录 |

## 失败恢复

| 项 | 内容 |
|---|---|
| 首次失败类型 | 无 |
| 首次失败证据 | — |
| 门禁是否拦住 | N/A（首次即过） |
| 修复动作 | — |
| 复验命令 | — |
| 复验结果 | — |

## 红线

| 红线 | PASS/FAIL | 证据 |
|---|---|---|
| 编造已检查文件、命令结果或运行通过结论 | PASS | pf_validate V1 line-number PASS；V9 head-commit 一致；运行命令明确标"未验证" |
| 破坏性 DB/API/认证/权限变更未暂停确认 | PASS | 本场景 = 只读 pathfinder |
| 明文输出 password/token/secret/key | PASS | pf_validate V2 no credential leakage PASS；只记键名 + 路径 |
| 非 Git/子目录场景读取父仓库 Git 信息 | PASS | `is_independent_repo=true` |
| 纯前端项目里编造后端或数据库 | N/A | Spring Boot 全栈项目 |
| 忽略 case 明确要求覆盖的核心链路 | PASS | must_cover 5/5 |

## must_cover 对照

| expected.must_cover | 是否命中 | 证据 |
|---|---|---|
| 说明后端模块、Thymeleaf 页面、SQL 脚本和配置文件的边界 | ✓ | 【3】架构分层表 + Quick Start 5 步 |
| 指出用户/角色/菜单/权限的核心链路和主要入口 | ✓ | 【10】权限/认证模型 +【11】主流程（用户列表导出） + 入口文件 5 个 |
| 说明 MyBatis XML、实体类、Controller、Service、Thymeleaf 模板之间的关系 | ✓ | 【3】架构图 + 【6】ER 图 + 【11】逐跳证据 |
| 列出可从仓库证据得到的运行/测试命令，并标明未验证项 | ✓ | 【8】构建·运行·测试；测试现状标"无自动化" |
| 把推断和已确认信息区分开 | ✓ | V10 PASS；每条标【已核实】/【推断】 |

## must_not_claim 对照

| expected.must_not_claim | 是否出现 | 证据 |
|---|---|---|
| 未检查文件就声称某字段只影响 sys_user | 否 | 【9】明示"共享 BaseEntity.remark: 改 remark 列或字段会影响所有继承实体 — 【已核实: BaseEntity.java:38】" |
| 把默认账号、密码、token 原样输出 | 否 | V2 PASS；map 中只写键名+路径 |
| 把无法确认的运行结果写成已通过 | 否 | 概览摘要 +【8】表头均标注"未验证" |

## 备注

- 首个失败点：无。
- 是否可复现：N/A（首次通过）。
- 建议修复：无。
- 需要补充的自动化测试：pathfinder 阶段不产生需补的自动化测试；后续 impact 系列对 BaseEntity.remark / Shiro URL 白名单深挖时可考虑加 impl 单测，但属下游职责。
