# 真实项目回归测试

这套用例用于验证 `pathfinder` 和 `impact` 在真实代码库里的表现。它不替代现有 L0/L1/L2 测评，而是作为 RG2/RG3 的真实项目补充：项目固定、任务固定、评分口径固定，方便不同模型或不同 skill 版本复跑。

2026-07-03 起，本目录新增一层**真实交付验收**：不只看模型能否发现单点 bug，也看弱模型能否在 skill 约束下完成「只读摸底 → 影响分析 → Phase 4 文档 → Phase 5 隔离副本改代码 → 验证失败后修复 → 复验」这一整条链路。

2026-07-04 起，每个 case 新增 `scenario_type` 字段，标记它属于 8 类真实工程场景中的哪一类。这 8 类场景覆盖日常工程中最容易出错的变更模式：

| 场景类型 | 测什么 |
|---|---|
| `ui-rename` | UI 文案改名但有多个展示源，测“只改 label 不改 title”是否还会出现 |
| `field-rename` | 后端字段重命名，测是否漏 API 契约或持久化层 |
| `permission-add` | 权限逻辑新增，测是否找鉴权入口、路由守卫、后端校验 |
| `feature-removal` | 功能入口删除，测是否清引用、测入口、处理文档；交付题额外检查文件是否真的删除 |
| `enum-add` | 新增枚举值，测“先确认合法值再使用”是否发挥作用 |
| `config-migration` | 配置项迁移，测是否查配置入口和运行命令 |
| `non-git-pathfinder` | 非 Git 子目录项目，测是否误读父仓库信息 |
| `lazy-trap` | 故意诱导偷懒的需求，测 skill 能不能压住弱模型迎合用户的冲动；交付题额外检查代码和测试同步 |

Phase 5 交付 case 还包含 `acceptance` 块（标准答案）：必须改的文件、必须删除的文件、不能改的文件、验证命令、必须包含/不能包含的内容。这让判分从主观感觉变成客观对照。交付后先跑：

```powershell
python eval/real-projects/scripts/check_delivery.py --fixture <隔离副本目录> --scenario <场景ID>
```

默认只做 diff 和内容验收；需要实际执行 `acceptance.validators` 时再加 `--run-validators` 和 `--requirement-dir <需求目录>`。

## 目标

- 检查 `pathfinder` 能否在陌生项目里给出有证据的项目地图，而不是只复述目录名。
- 检查 `impact` 能否正确区分 light/full/negative，不遗漏 DB、API、权限、前端、导出、测试等影响面。
- 检查弱模型是否会跳过上下文、编造证据、误用父仓库 Git 信息、把危险写操作当成普通改动。
- 检查弱模型在 Phase 5 里能否留下完整执行记录、同步测试、真实运行验证，并在门禁失败后修到可交付。
- 给每轮真实 agent 复测留下可比较的记录。

## 目录

| 路径 | 内容 |
|---|---|
| `projects.json` | 5 个固定真实项目，包含仓库地址、固定 commit、选型理由和重点检查面 |
| `cases/` | 每个项目至少 4 个任务：pathfinder、impact-light、impact-full、negative；部分项目额外包含 Phase 5 交付题 |
| `delivery-matrix.json` | 真实交付验收矩阵：runner、S/M/L/NEG 场景、Phase 5 验收点和失败修复循环；含 8 类场景覆盖度检查 |
| `delivery-results.json` | 已跑场景的结构化结果台账：状态、证据、run record、阻塞原因 |
| `case-schema.json` | 真实项目 case 的本地结构说明 |
| `scorecard-template.md` | 人工评分模板 |
| `runbook.md` | 克隆、执行、归档、判分的复跑流程 |
| `scripts/validate_real_projects.py` | 轻量结构校验，防止项目和 case 不一致 |
| `scripts/check_delivery.py` | Phase 5 隔离副本交付验收，检查必改/禁改文件和内容残留 |

## 项目选择

| 项目 | 类型 | 阶段 | 主要考点 |
|---|---|---:|---|
| RuoYi | Java 后端 + Thymeleaf 管理页面 | 1 | Spring/MyBatis/Shiro、权限、用户、菜单、SQL、导出 |
| RealWorld Node/Prisma | Node API | 1 | Express/TypeScript/Prisma、认证、响应契约、迁移风险 |
| Full Stack FastAPI Template | Python 全栈 | 1 | FastAPI/SQLModel/Alembic、OpenAPI、前后端联动、Docker |
| React Admin Dashboard | 前端项目 | 2 | React/Vite/TypeScript、路由、状态、构建；避免凭空补 DB/API |
| Full Stack Starter Kit | monorepo/非 Git 模拟 | 2 | pnpm/Turborepo、shared types、API/DB/前端联动、子目录/无 Git 降级 |

阶段 1 先跑前三个项目，覆盖最容易出错的 DB/API/权限/前后端链路。阶段 2 再补纯前端和 monorepo/非 Git 场景。

## 怎么跑

1. 按 `runbook.md` 把真实项目克隆到仓库外的 fixture 目录。
2. 按 `delivery-matrix.json` 选择 runner 和场景。`gpt-5.4-mini` 子代理只用于只读/分析或无保护压力测试；Phase 5 正式交付优先用交互式或带写前门禁的 runner。
3. 给 runner 的 prompt 只放 `[评测环境]` 和 `[用户输入]`；验收答案、validator 命令、Step 规则和评分口径都留在 runbook/判分脚本里。
4. 复跑前清理隔离副本里的旧 `change-impact`，除非这次专门测试恢复、刷新地图或旧文档接续。
5. 把完整输出、diff、命令结果、失败修复过程和评分卡归档到 `eval/runs/real-projects/<date>-<runner>/`。
6. 运行结构校验：

```powershell
python eval/real-projects/scripts/validate_real_projects.py
```

真实项目代码不要提交进本仓库。本目录只保存评测定义、评分模板和复跑记录摘要。
