#!/usr/bin/env bash
# L1 行为契约测试 — 编排 + 校验 + 评分卡收集
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CASES_DIR="$REPO_ROOT/eval/cases"
RUNS_DIR="$REPO_ROOT/eval/runs"
SCHEMAS_DIR="$REPO_ROOT/eval/schemas"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SKILL="${1:-all}"
JUDGE_MODEL="${2:-unspecified}"

echo "═══ L1 行为契约测试 ═══"
echo "  Skill 过滤: $SKILL"
echo "  评委模型: $JUDGE_MODEL"
echo ""

# 收集 case
declare -a CASE_FILES=()
for skill_dir in "$CASES_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  if [[ "$SKILL" != "all" && "$SKILL" != "$skill_name" ]]; then
    continue
  fi
  while IFS= read -r -d '' f; do
    CASE_FILES+=("$f")
  done < <(find "$skill_dir" -name '*.json' -print0 | sort -z)
done

echo "找到 ${#CASE_FILES[@]} 个 case"
echo ""

# 校验每个 case
PASS_COUNT=0
FAIL_COUNT=0
for case_file in "${CASE_FILES[@]}"; do
  case_id=$(python -c "import json; print(json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')).get('id','?'))" 2>/dev/null || echo "?")
  skill=$(python -c "import json; print(json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')).get('skill','?'))" 2>/dev/null || echo "?")
  tier=$(python -c "import json; print(json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')).get('tier','?'))" 2>/dev/null || echo "?")
  prompt_preview=$(python -c "import json; p=json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')).get('prompt',''); print(p[:60]+'...' if len(p)>60 else p)" 2>/dev/null || echo "?")

  echo -e "  ${BLUE}[$skill/$case_id]${NC} tier=$tier"
  echo -e "    prompt: $prompt_preview"

  # 校验必需字段
  has_prompt=$(python -c "import json; d=json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')); print('yes' if 'prompt' in d else 'no')" 2>/dev/null || echo "no")
  has_must_hit=$(python -c "import json; d=json.load(open(r'$(cygpath -w "$case_file" 2>/dev/null || echo "$case_file")')); print('yes' if 'must_hit_files' in d.get('expected',{}) else 'no')" 2>/dev/null || echo "no")

  if [[ "$has_prompt" == "yes" && "$has_must_hit" == "yes" ]]; then
    echo -e "    ${GREEN}✓${NC} case schema 校验通过"
    PASS_COUNT=$((PASS_COUNT+1))
  else
    echo -e "    ${RED}✗${NC} case schema 校验失败 (prompt=$has_prompt, must_hit_files=$has_must_hit)"
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi
done

echo ""
echo "═══════════════════════════════════════"
echo "  校验通过: $PASS_COUNT"
echo "  校验失败: $FAIL_COUNT"
echo "═══════════════════════════════════════"

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo ""
  echo "⚠ 有 case 校验失败，请修复后再跑 L1"
  exit 1
fi

echo ""
echo "✓ 全部 case 校验通过"
echo ""
echo "下一步："
echo "  1. 对每个 case 启动 subagent（用 02-执行协议.md 的 system prompt 模板）"
echo "  2. 收集 subagent 产出（change-impact/ 目录）"
echo "  3. 用评委模型/人审按 rubric 打分"
echo "  4. 将评分卡写入 eval/runs/<date>-<skill>@<commit>/<case-id>.scorecard.md"
echo "  5. 运行 eval/diff-baseline.sh 与上一基线对比"
