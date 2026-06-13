#!/usr/bin/env bash
# pathfinder L0 静态校验入口
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/validate.sh"

echo "═══ Pathfinder L0 静态校验 ═══"

find "$SCRIPT_DIR/scenarios" -name '*.json' -type f | sort | while read -r f; do
  validate_scenario "$f" || true
done

print_summary
