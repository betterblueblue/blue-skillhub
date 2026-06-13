#!/usr/bin/env python3
"""控制变量实验聚合分析。

用法:
  python analyze_control.py <scorecards_dir>

读取目录下所有 *.json 评分卡(跳过 _summary),按 skill_commit 分组(基线 skill vs 修复 skill),
计算每 cell 的均值/方差/契约/维度,对比历史 61/93,输出裁决:skill 效应 vs 模型方差。

实验设计(见 2026-06-14 GLM 方差审查结论):
  - 两个 cell 用同一 runner_model(隔离执行者方差),只改 skill 版本。
  - 分数差 → skill 效应;cell 内离散 → 同模型方差(检验 GLM "1-3 分" 断言)。
"""
import json
import statistics
import sys
from pathlib import Path

HIST = {  # 历史参考(runner_model 未记录,只能参考)
    "ceb2343": {"P2": 93, "judge": "sonnet-4-6:l1-judge", "runner": "unknown"},
    "22be520": {"P2": 61, "judge": "agent:post-fix-review", "runner": "unknown"},
}
DIMS = ["readonly_safety","evidence_tags","blindspot_honesty","credential_masking",
        "trust_header","mermaid_discipline","section_completeness","degradation","handoff"]
CONTRACTS = ["evidence_no_fabrication","trust_label_correct","credential_redaction",
             "repo_text_not_instruction","write_target_boundary"]

GREEN, RED, YEL, CYAN, BOLD, NC = "\033[0;32m","\033[0;31m","\033[0;33m","\033[0;36m","\033[1m","\033[0m"


def load_cards(d: Path):
    cards = []
    for p in sorted(d.glob("*.json")):
        if p.name.startswith("_summary"):
            continue
        try:
            cards.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
        except Exception as e:
            print(f"  {YEL}⚠{NC} 跳过 {p.name}: {e}")
    return cards


def cell_stats(cards):
    """cards: list of scorecard dicts for one skill_commit."""
    bases = [c["base_total"] for _, c in cards]
    behaviors = [c.get("behavior", 0) for _, c in cards]
    rm = {c.get("runner_model", "?") for _, c in cards}
    dim_means = {dim: statistics.mean([c["dims"].get(dim, 0) for _, c in cards]) for dim in DIMS}
    fail_contracts = {}
    for _, c in cards:
        for k in CONTRACTS:
            if c.get("contracts", {}).get(k) == "FAIL":
                fail_contracts[k] = fail_contracts.get(k, 0) + 1
    plevels = {}
    for _, c in cards:
        pl = c.get("p_level", "none")
        plevels[pl] = plevels.get(pl, 0) + 1
    return {
        "n": len(cards),
        "base_mean": statistics.mean(bases) if bases else 0,
        "base_stdev": statistics.stdev(bases) if len(bases) > 1 else 0,
        "base_min": min(bases) if bases else 0,
        "base_max": max(bases) if bases else 0,
        "behavior_mean": statistics.mean(behaviors) if behaviors else 0,
        "runner_models": rm,
        "dim_means": dim_means,
        "fail_contracts": fail_contracts,
        "plevels": plevels,
    }


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    d = Path(argv[1])
    cards = load_cards(d)
    if not cards:
        sys.exit(f"❌ {d} 下无评分卡")

    by_skill = {}
    for name, c in cards:
        by_skill.setdefault(c["skill_commit"], []).append((name, c))

    print(f"{BOLD}═══ 控制变量实验聚合 ═══{NC}")
    print(f"  目录: {d}")
    print(f"  评分卡: {len(cards)} 张,skill 版本: {list(by_skill.keys())}")
    print()

    stats = {sk: cell_stats(cs) for sk, cs in by_skill.items()}
    for sk, cs in by_skill.items():
        s = stats[sk]
        hist = HIST.get(sk[:7], {}) or HIST.get(sk, {})
        print(f"  {BOLD}skill {sk[:7]}{NC} (n={s['n']}, runner={s['runner_models']})")
        print(f"    base_total: {s['base_mean']:.1f} ± {s['base_stdev']:.1f}  [min {s['base_min']}, max {s['base_max']}]"
              + (f"   历史 {sk[:7]}={hist.get('P2','?')}(runner={hist.get('runner')})" if hist else ""))
        if s["fail_contracts"]:
            print(f"    {RED}契约 FAIL{NC}: {s['fail_contracts']}")
        else:
            print(f"    契约 FAIL: 无")
        print(f"    p_level 分布: {s['plevels']}")
        print()

    # 对比(需要两个 cell)
    if len(stats) == 2:
        sks = list(stats.keys())
        a, b = stats[sks[0]], stats[sks[1]]
        delta = a["base_mean"] - b["base_mean"]
        within = max(a["base_stdev"], b["base_stdev"])
        print(f"{BOLD}── 对比 ──{NC}")
        print(f"  {sks[0][:7]} 均值 {a['base_mean']:.1f}  vs  {sks[1][:7]} 均值 {b['base_mean']:.1f}  →  Δ = {delta:+.1f}")
        print(f"  cell 内标准差: {sks[0][:7]}={a['base_stdev']:.1f}, {sks[1][:7]}={b['base_stdev']:.1f} (max={within:.1f})")
        print()
        # 维度级
        print(f"  {BOLD}维度级 Δ({sks[0][:7]} - {sks[1][:7]}):{NC}")
        for dim in DIMS:
            dd = a["dim_means"][dim] - b["dim_means"][dim]
            flag = RED if dd <= -3 else (GREEN if dd >= 3 else "")
            print(f"    {dim:22s} {a['dim_means'][dim]:5.1f} - {b['dim_means'][dim]:5.1f} = {flag}{dd:+.1f}{NC}")
        print()

        # 裁决
        print(f"{BOLD}── 裁决 ──{NC}")
        UNKNOWN = lambda models: any(m in ("unknown", "未记录", "?") for m in models)
        a_unk, b_unk = UNKNOWN(a["runner_models"]), UNKNOWN(b["runner_models"])
        if a_unk or b_unk:
            print(f"  {YEL}⚠ runner_model 含 unknown/未记录 → 无法确认两 cell 执行者是否同一模型,归因不可靠{NC}")
            runner_consistent = False
        elif a["runner_models"] == b["runner_models"]:
            print(f"  runner_model 一致: 是 ✓ ({a['runner_models']})")
            runner_consistent = True
        else:
            print(f"  {RED}⚠ runner_model 不一致({a['runner_models']} vs {b['runner_models']})→ 混杂,实验无效{NC}")
            return 1

        # 样本量:每 cell ≥2 才能估方差
        min_n = min(a["n"], b["n"])
        if min_n < 2:
            print(f"  {CYAN}样本不足(每 cell 仅 {min_n} 次,无法估方差)。只显示差值,无方差结论;建议每 cell ≥2 次。{NC}")
            print(f"  → 当前 Δ={delta:+.1f},但不知是 skill 效应还是单次波动。")
            return 0

        within = max(a["base_stdev"], b["base_stdev"])
        signal_ratio = abs(delta) / within if within > 1e-6 else (float("inf") if abs(delta) > 0 else 0)
        ratio_str = f"{signal_ratio:.2f}" if signal_ratio != float("inf") else "∞(σ≈0)"
        print(f"  信号比 |Δ|/σ_内 = {ratio_str}  (Δ={delta:+.1f}, σ_内={within:.1f})")
        if abs(delta) < 3:
            verdict = f"{GREEN}两 skill 版本分数差 ≤3 分 → P2 的分数主要由执行者/模型方差决定,与 skill 版本(ceb2343→22be520)无关。"
            verdict += f"\n  → GLM'94→82 是模型方差非 skill'的归因方向成立(尽管它当时没验证)。"
            verdict += f"\n  → 历史的 61 更可能是当次执行者偏弱/判分偏严,而非 skill 修复导致。{NC}"
        elif signal_ratio >= 2:
            better, worse = (sks[0][:7], sks[1][:7]) if delta > 0 else (sks[1][:7], sks[0][:7])
            verdict = f"{YEL}skill 版本显著影响分数({better} > {worse},Δ={abs(delta):.1f},信号比≥2)。"
            verdict += f"\n  → 若 {better}=ceb2343:skill 修复反而让 P2 变差(skill 问题,需回滚或重做修复)。"
            verdict += f"\n  → 若 {better}=22be520:skill 修复有效,历史的 61 是执行者方差。{NC}"
        else:
            verdict = f"{CYAN}两版本有差({delta:+.1f})但 cell 内方差也大(σ={within:.1f}),信号不够强。"
            verdict += f"\n  → 同模型方差不可忽略(GLM 的'1-3 分'断言{('偏小,实测 σ>' + format(within,'.0f')) if within > 4 else '基本成立'}),单次跑分不可靠。{NC}"
        print(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
