-- 050-validation/001-add-export-permission.sql
-- 目的：验证 / 幂等地确保 system:user:export 权限存在
-- 说明：本需求文档执行前已确认 menu_id=1004 (system:user:export) 已存在
--       本脚本为幂等 INSERT IGNORE 形式，可重复执行无需修改

START TRANSACTION;

-- 1) 确保父菜单存在（用户管理, menu_id=100）— 项目自带，重复插入会冲突，这里仅做存在性校验
SELECT 'parent menu 100:' AS info, COUNT(*) AS cnt
  FROM sys_menu WHERE menu_id = 100;

-- 2) 幂等写入导出权限（与 sql/ry_20260417.sql:193 一致）
-- 注：原 seed 已有此行；本脚本在全新环境（无 seed）下能补齐
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache,
    menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark
) VALUES (
    '1004', '用户导出', '100', '5',  '#', '', 1, 0, 'F', '0', '0',
    'system:user:export', '#', 'admin', NOW(), '', NULL, '用户导出权限'
) ON DUPLICATE KEY UPDATE perms = VALUES(perms);

-- 3) 给 admin 角色（role_id=1）授予该权限（与项目默认一致）
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, 1004 FROM DUAL
 WHERE NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = 1004);

-- 4) 验证
SELECT menu_id, menu_name, perms, status FROM sys_menu WHERE menu_id = 1004;
SELECT * FROM sys_role_menu WHERE menu_id = 1004;

COMMIT;

-- 凭证说明：此 SQL 不含任何 password / secret / token / connection string
