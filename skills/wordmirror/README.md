# 言镜 · WordMirror

> 以铜为镜，可以正衣冠；以史为镜，可以知兴替；**以言为镜，可以知自己。**

把你说给 AI 的话，变成 AI 对你的认识。

## 这是什么

一个放进 agent skills 目录的技能包。装上之后，你开的每个新会话，AI 都是老熟人：开局就知道你是谁、在忙什么、怎么跟你说话；你查旧账，它引原话、带日期、查不到就直说；你说"记住这个"，它只记你确认过的事实。

所有数据只存在你自己的机器上。这个包不联网、不收集、不分析——你的话是你的。

## 装上你会得到什么

- **认识你**：装完，AI 就认识你（你是谁、在忙什么、跟你说要什么规矩），不用再每次重新介绍自己
- **旧账可查**：你说过几千句话都能翻出来——你问的词跟当时说的不一样，也能按意思搜到（要装个可选的东西）；同一件事前后说法变了，两版都摆出来，你自己判断
- **跨工具**：你在多个 agent 里的历史合成一本账，在任何一处都能查别处说过的话
- **对外安全**：要分享时先把隐私去掉，不能公开的部分绝不发出去，发给谁由你当场确认
- **不端着**：AI 只在你问起来时摆事实（原话、日期、条数），不主动分析你的心理和行为——你的情况是给 AI 干活用的，不是用来评判你的

## 按意思搜（可选，默认没开）

只按字面搜的死穴是：你记不住当时用的词。装了这个之后能按意思搜——问「当初为什么换技术栈」，能翻出你当时说的「把老项目迁到 Go」，一个字都不一样也搜得到。

```bash
python scripts/vecsearch.py build    # 建好（几千句话约 2 分钟）
python scripts/vecsearch.py query "问题"   # 按意思搜（AI 字面搜不到时会自己调它）
```

- 装依赖：`pip install chromadb sentence-transformers`（都在你自己电脑上跑）
- 第一次建要下载一个约 117MB 的模型到 `~/.cache/huggingface`——这是下载工具，**不是把你的话传出去**；搜的时候全程在你自己电脑上
- 没装依赖或没建：自动退回按字面搜（带近义词），照样能用
- 你说过的话变多了：`wm.py vec build --update` 把新的补进去

## 快速开始

1. 把整个 `wordmirror/` 目录拷进你 agent 的 skills 目录
2. 对你的 agent 说：**初始化 wordmirror**
3. 日常使用不用任何命令——"我之前说过什么""记住这个""这个能发出去吗"，直接说就行

命令行入口（可选）：`scripts/wm.py`——`ingest`（把你说过话提取出来）、`promise`（说过要做的事：add 记一笔 / done 划掉）、`wb`（记你确认过的事：add / list）、`vec`（按意思搜：build / status）、`monthly`（这个月的报告）、`bind`（把已有数据接上）、`check`（自检）、`open`（浏览器打开产物首页）。

## 数据放在哪（两层）

**全局层**——"你是谁"（你的情况/规矩/你说的话/月报），不分项目，跟着你走。默认在用户主目录 `~/WordMirror/`（数据在 `~/WordMirror/data/`）；环境变量 `WORD_MIRROR_HOME` 或 `wm.py bind <目录>` 可以指到别处。旧名字 `DIGITAL_SELF_HOME`、`~/.digital-self/` 也能认。详见 `references/data-locations.md`。

**项目层**——"这个项目的事"（说过要做的事/记的事），在哪个目录干活就记哪：`<当前目录>/.wordmirror/promises.jsonl`，第一次记时自动建。⚠️ **注意：账本里存的是你的原话，可能含隐私（姓名/公司/薪资…）。默认不要把它提交进 git**——建议在项目 `.gitignore` 里加一行 `.wordmirror/`；真想跟着项目走，先把内容过一遍再手动挑出来。每次开工两层都看；月报里"办完的事"也收两层。

## 装完就能用（自包含）

这个 skill 包自带提取引擎（`engine/`）——ingest、查旧账、记你确认过的事、生成网页、按意思搜，装完就能用，不需要再找一个"完整仓库"。数据默认产在用户主目录 `~/WordMirror/data`（含你的原话，跟着你的机器走，不在 skill 包里）。

如果你的数据在别处（比如旧版留下的），`python wm.py bind <数据目录>` 一条命令接上，或设环境变量 `WORD_MIRROR_HOME`。

## 支持哪些 agent

ingest 会探测并提取你在这些工具里说过的话（清单在 skill 包的 `engine/detect_agents.py` 维护）：

- Claude Code、Codex、Cursor、DeepSeek Harness、美团 CatPaw、zcode、Qwen、WorkBuddy、Pi、AtomCode、Google Antigravity（Grok 仅能采 shell 输入）

各工具存档格式不同，个别要多装一个依赖：**DeepSeek Harness 需要 `pip install zstandard`**（解压它的 zstd 会话文件）。缺了不影响其他工具，只是 dsh 跳过并在跑 ingest 时提示。

想加一个新的 agent：在 `engine/detect_agents.py` 加一行探测，再在 `extract_all.py` / `extract_ai.py` 各写一个解析函数。

## 目录导览

```
SKILL.md          AI 的入口：按场景干活，AI 只读这一个文件就够
references/       六份协议（初始化/翻旧账/记事/隐私/更新/数据放哪）+ 两份生成模板
layers/           隐私层模板（出厂是空的）：真实的 public.md 和 redact_list.json 在数据目录 data/layers/，整理生成；清单本身含敏感词，绝不外传
scripts/wm.py     命令行入口（翻旧账/记事/导出/月报）
scripts/render.py  网页生成：read（首页/你的情况/翻给你看）/ monthly / tracker / all
templates/        视觉规矩：DESIGN.md + read_shell.html + tracker.html（改样式只改这里）
```

## 诚实边界

- 你说过的话不到 500 条，了解得还比较粗；几千条才是完整体验
- 只记你对 AI 说的话——你跟人线下说的，它不知道
- 你的情况是个快照，说了新东西要重新整理才会更新（怎么更新在 references/ingest-protocol.md）
