/**
 * 场景 5：堆设小、无泄漏（对照组）。
 * 一堆不同类型的小对象在正常业务中流转：不持有全局引用、对象可被回收，
 * 堆给得很小（-Xmx32m），持续分配直到接近上限。
 * 期望：no-dominant-class（对象分布平均，无单类大头）→ 倾向堆设小。
 *
 * 运行：java -Xmx32m HeapTooSmall
 */
public class HeapTooSmall {
    static class TaskA { long id; double val; String tag = new String(new char[1024]); }
    static class TaskB { int[] buf = new int[1024]; String name = new String(new char[512]); }
    static class TaskC { java.util.Date ts = new java.util.Date(); byte[] payload = new byte[2048]; }

    public static void main(String[] args) throws Exception {
        System.out.println("MY_PID " + ProcessHandle.current().pid()); // 供评测脚本定位
        // 三种对象交替分配，且不保存全局引用（可回收）
        long seq = 0;
        while (true) {
            for (int i = 0; i < 10_000; i++) {
                Object o;
                switch ((int) (seq % 3)) {
                    case 0: o = new TaskA(); break;
                    case 1: o = new TaskB(); break;
                    default: o = new TaskC(); break;
                }
                if (o.hashCode() == Integer.MIN_VALUE) System.out.print(""); // 防优化
            }
            seq += 10_000;
            long used = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
            long max = Runtime.getRuntime().maxMemory();
            if (used > max * 0.6) {
                System.out.println("READY pressure seq=" + seq);
                Thread.sleep(120_000);
                break;
            }
        }
    }
}
