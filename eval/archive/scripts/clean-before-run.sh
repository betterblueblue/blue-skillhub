#!/usr/bin/env bash
# clean-before-run.sh — 清理测试项目的 change-impact/ 目录
#
# 在每个模型盲测前运行，确保没有之前测试的残留文件。
# 不清理的话会导致：
#   1. pf_scan.py 把残留文件计入项目文件数（file_count 虚高）
#   2. pf_validate.py V6 因旧 facts 文件假通过
#   3. 模型可能读到其他模型的产出，破坏独立性
#
# 用法:
#   ./clean-before-run.sh [project-path ...]
#
# 不传参数时默认清理两个测试项目:
#   test-projects/prisma-express-ts
#   test-projects/ruoyi-vue

set -euo pipefail

DEFAULT_PROJECTS=(
  "test-projects/prisma-express-ts"
  "test-projects/ruoyi-vue"
)

PROJECTS=("$@")
if [ ${#PROJECTS[@]} -eq 0 ]; then
  PROJECTS=("${DEFAULT_PROJECTS[@]}")
fi

for proj in "${PROJECTS[@]}"; do
  ci_path="$proj/change-impact"
  if [ -d "$ci_path" ]; then
    echo "Cleaning: $ci_path"
    rm -rf "$ci_path"
  else
    echo "Skip (not found): $ci_path"
  fi
done

echo "Done. change-impact/ directories cleaned."
