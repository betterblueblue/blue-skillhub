/**
 * 场景 1：静态集合越塞越多（经典泄漏）。
 * 一个静态 List 无限 add，每个元素持有 64KB 的 int[]，永不释放。
 * 期望：leak-suspect（单类大头），Top 类 = int[]（[I）或本类。
 *
 * 运行：java -Xmx128m StaticListLeak
 */
public class StaticListLeak {
    // 静态引用把对象钉在 GC root 上，回收不掉
    static final java.util.List<LeakedItem> LEAK = new java.util.ArrayList<>();

    static class LeakedItem {
        final int[] payload = new int[16384]; // 64KB
        final long seq;
        LeakedItem(long seq) { this.seq = seq; }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("MY_PID " + ProcessHandle.current().pid()); // 供评测脚本定位
        long seq = 0;
        while (true) {
            // 填到接近堆上限后停下等待抓取（-Xmx128m）
            if (LEAK.size() > 0 && LEAK.size() % 512 == 0) {
                long used = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
                long max = Runtime.getRuntime().maxMemory();
                if (used > max * 0.75) {
                    System.out.println("READY size=" + LEAK.size());
                    Thread.sleep(120_000); // 给 jmap 抓取留时间
                    break;
                }
            }
            LEAK.add(new LeakedItem(seq++));
        }
    }
}
