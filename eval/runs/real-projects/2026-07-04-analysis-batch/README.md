# 分析题批次 Prompt（D3 + D8-D18）

> 生成日期：2026-07-04
> 目的：为 D3 重跑和 D8/D13-D18 分析题批次准备去毒化 prompt 文件

## 设计原则

**prompt 只放两样东西：**

1. `[评测环境]` — runner 需要的最小基础设施（工作目录、skill 路径、输出归档路径）。这些是真实用户不需要写的，但 runner 环境必须知道。
2. `[用户输入]` — 真实用户会打的那句话，从 case JSON 一字不改提取。

**prompt 里不放的：**

- "你是本轮真实交付评测 runner" — 角色设定是 runner harness 的职责，不是用户输入
- "遵循 SKILL.md 及其模板" — skill 激活后本身就执行 SKILL.md，同义反复
- "运行 impact_validate.py 验证" — SKILL.md 第 231-243 行已强制要求
- "验证命令必须记录真实输出、退出码" — SKILL.md 规则 #14 已覆盖
- "impact_validate.py 失败时按错误修复后重跑" — SKILL.md 第 239 行已写
- "这是 analysis-only 场景" — case prompt 本身已说"先不要写代码"
- "全程只读" — pathfinder skill 本身就是只读的

**为什么去掉这些：** 如果 prompt 替 skill 说了该做的事，评测就变成测"prompt 够不够详细"，而不是测"skill 本身能不能引导模型做对"。真实用户不会写这些执行规则，它们应该由 skill 自己管。

## 文件清单

| 文件 | 场景 | Runner | Fixture | Skill |
|------|------|--------|---------|-------|
| `d3-minimax-m3-claude-cli.txt` | D3-python-item-phase4 (L) | MiniMax M3 | python-fastapi-template | impact |
| `d8-deepseek-v4-flash.txt` | D8-node-login-message-analysis (S) | DeepSeek V4 Flash | node-realworld-prisma | impact |
| `d8-composer-25fast-subagent.txt` | D8-node-login-message-analysis (S) | Composer 2.5 Fast | node-realworld-prisma | impact |
| `d9-gpt-54-mini-subagent.txt` | D9-monorepo-organization-phase4 (L) | GPT-5.4 Mini | monorepo-full-stack-starter-d9-gpt54mini | impact |
| `d9-minimax-m3-claude-cli.txt` | D9-monorepo-organization-phase4 (L) | MiniMax M3 | monorepo-full-stack-starter-d9-m3 | impact |
| `d11-gpt-54-mini-subagent.txt` | D11-java-external-id-analysis (L) | GPT-5.4 Mini | java-ruoyi | impact |
| `d11-minimax-m3-claude-cli.txt` | D11-java-external-id-analysis (L) | MiniMax M3 | java-ruoyi | impact |
| `d12-gpt-54-mini-subagent.txt` | D12-monorepo-pathfinder-map (M) | GPT-5.4 Mini | monorepo-full-stack-starter + non-git copy | pathfinder |
| `d12-minimax-m3-claude-cli.txt` | D12-monorepo-pathfinder-map (M) | MiniMax M3 | monorepo-full-stack-starter + non-git copy | pathfinder |
| `d13-deepseek-v4-flash.txt` | D13-java-permission-analysis (M) | DeepSeek V4 Flash | java-ruoyi | impact |
| `d13-minimax-m3-claude-cli.txt` | D13-java-permission-analysis (M) | MiniMax M3 | java-ruoyi | impact |
| `d13-composer-25fast-subagent.txt` | D13-java-permission-analysis (M) | Composer 2.5 Fast | java-ruoyi | impact |
| `d14-minimax-m3-claude-cli.txt` | D14-java-enum-analysis (M) | MiniMax M3 | java-ruoyi-d14-m3-20260704-223205 | impact |
| `d14-composer-25fast-subagent.txt` | D14-java-enum-analysis (M) | Composer 2.5 Fast | java-ruoyi-d14-composer-20260704-223205 | impact |
| `d15-deepseek-v4-flash.txt` | D15-node-feature-removal-analysis (L) | DeepSeek V4 Flash | node-realworld-prisma | impact |
| `d15-minimax-m3-claude-cli.txt` | D15-node-feature-removal-analysis (L) | MiniMax M3 | node-realworld-prisma | impact |
| `d15-composer-25fast-subagent.txt` | D15-node-feature-removal-analysis (L) | Composer 2.5 Fast | node-realworld-prisma | impact |
| `d16-minimax-m3-claude-cli.txt` | D16-python-config-migration-analysis (M) | MiniMax M3 | python-fastapi-template | impact |
| `d16-deepseek-v4-flash.txt` | D16-python-config-migration-analysis (M) | DeepSeek V4 Flash | python-fastapi-template | impact |
| `d16-composer-25fast-subagent.txt` | D16-python-config-migration-analysis (M) | Composer 2.5 Fast | python-fastapi-template | impact |
| `d17-deepseek-v4-flash.txt` | D17-python-lazy-trap-analysis (M) | DeepSeek V4 Flash | python-fastapi-template | impact |
| `d17-composer-25fast-subagent.txt` | D17-python-lazy-trap-analysis (M) | Composer 2.5 Fast | python-fastapi-template | impact |
| `d18-minimax-m3-claude-cli.txt` | D18-monorepo-lazy-trap-analysis (M) | MiniMax M3 | monorepo-full-stack-starter-d18-m3-20260704-223205 | impact |
| `d18-composer-25fast-subagent.txt` | D18-monorepo-lazy-trap-analysis (M) | Composer 2.5 Fast | monorepo-full-stack-starter-d18-composer-20260704-223205 | impact |

共 24 个 prompt 文件，覆盖 10 个场景 × 不同 runner 组合。

## Runner 替换说明

- `gpt-54-mini-subagent` → `deepseek-v4-flash`（GPT-5.4-mini 调不通，替换为 DeepSeek V4 Flash）
- `minimax-m3-claude-cli` 保持不变
- `composer-25fast-subagent` 保持不变

## 验收标准

每个 run 完成后检查：

1. **skill 自主执行**：impact_validate.py 是否被 skill 引导运行（不是 prompt 要求的）
2. **判档正确**：对照 delivery-matrix.json 中 success_target 检查
3. **门禁不跳**：validator FAIL 时是否修复重跑
4. **只读边界**：read-only-original 场景下 git diff 应为空（change-impact/ 目录除外）
5. **输出真实**：README 中的 validator 结果须附原始输出和退出码

D14/D18 这类 `impact-phase4` 场景跑完后，还要跑 analysis gate：

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture <对应 fixture> `
  --scenario <D14-java-enum-analysis 或 D18-monorepo-lazy-trap-analysis> `
  --run-record <对应 README.md> `
  --requirement-dir <实际 change-impact 需求目录>
```

它会检查：除 `change-impact/**` 外无源码 diff、run README 存在、Phase 4 full 文档齐全。

## 判分要点

| 场景 | 核心考察点 | 典型失败信号 |
|------|-----------|-------------|
| D3 | L 级 full 判档 + Alembic/OpenAPI 覆盖 | 只改前端状态不处理后端存储 |
| D8 | S 级 light 判档 + 不升级为 DB 变更 | 把文案改动升级成 Prisma schema 变更 |
| D9 | L 级 monorepo 字段新增 + shared types/API/Prisma/前端 | 跳过 shared package 或从子目录规划验证 |
| D11 | L 级 RuoYi 字段新增 + DB/实体/Mapper/页面/导出 | 漏导出或未确认字段约束就直接给 DDL |
| D12 | Pathfinder Git 与非 Git 双运行对比 | 非 Git 副本仍输出父仓库 HEAD/branch/hotspots |
| D13 | 权限链路覆盖 + 前后端同时校验 | 只改前端按钮就声明完成 |
| D14 | 改前回看枚举定义 + 登录校验 + 导出/字典 | 不查现有枚举定义就直接使用新值 |
| D15 | 删除链路覆盖 + API 契约兼容期 | 只删路由就声明完成 |
| D16 | 配置迁移覆盖 + docker-compose/.env/CI | 只改 config.py 就声明完成 |
| D17 | 不被"快速改一下"误导 + 跨前后端 | 被快改误导跳过影响分析 |
| D18 | 不被"快速改一下"误导 + 跨包 | 只改一个包就声明完成 |
