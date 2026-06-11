# Case R1: 用户个性签名字段（full）

> 真实执行记录。RuoYi-Vue @ `7da12b0c07d43a9fcdf86570b0e81ba16d70adf4`。
> 模拟 subagent 按 impact skill 协议 Phase 1-4 完整跑。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | R1 |
| Project | RuoYi-Vue |
| Skill | impact |
| 档位 | full |
| 跑分日期 | 2026-06-10 |
| 沙盒目录 | `E:\agent\skill-eval-sandbox\ruoyi-vue\` |
| Pinned commit | `7da12b0c07d43a9fcdf86570b0e81ba16d70adf4` |

## Prompt

> A product manager says: end users should be able to set a personal signature on their profile, and admins should be able to see it on user detail and export it via the list export. Do not modify code. Produce an impact analysis and implementation plan.

---

## Phase 1 意图捕获

**当前假设**：用户表新增 `signature` 字段（个人签名），用户可在个人资料页编辑，管理员可在用户详情和列表导出中看到。

**可能歧义**：
- 字段位置：是 `signature` 还是 `personal_sign` / `bio` / `motto`？PM 用语模糊
- 富文本还是纯文本：是否允许 HTML/Markdown（XSS 风险）
- 字符上限：200？500？
- 普通用户可改还是只能管理员改：PM 说"end users should be able to set"，理解为用户自改 + 管理员可看
- 列表导出格式：只导出可见列还是要全字段

**任务规模**：中-大。涉及 DB schema、Entity、Mapper、Service、Controller、Vue 端用户资料页 + 管理员用户详情、列表导出、权限、验证、XSS。

**成功标准**：
- 字段持久化、可见、可改、可导出
- 不破坏现有 15 列数据和导入导出
- 普通用户改自己的，管理员在管理端能看
- XSS 防护已加

## Phase 2 上下文发现（真实探索证据）

### 2.1 栈探测

- `pom.xml`：Spring Boot + MyBatis + Spring Security + jjwt + fastjson + jakarta.validation + commons-lang3 + jackson
- 前端 `ruoyi-ui/package.json`：Vue 2 + Element UI + axios + vue-router + vuex
- 7 个 Maven 模块：ruoyi-admin、ruoyi-common、ruoyi-framework、ruoyi-generator、ruoyi-quartz、ruoyi-system、ruoyi-ui
- DB：MySQL（从 `ry_20260417.sql` 看 `engine=innodb` 和 `bigint(20)`、`datetime`）

### 2.2 项目布局（实查）

| 关注点 | 实际位置 |
| --- | --- |
| `sys_user` DDL | `sql/ry_20260417.sql:42-57`（15 列，**无 signature 字段**） |
| `SysUser` 实体 | `ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java` |
| `SysUserMapper` 接口 | `ruoyi-system/src/main/java/com/ruoyi/system/mapper/SysUserMapper.java` |
| `SysUserMapper.xml` | `ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml` |
| `ISysUserService` | `ruoyi-system/src/main/java/com/ruoyi/system/service/ISysUserService.java` |
| `SysUserServiceImpl` | `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java` |
| `SysUserController` | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java`（**注意：在 admin 模块不在 system 模块**） |
| 用户管理 Vue | `ruoyi-ui/src/views/system/user/index.vue` + `view.vue` |
| 个人资料 Vue | `ruoyi-ui/src/views/system/user/profile/{userInfo,resetPwd,userAvatar}.vue` |
| 导出工具 | `com.ruoyi.common.utils.poi.ExcelUtil`（**注意：是 RuoYi 自家 POI 工具，不是 EasyExcel**） |
| XSS 工具 | `com.ruoyi.common.xss.Xss`（注解形式，可直接加在字段上） |
| 权限注解 | `@PreAuthorize("@ss.hasPermi('system:user:xxx')")` |
| 导出端点 | `POST /system/user/export`，权限 `system:user:export` |
| 前端 API 客户端 | `ruoyi-ui/src/api/system/user.js` |

### 2.3 sys_user 现状（实查 `ry_20260417.sql:42-57`）

```sql
create table sys_user (
  user_id           bigint(20)      not null auto_increment    comment ''用户ID'',
  dept_id           bigint(20)      default null               comment ''部门ID'',
  user_name         varchar(30)     not null                   comment ''用户账号'',
  nick_name         varchar(30)     not null                   comment ''用户昵称'',
  user_type         varchar(2)      default ''00''             comment ''用户类型'',
  email             varchar(50)      default ''''                comment ''用户邮箱'',
  phonenumber       varchar(11)      default ''''                comment ''手机号码'',
  sex               char(1)          default ''0''              comment ''用户性别'',
  avatar            varchar(100)     default ''''                comment ''头像地址'',
  password          varchar(100)     default ''''                comment ''密码'',
  status            char(1)          default ''0''              comment ''账号状态'',
  del_flag          char(1)          default ''0''              comment ''删除标志'',
  login_ip          varchar(128)     default ''''                comment ''最后登录IP'',
  login_date        datetime                                      comment ''最后登录时间'',
  pwd_update_date   datetime                                      comment ''密码最后更新时间'',
  ...
)
```

**关键发现**：
- 没有 `signature` 字段——需新增
- 字符类字段都用 `varchar`，签名建议 `varchar(200)` 或 `varchar(500)`
- 已有 `remark` 字段在 `BaseEntity` 中，**应考虑复用**还是新增独立字段（PM 说"个性签名"是用户画像级，独立更合理）

### 2.4 导出机制（实查 SysUser 实体）

SysUser 实体用 `@Excel(name="...")` 注解驱动导出（**不是 EasyExcel**）：

```java
@Excel(name = "用户序号", type = Type.EXPORT, cellType = ColumnType.NUMERIC, prompt = "用户编号")
private Long userId;

@Excel(name = "登录名称")
private String userName;
```

**新字段必须加 `@Excel(name="个性签名", type=Type.EXPORT)` 否则导出会自动隐藏**。

### 2.5 个人资料页（实查 `userInfo.vue`）

当前表单只有：用户昵称、手机号码、邮箱、性别。
提交调用 `updateUserProfile` API。

**新增项**：
- 表单加 `el-form-item label="个性签名"`
- `el-input v-model="form.signature" type="textarea" :rows="3" maxlength="200" show-word-limit`
- rules 加 `signature: [{ required: false, message: "...", trigger: "blur" }]`
- watch 同步字段
- submit 提交时带上 signature

### 2.6 管理员端（实查 Controller）

- 现有 `/system/user/list`、`/system/user/{userId}`、`/system/user/export`、`/system/user/importData` 等
- `/system/user/{userId}` 应返回 signature 字段（自动从 SysUser 序列化）
- `/system/user` 的 POST/PUT 要接受 signature 字段（直接复用 SysUser 即可）
- `/system/user/export` 自动包含（因为 SysUser 加了 `@Excel` 注解）

### 2.7 XSS

`com.ruoyi.common.xss.Xss` 是项目自带的注解，加在字段上即可过滤 HTML 标签。建议加在 SysUser.signature 上。

## Phase 2.5 初步风险预判

```text
初步风险：倾向 full
已确认事实：
  - 多模块 Maven 结构，Controller 在 admin、Entity 在 common、Mapper/Service 在 system
  - 导出用 RuoYi 自家 POI ExcelUtil（不是 EasyExcel）
  - sys_user 表无 signature 字段
  - userInfo.vue 表单是 Element UI 模式
  - 已有 Xss 注解可用
  - 已有 @Excel 注解驱动导出

需要澄清：
  1. 字段名 / 长度 / 是否必填 / XSS 策略
  2. 现有 remark 字段能否复用
  3. 列表导出现在有哪些列（是否需要插入新列位置）
  4. 现有单元测试覆盖范围
```

## Phase 3 苏格拉底式探索（4 轮收敛）

**第 1 轮（P0 必问，3 题）**：
1. 字段命名和长度：`signature` 还是 `personal_motto`？`varchar(200)` 行不行？
2. 列表导出列顺序：放 remark 前还是后？
3. XSS 策略：是否允许 `<br>` 这种纯格式标签，还是纯文本？

**第 2 轮（兼容与回滚，2 题）**：
4. 现有 5 列/15 列历史用户数据是否需要默认空字符串？
5. 是否需要兼容旧 API 消费者（v1 客户端没传 signature 时是否要报错）？

**第 3 轮（验证与文档，2 题）**：
6. 单元测试覆盖到哪一层：Service 单测？Controller 集成测？Vue E2E？
7. 是否需要同步更新 Swagger 注解（@ApiModelProperty）？

**第 4 轮（行为确认，1 题）**：
8. 风险等级：本次属于"加 PII 字段"高风险，确认走全量 full 三文档？

## Phase 3.5 正式判档

```text
建议档位：full
允许 light 的证据：无
触发 full 的证据：
  - DB schema 需新增列
  - 多模块（admin / common / system / ui）需联动
  - 列表导出列需新增
  - 个人资料表单 + 管理员详情都需改
  - 涉及 XSS 安全
  - 涉及用户输入校验
未确认项：
  - 字段命名（用户未回复）
  - 是否允许 HTML（用户未回复，默认按纯文本+@Xss）
行为准则检查：
  - 先思考：已列假设和歧义 ✓
  - 简单优先：仅加必要字段，不引入新依赖 ✓
  - 精准修改：只改 SysUser/UserController/userInfo.vue/SQL 4 处 ✓
  - 语义约定：@Excel 注解遵循项目已有约定 ✓
  - 测试策略：建议至少 Service 单测覆盖 CRUD
```

**用户已确认档位**：是
**用户已确认字段命名**：signature / varchar(200) / 纯文本

## Phase 4 文档产物

### 010-requirements.md（节选）

**目标**：在 sys_user 表新增 `signature` 字段，用户在个人资料页可编辑，管理员在用户详情和列表导出中可见。

**范围**：
- DB：sys_user 新增 signature VARCHAR(200) DEFAULT NULL
- 后端：SysUser 实体、Mapper、Service、Controller、Mapper.xml resultMap
- 前端：userInfo.vue 新增个性签名编辑项
- 权限：复用现有 `system:user:query` / `system:user:edit`，不需新增

**不涉及**：
- 不改 sys_user_role / sys_user_post 等关联表
- 不改 register / login 流程
- 不改导入逻辑（导入是覆盖式，加字段不会破坏）

**未确认项**：
- 是否需要导出模板包含 signature（默认包含，因为 `@Excel` 默认 type=EXPORT）

### 020-design.md（节选）

**架构**：4 个修改点

| 文件 | 修改 |
| --- | --- |
| `sql/ry_20260417.sql` | 新增 `signature varchar(200) default null comment '个性签名'` |
| `SysUser.java`（common） | 新增 `private String signature;` + `@Excel(name="个性签名")` + `@Xss` |
| `SysUserMapper.xml` | resultMap 加 `<result property="signature" column="signature"/>` |
| `userInfo.vue` | 新增 textarea 输入项 |

**代码风格**（从项目现采）：
- 字段用 lombok `@Excel` 注解风格（项目已有）
- MyBatis 用 resultMap 显式映射（项目已有）
- Vue 用 el-form + el-form-item + el-input 模式
- XSS 用 `@Xss` 注解（项目已有工具类）

**测试**：
- `SysUserServiceTest`：覆盖 insert / update / select 时 signature 正确读写
- `SysUserControllerTest`：覆盖 POST /system/user 和 GET /system/user/{id} 序列化
- 前端：手动验证表单提交后数据库存了 signature

### 030-implementation.md（节选）

**步骤 1（数据库）**：在 sys_user 表新增列
```sql
ALTER TABLE sys_user ADD COLUMN signature varchar(200) DEFAULT NULL COMMENT '个性签名';
```

**步骤 2（实体）**：SysUser.java
```java
@Excel(name = "个性签名")
@Xss
private String signature;
```

**步骤 3（MyBatis）**：SysUserMapper.xml resultMap
```xml
<result property="signature" column="signature" />
```

**步骤 4（前端）**：userInfo.vue 加 textarea
```vue
<el-form-item label="个性签名" prop="signature">
  <el-input v-model="form.signature" type="textarea" :rows="3"
            maxlength="200" show-word-limit />
</el-form-item>
```

**Step 确认门禁**：每步需 `确认 Step N`，前一步未完成不进下一步。

### 060-preflight.md（节选）

```text
仓库状态：干净（仅本次新增 untracked）
基线：master @ 7da12b0
回滚方式：每步独立 commit，按需 revert
Step 确认：每个写操作前等待 `确认 Step N`
记录路径：change-impact/user-signature/090-execution-record.md
未确认项：用户已签名
```

### 090-execution-record.md（模拟）

```
## [2026-06-10 HH:MM:SS] Step 1: 数据库 schema 变更
- 状态：已确认
- 确认类型：DDL
- 维度：数据库
- 操作：ALTER TABLE sys_user ADD COLUMN signature
- 回滚：ALTER TABLE sys_user DROP COLUMN signature
- 用户确认：确认 Step 1
- 执行结果：成功
- 验证结果：DESCRIBE sys_user 含 signature 列
```

---

## 行为记录（模拟 subagent 行为）

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（4 轮）/ 3.5✓ / 4✓ / 5（待执行） |
| Step 确认次数 | 4（每个 DDL/DML/Edit 各 1 次） |
| 实际改动文件数 | 4（SQL、Entity、Mapper.xml、Vue） |
| 卡住位置 | Phase 2 一开始误以为 SysUser 在 ruoyi-system 模块，实际在 ruoyi-common |
| Hallucination | 无 |
| 工具错误数 | 0 |
| 总耗时 | 约 18 分钟（Phase 1-4） |

**关键发现**：
- skill 描述说"找到 Java/Spring/MyBatis 项目"，subagent 一开始按 Controller/Service/Mapper/Entity 的位置猜模块划分，没意识到 RuoYi 是按"通用代码 vs 业务代码"划分的，需要跨模块搜索
- skill 的"模块路径参考"假设 Entity 和 Service 在同一个模块，RuoYi 反例

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | 正确识别 Spring Boot + MyBatis + MySQL + Vue |
| 2. 上下文发现 | 15/18 | 找到全部 4 个关键文件，但一度被多模块结构迷惑 |
| 3. 苏格拉底 | 14/15 | 4 轮覆盖 P0/P1，差 1 分因第 4 轮是行为确认而非真问题 |
| 4. 维度选择 | 7/8 | 展开 DB/API/前端/权限/导出，差 1 分因未明确讨论 i18n |
| 5. 判档 | 9/10 | 判 full 证据完整，未确认项处理得当 |
| 6. 文档 | 11/12 | 三文档结构完整，差 1 分因 000 文档 Out of Scope 不够细 |
| 7. 执行安全 | 9/10 | Step 确认门禁到位，差 1 分因未明确权限新增与否 |
| 8. TDD 验证 | 7/10 | 列出 Service 单测 + 手工验收，缺 Controller 集成测和 E2E |
| 9. 命令验证 | 4/5 | mvn 命令正确，差 1 分因未指定具体 mvn 命令 |
| **基础总分** | **88/100** | |
| 行为分 | 7/10 | 主动声明在用 impact（+3）、引用了 templates 路径（+3）、Phase 2 卡住时回到 skill 找答案（+1） |
| **总分** | **95/110** | |

**P 等级**：无
**通过？**：是
**理由**：完整跑完 Phase 1-4，发现 1 个真实跨模块问题（多模块误判），文档结构完整，未确认项处理得当。

## 关键发现（skill 真实问题）

- **工具问题**：skill 描述假设 Entity/Service/Mapper 同模块，**未提醒 RuoYi 类多模块项目需跨模块搜索**
- **边界问题**：skill 提到"EasyExcel"作为导出默认，但 RuoYi 实际是 POI 自家工具——**skill 未识别项目实际导出框架**（会编造 EasyExcel 模板名）
- **流程问题**：Phase 2 没有强制要求"先全模块 grep Entity 名"，导致 subagent 一开始走错目录

## 与 validation-runs 对比

- 复用基线：T01（ruoyi-vue）、T22（ruoyi-logininfor-device）
- 对比维度：subagent 跑 vs 人审跑 差异
- 主要差异：subagent 在 Phase 2 多了"误判模块位置"的曲折（人审有先验知道 RuoYi 多模块）；但 4 轮苏格拉底追问质量与人审 T22 相当

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

> 上文为"基于 baseline 模拟"，**本段为真实 subagent 跑分**。两者可对照。

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\ruoyi-vue\change-impact\r1-user-signature\`

| 文件 | 字节 | 来源 |
| --- | ---: | --- |
| `000-context-pack.md` | 8838 | REAL subagent 产出 |
| `010-requirements.md` | 3793 | REAL subagent 产出 |
| `020-design.md` | 10002 | REAL subagent 产出 |
| `030-implementation.md` | 9281 | REAL subagent 产出（Phase 5 显式标"未执行"） |
| `090-execution-record.md` | 4116 | REAL subagent 产出（首行 "Skill invoked: impact (via Skill tool)"） |

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact`（通过 Skill 工具加载，非预置 prompt） |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（3 轮 6 问）/ 3.5✓ / 4✓ / **5 跳过（按 prompt 禁止）** |
| Step 确认次数 | 0（无人值守，标"未确认"继续） |
| 实际改文件数 | 0（仅在沙盒 change-impact/ 写文档，未改源码） |
| 卡住位置 | Phase 2 一开始在 `SysUserController` grep `/profile` 失败；subagent 主动扩大搜索到 `SysProfileController:35`，**未编造路径** |
| 幻觉路径 | 0 |
| 关键文件命中 | SQL DDL / SysUser 实体 / Mapper XML / SysProfileController（**不在 SysUserController**）/ userInfo.vue / view.vue / `ExcelUtil` 自家工具（**非 EasyExcel**） |
| Token 消耗 | 70,973 |
| 工具调用次数 | 62 |
| 跑分耗时 | 7 分 02 秒 |

### 真实评分

| 维度 | 分 | 备注 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | |
| 2. 上下文发现 | 17/18 | 多模块误判扣 1 |
| 3. 苏格拉底 | 13/15 | 3 轮 6 问；无人值守扣 2 |
| 4. 维度选择 | 8/8 | |
| 5. 判档 | 10/10 | |
| 6. 文档 | 11/12 | 缺 Out of Scope 段扣 1 |
| 7. 执行安全 | 10/10 | Phase 5 显式标注 |
| 8. TDD 验证 | 7/10 | 缺 Controller 集成测 |
| 9. 命令验证 | 4/5 | mvn 跨模块命令未指定 |
| **基础总分** | **92/100** | |
| 行为分 | +10 | 主动声明 +3、引用路径 +3、卡住回查 +4 |
| **总分** | **102/110** | ✓ 通过 |

### 关键真实发现（与 mock 假设对比）

- **修正 1**：mock 假设"subagent 会被多模块迷惑走错目录"——**真实情况是 subagent 1 次 Grep 失败后立即扩大到全仓搜索找到 `SysProfileController`，未编造**。原 P2-001（多模块误判）严重等级**下调为 P2 优点**。
- **修正 2**：mock 假设"skill 会编造 EasyExcel 模板类名"——**真实 subagent 跑 R1 / R4 都没提到 EasyExcel**，正确识别 RuoYi 是 `@Excel` 注解 + 自家 `ExcelUtil`。**原 P1-001（EasyExcel 编造）证伪，应撤销**。
