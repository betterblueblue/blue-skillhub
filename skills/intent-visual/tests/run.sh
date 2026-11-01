#!/usr/bin/env bash
# run.sh — intent-visual skill tests
# 用法：cd skills/intent-visual/tests && ./run.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if python3 -c "print(1)" &>/dev/null; then
  PYTHON_BIN=python3
elif python -c "print(1)" &>/dev/null; then
  PYTHON_BIN=python
else
  echo "  🔴 python 未找到，无法运行测试"
  exit 1
fi

echo "═══════════════════════════════════════"
echo "  visual_validate 单元测试 (test_visual_validate.py)"
echo "═══════════════════════════════════════"
if $PYTHON_BIN -m pytest "$SCRIPT_DIR/test_visual_validate.py" -v 2>&1; then
  echo "  🟢 visual_validate 测试全部通过"
  exit 0
else
  echo "  🔴 visual_validate 测试有失败 — 检查上面输出"
  exit 1
fi
