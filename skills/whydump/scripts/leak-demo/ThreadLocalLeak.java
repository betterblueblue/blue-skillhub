/**
 * 场景 2：ThreadLocal 没 remove（线程池场景的经典泄漏）。
 * 每个线程往 ThreadLocal 里塞一个 1MB byte[]，线程不退出、不 remove，
 * ThreadLocal 值被线程对象钉住永不回收。
 * 期望：leak-suspect，Top 类 = byte[]（[B）。
 *
 * 运行：java -Xmx128m ThreadLocalLeak
 */
public class ThreadLocalLeak {
    // 每个线程一个 1MB 的本地数组，塞进去就不 remove
    static final ThreadLocal<byte[]> TL = new ThreadLocal<>();

    public static void main(String[] args) throws Exception {
        System.out.println("MY_PID " + ProcessHandle.current().pid()); // 供评测脚本定位
        Thread t = new Thread(() -> {
            TL.set(new byte[1024 * 1024]); // 1MB
            try { Thread.sleep(120_000); } catch (InterruptedException ignored) {}
        }, "leak-worker");
        t.start();

        // 主线程也塞一个，等子线程 READY 后对外报告
        TL.set(new byte[1024 * 1024]);
        System.out.println("READY threads-alive");
        t.join();
    }
}
