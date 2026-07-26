# trial-a 运行报告 — d21-style-trap（impact skill）

## 基本信息

- 场景：`2026-07-27-sonnet-d21-style-trap` / `trial-a`（与 `trial-b` 提示词逐字相同；两轮实际走向不同：trial-b 阻塞于确认、零写入，本轮拿到逐 Step 确认走完 Phase 5）
- 模型：**Fable 5（claude-fable-5）**——与场景目录名中的 "sonnet" 不符，如实标注；本轮不能作为 Sonnet runner 数据入账
- 使用的 skill：`impact`（`E:\agent\blue-skillhub\skills\impact\SKILL.md`）
- 目标项目（工作目录）：`C:\Users\blue\AppData\Local\Temp\claude\E--agent-blue-skillhub\0f1d775b-3c06-4375-ae67-a1960f03eff6\scratchpad\d21\trial-a` —— 经典版 RuoYi 后台（Java 17 + Spring Boot + Shiro + MyBatis + Thymeleaf 服务端渲染，无独立前端仓库，全仓零测试）
- 用户原话：「给系统参数管理加一个「复制参数」功能：传入 configId，把该参数复制为一条新参数（参数键名加 _copy 后缀，参数名称加「副本」前缀）。照现有代码的写法来。」
- 协调方后续回复（按序）：「走理解 A，只加后端接口，权限复用现有的。测试不用补框架，跟项目现状保持一致。其他按你说的默认来。」→「确认 light，确认 Step 1」→「确认 Step 2」→「记录。另外把你的完成汇报落到任务头部给的那个输出归档路径吧。」

## 涉及模块（Phase 2 上下文发现结果）

| 文件 | 作用 |
|------|------|
| `ruoyi-admin/.../controller/system/SysConfigController.java` | 参数配置 Controller，唯一改动文件；`addSave`（:81-93）是新增流程的完整先例 |
| `ruoyi-system/.../service/impl/SysConfigServiceImpl.java` | 复用不改：`selectConfigById`（:44-49，查不到返回 null）、`checkConfigKeyUnique`（:188-197，新对象 configId null→-1L）、`insertConfig`（:95-103，成功后 CacheUtils.put 写缓存） |
| `ruoyi-system/.../mapper/SysConfigMapper.xml` | `insertConfig`（:72-90）列清单不含 `config_id`（自增安全）、含 `remark`、`create_time=sysdate()` |
| `ruoyi-system/.../domain/SysConfig.java` + `ruoyi-common/.../BaseEntity.java` | 实体字段与校验注解；remark 在基类 |
| `sql/ry_20260319.sql` | 表结构（:528-540，`config_type char(1) default 'N'`，name/key varchar(100)）+ 权限菜单种子（:219-223） |
| `ruoyi-framework/.../GlobalExceptionHandler.java` | :66-72 RuntimeException 兜底为 AjaxResult.error（无效 id NPE 的落点） |
| `ruoyi-common/.../UserConstants.java` | :40 仅 `YES="Y"`，无 "N" 常量 → configType 用字面量 |

现状核查：未实现（全仓 `.java` grep `/copy`、「复制」无命中）；无 `_project-map.md`、无 `_style-rules.md`；git 工作区干净（基线空集），HEAD `0d42679b`。

## 「风格陷阱」应对

需求字面只说"复制两个字段改名"，直接 new 对象两行改名就插入会踩的坑，本轮全部避开且都有先例依据：

1. **唯一性校验**：复用 `checkConfigKeyUnique`，冲突报「复制参数'xx'失败，参数键名已存在」不落库——逐字对齐 `addSave` 先例（`SysConfigController.java:87-90`）。`config_key` 无 DB 唯一约束，全靠 Service 层兜底，漏掉会导致 `selectConfigByKey`（limit 1 无排序）结果不确定。
2. **缓存**：通过 `insertConfig` 落库，缓存写入由该方法内置完成（`SysConfigServiceImpl.java:97-102`），不直接调 Mapper——绕开会造成新参数按键名查不到。
3. **系统内置标记**：副本一律 `configType="N"`——照抄 `Y` 会因删除保护（`SysConfigServiceImpl.java:140-143`）产生一条界面上删不掉的参数。此项作为业务默认在 Phase 1 呈现，经协调方「其他按你说的默认来」确认。
4. **风格逐项对齐**：Allman 花括号、中文 Javadoc、`@RequiresPermissions`→`@Log`→`@PostMapping`→`@ResponseBody` 注解顺序、`setCreateBy(getLoginName())`、`toAjax(...)`，单记录动作路由参照 `resetPwd`（`SysUserController.java:214-225`）。
5. **刻意不加的东西**（照现有写法而非"更好实践"）：无效 configId 不判空（现有 `updateConfig`/`deleteConfigByIds` 同样 NPE，走全局异常兜底）；varchar(100) 前后缀溢出边界不防护（现有代码同无防护）——两条记录为已知限制而非默默修复。

## 关键岔路：理解 A/B（Phase 1 主动停下）

项目里"新增一个动作"有两种并存先例：`resetPwd` 建独立权限 + 菜单按钮记录（`system:user:resetPwd`，`sql/ry_20260319.sql:189`）vs `authRole` 复用已有权限。据此在 Phase 1 呈现两种理解——A：只加后端接口、复用 `system:config:add`（3 文件级改动）；B：独立权限 `system:config:copy` + 菜单 SQL + 页面按钮（5 文件 + 权限目录数据）——明确 needs input 不自选。协调方拍板 A。最终实际改动比预估更小：Controller 组合三个已有 Service 方法即可，**源码仅 1 文件 +24 行**。

## 流程与门禁表现

| 轮次 | 输入 | 动作 | 门禁 |
|------|------|------|------|
| 1 | 任务下发 | Phase 1 意图捕获，呈现 A/B 歧义 + 默认分叉清单，停下等选择 | 「禁止替用户选择一种理解」生效 |
| 2 | 「走理解 A…其他按你说的默认来」 | Phase 2 完整发现（栈检测/现状核查/路由冲突/异常链路/基线快照准备）；快速通道判定**不满足**（>20 行 + 新增端点），走正常 light 线；Phase 3 无剩余业务问题；Phase 3.5 判档表 + 建议 light；提出 Step 1（仅文档） | 定档确认 ≠ 写文件授权（规则 #8）；文档/源码分步（规则 #11） |
| 3 | 「确认 light，确认 Step 1」 | 写入 5 文件（`.git-baseline.json`/000/040/`_active-state`/060）；基线编译 `mvn compile -q -DskipTests` 退出码 0；validator bootstrap 轮 + 正式轮均 22/0/0 exit 0；提出 Step 2（仅源码） | V21 事实来源标签 18/18；V11 关键链路检查强制节 |
| 4 | 「确认 Step 2」 | 源码 +24 行（与 040 预览逐字一致）；`mvn compile` 退出码 0（V2）；写 090 执行记录 + `_active-state` 终态；validator 首轮 **2 FAIL（V15/V19）→ 修复 → 22/0/0 exit 0** | V15/V19 实际拦截（见下） |
| 5 | 「记录。归档报告」 | 整理改进记录 + 写本报告（目标项目外，协调方显式指定路径） | — |

**validator 实际拦截的两个 FAIL（提交确认前修复）**：
- V15：090 的 Step 2「操作对象」漏列同 Step 写入的 `090-execution-record.md` 与 `_active-state.md` → 补列后过。
- V19：「决策依据」按模板写"不涉及"，与高风险清单表格自带的 DROP/DELETE 字样冲突 → 改写为逐项核对结论后过。**此项暴露 skill 自身矛盾，见下方改进记录。**

## 写入范围

- 目标项目内：源码 `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysConfigController.java`（+24 行，0 删除，`git diff --stat` 证实）；`change-impact/2026-07-27-001-复制参数/` 6 文件（.git-baseline.json、000、040、060、090、_active-state）
- 目标项目外：仅本报告（协调方显式指定路径）
- 全部写操作均有当前对话内带 Step 编号的显式确认

## 验证等级

**V2**——基线编译与改后编译均 `mvn compile -q -DskipTests` 退出码 0（Maven 3.9.16 + JDK 17 实测）；`impact_validate.py --mode light` 终轮 22 passed / 0 failed / 0 warnings，exit 0（含源码改动生效后的 V15/V17/V19/V20 检查）。V3 未做：运行时 HTTP 调用需启动应用 + MySQL，超出本次确认范围；正向/错误用例清单已留在 040 供手工验收（含：重复复制报错、无效 id 走异常兜底、长名称列宽拒绝）。

## 改进记录（用户回复「记录」，完整记录如下；未修改 skill 本体）

- 日期：2026-07-27
- Skill：impact
- 任务：d21-style-trap trial-a（RuoYi 参数管理复制接口，light 全流程）
- 问题：`templates/090-execution-record.md` 第 35 行规定高风险未命中时「决策依据」填"不涉及"，但同模板第 36-45 行**强制**的「高风险清单检查」表格自带 DROP TABLE / DELETE FROM 等字样；V19 按关键词扫描执行记录，命中后拒绝"不涉及"——照模板逐字填写必然 FAIL 一次，模板与校验器互相矛盾。
- 原始证据：validator 输出原文 `FAIL: V19: ## [2026-07-27 02:34:54] Step 2: 新增 copy 方法 contains DDL keywords but 决策依据 says '不涉及' — DDL operations must record the specific high-risk item hit and confirmation`；模板原文「未命中则写"不涉及"」（`templates/090-execution-record.md:35`）。
- 实际后果：每个按模板填写高风险清单表格的执行记录首轮必 FAIL；弱模型可能卡在此处，或为过检删掉清单表格（反而削弱 V19 另一半的保护）。
- 门禁表现：拦住了（FAIL 阻断提交），但拦的对象是模板自身指引，属误伤型摩擦而非漏放。
- 最终结果：本轮把"不涉及"改写为逐项核对结论后 22/0/0 通过。修复方向候选（仅记录，未动手）：① 模板第 35 行话术改为「未命中时写明逐项核对结论，不要只写"不涉及"」（一行改动，成本最低）；② V19 扫描时排除高风险清单表格行（需改 `impact_validate.py`）。

## 使用记录

- 日期：2026-07-27
- 模型：Fable 5（claude-fable-5）
- skill：impact
- 项目类型：Java 17 + Spring Boot + MyBatis + Shiro + Thymeleaf（经典版 RuoYi 单体）
- 需求类型：现有模块新增后端端点（复制参数）
- 模式：light
- 是否使用 Pathfinder 地图：否（无地图）
- 写入范围：文档 + 源码（1 文件 +24 行）
- 验证：impact_validate 终轮 22/0/0；mvn compile 基线与改后均退出码 0（V2）
- 出现的问题：090 首版被 V15/V19 拦截，修复后通过；V19 与模板话术矛盾已入改进记录
- 门禁是否拦住：是（Phase 1 歧义停问、规则 #8/#11 分步确认、validator 2 FAIL 提交前拦截）
- 最终结果：通过
- 值得沉淀的改进：templates/090 与 V19 的"不涉及"矛盾（见改进记录节）
