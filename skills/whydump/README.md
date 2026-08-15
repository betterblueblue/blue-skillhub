# whydump — Java OOM 排查（先问清，能取就自己取）

用户说「OOM 了」时，不要先甩工具名。先问清现场；进程还活着且碰得到，由 agent 自己抓「堆里各类对象各占多少」；进程已经死了，由 agent 在项目里改下次启动参数（先确认）。有了直方图再算「疑似泄漏还是倾向堆小」。

`.hprof` 堆快照本工具**解析不了**。GC 日志本工具也**不解析**。

生产机/容器碰不到时，走 SKILL.md 的「服务器 / 容器场景」取证卡流程：用户复制粘贴命令、把结果带回来，agent 不直连生产。

## 那些文件从哪来

它们通常不是现成日志，是现场生成的：

| 对用户怎么说 | 怎么来 | 谁来拿 |
|---|---|---|
| 堆里各类对象各占多少 | 对还活着的进程跑 `jmap -histo:live <pid>` | 碰得到进程 → agent 跑；碰不到 → 把命令给用户 |
| 这个进程堆上限 | `jcmd <pid> VM.flags` | 同上，建议有 |
| OOM 那一瞬间的堆快照（`.hprof`） | 必须启动前打开 `-XX:+HeapDumpOnOutOfMemoryError`，崩完再加没用 | 已有文件就问路径；没有就由 agent 改启动脚本（先确认） |
| 垃圾回收流水账 | 启动时打开 GC 日志 | 同上；本工具不读这份 |

## 分析（有直方图之后）

```bash
python skills/whydump/scripts/analyze.py histo.txt --flags flags.txt
```

- `leak-suspect`：单类占堆超过 50% → 疑似泄漏，先排除缓存/业务大表
- `no-dominant-class`：无单类大头 → 倾向堆偏小；但前 3 类合计占比很高且多为数组/集合内部类时，可能是同一泄漏源摊到了多个类

## 测试

```bash
python -m unittest discover -s skills/whydump/tests -p "test_*.py"
bash skills/whydump/scripts/leak-demo/run_all.sh
```

## 本版不做

- 不解析 `.hprof`、GC 日志、线程 dump
- 不替代桌面堆分析软件
