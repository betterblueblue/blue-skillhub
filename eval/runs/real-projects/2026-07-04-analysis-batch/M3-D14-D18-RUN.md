# MiniMax M3 D14/D18 手动运行索引

用途：只给操作者定位文件和验分入口。不要把本文件内容发给 runner。

## D14 Java LOCKED 状态

复制这个 prompt 文件全文给 Claude Code CLI / MiniMax M3：

```text
eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d14-minimax-m3-claude-cli.txt
```

目标副本：

```text
E:\agent\real-project-fixtures\java-ruoyi-d14-m3-20260704-223205
```

跑完后判分方验分：

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture E:\agent\real-project-fixtures\java-ruoyi-d14-m3-20260704-223205 `
  --scenario D14-java-enum-analysis `
  --run-record E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-minimax-m3-delivery-d14\README.md
```

若存在标准 full 文档，再跑：

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py <requirement-dir> --mode full --repo-root E:\agent\real-project-fixtures\java-ruoyi-d14-m3-20260704-223205
```

## D18 monorepo 密码长度 lazy-trap

复制这个 prompt 文件全文给 Claude Code CLI / MiniMax M3：

```text
eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d18-minimax-m3-claude-cli.txt
```

目标副本：

```text
E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-m3-20260704-223205
```

跑完后判分方验分：

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-m3-20260704-223205 `
  --scenario D18-monorepo-lazy-trap-analysis `
  --run-record E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-minimax-m3-delivery-d18\README.md
```

若存在标准 full 文档，再跑：

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py <requirement-dir> --mode full --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-m3-20260704-223205
```
