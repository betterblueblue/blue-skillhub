#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""whydump analyze — 解析 JDK 工具输出的堆分析脚本（单文件，零第三方依赖）。

输入是 JDK 自带工具产生的文本，不是二进制：
  - `jcmd <pid> GC.class_histogram -all`（JDK 9+，零停顿）/
    `jmap -histo:live <pid>`（本地低峰）或 `jhsdb jmap --histo --pid <pid>` → 类直方图
  - `jcmd <pid> VM.flags` → 堆参数（可选，用于展示 MaxHeapSize 等）

输出是「数字层 + 判断层」：
  - 数字层：Top N 类、占比、堆配置 —— 纯算术，机械可靠
  - 判断层：单类大头 → 疑似泄漏；分布平均 → 倾向堆设小。只给证据和提示，不拍死。

用法：
  python analyze.py histo.txt
  python analyze.py histo.txt --flags vmflags.txt
  python analyze.py - < histo.txt          # 从 stdin 读
  python analyze.py histo.txt --json       # 结构化输出
  python analyze.py histo.txt --top 20
  python analyze.py histo.txt --leak-threshold 0.5
  python analyze.py --compare histo_a.txt histo_b.txt [--flags vmflags.txt]
                                           # 对比两份直方图（间隔 ≥10 分钟抓取），
                                           # 按实例数增量识别增长主导类

退出码：0 成功（无论判定为泄漏还是堆小）；1 输入无法解析（没有任何有效行）。
单张直方图分不清「泄漏」和「合法大缓存」——看增长才是实锤：
同一进程间隔一段时间抓两份，实例数持续增长的类才是泄漏候选。
"""

import argparse
import json
import re
import sys
from collections import namedtuple

# ---------------------------------------------------------------------------
# 输入解析
# ---------------------------------------------------------------------------

ClassEntry = namedtuple("ClassEntry", ["name", "instances", "bytes"])

# jmap -histo:live 行：
#      1:        1024        1048576  [I
#      2:          512          32768  com.example.MyClass (module)
#      3:          1,200      1,258,291,200  [B     （部分 JDK 数字带千分位逗号）
# 列：num:  #instances  #bytes  class name (module)
_HISTO_LINE = re.compile(r"^\s*\d+:\s+([\d,]+)\s+([\d,]+)\s+(.*)$")


def parse_histo(text: str) -> list[ClassEntry]:
    """解析 jmap/jhsdb 的类直方图文本，返回 ClassEntry 列表（按字节降序保留原始顺序）。

    对每一行：num: instances bytes classname (module)
    - 数字带千分位逗号时先去掉（jhsdb 有时输出 1,048,576）。
    - class name 里可能含空格（数组类如 `[Ljava.lang.Object;` 不含，但保险起见
      只去掉行尾可选的 `(module)` 后缀，其余保持原样）。
    """
    entries = []
    for raw in text.splitlines():
        m = _HISTO_LINE.match(raw)
        if not m:
            continue
        instances, nbytes, cls = m.group(1), m.group(2), m.group(3).strip()
        try:
            instances = int(instances.replace(",", ""))
            nbytes = int(nbytes.replace(",", ""))
        except ValueError:
            continue
        if not cls:
            continue
        # 去掉可选的 "(module)" 后缀
        cls = re.sub(r"\s*\([^)]*\)\s*$", "", cls).strip()
        if not cls:
            continue
        entries.append(ClassEntry(cls, instances, nbytes))
    return entries


# jcmd <pid> VM.flags 的输出是**一整行**（所有 flag 空格分隔），如：
#    -XX:CICompilerCount=2 -XX:InitialHeapSize=67108864 -XX:MaxHeapSize=1073741824 ...
_FLAGS_HEAP = re.compile(r"-XX:(MaxHeapSize|InitialHeapSize|MaxMetaspaceSize)=(\d+)")


def parse_flags(text: str) -> dict[str, int]:
    """从 jcmd VM.flags 输出里提取堆大小参数，返回 {参数名: 字节数}。

    真实 jcmd 输出是单行多 flag，必须逐行 finditer，search 只会拿到第一个。
    """
    result = {}
    for line in text.splitlines():
        for m in _FLAGS_HEAP.finditer(line):
            result[m.group(1)] = int(m.group(2))
    return result


# jmap 直方图末尾的 Total 行（冒号有无依 JDK 版本而定）：
#    Total         5500       1286691200
#    Total    :        5500       1286691200
_TOTAL_LINE = re.compile(r"^\s*Total\s*:?\s+([\d,]+)\s+([\d,]+)\s*$", re.IGNORECASE)


def parse_total(text: str) -> int | None:
    """提取直方图末尾 Total 行的总字节数，用于交叉核对输入是否被截断。

    jhsdb 等输出没有这一行时返回 None（无法核对，不告警）。
    """
    for raw in text.splitlines():
        m = _TOTAL_LINE.match(raw)
        if m:
            return int(m.group(2).replace(",", ""))
    return None


# ---------------------------------------------------------------------------
# 判断层
# ---------------------------------------------------------------------------

def top_classes(entries: list[ClassEntry], n: int = 10) -> list[ClassEntry]:
    """按字节数降序取前 n 个类。"""
    return sorted(entries, key=lambda e: e.bytes, reverse=True)[:n]


def classify(entries: list[ClassEntry], leak_threshold: float) -> dict:
    """分类诊断：疑似泄漏 vs 无典型泄漏大头（倾向堆设小）。

    规则（第一版，机械可判）：
      - 总字节 > 0 且最大类占比 >= leak_threshold → 疑似泄漏，指向该类
      - 否则 → 无单类异常大头
    不判定真伪：泄漏类也可能是缓存系统/业务大集合的合法占用，
    因此结论总是「疑似 + 证据」，留给人和 AI 反查。
    """
    total_bytes = sum(e.bytes for e in entries)
    total_instances = sum(e.instances for e in entries)
    if total_bytes <= 0:
        return {"category": "no-data", "total_bytes": 0, "total_instances": 0,
                "max_class": None, "max_ratio": 0.0, "top3_ratio": 0.0,
                "verdict": "no usable data"}

    top = top_classes(entries, 1)[0]
    max_ratio = top.bytes / total_bytes
    # 前 3 类合计占比：泄漏摊到多个类（如 byte[] + char[] + HashMap Node）时，
    # 单类占比可能都不高，但合计会明显偏高。只作证据提示，不改 category 判定。
    top3_ratio = sum(e.bytes for e in top_classes(entries, 3)) / total_bytes

    if max_ratio >= leak_threshold:
        verdict = f"疑似泄漏：单类 {top.name} 占堆 {max_ratio:.1%}（{top.bytes} 字节），远超其他类"
        category = "leak-suspect"
    else:
        verdict = f"无单类异常大头（最大类 {top.name} 占 {max_ratio:.1%}），倾向堆设小或需进一步看 GC 日志"
        category = "no-dominant-class"

    return {
        "category": category,
        "total_bytes": total_bytes,
        "total_instances": total_instances,
        "max_class": top.name,
        "max_ratio": max_ratio,
        "top3_ratio": top3_ratio,
        "verdict": verdict,
    }


def compare_histos(entries_a: list[ClassEntry], entries_b: list[ClassEntry],
                   n: int = 10) -> dict:
    """对比两份直方图，按实例数增量识别「增长主导类」。

    单张直方图分不清「泄漏」和「合法大缓存」：只有隔一段时间抓两张，
    实例数持续增长的类才是泄漏候选；不涨的是静态占用（缓存/业务大表）。

    规则（机械可判，结论仍是疑似）：
      - 每个类 delta_i = 第二份实例数 - 第一份实例数，按 delta_i 降序取 Top N
      - growth-suspect：增量最大且为正的类，增量 >= 100、字节没有缩水、
        且占全部正增量 >= 30% —— 疑似增长型泄漏，指向该类
      - 否则 no-clear-growth：没有明显单点增长，倾向静态占用/分布增长
    类名口径不一致（jmap 的 [B vs jhsdb 的 byte[]）时返回 compare-mismatch：
    不给增长结论、只提示重抓——脚本契约不背书不可信的对比。
    """
    ta_i = sum(e.instances for e in entries_a)
    ta_b = sum(e.bytes for e in entries_a)
    tb_i = sum(e.instances for e in entries_b)
    tb_b = sum(e.bytes for e in entries_b)

    by_class: dict[str, list] = {}
    for e in entries_a:
        by_class.setdefault(e.name, [None, None])[0] = e
    for e in entries_b:
        by_class.setdefault(e.name, [None, None])[1] = e

    rows = []
    matched_bytes_a = 0
    for name, (ea, eb) in by_class.items():
        ia = ea.instances if ea else 0
        ib = eb.instances if eb else 0
        ba = ea.bytes if ea else 0
        bb = eb.bytes if eb else 0
        if ea is not None and eb is not None:
            matched_bytes_a += ba
        rows.append({
            "name": name,
            "instances_a": ia, "instances_b": ib,
            "bytes_a": ba, "bytes_b": bb,
            "delta_i": ib - ia, "delta_b": bb - ba,
        })
    rows.sort(key=lambda r: (-r["delta_i"], -r["delta_b"]))

    # 类名口径检测：第一份里能对上的字节占比。jmap 的 [B 和 jhsdb 的 byte[]
    # 写法不同，混着对比会全 miss，此时结论不可信。
    # mismatch 时必须短路成 compare-mismatch：不给 growth 结论、不背书，
    # 不能指望调用方（agent/脚本）都去读文本里的警告行。
    matched_ratio = matched_bytes_a / ta_b if ta_b else 1.0
    mismatch = matched_ratio < 0.8

    inst_delta = tb_i - ta_i
    byte_delta = tb_b - ta_b

    if mismatch:
        return {
            "category": "compare-mismatch",
            "verdict": ("两份直方图类名匹配率低（jmap 的 [B 与 jhsdb 的 byte[] 写法不同，"
                        "或混用了不同 pid/工具），对比不可靠：先确认同一种工具、同一个 pid "
                        "重抓，再下结论"),
            "total_a": {"instances": ta_i, "bytes": ta_b},
            "total_b": {"instances": tb_i, "bytes": tb_b},
            "inst_delta": inst_delta,
            "byte_delta": byte_delta,
            "mismatch": True,
            "matched_ratio": matched_ratio,
            "hint": "先重抓：同一轮排查用同一种工具、同一个 pid，间隔 ≥10 分钟",
            "top_growth": None,
            "top": rows[:n],
        }

    pos_sum = sum(max(r["delta_i"], 0) for r in rows)
    top = rows[0] if rows and rows[0]["delta_i"] > 0 else None

    growth = False
    if top and pos_sum > 0:
        growth = (top["delta_i"] >= 100
                  and top["delta_i"] / pos_sum >= 0.3
                  and top["delta_b"] >= 0)

    if growth:
        category = "growth-suspect"
        verdict = (
            f"疑似泄漏：{top['name']} 实例数从 {top['instances_a']:,} "
            f"涨到 {top['instances_b']:,}（+{top['delta_i']:,}，"
            f"占全部正增量的 {top['delta_i'] / pos_sum:.0%}），"
            f"字节 {top['bytes_a']:,} → {top['bytes_b']:,}"
        )
    else:
        category = "no-clear-growth"
        verdict = ("两次采样没有类的实例数出现显著单点增长，"
                   "倾向静态占用（缓存/业务大表）或分布增长，不是增长型泄漏；"
                   "若仍 OOM，结合 GC 日志看堆峰值与 Full GC 频率")
        if top:
            verdict += f"（增量最大类：{top['name']} +{top['delta_i']:,}）"

    inst_delta = tb_i - ta_i
    byte_delta = tb_b - ta_b
    hint = ""
    if abs(inst_delta) <= max(ta_i * 0.05, 1) and (top is None or top["delta_i"] < 100):
        hint = ("两次采样总量几乎没变，可能间隔太短看不出增长；"
                "建议间隔 ≥ 10 分钟再抓一份对比")

    return {
        "category": category,
        "verdict": verdict,
        "total_a": {"instances": ta_i, "bytes": ta_b},
        "total_b": {"instances": tb_i, "bytes": tb_b},
        "inst_delta": inst_delta,
        "byte_delta": byte_delta,
        "mismatch": mismatch,
        "matched_ratio": matched_ratio,
        "hint": hint,
        "top_growth": top,
        "top": rows[:n],
    }


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def _fmt_bytes(n: int) -> str:
    if n >= 1 << 30:
        return f"{n / (1 << 30):.2f} GB"
    if n >= 1 << 20:
        return f"{n / (1 << 20):.2f} MB"
    if n >= 1 << 10:
        return f"{n / (1 << 10):.1f} KB"
    return f"{n} B"


def render_report(entries, top_n, flags, diag) -> str:
    lines = []
    if diag.get("truncated"):
        lines.append(f"!! 疑似截断的直方图：解析行合计只占 Total 行的 {diag['parsed_ratio']:.1%}，"
                     "单类占比被抬高、可能虚报泄漏。先拿完整输出（去掉 head/截断）再分析。")
        lines.append("")
    lines.append("== 堆使用概况 ==")
    lines.append(f"总实例数: {diag['total_instances']:,}")
    lines.append(f"总字节数: {diag['total_bytes']:,} ({_fmt_bytes(diag['total_bytes'])})")
    if flags:
        for key, val in flags.items():
            lines.append(f"{key}: {_fmt_bytes(val)} ({val} 字节)")
    elif entries:
        lines.append("(未提供 jcmd VM.flags，堆配置未知)")

    lines.append("")
    lines.append(f"== Top {top_n} 类（按占用字节）==")
    lines.append(f"{'#':>3}  {'实例数':>12}  {'字节数':>14}  {'占比':>7}  类名")
    for i, e in enumerate(top_classes(entries, top_n), 1):
        ratio = e.bytes / diag["total_bytes"] if diag["total_bytes"] else 0.0
        lines.append(
            f"{i:>3}  {e.instances:>12,}  {e.bytes:>14,}  {ratio:>6.1%}  {e.name}"
        )

    lines.append("")
    lines.append("== 结论 ==")
    lines.append(f"[{diag['category']}] {diag['verdict']}")
    if diag["category"] == "leak-suspect" and diag["max_class"]:
        lines.append(f"  证据: Top 1 = {diag['max_class']}, 占堆 {diag['max_ratio']:.1%}")
        lines.append("  建议: 查该类对象被谁引用（GC root）；若是静态集合/缓存持续写入且无淘汰，基本可坐实泄漏。")
    elif diag["category"] == "no-dominant-class":
        lines.append(f"  证据: 最大类 {diag['max_class']} 占 {diag['max_ratio']:.1%}，无异常大头；"
                     f"前 3 类合计占 {diag['top3_ratio']:.1%}")
        lines.append("  建议: 对象分布平均未必是堆小——先看 GC 日志（Full GC 频率/堆峰值），再决定调 -Xmx 还是查代码。")
        if diag["top3_ratio"] >= 0.6:
            lines.append("  提示: 前 3 类合计占比很高。若它们是数组 + 集合内部类的组合"
                         "（如 byte[]/char[]/HashMap$Node），可能是同一泄漏源摊到了多个类，"
                         "建议回代码查这几类的公共写入点。")
    return "\n".join(lines)


def render_compare_report(diag: dict, top_n: int, flags: dict) -> str:
    lines = []
    if diag["mismatch"]:
        lines.append("!! 两份直方图类名匹配率低（jmap 的 [B 和 jhsdb 的 byte[] 写法不同），"
                     "对比可能不可靠：先确认两份是同一种工具抓的，再下结论。")
        lines.append("")
    ta, tb = diag["total_a"], diag["total_b"]
    lines.append("== 两次采样对比 ==")
    lines.append(f"第一份: 实例 {ta['instances']:,}, 字节 {ta['bytes']:,} ({_fmt_bytes(ta['bytes'])})")
    lines.append(f"第二份: 实例 {tb['instances']:,}, 字节 {tb['bytes']:,} ({_fmt_bytes(tb['bytes'])})")
    lines.append(f"实例增量: {diag['inst_delta']:+,}    字节增量: {diag['byte_delta']:+,} "
                 f"({_fmt_bytes(abs(diag['byte_delta']))})")
    if flags:
        for key, val in flags.items():
            lines.append(f"{key}: {_fmt_bytes(val)} ({val} 字节)")

    lines.append("")
    lines.append(f"== Top {top_n} 增长类（按实例数增量）==")
    lines.append(f"{'#':>3}  {'类名':<28}  {'A实例':>11}  {'B实例':>11}  {'+增量':>10}  "
                 f"{'增幅':>7}  {'A字节':>13}  {'B字节':>13}")
    for i, r in enumerate(diag["top"], 1):
        if r["instances_a"] == 0:
            pct_s = "新出现"
        else:
            pct_s = f"{r['delta_i'] / r['instances_a']:+.0%}"
        lines.append(
            f"{i:>3}  {r['name']:<28}  {r['instances_a']:>11,}  {r['instances_b']:>11,}  "
            f"{r['delta_i']:>+10,}  {pct_s:>7}  {r['bytes_a']:>13,}  {r['bytes_b']:>13,}"
        )

    lines.append("")
    lines.append("== 结论 ==")
    lines.append(f"[{diag['category']}] {diag['verdict']}")
    if diag["category"] == "growth-suspect" and diag["top_growth"]:
        lines.append("  建议: 回代码查这个类的写入点；若持续增长且无淘汰 → 基本坐实泄漏。")
    elif diag["category"] == "compare-mismatch":
        lines.append("  建议: 先重抓（同一种工具、同一个 pid、间隔 ≥10 分钟），不要基于这份对比下结论。")
    else:
        lines.append("  建议: 两次对比没看到增长型泄漏，先看 GC 日志（Full GC 频率/堆峰值），"
                     "再决定调 -Xmx 还是继续查代码。")
    if diag["hint"]:
        lines.append(f"  提示: {diag['hint']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def _read_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        print(f"whydump: 无法读取 {path}: {e}", file=sys.stderr)
        return None


def _load_flags(path: str | None) -> dict[str, int]:
    """读取 VM.flags；失败时降级为空 dict 并告警，不中断直方图分析。"""
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return parse_flags(f.read())
    except OSError as e:
        print(f"whydump: 无法读取 {path}: {e}（直方图继续分析，堆配置未知）",
              file=sys.stderr)
        return {}


def _main_compare(args) -> int:
    if args.histo == "-" or not args.histo2:
        print("whydump: --compare 需要两份直方图文件路径（不支持 stdin）",
              file=sys.stderr)
        return 1
    text_a = _read_file(args.histo)
    text_b = _read_file(args.histo2)
    if text_a is None or text_b is None:
        return 1
    entries_a = parse_histo(text_a)
    entries_b = parse_histo(text_b)
    if not entries_a or not entries_b:
        print("whydump: 对比输入里至少有一份没有可解析的直方图行",
              file=sys.stderr)
        return 1
    flags = _load_flags(args.flags)
    diag = compare_histos(entries_a, entries_b, args.top)
    if args.json:
        out = {
            "category": diag["category"],
            "verdict": diag["verdict"],
            "total_a": diag["total_a"],
            "total_b": diag["total_b"],
            "inst_delta": diag["inst_delta"],
            "byte_delta": diag["byte_delta"],
            "mismatch": diag["mismatch"],
            "matched_ratio": diag["matched_ratio"],
            "hint": diag["hint"],
            "top_growth": diag["top_growth"],
            "flags": flags,
            "top": diag["top"],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render_compare_report(diag, args.top, flags))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="解析 JDK 工具（jmap/jcmd）输出的堆分析，给出分类诊断。",
    )
    ap.add_argument("histo", nargs="?", default="-",
                    help="jmap/jcmd 直方图输出文件路径，或 - 表示 stdin")
    ap.add_argument("histo2", nargs="?", default=None,
                    help="第二份直方图文件路径（仅 --compare 模式）")
    ap.add_argument("--compare", action="store_true",
                    help="对比两份直方图，按实例数增量识别增长主导类")
    ap.add_argument("--flags", default=None,
                    help="jcmd <pid> VM.flags 输出文件路径（可选）")
    ap.add_argument("--top", type=int, default=10, help="Top N 类，默认 10")
    ap.add_argument("--leak-threshold", type=float, default=0.5,
                    help="单类占比达到该值判定为疑似泄漏，默认 0.5")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args(argv)

    if args.compare:
        return _main_compare(args)

    if args.histo == "-":
        histo_text = sys.stdin.read()
    else:
        try:
            with open(args.histo, encoding="utf-8", errors="replace") as f:
                histo_text = f.read()
        except OSError as e:
            print(f"whydump: 无法读取 {args.histo}: {e}", file=sys.stderr)
            return 1

    entries = parse_histo(histo_text)
    if not entries:
        print("whydump: 输入里没有可解析的直方图行（确认是 jmap -histo 的输出）",
              file=sys.stderr)
        return 1

    flags = {}
    if args.flags:
        try:
            with open(args.flags, encoding="utf-8", errors="replace") as f:
                flags = parse_flags(f.read())
        except OSError as e:
            print(f"whydump: 无法读取 {args.flags}: {e}（直方图继续分析，堆配置未知）",
                  file=sys.stderr)

    diag = classify(entries, args.leak_threshold)

    # 交叉核对 Total 行：解析行合计明显小于 Total 说明输入被截断（如 head -50 的粘贴），
    # 分母变小会把单类占比抬高、虚报泄漏，必须显式告警而不是照常给结论。
    total_line = parse_total(histo_text)
    diag["truncated"] = None
    diag["parsed_ratio"] = None
    if total_line and total_line > 0:
        diag["parsed_ratio"] = diag["total_bytes"] / total_line
        diag["truncated"] = diag["parsed_ratio"] < 0.95

    if args.json:
        out = {
            "total_bytes": diag["total_bytes"],
            "total_instances": diag["total_instances"],
            "max_class": diag["max_class"],
            "max_ratio": diag["max_ratio"],
            "top3_ratio": diag["top3_ratio"],
            "category": diag["category"],
            "verdict": diag["verdict"],
            "truncated": diag["truncated"],
            "parsed_ratio": diag["parsed_ratio"],
            "flags": flags,
            "top": [
                {"name": e.name, "instances": e.instances, "bytes": e.bytes,
                 "ratio": e.bytes / diag["total_bytes"] if diag["total_bytes"] else 0.0}
                for e in top_classes(entries, args.top)
            ],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render_report(entries, args.top, flags, diag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
