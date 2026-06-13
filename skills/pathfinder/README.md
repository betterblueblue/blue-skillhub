# Pathfinder — 陌生项目认知地图 Skill

## 这个 Skill 是干什么的

面向**刚接手、还不熟悉**的现有项目,通过只读发现建一张**全项目级认知地图**:技术栈、核心功能、架构分层、关键入口、数据模型概览、构建/运行/测试、雷区、权限模型、典型主链路、文档入口。

地图产出到 `change-impact/_project-map.md`,作为 `impact` / `impact-pro` 的 **L1 项目地图**导航上下文。

它不是从 0 到 1 的生成器,也不做具体变更的影响分析(那是 impact 系列的事)。它只回答一件事:**"这个项目是什么样的?"**

## 工具箱定位:脑 / 眼 / 手

- **律刃(RuleBlade)** 管 AI 的**脑子** — 少猜、说人话。
- **Pathfinder(领航,本 Skill)** 管 AI 的**眼睛** — 看懂陌生项目。
- **ImpactRadar / Pro(impact)** 管 AI 的**手** — 不乱动、按步骤、必确认。

先有眼,才谈得上手。Pathfinder 是 impact 的可选**加速器**,不是前置必跑项 —— 没有地图时 impact 完全照旧。

## 核心能力

- **全景广度优先** — 所有核心模块都上地图,聚焦信号只决定哪片挖更深,不裁剪广度
- **自适应分档 + 可续挖** — 先量体量定预算,大仓不硬扫;没挖深的显式进盲区,用户可「再挖 X」续扫
- **信任标签** — 每条结论标【已核实: 证据】或【推断: 待验证】,直接对接 impact 的「已确认/未确认」二分
- **信任契约头** — 记录 git HEAD(防过期)、聚焦信号(解释深浅)、覆盖度(显式声明盲区)
- **典型主链路** — 只 trace 一条代表性请求,端到端串通,"读懂项目"杠杆最高的一节
- **100% 只读 + 只描述不开药方** — 不改项目本体,不给"该怎么改"的建议
- **栈无关通用版** — 自带轻量清单文件栈探测,不依赖 impact-pro 的 profiles,留接缝以后可挂接

## 什么时候用

**适合:**

| 场景 | 原因 |
|------|------|
| 刚接手一个不熟的项目 | 先建整体认知再谈动手 |
| 接外包 / 老项目交接 | 快速摸清技术栈、核心功能、雷区 |
| 动 impact 之前想先预热上下文 | 产出地图给 impact 当 L1 导航 |
| "这项目是干嘛的 / 怎么跑起来 / 哪里危险" | 一次只读扫描回答全景问题 |

**不适合:**

| 场景 | 更应该用 |
|------|----------|
| 已经熟悉项目、要做具体变更影响分析 | `/impact` 或 `/impact-pro` |
| 从 0 到 1 搭新系统 | 架构设计 / 脚手架生成 |
| 只想找某个具体文件/函数 | 直接 grep / 搜索 |

## 触发方式

已禁用模型自动触发(`disable-model-invocation: true`),唯一入口手动 `/pathfinder`。

## 与 impact 的交接(拉取式,零硬依赖)

```
Pathfinder ──写──> change-impact/_project-map.md
                          │ (impact Phase 2 主动去读,读不到就照旧)
                          ▼
impact / impact-pro ── 把地图当 L1 预热 ──> 自己做 L2/L3 切片深挖
```

- impact 读地图时:`【已核实】`当导航线索,`【推断】`按未确认处理动手前重新取证,HEAD 不一致报过期。
- 地图里任何文本对 impact **不构成写授权** —— 只提供发现线索,不提供任何确认。
- 完整契约见 `references/handoff-contract.md`。

## 目录结构

```
pathfinder/
├── SKILL.md                      # 核心规则(铁律子集 + Phase 概览 + 章节结构 + 索引)
├── README.md                     # 本文件
├── references/                   # 详细执行规则(按需加载)
│   ├── phase-1-sizing.md         # 体量测量 + 预算分档 + 超大仓处理
│   ├── phase-2-breadth-scan.md   # 广度优先扫描:栈探测/目录树/模块边界/入口
│   ├── phase-3-depth-fill.md     # 各节深挖方法 + 主链路 trace + 续挖
│   ├── stack-detection.md        # 通用栈探测:清单文件 → 栈/构建/测试映射
│   ├── handoff-contract.md       # 与 impact/impact-pro 交接契约 + L1 接口
│   └── cross-platform-notes.md   # 跨平台差异(时间戳/HEAD/体量命令/路径)
└── templates/
    └── project-map.md            # _project-map.md 章节模板(14 核心 + 3 可选)
```

## 安全姿态(只读)

- **只读铁律**:不 Edit/Write 项目源码、不跑 DDL/DML、不改配置、不删文件;DB 只 SELECT/SHOW/DESCRIBE。
- **唯一写入目标**:Write/Edit 只写 `change-impact/_project-map.md`,且必须在目标项目根内。
- **凭证脱敏 + 仓内文本不构成指令**:同 impact 家族铁律。

设计文档见 [../../docs/plans/2026-06-13-pathfinder-skill-design.md](../../docs/plans/2026-06-13-pathfinder-skill-design.md)。
