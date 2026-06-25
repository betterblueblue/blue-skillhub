# 优先级 4 盲测设计 — 扩大覆盖面（技术栈 + 破坏性变更）

> 日期：2026-06-25
> 路线图优先级 4：扩大盲测覆盖面
> skill_commit: e252fc8（v4.1 + Phase 5 改进）
> runner: Composer 2.5

---

## 一、为什么做这个测试

此前所有盲测（B1-B6, E1-E4）全是"加"场景（加字段、加功能）。破坏性变更（删字段、改 API 契约）是风险最高的场景，恰恰最需要 skill 兜底，但没有盲测覆盖。

技术栈方面，go-gin-gorm profile 从未被盲测过。

## 二、Case 设计

### B7: go-admin — 给用户加微信号（impact-pro，Go/Gin/GORM 栈覆盖）

| 字段 | 值 |
|------|-----|
| skill | impact-pro |
| stack | go-gin-gorm |
| 项目 | test-projects/go-admin |
| 变更 | 给 SysUser 加 `wechat` 字段，用户管理 API 支持设置和返回 |
| 档位 | full（DB schema + API + 测试） |
| 变更类型 | 增量变更 |
| 验证目标 | go-gin-gorm profile 在盲测下的表现 |

用户原话："用户能不能加个微信号字段，就是在编辑用户的时候能填，列表里也能看到"

### B8: prisma-express-ts — 把用户 name 改成 fullName（impact-pro，破坏性变更：改 API 契约）

| 字段 | 值 |
|------|-----|
| skill | impact-pro |
| stack | node-express-prisma |
| 项目 | test-projects/prisma-express-ts |
| 变更 | 把 User 的 `name` 字段重命名为 `fullName`，API 返回字段名跟着改 |
| 档位 | full（DB schema + API 契约 + 测试） |
| 变更类型 | **破坏性变更**（改 API 契约） |
| 验证目标 | 破坏性请求保护流程是否触发；反向引用检查是否覆盖所有消费者 |

用户原话："用户的 name 字段能不能改成 fullName，就是接口返回的和表单里显示的都要改"

### B9: ruoyi-vue — 删掉用户的备注字段（impact-pro，破坏性变更：删字段）

| 字段 | 值 |
|------|-----|
| skill | impact-pro |
| stack | java-spring-mybatis |
| 项目 | test-projects/ruoyi-vue |
| 变更 | 删除 SysUser 的 `remark` 字段，后端 Entity/Mapper/Service/Controller 和前端页面全部清理 |
| 档位 | full（DB schema + Java + 前端） |
| 变更类型 | **破坏性变更**（删字段） |
| 验证目标 | 破坏性请求保护流程是否触发（先只读搜索引用 → 回显破坏面 → 追问决策）；反向引用检查是否完整 |

用户原话："用户的备注字段不要了，把它删掉，相关的代码也清理一下"

## 三、Case 覆盖矩阵

| 验证点 | B7 (go-admin, 增量) | B8 (prisma, 破坏-改名) | B9 (ruoyi, 破坏-删字段) |
|--------|:-------------------:|:---------------------:|:----------------------:|
| 新技术栈 | ✅ Go/Gin/GORM | ❌ | ❌ |
| 破坏性变更保护 | ❌ | ✅ 改 API 契约 | ✅ 删字段 |
| 反向引用检查 | ❌ | ✅ name 的所有消费者 | ✅ remark 的所有引用 |
| 高风险拦截 | ⚠ ALTER TABLE | ⚠ DROP COLUMN + 改契约 | ⚠ DROP COLUMN |
| impact-pro + RuoYi | ❌ | ❌ | ✅ 首次 |
| 实际写代码 | ✅ | ✅ | ✅ |

## 四、评审重点

### 增量变更（B7）
- go-gin-gorm profile 是否正确触发（技术栈检测、style_axes、验证命令）
- GORM struct tag 修改是否被识别为高风险（等同于 ALTER TABLE）

### 破坏性变更（B8/B9）
- **破坏性请求保护流程**是否触发：先只读搜索引用 → 回显破坏面 → 追问决策
- **反向引用检查**是否完整：B8 的 `name` 字段在哪些文件中被引用？B9 的 `remark` 在哪些文件中被引用？
- **高风险拦截**是否命中：DROP COLUMN / 删旧接口 / 删公共导出
- **单独确认**是否执行：破坏性 Step 是否禁止合并确认
