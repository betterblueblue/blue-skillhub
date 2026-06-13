#!/usr/bin/env bash
# 基线 diff / 控制变量对比 — 防漂移红线检查
# 用法:
#   bash eval/diff-baseline.sh <skill>                # 最新非基线 run vs 基线
#   bash eval/diff-baseline.sh <skill> <run>          # 指定 run vs 基线
#   bash eval/diff-baseline.sh <skill> <run_a> <run_b>  # 两 run 直接对比(控制变量实验)
# <run> = commit 前缀(如 22be520)/ 目录名 / 路径
# 逻辑见 eval/scripts/diff_baseline.py
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python "$SCRIPT_DIR/scripts/diff_baseline.py" "$@"
