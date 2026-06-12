# Fixtures 来源与版本

| 项目 | URL | Commit | 用途 |
|------|-----|--------|------|
| go-admin | https://github.com/go-admin-team/go-admin | b83eef8670b09533213cdd29635e01842704ddd8 | impact-pro 2 个场景 |

## 设置步骤

```bash
# 在仓库根目录
mkdir -p test-projects
git clone --depth 1 https://github.com/go-admin-team/go-admin.git test-projects/go-admin
git -C test-projects/go-admin rev-parse HEAD
# 期望: b83eef8670b09533213cdd29635e01842704ddd8
```

## fixture 不进 git
- `test-projects/` 在工作区，git 不追踪
- commit 哈希锁定避免上游变化导致 scenario 失效
