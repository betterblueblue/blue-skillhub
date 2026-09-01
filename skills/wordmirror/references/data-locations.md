# 数据目录定位 · 不写死路径

> 本 skill 拷到任何机器都要能找到数据。你（AI）自己按下面的顺序找，找到第一个存在的就用。

## 定位顺序

1. **环境变量** `WORD_MIRROR_HOME`（用户显式指定，最优先；旧名 `DIGITAL_SELF_HOME` 仍兼容）
2. **bind 指针** `~/.wordmirror/bind.json`（`python ds.py bind <数据目录>` 写入）——数据在别处时接上
3. `~/.wordmirror/`（产品化标准位置：`~/.wordmirror/data/`；旧目录 `~/.digital-self/` 仍兼容）
4. 仓库布局：从 skill 目录向上逐级找祖先目录里有 `data/corpus_dedup.jsonl`（或 `corpus_all.jsonl`）的——数据在 skill 目录内时自动生效
5. 都没有 → 默认 `~/.wordmirror/`，首次写入时自动创建（单装用户数据不再撒到奇怪的地方）

## 单装用户推荐接法（bind）

skill 拷进某个 agent 的 skills 目录后，如果完整数据仓库在别处（比如另一块盘），一条命令接上：

```bash
python <skill目录>/scripts/ds.py bind E:\path\to\digital-self
```

之后所有命令（ingest / vec / monthly / promise / wb / open）都用绑定的数据；查旧话、看数据这种活你直接读绑定位置的文件就行。解绑：`ds.py bind --clear`。

**项目层（欠账/写回专用）**：当前目录 `.wordmirror/promises.jsonl`——在哪个目录干活，账记哪，随项目走。⚠️ **账本存的是你的原话、可能含隐私，默认别进 git**——项目 `.gitignore` 加一行 `.wordmirror/`；真想跟着项目走，先把内容过一遍再手动挑出来。全局层和项目层开场都查；`ds.py promise` 也扫两层。

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
