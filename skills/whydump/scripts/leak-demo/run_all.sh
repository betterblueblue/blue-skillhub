#!/usr/bin/env bash
# whydump 评测 runner：对 5 种已知答案的 OOM 场景，
# 各造一次真实堆现场 → jmap 抓 histo → analyze.py 判定 → 与期望比对。
#
# 用法：./run_all.sh            # 全部场景
#      ./run_all.sh StaticListLeak   # 只跑单个场景
#
# 前置：JDK 在 PATH（javac/java/jmap），bash 环境（Git Bash 可用）。
# 注意：jmap -histo:live 需要与目标进程同用户权限，Windows 上需以同账号运行。
# 退出码：全部场景 category + Top1 都对上才为 0；任一失败或跑不通为 1。

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYZE="$(dirname "$SCRIPT_DIR")/analyze.py"
cd "$SCRIPT_DIR"

# 场景 => (源文件, 堆大小, 期望类别, 期望 Top1；- 表示不比对 Top1)
declare -A SCENES=(
    [StaticListLeak]="StaticListLeak.java 128m leak-suspect [I"
    [ThreadLocalLeak]="ThreadLocalLeak.java 128m leak-suspect [B"
    [CacheLeak]="CacheLeak.java 128m leak-suspect [B"
    [HugeObjectOOM]="HugeObjectOOM.java 128m leak-suspect [B"
    [HeapTooSmall]="HeapTooSmall.java 32m no-dominant-class -"
)

PASSED=0
FAILED=0

cleanup_scene() {
    local scene="$1"
    rm -f "${scene}.class" ${scene}\$*.class "histo_${scene}.txt" "/tmp/${scene}.out"
}

run_one() {
    local scene="$1"
    if [ -z "${SCENES[$scene]+x}" ]; then
        echo "未知场景: $scene"
        FAILED=$((FAILED + 1))
        return 1
    fi
    IFS=' ' read -r src heap expect expect_top <<< "${SCENES[$scene]}"
    echo "===== [$scene] 期望: $expect Top1=${expect_top} (heap=$heap) ====="

    javac "$src" 2>/tmp/why_javac_err || {
        echo "编译失败: $(cat /tmp/why_javac_err)"
        FAILED=$((FAILED + 1))
        cleanup_scene "$scene"
        return 1
    }

    java -Xmx"$heap" "$scene" > "/tmp/${scene}.out" 2>&1 &
    local jpid=$!

    local ready=0
    for i in $(seq 1 120); do
        if grep -q READY "/tmp/${scene}.out" 2>/dev/null; then ready=1; break; fi
        if ! kill -0 "$jpid" 2>/dev/null; then
            echo "进程提前退出，输出：$(cat /tmp/${scene}.out)"
            FAILED=$((FAILED + 1))
            cleanup_scene "$scene"
            return 1
        fi
        sleep 0.5
    done
    if [ "$ready" -ne 1 ]; then
        echo "超时未 READY"
        kill "$jpid" 2>/dev/null
        wait "$jpid" 2>/dev/null
        FAILED=$((FAILED + 1))
        cleanup_scene "$scene"
        return 1
    fi

    # Git Bash 的 $! / jps 不是 Windows 原生 PID，用 Java 自报的 MY_PID
    local java_pid=""
    java_pid=$(grep '^MY_PID ' "/tmp/${scene}.out" | awk '{print $2}' | head -1)
    if [ -z "$java_pid" ]; then
        echo "未从输出读到 MY_PID，改用 bash pid $jpid"
        java_pid="$jpid"
    fi
    echo "java_pid=$java_pid 现场输出：$(grep READY /tmp/${scene}.out)"

    if ! jmap -histo:live "$java_pid" > "histo_${scene}.txt" 2>/tmp/why_jmap_err; then
        echo "jmap 失败: $(cat /tmp/why_jmap_err)"
        kill "$jpid" 2>/dev/null
        wait "$jpid" 2>/dev/null
        FAILED=$((FAILED + 1))
        cleanup_scene "$scene"
        return 1
    fi

    kill "$jpid" 2>/dev/null
    wait "$jpid" 2>/dev/null

    local out
    out=$(python "$ANALYZE" "histo_${scene}.txt" --json 2>/tmp/why_an_err) || {
        echo "analyze 失败: $(cat /tmp/why_an_err)"
        FAILED=$((FAILED + 1))
        cleanup_scene "$scene"
        return 1
    }

    local cat maxcls ratio
    cat=$(echo "$out" | python -c "import json,sys;print(json.load(sys.stdin)['category'])")
    maxcls=$(echo "$out" | python -c "import json,sys;d=json.load(sys.stdin);print(d['max_class'])")
    ratio=$(echo "$out" | python -c "import json,sys;d=json.load(sys.stdin);print(round(d['max_ratio'],3))")

    local ok=1
    if [ "$cat" != "$expect" ]; then
        ok=0
    fi
    if [ "$expect_top" != "-" ] && [ "$maxcls" != "$expect_top" ]; then
        ok=0
    fi

    if [ "$ok" -eq 1 ]; then
        echo "PASS  category=$cat Top1=$maxcls 占 $ratio"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL  category=$cat (期望 $expect) | Top1=$maxcls (期望 $expect_top) 占 $ratio"
        FAILED=$((FAILED + 1))
    fi
    cleanup_scene "$scene"
    echo ""
}

if [ $# -gt 0 ]; then
    run_one "$1"
else
    for scene in StaticListLeak ThreadLocalLeak CacheLeak HugeObjectOOM HeapTooSmall; do
        run_one "$scene"
    done
fi

echo "合计 PASS=$PASSED FAIL=$FAILED"
if [ "$FAILED" -ne 0 ]; then
    exit 1
fi
exit 0
