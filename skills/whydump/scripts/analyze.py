#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""whydump analyze — 解析 JDK 工具输出的堆分析脚本（单文件，零第三方依赖）。

输入是 JDK 自带工具产生的文本，不是二进制：
  - `jmap -histo:live <pid>`（或 `jhsdb jmap --histo --pid <pid>`）→ 类直方图
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

退出码：0 成功（无论判定为泄漏还是堆小）；1 输入无法解析（没有任何有效行）。
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


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="解析 JDK 工具（jmap/jcmd）输出的堆分析，给出分类诊断。",
    )
    ap.add_argument("histo", nargs="?", default="-",
                    help="jmap -histo:live 输出文件路径，或 - 表示 stdin")
    ap.add_argument("--flags", default=None,
                    help="jcmd <pid> VM.flags 输出文件路径（可选）")
    ap.add_argument("--top", type=int, default=10, help="Top N 类，默认 10")
    ap.add_argument("--leak-threshold", type=float, default=0.5,
                    help="单类占比达到该值判定为疑似泄漏，默认 0.5")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args(argv)

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
            print(f"whydump: 无法读取 {args.flags}: {e}", file=sys.stderr)
            return 1

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
