# B7-B9 盲测归档总结

> 日期：2026-06-25 / 2026-06-26 修复重跑
> Runner：Composer 2.5（原会话）；CatPaw（B9 修复 + B8 干净重跑）
> Skill：impact-pro
> 补档说明：原会话完成了三个任务的 Phase 1-5 文档产出和代码修改，但归档步骤未执行。后续会话补产了归档和评审，并修复了 B9 遗漏和 B8 预存变更问题。

---

## 一、任务完成状态总览

| Case | 项目 | 技术栈 | 变更类型 | Phase 1-5 | 代码修改 | 验证等级 | 状态 |
|------|------|--------|----------|:---------:|:--------:|:--------:|:----:|
| B7 | go-admin | Go/Gin/GORM | 增量（加字段） | ✅ | ✅ 4 文件 | V1 | 已完成 |
| B8 | prisma-express-ts | Node/Express/Prisma | 破坏性（改 API 契约） | ✅ | ✅ 15 文件* | V2 | 已完成 |
| B9 | ruoyi-vue | Java/Spring/MyBatis | 破坏性（删字段） | ✅ | ✅ 3 文件 | V2 | 已完成 |

*B8 的 git diff 包含源项目预存变更，详见第四节问题说明。

---

## 二、各任务产出文件清单

### B7（go-admin — 给用户加微信号）

```
change-impact/B7/
  000-context-pack.md       — 上下文包（现状核查、链路追踪、假设清单）
  010-requirements.md       — 需求文档（业务场景、功能需求、验收标准）
  020-design.md             — 设计文档（数据模型、DTO、API、风格合规）
  030-implementation.md     — 实施文档（Step 1-3，高风险标注）
  060-preflight.md          — 执行前检查（P0 硬门禁全检）
  090-execution-record.md   — 执行记录（3 Step，含时间戳和 V 等级）
  _active-state.md          — 活跃状态（已完成，V1）
```

### B8（prisma-express-ts — name 改成 fullName）

```
change-impact/B8/
  000-context-pack.md       — 上下文包（破坏性引用扫描、破坏面回显、模拟决策）
  010-requirements.md       — 需求文档（业务场景、功能需求、破坏性说明）
  020-design.md             — 设计文档（Schema、代码层、Step 划分）
  030-implementation.md     — 实施文档（Step 1-4，高风险标注）
  060-preflight.md          — 执行前检查（P0 项）
  090-execution-record.md   — 执行记录（4 Step，含时间戳和 V 等级）
  _active-state.md          — 活跃状态（已完成，V2）
```

### B9（ruoyi-vue — 删掉用户备注字段）

```
change-impact/B9/
  000-context-pack.md       — 上下文包（remark 引用扫描、破坏面回显、模拟决策）
  010-requirements.md       — 需求文档（业务场景、功能需求、范围外说明）
  020-design.md             — 设计文档（后端、前端、不修改项）
  030-implementation.md     — 实施文档（Step 1-3）
  060-preflight.md          — 执行前检查（破坏面已回显、模拟确认）
  090-execution-record.md   — 执行记录（3 Step，含时间戳和 V 等级）
  _active-state.md          — 活跃状态（已完成，V2）
```

---

## 三、源码改动清单

### B7 — go-admin（4 files changed, 7 insertions）

```
app/admin/models/sys_user.go             | 1 +
app/admin/service/dto/sys_user.go        | 4 ++++
cmd/migrate/migration/models/sys_user.go | 1 +
common/middleware/handler/user.go        | 1 +
```

改动内容：在 SysUser 的 3 处 model 定义中同步新增 `Wechat string` 字段（GORM tag `size:64`/`type:varchar(64)`），DTO Insert/Update 增加 `Wechat` 字段及 `Generate()` 赋值。

验证：Go 未安装，`go build`/`go test` 无法运行，最高 V1（grep 验证）。

### B8 — prisma-express-ts（11 files changed, 34 insertions, 34 deletions）— 干净重跑

```
 prisma/schema.prisma               |  2 +-
 src/config/passport.ts             |  2 +-
 src/controllers/user.controller.ts |  6 +++---
 src/docs/components.yml            |  4 ++-
 src/routes/v1/auth.route.ts        |  6 +++---
 src/routes/v1/user.route.ts        | 14 +++++++-------
 src/services/auth.service.ts       |  2 +-
 src/services/user.service.ts       | 14 +++++++-------
 src/validations/user.validation.ts |  6 +++---
 tests/fixtures/user.fixture.ts     |  6 +++---
 tests/integration/auth.test.ts     |  6 +++---
 11 files changed, 34 insertions(+), 34 deletions(-)
```

改动内容：Prisma schema `name` → `fullName`，全量替换 User 字段引用（services、controllers、validations、routes、tests、swagger docs）。

验证：`npx prisma generate` 成功，`npx tsc --noEmit` 退出码 0（V2），`npm test` 因 Docker 未运行无法启动 PostgreSQL（V1 for test）。git diff 完全干净，无预存变更污染。

### B9 — ruoyi-vue（3 files changed + 1 修复）

```
ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml | 8 ++------
ruoyi-ui/src/views/system/user/index.vue                        | 8 --------
ruoyi-ui/src/views/system/user/view.vue                         | 8 --------
```

改动内容：SysUserMapper.xml 移除 remark 的 resultMap、SELECT、INSERT、UPDATE 引用；index.vue 移除备注表单项和 reset 中的 remark；view.vue 移除备注展示行。

验证：`mvn compile -q` 退出码 0（V2）。修复后再次 `mvn compile -q` 通过，grep SysUser.java 无 remark。

---

## 四、问题说明

### 问题 1：~~B8 源项目预存变更~~ — 已解决

**现象**：源项目 `test-projects/prisma-express-ts` 在复制前已有 8 个文件的未提交修改（来自此前 B3 phone validation 盲测）。

**解决**：2026-06-26 用干净副本（`git stash` 源项目后重新复制）重跑了 B8 全部 name→fullName 变更。新 diff 仅 11 个文件 34 行，全部是 name→fullName 相关改动，无任何预存变更污染。`npx prisma generate` + `npx tsc --noEmit` 均通过。

### 问题 2：B8/B9 文档较 B7 简略

B7 的分析文档（context-pack 37 行、design 35 行）较为详实，包含行号引用和链路追踪。B8（context-pack 44 行但 preflight 仅 12 行）和 B9（implementation 仅 8 行、preflight 仅 7 行）的文档明显更简略，执行记录也较为压缩。

### 问题 4：B9 SysUser.toString 遗漏 — 已修复

**现象**：`SysUser.java` 第 334 行 toString() 仍有 `.append("remark", getRemark())`。

**解决**：2026-06-26 00:15 删除该行，`mvn compile -q` 通过，grep SysUser.java 无 remark。

---

## 五、评审指引

评审时请使用 `eval/cases/blind-b7-b9/JUDGE-RUBRIC-B7-B9.md` 中的评分标准。

关键评审点：
1. **B7**：go-gin-gorm profile 是否正确触发；GORM struct tag 修改是否被标为高风险
2. **B8**：破坏性变更保护流程是否触发（先搜索引用 → 回显破坏面 → 追问决策）；name 的所有消费者是否被找到
3. **B9**：remark 的所有引用是否被找到；是否正确决定不动 BaseEntity（共享基类）和不 DROP COLUMN
4. **通用**：V 等级标注是否诚实（B7 V1 因 Go 未安装，B8 V2 因 build 通过，B9 V2 因 mvn compile 通过）
