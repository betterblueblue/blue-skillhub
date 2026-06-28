# E2E 验证评审手册

> 评审对象：Pathfinder 摸底 + Impact 变更分析的端到端产出
> 测试项目：`test-projects/realworld-express-prisma`
> 产出路径：`test-projects/realworld-express-prisma/change-impact/`

---

## 一、验证目标

本次 E2E 验证回答 4 个核心问题：

| # | 核心问题 | 验证模块 |
|---|---------|---------|
| Q1 | Pathfinder 能否对陌生项目产出结构完整、事实准确的项目认知地图？ | 任务 1 产出 |
| Q2 | Impact 能否基于模糊需求产出证据化的影响分析，且不确定项分类合理？ | 任务 2、3 产出 |
| Q3 | Pathfinder → Impact 的 L1 上下文交接是否真正生效？ | 任务 3 产出 |
| Q4 | Skill 的脚本闸门（Phase 1.5 + Script Gate）是否被正确执行？ | 任务 1 过程 |

---

## 二、项目 Ground Truth（评审基准）

> 以下是从源码直接读取的确定性事实，评审时用来对照产出文档是否准确。

### 2.1 技术栈

| 事实 | 证据 |
|------|------|
| Node.js + Express 4.18 + TypeScript 4.9 | `package.json` dependencies |
| Prisma 4.5 + PostgreSQL | `prisma/schema.prisma` datasource |
| JWT 认证（`express-jwt` 8.3 + `jsonwebtoken` 9.0） | `package.json` + `src/middleware/auth/authenticator.ts` |
| bcrypt 密码哈希 | `package.json` + `src/utils/hashPasswords.ts` |
| Winston 日志 | `package.json` dependencies |
| Jest 测试框架 | `package.json` devDependencies |

### 2.2 数据模型（4 个模型）

| 模型 | 主键 | 关键字段 | 关系 |
|------|------|---------|------|
| User | `username`（String @id） | email(@unique)、password、bio?、image? | follows/followedBy（自引用 M:N）、authored（1:M Article）、favorites（M:N Article）、comment（1:M Comment） |
| Article | `slug`（String @id） | title(@unique)、description、body、createdAt、updatedAt | author（M:1 User）、favoritedBy（M:N User）、comments（1:M Comment）、tagList（M:N Tag） |
| Comment | `id`（Int @id autoincrement） | body、createdAt、updatedAt | author（M:1 User）、Article（M:1 Article） |
| Tag | `tagName`（String @id） | — | article（M:N Article） |

### 2.3 认证链路

| 事实 | 证据 |
|------|------|
| JWT 签名算法 HS256 | `authenticator.ts:27` |
| 支持 `Token` 和 `Bearer` 两种 header 前缀 | `authenticator.ts:21` |
| JWT payload 含 `{ username, email }` | `createUserToken.ts:15` |
| 有两个 auth 中间件：`authenticate`（强制）和 `optionalAuthenticate`（可选） | `authenticator.ts:26-38` |
| JWT_SECRET 从环境变量读取，缺失时启动报错 | `authenticator.ts:7-9` |
| **无 role/权限字段**——纯身份认证，无 RBAC | User 模型无 role 字段，无权限中间件 |

### 2.4 注册流程（C2 变更基准）

| 事实 | 证据 |
|------|------|
| 注册路由 `POST /api/users` | `routes/api/users.ts:9` |
| 注册只接收 `{ email, password, username }` | `usersRegister.ts:19` |
| 密码哈希后存入 DB | `usersRegister.ts:22` |
| 注册成功后立即签发 JWT token | `usersRegister.ts:28` |
| **无邮箱验证步骤**——注册即用 | 全流程无 verify/email/confirmation 相关代码 |
| **User 模型无 emailVerified / verified 字段** | `schema.prisma` User 模型 |

### 2.5 请求体解析（C1 变更基准）

| 事实 | 证据 |
|------|------|
| 请求体解析在 `app.ts:18`：`app.use(express.json())` | `app.ts:18` |
| **未设 `limit` 参数**——默认 100kb（Express 4 内置 body-parser 默认值） | 无第二参数 |
| 全局生效，所有路由共用这一个 `express.json()` | `app.ts` 只调用一次 |

### 2.6 分层架构

```
src/
├── app.ts                    # Express 应用配置 + 全局中间件
├── server.ts                 # 启动入口
├── routes/api/               # 路由层（5 个路由文件）
├── controllers/              # 控制器层（按资源拆分目录）
├── middleware/               # 中间件层（auth / validator / errorHandling）
├── utils/
│   ├── auth/                 # JWT 工具
│   ├── db/                   # Prisma 数据访问层（按资源拆分）
│   ├── hashPasswords.ts      # 密码工具
│   ├── logger.ts             # Winston 日志
│   └── slugfy.ts             # Slug 工具
└── view/                     # 响应格式化层（5 个 viewer）
```

### 2.7 构建运行测试命令

| 操作 | 命令 |
|------|------|
| 安装依赖 | `npm install` |
| 数据库迁移 | `npm run migrate:develop`（即 `prisma db push`） |
| 开发模式启动 | `npm run develop`（即 `ts-node-dev`） |
| 构建 | `npm run build`（即 `tsc`） |
| 测试 | `npm test`（即 `jest -i`） |
| Docker 启动 PostgreSQL | `docker-compose.yml` |

---

## 三、任务 1 验证：Pathfinder 摸底

### 3.1 文件存在性检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-F1 | 地图文件存在 | 读 `change-impact/_project-map.md` | 文件存在且非空 |
| P-F2 | facts 目录存在 | 检查 `change-impact/_project-map/facts/` | 目录下有 `scan.json` 和 `git.json` |
| P-F3 | scan.json 非空 | 读 `facts/scan.json` | JSON 合法，含文件数/扩展名/目录树 |
| P-F4 | git.json 非空 | 读 `facts/git.json` | JSON 合法，含 HEAD/commits |

### 3.2 章节完整性检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-S1 | Executive Summary 存在 | grep `Executive Summary` | 找到，且有一句话概述 + Quick Start |
| P-S2 | 【0】～【14】全部存在 | 逐节 grep `【0】`到`【14】` | 15 个核心节全部存在 |
| P-S3 | **【14】代码风格观察非空壳** | 读【14】节内容 | 有实质性观察（naming/layering/orm/transaction/exception/logging/api_response 等轴），不是只有标题 |
| P-S4 | 【13】未覆盖项有内容 | 读【13】节 | 至少 1 条非空条目 |
| P-S5 | 可选节不强制 | 检查是否有"仓库活跃度""部署拓扑""可观测性" | 有则加分，无则不扣分 |

### 3.3 事实准确性检查（对照 Ground Truth）

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-A1 | 技术栈准确 | 对照【2】技术栈节 | 包含 Express/TS/Prisma/PostgreSQL/JWT/bcrypt/Winston，不能遗漏或编造 |
| P-A2 | 数据模型 4 个模型全列 | 对照【6】数据模型 ER 图 | User/Article/Comment/Tag 全部出现，关系正确 |
| P-A3 | User 主键是 username 不是 id | 检查【6】描述 | `username String @id`，不是自增 id |
| P-A4 | 认证机制描述准确 | 对照【10】权限/认证模型 | HS256、Token/Bearer header、两个中间件（authenticate/optionalAuthenticate） |
| P-A5 | **明确标注无 RBAC** | 检查【10】描述 | User 无 role 字段，纯身份认证无权限分级 |
| P-A6 | 注册即签发 token | 对照【11】主流程或【4】核心功能 | 注册成功后立即返回 JWT，无邮箱验证 |
| P-A7 | 分层描述准确 | 对照【3】架构分层 | routes → controllers → utils/db → view 四层 |

### 3.4 可信度标签检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-T1 | 每条事实有可信度标签 | 抽查 5 条事实 | 每条标 `【已核实: 证据】` 或 `【推断: 待验证】` |
| P-T2 | 已核实项有证据 | 抽查 3 条 `【已核实】` | 附带文件名/命令等证据 |
| P-T3 | 概览头部有 commit | 检查文件开头 | 有 `基于 commit:` + 真实 git HEAD |

### 3.5 三张图检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-G1 | 【3】架构/模块图存在 | grep Mermaid 代码块 | 有 `graph` 或 `flowchart` 语法 |
| P-G2 | 【6】数据模型 ER 图存在 | grep Mermaid 代码块 | 有 `erDiagram` 语法 |
| P-G3 | 【11】主流程图存在 | grep Mermaid 代码块 | 有 `sequenceDiagram` 或 `flowchart` 语法 |
| P-G4 | 箭头语义正确 | 检查实线/虚线 | 实线 = 已核实，虚线 = 推断 |

### 3.6 Script Gate 检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-V1 | pf_validate.py 被执行 | 检查 Composer 执行日志或对话中是否有运行记录 | 有运行 `pf_validate.py` 的命令输出 |
| P-V2 | V7 检查通过 | 检查验证输出 | `PASS: V7: section [14]` |
| P-V3 | 无 FAIL 项 | 检查验证输出 SUMMARY | `0 failed` |

### 3.7 认证-鉴权自检检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| P-Auth1 | 自检已执行 | 检查【10】或【9】节是否有自检记录 | 有认证-鉴权字段比对的记录 |
| P-Auth2 | 识别为 JWT 机制 | 检查自检描述 | 明确写出 JWT / express-jwt |
| P-Auth3 | claims 字段记录 | 检查自检描述 | 记录 `{ username, email }` 为 JWT payload |

---

## 四、任务 2 验证：Impact C1（light）— 请求体大小限制

### 4.1 产出文件检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C1-F1 | light 摘要文件存在 | 读 `change-impact/e2e/C1/040-light.md` | 文件存在且非空 |
| C1-F2 | Context Pack 存在 | 读 `change-impact/e2e/C1/000-context-pack.md` | 文件存在 |
| C1-F3 | active-state 存在 | 读 `change-impact/e2e/C1/_active-state.md` | 文件存在 |

### 4.2 影响范围准确性

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C1-A1 | 定位到 `app.ts:18` | 检查文档中引用的修改点 | `express.json()` 调用点，`app.ts:18` |
| C1-A2 | 识别为单点修改 | 检查影响范围描述 | 只涉及 `app.ts` 一个文件，不涉及 DB/schema/API 契约 |
| C1-A3 | 未过度扩大范围 | 检查是否有不必要的连带修改 | 不涉及 controller/middleware/route 改动 |
| C1-A4 | 提到 Express 默认 100kb | 检查现状描述 | 提到或知道 `express.json()` 默认 limit |

### 4.3 不确定项分类检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C1-U1 | Step 3.0 执行 | 检查文档中是否有分类记录 | 有"代码可推断"和"业务需决策"的分类 |
| C1-U2 | 限制大小为业务决策 | 检查分类 | "限制多少 MB"应为业务需决策项，标注 `[假设]` |
| C1-U3 | 修改位置为代码可推断 | 检查分类 | "改哪里"应为代码推断项，标注 `【代码推断: app.ts:18】` |

### 4.4 定级检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C1-L1 | 定级为 light | 检查定级记录 | light 档，理由：单文件、不涉及 DB/API/权限 |
| C1-L2 | 判档决策表存在 | 检查定级记录 | 有判档决策表（条件 + 证据 + 结论） |

---

## 五、任务 3 验证：Impact C2（full）— 强制邮箱验证

### 5.1 产出文件检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-F1 | Context Pack 存在 | 读 `000-context-pack.md` | 文件存在且非空 |
| C2-F2 | 需求文档存在 | 读 `010-requirements.md` | 文件存在且非空 |
| C2-F3 | 设计文档存在 | 读 `020-design.md` | 文件存在且非空 |
| C2-F4 | 实施文档存在 | 读 `030-implementation.md` | 文件存在且非空 |
| C2-F5 | active-state 存在 | 读 `_active-state.md` | 文件存在 |

### 5.2 多层影响覆盖检查

> 这是 C2 的核心验证点。强制邮箱验证涉及多个变更层面，文档必须覆盖。

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-A1 | **Prisma schema 变更** | 检查文档是否提到 User 模型加字段 | 需加 `emailVerified Boolean` 或类似字段，且标为高风险（ORM schema 编辑 = ALTER TABLE） |
| C2-A2 | **注册流程改动** | 检查文档是否提到 `usersRegister.ts` | 注册后不再立即签发可用 token，或签发受限 token |
| C2-A3 | **登录校验改动** | 检查文档是否提到 `usersLogin.ts` | 登录时需检查邮箱验证状态 |
| C2-A4 | **新增验证端点** | 检查文档是否提到新路由 | 需新增 `POST /api/users/verify` 或类似端点 |
| C2-A5 | **邮件发送工具** | 检查文档是否提到邮件发送 | 需引入 nodemailer 或类似库，当前项目无邮件依赖 |
| C2-A6 | **auth 中间件影响** | 检查文档是否提到 `authenticator.ts` | `authenticate` 中间件可能需检查 emailVerified 状态 |
| C2-A7 | **JWT payload 影响** | 检查文档是否提到 `createUserToken.ts` | token payload 是否需包含验证状态 |

### 5.3 不确定项分类检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-U1 | Step 3.0 执行 | 检查分类记录 | 有"代码可推断"和"业务需决策"分类 |
| C2-U2 | 验证方式为业务决策 | 检查分类 | "邮件链接 vs 验证码"应为业务需决策 |
| C2-U3 | 现有路由结构为代码推断 | 检查分类 | "注册路由路径""登录路由路径"应为代码推断，不问用户 |
| C2-U4 | User 模型无验证字段为代码推断 | 检查分类 | "schema 有没有 emailVerified"应为代码推断 |
| C2-U5 | 假设标注清晰 | 检查所有 `[假设]` | 每个 `[假设]` 标注在哪个文档、哪个位置 |

### 5.4 L1 上下文交接检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-L1 | 读取了 _project-map.md | 检查 Context Pack 中 L1 项目地图节 | 有 `【L1 项目地图】` 引用或 `【已核实: _project-map.md】` |
| C2-L2 | 引用了地图中的架构分层 | 检查 Context Pack | 引用了【3】架构分层信息 |
| C2-L3 | 风格规范预读 | 检查文档是否提到代码风格 | 引用了 `_project-map.md`【14】代码风格观察或 `_style-rules.md` |
| C2-L4 | HEAD 一致性检查 | 检查文档是否比对地图 HEAD | 提到 commit 一致性或地图未过期 |

### 5.5 定级检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-L5 | 定级为 full | 检查定级记录 | full 档，理由：跨 schema/路由/中间件/工具层 |
| C2-L6 | 判档决策表存在 | 检查定级记录 | 有判档决策表 |
| C2-L7 | 高风险项标注 | 检查高风险清单 | Prisma schema 编辑标为高风险 |

### 5.6 文档间事实一致性检查

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| C2-X1 | Context Pack 与需求文档一致 | 交叉比对关键事实 | 模型名、字段名、路由路径一致 |
| C2-X2 | 设计文档与实施文档一致 | 交叉比对修改点 | 修改文件列表、Step 顺序一致 |
| C2-X3 | 无自相矛盾 | 通读全部文档 | 不能出现"注册流程需改"和"注册流程不改"同时存在 |

---

## 六、端到端协作验证

| # | 检查项 | 验证方法 | 预期 |
|---|--------|---------|------|
| E2E-1 | Pathfinder 先于 Impact 完成 | 检查产出时间顺序 | `_project-map.md` 存在后 C2 才引用它 |
| E2E-2 | Impact 实际读取了地图 | 检查 C2 文档中地图引用 | 有明确的地图引用痕迹，不是空壳引用 |
| E2E-3 | 地图中的事实被 Impact 复用 | 检查 C2 是否使用了地图中的分层/认证信息 | C2 的 Context Pack L1 节有地图内容 |
| E2E-4 | 地图中的推断项被 Impact 重新取证 | 检查 C2 是否对地图【推断】项做了验证 | 地图标【推断】的项在 C2 中有重新取证记录 |

---

## 七、评分标准

### 7.1 等级定义

| 等级 | 含义 | 标准 |
|------|------|------|
| **S** | 生产可用 | 所有 MUST 项通过，事实零错误，多层影响全覆盖 |
| **A** | 基本可用 | 所有 MUST 项通过，事实错误 ≤1 处，影响覆盖 ≥6/7 |
| **B** | 有缺陷 | MUST 项失败 ≤2 个，事实错误 ≤3 处 |
| **C** | 不可用 | MUST 项失败 >2 个，或事实错误 >3 处 |

### 7.2 MUST 项（一票否决）

以下检查项为 MUST，任一失败直接降到 B 或更低：

- P-F1（地图文件存在）
- P-S2（【0】～【14】全节存在）
- P-S3（【14】非空壳）
- P-A1（技术栈准确）
- P-A2（4 个模型全列）
- P-V1（Script Gate 执行）
- C1-A1（定位到 app.ts）
- C2-A1（schema 变更识别）
- C2-A2（注册流程改动识别）
- C2-F1～F4（full 四文档齐全）
- E2E-2（Impact 读取了地图）

### 7.3 加分项

- 认证-鉴权自检深度超出预期（P-Auth1~3 全通过）
- C2 影响覆盖 7/7（C2-A1~A7 全通过）
- V9 事实一致性零冲突（C2-X1~X3 全通过）
- 地图中有准确的 Mermaid ER 图且关系正确（P-G2 + 箭头语义正确）

---

## 八、评审执行流程

```
1. 读 PROMPT.md 确认 Composer 执行了哪些任务
2. 检查文件存在性（第三章 P-F1~F4、第四章 C1-F1~F3、第五章 C2-F1~F5）
3. 运行 pf_validate.py 确认 Script Gate 结果（P-V1~V3）
4. 逐章对照 Ground Truth 检查事实准确性（P-A1~A7、C1-A1~A4、C2-A1~A7）
5. 检查不确定项分类质量（C1-U1~U3、C2-U1~U5）
6. 检查 L1 交接是否生效（C2-L1~L4、E2E-1~4）
7. 检查文档间一致性（C2-X1~X3）
8. 按评分标准定级
9. 输出评审报告
```

### 评审报告模板

```markdown
# E2E 评审报告

## 总评

- Pathfinder 评级：[S/A/B/C]
- Impact C1 评级：[S/A/B/C]
- Impact C2 评级：[S/A/B/C]
- 端到端协作评级：[S/A/B/C]

## MUST 项结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| P-F1 | PASS/FAIL | ... |
| ... | ... | ... |

## 事实错误清单

| # | 错误描述 | 应为 | 实际 |
|---|---------|------|------|
| 1 | ... | ... | ... |

## 缺失影响点

| # | 预期影响点 | 是否覆盖 |
|---|-----------|---------|
| 1 | ... | ✅/❌ |

## 亮点

- ...

## 改进建议

- ...
```
