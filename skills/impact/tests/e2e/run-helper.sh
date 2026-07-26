#!/usr/bin/env bash
# run-helper.sh — e2e 测试辅助脚本
# 用法：
#   ./run-helper.sh setup <scenario.json>     # 准备 workdir
#   ./run-helper.sh compile <scenario.json>   # 跑 mvn compile
#   ./run-helper.sh diff <scenario.json>      # 看 git diff
#   ./run-helper.sh cleanup <scenario.json>   # 清理 workdir

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="$1"
SCENARIO="$2"

# 用 python 解析 JSON（Git Bash 兼容）
to_win_path() {
  local p="$1"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$p"
  else
    echo "$p"
  fi
}

# 解析 scenario 字段
SCENARIO_ID=$(python -c "
import json
with open(r'$(to_win_path "$SCENARIO")', encoding='utf-8') as f:
    d = json.load(f)
print(d['id'])
" 2>&1 | grep -v "^$" | head -1)

PROJECT_NAME=$(python -c "
import json
with open(r'$(to_win_path "$SCENARIO")', encoding='utf-8') as f:
    d = json.load(f)
print(d['fixture']['project'])
" 2>&1 | grep -v "^$" | head -1)

PROJECT_SLUG=$(echo "$PROJECT_NAME" | tr 'A-Z' 'a-z')

WORKDIR="$SCRIPT_DIR/workdirs/$SCENARIO_ID"
REPO_ROOT=$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")
FIXTURE="$REPO_ROOT/test-projects/$PROJECT_SLUG"

case "$CMD" in
  setup)
    echo "═══ Setup: $SCENARIO_ID ═══"
    echo "  fixture: $FIXTURE"
    echo "  workdir: $WORKDIR"

    if [[ ! -d "$FIXTURE" ]]; then
      echo "  ✗ fixture 不存在: $FIXTURE"
      exit 1
    fi

    rm -rf "$WORKDIR"
    mkdir -p "$(dirname "$WORKDIR")"
    cp -r "$FIXTURE" "$WORKDIR"
    echo "  ✓ workdir 已创建（$(du -sh "$WORKDIR" | cut -f1)）"

    ACTUAL_DIR="$SCRIPT_DIR/scenarios/$SCENARIO_ID/actual"
    mkdir -p "$ACTUAL_DIR"
    echo "  ✓ actual dir: $ACTUAL_DIR"
    ;;

  compile)
    echo "═══ Compile: $SCENARIO_ID ═══"
    if [[ ! -d "$WORKDIR" ]]; then
      echo "  ✗ workdir 不存在，先跑 setup"
      exit 1
    fi

    # RuoYi 是 Maven 项目，cd 到 workdir 跑
    cd "$WORKDIR"
    echo "  跑: mvn compile -q (timeout 5 min)"
    if timeout 300 mvn compile -q 2>&1 | tail -50; then
      echo "  ✓ BUILD SUCCESS"
      exit 0
    else
      echo "  ✗ BUILD FAILED"
      exit 1
    fi
    ;;

  diff)
    echo "═══ Diff: $SCENARIO_ID ═══"
    if [[ ! -d "$WORKDIR" ]]; then
      echo "  ✗ workdir 不存在，先跑 setup"
      exit 1
    fi

    cd "$WORKDIR"
    echo "--- 改动文件统计 ---"
    git diff --stat 2>/dev/null | tail -30
    echo ""
    echo "--- 新增文件 ---"
    git status --short 2>/dev/null | grep '^??' | head -20
    ;;

  cleanup)
    echo "═══ Cleanup: $SCENARIO_ID ═══"
    if [[ -d "$WORKDIR" ]]; then
      rm -rf "$WORKDIR"
      echo "  ✓ workdir 已删除"
    else
      echo "  ℹ workdir 本就不存在"
    fi

    # actual/ 保留供人工审查
    ACTUAL_DIR="$SCRIPT_DIR/scenarios/$SCENARIO_ID/actual"
    if [[ -d "$ACTUAL_DIR" ]]; then
      echo "  ℹ 保留 actual/ 给人工审查: $ACTUAL_DIR"
    fi
    ;;

  *)
    echo "用法: $0 {setup|compile|diff|cleanup} <scenario.json>"
    exit 1
    ;;
esac
