#!/usr/bin/env bash
# prepare-v5-parallel.sh — 为 V5 盲测创建 6 个独立并行测试环境
#
# 每个 cell（实验单元）获得自己独立的 test-projects 副本，
# 这样 6 个 prompt 可以同时并行执行，互不干扰。
#
# 用法:
#   ./eval/scripts/prepare-v5-parallel.sh
#
# 产出目录结构:
#   eval/runs/blind-2026-06-25-v5/
#   ├── cell-C1/test-projects/{prisma-express-ts,ruoyi-vue}/  # Opus no-skill
#   ├── cell-C2/test-projects/{prisma-express-ts,ruoyi-vue}/  # Opus skill
#   ├── cell-C3/test-projects/{prisma-express-ts,ruoyi-vue}/  # Composer no-skill
#   ├── cell-C4/test-projects/{prisma-express-ts,ruoyi-vue}/  # Composer skill
#   ├── cell-C5/test-projects/{prisma-express-ts,ruoyi-vue}/  # GLM no-skill
#   ├── cell-C6/test-projects/{prisma-express-ts,ruoyi-vue}/  # GLM skill
#   └── scorecards/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
V5_ROOT="$REPO_ROOT/eval/runs/blind-2026-06-25-v5"

# 6 个 cell 定义: ID|模型|条件
CELLS=(
  "C1|opus-noskill"
  "C2|opus-skill"
  "C3|composer-noskill"
  "C4|composer-skill"
  "C5|glm-noskill"
  "C6|glm-skill"
)

# 需要复制的测试项目（排除 change-impact/、node_modules/、.git/、target/）
PROJECTS=(
  "test-projects/prisma-express-ts"
  "test-projects/ruoyi-vue"
)

# 排除模式
EXCLUDE_PATTERNS=(
  "change-impact"
  "node_modules"
  ".git"
  "target"
  "__pycache__"
)

echo "=========================================="
echo "V5 并行测试环境准备"
echo "=========================================="
echo "仓库根目录: $REPO_ROOT"
echo "V5 产出根目录: $V5_ROOT"
echo ""

# 清理旧环境（如果存在）
if [ -d "$V5_ROOT" ]; then
  echo "发现旧的 V5 目录，清理中..."
  rm -rf "$V5_ROOT"
fi

mkdir -p "$V5_ROOT/scorecards"

# 为每个 cell 创建独立的 test-projects 副本
for cell_entry in "${CELLS[@]}"; do
  IFS='|' read -r cell_id cell_name <<< "$cell_entry"
  cell_dir="$V5_ROOT/cell-$cell_id"

  echo "─── 准备 cell-$cell_id ($cell_name) ───"

  mkdir -p "$cell_dir/test-projects"

  for proj_path in "${PROJECTS[@]}"; do
    proj_name=$(basename "$proj_path")
    src="$REPO_ROOT/$proj_path"
    dst="$cell_dir/test-projects/$proj_name"

    if [ ! -d "$src" ]; then
      echo "  ❌ 源项目不存在: $src"
      exit 1
    fi

    # 用 rsync 复制，排除不需要的目录
    if command -v rsync &> /dev/null; then
      rsync_excludes=""
      for pat in "${EXCLUDE_PATTERNS[@]}"; do
        rsync_excludes="$rsync_excludes --exclude=$pat"
      done
      rsync -a $rsync_excludes "$src/" "$dst/"
    else
      # Windows 没有 rsync，用 robocopy 或 cp
      if command -v robocopy &> /dev/null; then
        robocopy_args=()
        for pat in "${EXCLUDE_PATTERNS[@]}"; do
          robocopy_args+=("/XD" "$pat")
          robocopy_args+=("/XF" "$pat")
        done
        robocopy "$src" "$dst" /E "${robocopy_args[@]}" /NFL /NDL /NJH /NJS /NP
      else
        # 最后兜底：cp -r 然后手动清理
        cp -r "$src" "$dst"
        for pat in "${EXCLUDE_PATTERNS[@]}"; do
          find "$dst" -name "$pat" -type d -exec rm -rf {} + 2>/dev/null || true
        done
      fi
    fi

    # 确保没有残留的 change-impact
    rm -rf "$dst/change-impact"

    file_count=$(find "$dst" -type f | wc -l)
    echo "  ✅ $proj_name: $file_count 个文件"
  done

  echo ""
done

echo "=========================================="
echo "✅ 6 个并行环境准备完成"
echo "=========================================="
echo ""
echo "目录结构:"
echo "  $V5_ROOT/"
for cell_entry in "${CELLS[@]}"; do
  IFS='|' read -r cell_id cell_name <<< "$cell_entry"
  echo "  ├── cell-$cell_id/ ($cell_name)"
  echo "  │   └── test-projects/{prisma-express-ts,ruoyi-vue}/"
done
echo "  └── scorecards/"
echo ""
echo "下一步:"
echo "  1. 把 6 个 prompt 文件分别发给对应模型"
echo "     (每个 prompt 已包含 cell 专属路径)"
echo "  2. 6 个模型可以同时并行执行"
echo "  3. 全部完成后运行归档和盲评"
