# 数据目录定位 · 不写死路径

> 本 skill 拷到任何机器都要能找到数据。按下面的顺序找，找到第一个存在的就用。

## 定位顺序

1. **环境变量** `WORD_MIRROR_HOME`（用户显式指定，最优先；旧名 `DIGITAL_SELF_HOME` 仍兼容）
2. `~/.wordmirror/`（产品化标准位置：`~/.wordmirror/data/`；旧目录 `~/.digital-self/` 仍兼容）
3. 本 skill 目录往上两级：`../../data/`（开发实例的布局：skill 在 `<仓库>/skill/wordmirror/`，数据在 `<仓库>/data/`）

## 验证找对了

目标目录下应有这些文件（至少 corpus_dedup.jsonl 一个）：

```
corpus_dedup.jsonl     # 主力：全部原话
ai_messages.jsonl      # AI 回复
sessions.jsonl         # 会话卡
user_writebacks.jsonl  # 写回
stats_wordfreq.json    # 口头禅频率（脚本算的）
stalled_topics.json    # 搁置主题
profile/portrait.md    # 我是谁（初始化生成，见 init-protocol.md）
profile/habits.md      # 跟我干活的规矩（同上）
```

一个都没有 → 数据不存在或还没提取过：读 `references/ingest-protocol.md`，先跑 ingest。

## Windows / macOS / Linux 路径差异

- `~` = 用户主目录（`C:\Users\<名>` 或 `/home/<名>` 或 `/Users/<名>`）
- 路径分隔符：脚本已兼容，grep 时注意 Windows 是 `\`
- skill 目录自身：agent 通常知道（加载路径），用相对路径 `../../data/` 最稳
