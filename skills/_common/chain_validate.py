#!/usr/bin/env python3
"""intent-chain 链路目录批量校验。

一条命令对整个链路目录跑全部六个校验器，按流水线顺序输出结果矩阵。
用途：上游文档修订后快速确认下游是否需要同步——六个校验器本身就带
交叉检查，重跑一遍就是波及探测。

用法：
  python chain_validate.py /path/to/intent-chain/{链路目录}

行为：
  - intent.md 必须存在（链路起点），缺失直接 FAIL
  - 其余文件按流水线顺序校验；尚未产出的标「跳过」（链路做到一半是常态）
  - dev-record 全部工单 done 但 verify-record.md 未产出 → FAIL（验收不能被口头跳过）
  - 已产出但前置文件缺失的组合标 FAIL
  - 退出码：任一 FAIL → 1；全部 PASS / 合法跳过 → 0
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent.parent

# (校验器相对路径, 显示名, 输入文件列表——第一个是被校验对象，其余是前置)
PIPELINE = [
    ("intent-anchor/scripts/intent_validate.py", "intent.md",
     ["intent.md"]),
    ("intent-prd/scripts/prd_validate.py", "prd.md",
     ["prd.md", "intent.md"]),
    ("intent-design/scripts/design_validate.py", "architecture.md + design.md",
     ["architecture.md", "design.md", "intent.md"]),
    ("intent-issues/scripts/issues_validate.py", "issues.md",
     ["issues.md", "intent.md", "prd.md", "architecture.md"]),
    ("intent-dev/scripts/dev_validate.py", "dev-record.md",
     ["dev-record.md", "issues.md"]),
    ("intent-adversarial/scripts/adversarial_validate.py", "adversarial-record.md",
     ["adversarial-record.md", "intent.md"]),
    ("intent-verify/scripts/verify_validate.py", "verify-record.md",
     ["verify-record.md", "intent.md", "architecture.md", "design.md"]),
]


def _dev_all_done(chain_dir: Path) -> bool:
    """dev-record 是否已全部工单 done（链级门禁：完成后必须产出验收记录）。"""
    dev_path = chain_dir / "dev-record.md"
    issues_path = chain_dir / "issues.md"
    if not dev_path.exists() or not issues_path.exists():
        return False
    dev_text = dev_path.read_text(encoding="utf-8", errors="replace")
    issues_text = issues_path.read_text(encoding="utf-8", errors="replace")
    done_count = len(re.findall(r"^-\s*状态[：:]\s*done", dev_text, re.MULTILINE | re.IGNORECASE))
    issue_count = len(re.findall(r"^##\s+Issue\s+\d+", issues_text, re.MULTILINE))
    return issue_count > 0 and done_count >= issue_count


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python chain_validate.py /path/to/intent-chain/{链路目录}")
        return 1

    chain_dir = Path(sys.argv[1])
    if not chain_dir.is_dir():
        print(f"FAIL: 链路目录不存在: {chain_dir}")
        return 1

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    rows: list[tuple[str, str, str]] = []
    exit_code = 0

    for script_rel, label, inputs in PIPELINE:
        target = chain_dir / inputs[0]
        if not target.exists():
            if inputs[0] == "intent.md":
                rows.append((label, "FAIL", "intent.md 不存在——链路起点缺失"))
                exit_code = 1
            elif inputs[0] == "adversarial-record.md" and _dev_all_done(chain_dir):
                rows.append((label, "FAIL", "dev-record 全部工单 done，但 adversarial-record.md 未产出——对抗性验证（安全攻击/性能/并发一致性）不能被跳过"))
                exit_code = 1
            elif inputs[0] == "verify-record.md" and _dev_all_done(chain_dir):
                rows.append((label, "FAIL", "dev-record 全部工单 done，但 verify-record.md 未产出"))
                exit_code = 1
            else:
                rows.append((label, "跳过", "尚未产出"))
            continue
        missing = [name for name in inputs[1:] if not (chain_dir / name).exists()]
        if missing:
            rows.append((label, "FAIL", f"前置文件缺失: {', '.join(missing)}"))
            exit_code = 1
            continue
        cmd = [sys.executable, str(SKILLS_ROOT / script_rel)]
        cmd += [str(chain_dir / name) for name in inputs]
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )
        if proc.returncode == 0:
            rows.append((label, "PASS", ""))
        else:
            exit_code = 1
            fail_lines = [
                line.strip() for line in (proc.stdout or "").splitlines()
                if "FAIL" in line
            ]
            summary = "; ".join(fail_lines[:3]) if fail_lines else (proc.stderr or "").strip()[:200]
            rows.append((label, "FAIL", summary))

    # D5 漂移交叉检查：推迟/放弃项是否回流到下游实现承载区（见 d5_check.py）
    if (chain_dir / "intent.md").exists():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from d5_check import check as d5_run
            from term_check import check as term_run
        finally:
            sys.path.pop(0)
        d5_passes, d5_fails = d5_run(chain_dir)
        if d5_fails:
            exit_code = 1
            rows.append(("D5 漂移交叉检查", "FAIL", "; ".join(d5_fails[:3])))
        else:
            rows.append(("D5 漂移交叉检查", "PASS", d5_passes[0] if d5_passes else ""))
        # 术语落地交叉检查：原始术语不得出现在前端源码用户可见内容（见 term_check.py）
        term_passes, term_fails = term_run(chain_dir)
        if term_fails:
            exit_code = 1
            rows.append(("术语落地交叉检查", "FAIL", "; ".join(term_fails[:3])))
        else:
            rows.append(("术语落地交叉检查", "PASS", term_passes[0] if term_passes else ""))
    else:
        rows.append(("D5 漂移交叉检查", "跳过", "intent.md 缺失"))
        rows.append(("术语落地交叉检查", "跳过", "intent.md 缺失"))

    print(f"\n{'=' * 60}")
    print(f"intent-chain 链路校验: {chain_dir}")
    print(f"{'=' * 60}")
    for label, status, note in rows:
        mark = {"PASS": "[PASS]", "FAIL": "[FAIL]", "跳过": "[跳过]"}[status]
        print(f"  {mark} {label}" + (f" — {note}" if note else ""))
    passed = sum(1 for row in rows if row[1] == "PASS")
    skipped = sum(1 for row in rows if row[1] == "跳过")
    failed = sum(1 for row in rows if row[1] == "FAIL")
    print(f"\n  PASS: {passed}  跳过: {skipped}  FAIL: {failed}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
