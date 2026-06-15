<!-- version: 1.0, last_updated: 2026-06-15, skill_commit: <TODO> -->
# Phase 2: 广度优先扫描

> 本文件含 Phase 2 完整规则。目标:在 Phase 1 预算内做一遍**浅而全**的扫描,把项目广度铺满,不在任何单点深挖(深挖留给 Phase 3)。

## 原则:先广后深

- Phase 2 只建**骨架**:有哪些模块、各自大概干什么、从哪进入。
- 每个模块**只看够判断职责的最少内容**(目录名 + 1-2 个代表文件的签名/导出,不细读实现)。
- 广度必须覆盖**所有核心模块**,不因聚焦信号而跳过任何大块。

## Step 2.1: 轻量栈探测

读清单文件识别技术栈、构建工具、测试入口。**完整映射表见 `stack-detection.md`。**

- 找到清单(`package.json`/`pom.xml`/`go.mod`/`requirements.txt`/`pyproject.toml`/`*.csproj`/`Gemfile`/`composer.json` 等)→ 技术栈节标【已核实】。
- monorepo / 多栈 → 列出各子项目栈 + 目录边界,**不压成单栈**。
- 找不到任何清单 → 降级:按文件扩展名 + 目录名启发式推断,技术栈节标【推断】+ 声明"置信低"。

## Step 2.1.5: 可选结构索引探测

若运行时存在只读 code graph / repo-map MCP,按 `../code-graph-adapters/generic-mcp.md` 先取项目概览、入口、依赖边、hubs 或 bounded tree,用于辅助广度扫描。

- 只把结构索引当**候选集**:任何写入地图且标【已核实】的事实仍需 Read/Grep 核证。
- 若索引不可用、过期、截断、权限失败、返回无行号/无路径,标 `code_graph: unavailable/failed/degraded` 并降级普通 Glob/Grep/Read。
- 若工具需要在目标项目内创建/更新 `.codegraph/`、`.repomapper/`、`.cache/` 等索引目录,不得执行;Pathfinder 唯一写入目标仍是 `change-impact/_project-map.md`。
- 如果结果带 `total/truncated/limit/offset`,必须记录覆盖范围;不能把截断结果写成全项目覆盖。

## Step 2.2: 目录树扫描

按档位深度扫目录(小仓全展开 / 大仓到 2 层 / 超大仓仅顶层),为每个顶层(或聚焦区)目录记一行职责推断:

```
src/api/        【推断: 目录名 → HTTP 接口层】
src/services/   【推断: → 业务逻辑层】
src/models/     【已核实: 含 User.ts/Order.ts → 数据模型层】
```

目录职责能从代码证据确认的标【已核实】,只能从命名猜的标【推断】。

**目录内容验证(防事实错误)**:对任何声称"为空"/"无内容"/"仅含 X"的目录,必须用 Glob 或 Read 做一次实际验证——声称"空"但实际有文件 = 事实错误,等同于编造。正确做法:
- 不确定的目录标【推断: 待验证】,不要声称"空"
- 声称含特定文件的,用 Glob 确认后再标【已核实】
- 目录下文件数量多到无法逐个确认时,写"含 N 个文件,未逐一确认"而非"仅含 X"

## Step 2.3: 模块边界识别

判断模块如何切分:

- 按目录(`modules/`、`packages/`、`apps/`、`cmd/`)
- 按分层(`controller`/`service`/`repository`/`model`)
- 按领域(`user/`、`order/`、`payment/`)

记录:模块名、目录、推断职责、模块间明显的依赖方向(若一眼可见)。

## Step 2.4: 关键入口扫描

找程序从哪开始执行(广度,先列全不深挖):

| 类型 | 找什么 |
|------|--------|
| 进程入口 | `main()` / `index.*` / `app.*` / `Application.java` / `Program.cs` / `manage.py` |
| HTTP 路由 | 路由注册文件 / 注解扫描(`@RestController`/`@app.route`/`router.*`) |
| CLI | `cmd/` / `bin/` / argparse/cobra/commander 入口 |
| 定时任务 | `@Scheduled` / cron / worker / job 目录 |
| 消息消费 | MQ consumer / listener / subscriber |

## 相关性分级(沿用 impact 约定)

广度扫描时给模块/文件标相关性,辅助 Phase 3 决定深挖谁:

| 分值 | 含义 |
|------|------|
| 3 | 核心模块,Phase 3 必深挖(尤其落在聚焦区的) |
| 2 | 重要支撑模块,预算允许则深挖 |
| 1 | 背景 / 工具 / 配置,广度提及即可 |
| 0 | 噪音(依赖、构建产物、生成物),排除 |

## Phase 2 输出

广度扫描结束,先在对话里输出骨架草案(不写文件):

```text
技术栈: [已核实/推断]
结构索引: [used/unavailable/failed/degraded,若 used 写工具与覆盖范围]
模块地图: [N 个模块,各一行职责]
关键入口: [列表]
聚焦区候选深挖: [按聚焦信号 + 相关性 3 选出的模块]
```

确认骨架方向后进入 Phase 3 深挖。

## 维护注意

- 本文件是栈无关骨架。栈专属发现细节在 `stack-detection.md`,不在此堆砌。
- 引用计数异常大(单模式 > 20 命中)时,先验证依赖真实存在再抽样核实,不全纳也不全弃(同 impact 规则)。
