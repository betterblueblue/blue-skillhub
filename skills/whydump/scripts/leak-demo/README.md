# leak-demo — whydump 评测语料

5 种**已知答案**的真实 OOM 场景，用于验证 `analyze.py` 判定是否可靠。

## 场景清单

| 场景 | 源码 | 泄漏点 | 期望判定 |
|---|---|---|---|
| 1 | `StaticListLeak.java` | 静态 `List` 无限 add，元素带 64KB `int[]`，永不释放 | `leak-suspect`，Top1 = `[I` |
| 2 | `ThreadLocalLeak.java` | 线程往 `ThreadLocal` 塞 1MB `byte[]` 且不 remove，线程不退出 | `leak-suspect`，Top1 = `[B` |
| 3 | `CacheLeak.java` | 静态 `HashMap` 当缓存，只 put 不清不淘汰，value 为 256KB `byte[]` | `leak-suspect`，Top1 = `[B` |
| 4 | `HugeObjectOOM.java` | 单对象一次性分配接近整个堆 | `leak-suspect`，Top1 = `[B`，占比 ~99% |
| 5 | `HeapTooSmall.java` | 对照组：堆给很小、无泄漏，对象可回收、分布平均 | `no-dominant-class` |

## 原理

每个场景把堆填到接近上限后 `READY` 等待，脚本用 `jmap -histo:live` 抓存活对象直方图，
跑 `analyze.py --json`，把 `category` 与期望比对。`-histo:live` 先做一次 Full GC，
抓的是存活对象，正是泄漏现场。

## 运行

前置：JDK 在 PATH（javac / java / jmap），bash 环境（Git Bash 可用）。

```bash
bash run_all.sh              # 全部 5 个场景
bash run_all.sh StaticListLeak   # 只跑单个场景
```

输出形如：

```
===== [StaticListLeak] 期望: leak-suspect Top1=[I (heap=128m) =====
java_pid=28468 现场输出：READY size=1536
PASS  category=leak-suspect Top1=[I 占 0.993
```

`PASS` 表示 `category` 与期望一致；泄漏场景还比对 Top1 类名（`[I` / `[B`）。
对照组 `HeapTooSmall` 只比对 `category`（对象可回收，Top1 不稳定）。
任一场景失败或跑不通，脚本退出码为 1。每次场景结束后清理 `*.class` 和 `histo_*.txt`。

## 注意事项

- `jmap` attach 需要与目标进程同用户权限；Windows 上以同账号运行即可。
- Git Bash 里 `$!` 和 `jps` 拿到的都不是 Windows 原生 PID，脚本用 Java
  自报的 `MY_PID`（`ProcessHandle.current().pid()`）定位，勿改。
- 各场景运行时会 sleep 一段时间留出抓取窗口，超时会自动结束。
