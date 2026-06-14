#!/usr/bin/env bash
# pathfinder L0 静态校验入口
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/validate.sh"

echo "═══ Pathfinder L0 静态校验 ═══"

# 用 process substitution 而非 `find | while read`,否则循环体在子 shell 里跑,
# PASS_COUNT/FAIL_COUNT 的累加穿不回父 shell,summary 恒报 0/0、单项 FAIL 被吞。
while read -r f; do
  validate_scenario "$f" || true
done < <(find "$SCRIPT_DIR/scenarios" -name '*.json' -type f | sort)

print_summary
