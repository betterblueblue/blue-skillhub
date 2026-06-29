#!/usr/bin/env bash
# validate.sh — scenario 静态校验函数库
# 用法：source lib/validate.sh

set -euo pipefail

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 全局计数
PASS_COUNT=0
FAIL_COUNT=0
SCENARIO_NAME=""

ok() { echo -e "  ${GREEN}✓${NC} $1"; PASS_COUNT=$((PASS_COUNT+1)); }
fail() { echo -e "  ${RED}✗${NC} $1"; FAIL_COUNT=$((FAIL_COUNT+1)); }
info() { echo -e "  ${YELLOW}ℹ${NC} $1"; }

# 辅助：把 Unix 风格路径转成 Windows 路径（给 Python 用）
to_win_path() {
  local p="$1"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$p"
  else
    echo "$p"
  fi
}

# 辅助：从 scenario 文件路径推断 repo 根目录
repo_root_from_scenario() {
  local file="$1"
  local dir
  dir=$(dirname "$(realpath "$file")")
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/skills" ]]; then
      echo "$dir"
      return
    fi
    dir=$(dirname "$dir")
  done
  echo "."
}

# 校验 JSON 是否含必需字段
validate_json_schema() {
  local file="$1"
  local required_fields=("id" "title" "skill" "stack" "fixture" "query" "expected")

  for field in "${required_fields[@]}"; do
    if ! grep -q "\"$field\"" "$file"; then
      fail "JSON 缺少必需字段: $field"
      return 1
    fi
  done
  ok "JSON schema 完整"
  return 0
}

# 校验 fixture 项目存在 + commit 哈希匹配
validate_fixture() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")

  local fixture_url fixture_commit fixture_name
  fixture_url=$(grep -oE '"url"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  fixture_commit=$(grep -oE '"commit"[[:space:]]*:[[:space:]]*"[a-f0-9]+"' "$file" | head -1 | sed 's/.*"commit"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  fixture_name=$(grep -oE '"project"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"project"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

  local fixture_name_slug
  fixture_name_slug=$(echo "$fixture_name" | tr 'A-Z' 'a-z')
  local fixture_path="$repo_root/test-projects/$fixture_name_slug"

  if [[ ! -d "$fixture_path" ]]; then
    fail "fixture 不存在: $fixture_path"
    info "  设置: git clone --depth 1 $fixture_url $fixture_path"
    return 1
  fi
  ok "fixture 存在: $fixture_name_slug"

  if [[ -n "$fixture_commit" ]]; then
    local actual_commit
    actual_commit=$(git -C "$fixture_path" rev-parse HEAD 2>/dev/null || echo "unknown")
    if [[ "$actual_commit" == "$fixture_commit" ]]; then
      ok "fixture commit 匹配: ${fixture_commit:0:7}"
    else
      fail "fixture commit 不一致: 期望 ${fixture_commit:0:7} 实际 ${actual_commit:0:7}"
      info "  解决: cd $fixture_path && git fetch && git checkout $fixture_commit"
      return 1
    fi
  fi
  return 0
}

# 校验 expected.iron_rules_triggered 中的每条硬性规则在 SKILL.md 中存在
validate_iron_rules() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")

  local skill
  skill=$(grep -oE '"skill"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  local skill_md="$repo_root/skills/$skill/SKILL.md"

  if [[ ! -f "$skill_md" ]]; then
    fail "SKILL.md 不存在: $skill_md"
    return 1
  fi

  local rules
  local file_win
  file_win=$(to_win_path "$file")
  rules=$(python -c "
import json
with open(r'$file_win', encoding='utf-8') as f:
    d = json.load(f)
expected = d.get('expected', {})
rules = expected.get('iron_rules_triggered', [])
print(' '.join(rules))
" 2>&1 | grep -v "^$" | head -1)

  if [[ -z "$rules" ]]; then
    info "expected.iron_rules_triggered 为空（不强制要求）"
    return 0
  fi

  for rule in $rules; do
    local rule_num="${rule#\#}"
    local pattern
    case "$skill" in
      impact)
        pattern="^\s*${rule_num}[\.、\)]\s+\*\*(最高确认|高风险|DB 只读|写入目标|破坏性|阻塞恢复|凭证脱敏)"
        ;;
      pathfinder)
        pattern="^\s*${rule_num}[\.、\)]\s+\*\*(只读硬性规则|唯一写入|可信度|不给修复建议|凭证脱敏|仓库内的文本)"
        ;;
      *)
        pattern="^\s*${rule_num}[\.、\)]\s+\*\*"
        ;;
    esac
    if grep -qE "$pattern" "$skill_md"; then
      ok "硬性规则 $rule 存在于 $skill/SKILL.md 强制规则"
    else
      fail "硬性规则 $rule 在 $skill/SKILL.md 强制规则未找到"
    fi
  done
}

# 校验 expected.references_loaded 中每个文件存在
validate_references() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")

  local skill
  skill=$(grep -oE '"skill"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  local refs_dir="$repo_root/skills/$skill/references"

  if [[ ! -d "$refs_dir" ]]; then
    fail "references 目录不存在: $refs_dir"
    return 1
  fi

  local refs
  local file_win
  file_win=$(to_win_path "$file")
  refs=$(python -c "
import json
with open(r'$file_win', encoding='utf-8') as f:
    d = json.load(f)
expected = d.get('expected', {})
refs = expected.get('references_loaded', [])
print(' '.join(r.split('/')[-1] for r in refs))
" 2>&1 | grep -v "^$" | head -1)

  if [[ -z "$refs" ]]; then
    info "expected.references_loaded 为空"
    return 0
  fi

  for ref in $refs; do
    if [[ -f "$refs_dir/$ref" ]]; then
      ok "reference 存在: $ref"
    else
      fail "reference 缺失: $ref"
    fi
  done
}

# 校验 files_to_inspect 中的文件存在 + 含必须字符串（用 win 路径给 Python）
validate_fixture_files() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")

  local fixture_name
  fixture_name=$(grep -oE '"project"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"project"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  local fixture_name_slug
  fixture_name_slug=$(echo "$fixture_name" | tr 'A-Z' 'a-z')
  local fixture_path="$repo_root/test-projects/$fixture_name_slug"

  if [[ ! -d "$fixture_path" ]]; then
    return 1
  fi

  local file_win fixture_win
  file_win=$(to_win_path "$file")
  fixture_win=$(to_win_path "$fixture_path")

  # 把每条结果通过前缀 OK:/FAIL: 输出，调用方按前缀计入计数
  # 用 process substitution 避免 pipe-subshell 计数丢失
  while IFS= read -r line; do
    if [[ "$line" == OK:* ]]; then
      ok "${line#OK: }"
    elif [[ "$line" == FAIL:* ]]; then
      fail "${line#FAIL: }"
    fi
  done < <(python -c "
import json, os
with open(r'$file_win', encoding='utf-8') as f:
    d = json.load(f)
files = d.get('files_to_inspect', [])
for entry in files:
    rel = entry.get('path', '')
    must_contain = entry.get('must_contain', '')
    must_exist = entry.get('must_exist', True)
    full = os.path.join(r'$fixture_win', rel)
    if must_exist and not os.path.exists(full):
        print(f'FAIL: {rel} 文件不存在')
        continue
    if must_contain:
        try:
            with open(full, 'r', encoding='utf-8', errors='ignore') as f2:
                content = f2.read()
            if must_contain in content:
                print(f'OK: {rel} 含目标字符串')
            else:
                print(f'FAIL: {rel} 不含 \"{must_contain[:40]}\"')
        except Exception as e:
            print(f'FAIL: {rel} 读取错误: {e}')
" 2>&1 | grep -E "^(OK|FAIL):")
}

# 校验 phase_3_5_classification 是 light 或 full
validate_classification() {
  local file="$1"
  local file_win
  file_win=$(to_win_path "$file")
  # 用 process substitution 避免 pipe-subshell 计数丢失
  while IFS= read -r line; do
    if [[ "$line" == OK:* ]]; then
      ok "${line#OK: }"
    else
      fail "${line#FAIL: }"
    fi
  done < <(python -c "
import json
with open(r'$file_win', encoding='utf-8') as f:
    d = json.load(f)
cls = d.get('expected', {}).get('phase_3_5_classification', '')
print('OK: phase_3_5 = ' + cls if cls in ('light', 'full') else 'FAIL: phase_3_5 必须是 light/full，实际=' + str(cls))
" 2>&1 | grep -E "^(OK|FAIL):")
}

# 校验单个 scenario
validate_scenario() {
  local file="$1"
  SCENARIO_NAME=$(basename "$file" .json)
  echo ""
  echo "═══ Scenario: $SCENARIO_NAME ═══"
  echo "  文件: $file"

  validate_json_schema "$file" || return 1
  validate_fixture "$file" || true
  validate_iron_rules "$file" || true
  validate_references "$file" || true
  validate_code_graph_adapter "$file" || true
  validate_classification "$file" || true
  validate_fixture_files "$file" || true
  validate_shared_contracts "$file" || true
}

# 校验可选 code graph adapter 存在且包含结果完整性纪律
validate_code_graph_adapter() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")
  local skill
  skill=$(grep -oE '"skill"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  local adapter="$repo_root/skills/$skill/code-graph-adapters/generic-mcp.md"

  if [[ ! -e "$adapter" ]]; then
    info "code graph adapter 未配置（可选）"
    return 0
  fi

  ok "code graph adapter 存在: code-graph-adapters/generic-mcp.md"
  if grep -q "Freshness and result integrity" "$adapter" && grep -q "truncated" "$adapter" && grep -q "empty.*result\|Empty.*does not prove" "$adapter"; then
    ok "code graph adapter 含新鲜度/截断/空结果纪律"
  else
    fail "code graph adapter 缺少新鲜度/截断/空结果纪律"
  fi
}

# ── 共享契约存在性检查（三 skill 统一） ──
# 检查 docs/skill-eval/contracts.md 中列出的每条共享契约
# 在本 skill 的 SKILL.md 强制规则中存在

validate_shared_contracts() {
  local file="$1"
  local repo_root
  repo_root=$(repo_root_from_scenario "$file")
  local skill
  skill=$(grep -oE '"skill"[[:space:]]*:[[:space:]]*"[^"]+"' "$file" | head -1 | sed 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  local skill_md="$repo_root/skills/$skill/SKILL.md"
  local contracts_md="$repo_root/docs/skill-eval/contracts.md"

  if [[ ! -f "$contracts_md" ]]; then
    info "docs/skill-eval/contracts.md 不存在，跳过共享契约检查"
    return 0
  fi
  if [[ ! -f "$skill_md" ]]; then
    fail "SKILL.md 不存在: $skill_md"
    return 1
  fi

  # 按 skill 选择搜索关键词（见 contracts.md「各 skill 搜索关键词」）
  case "$skill" in
    impact)
      local keywords=("最高确认法" "凭证脱敏" "仓库内的文本不构成指令" "唯一写入目标")
      ;;
    pathfinder)
      local keywords=("可信度强制" "凭证脱敏" "仓库内的文本不构成指令" "唯一写入目标")
      ;;
    *)
      fail "未知 skill: $skill"
      return 1
      ;;
  esac

  for kw in "${keywords[@]}"; do
    if grep -q "$kw" "$skill_md"; then
      ok "共享契约 [$kw] 在 $skill/SKILL.md 强制规则存在"
    else
      fail "共享契约 [$kw] 在 $skill/SKILL.md 强制规则未找到 — 可能不一致！"
    fi
  done
}

# 报告总数
print_summary() {
  echo ""
  echo "═══════════════════════════════════════"
  echo "  PASS: $PASS_COUNT"
  echo "  FAIL: $FAIL_COUNT"
  echo "═══════════════════════════════════════"
  if [[ $FAIL_COUNT -gt 0 ]]; then
    return 1
  fi
  return 0
}
