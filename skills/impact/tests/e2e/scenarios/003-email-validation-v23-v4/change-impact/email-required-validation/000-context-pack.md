# Context Pack

## 1. 变更意图

- 用户原话：给用户创建流程加邮箱必填和格式校验
- 项目地图状态：无地图

## 2. 模式定级

- 模式：full
- 理由：涉及后端 Bean Validation + 前端校验 + 存量回填 + 测试，跨 4 个文件以上

## 7. 已确认事实

- 【代码推断】`SysUser.java` 的 `userName` getter 已有 `@Xss + @NotBlank + @Size` 三段式注解
- 【代码推断】`spring-boot-starter-validation` 已在 `ruoyi-common/pom.xml` 中
