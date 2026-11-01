#!/usr/bin/env python3
"""每个带校验器的技能，测试都必须对 git 可见。

.gitignore 默认忽略 skills/*/tests/（e2e 夹具和克隆项目太大），再逐个技能放行。
新技能忘了放行时，测试文件在本地存在、也跑得通，却从没进过 git，CI 也跑不到。
2026-07-26 修过一次；后来新增的 intent-adversarial、intent-visual 又踩了一次，
连带 _common 的链路测试在干净检出里找不到 intent-visual 的夹具而报错。

两项检查：
  1. 凡有 *_validate.py 的技能（整目录不入库的私有技能除外），tests/ 下至少有一个
     对 git 可见（已跟踪，或未跟踪但没被忽略）的 test_*.py。CI 的干净检出里等价于「已跟踪」。
  2. skills/*/tests/ 下不得有被 .gitignore 吞掉的文件（缓存目录和 impact 的 e2e 工作目录除外）。
     这项只在本地有意义；CI 检出里没有被忽略的文件，自然通过。

Run:
  python tests/test_skill_tests_tracked.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

# 允许被忽略的测试目录内容：缓存，以及 impact 端到端测试的大工作目录
ALLOWED_IGNORED = (
    re.compile(r"/(__pycache__|\.pytest_cache)/"),
    re.compile(r"^skills/impact/tests/e2e/workdirs/"),
)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _is_private(skill_dir: Path) -> bool:
    """整个技能目录都不入库（如 blue-interview）。"""
    rel = skill_dir.relative_to(ROOT).as_posix()
    return _git("check-ignore", "-q", f"{rel}/").returncode == 0


class TestSkillTestsTracked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("git") is None or _git("rev-parse", "--git-dir").returncode != 0:
            raise unittest.SkipTest("需要在 git 工作树里运行")

    def test_validator_skills_have_visible_tests(self):
        problems: list[str] = []
        for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")):
            validators = list(skill_dir.glob("scripts/*_validate.py")) + list(skill_dir.glob("*_validate.py"))
            if not validators or _is_private(skill_dir):
                continue
            rel = skill_dir.relative_to(ROOT).as_posix()
            visible = _git("ls-files", "--cached", "--others", "--exclude-standard", "--", f"{rel}/tests").stdout.splitlines()
            if not any(re.search(r"/test_[^/]+\.py$", path) for path in visible):
                problems.append(f"{rel}：有 {validators[0].name}，但 tests/ 下没有对 git 可见的 test_*.py")
        self.assertFalse(problems, "\n".join(problems) + "\n检查 .gitignore 的「测试产物」放行清单。")

    def test_no_test_files_silently_ignored(self):
        ignored = _git("ls-files", "--others", "--ignored", "--exclude-standard", "--", "skills/").stdout.splitlines()
        private_prefixes = tuple(
            f"{p.relative_to(ROOT).as_posix()}/"
            for p in SKILLS.iterdir() if p.is_dir() and _is_private(p)
        )
        swallowed = [
            path for path in ignored
            if re.match(r"^skills/[^/]+/tests/", path)
            and not path.startswith(private_prefixes)
            and not any(pattern.search(path) for pattern in ALLOWED_IGNORED)
        ]
        self.assertFalse(
            swallowed,
            "这些测试文件被 .gitignore 忽略，不会进 git，CI 也跑不到：\n"
            + "\n".join(swallowed[:20])
            + "\n在 .gitignore 的「测试产物」放行清单里加上对应技能。",
        )


if __name__ == "__main__":
    unittest.main()
