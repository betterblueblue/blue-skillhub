#!/usr/bin/env python3
"""Tests for check_delivery.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_delivery.py"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_repo() -> Path:
    td = Path(tempfile.mkdtemp())
    run(["git", "init"], td)
    run(["git", "config", "user.email", "test@example.com"], td)
    run(["git", "config", "user.name", "Test User"], td)
    write(
        td / "src/views/dashboard/dashboard.router.tsx",
        """const route = {
  label: 'Dashboard',
  title: 'Dashboard',
  path: 'dashboard',
  key: '/dashboard',
}
""",
    )
    write(td / "package.json", '{"name":"fixture"}\n')
    write(td / "src/feature.ts", "export const feature = 'favorite'\n")
    run(["git", "add", "."], td)
    run(["git", "commit", "-m", "initial"], td)
    return td


def make_acceptance(repo: Path, data: dict[str, object]) -> Path:
    path = Path(tempfile.mkdtemp()) / "acceptance.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def run_check(repo: Path, acceptance: dict[str, object]) -> tuple[int, dict[str, object]]:
    acceptance_path = make_acceptance(repo, acceptance)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(repo), "--acceptance", str(acceptance_path), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, json.loads(result.stdout)


BASE_ACCEPTANCE = {
    "expected_changed_files": ["src/views/dashboard/dashboard.router.tsx"],
    "forbidden_changed_files": ["package.json"],
    "validators": ["git diff --check"],
    "must_contain": ["label: 'Insights'", "title: 'Insights'"],
    "must_not_contain": ["label: 'Dashboard'", "path: 'insights'", "key: '/insights'"],
}


class TestCheckDelivery(unittest.TestCase):
    def test_passes_when_expected_file_and_content_match(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            """const route = {
  label: 'Insights',
  title: 'Insights',
  path: 'dashboard',
  key: '/dashboard',
}
""",
        )
        write(repo / "change-impact/req/090-execution-record.md", "expected doc noise\n")

        code, report = run_check(repo, BASE_ACCEPTANCE)

        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["changed_files"], ["src/views/dashboard/dashboard.router.tsx"])

    def test_untracked_file_inside_new_directory_can_be_expected(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        write(repo / "tests/new/dashboard.test.ts", "expect('Insights').toBe('Insights')\n")
        acceptance = dict(BASE_ACCEPTANCE)
        acceptance["expected_changed_files"] = [
            "src/views/dashboard/dashboard.router.tsx",
            "tests/new/dashboard.test.ts",
        ]
        acceptance["must_contain"] = ["label: 'Insights'", "expect('Insights')"]

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 0, report)
        self.assertIn("tests/new/dashboard.test.ts", report["changed_files"])

    def test_dot_prefixed_paths_are_preserved(self) -> None:
        repo = make_repo()
        write(repo / ".github/workflows/eval.yml", "name: Eval\n")
        acceptance = {
            "expected_changed_files": [".github/workflows/eval.yml"],
            "forbidden_changed_files": ["package.json"],
            "validators": ["git diff --check"],
            "must_contain": ["name: Eval"],
        }

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 0, report)
        self.assertEqual(report["changed_files"], [".github/workflows/eval.yml"])

    def test_missing_expected_change_fails(self) -> None:
        repo = make_repo()

        code, report = run_check(repo, BASE_ACCEPTANCE)

        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(check["code"] == "expected-changed-files" for check in report["checks"]))

    def test_forbidden_changed_file_fails(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        write(repo / "package.json", '{"name":"changed"}\n')

        code, report = run_check(repo, BASE_ACCEPTANCE)

        self.assertEqual(code, 1)
        self.assertTrue(any(check["code"] == "forbidden-changed-files" for check in report["checks"]))

    def test_expected_deleted_file_must_be_deleted(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        write(repo / "src/feature.ts", "")
        acceptance = dict(BASE_ACCEPTANCE)
        acceptance["expected_changed_files"] = [
            "src/views/dashboard/dashboard.router.tsx",
            "src/feature.ts",
        ]
        acceptance["expected_deleted_files"] = ["src/feature.ts"]

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 1)
        self.assertTrue(any(check["code"] == "expected-deleted-files" for check in report["checks"]))

    def test_expected_deleted_file_passes_when_deleted(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        (repo / "src/feature.ts").unlink()
        acceptance = dict(BASE_ACCEPTANCE)
        acceptance["expected_changed_files"] = [
            "src/views/dashboard/dashboard.router.tsx",
            "src/feature.ts",
        ]
        acceptance["expected_deleted_files"] = ["src/feature.ts"]

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 0, report)
        self.assertTrue(any(check["code"] == "expected-deleted-files" for check in report["checks"]))

    def test_deleted_only_file_does_not_warn_unexpected(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        (repo / "src/feature.ts").unlink()
        acceptance = dict(BASE_ACCEPTANCE)
        acceptance["expected_deleted_files"] = ["src/feature.ts"]

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(any(check["code"] == "unexpected-changed-files" for check in report["checks"]))

    def test_forbidden_content_in_expected_file_fails(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'insights'\nkey: '/dashboard'\n",
        )

        code, report = run_check(repo, BASE_ACCEPTANCE)

        self.assertEqual(code, 1)
        self.assertTrue(any(check["code"] == "must-not-contain" for check in report["checks"]))

    def test_repo_content_scope_catches_residual_reference(self) -> None:
        repo = make_repo()
        write(
            repo / "src/views/dashboard/dashboard.router.tsx",
            "label: 'Insights'\ntitle: 'Insights'\npath: 'dashboard'\nkey: '/dashboard'\n",
        )
        acceptance = dict(BASE_ACCEPTANCE)
        acceptance["content_scope"] = "repo"
        acceptance["must_not_contain"] = ["favorite"]

        code, report = run_check(repo, acceptance)

        self.assertEqual(code, 1)
        self.assertTrue(any(check["code"] == "must-not-contain" for check in report["checks"]))


if __name__ == "__main__":
    unittest.main()
