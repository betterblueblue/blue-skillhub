# 010 — 需求文档 (Requirements)

## 1. 用户需求

给用户创建流程加邮箱必填和格式校验。

## 2. 验收标准

1. 后端 `SysUser.getEmail()` 有 `@NotBlank` + `@Email` 校验注解
2. 前端 `rules.email` 有 `required: true`
3. 存量空 email 数据有回填脚本
4. 有对应的单元测试
