# 写回协议 · "记住这个"

> 触发场景：用户在对话中确认了值得长期记住的新事实——新决定、状态变化、偏好澄清、对旧说法的更正。
> 核心原则：**只写用户确认过的事实，不写你的推断**。写回是 append-only（追加，不改旧数据）。

## 什么值得写回

✅ 写：
- 用户明确说"我决定了X""以后就这样""这件事完了/黄了"
- 用户纠正你情况里的旧信息（"不是 22 万，是 20 万"）
- 状态变化（"offer 到了""那个项目弃了"）

❌ 不写：
- 你自己的推断和总结
- 用户随口的情绪（"烦死了"不是事实）
- 闲聊、待确认的想法（"我在想要不要X"）

拿不准就问一句："这个要记下来吗？"——用户说"要"再写。

## 怎么写（必须走命令，不许手写文件）

**硬门槛：写回和欠账记账一律跑命令，禁止直接编辑 jsonl 文件。** 命令保证格式永远正确、坏账本永远进不了写入路径（手写没有这个保证——模型换个宿主就可能写出坏行）。命令不可用（找不到脚本/Python）才允许按下面格式手写，且写完跑 `wm.py promise` 验证能读出来。

```bash
python <skill目录>/scripts/wm.py wb add "事实内容" --topic 主题 --ref "用户原话" [--agent 工具名]
# 欠账本见下节：promise add / promise done
```

手写兜底格式（定位数据目录见 `references/data-locations.md`，往 `user_writebacks.jsonl` **末尾追加一行**）：

```json
{"date": "YYYY-MM-DD", "source": "当前agent名", "topic": "主题（如 jobsearch/项目名）", "msg": "事实内容，用用户的说法", "ref": "依据或用户原话"}
```

示例（日期换成当天，`YYYY-MM-DD`）：
```json
{"date": "2026-08-30", "source": "zcode", "topic": "project/demo", "msg": "demo 项目 7/19 提交，无回复，确认关闭等待", "ref": "用户原话「没有消息」"}
```

## 写完之后

1. 告诉用户"记下了：XXX"——让用户知道写了什么，可当场纠正
2. 不用马上重新整理；下次 ingest 时会合并进你的情况
3. 写回文件损坏（不是合法 JSON 行）→ 停下来报告，不要静默修复

## 承诺记账（说要做的事）

> 用户说"我要做X""下周去Y"——这算事实（他亲口说的要做），记进欠账本。
> "我在想要不要做"是想法，不记。拿不准就问一句。

**记在哪（两层账本）**：你在哪个目录干活，账就记哪——当前目录 `.wordmirror/promises.jsonl`（目录自动创建）；在仓库实例目录里干活则记全局 `data/promises.jsonl`。开场检查两层都看（见 SKILL.md 第一步）。

**一律走命令**（格式保证 + 坏账本拦截都在命令里）：

```bash
python <skill目录>/scripts/wm.py promise add 要做的事 [--agent 工具名]  # 记一笔（open）
python <skill目录>/scripts/wm.py promise done 关键词           # 划掉（closed）
python <skill目录>/scripts/wm.py promise drop 关键词           # 不做了（dropped）
python <skill目录>/scripts/wm.py promise                       # 看两层欠账
```

命令不可用时手写兜底——对应账本末尾追加一行（文件不存在就创建）：

```json
{"date": "YYYY-MM-DD", "text": "要做的事，用用户的原话", "status": "open", "agent": "当前agent名"}
```

划掉（closed / dropped）：用户说"做完了""这事黄了"→ 找到对应那行，把 status 改成 `closed`（完成）或 `dropped`（不做了），加一个 `"closed_date": "YYYY-MM-DD"`。手写后跑 `wm.py promise` 验证可读。
欠账本改状态是记账，不算改历史——append-only 的规矩只约束 `user_writebacks.jsonl`。

**当场回一声**："记下了：X" 或 "划掉了：X"。

**和开场联动**：SKILL.md 第一步的"开工三句话"会瞄一眼这个本子，最老的一笔提一句——所以记账后用户在之后任何会话里都会被温柔地提醒。
