# D1 Prompt 文件

三个 runner 共用同一个任务 prompt（case 原文），区别只在 runner 信息和输出路径。

| 文件 | Runner | 模型 |
|---|---|---|
| d1-deepseek-v4-flash.txt | deepseek-v4-flash | DeepSeek V4 Flash |
| d1-minimax-m3-claude-cli.txt | minimax-m3-claude-cli | MiniMax M3 |
| d1-composer-25fast-subagent.txt | composer-25fast-subagent | Composer 2.5 Fast |

运行前确认：
1. RuoYi fixture 存在且 commit 正确（`0d42679bc25576286bf34a156002716ed7de5739`）
2. 旧 `change-impact/` 已清理
3. 全新会话（模型对其他场景无记忆）
