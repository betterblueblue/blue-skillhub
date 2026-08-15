# whydump — Java OOM 排查（先问清，能取就自己取）

## 这个 skill 为什么存在

一个对 JVM 一无所知的用户说「OOM 了」时，没有辅助的 agent 只有两种失败姿态：把一墙的 JDK 工具名和参数甩给用户（「你去抓个 histo、开个 GC 日志」），或者不看证据直接猜「应该是内存泄漏」。而用户这边是完全束手无策——连该提供什么材料都不知道。

whydump 把老手的排查顺序写死成流程，让 agent 带着用户走完一条完整的路：

**问清现场 → 取证 → 分析 → 确认 → 修 → 验证**

1. 先按报错原文分流：堆 / Metaspace / 直接内存 / 线程 / 被容器杀——不是所有 OOM 都去抓堆
2. 能自己做的自己做：进程活着且碰得到 → agent 自己跑 JDK 工具；碰不到生产 → 发「取证卡」，用户只需复制粘贴、把结果带回来
3. 有直方图才算数：占比、增长这些数字交给脚本机械计算，不靠模型心算
4. 单张直方图分不清「泄漏」和「合法大缓存」→ 间隔 ≥10 分钟再抓一份，`--compare` 看哪个类在涨
5. 定位到嫌疑类 → 按 SKILL.md Phase 4 的泄漏模式对照表找代码、修 → 修完重抓两份验证不再增长

三条底线：

- **对人说话用人话**：不假设用户认识 histo、MAT、HeapDump 这些词；材料是什么、谁去拿、拿到什么，都说清楚
- **agent 能做的绝不推给用户**：能跑的命令自己跑，该改的启动参数自己写好 diff、先确认再改
- **结论只给证据支撑的**：疑似就是疑似；算不了（如 `.hprof`）就明说，不编「已定位到泄漏」

它是有意收窄的入口，不是终点：`.hprof` 堆快照**解析不了**、GC 日志**不解析**（但它是文本，agent 可以直接读 Full GC 频率/堆峰值）；需要引用链和 dominator tree 时，把 dump 留给桌面堆分析工具。生产机/容器碰不到时的取证方式，见 SKILL.md「服务器 / 容器场景」。

## 那些文件从哪来

它们通常不是现成日志，是现场生成的：

| 对用户怎么说 | 怎么来 | 谁来拿 |
|---|---|---|
| 堆里各类对象各占多少 | 对还活着的进程跑 `jcmd <pid> GC.class_histogram -all`（零停顿）或本地低峰 `jmap -histo:live <pid>` | 碰得到进程 → agent 跑；碰不到 → 把命令给用户 |
| 哪个类在涨 | 同一进程间隔 ≥10 分钟抓两份直方图，`--compare` 对比 | 同上，这是区分泄漏和合法大缓存的关键证据 |
| 这个进程堆上限 | `jcmd <pid> VM.flags` | 同上，建议有 |
| OOM 那一瞬间的堆快照（`.hprof`） | 必须启动前打开 `-XX:+HeapDumpOnOutOfMemoryError`，崩完再加没用 | 已有文件就问路径；没有就由 agent 改启动脚本（先确认） |
| 垃圾回收流水账 | 启动时打开 GC 日志 | 同上；本工具不解析，但 agent 可以直接读（Full GC 频率/堆峰值） |

## 分析（有直方图之后）

```bash
python skills/whydump/scripts/analyze.py histo.txt --flags flags.txt
python skills/whydump/scripts/analyze.py --compare histo_a.txt histo_b.txt [--flags flags.txt]
```

- `leak-suspect`：单类占堆超过 50% → 疑似泄漏，先排除缓存/业务大表
- `no-dominant-class`：无单类大头 → 倾向堆偏小；但前 3 类合计占比很高且多为数组/集合内部类时，可能是同一泄漏源摊到了多个类
- `growth-suspect`（`--compare`）：某类实例数在两次采样间持续大幅增长 → 比单张直方图更接近实锤
- `no-clear-growth`（`--compare`）：无显著单点增长 → 倾向静态占用/分布增长
- `compare-mismatch`（`--compare`）：两份直方图类名对不上（如 jmap `[B` vs jhsdb `byte[]` 混用）→ 脚本不背书、不给结论，先重抓

两份直方图要**同一种工具、同一个 pid、间隔 ≥10 分钟**；混用 jmap/jhsdb 会返回 `compare-mismatch`，不会当成泄漏。

定位到嫌疑类后，按 SKILL.md Phase 4 的泄漏模式对照表修，**修完重抓两份验证**（嫌疑类不再增长、堆峰值回落）。

## 测试

```bash
python -m unittest discover -s skills/whydump/tests -p "test_*.py"
bash skills/whydump/scripts/leak-demo/run_all.sh
```

## 本版不做

- 不解析 `.hprof`、GC 日志、线程 dump
- 不替代桌面堆分析软件
