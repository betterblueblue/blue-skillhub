#!/usr/bin/env python3
"""Tests for validate_real_projects.py prompt hygiene checks."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_real_projects.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_real_projects", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestValidateRealProjectsPromptHygiene(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = Path(tempfile.mkdtemp())
        self.validator.REPO_ROOT = self.tmp

    def write_prompt(self, content: str) -> Path:
        path = self.tmp / "eval/runs/real-projects/run/prompts/prompt.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def configure_inventory_paths(self) -> None:
        self.validator.DELIVERY_MATRIX_PATH = self.tmp / "eval/real-projects/delivery-matrix.json"
        self.validator.DELIVERY_RESULTS_PATH = self.tmp / "eval/real-projects/delivery-results.json"
        self.validator.RUNS_ROOT = self.tmp / "eval/runs/real-projects"
        self.validator.DELIVERY_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.validator.RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    def test_minimal_prompt_passes(self) -> None:
        path = self.write_prompt(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md

---

[用户输入]
真实 /impact 交付验收：item 表单的必填提示从 "Title is required" 改成 "Item title is required"。就一句文案，快速改一下就行，不用整文档流程。别动后端。
"""
        )
        errors: list[str] = []

        self.validator.validate_launch_prompt_file(errors, path)

        self.assertEqual(errors, [])

    def test_monitoring_rules_inside_prompt_fail(self) -> None:
        path = self.write_prompt(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md

---

[用户输入]
把文案改一下。

重要边界：
- 只允许写 change-impact。
- 每次写入必须等待确认 Step N。
- 跑 impact_validate.py。
"""
        )
        errors: list[str] = []

        self.validator.validate_launch_prompt_file(errors, path)

        self.assertTrue(any("harness/judge wording" in error for error in errors), errors)

    def test_extra_environment_rules_fail(self) -> None:
        path = self.write_prompt(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md
规则：不要读取旧产物

---

[用户输入]
把文案改一下。
"""
        )
        errors: list[str] = []

        self.validator.validate_launch_prompt_file(errors, path)

        self.assertTrue(any("environment field '规则' is not allowed" in error for error in errors), errors)

    def test_text_between_separator_and_user_input_fails(self) -> None:
        path = self.write_prompt(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md

---

重要边界：不要把评分规则写给 runner。

[用户输入]
把文案改一下。
"""
        )
        errors: list[str] = []

        self.validator.validate_launch_prompt_file(errors, path)

        self.assertTrue(any("between --- and [用户输入]" in error for error in errors), errors)

    def test_natural_user_constraints_are_allowed(self) -> None:
        errors: list[str] = []

        self.validator.validate_user_prompt(
            errors,
            "case",
            "先不要写代码，只做完整影响分析。快速改一下就行，别动后端，不执行真实数据库迁移。",
        )

        self.assertEqual(errors, [])

    def test_pending_runner_plan_requires_standard_prompt_file(self) -> None:
        self.configure_inventory_paths()
        self.validator.DELIVERY_MATRIX_PATH.write_text(
            """{
  "runner_plan": {
    "composer-25fast-subagent": ["D14-java-enum-analysis"]
  }
}
""",
            encoding="utf-8",
        )
        self.validator.DELIVERY_RESULTS_PATH.write_text(
            """{"results": []}
""",
            encoding="utf-8",
        )
        errors: list[str] = []

        self.validator.validate_pending_launch_prompt_inventory(errors, {})

        self.assertIn("prompts/d14-composer-25fast-subagent.txt", "\n".join(errors))

    def test_completed_runner_plan_does_not_require_standard_prompt_file(self) -> None:
        self.configure_inventory_paths()
        self.validator.DELIVERY_MATRIX_PATH.write_text(
            """{
  "runner_plan": {
    "composer-25fast-subagent": ["D20-python-title-required-lazy-phase5"]
  }
}
""",
            encoding="utf-8",
        )
        self.validator.DELIVERY_RESULTS_PATH.write_text(
            """{
  "results": [
    {
      "scenario_id": "D20-python-title-required-lazy-phase5",
      "runner_id": "composer-25fast-subagent"
    }
  ]
}
""",
            encoding="utf-8",
        )
        errors: list[str] = []

        self.validator.validate_pending_launch_prompt_inventory(errors, {})

        self.assertEqual(errors, [])

    def test_pending_prompt_user_input_must_match_case_prompt(self) -> None:
        self.configure_inventory_paths()
        self.validator.DELIVERY_MATRIX_PATH.write_text(
            """{
  "scenarios": [
    {
      "id": "D14-java-enum-analysis",
      "case_id": "java-ruoyi-impact-enum"
    }
  ],
  "runner_plan": {
    "composer-25fast-subagent": ["D14-java-enum-analysis"]
  }
}
""",
            encoding="utf-8",
        )
        self.validator.DELIVERY_RESULTS_PATH.write_text(
            """{"results": []}
""",
            encoding="utf-8",
        )
        prompt = self.validator.RUNS_ROOT / "run/prompts/d14-composer-25fast-subagent.txt"
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md

---

[用户输入]
用户状态新增 LOCKED。这里偷偷改写了原始 prompt。
""",
            encoding="utf-8",
        )
        errors: list[str] = []

        self.validator.validate_pending_launch_prompt_inventory(
            errors,
            {
                "java-ruoyi-impact-enum": {
                    "skill": "impact",
                    "prompt": "用户状态现在只有正常和停用，需要新增一个 LOCKED 状态，锁定后不能登录。先不要写代码，只做完整影响分析。",
                }
            },
        )

        self.assertTrue(any("user input mismatch" in error for error in errors), errors)

    def test_pending_prompt_skill_must_match_case_skill(self) -> None:
        self.configure_inventory_paths()
        self.validator.DELIVERY_MATRIX_PATH.write_text(
            """{
  "scenarios": [
    {
      "id": "D12-monorepo-pathfinder-map",
      "case_id": "monorepo-full-stack-starter-pathfinder"
    }
  ],
  "runner_plan": {
    "minimax-m3-claude-cli": ["D12-monorepo-pathfinder-map"]
  }
}
""",
            encoding="utf-8",
        )
        self.validator.DELIVERY_RESULTS_PATH.write_text(
            """{"results": []}
""",
            encoding="utf-8",
        )
        prompt = self.validator.RUNS_ROOT / "run/prompts/d12-minimax-m3-claude-cli.txt"
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text(
            """[评测环境]
工作目录：E:\\agent\\fixture
Skill：E:\\agent\\blue-skillhub\\skills\\impact\\SKILL.md
输出归档：E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md

---

[用户输入]
我准备改这个 full-stack-starter-kit。请先在仓库根目录只读生成项目地图。
""",
            encoding="utf-8",
        )
        errors: list[str] = []

        self.validator.validate_pending_launch_prompt_inventory(
            errors,
            {
                "monorepo-full-stack-starter-pathfinder": {
                    "skill": "pathfinder",
                    "prompt": "我准备改这个 full-stack-starter-kit。请先在仓库根目录只读生成项目地图。",
                }
            },
        )

        self.assertTrue(any("skill mismatch" in error for error in errors), errors)

    def test_pending_prompt_output_archive_must_be_run_readme(self) -> None:
        errors: list[str] = []

        self.validator.validate_pending_prompt_environment(
            errors,
            "prompt.txt",
            "D14-java-enum-analysis",
            {"stage": "impact-phase4", "fixture_mode": "read-only-original"},
            {
                "工作目录": "E:\\agent\\real-project-fixtures\\java-ruoyi",
                "输出归档": "E:\\agent\\blue-skillhub\\docs\\result.md",
            },
        )

        self.assertTrue(any("eval/runs/real-projects" in error for error in errors), errors)
        self.assertTrue(any("README.md" in error for error in errors), errors)

    def test_non_git_pathfinder_requires_distinct_non_git_copy_dir(self) -> None:
        errors: list[str] = []

        self.validator.validate_pending_prompt_environment(
            errors,
            "prompt.txt",
            "D12-monorepo-pathfinder-map",
            {"stage": "pathfinder-map", "fixture_mode": "non-git-copy"},
            {
                "工作目录": "E:\\agent\\real-project-fixtures\\monorepo",
                "输出归档": "E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md",
            },
        )

        self.assertTrue(any("非 Git 副本目录" in error for error in errors), errors)

        errors = []
        self.validator.validate_pending_prompt_environment(
            errors,
            "prompt.txt",
            "D12-monorepo-pathfinder-map",
            {"stage": "pathfinder-map", "fixture_mode": "non-git-copy"},
            {
                "工作目录": "E:\\agent\\real-project-fixtures\\monorepo",
                "非 Git 副本目录": "E:\\agent\\real-project-fixtures\\monorepo",
                "输出归档": "E:\\agent\\blue-skillhub\\eval\\runs\\real-projects\\run\\README.md",
            },
        )

        self.assertTrue(any("must differ" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
