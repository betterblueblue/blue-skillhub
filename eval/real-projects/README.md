# 真实项目回归测试

这套用例用于检查 Pathfinder 和 ImpactRadar 在真实代码库中的表现。测试项目、任务和评分方法保持不变，便于比较不同模型或不同 Skill 版本。它是 L0/L1/L2 的补充，不替代已有测评。

从 2026-07-03 开始，测试范围扩展到完整交付过程。除了检查模型能否发现单个问题，还要看它能否完成只读摸底、影响分析、Phase 4 文档、在隔离副本中修改代码、处理校验失败并重新验证。

从 2026-07-04 开始，每个用例增加 `scenario_type` 字段，用来标记它属于哪一类工程场景。当前共 8 类：

| 场景类型 | 测什么 |
|---|---|
| `ui-rename` | UI 文案改名但有多个展示源，测“只改 label 不改 title”是否还会出现 |
| `field-rename` | 后端字段重命名，测是否漏 API 契约或持久化层 |
| `permission-add` | 权限逻辑新增，测是否找鉴权入口、路由守卫、后端校验 |
| `feature-removal` | 功能入口删除，检查是否清理引用和测试入口，并同步更新文档；交付题还会检查文件是否真的删除 |
| `enum-add` | 新增枚举值，检查模型是否先确认合法值再使用 |
| `config-migration` | 配置项迁移，测是否查配置入口和运行命令 |
| `non-git-pathfinder` | 非 Git 子目录项目，测是否误读父仓库信息 |
| `lazy-trap` | 用容易诱发草率修改的需求，检查模型是否会跳过流程；交付题还会核对代码和测试是否同步 |

Phase 5 交付用例还包含 `acceptance` 验收条件：必须修改、必须删除和禁止修改的文件，验证命令，以及必须出现或不能残留的内容。完成改动后先运行：

```powershell
python eval/real-projects/scripts/check_delivery.py --fixture <隔离副本目录> --scenario <场景ID>
```

默认只检查实际改动和文件内容。需要运行 `acceptance.validators` 中的命令时，再加上 `--run-validators` 和 `--requirement-dir <需求目录>`。

## 目标

- 检查 Pathfinder 能否给陌生项目生成有证据的项目地图，而不只是复述目录名。
- 检查 ImpactRadar 能否正确选择 `light`、`full` 或拦截流程，并覆盖 DB、API、权限、前端、导出和测试等相关部分。
- 检查模型是否会跳过上下文、编造证据、误用父目录仓库的 Git 信息，或把危险写操作当成普通改动。
- 检查 Phase 5 是否留下完整执行记录、同步更新测试并实际运行验证；检查失败后是否能根据错误修正。
- 为每次复跑保留可以比较的结果。

## 目录

| 路径 | 内容 |
|---|---|
| `projects.json` | 5 个固定项目的仓库地址、固定 commit、选择理由和重点检查内容 |
| `cases/` | 每个项目的 Pathfinder、ImpactRadar `light` / `full`、负向拦截和部分 Phase 5 交付任务 |
| `delivery-matrix.json` | 执行模型、任务规模、Phase 5 验收点和失败后修正要求 |
| `delivery-results.json` | 已运行场景的状态、证据、运行记录和阻塞原因 |
| `case-schema.json` | 真实项目用例的本地格式说明 |
| `scorecard-template.md` | 人工评分模板 |
| `runbook.md` | 准备项目、执行、归档和评分的完整步骤 |
| `scripts/validate_real_projects.py` | 检查项目、用例和矩阵之间是否一致 |
| `scripts/check_delivery.py` | 在 Phase 5 隔离副本中检查必改文件、禁改文件和残留内容 |

## 项目选择

| 项目 | 类型 | 阶段 | 主要考点 |
|---|---|---:|---|
| RuoYi | Java 后端 + Thymeleaf 管理页面 | 1 | Spring/MyBatis/Shiro、权限、用户、菜单、SQL、导出 |
| RealWorld Node/Prisma | Node API | 1 | Express/TypeScript/Prisma、认证、响应契约、迁移风险 |
| Full Stack FastAPI Template | Python 全栈 | 1 | FastAPI/SQLModel/Alembic、OpenAPI、前后端联动、Docker |
| React Admin Dashboard | 前端项目 | 2 | React/Vite/TypeScript、路由、状态、构建；避免凭空补 DB/API |
| Full Stack Starter Kit | monorepo/非 Git 模拟 | 2 | pnpm/Turborepo、shared types、API/DB/前端联动、子目录/无 Git 降级 |

阶段 1 先运行前三个项目，覆盖容易出错的 DB、API、权限和前后端协作。阶段 2 再补纯前端和 monorepo/非 Git 场景。

## 怎么跑

1. 按 `runbook.md` 把原始测试项目准备在仓库外。
2. 每个模型、每个场景都从原始项目复制一份新的物理副本。不能只删除旧 `change-impact/` 后复用同一个目录；测试恢复或地图刷新时，才可以在同一次场景内延续已有副本。
3. 按 `delivery-matrix.json` 选择执行模型和场景。`gpt-5.4-mini` 子代理只用于只读分析或没有写入保护的压力测试；Phase 5 正式交付优先使用交互式模型，或启用了写入前检查的执行环境。
4. 发给执行模型的 Prompt 只包含 `[评测环境]` 和 `[用户输入]`。验收答案、校验命令、Step 规则和评分方法只保存在运行手册和评分脚本中。
5. 把完整输出、实际改动、命令结果、失败后的修正过程和评分卡归档到 `eval/runs/real-projects/<date>-<执行模型>/`。
6. 运行结构检查：

```powershell
python eval/real-projects/scripts/validate_real_projects.py
```

不要把测试项目源码提交到本仓库。本目录只保存测试定义、评分模板和复跑结果摘要。
