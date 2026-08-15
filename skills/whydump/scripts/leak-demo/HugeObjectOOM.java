/**
 * 场景 4：单对象超大（一个对象撑爆堆）。
 * 尝试一次性分配接近整个堆的超大 byte[]。若 OOM 则捕获后仍持有，
 * 让进程活着供 jmap 抓取；否则持有数组并等待。
 * 期望：leak-suspect，Top 类 = byte[]（[B），且占比极高（~90%+）。
 *
 * 运行：java -Xmx128m HugeObjectOOM
 */
public class HugeObjectOOM {
    public static void main(String[] args) throws Exception {
        System.out.println("MY_PID " + ProcessHandle.current().pid()); // 供评测脚本定位
        byte[] huge = null;
        try {
            huge = new byte[96 * 1024 * 1024]; // 96MB，占 -Xmx128m 的 75%
        } catch (OutOfMemoryError e) {
            System.out.println("OOM-caught");
            // 降到 64MB 再试，尽量保住进程
            huge = new byte[64 * 1024 * 1024];
        }
        // 用一下防止被优化掉
        long checksum = 0;
        for (int i = 0; i < huge.length; i += 1024 * 1024) checksum += huge[i];
        System.out.println("READY huge=" + huge.length + " chk=" + checksum);
        Thread.sleep(120_000);
    }
}
