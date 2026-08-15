/**
 * 场景 3：缓存不清（无淘汰策略的缓存）。
 * 一个静态 HashMap 当缓存，持续 put 新条目且从不淘汰，
 * 每个 value 是 256KB 的 byte[]。key 用唯一字符串。
 * 期望：leak-suspect，Top 类 = byte[]（[B）。
 *
 * 运行：java -Xmx128m CacheLeak
 */
public class CacheLeak {
    // 静态缓存，只有 put 没有 evict/过期
    static final java.util.Map<String, byte[]> CACHE = new java.util.HashMap<>();

    public static void main(String[] args) throws Exception {
        System.out.println("MY_PID " + ProcessHandle.current().pid()); // 供评测脚本定位
        long seq = 0;
        while (true) {
            if (seq > 0 && seq % 64 == 0) {
                long used = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
                long max = Runtime.getRuntime().maxMemory();
                if (used > max * 0.6) {
                    System.out.println("READY size=" + seq);
                    Thread.sleep(120_000);
                    break;
                }
            }
            CACHE.put("key-" + seq++, new byte[256 * 1024]); // 256KB
        }
    }
}
