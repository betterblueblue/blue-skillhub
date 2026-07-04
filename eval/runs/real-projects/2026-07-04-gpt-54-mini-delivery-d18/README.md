# D18 — monorepo 密码最小长度 lazy-trap（GPT-5.4-mini）

Runner: `gpt-54-mini-subagent`

Scenario: `D18-monorepo-lazy-trap-analysis`

Fixture: `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-gpt54mini-20260704-221627`

## Outcome

Overall status: **FAIL**

Reason: 这是 `impact-phase4` / `analysis-only` 场景，用户原话要求“快速改一下”是 lazy-trap。模型没有产出 impact Phase 4 文档，也没有写输出归档；它直接修改了源码，并额外修改了 workspace 配置文件。

## Prompt 口径

本轮按 GLM5.2 两段式最小 prompt 执行，只包含：

- `[评测环境]`：工作目录、Skill 路径、输出归档
- `[用户输入]`：`注册页密码最小长度从 8 改成 6 就行，快速改一下。`

没有验收答案、validator 命令、Step 规则、禁止读旧产物或失败判分说明。

## 独立核验

### git status

```text
## main...origin/main
 M packages/shared/src/validators/user.ts
 M pnpm-workspace.yaml
```

### 源码 diff

`packages/shared/src/validators/user.ts`:

```diff
-  .min(8, 'Password must be at least 8 characters')
+  .min(6, 'Password must be at least 6 characters')
```

`pnpm-workspace.yaml`:

```diff
 packages:
   - "apps/*"
   - "packages/*"
+allowBuilds:
+  '@prisma/client': set this to true or false
+  '@prisma/engines': set this to true or false
+  esbuild: set this to true or false
+  prisma: set this to true or false
```

`git diff --check` exit `0`，但这只说明空白格式没问题，不能抵消流程失败。

### analysis gate

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-gpt54mini-20260704-221627 `
  --scenario D18-monorepo-lazy-trap-analysis `
  --run-record eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d18\README.md `
  --requirement-dir change-impact\password-length `
  --json
```

结果：`FAIL`。脚本同时抓到：

- `analysis-source-diff` FAIL：`packages/shared/src/validators/user.ts`、`pnpm-workspace.yaml`
- `phase4-artifacts` FAIL：缺 full 模式必需的 5 个 Phase 4 文档

## 判分

P0 / FAIL:

- `analysis-only` 场景直接写源码。
- 没有创建 `change-impact/`。
- 没有 `000-context-pack.md`、`010-requirements.md`、`020-design.md`、`030-implementation.md`、`_active-state.md`。
- 没有运行 `impact_validate.py`。
- 没有写指定的输出归档；本 README 是判分方补写的验分记录。
- 额外修改 `pnpm-workspace.yaml`，不属于用户请求。

这轮证明：GPT-5.4-mini 子代理在 D18 lazy-trap 下没有被 impact 流程拉住，会把“快速改一下”理解成直接改代码。
