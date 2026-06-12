# Fixtures 来源与版本

每个 scenario 引用一个真实开源项目作为 fixture。

## 当前 fixtures

| 项目 | URL | Commit | 用途 |
|------|-----|--------|------|
| RuoYi-Vue | https://github.com/yangzongzhuan/RuoYi-Vue | 41720e624c5a668c7d3777835e4c87095a7a1dfd | impact 3 个场景 |

## 设置步骤

```bash
# 在仓库根目录
mkdir -p test-projects
git clone --depth 1 https://github.com/yangzongzhuan/RuoYi-Vue.git test-projects/ruoyi-vue
git -C test-projects/ruoyi-vue rev-parse HEAD
# 期望: 41720e624c5a668c7d3777835e4c87095a7a1dfd
```

## 何时需要更新

- 跑 scenario 发现 fixture 已变更（commit 漂移）
- 新增 scenario 引用更新的代码位置

## 注意事项

- fixture 不进 git（`test-projects/` 在 `.gitignore` 或临时目录）
- commit 哈希锁定避免上游变化导致 scenario 失效
- 跑 scenario 前可手动 `git -C test-projects/<fixture> pull` 验证仍可用
