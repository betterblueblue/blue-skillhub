---
name: whydump
description: >
  Utility tool — Java OOM / 内存问题排查（非核心 Skill）。用户说 OOM、堆爆了、
  内存泄漏、堆占用异常时：先用人话问清现场，agent 能自己取的材料自己取，
  能改的下次启动参数自己改（先确认），缺材料时才向用户要文件，有直方图再分析。
  不参与 Skill 评测体系，不作为变更影响分析工具使用。
disable-model-invocation: false
# allowed-tools 按环境映射：Claude Code 用 Bash，DSH/本仓库用 pwsh，其他 agent 用各自的执行工具。
# 它只是「需要执行命令 + 读写 + 搜索」的声明，不是安全白名单，实际权限由环境自己的设置管。
allowed-tools: Bash, pwsh, Read, Write, Grep, Glob
---

# whydump — Java OOM 排查（先引导，再取证，再分析）

## 写入边界

- 取证 / 分析产出写入用户确认的路径；修改启动参数需先确认。
- 其余内容只读。

> utility，不是 pathfinder / impact 同类。用户对 OOM 没头绪时用。
> **对用户说话用人话。** 不要一上来甩 `histo.txt`、MAT、HeapDump 这种词。
> 要材料时说明：这是什么、谁来跑命令、跑完得到什么。

## 环境适配（工具名 / 命令跨环境）

- `allowed-tools` 里的执行工具按环境映射：Claude Code 用 `Bash`，DSH/本仓库用 `pwsh`，其他 agent 用各自的执行工具。它只是「这个 skill 需要执行命令 + 读写 + 搜索」的声明，不是安全白名单——实际权限由环境自己的设置管。
- 正文命令示例默认 bash 风格。**JDK 工具（`jps`/`jcmd`/`jmap`/`jhsdb`）和 `python` 跨平台**，Windows/pwsh 下直接跑，`>` 重定向通用。
- 取证卡里的 Linux 专属命令（`dmesg`、`ps -ef`、`find /`、`ulimit -u`）面向 Linux 服务器，保持 bash 原样发给用户；agent 在 Windows 本机执行时用等价命令（`Get-Process java`、`Get-CimInstance Win32_Process`、`Select-String`）。
- 跑分析脚本统一用 `python <skill根>/scripts/analyze.py ...`，与环境无关。

## 硬规则

1. **先问现场，再取证，最后才分析。** 用户只说「OOM 了」时，先问「一次问清」那几项。
2. **能自己做的不要丢给用户。** 进程还活着、当前环境能执行 JDK 工具 → 你来跑，不要让用户去敲 `jmap`。下次复现需要的启动参数 → 你在项目里找到启动入口，写好改动，**先给用户看，确认后再改**。
3. **只在你够不着的时候向用户要文件。** 例如：崩在另一台机器、没有登录权限、文件在运维手里。
4. **没有可分析材料时停在引导。** 不要编「已经定位到泄漏」。
5. **结论是疑似。** 单类大头也可能是缓存或业务大表。
6. **对还在跑的进程，先确认再抓堆。** `jmap -histo:live` 和堆转储都会让进程停顿一会儿。生产必须先问。

## 材料用人话怎么说

这些都不是用户磁盘上本来就有的「日志」。该生成的时候由 **agent 生成**，用户只在 agent 碰不到那台机器时才自己跑同一条命令。

| 对用户怎么说 | 实际是什么 | 谁来拿 |
|---|---|---|
| 「堆里现在各类对象各占多少」 | `jcmd <pid> GC.class_histogram -all`（零停顿）或本地低峰 `jmap -histo:live <pid>` 的文本输出，习惯存成 histo 文件 | 进程活着且你能执行命令 → **你跑**；否则把命令交给用户 |
| 「隔一段时间再抓一次，看哪个类在涨」 | 同一进程间隔 ≥10 分钟的两份直方图文本，用 `analyze.py --compare` 对比 | 同上，见 Phase 2——这是确认「泄漏」和「合法大缓存」的关键证据 |
| 「这个进程实际堆上限是多少」 | `jcmd <pid> VM.flags` 的文本，里面有 MaxHeapSize | 同上，建议有，没有也能分析直方图 |
| 「OOM 那一瞬间的堆快照」 | JVM 写出的 `.hprof` 文件。必须在**启动前**打开开关，崩完再补加不上 | 已经有文件 → 向用户要路径；还没有 → **你去改启动参数**，等下次复现 |
| 「垃圾回收流水账」 | GC 日志。同样是启动时打开 | 同上，本工具**不解析**，但 GC 日志是文本、agent 可以直接读（Full GC 频率/堆峰值）；没有日志才改参数等下次 |

**本工具真正能算的只有「各类对象各占多少」那份文本。**  
`.hprof` 是二进制，**现在解析不了**，不要假装从 dump 里算出了 Top 类。

不要对用户说「MAT」。那是 Eclipse Memory Analyzer，一个要单独安装的桌面软件。用户没问就不要让他去装。进程已死又只有 `.hprof` 时：诚实说算不了这份快照，能做的是根据报错原文和项目代码帮他缩小范围；如果他主动要桌面工具，再提 MAT。

## Phase 0 — 一次问清（用人话）

用户已经说了的不要再问：

1. 报错原文：`OutOfMemoryError` 那一行 + 后面的堆栈 `at ...` 行（一起贴出来）。
   **堆栈要收，但要防误导**：一次性大分配（如读大文件时 `new byte[...]`）时堆栈几乎直接指向根因；
   慢性泄漏时堆栈常常指向无辜代码——它只说明「最后一次分配在哪失败」，不说明谁把堆吃光了。两条都当线索，别当结论。
2. 出问题的 Java 进程现在还在跑吗
3. 你现在这台环境能不能对那个进程执行命令（就在本机 / 能 SSH / 完全碰不到）
4. 手里有没有别人已经留下的堆快照（`.hprof`）或直方图文本

用报错后半句分流，**不要**所有 OOM 都去抓堆：

| 报错后半句 | 走哪条 |
|---|---|
| `Java heap space` / `GC overhead limit exceeded` | 堆。进程活着 → 抓直方图；已死 → 看有没有快照，没有就改下次启动参数 |
| `Metaspace` / `PermGen` | **不是** Java 堆。不要抓直方图。看是不是大量动态生成类，以及启动参数里的 Metaspace 上限 |
| `Direct buffer memory` | **不是** Java 堆。看 NIO/Netty 和 DirectMemory 上限 |
| `unable to create native thread` | **不是** 堆。看线程数和系统进程数上限 |
| 进程被直接杀死：退出码 137 / K8s `OOMKilled` / `dmesg` 里有 `Out of memory: Killed process` | **不是 Java 的 OOM**，是内核或容器内存上限把进程杀了。不要抓直方图。查容器/cgroup 内存上限 vs JVM 总占用（堆 + Metaspace + 直接内存 + 线程栈），常见根因是 `-Xmx` 顶得太近或堆外内存把总量顶穿 |
| 只有「OOM 了」、没有原文 | 先要那一行原文 |

## Phase 1 — 取证（能跑就自己跑）

### 堆 OOM，进程还活着，你碰得到

1. `jps -l` 列出进程，让用户确认是哪一个，**不要猜 pid**。
2. 说明接下来要做的会不会停顿，问可不可以：
   - `jcmd <pid> VM.flags`、`jcmd <pid> GC.class_histogram -all`、`jmap -histo`（不带 `:live`）→ 只读零停顿，随手跑；
   - `jmap -histo:live` → 会触发 Full GC 让进程停顿一会儿，生产必须先把话说明、用户点头再跑。
3. 你来执行（生产首选零停顿口径；本地低峰想要「只算活对象」口径再换）：

```bash
jcmd <pid> VM.flags > flags.txt
jcmd <pid> GC.class_histogram -all > histo.txt     # 零停顿，但结果里含未回收垃圾
```

> JDK 8 的 `jcmd` 没有 `-all`（JDK 9+ 才有）：JDK 8 上零停顿口径用 `jmap -histo <pid>`（不带 `:live`），JDK 9+ 用 `-all` 或 `jmap -histo` 均可。

本地 / 低峰期想要「活对象」口径：

```bash
jmap -histo:live <pid> > histo.txt                 # 触发 Full GC，有停顿；生产先确认
jmap -histo <pid> > histo.txt                      # 零停顿，含垃圾，同 -all 口径
```

`jcmd`/`jmap` 都不可用时才用 `jhsdb`（最后手段，attach 运行中进程风险更大）：

```bash
jhsdb jmap --histo --pid <pid> > histo.txt
```

`jhsdb` 没有「只抓活对象」，结果里会掺垃圾，解读时说一声。类名写法也不同：`jmap`/`jcmd` 打印 `[B`/`[I`，`jhsdb` 打印 `byte[]`/`int[]`——拿 jhsdb 的输出做类名比对或回代码检索时先换算，不要按 `[B` 口径直接搜。**同一轮排查里两次抓取用同一种工具**，混用会让 `--compare` 的类名对不上。

4. **抓两份，对比增长**（确认泄漏的关键证据）：间隔 ≥10 分钟（10-30 分钟）再抓一份同样的直方图，`--compare` 对比。实例数持续增长的类才是泄漏候选；不涨的是缓存/业务大表的静态占用。生产用 `-all` 零停顿，可以放心抓；抓之前仍说明一声。
5. 有了直方图 → Phase 2。

#### attach 失败怎么办（jcmd/jmap/jhsdb 都报「拒绝访问 / Unable to open socket file / ptrace 不允许」）

1. 确认和目标是同一个系统用户：Windows 看是否同账号/管理员；Linux `ps -o user= -p <pid>` 对比当前用户。
2. Linux 查 `/proc/sys/kernel/yama/ptrace_scope`：为 1 或 2 时非父子进程 attach 被禁，用 `sudo -u <运行用户> jcmd <pid> ...`（需要 sudo，先问用户）。
3. 确认 JDK 工具版本能 attach 目标进程（同发行版一般没问题；太老的工具 attach 新版 JVM 可能失败）。
4. 都失败：**放弃现场取证**，走「进程已死」那条——改启动参数，下次复现留材料。不要反复重试吓用户。

碰不到那台机器时：不要只甩两条命令，按下面「服务器 / 容器场景」的取证卡流程来。

### 堆 OOM，进程已经死了

直方图做不出来，死进程补不上。

1. 问用户有没有现成的 `.hprof`（有的团队会自动留）。有路径就接下来用「读不了 dump」那条。
2. **没有快照时，不要只丢参数给用户。** 在当前项目里找启动入口（`JAVA_OPTS`、`start.sh`、`docker-compose`、K8s yaml、Maven/Gradle 的 jvmArgs、Windows 服务脚本），准备加上（JDK 9+）：

```text
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=<项目里一个明确目录>
-Xlog:gc*:file=<同样明确的 gc.log 路径>:time,uptime,level,tags
```

JDK 8 用 `-XX:+PrintGCDetails -Xloggc=<路径>` 代替 `-Xlog:gc*`。

把要改的文件和 diff 给用户看，**确认后再改**。说明：已经崩过的那次救不回来，这是为了下次再崩时自动留下快照。不要重启生产，除非用户明确要你重启。

3. 与此同时，可以根据报错原文 + 代码里无界缓存/静态集合做**推断**，必须标明是推断，不是证据。

### 非堆 OOM

不要跑分析脚本。直方图看的是 Java 堆，拿去分析 Metaspace/线程/容器会指错方向。按报错分支取对应材料（命令都带前置条件，缺了先补开关、等下次复现，别硬跑）：

| 报错分支 | 取什么材料 | 命令与前置条件 |
|---|---|---|
| `Metaspace` / `PermGen` | 元空间用量 + 启动参数上限 | `jcmd <pid> GC.heap_info`（只读零停顿，输出里有 Metaspace used/committed）；`jcmd <pid> GC.class_stats` 需先 `-XX:+UnlockDiagnosticVMOptions`（诊断命令、输出大，慎用）；查 `MaxMetaspaceSize`/`MetaspaceSize`。大量动态生成类 → 反射代理 / 热部署 / 模板编译 / 字节码增强 |
| `Direct buffer memory` | 直接内存用量 + 上限 | `jcmd <pid> VM.native_memory` 需**启动时** `-XX:NativeMemoryTracking=summary` 才有数据，没开就下次启动加（已死的进程补不上）；`-XX:MaxDirectMemorySize` 默认等于 `-Xmx`；查 NIO/Netty 的直接内存分配点 |
| `unable to create native thread` | 线程/进程数上限 vs 当前值 | `ulimit -u`（每用户进程/线程上限）、`/proc/sys/kernel/threads-max`、`ps -eLf \| wc -l`（全系统线程数）、`jcmd <pid> Thread.print`（看线程数和栈，输出大） |
| 退出码 137 / OOMKilled / dmesg 杀进程 | 容器/cgroup 内存上限 vs 进程总占用 | 见「服务器 / 容器场景」里的容器内存测量 |

## 服务器 / 容器场景（agent 碰不到生产机）

生产机通常不允许 agent 直接连，也不该连。这时你的角色从「自己跑命令」变成「**发取证卡**」：用户不需要懂 JVM，只需要复制粘贴、把结果带回来。

### 取证卡纪律

- **一次只发一张卡**，下一张以上一张的结果为条件。一次甩五张，用户会乱。
- 每张卡四要素：**可整段粘贴的命令**（占位符留好）、**风险等级**（只读 / 停顿几秒 / 停顿较久）、**跑完得到什么**（明确的文件路径或直接粘贴的输出）、**怎么带回来**（小文本直接粘贴；大文件 `scp` / `kubectl cp`）。
- 有停顿的卡，先写明「会让服务停顿，生产高峰期先和运维确认」，用户点头再发。

### 第 0 张卡：任何情况先发（纯只读）

```bash
dmesg -T | grep -iE 'oom|killed process' | tail -20
grep -m 5 'OutOfMemoryError' /path/to/应用日志 2>/dev/null
ps -ef | grep java | grep -v grep
```

一次回答三件事：是不是内核杀的（是 → 走 Phase 0 分流表「进程被直接杀死」那条）、Java 报错原文是哪半句、进程现在还活着吗。输出直接粘贴回来。

### 按用户能做什么分层要材料

| 用户处境 | 要什么 |
|---|---|
| 完全碰不到服务器 | 只要**现成文件**：报错原文、`dmesg`/`journalctl` 片段、`kubectl describe pod` 输出、遗留 `.hprof` 的路径。现场生成类材料全部放弃，走「改下次启动参数」+ 代码推断（标注是推断） |
| 能登服务器，进程活着 | 第 1 层（只读，随手跑）：`jcmd <pid> VM.flags`、`jcmd <pid> GC.heap_info`；第 2 层（零停顿）：`jcmd <pid> GC.class_histogram -all`（或 `jmap -histo <pid>`，不带 `:live`）；第 3 层（有停顿，先确认）：`jmap -histo:live <pid>`、JFR、dump |
| 能登服务器，进程已死 | 先发找快照卡。服务器常有自动重启（systemd `Restart=always` / K8s 自愈），等用户找你时**出事现场早没了**，遗留的 `.hprof` 是唯一能救回那次的材料 |

第 2 层不带 `:live` 是刻意的：不触发 Full GC、零停顿，结果是「对象 + 未回收垃圾」，多数时候已够初判；确需活对象再升级到第 3 层。

**找快照卡**（只读，进程已死时发）：

```bash
find / -name '*.hprof' -mtime -7 2>/dev/null
grep -rn 'HeapDumpOnOutOfMemoryError\|Xmx\|MaxRAMPercentage' /etc/systemd/system/ /path/to/启动脚本 2>/dev/null | head -20
```

找到 `.hprof` → 见下面「.hprof 的现实困难」。没找到 → 把 Phase 1 的 dump/GC 日志参数整理成具体 diff（systemd unit / `start.sh` / K8s yaml），交给用户或运维去改，并提醒两件事：**已经崩过的那次救不回来**；**dump 路径要挂持久卷**——写进容器里的 dump 会随 Pod 销毁丢掉，下次崩了白抓。

### 生产上的优先级

- **JFR 优先，jmap 谨慎**：`jmap -histo:live` 触发 Full GC 全程停顿，生产高峰期是事故放大器；JFR 采样开销 <1%，还能拿到分配栈。`VM.flags` / `GC.heap_info` 这类只读命令无感，随时可发。

### 容器内存怎么量（137 / OOMKilled 分支用）

1. 判断 cgroup 版本：`test -f /sys/fs/cgroup/memory.max` 存在即 v2（或 `cat /proc/self/cgroup` 里有 `0::` 行，有即 v2）；否则是 v1。
2. 内存上限与当前用量：
   - v2：`/sys/fs/cgroup/memory.max`（上限，`max` 表示不限）+ `/sys/fs/cgroup/memory.current`
   - v1：`/sys/fs/cgroup/memory/memory.limit_in_bytes` + `/sys/fs/cgroup/memory/memory.usage_in_bytes`
3. 进程实际占了多少：`/proc/<pid>/status` 里的 `VmRSS` / `VmPeak`（容器里 `kubectl exec` 后跑；pid 用 `jps -l` 或 `ps` 找）。
4. `kubectl describe pod <name>`：看容器内存 limit、`Exit Code: 137`、`OOMKilled`、重启次数。
5. 对比：容器内存上限 vs JVM 总占用（堆 + Metaspace + 直接内存 + 线程栈）。常见根因：`-Xmx` 顶得太近、堆外内存顶穿、容器里 JVM 默认按 `MaxRAMPercentage`（通常 25%）感知容器内存导致堆设太小——用 `jcmd <pid> VM.flags` 确认实际生效的 `MaxHeapSize` / `MaxRAMPercentage`。

### .hprof 的现实困难，如实说

几十 MB 到几 GB 的二进制，粘贴不可能。先问用户能不能 `scp` / `kubectl cp` 拉到一台能分析的机器；拉不出来就明说「这份快照本工具分析不了」，转 Phase 1 的代码推断，**不要让用户干等、也不要假装在读 dump**。

## Phase 2 — 有直方图再分析

脚本在**本 skill 根目录**（仓库里是 `skills/whydump/`，装好后是 `~/.claude/skills/whydump/`）；histo/flags 是 Phase 1 抓取时落在**当时工作目录**（通常是用户项目目录）的文件。传取证时的实际路径（必要时绝对路径），不要为了跑脚本把文件挪到 skill 目录：

```bash
python <skill根目录>/scripts/analyze.py <取证目录>/histo.txt --flags <取证目录>/flags.txt
```

在仓库根目录的等价写法：`python skills/whydump/scripts/analyze.py <histo路径>`

两次采样对比（确认增长型泄漏的关键证据）：

```bash
python <skill根目录>/scripts/analyze.py --compare <histo-第一份> <histo-第二份> [--flags <flags.txt>]
```

两份必须是**同一种工具、同一个 pid** 抓的（间隔 ≥10 分钟）。混用 jmap/jhsdb 会让类名对不上（`[B` vs `byte[]`）——脚本检测到匹配率低会显式告警，这时结论不可信，先重抓。退出码与单份相同：0 成功，1 有输入无法解析。

退出码 0 = 解析成功（不论判成哪类）；1 = 文件不是直方图。失败就回头检查文件，不要改口编结论。
输出开头若提示「疑似截断的直方图」，说明拿到的文本不完整、占比被抬高——先重新拿完整输出（如去掉 `head`、整段重抓），再下结论。

## Phase 3 — 解读

- `leak-suspect`：有一个类占了堆的一大半（默认 ≥ 50%）。先问用户这类是不是缓存或业务大表。再回代码查谁在往里写、有没有淘汰。需要引用链且进程仍活着、用户允许再停顿一次：才考虑 `jmap -dump:live,format=b,file=x.hprof <pid>`。dump 你仍然解析不了，用途是留给用户用桌面工具看，或以后另做。
- `no-dominant-class`：没有单类大头。可能是堆偏小，也可能要看回收流水账。输出同时给「前 3 类合计占比」：合计很高、且前几名是数组 + 集合内部类的组合（如 `byte[]`/`char[]`/`HashMap$Node`）时，可能是同一泄漏源摊到了多个类——回代码查这几类的公共写入点。需要看 GC 流水账时：GC 日志是文本，**agent 可以直接读**（Full GC 频率、堆峰值、`GC overhead limit` 前兆），不必等下次复现；手上没有日志才按 Phase 1 改启动参数，下次再看。
- `growth-suspect`（来自 `--compare`）：有一个类实例数在两次采样间持续大幅增长——这比单张直方图的 `leak-suspect` 更接近实锤（排除缓存/业务大表靠的就是「不涨」）。回代码查这个类的写入点；持续增长且无淘汰 → 基本坐实泄漏。
- `no-clear-growth`（来自 `--compare`）：没有类出现显著单点增长，倾向静态占用（缓存/业务大表）或分布增长。仍 OOM 时看 GC 日志（堆峰值/Full GC 频率），再决定调 `-Xmx` 还是继续查代码。
- `compare-mismatch`（来自 `--compare`）：两份直方图类名对不上（jmap 的 `[B` vs jhsdb 的 `byte[]`，或混用了不同 pid/工具）。**脚本不给结论**，按提示重抓（同一种工具、同一个 pid、间隔 ≥10 分钟），不要基于这份对比分析。
- `no-data`：文件里没有可解析的行。

## Phase 4 — 修与验证（把「疑似」变成「已解决」）

定位到嫌疑类之后，按模式对照表找代码，**修完必须验证**，不然不算完。

### 常见泄漏模式 → 代码特征 → 怎么修

| 模式 | 代码长什么样 | 怎么修 |
|---|---|---|
| 无界缓存 / 静态集合 | `static Map/List`、缓存只写不淘汰；每次请求往里 `put/add` | 加容量上限与淘汰（`LinkedHashMap#removeEldestEntry`、Guava Cache、Caffeine）；确认 key 集合有界 |
| ThreadLocal 不清理 | 线程池任务里 `ThreadLocal.set(大对象)`，从不 `remove()` | `finally` 里 `remove()`；能传参就别用 ThreadLocal |
| 大文件 / 大报文整读 | `Files.readAllBytes`、`new byte[file.length()]`、整条报文塞进内存 | 改流式 / 分片处理 |
| 批处理全量收集 | 一次查全表、全量 List 累积再处理 | 分页 / 流式 / 批量提交 |
| 连接/会话/游标不关 | JDBC/HTTP/IO 打开后不 close | `try-with-resources`；检查连接池上限与回收 |
| 动态类生成（偏 Metaspace） | 反射代理 / 热部署 / 模板编译每轮生成新类 | 限制生成、复用、卸载（配 Metaspace 分支一起看） |

### 修完怎么验证

1. 本地直接重启（生产走正常发布流程，不要偷偷重启）。
2. 修完再用**同一种工具、同一个 pid** 抓两份直方图（间隔 ≥10 分钟），`--compare`：
   - 嫌疑类实例数不再持续增长 → 修对了；
   - 仍增长 → 没修到点上，继续查公共写入点。
3. 顺手看堆峰值是否回落（`jcmd <pid> GC.heap_info` 或 GC 日志），观察几天不再 OOM 才算完。

## 依赖

- Python >= 3.10（`scripts/analyze.py` 只用标准库）
- 取证需要本机有 JDK：`jcmd` / `jmap` / `jhsdb`

## 本版明确不做

- **不解析** `.hprof`、不解析 GC 日志、不做线程 dump 分析
- 不替代任何桌面堆分析软件
- `scripts/leak-demo/` 只测分析脚本，不代替 Phase 0/1
