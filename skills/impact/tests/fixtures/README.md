# 测试项目来源与版本

ImpactRadar 的 L0 场景会引用固定版本的真实开源项目。固定 commit 是测试的一部分，不能在运行前随意更新。

## 当前项目

| 项目 | URL | Commit | 用途 |
|------|-----|--------|------|
| RuoYi-Vue | https://github.com/yangzongzhuan/RuoYi-Vue | 41720e624c5a668c7d3777835e4c87095a7a1dfd | ImpactRadar 3 个场景 |

## 设置步骤

```bash
# 在仓库根目录
mkdir -p test-projects
git clone https://github.com/yangzongzhuan/RuoYi-Vue.git test-projects/ruoyi-vue
git -C test-projects/ruoyi-vue checkout 41720e624c5a668c7d3777835e4c87095a7a1dfd
git -C test-projects/ruoyi-vue rev-parse HEAD
# 期望：41720e624c5a668c7d3777835e4c87095a7a1dfd
```

## 何时需要更新

- 准备增加依赖上游新代码的场景。
- 上游仓库的旧 commit 已无法获取。
- 决定整体升级测试基线，并愿意同步检查所有文件路径和预期内容。

## 注意事项

- 测试项目不提交到本仓库，`test-projects/` 由 `.gitignore` 排除。
- 运行场景前先核对 HEAD，不要执行 `git pull`。拉取最新代码会改变固定版本，使路径和预期内容失效。
- 如需评估上游新版，请复制一份新的测试目录；确认所有场景仍成立后，再更新 commit 和相关 JSON。
