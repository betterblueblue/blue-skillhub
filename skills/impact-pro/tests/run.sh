#!/usr/bin/env bash
# run.sh — impact-pro skill scenario runner
# 用法：cd skills/impact-pro/tests && ./run.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/validate.sh"

echo "═══════════════════════════════════════"
echo "  impact-pro skill — scenarios runner"
echo "═══════════════════════════════════════"
echo "  目录: $SCRIPT_DIR"
echo "  时间: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"

mapfile -t SCENARIOS < <(find "$SCRIPT_DIR/scenarios" -name "*.json" -type f | sort)

if [[ ${#SCENARIOS[@]} -eq 0 ]]; then
  echo ""
  echo "  ⚠ 未找到任何 scenario JSON"
  exit 0
fi

echo "  找到 ${#SCENARIOS[@]} 个 scenario"

for scenario in "${SCENARIOS[@]}"; do
  validate_scenario "$scenario"
done

print_summary
exit_code=$?

if [[ $exit_code -eq 0 ]]; then
  echo ""
  echo "  🟢 ALL PASS — 拆分后 impact-pro skill 在 fixtures 上行为自洽"
else
  echo ""
  echo "  🔴 有 FAIL — 检查上面输出"
fi

exit $exit_code
