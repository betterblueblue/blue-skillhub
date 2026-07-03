# 真实项目回归测试

这套用例用于验证 `pathfinder` 和 `impact` 在真实代码库里的表现。它不替代现有 L0/L1/L2 测评，而是作为 RG2/RG3 的真实项目补充：项目固定、任务固定、评分口径固定，方便不同模型或不同 skill 版本复跑。

## 目标

- 检查 `pathfinder` 能否在陌生项目里给出有证据的项目地图，而不是只复述目录名。
- 检查 `impact` 能否正确区分 light/full/negative，不遗漏 DB、API、权限、前端、导出、测试等影响面。
- 检查弱模型是否会跳过上下文、编造证据、误用父仓库 Git 信息、把危险写操作当成普通改动。
- 给每轮真实 agent 复测留下可比较的记录。

## 目录

| 路径 | 内容 |
|---|---|
| `projects.json` | 5 个固定真实项目，包含仓库地址、固定 commit、选型理由和重点检查面 |
| `cases/` | 每个项目 4 个任务：pathfinder、impact-light、impact-full、negative |
| `case-schema.json` | 真实项目 case 的本地结构说明 |
| `scorecard-template.md` | 人工评分模板 |
| `runbook.md` | 克隆、执行、归档、判分的复跑流程 |
| `scripts/validate_real_projects.py` | 轻量结构校验，防止项目和 case 不一致 |

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
2. 对每个 case 原样使用 `prompt` 字段触发 `/pathfinder` 或 `/impact`。
3. 把完整输出、命令结果和评分卡归档到 `eval/runs/real-projects/<date>-<runner>/`。
4. 运行结构校验：

```powershell
python eval/real-projects/scripts/validate_real_projects.py
```

真实项目代码不要提交进本仓库。本目录只保存评测定义、评分模板和复跑记录摘要。
