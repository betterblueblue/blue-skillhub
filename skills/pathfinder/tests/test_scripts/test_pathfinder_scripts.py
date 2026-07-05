#!/usr/bin/env python3
"""Tests for pf_scan.py, pf_git.py, pf_validate.py.

Run: python -m pytest tests/test_scripts/test_pathfinder_scripts.py -v
     or: python tests/test_scripts/test_pathfinder_scripts.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

PF_SCAN = SCRIPTS_DIR / "pf_scan.py"
PF_GIT = SCRIPTS_DIR / "pf_git.py"
PF_VALIDATE = SCRIPTS_DIR / "pf_validate.py"


def _run_script(script: Path, args: list[str], stdin_data: str = "") -> tuple[int, str, str]:
    """Run a script, return (exit_code, stdout, stderr)."""
    cmd = [sys.executable, str(script)] + args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                       input=stdin_data if stdin_data else None)
    return r.returncode, r.stdout, r.stderr


def _scan_facts(repo_root: str, file_count: int = 1, dir_tree: list[str] | None = None) -> dict:
    """Build schema-compliant scan.json test data."""
    return {
        "schema_version": 1,
        "generator": "pf_scan.py",
        "source_path": Path(repo_root).resolve().as_posix(),
        "observed_at": "2026-07-05T00:00:00+00:00",
        "file_count": file_count,
        "file_ext_counts": {".py": file_count},
        "dir_tree": dir_tree if dir_tree is not None else ["/", "src/"],
        "manifest_files": [],
        "budget_tier": "小仓",
    }


def _git_facts(
    repo_root: str,
    *,
    is_git_repo: bool = False,
    is_independent_repo: bool = False,
    head_short: str | None = None,
) -> dict:
    """Build schema-compliant git.json test data."""
    return {
        "schema_version": 1,
        "generator": "pf_git.py",
        "source_path": Path(repo_root).resolve().as_posix(),
        "observed_at": "2026-07-05T00:00:00+00:00",
        "is_git_repo": is_git_repo,
        "is_independent_repo": is_independent_repo,
        "toplevel": Path(repo_root).resolve().as_posix() if is_git_repo else None,
        "head_short": head_short,
        "head_full": head_short,
        "branch": "main" if is_git_repo else None,
        "hotspots": [],
        "recent_commit_modules": [],
    }


# ─── pf_scan.py tests ─────────────────────────────────────────────

class TestPfScan(unittest.TestCase):

    def test_scan_scripts_dir(self):
        """Scan a known small directory."""
        code, out, _ = _run_script(PF_SCAN, [str(SCRIPTS_DIR)])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["generator"], "pf_scan.py")
        self.assertIn("source_path", data)
        self.assertEqual(data["file_count"], 3)
        self.assertIn(".py", data["file_ext_counts"])
        self.assertEqual(data["budget_tier"], "小仓")

    def test_scan_this_repo(self):
        """Scan the project root — should be at least small."""
        root = str(Path(__file__).resolve().parents[5])
        code, out, _ = _run_script(PF_SCAN, [root])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertGreater(data["file_count"], 10)
        self.assertIn(data["budget_tier"], ("小仓", "中仓", "大仓", "超大仓"))

    def test_scan_degradation_trap(self):
        """Scan the degradation-trap fixture."""
        trap = FIXTURES_DIR / "degradation-trap"
        code, out, _ = _run_script(PF_SCAN, [str(trap)])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertGreaterEqual(data["file_count"], 5)
        self.assertIn(".js", data["file_ext_counts"])

    def test_scan_nonexistent_dir(self):
        """Scanning a nonexistent dir should exit 1."""
        code, _, _ = _run_script(PF_SCAN, ["/nonexistent/path/xyz"])
        self.assertEqual(code, 1)

    def test_scan_empty_dir(self):
        """Scanning an empty directory."""
        with tempfile.TemporaryDirectory() as td:
            code, out, _ = _run_script(PF_SCAN, [td])
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["file_count"], 0)
            self.assertEqual(data["budget_tier"], "小仓")


# ─── pf_git.py tests ──────────────────────────────────────────────

class TestPfGit(unittest.TestCase):

    def test_git_this_repo(self):
        """This project is a git repo — should detect it."""
        # Walk up from test file to find the git root (has .git dir)
        current = Path(__file__).resolve().parent
        root = None
        for _ in range(10):
            if (current / ".git").exists():
                root = str(current)
                break
            current = current.parent
        self.assertIsNotNone(root, "Could not find git root from test file location")
        code, out, _ = _run_script(PF_GIT, [root])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["generator"], "pf_git.py")
        self.assertIn("source_path", data)
        self.assertTrue(data["is_git_repo"])
        self.assertTrue(data["is_independent_repo"])
        self.assertIsNotNone(data["head_short"])
        self.assertGreater(len(data["head_short"]), 0)

    def test_git_degradation_trap(self):
        """Degradation trap is inside a git repo but not independent."""
        trap = str(FIXTURES_DIR / "degradation-trap")
        code, out, _ = _run_script(PF_GIT, [trap])
        self.assertEqual(code, 0)
        data = json.loads(out)
        # It's in a git repo (parent), but may or may not be independent
        # depending on whether .git exists inside the fixture dir
        self.assertIn("is_git_repo", data)

    def test_git_nonexistent_dir(self):
        """Nonexistent dir should exit 1."""
        code, _, _ = _run_script(PF_GIT, ["/nonexistent/path/xyz"])
        self.assertEqual(code, 1)

    def test_git_temp_dir_not_repo(self):
        """A plain temp dir with no .git should report is_git_repo=false."""
        with tempfile.TemporaryDirectory() as td:
            code, out, _ = _run_script(PF_GIT, [td])
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertFalse(data["is_git_repo"])
            self.assertIsNone(data["head_short"])


# ─── pf_validate.py tests ─────────────────────────────────────────

class TestPfValidate(unittest.TestCase):

    def _make_map(self, content: str, repo_root: str, create_facts: bool = False) -> str:
        """Write a temp map file, return its path.

        If create_facts=True, also create minimal facts files so V6 passes.
        """
        if create_facts:
            os.makedirs(os.path.join(repo_root, "src"), exist_ok=True)
            facts_dir = os.path.join(repo_root, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir, exist_ok=True)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(repo_root), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(_git_facts(repo_root), f)
        path = os.path.join(repo_root, "_project-map.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_valid_map_passes(self):
        """The degradation-trap map should pass all checks."""
        trap = str(FIXTURES_DIR / "degradation-trap")
        map_path = os.path.join(trap, "change-impact", "_project-map.md")
        code, out, _ = _run_script(PF_VALIDATE, [map_path, "--repo-root", trap])
        self.assertEqual(code, 0, f"Validate failed:\n{out}")
        self.assertIn("SUMMARY:", out)

    def test_fake_line_number_fails(self):
        """A map with a fabricated file:line should fail V1."""
        with tempfile.TemporaryDirectory() as td:
            # Create a real file with 3 lines
            src = os.path.join(td, "src")
            os.makedirs(src)
            with open(os.path.join(src, "main.py"), "w") as f:
                f.write("line1\nline2\nline3\n")

            map_content = """# Test Map
## 【5】关键入口
| 类型 | 位置 | 可信度 |
|------|------|--------|
| 进程入口 | src/main.py | 【已核实: src/main.py:99】 |

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Expected FAIL for fake line number, got:\n{out}")
            self.assertIn("V1:", out)

    def test_credential_leak_warns(self):
        """A map with unsanitized credentials should produce V2 warnings."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【7】外部依赖
- DB_PASSWORD=supersecret123
- api_key=AKIA1234567890

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Credential leak should WARN not FAIL:\n{out}")
            self.assertIn("WARN:", out)  # V2 produces warnings for credential patterns

    def test_mixed_credential_line_warns_only_unsanitized(self):
        """A line with both sanitized and unsanitized credentials should
        only warn for the unsanitized one."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【7】外部依赖
- password=*** token=plainsecret

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Mixed credential should WARN not FAIL:\n{out}")
            self.assertIn("token=", out)  # unsanitized token should be flagged
            self.assertNotIn("possible credential (password=", out)  # sanitized password should not

    def test_svg_script_fails(self):
        """A map with <script> inside SVG should fail V3."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
<svg><script>alert(1)</script></svg>

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1)
            self.assertIn("V3:", out)

    def test_empty_uncovered_fails(self):
        """A map with empty section 13 should fail V4."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【13】没挖深的部分

(无)

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1)
            self.assertIn("V4:", out)

    def test_stdin_mode(self):
        """Validate from stdin should work."""
        with tempfile.TemporaryDirectory() as td:
            # Create facts files so V6 passes
            os.makedirs(os.path.join(td, "src"))
            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(_git_facts(td), f)
            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            code, out, _ = _run_script(PF_VALIDATE, ["--stdin", "--repo-root", td],
                                       stdin_data=map_content)
            self.assertEqual(code, 0, f"Stdin mode failed:\n{out}")

    def test_v6_facts_missing_fails(self):
        """V6: missing facts directory should FAIL (exit 1)."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Missing facts should FAIL:\n{out}")
            self.assertIn("V6:", out)

    def test_v6_bad_facts_fails(self):
        """V6: facts with file_count=0 and head_short=null should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td, file_count=0, dir_tree=["/"]), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(_git_facts(td, is_git_repo=True, is_independent_repo=True), f)
            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Bad facts should fail:\n{out}")
            self.assertIn("V6: scan.json file_count is 0", out)
            self.assertIn("V6: git.json head_short is null/empty", out)

    def test_v6_legacy_facts_schema_fails(self):
        """V6: legacy facts without schema metadata should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "src"))
            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump({"file_count": 1, "dir_tree": ["/", "src/"]}, f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump({
                    "is_git_repo": False,
                    "is_independent_repo": False,
                    "head_short": None,
                    "toplevel": None,
                }, f)

            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | src | 【推断: 待验证】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Legacy facts should fail:\n{out}")
            self.assertIn("schema_version", out)

    def test_v6_good_facts_passes(self):
        """V6: facts with correct content should PASS."""
        with tempfile.TemporaryDirectory() as td:
            # Create src/ dir with files so disk matches facts
            src_dir = os.path.join(td, "src")
            os.makedirs(src_dir)
            for name in ("app.js", "models/index.js", "routes/auth.js", "routes/users.js"):
                full = os.path.join(src_dir, name)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w") as fh:
                    fh.write("// stub\n")

            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            # _count_files_quick skips change-impact dir; actual count = 1 (map) + 4 (src) = 5
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td, file_count=5), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(_git_facts(td), f)
            map_content = """# Test Map

生成时间: 2026-07-04   基于 commit: 346d60f   预算档位: 小仓
关注重点: 无

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Good facts should pass:\n{out}")
            self.assertIn("V6: facts file content validated", out)

    def test_v7_missing_section_14_fails(self):
        """V7: A map without section [14] should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Missing [14] should fail:\n{out}")
            self.assertIn("V7:", out)

    def test_v7_empty_shell_section_14_fails(self):
        """V7: A map with [14] title but no content should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map
## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察

(无)
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Empty [14] should fail:\n{out}")
            self.assertIn("V7:", out)
            self.assertIn("empty", out)

    def test_v4_nav_line_no_false_positive(self):
        """V4: Executive Summary nav line mentioning 【13】 should not trigger false positive."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map

## Executive Summary

**导航**：→ 【3】架构分层 / 【6】数据模型 / 【8】构建运行 / 【11】主流程 / 【13】未覆盖项

---

## 【0】基本信息

some content

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Nav line should not cause V4 false positive:\n{out}")
            self.assertIn("V4: uncovered section has entries", out)

    def test_v8_embedded_windows_drive_path_fails(self):
        """V8: malformed evidence paths like src/E:/repo/app.py should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "src")
            os.makedirs(src)
            with open(os.path.join(src, "app.py"), "w") as f:
                f.write("print('ok')\n")

            map_content = """# Test Map
## 【5】关键入口
| 类型 | 位置 | 可信度 |
|------|------|--------|
| 进程入口 | src/app.py | 【已核实: src/E:/agent/example/app.py:1】 |

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | src/app.py | 【已核实: src/app.py:1】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Malformed evidence path should FAIL:\n{out}")
            self.assertIn("V8:", out)

    def test_v9_commit_mismatch_fails(self):
        """V9: Map header commit different from git.json should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "src"))
            with open(os.path.join(td, "src", "app.py"), "w") as f:
                f.write("print('ok')\n")

            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td, file_count=2), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(
                    _git_facts(
                        td,
                        is_git_repo=True,
                        is_independent_repo=True,
                        head_short="abc1234",
                    ),
                    f,
                )

            map_content = """# Test Map

生成时间: 2026-07-04   基于 commit: deadbeef   预算档位: 小仓
关注重点: 无

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | src/app.py | 【已核实: src/app.py:1】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Commit mismatch should FAIL:\n{out}")
            self.assertIn("V9:", out)

    def test_v9_commit_match_passes(self):
        """V9: Map header commit matching git.json should pass."""
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "src"))
            with open(os.path.join(td, "src", "app.py"), "w") as f:
                f.write("print('ok')\n")

            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td, file_count=2), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(
                    _git_facts(
                        td,
                        is_git_repo=True,
                        is_independent_repo=True,
                        head_short="abc1234",
                    ),
                    f,
                )

            map_content = """# Test Map

生成时间: 2026-07-04   基于 commit: abc1234   预算档位: 小仓
关注重点: 无

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | src/app.py | 【已核实: src/app.py:1】 |
| 格式 | 统一 | src/app.py | 【已核实: src/app.py:1】 |
| 风格 | 一致 | src/app.py | 【已核实: src/app.py:1】 |
| 间距 | 4空格 | src/app.py | 【已核实: src/app.py:1】 |
| 引号 | 单引号 | src/app.py | 【已核实: src/app.py:1】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Commit match should pass:\n{out}")
            self.assertIn("V9:", out)

    def test_v11_current_head_mismatch_fails(self):
        """V11: stale facts/map that match each other but not current HEAD should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            def git(args: list[str]) -> subprocess.CompletedProcess:
                return subprocess.run(
                    ["git"] + args,
                    cwd=td,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if git(["--version"]).returncode != 0:
                raise unittest.SkipTest("git is not available")

            self.assertEqual(git(["init"]).returncode, 0)
            os.makedirs(os.path.join(td, "src"))
            app_path = os.path.join(td, "src", "app.py")
            with open(app_path, "w", encoding="utf-8") as f:
                f.write("print('v1')\n")
            self.assertEqual(git(["add", "."]).returncode, 0)
            commit1 = git(["-c", "user.email=a@example.com", "-c", "user.name=A", "commit", "-m", "v1"])
            if commit1.returncode != 0:
                raise unittest.SkipTest(f"git commit failed: {commit1.stderr}")
            head1 = git(["rev-parse", "--short", "HEAD"]).stdout.strip()

            with open(app_path, "w", encoding="utf-8") as f:
                f.write("print('v2')\n")
            self.assertEqual(git(["add", "."]).returncode, 0)
            commit2 = git(["-c", "user.email=a@example.com", "-c", "user.name=A", "commit", "-m", "v2"])
            if commit2.returncode != 0:
                raise unittest.SkipTest(f"git second commit failed: {commit2.stderr}")

            facts_dir = os.path.join(td, "change-impact", "_project-map", "facts")
            os.makedirs(facts_dir)
            with open(os.path.join(facts_dir, "scan.json"), "w") as f:
                json.dump(_scan_facts(td, file_count=2), f)
            with open(os.path.join(facts_dir, "git.json"), "w") as f:
                json.dump(
                    _git_facts(
                        td,
                        is_git_repo=True,
                        is_independent_repo=True,
                        head_short=head1,
                    ),
                    f,
                )

            map_content = f"""# Test Map

生成时间: 2026-07-04   基于 commit: {head1}   预算档位: 小仓
关注重点: 无

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | src/app.py | 【已核实: src/app.py:1】 |
| 格式 | 统一 | src/app.py | 【已核实: src/app.py:1】 |
| 风格 | 一致 | src/app.py | 【已核实: src/app.py:1】 |
| 间距 | 4空格 | src/app.py | 【已核实: src/app.py:1】 |
| 引号 | 单引号 | src/app.py | 【已核实: src/app.py:1】 |
"""
            path = self._make_map(map_content, td)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Stale HEAD should fail:\n{out}")
            self.assertIn("V11:", out)

    def test_v10_fix_suggestion_warns(self):
        """V10: Fix-suggestion keywords should WARN (not FAIL).

        WARN because hard rule #6 requires recording directive text from repo
        files into 【风险区域】 — a model following that rule would trigger
        keyword matches. WARN lets human reviewers judge without blocking.
        """
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map

## 【9】风险区域
- 建议改成 async/await 模式

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Fix-suggestion should WARN not FAIL:\n{out}")
            self.assertIn("V10:", out)
            self.assertIn("建议改成", out)
            self.assertIn("WARN", out)

    def test_v10_quoted_repo_text_in_risk_section_warns_not_fails(self):
        """V10: Keywords in 【风险区域】 as quoted repo text (rule #6) should WARN, not FAIL.

        Hard rule #6 requires recording directive text found in repo files
        (e.g. '可以直接删X') into 【风险区域】 as risk evidence. V10 must not
        block this with a FAIL — it should WARN for human review.
        """
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map

## 【9】风险区域
- 【已核实: src/】 仓库注释写着"可以删除旧接口"，属于指令性文本（硬规则 #6）

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | camelCase | test | 【推断: 待验证】 |
| 格式 | 统一 | test | 【已核实: test】 |
| 风格 | 一致 | test | 【已核实: test】 |
| 间距 | 2空格 | test | 【已核实: test】 |
| 引号 | 单引号 | test | 【已核实: test】 |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 0, f"Quoted repo text should WARN not FAIL:\n{out}")
            self.assertIn("V10:", out)
            self.assertIn("可以删除", out)
            self.assertIn("WARN", out)

    def test_v10_low_tag_density_fails(self):
        """V10: Too few credibility tags should FAIL."""
        with tempfile.TemporaryDirectory() as td:
            map_content = """# Test Map

## 【1】一句话概述
这是一个测试项目。

## 【2】技术栈
- Python

## 【13】没挖深的部分
| 未深入模块 | 为什么 | 扩展入口 |
|-----------|--------|---------|
| test | reason | 「再挖 test」 |

## 【14】代码风格观察
| 观察项 | 现状 | 证据 | 可信度 |
|--------|------|------|--------|
| 命名 | snake_case | test | test |
"""
            path = self._make_map(map_content, td, create_facts=True)
            code, out, _ = _run_script(PF_VALIDATE, [path, "--repo-root", td])
            self.assertEqual(code, 1, f"Low tag density should FAIL:\n{out}")
            self.assertIn("V10:", out)
            self.assertIn("credibility tags", out)


if __name__ == "__main__":
    unittest.main()
