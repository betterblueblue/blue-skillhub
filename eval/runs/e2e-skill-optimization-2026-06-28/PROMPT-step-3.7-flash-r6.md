# 端到端验证（第六轮）：O14+O16 修复验证（Step 3.7 Flash）

> 复制 `---` 之后的内容发给模型执行。
> R6 复用 R5 的弱引导 prompt，测试 O14（强制跑脚本门禁）+ O16（读路径 SQL 判 light）是否修复 S37 的两个问题。
> prompt 与 R4/R5 完全一致（口语化，不给实现提示），纯靠 Skill 流程引导。

---

你接下来要完成 3 个任务，按顺序逐个执行。

**工作目录**：`e:\agent\blue-skillhub`

**测试项目路径**（只读，不修改源代码）：`test-projects/realworld-springboot-java-step-3.7-flash-r6`

这是一个 Spring Boot + MyBatis + SQLite 的 RealWorld (Conduit) API 实现，包含用户认证（JWT）、文章 CRUD、评论、关注、标签等功能。用 Gradle 构建。

**不要使用 `/pathfinder` 或 `/impact` 斜杠命令。** 手动从仓库目录 `skills/` 读取 skill 文件并按流程执行。仓库是 source of truth，不要用 `~/.claude/skills/` 下的已安装副本。

任务开始前，Read 以下入口文件，然后按其中的索引按需读取 references/、profiles/、templates/ 下的文件：

- `skills/pathfinder/SKILL.md`
- `skills/impact/SKILL.md`

---

## 任务 1：项目摸底

对 `test-projects/realworld-springboot-java-step-3.7-flash-r6` 做项目认知地图。

输出路径：`test-projects/realworld-springboot-java-step-3.7-flash-r6/change-impact/_project-map.md`

按 Pathfinder SKILL.md 中定义的流程执行。

---

## 任务 2

用户说："文章列表接口每次都返回完整正文，列表页加载特别慢，能不能列表不返回 body"

项目路径：`test-projects/realworld-springboot-java-step-3.7-flash-r6`
输出到：`test-projects/realworld-springboot-java-step-3.7-flash-r6/change-impact/e2e/C1/`

按 Impact SKILL.md 中定义的流程处理这个需求。

如果流程中需要向用户提问，你**不需要等待回答**。自行做合理假设并标注为 `[假设]`。只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行。

---

## 任务 3

用户说："现在文章一创建就公开了，能不能加个草稿功能，让用户先存草稿，想好了再发布"

项目路径：`test-projects/realworld-springboot-java-step-3.7-flash-r6`
输出到：`test-projects/realworld-springboot-java-step-3.7-flash-r6/change-impact/e2e/C2/`

按 Impact SKILL.md 中定义的流程处理这个需求。

如果流程中需要向用户提问，你**不需要等待回答**。自行做合理假设并标注为 `[假设]`。只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行。

---

## 全部完成后

列出所有产出文件清单作为总结：

```bash
echo "=== Pathfinder 产出 ==="
dir /s /b test-projects\realworld-springboot-java-step-3.7-flash-r6\change-impact\_project-map.md
dir /s /b test-projects\realworld-springboot-java-step-3.7-flash-r6\change-impact\_project-map\facts\

echo "=== Impact C1 产出 ==="
dir /s /b test-projects\realworld-springboot-java-step-3.7-flash-r6\change-impact\e2e\C1\

echo "=== Impact C2 产出 ==="
dir /s /b test-projects\realworld-springboot-java-step-3.7-flash-r6\change-impact\e2e\C2\
```
