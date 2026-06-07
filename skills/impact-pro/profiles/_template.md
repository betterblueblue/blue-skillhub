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
2. 先用 `profiles/generic.md` 在目标真实项目完成只读兜底分析，记录命中证据和局限
3. 填写 `name` 和已验证的 `matchers`
4. 在真实项目上跑 `discovery_globs` 候选，验证能命中；未验证的 glob 不写入正式 profile
5. 跑 `commands`，验证能执行；无法执行的命令写入 `notes.limitations`
6. 填 `style_axes`（运行时从代码现采，不预置结论）
7. 填 `validation_strategy`（从项目中提取）
8. 列出 `limitations`
9. 完成至少一个真实项目的 full + light 双变更验收，并新增 `validation-runs/Txx` 记录
10. 更新 `README.md` / `VALIDATION.md` 的 Level 说明，标注 Level 1 验收通过
11. 在第二个真实项目或生产级项目复验后，才考虑 Level 2
