# [栈名] Profile

> 空白模板，复制此文件创建新 profile。

```yaml
name: example-stack
level: 1
matchers:
  files: []
  dependencies: []
  directories: []
roles: []
discovery_globs:
  service: []
  data_access: []
  api: []
  config: []
  test: []
  migration: []
style_axes:
  naming: ""        # 结论需运行时现采
  layering: ""      # 结论需运行时现采
  orm: ""           # 结论需运行时现采
  transaction: ""  # 结论需运行时现采
  exception: ""     # 结论需运行时现采
  logging: ""       # 结论需运行时现采
  api_response: ""  # 结论需运行时现采
  dependency_injection: "" # 结论需运行时现采
commands:
  build: ""
  test: ""
  dev: ""
  lint: ""
db_introspection:
  orm: ""
  migration_tool: ""
  schema_source: ""
validation_strategy:
  grep_patterns: []
  file_patterns: []
notes:
  limitations: []
  edge_cases: []
```

## 创建步骤

1. 复制本文件
2. 填写 `name` 和 `matchers`
3. 在真实项目上跑 `discovery_globs` 候选，验证能命中
4. 跑 `commands`，验证能执行
5. 填 `style_axes`（运行时从代码现采，不预置结论）
6. 填 `validation_strategy`（从项目中提取）
7. 列出 `limitations`
8. 在第二个同栈项目上复验
9. 提交 PR，标注 Level 1 验收通过
