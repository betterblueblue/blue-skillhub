#!/usr/bin/env bash
# run.sh — impact skill scenario runner
# 用法：cd skills/impact/tests && ./run.sh
# 需要：bash + python3（已自带）

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
source "$SCRIPT_DIR/lib/validate.sh"

# 共享模板一致性检查（L0 前置）
if command -v python3 &>/dev/null; then
  PYTHON_BIN=python3
elif command -v python &>/dev/null; then
  PYTHON_BIN=python
else
  echo "  ⚠ python 未找到，跳过模板一致性检查"
  PYTHON_BIN=""
fi

if [[ -n "$PYTHON_BIN" ]]; then
  echo "  检查共享模板一致性..."
  if ! $PYTHON_BIN "$REPO_ROOT/scripts/sync_templates.py" --check; then
    echo "  🔴 模板不一致 — 运行: python scripts/sync_templates.py"
    exit 1
  fi
fi

echo "═══════════════════════════════════════"
echo "  impact skill — scenarios runner"
echo "═══════════════════════════════════════"
echo "  目录: $SCRIPT_DIR"
echo "  时间: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"

# 找所有 scenario JSON
mapfile -t SCENARIOS < <(find "$SCRIPT_DIR/scenarios" -name "*.json" -type f | sort)

if [[ ${#SCENARIOS[@]} -eq 0 ]]; then
  echo ""
  echo "  ⚠ 未找到任何 scenario JSON（在 scenarios/ 子目录下）"
  exit 0
fi

echo "  找到 ${#SCENARIOS[@]} 个 scenario"

# 跑每个
for scenario in "${SCENARIOS[@]}"; do
  validate_scenario "$scenario"
done

# 总报告
print_summary
exit_code=$?

if [[ $exit_code -eq 0 ]]; then
  echo ""
  echo "  🟢 ALL PASS — 拆分后 impact skill 在 fixtures 上行为自洽"
else
  echo ""
  echo "  🔴 有 FAIL — 检查上面输出"
fi

exit $exit_code
