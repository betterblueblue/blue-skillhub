# T22 生产级复验 - RuoYi 登录日志设备指纹

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Java / Spring Boot / MyBatis / Vue
- 项目路径：`E:\agent\impact-pro-validation-work\RuoYi-Vue`
- Commit：`7da12b0c07d43a9fcdf86570b0e81ba16d70adf4`
- 变更意图：登录日志新增“设备指纹 device_fingerprint”，登录成功/失败都记录，登录日志列表、查询、导出都支持。
- 使用档位：full
- 命中 profile：`java-spring-mybatis`
- 最终评分：93
- 失败等级：无
- 复验类型：生产级项目 full 变更复验

## 生产复杂度依据

RuoYi 是多模块管理后台，包含 `ruoyi-admin`、`ruoyi-framework`、`ruoyi-system`、`ruoyi-quartz`、`ruoyi-generator`、`ruoyi-ui` 和 SQL 初始化脚本。该变更跨登录异步记录、DB schema、MyBatis XML、Controller 权限、前端列表/导出，符合生产级 full 复验场景。

## 证据账本

| 类型 | 证据 | 结论 |
|------|------|------|
| 已确认 | `pom.xml`、多模块目录 | 命中 Java/Spring/MyBatis/RuoYi profile |
| 已确认 | `sql/ry_20260417.sql:562` | 存在 `sys_logininfor` 表 |
| 已确认 | `sql/ry_20260417.sql:566`、`:568`、`:569`、`:574`、`:575` | 登录日志已有 IP、浏览器、OS、状态和登录时间索引 |
| 已确认 | `ruoyi-framework/src/main/java/com/ruoyi/framework/web/service/SysLoginService.java` 多处 `AsyncFactory.recordLogininfor(...)` | 登录成功/失败/验证码错误等路径均异步记录登录日志 |
| 已确认 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/monitor/SysLogininforController.java` | 登录日志有 Controller 与权限入口 |
| 已确认 | `ruoyi-system/src/main/resources/mapper/system/SysLogininforMapper.xml` | MyBatis XML 需要 resultMap/select/insert 条件同步 |
| 已确认 | `ruoyi-ui/src/api/monitor/logininfor.js`、`ruoyi-ui/src/views/monitor/logininfor` | 前端 API 与页面存在 |
| 未确认 | 真实生产表行数、索引基数、脱敏策略 | 无 DB 直连，不能声称已确认 |

## 判档

建议档位：full。

触发 full 的证据：

- DB schema 新增字段。
- 登录成功/失败链路和异步日志记录。
- 后台查询、导出和权限菜单。
- 设备指纹可能涉及隐私/合规和脱敏展示。

允许 light 的证据：无。

## 苏格拉底式追问

1. `device_fingerprint` 来源是什么：前端 header、cookie、浏览器指纹 SDK，还是服务端生成？
2. 字段长度、是否允许为空、历史日志默认值和索引策略是什么？
3. 导出和列表是否展示原始值、脱敏值，还是仅用于检索？

## 验证方案

正向用例：

- 登录成功后写入设备指纹，列表和详情可查看。
- 登录失败/验证码错误也记录设备指纹。
- 按设备指纹查询命中对应登录日志。
- 导出包含或按要求脱敏设备指纹。

错误用例：

- 设备指纹为空时仍能记录登录日志。
- 超长设备指纹被截断或校验拒绝，不破坏登录。
- 恶意 XSS 字符在列表/导出中被安全处理。

## 运行时验证

执行命令：

```powershell
mvn -pl ruoyi-admin -am -DskipTests compile
```

结果：通过。

关键输出：

```text
Reactor Summary for ruoyi 3.9.2:
ruoyi-common SUCCESS
ruoyi-system SUCCESS
ruoyi-framework SUCCESS
ruoyi-quartz SUCCESS
ruoyi-generator SUCCESS
ruoyi-admin SUCCESS
BUILD SUCCESS
```

## 结论

通过生产级复验。`java-spring-mybatis` profile 在 RuoYi 的第二个 full 场景中继续稳定，能覆盖 DB、异步登录记录、MyBatis、Controller、前端和导出风险。
