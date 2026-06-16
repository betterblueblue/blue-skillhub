# 任务 T05-B3 — adapter 选择验证（强模型）

> 🔴 最关键。独立任务。读我即跑。
> 产出：`docs/skill-eval/layer-4-results/T05-adapter-selection-strong.md`
> PG 配置已由 setup-parallel.sh 在 ruoyi-vue-b3 中预先改好。

## 执行

```bash
cd E:/agent/blue-skillhub/test-projects/ruoyi-vue-b3
```

确认 PG 配置生效：
```bash
grep "postgresql" ruoyi-admin/src/main/resources/application-druid.yml | head -2
```
应有 `org.postgresql.Driver` 和 `jdbc:postgresql://` → 确认后继续。

```
/impact-pro

给 sys_user 加一个 phone_model 字段（varchar(64)），在用户列表接口返回。
```

**只走到 Phase 2 完成即可，不需要真执行。**

## 判定（PASS/FAIL，不评分）

| 判定项 | PASS/FAIL |
|--------|-----------|
| Phase 2.1 解析 datasource URL 识别到 PostgreSQL | |
| Phase 2.2 加载了 db-adapters/postgresql.md | |
| Phase 2.2 **没有**加载 mysql.md | |
| Phase 2.3 使用 pg_catalog 而非 SHOW CREATE TABLE | |
| 明确输出"DB 类型覆盖"说明 | |

全部 PASS → adapter 优先级链修复生效。任一 FAIL → P0 回归。

## 写入

`E:/agent/blue-skillhub/docs/skill-eval/layer-4-results/T05-adapter-selection-strong.md`
