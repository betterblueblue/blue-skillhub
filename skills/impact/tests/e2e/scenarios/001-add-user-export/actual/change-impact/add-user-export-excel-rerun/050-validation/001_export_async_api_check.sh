#!/usr/bin/env bash
# 001_export_async_api_check.sh
# 验证用户异步导出三个接口的契约：提交异步导出 + 查询任务状态 + 通用下载
#
# 用法：先登录拿到 token，再执行本脚本
#   TOKEN=xxx BASE_URL=http://localhost:8080 bash 001_export_async_api_check.sh
#
# 说明：本脚本为验证任务产出的接口契约检查脚本，不自动执行（需运行环境）。

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
TOKEN="${TOKEN:-}"

if [ -z "$TOKEN" ]; then
  echo "请先设置 TOKEN 环境变量（登录后获取的 Authorization Bearer token）"
  exit 1
fi

AUTH_HEADER="Authorization: Bearer $TOKEN"

echo "=== 1. 提交异步导出任务（选中 userIds=1,2）==="
SUBMIT_RESP=$(curl -s -X POST "$BASE_URL/system/user/exportAsync?userIds=1&userIds=2" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/x-www-form-urlencoded")
echo "响应：$SUBMIT_RESP"

TASK_ID=$(echo "$SUBMIT_RESP" | grep -o '"taskId":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -z "$TASK_ID" ]; then
  echo "FAIL: 未拿到 taskId，接口契约异常或无权限"
  exit 1
fi
echo "拿到 taskId：$TASK_ID"

echo ""
echo "=== 2. 轮询任务状态（最多 30 次，每次间隔 2 秒）==="
STATUS=""
FILE_PATH=""
for i in $(seq 1 30); do
  sleep 2
  TASK_RESP=$(curl -s -X GET "$BASE_URL/system/user/exportTask/$TASK_ID" -H "$AUTH_HEADER")
  STATUS=$(echo "$TASK_RESP" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "第 $i 次轮询：status=$STATUS"
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILED" ]; then
    FILE_PATH=$(echo "$TASK_RESP" | grep -o '"filePath":"[^"]*"' | head -1 | cut -d'"' -f4)
    break
  fi
done

if [ "$STATUS" != "SUCCESS" ]; then
  echo "FAIL: 任务未成功，最终状态=$STATUS"
  exit 1
fi

echo "任务成功，filePath=$FILE_PATH"
FILE_NAME=$(echo "$FILE_PATH" | rev | cut -d'/' -f1 | rev)
echo "提取 fileName=$FILE_NAME"

echo ""
echo "=== 3. 通用下载接口下载文件 ===="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/common/download?fileName=$FILE_NAME&delete=false" -H "$AUTH_HEADER")
echo "下载 HTTP 状态码：$HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  echo "PASS: 异步导出三接口契约验证通过"
else
  echo "FAIL: 下载接口返回 $HTTP_CODE"
  exit 1
fi
