#!/usr/bin/env python3
"""Shared contract tests for user-facing Skill improvement prompts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_FILES = (
    ROOT / "skills" / "intent-anchor" / "SKILL.md",
    ROOT / "skills" / "pathfinder" / "SKILL.md",
    ROOT / "skills" / "impact" / "SKILL.md",
)


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"Missing section: {heading}")
    return match.group(1)


class TestSkillImprovementPrompt(unittest.TestCase):
    def test_all_core_skills_keep_the_user_interaction_simple(self):
        for path in SKILL_FILES:
            with self.subTest(skill=path.parent.name):
                content = path.read_text(encoding="utf-8")
                section = _section(content, "## 改进记录提示")
                self.assertIn("要把它记录下来吗？", section)
                self.assertIn("记录", section)
                self.assertIn("不用", section)
                self.assertIn("普通完成不询问", section)
                for internal_term in (
                    "RC-",
                    "rule-promotion",
                    "waiting-evidence",
                    "候选编号",
                ):
                    self.assertNotIn(internal_term, section)

    def test_maintainer_document_keeps_internal_steps_out_of_user_section(self):
        content = (
            ROOT / "docs" / "skill-eval" / "rule-promotion.md"
        ).read_text(encoding="utf-8")
        section = _section(content, "## 面向用户的交互")
        self.assertIn("要把它记录下来吗？", section)
        self.assertIn("记录", section)
        self.assertIn("不用", section)
        for internal_term in ("RC-", "waiting-evidence", "accepted"):
            self.assertNotIn(internal_term, section)


if __name__ == "__main__":
    unittest.main()
