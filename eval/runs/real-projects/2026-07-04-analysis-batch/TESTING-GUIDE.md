# 测试操作指南

## 核心原则

**每个 run 开始前，fixture 必须是干净的。** 上一个 run 的 `change-impact/` 产物不能留给下一个 run 看。

## 19 个 run 的 fixture 分配

| fixture | run 清单 | 数量 |
|---------|----------|------|
| java-ruoyi | D1×3 (composer/m3/deepseek) + D13×3 + D14×1 | 7 |
| node-realworld-prisma | D8×2 + D15×3 | 5 |
| python-fastapi-template | D3×1 + D16×3 + D17×2 | 6 |
| monorepo-full-stack-starter | D18×1 | 1 |

## 每次 run 的操作流程

### 第 1 步：清理 fixture

```powershell
# read-only-original 场景（D1, D8, D13-D18）
Remove-Item -Path "E:\agent\real-project-fixtures\<fixture>\change-impact" -Recurse -Force -ErrorAction SilentlyContinue

# 验证干净
cd E:\agent\real-project-fixtures\<fixture>
git status --short
# 期望输出：空（没有任何 untracked 或 modified 文件）
```

### 第 2 步：开新的 agent 会话

用对应 runner 开一个新的 agent 会话。不要复用上一个 run 的会话。

### 第 3 步：贴 prompt

把对应的 prompt 文件内容贴进去。prompt 格式：

```
[评测环境]
工作目录：...
Skill：...
输出归档：...

---

[用户输入]
...
```

### 第 4 步：agent 执行

让 agent 自己跑。不要中途指导。

### 第 5 步：检查结果

- fixture 的 `git status --short` 是否符合预期（read-only 场景应只有 `?? change-impact/`）
- README 是否写到了指定路径
- validator 结果是否真实（有原始输出 + 退出码）

### 第 6 步：归档

把 README 和产出物归档到对应的 run 目录。

## 已知问题：D1 三个 runner 的结果可能被污染

D1 的三个 runner（Composer、M3、DeepSeek）共用同一个 java-ruoyi fixture，且没有在每次 run 前清理。Composer 先跑写了 `change-impact/_project-map.md`，M3 和 DeepSeek 跑的时候都看到了这个文件（两个 README 里都写了"已存在"、"已有但已覆盖"）。

**影响**：M3 和 DeepSeek 的 D1 结果可能不是完全独立完成的——它们可能读了 Composer 的产物作为参考。

**处理建议**：
- 如果 M3 和 DeepSeek 的产物质量明显好于 Composer（因为读了前者的地图），需要在 delivery-results 里标注"可能被污染"
- 如果要严格公平，需要在清理 fixture 后重跑 M3 和 DeepSeek 的 D1

## D3 的特殊处理

D3 的 fixture_mode 是 `isolated-copy`，需要从原始 fixture 复制一份副本：

```powershell
Copy-Item -Path "E:\agent\real-project-fixtures\python-fastapi-template" -Destination "E:\agent\real-project-fixtures\python-fastapi-template-d3-m3" -Recurse
```

然后 prompt 里的工作目录改为副本路径。
