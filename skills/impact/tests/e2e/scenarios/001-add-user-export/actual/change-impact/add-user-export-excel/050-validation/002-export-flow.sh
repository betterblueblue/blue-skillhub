#!/usr/bin/env bash
# 050-validation/002-export-flow.sh
# 目的：演示异步导出完整流程（提交 + 轮询 + 下载）
# 凭证脱敏：所有 token/secret/password 使用 ${VAR:-default} 形式，可直跑
# 默认值仅为示例 token，请通过环境变量覆盖

set -euo pipefail

# --- 可配置项（直跑可用默认值；生产请用环境变量覆盖） -------------------------
BASE_URL="${BASE_URL:-http://localhost:8080}"
# 默认 token = 一个有 system:user:export 权限的示例账号；CI 覆盖：export TOKEN=...
TOKEN="${TOKEN:-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.demo-admin-token}"
# 无权限 token：默认 = 普通用户 token，期望返回 403
NO_PERM_TOKEN="${NO_PERM_TOKEN:-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.demo-no-perm-token}"
USER_IDS="${USER_IDS:-1,2,3}"
OUT_DIR="${OUT_DIR:-/tmp/ruoyi-export-demo}"
# -----------------------------------------------------------------------------

mkdir -p "$OUT_DIR"

echo "=== 1) 提交异步导出（admin） ==="
RESP_FILE="$OUT_DIR/submit.json"
HTTP_CODE=$(curl -sS -o "$RESP_FILE" -w "%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST "${BASE_URL}/system/user/exportAsync?userIds=${USER_IDS}")

echo "HTTP $HTTP_CODE  body=$(cat "$RESP_FILE")"

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "FAIL: 提交失败，HTTP $HTTP_CODE"
    exit 1
fi

TASK_ID=$(grep -oE '"taskId":"[a-zA-Z0-9]+"' "$RESP_FILE" | head -1 | cut -d'"' -f4)
echo "taskId=$TASK_ID"

echo "=== 2) 轮询任务状态（最多 30 秒） ==="
for i in $(seq 1 30); do
    POLL_FILE="$OUT_DIR/poll.json"
    HTTP_CODE=$(curl -sS -o "$POLL_FILE" -w "%{http_code}" \
        -H "Authorization: Bearer ${TOKEN}" \
        "${BASE_URL}/system/user/exportTask/${TASK_ID}")
    STATUS=$(grep -oE '"status":"[A-Z]+"' "$POLL_FILE" | head -1 | cut -d'"' -f4)
    echo "[$i] HTTP $HTTP_CODE  status=$STATUS"
    [[ "$STATUS" == "SUCCESS" || "$STATUS" == "FAILED" ]] && break
    sleep 1
done

if [[ "$STATUS" != "SUCCESS" ]]; then
    echo "FAIL: 任务未在超时内成功，最终 status=$STATUS"
    exit 1
fi

FILE_PATH=$(grep -oE '"filePath":"[^"]+"' "$POLL_FILE" | cut -d'"' -f4)
echo "=== 3) 拉取生成的 xlsx ==="
cp "$FILE_PATH" "$OUT_DIR/exported.xlsx"
ls -la "$OUT_DIR/exported.xlsx"

echo "=== 4) 反向用例：无权限 token 应 403 ==="
DENY_FILE="$OUT_DIR/deny.json"
DENY_CODE=$(curl -sS -o "$DENY_FILE" -w "%{http_code}" \
    -H "Authorization: Bearer ${NO_PERM_TOKEN}" \
    -X POST "${BASE_URL}/system/user/exportAsync?userIds=1")
echo "no-perm HTTP $DENY_CODE  body=$(cat "$DENY_FILE")"
if [[ "$DENY_CODE" != "403" ]]; then
    echo "FAIL: 期望 403，实际 $DENY_CODE"
    exit 1
fi

echo "=== PASS: 全流程通过 ==="
echo "导出文件: $OUT_DIR/exported.xlsx"
echo "任务ID : $TASK_ID"
