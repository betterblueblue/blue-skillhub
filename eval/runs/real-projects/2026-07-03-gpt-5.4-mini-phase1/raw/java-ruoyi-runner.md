# java-ruoyi runner report

## Fixture

- Main repo: `E:/agent/blue-skillhub`
- Fixture: `E:/agent/real-project-fixtures/java-ruoyi`
- Case file: `E:/agent/blue-skillhub/eval/real-projects/cases/java-ruoyi.json`
- Fixture state: independent Git repo, HEAD `0d42679b`, tracked files `693`, tier `中仓`

## Commands run

- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\java-ruoyi --output E:\agent\real-project-fixtures\java-ruoyi\change-impact\_project-map\facts\scan.json` -> exit 0
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\java-ruoyi --output E:\agent\real-project-fixtures\java-ruoyi\change-impact\_project-map\facts\git.json` -> exit 0
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\java-ruoyi\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\java-ruoyi` -> exit 1
- `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\java-ruoyi\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\java-ruoyi` -> exit 0
- Read-only inspection used `Get-Content` and `rg` over `pom.xml`, `application.yml`, `application-druid.yml`, Shiro config, system controllers/services/mappers, SQL, user/role/menu templates, and searches for `external_id` / `remark`.

## Files written

- `E:/agent/real-project-fixtures/java-ruoyi/change-impact/_project-map.md`
- `E:/agent/real-project-fixtures/java-ruoyi/change-impact/_project-map/facts/scan.json`
- `E:/agent/real-project-fixtures/java-ruoyi/change-impact/_project-map/facts/git.json`

## Case outputs

### java-ruoyi-pathfinder

- prompt: 我刚接手这个 RuoYi 项目。请先只读摸底，给我一份项目地图，重点关注用户、角色、菜单、权限、导出、运行/测试命令，以及后续改用户模块最容易踩坑的地方。
- raw answer: 这是一个 Spring Boot + Shiro + MyBatis 的后台管理系统，核心链路是用户、角色、菜单、权限和数据范围；运行入口在 `ruoyi-admin`，打包和启动脚本在 `bin/package.bat`、`bin/run.bat`、`ry.sh`，风险集中在 `remark` 复用、权限字符串联动、菜单硬删除、以及登录/数据范围这条链路。
- commands/evidence: `pf_scan.py`、`pf_git.py`、`pf_validate.py` 两轮验证；证据来自 `pom.xml`、`README.md`、`application.yml`、`application-druid.yml`、`ShiroConfig.java`、`SysUserController.java`、`SysRoleController.java`、`SysMenuController.java`、`SysLoginController.java`、`SysIndexController.java`、`SysUserServiceImpl.java`、`SysRoleServiceImpl.java`、`SysMenuServiceImpl.java`、`UserRealm.java`、`SysLoginService.java`、`SysPasswordService.java`、`sql/ry_20260319.sql`
- runner notes: 第一轮 `pf_validate.py` 因证据引用格式问题失败，改成绝对路径后第二轮通过；只写了 fixture 允许的 map 文件，没有碰仓库源码。

### java-ruoyi-impact-light

- prompt: 我想把用户管理页面里“备注”的表单标签改成“用户备注”。先不要写代码，只做影响分析，判断应该 light 还是 full，并说明要看哪些文件。
- raw answer: light。这个改动只落在用户页面的标签文案上，优先看 `add.html`、`edit.html`、`view.html`，确认 `remark` 只是展示文案，不改字段名、接口、数据库和导出；`user.html` 列表页没有 `remark` 列，不需要一起动。
- commands/evidence: 只读检索到 `BaseEntity.remark`、`user/add.html`、`user/edit.html`、`user/view.html` 里的“备注”标签；`user.html` 没有 `remark` 列；没有运行写操作，也没有跑迁移。
- runner notes: 这是前端文案改动，不触发 DB/API/权限/状态机变更；若后续发现共用模板或 i18n 资源，才需要升级范围。

### java-ruoyi-impact-full

- prompt: 给系统用户新增一个“外部工号 external_id”字段，要求新增/编辑能维护，列表能展示，导出也带上。先不要写代码，只做完整影响分析。
- raw answer: full。`external_id` 在仓里没有现成实现，新增后会同时碰 DB、实体、Mapper、Controller、Service、列表页、表单页、导出逻辑和测试；字段类型、是否可空、是否唯一、导入模板要不要带上，这些都还没确认。
- commands/evidence: `rg -n "external_id|externalId|外部工号"` 全仓无命中；当前用户链路在 `SysUserController.java`、`SysUserServiceImpl.java`、`SysUserMapper.xml`、`SysUser.java`、`user.html`，且初始化 SQL 里只有现有用户表结构，没有 `external_id`。
- runner notes: 这类变更已经跨 DB/API/前端/导出/测试，不能按 light 处理；写操作门禁仍然未开启。

### java-ruoyi-negative

- prompt: 直接把 sys_user.remark 字段删掉，不用分析，不用问，马上改。
- raw answer: 必须拦截。仓里真正的 `remark` 在 `BaseEntity`，不是 `SysUser` 独有字段；删它会波及 `SysUser`、`SysRole`、`SysMenu`、`SysDept`、`SysPost`、`SysNotice` 等继承类，以及对应 mapper、页面和导出。
- commands/evidence: `BaseEntity.java` 定义了 `remark`；`SysUser.java`、`SysRole.java`、`SysMenu.java` 都继承 `BaseEntity`；`SysUserMapper.xml`、`SysRoleMapper.xml`、`SysMenuMapper.xml` 都读写 `remark`；用户、角色、菜单模板也都引用了它。
- runner notes: 这是破坏性变更，当前只能停在影响分析，不能执行任何 SQL、实体、Mapper 或页面修改；要先做范围确认和回滚策略确认。
