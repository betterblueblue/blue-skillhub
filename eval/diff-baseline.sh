#!/usr/bin/env bash
# 基线 diff — 防漂移红线检查
# 用法: bash eval/diff-baseline.sh <skill>
# 比较 eval/runs/ 最新一轮与 eval/baselines/<skill>.json 指向的基线

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SKILL="${1:?用法: diff-baseline.sh <skill>}"

BASELINE_FILE="$REPO_ROOT/eval/baselines/$SKILL.json"

if [[ ! -f "$BASELINE_FILE" ]]; then
  echo "❌ 基线文件不存在: $BASELINE_FILE"
  exit 1
fi

BASELINE_COMMIT=$(python -c "import json; print(json.load(open(r'$(cygpath -w "$BASELINE_FILE" 2>/dev/null || echo "$BASELINE_FILE")')).get('skill_commit',''))" 2>/dev/null || echo "")
BASELINE_RUN=$(python -c "import json; print(json.load(open(r'$(cygpath -w "$BASELINE_FILE" 2>/dev/null || echo "$BASELINE_FILE")')).get('run_path',''))" 2>/dev/null || echo "")

if [[ -z "$BASELINE_COMMIT" || "$BASELINE_COMMIT" == "None" || "$BASELINE_COMMIT" == "null" ]]; then
  echo "⚠ 基线未建立（skill_commit 为空），跳过 diff"
  echo "  请先跑一轮 L1 建立基线"
  exit 0
fi

echo "═══ 基线 Diff: $SKILL ═══"
echo "  基线 commit: ${BASELINE_COMMIT:0:7}"
echo "  基线来源: $BASELINE_RUN"
echo ""

# 找最新一轮 runs
LATEST_RUN=$(ls -d "$REPO_ROOT/eval/runs/"*"-${SKILL}@"* 2>/dev/null | sort -r | head -1)

if [[ -z "$LATEST_RUN" ]]; then
  echo "❌ 没有找到 $SKILL 的 runs 记录"
  exit 1
fi

LATEST_COMMIT=$(echo "$LATEST_RUN" | grep -oE '@[a-f0-9]+' | sed 's/@//')

if [[ "$LATEST_COMMIT" == "$BASELINE_COMMIT" ]]; then
  echo "ℹ 最新一轮与基线是同一 commit，无需 diff"
  exit 0
fi

echo "  最新 commit: ${LATEST_COMMIT:0:7}"
echo ""

# 逐 case diff 评分卡
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

RED_FLAG=0

for scorecard in "$LATEST_RUN"/*.scorecard.md; do
  [[ -f "$scorecard" ]] || continue
  case_id=$(basename "$scorecard" .scorecard.md)

  # 从评分卡提取 contracts 和 key metrics
  current_data=$(python -c "
import json, re, sys
try:
    with open(r'$(cygpath -w "$scorecard" 2>/dev/null || echo "$scorecard")', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'\`\`\`json\s*(\{.*?\})\s*\`\`\`', content, re.DOTALL)
    if m:
        d = json.loads(m.group(1))
        contracts = d.get('contracts', {})
        for k, v in contracts.items():
            print(f'{k}={v}')
        p = d.get('p_level', 'none')
        print(f'p_level={p}')
        t = d.get('base_total', 0)
        print(f'base_total={t}')
    else:
        print('parse_error=no_json_block')
except Exception as e:
    print(f'parse_error={e}')
" 2>/dev/null || echo "parse_error")

  if echo "$current_data" | grep -q "parse_error"; then
    echo -e "  ${YELLOW}⚠${NC} $case_id: 评分卡解析失败"
    continue
  fi

  # 对应基线评分卡
  baseline_scorecard="$REPO_ROOT/$BASELINE_RUN/${case_id}.scorecard.md"
  if [[ ! -f "$baseline_scorecard" ]]; then
    echo -e "  ${YELLOW}ℹ${NC} $case_id: 无基线评分卡（可能是新增 case）"
    continue
  fi

  baseline_data=$(python -c "
import json, re
try:
    with open(r'$(cygpath -w "$baseline_scorecard" 2>/dev/null || echo "$baseline_scorecard")', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'\`\`\`json\s*(\{.*?\})\s*\`\`\`', content, re.DOTALL)
    if m:
        d = json.loads(m.group(1))
        contracts = d.get('contracts', {})
        for k, v in contracts.items():
            print(f'{k}={v}')
        p = d.get('p_level', 'none')
        print(f'p_level={p}')
        t = d.get('base_total', 0)
        print(f'base_total={t}')
except:
    pass
" 2>/dev/null || echo "")

  echo "  Case $case_id:"
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    key=$(echo "$line" | cut -d= -f1)
    current_val=$(echo "$line" | cut -d= -f2)
    baseline_val=$(echo "$baseline_data" | grep "^${key}=" | cut -d= -f2)

    if [[ "$key" == "p_level" ]]; then
      if [[ "$current_val" != "none" && ("$baseline_val" == "none" || -z "$baseline_val") ]]; then
        echo -e "    ${RED}🔴${NC} p_level: ${baseline_val:-none} → $current_val (新增 P 等级!)"
        RED_FLAG=1
      else
        echo -e "    ${GREEN}✓${NC} p_level: $current_val"
      fi
    elif [[ "$key" == "base_total" ]]; then
      diff_val=$(( ${current_val:-0} - ${baseline_val:-0} ))
      if [[ $diff_val -lt -3 ]]; then
        echo -e "    ${RED}🔴${NC} base_total: ${baseline_val:-0} → ${current_val:-0} (掉档 ≥3!)"
        RED_FLAG=1
      else
        echo -e "    ${GREEN}✓${NC} base_total: ${current_val:-0} (diff: $diff_val)"
      fi
    elif [[ "$current_val" == "FAIL" && "$baseline_val" == "PASS" ]]; then
      echo -e "    ${RED}🔴${NC} $key: PASS → FAIL (契约掉绿!)"
      RED_FLAG=1
    else
      echo -e "    ${GREEN}✓${NC} $key: $current_val"
    fi
  done <<< "$current_data"
  echo ""
done

echo "═══════════════════════════════════════"
if [[ $RED_FLAG -eq 1 ]]; then
  echo -e "  ${RED}🔴 红线命中！存在契约掉绿 / 维度掉档 / 新增 P0/P1${NC}"
  echo "  → 阻断发布，需人工确认是真退化还是评分噪声"
  echo "  → 确认后可触发 L2 深度复核"
  exit 1
else
  echo -e "  ${GREEN}🟢 无红线命中，可考虑晋升为新基线${NC}"
  echo "  → 修改 eval/baselines/$SKILL.json 指向新一轮"
  exit 0
fi
