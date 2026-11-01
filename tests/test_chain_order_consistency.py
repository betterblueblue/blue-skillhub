#!/usr/bin/env python3
"""intent-chain 的先后顺序在各份文档里必须一致。

链路顺序在好几份文档里各写了一遍（各技能 README 的「第 N 步」、安装清单、契约矩阵、
ask-blue 的路由表……），插入或调换环节时容易漏改其中一处。以
skills/_common/chain_validate.py 的 PIPELINE 为准，检查两件事：

  1. 同一行里用箭头（→ / ->）直接相连的两个链路技能，前一个在 PIPELINE 里必须排在前面。
     中间隔着表格竖线 | 的不算相连（比如「缺陷回 /intent-dev」是另一列里的回流说明）。
  2. 链路技能 README 里写的「链路的第 N 步」，N 必须等于它在 PIPELINE 里的位置。

只查对 git 可见的现行文档；docs/archive、CHANGELOG、validation-runs、eval 这类历史记录不查。

Run:
  python tests/test_chain_order_consistency.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "_common"))
try:
    from chain_validate import PIPELINE  # noqa: E402
finally:
    sys.path.pop(0)

CHAIN = [script.split("/", 1)[0] for script, _label, _inputs in PIPELINE]
NAME_RE = re.compile(
    r"intent-(?:" + "|".join(name[len("intent-"):] for name in CHAIN) + r")(?![a-z-])"
)
ARROW_RE = re.compile(r"→|->")
STEP_RE = re.compile(r"链路的第\s*(\d+)\s*步")

# 现行文档：根目录说明、docs 顶层（不含 archive）、各技能的 SKILL/README/references/templates
DOC_PATHSPECS = [
    ":(glob)README.md",
    ":(glob)QUICKSTART.md",
    ":(glob)docs/*.md",
    ":(glob)docs/skills/*.md",
    ":(glob)docs/adr/*.md",
    ":(glob)skills/*/SKILL.md",
    ":(glob)skills/*/README.md",
    ":(glob)skills/*/references/**/*.md",
    ":(glob)skills/*/templates/**/*.md",
]


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _docs() -> list[Path]:
    listed = _git("ls-files", "--cached", "--others", "--exclude-standard", "--", *DOC_PATHSPECS)
    return [ROOT / rel for rel in sorted(set(listed.stdout.splitlines())) if (ROOT / rel).is_file()]


def _arrow_edges(line: str) -> list[tuple[str, str]]:
    """返回一行里用箭头直接相连的 (前, 后) 链路技能对。"""
    names = list(NAME_RE.finditer(line))
    edges = []
    for first, second in zip(names, names[1:]):
        between = line[first.end():second.start()]
        if ARROW_RE.search(between) and "|" not in between:
            edges.append((first.group(0), second.group(0)))
    return edges


def _is_backwards(edge: tuple[str, str]) -> bool:
    return CHAIN.index(edge[0]) >= CHAIN.index(edge[1])


class TestEdgeDetection(unittest.TestCase):
    """先确认检查规则本身认得出顺序写反。"""

    def test_forward_chain_passes(self):
        edges = _arrow_edges("intent-anchor → **intent-prd** → intent-design（仅 UI）→ intent-visual")
        self.assertEqual(len(edges), 3)
        self.assertFalse(any(_is_backwards(e) for e in edges))

    def test_swapped_order_is_caught(self):
        edges = _arrow_edges("intent-dev → intent-verify → intent-adversarial")
        self.assertEqual([e for e in edges if _is_backwards(e)], [("intent-verify", "intent-adversarial")])

    def test_table_cell_boundary_is_not_an_edge(self):
        line = "| 交付前 | `/intent-adversarial` → `/intent-verify` | 缺陷回 `/intent-dev` 修 |"
        self.assertEqual(_arrow_edges(line), [("intent-adversarial", "intent-verify")])


class TestChainOrderConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("git") is None or _git("rev-parse", "--git-dir").returncode != 0:
            raise unittest.SkipTest("需要在 git 工作树里运行")

    def test_pipeline_names_real_skills(self):
        self.assertEqual(len(CHAIN), len(set(CHAIN)), f"PIPELINE 里有重复技能：{CHAIN}")
        missing = [name for name in CHAIN if not (ROOT / "skills" / name / "SKILL.md").is_file()]
        self.assertFalse(missing, f"PIPELINE 指向不存在的技能：{missing}")

    def test_arrows_follow_pipeline_order(self):
        problems: list[str] = []
        edge_count = 0
        for path in _docs():
            rel = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                for edge in _arrow_edges(line):
                    edge_count += 1
                    if _is_backwards(edge):
                        problems.append(f"{rel}:{lineno}: {edge[0]} → {edge[1]}")
        self.assertGreater(edge_count, 0, "一处链路箭头都没找到，检查规则可能失效了")
        self.assertFalse(
            problems,
            "这些地方的先后顺序和 PIPELINE 不一致：\n" + "\n".join(problems)
            + f"\nPIPELINE 顺序：{' → '.join(CHAIN)}",
        )

    def test_readme_step_numbers_match_pipeline(self):
        problems: list[str] = []
        checked = 0
        for position, name in enumerate(CHAIN, 1):
            readme = ROOT / "skills" / name / "README.md"
            if not readme.is_file():
                continue
            for lineno, line in enumerate(readme.read_text(encoding="utf-8").splitlines(), 1):
                match = STEP_RE.search(line)
                if not match:
                    continue
                checked += 1
                if int(match.group(1)) != position:
                    problems.append(
                        f"skills/{name}/README.md:{lineno}: 写的是第 {match.group(1)} 步，PIPELINE 里是第 {position} 步"
                    )
        self.assertGreater(checked, 0, "没找到任何「链路的第 N 步」，检查规则可能失效了")
        self.assertFalse(problems, "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
