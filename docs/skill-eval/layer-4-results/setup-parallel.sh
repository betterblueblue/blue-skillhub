# setup-parallel.sh — 并行跑测环境准备

# 在 blue-skillhub 根目录执行此脚本

ROOT="E:/agent/blue-skillhub"
cd "$ROOT"

echo "=== 克隆 ruoyi-vue 副本（4 个场景各一份）==="

# A1: impact light
echo "[1/4] ruoyi-vue-a1 ..."
cp -r test-projects/ruoyi-vue test-projects/ruoyi-vue-a1

# A2: impact full
echo "[2/4] ruoyi-vue-a2 ..."
cp -r test-projects/ruoyi-vue test-projects/ruoyi-vue-a2

# B3: adapter selection (PG config)
echo "[3/4] ruoyi-vue-b3 ..."
cp -r test-projects/ruoyi-vue test-projects/ruoyi-vue-b3
# 修改为 PG 配置
cd test-projects/ruoyi-vue-b3
sed -i 's/com.mysql.cj.jdbc.Driver/org.postgresql.Driver/' ruoyi-admin/src/main/resources/application-druid.yml
sed -i 's|jdbc:mysql://localhost:3306/ry-vue?[^ ]*|jdbc:postgresql://localhost:5432/ry-vue|' ruoyi-admin/src/main/resources/application-druid.yml
sed -i 's/SELECT 1 FROM DUAL/SELECT 1/' ruoyi-admin/src/main/resources/application-druid.yml
sed -i 's/helperDialect: mysql/helperDialect: postgresql/' ruoyi-admin/src/main/resources/application.yml
cd "$ROOT"

# C1: pathfinder
echo "[4/4] ruoyi-vue-c1 ..."
cp -r test-projects/ruoyi-vue test-projects/ruoyi-vue-c1

echo ""
echo "=== 验证 ==="
echo "ruoyi-vue-a1: $(ls test-projects/ruoyi-vue-a1/pom.xml 2>/dev/null && echo OK || echo MISSING)"
echo "ruoyi-vue-a2: $(ls test-projects/ruoyi-vue-a2/pom.xml 2>/dev/null && echo OK || echo MISSING)"
echo "ruoyi-vue-b3: $(ls test-projects/ruoyi-vue-b3/pom.xml 2>/dev/null && echo OK || echo MISSING)"
echo "  PG driver: $(grep 'org.postgresql.Driver' test-projects/ruoyi-vue-b3/ruoyi-admin/src/main/resources/application-druid.yml | head -1)"
echo "ruoyi-vue-c1: $(ls test-projects/ruoyi-vue-c1/pom.xml 2>/dev/null && echo OK || echo MISSING)"
echo ""
echo "=== 并行布局完成 ==="
echo "A1 → test-projects/ruoyi-vue-a1"
echo "A2 → test-projects/ruoyi-vue-a2"
echo "B1 → test-projects/go-admin（独立项目，已存在）"
echo "B2 → test-projects/full-stack-fastapi-template（独立项目，已存在）"
echo "B3 → test-projects/ruoyi-vue-b3（PG 配置已改）"
echo "C1 → test-projects/ruoyi-vue-c1"
echo ""
echo "现在可以打开 6 个终端，各自读取对应的 task 文件并行执行。"
