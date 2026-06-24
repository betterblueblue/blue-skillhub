# 盲测说明

> 用真实开发场景测试小模型（Composer 2.5 / Step 3.7 Flash）执行 skill 的能力。
> 与现有 L1 的区别：不预设答案、不写 trap_for、独立评审。

## 设计原则

1. **只给 prompt，不给答案**：case JSON 里只有用户需求 + 项目路径，没有 `expected`、`trap_for`
2. **真实场景**：每个 prompt 都是开发中会真实遇到的需求，不是为了让 skill 翻车而设计的陷阱
3. **独立评审**：跑完后由独立 judge 拿着源码核实，不是让跑分模型自己打分
4. **聚焦小模型**：重点看小模型在证据真实性、引用完整性、判档准确性上的表现

## Case 清单

| ID | skill | 项目 | 场景 | 测试重点 |
|----|-------|------|------|----------|
| B1 | impact | RuoYi-Vue | 给操作日志加响应耗时记录 | 跨模块发现（AOP + DB + 前端 + 导出） |
| B2 | impact | RuoYi-Vue | 密码加密从 MD5 改 BCrypt | 安全敏感变更 + 兼容性处理 |
| B3 | impact-pro | prisma-express-ts | 给用户加手机号字段 | Prisma schema + 验证 + 迁移 |
| B4 | impact-pro | go-admin | 给用户管理加重置密码功能 | go-admin 多处重复 struct + API 新增 |
| B5 | pathfinder | full-stack-fastapi-template | 摸底全栈项目架构 | 全栈栈检测 + 数据模型 + 构建命令 |
| B6 | pathfinder | prisma-express-ts | 摸底数据模型和认证流程 | 认证链路 trace + 数据模型 ER |

## 执行方式

### 对每个 case × 每个模型：

1. **准备**：确保 test-projects/ 下的项目已 clone 且干净
2. **执行**：让小模型用对应 skill 处理 case 的 prompt
3. **收集**：产出文件在 `test-projects/<project>/change-impact/` 下
4. **评审**：judge 拿着 `JUDGE-RUBRIC.md` + 项目源码，核实产出中的每条证据
5. **出卡**：写评分卡到 `eval/runs/blind-<date>-<model>/B<id>.scorecard.json`

### 每个模型跑 6 个 case，2 个模型 = 12 次执行

```
模型 A（Composer 2.5）→ B1 B2 B3 B4 B5 B6
模型 B（Step 3.7 Flash）→ B1 B2 B3 B4 B5 B6
```

### 评审产出

每个 case 出一张评分卡，包含：
- 安全门禁（4 项 PASS/FAIL）
- 质量维度（6 项共 100 分）
- 关键发现（3-5 条，附证据）
- 是否可直接 approve（yes / no / with-fixes）

## 目录结构

```
eval/cases/blind/
├── README.md              # 本文件
├── JUDGE-RUBRIC.md        # 评审标准
├── impact/
│   ├── B1-*.json
│   └── B2-*.json
├── impact-pro/
│   ├── B3-*.json
│   └── B4-*.json
└── pathfinder/
    ├── B5-*.json
    └── B6-*.json
```

跑分记录写入：
```
eval/runs/blind-<date>-<model>/
├── B1.scorecard.json
├── B2.scorecard.json
├── ...
└── _summary.md
```

## 为什么这些 case 能测出真问题

| Case | 隐藏的复杂度 | 小模型容易忽略什么 |
|------|-------------|-------------------|
| B1 | 操作日志的记录不在 Controller 而在 AOP 切面；耗时需要在过滤器/拦截器层记录；列表页 Excel 导出也要加字段 | 漏掉 AOP/拦截器层；漏掉导出功能 |
| B2 | RuoYi 密码可能不是纯 MD5；需要确认实际加密方式；兼容方案涉及登录流程改动 | 不核实就假设是 MD5；兼容方案不完整 |
| B3 | Prisma schema 改了要迁移；注册验证逻辑分散在 controller + service + validation；已有用户手机号为空 | 漏迁移；漏验证层 |
| B4 | go-admin 的 SysUser struct 在 3+ 个地方重复定义；重置密码涉及密码加密逻辑；权限路由 | 漏掉重复 struct；漏密码加密 |
| B5 | 全栈项目前后端分离；alembic 迁移；Docker 编排；OpenAPI 自动生成 client | 漏掉一端的技术栈 |
| B6 | JWT auth 流程跨 controller + service + middleware + token model | 认证链路串不完整 |
