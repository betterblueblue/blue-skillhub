#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for python_cmd in python3 python py; do
  if command -v "$python_cmd" >/dev/null 2>&1 && "$python_cmd" -c 'import sys' >/dev/null 2>&1; then
    exec "$python_cmd" "$script_dir/impact-write-gate.py"
  fi
done

echo "python was not found; cannot run impact-write-gate" >&2
exit 2
