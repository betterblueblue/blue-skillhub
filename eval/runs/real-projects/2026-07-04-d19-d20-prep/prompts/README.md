# D19 / D20 启动 Prompt

直接复制对应 `.txt` 全文粘贴到 runner 入口即可。

| 文件 | 场景 | Runner | 用法 |
|---|---|---|---|
| `d19-gpt-54-mini-subagent.txt` | D19 | Codex 子代理 `gpt-5.4-mini` | 在 blue-skillhub 主会话 spawn 子代理，粘贴全文 |
| `d19-minimax-m3-claude-cli.txt` | D19 | Claude Code CLI + MiniMax M3 | `cd` 到 node minimax 副本后启动 CLI，粘贴全文 |
| `d20-gpt-54-mini-subagent.txt` | D20 | Codex 子代理 `gpt-5.4-mini` | 同上 |
| `d20-minimax-m3-claude-cli.txt` | D20 | Claude Code CLI + MiniMax M3 | `cd` 到 python minimax 副本后启动 CLI，粘贴全文 |

## 副本路径

- D19 gpt-54-mini: `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-gpt54mini-d19-20260704`
- D19 minimax-m3: `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-minimax-m3-d19-20260704`
- D20 gpt-54-mini: `E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-20260704`
- D20 minimax-m3: `E:\agent\real-project-fixtures-delivery\python-fastapi-template-minimax-m3-d20-20260704`

## 操作者职责

模型每请求 `确认 Step N` 时，原话回复 `确认 Step N`；Step 范围过宽则回复 `拆分 Step N`。不要把初始 prompt 当成任何 Step 的预授权。

## 跑完验收

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture <隔离副本> `
  --scenario D19-node-tags-removal-phase5 `   # 或 D20-python-title-required-lazy-phase5
  --run-validators `
  --requirement-dir <change-impact 下的需求目录>
```
