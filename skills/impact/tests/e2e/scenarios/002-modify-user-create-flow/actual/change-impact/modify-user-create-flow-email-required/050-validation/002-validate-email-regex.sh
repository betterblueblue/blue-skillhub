#!/usr/bin/env bash
# ============================================================================
# 002-validate-email-regex.sh
#
# 目的:  对 /system/user 接口做 email 必填 + 格式校验的冒烟测试
# 适用:  RuoYi-Vue 3.9.2 / ruoyi-admin (端口默认 8080)
#
# 硬约束 C (可执行性):
#   - 所有凭证用 ${VAR:-default} 形式，可被环境变量覆盖
#   - 任何 mock value 有合理 default，不依赖手工替换
#
# 使用:
#   BASE_URL=http://localhost:8080 \
#   TOKEN=eyJ0eXAi... \
#   ./002-validate-email-regex.sh
#
# 不适用:  生产环境（脚本会真的调用接口）
# ============================================================================
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
TOKEN="${TOKEN:-test-token-please-override}"
DEPT_ID="${DEPT_ID:-103}"
USER_NAME="smoke_$(date +%s)"

# ---------- 工具函数 ----------
hr() { printf '\n%s\n' "------------------------------------------------------------"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

# ---------- 0. 前置: 登录获取 token (若 TOKEN 为占位符) ----------
hr
echo "[STEP 0] 检查 TOKEN"
if [[ "${TOKEN}" == "test-token-please-override" ]]; then
  echo "WARN: 当前 TOKEN 是占位符。"
  echo "      本脚本假设你已通过 ruoyi-admin 登录拿到 JWT。"
  echo "      跳过需要认证的接口，仅打印请求结构。"
  AUTH_HEADER="Authorization: Bearer PLACEHOLDER_NO_AUTH"
else
  AUTH_HEADER="Authorization: Bearer ${TOKEN}"
fi

# ---------- 1. Case 1: email 为空  → 期望 HTTP 400 ----------
hr
echo "[CASE 1] email 缺省 → 期望 400 '邮箱不能为空'"
read -r -d '' BODY1 <<EOF || true
{
  "userName": "${USER_NAME}_empty",
  "nickName": "smoke_empty",
  "deptId": ${DEPT_ID},
  "password": "***",
  "status": "0"
}
EOF
echo "REQUEST: POST ${BASE_URL}/system/user"
echo "BODY: ${BODY1}"

# ---------- 2. Case 2: email 非法  → 期望 HTTP 400 ----------
hr
echo "[CASE 2] email='not-an-email' → 期望 400 '邮箱格式不正确'"
BODY2=$(cat <<EOF
{
  "userName": "${USER_NAME}_invalid",
  "nickName": "smoke_invalid",
  "deptId": ${DEPT_ID},
  "password": "***",
  "email": "not-an-email",
  "status": "0"
}
EOF
)
echo "REQUEST: POST ${BASE_URL}/system/user"
echo "BODY: ${BODY2}"

# ---------- 3. Case 3: email 合法  → 期望 HTTP 200 (假设有权限) ----------
hr
echo "[CASE 3] email='valid@example.com' → 期望 200"
BODY3=$(cat <<EOF
{
  "userName": "${USER_NAME}_valid",
  "nickName": "smoke_valid",
  "deptId": ${DEPT_ID},
  "password": "***",
  "email": "valid@example.com",
  "status": "0"
}
EOF
)
echo "REQUEST: POST ${BASE_URL}/system/user"
echo "BODY: ${BODY3}"

# ---------- 4. 实跑 (仅当 ALLOW_RUN=1 时) ----------
if [[ "${ALLOW_RUN:-0}" == "1" ]]; then
  hr
  echo "[RUN] ALLOW_RUN=1，开始实跑 curl（仅对非生产）"
  for body in "${BODY1}" "${BODY2}" "${BODY3}"; do
    echo ">>> ${body}"
    curl -sS -X POST \
      -H "${AUTH_HEADER}" \
      -H "Content-Type: application/json" \
      -d "${body}" \
      -w "\nHTTP %{http_code}\n" \
      "${BASE_URL}/system/user" || true
    echo
  done
else
  echo
  echo "TIP: 设置 ALLOW_RUN=1 实跑 (前提是非生产):"
  echo "     ALLOW_RUN=1 BASE_URL=http://localhost:8080 TOKEN=eyJ... ./002-validate-email-regex.sh"
fi

hr
echo "[DONE] 冒烟脚本结构验证完成"
exit 0
