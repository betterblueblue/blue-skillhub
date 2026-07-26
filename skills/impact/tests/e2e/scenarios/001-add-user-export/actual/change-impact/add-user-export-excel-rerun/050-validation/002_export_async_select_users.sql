-- 002_export_async_select_users.sql
-- 验证选中用户导出的数据正确性
-- 对比：选中导出的用户行数 与 选中 userIds 在 sys_user 中的实际可见行数
--
-- 说明：本脚本为验证任务产出的 SQL 检查脚本，不自动执行（需 DB 连接）。
-- 执行前替换 :SELECTED_USER_IDS 为实际选中的用户编号。

-- 1. 查询选中用户在 sys_user 中的实际数量（未删除的）
SELECT COUNT(*) AS selected_user_count
FROM sys_user
WHERE del_flag = '0'
  AND user_id IN (:SELECTED_USER_IDS);

-- 2. 查询当前登录用户（admin）数据权限范围内的用户总数（对比全量导出场景）
-- admin 可见全部，普通用户只能见本部门及下级
SELECT COUNT(*) AS visible_user_count
FROM sys_user u
LEFT JOIN sys_dept d ON u.dept_id = d.dept_id
WHERE u.del_flag = '0';

-- 3. 验证导出文件不应包含已删除用户（del_flag='2'）
SELECT user_id, user_name, del_flag
FROM sys_user
WHERE del_flag = '2'
  AND user_id IN (:SELECTED_USER_IDS);
-- 预期：返回 0 行（已删除用户不应出现在导出结果中）

-- 4. 验证 password 字段不在导出范围（导出注解未标记 password）
-- 此项通过代码确认：SysUser.java:59 password 字段无 @Excel 注解
-- SQL 层无需检查，仅记录代码证据
