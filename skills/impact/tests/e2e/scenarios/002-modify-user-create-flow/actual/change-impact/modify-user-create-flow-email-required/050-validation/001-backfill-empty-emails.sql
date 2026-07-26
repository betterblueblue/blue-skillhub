-- ============================================================================
-- 001-backfill-empty-emails.sql
--
-- 目的:  把 sys_user 表里 email 列为空字符串或 NULL 的行批量回填为 'unknown@local'
-- 触发:  铁律 #2 (高风险 - 存量数据回填) + 铁律 #3 (DDL/DML 默认生成脚本不直接执行)
-- 适用:  RuoYi-Vue 3.9.2 / MySQL 5.7+ / sys_user.email 现状 varchar(50) default ''
--
-- 铁律 #2 DDL/DML 预检: 脚本顶部 SELECT COUNT(*) 报告预计影响行数，DBA 据此决定是否执行
-- 铁律 #3:           本脚本**不**直接执行；落 050-validation/，DBA 在维护窗口手动跑
--
-- 执行方式 (DBA):
--   mysql -u <user> -p <DB_NAME> < 001-backfill-empty-emails.sql
--   或在 MySQL 客户端:  source /path/to/001-backfill-empty-emails.sql
--
-- 回滚 (按需):
--   UPDATE sys_user SET email = '' WHERE email = 'unknown@local';
-- ============================================================================

-- 预检 #1: 报告待回填行数（铁律 #2 强制）
SELECT CONCAT('[PRECHECK] 待回填行数 (email IS NULL OR email = ''''): ', COUNT(*)) AS precheck_msg
FROM sys_user
WHERE email IS NULL OR email = '';

-- 预检 #2: 报告总用户数（用于影响评估）
SELECT CONCAT('[PRECHECK] sys_user 总行数: ', COUNT(*)) AS precheck_total
FROM sys_user;

-- ============================================================================
-- 主回填: 在事务内执行，便于回滚
-- 注意: 'unknown@local' 不是合法 RFC 5321 邮箱（无 TLD），仅作内部占位
-- ============================================================================
START TRANSACTION;

UPDATE sys_user
SET email = 'unknown@local',
    update_time = NOW()
WHERE email IS NULL OR email = '';

-- 验证 #1: 行级验证
SELECT ROW_COUNT() AS affected_rows;

-- 验证 #2: 再次扫描确认 0 行残留
SELECT CONCAT('[POSTCHECK] 残留空 email 行数 (应为 0): ', COUNT(*)) AS postcheck_msg
FROM sys_user
WHERE email IS NULL OR email = '';

COMMIT;

-- ============================================================================
-- 兜底: 如果上面的 START TRANSACTION / COMMIT 在某些 MySQL 配置下未自动提交
-- 可手动执行:  COMMIT;  或  ROLLBACK;
-- ============================================================================
