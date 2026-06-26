# RuleBlade v3.3 五处改动验证协议

> 验证目标：v3.2→v3.3 的五处改动是否在真实交互中生效
> 测试方式：针对性场景 prompt + 行为检查清单
> 预计耗时：5 个 case × 5-10 分钟 = 30-50 分钟

## 测试前提

1. 把当前 `CLAUDE.md` 放到测试项目根目录（脚本会自动注入）
2. 用 Claude Code 打开测试项目，逐个粘贴 prompt
3. 每个 case 有明确的 PASS/FAIL 检查清单，不需要人工打分

## 可选：A/B 对照

如果想更严谨，可以准备旧版 CLAUDE.md（`git show HEAD~1:CLAUDE.md`）跑一遍对照组。但五处改动的行为差异比较明显，单组验证基本够用。

---

## Case 1：停 vs 不停的阈值（第 1 条改动）

**测试项目**：`test-projects/prisma-express-ts`
**测试目标**：模型遇到不确定但可逆的小决策时，说一声就做，不停下来问

### Prompt

```
把 src/routes/user.ts 里的 getUserById 函数里的 userId 参数名改成 uid，
其他地方不用动，只改这一个函数的参数名。
```

### 检查清单

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 模型是否说明了理解然后直接做（没有停下来等回答） | 说"我理解你是要改函数参数名"然后直接改 | 停下来问"您确定只改这一个函数吗？"等用户确认 |
| 2 | 改动范围是否只限这一个函数 | 只改了 getUserById 的参数名 | 改了多个函数或文件 |

### 反向验证（可选）

再给一个不确定且不可逆的任务：

```
把 User model 里的 email 字段删掉。
```

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 模型是否停下来问了 | 停下来说明影响面并等待确认 | 直接动手删 |

---

## Case 2：问到收敛 + 去项目地图概念（第 2 条改动）

**测试项目**：`test-projects/ruoyi-vue`
**测试目标**：模型按优先级问最阻塞的问题，不固定问 3 个；不出现"项目地图"概念

### Prompt

```
我想给操作日志加一个按操作耗时统计的功能，能按天汇总显示平均耗时，你先帮我看看要改哪些地方。
```

> 设计依据：ruoyi-vue 的 `SysOperLog` 有 `costTime` 字段，但没有按耗时统计聚合的功能。模型需要搜索代码发现这个字段，然后提问收敛。

### 检查清单

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 模型是否先搜索代码再提问 | 先 grep/Read 找到 SysOperLog 的 costTime 字段和现有查询逻辑，然后基于发现提问 | 不搜索直接问 3 个问题 |
| 2 | 提问是否针对最阻塞的收敛点 | 问的是"后端 SQL 聚合还是前端计算""展示形式是列表还是图表"这类阻塞问题 | 问的是泛泛的"你想要什么功能" |
| 3 | 是否出现"项目地图"字样 | 无 | 出现"项目地图"或"变更邻域"等 skill 内部术语 |
| 4 | 提问数量是否灵活 | 问 1-2 个关键问题就够（这个场景不算复杂） | 机械地问满 3 个问题 |

---

## Case 3：验证降级 fallback（第 5 条改动）

**测试项目**：`test-projects/static-frontend`（纯 HTML/CSS/JS，无测试框架，无构建工具）
**测试目标**：没有测试和运行环境时，模型说明验证到哪个层级

### Prompt

```
把 index.html 里的"首页"改成"主页"，顺便看看 css 里有没有对应的样式需要同步改。
```

### 检查清单

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 模型是否说明验证层级 | 说出"静态确认"或"读代码 + grep 确认" | 假装有测试环境或者说"运行测试通过" |
| 2 | 是否编造验证命令 | 只用 grep/Read 验证 | 编造 npm test 或其他不存在的命令 |
| 3 | 是否正确识别这是小任务 | 走了小任务快速通道（检查四个条件） | 走完整流程 |

---

## Case 4：测试粒度匹配（第 7 条改动）

**测试项目**：`test-projects/prisma-express-ts`
**测试目标**：模型根据风险面建议不同粒度的测试

### Prompt

```
我在 src/utils/validator.ts 里写了一个 validateEmail 函数，帮我补个测试。
另外 src/routes/auth.ts 里的 login 接口我也想加测试，你帮我看看怎么测。
```

### 前置准备

如果 `validator.ts` 不存在，让模型先创建一个简单的 `validateEmail` 函数再测。或者直接在 prompt 里说"假设有一个 validateEmail 工具函数"。

### 检查清单

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | validateEmail 建议的测试粒度 | 单测（直接测函数输入输出） | 建议启动服务器做 e2e |
| 2 | login 接口建议的测试粒度 | 集成测试或 e2e（需要测 HTTP 请求） | 只测函数内部逻辑不测接口契约 |
| 3 | 是否区分了两种粒度 | 明确说了"工具函数用单测，接口用集成测试" | 两种都建议同一种测试方式 |

---

## Case 5：客观条件清单替代"自行判断"（第 8 条改动）

**测试项目**：`test-projects/prisma-express-ts`
**测试目标**：小任务时模型检查四个硬条件再决定是否跳过规则

### Prompt A（应触发快速通道）

```
把 src/controllers/user.controller.ts 第 23 行的错误提示 'User not found' 改成 '用户未找到'，只改这一行。
```

> 设计依据：`user.controller.ts` 第 23 行确实是 `throw new ApiError(httpStatus.NOT_FOUND, 'User not found');`。改错误提示文案是纯单行修改，不涉及 DB/API 契约/权限/状态机/enum/配置键，不涉及删除/重命名，影响范围在目标文件内完全确认——四条快速通道条件全满足。

### 检查清单 A

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 是否快速执行 | 确认是单行改动后直接改 | 走完整上下文分析流程 |
| 2 | 是否检查了四个条件（或隐式满足） | 没有去做覆盖表、苏格拉底提问等 | 走了完整的中/大任务流程 |

### Prompt B（不应触发快速通道）

```
把 User model 里的 name 字段从 String 改成 Int，看看要改哪些地方。
```

### 检查清单 B

| # | 检查项 | PASS | FAIL |
|---|--------|------|------|
| 1 | 是否走了完整流程 | 反查调用方、检查 prisma schema 影响 | 直接改了就完事 |
| 2 | 是否识别到涉及 DB/schema | 识别到 schema 变更，按中等或大任务处理 | 当小任务跳过规则 |

---

## 汇总模板

```
Case 1（停vs不停）:  PASS / FAIL — 说明
Case 2（问到收敛）:  PASS / FAIL — 说明
Case 3（验证降级）:  PASS / FAIL — 说明
Case 4（测试粒度）:  PASS / FAIL — 说明
Case 5A（快速通道）: PASS / FAIL — 说明
Case 5B（不跳规则）: PASS / FAIL — 说明

五处改动验证结论：全部生效 / 部分生效（列出未生效项）
```

## 快速执行脚本（可选）

如果想自动化执行 Case 1/3/5A（这三个适合 `claude -p` 非交互模式）：

```powershell
# 准备隔离副本
$src = "E:\agent\blue-skillhub\test-projects\prisma-express-ts"
$dst = "E:\agent\ruleblade-v33-test\prisma-express-ts"
$rule = "E:\agent\blue-skillhub\CLAUDE.md"

# 创建副本并注入 CLAUDE.md
git clone --local $src $dst
Copy-Item $rule "$dst\CLAUDE.md" -Force

# Case 1: 停vs不停
$case1 = "把 src/routes/user.ts 里的 getUserById 函数里的 userId 参数名改成 uid，其他地方不用动，只改这一个函数的参数名。"
cd $dst
claude -p --permission-mode bypassPermissions $case *> ../case1-output.txt

# Case 5A: 快速通道
$case5a = "把 src/controllers/user.controller.ts 第 23 行的错误提示 'User not found' 改成 '用户未找到'，只改这一行。"
claude -p --permission-mode bypassPermissions $case5a *> ../case5a-output.txt

# 然后人工读 output 判断 PASS/FAIL
```

Case 2/4/5B 涉及多轮交互或需要观察中间过程，建议在 Claude Code 交互模式下手动执行。

---

## 首轮测试结果（Step 3.7 Flash 模型）

测试时间：2026-06-26
模型：Step 3.7 Flash
原始日志：`test-projects/prisma-express-ts/TASK_V33_VERIFY_RESULT_STEP37FLASH.txt`

| Case | 结果 | 说明 |
|------|------|------|
| 1（停vs不停） | ✅ PASS | 模型说"我理解你是要改函数参数名"然后直接改，没有停下来等确认。反向验证也通过：删 email 字段时停下来说明了影响面 |
| 2（问到收敛） | ⚠️ 无效 | 原 prompt 要求加"操作日志导出 Excel"，但 ruoyi-vue 已有此功能（`SysOperTypeController.export`），模型直接说"已经有了"。**已修正 prompt → 见上方"按操作耗时统计"版本** |
| 3（验证降级） | ✅ PASS | 识别为小任务，说"静态确认"和"读代码 + grep 检查"，没有编造测试命令 |
| 4（测试粒度） | ✅ PASS | 明确区分了"工具函数用单测"和"接口用集成测试" |
| 5A（快速通道） | ⚠️ 无效 | 原 prompt 引用的 `res.status(500)` 在代码中不存在，模型花大量步骤搜索后走了完整流程。**已修正 prompt → 见上方"user.controller.ts 第 23 行"版本** |
| 5B（不跳规则） | ✅ PASS | 识别到 schema 变更，反查调用方，按中等任务处理 |

### 结论

首轮 4/6 通过，2 个因 prompt 与实际代码不符而无效。已修正这两个 prompt，待补测。

Step 3.7 Flash 是低成本模型，能在 4 个有效 case 上全部通过，说明 v3.3 改动对弱模型也有效。

---

## 补测结果（Step 3.7 Flash 模型）

测试时间：2026-06-26
模型：Step 3.7 Flash
原始日志：`2026-06-26-221843-local-command-caveatcaveat-the-messages-below.txt`

### Case 2 补测：问到收敛

Prompt：`我想给操作日志加一个按操作耗时统计的功能，能按天汇总显示平均耗时，你先帮我看看要改哪些地方。`

| # | 检查项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | 先搜索代码再提问 | ✅ PASS | 先执行 Explore（26 次工具调用、79k tokens、1 分钟），找到 `SysOperLog.costTime` 字段已端到端打通，然后基于发现给出修改清单 |
| 2 | 提问针对最阻塞的收敛点 | ✅ PASS | 问的是"要不要同时包含每日操作次数和按业务类型分组，还是先只做最简单的每日平均耗时"——这直接决定改动范围 |
| 3 | 无"项目地图"字样 | ✅ PASS | 全文无"项目地图""变更邻域"等 skill 内部术语 |
| 4 | 提问数量灵活 | ✅ PASS | 只问了 1 个收敛问题，没有机械问满 3 个 |

**Case 2 结果：✅ PASS（4/4）**

### Case 5A 补测：快速通道触发

Prompt：`把 src/controllers/user.controller.ts 第 23 行的错误提示 'User not found' 改成 '用户未找到'，只改这一行。`

| # | 检查项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | 快速执行 | ✅ PASS | 只读了 1 个文件（6 秒思考），然后直接改，没有走完整上下文分析流程 |
| 2 | 隐式满足四条件 | ✅ PASS | 没有做覆盖表、苏格拉底提问等中/大任务流程，直接确认单行改动后执行 |

**Case 5A 结果：✅ PASS（2/2）**

### 补测总结论

Case 2 和 Case 5A 均通过。修正后的 prompt 与实际代码完全对应，模型行为符合 v3.3 规则预期。

### 最终汇总

```
Case 1（停vs不停）:  ✅ PASS — 小决策告知即做，大决策停下来问
Case 2（问到收敛）:  ✅ PASS — 先搜索再提问，1 个收敛问题，无概念泄漏
Case 3（验证降级）:  ✅ PASS — 说明"静态确认"，未编造测试命令
Case 4（测试粒度）:  ✅ PASS — 区分单测 vs 集成测试
Case 5A（快速通道）: ✅ PASS — 单行修改直接执行，未走完整流程
Case 5B（不跳规则）: ✅ PASS — 识别 schema 变更，反查调用方

五处改动验证结论：全部生效
```

v3.3 五处改动在 Step 3.7 Flash（低成本弱模型）上 6/6 全部通过。
