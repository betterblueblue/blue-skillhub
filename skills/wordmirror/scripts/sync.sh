#!/usr/bin/env bash
# 把 wordmirror 的源头副本分发到各 Agent 客户端的 skills 目录。
# 用法：bash skills/wordmirror/scripts/sync.sh
# 数据（~/.wordmirror/）不进 skill 目录，天然共享，本脚本只管代码/文档版本。
# 注意：_prototype/ 里可能有真实数据的渲染稿（本地 gitignore 着），绝不能扩散——同步时排除。
set -e
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SRC="$ROOT/skills/wordmirror"
DESTS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.cursor/skills-cursor"
  "$HOME/.workbuddy/skills"
)
for dest in "${DESTS[@]}"; do
  [ -d "$dest" ] || { echo "跳过（不存在）：$dest"; continue; }
  rm -rf "$dest/wordmirror"          # 整目录替换，防止残留已删除的旧文件
  cp -r "$SRC" "$dest/wordmirror"
  # 剥掉不该进客户端的东西：原型目录（可能有真实数据稿）、测试、缓存
  rm -rf "$dest/wordmirror/_prototype" "$dest/wordmirror/tests"
  find "$dest/wordmirror" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
  rm -rf "$dest/wordmirror/.pytest_cache"
  echo "同步 wordmirror → $dest"
done
echo "完成。源头：$SRC"
