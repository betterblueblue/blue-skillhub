# P0 Cell B — Opus + CLAUDE.md（仅行为准则）战略定位验证

> 复制下面 `---` 之后的内容发给 Opus 执行。
> 本 cell 是战略定位验证的「无 skill」对照组：只有 CLAUDE.md 行为准则，不加载任何 skill。
> 目标：作为基准线，对比 Composer 2.5 + skill 是否达到同等分析质量。
> 三个 cell（P0-A / P0-B / P1）在不同会话中并行运行，互不干扰。

---

你接下来要连续完成 3 个分析任务，按顺序逐个执行。

**工作目录**：`e:\agent\blue-skillhub`

**CLAUDE.md**：工作区行为准则已自动加载。如果你不在 Claude Code 环境中运行，请先 Read `CLAUDE.md` 文件。

**测试项目路径**（共享，只读，不修改源代码）：
- RuoYi-Vue 项目：`test-projects/ruoyi-vue`
- Prisma/Express 项目：`test-projects/prisma-express-ts`

**重要 — 约束规则**：
1. **不使用任何 skill**——不要 Read `skills/` 目录下的任何文件，不要运行 `/impact`、`/impact-pro`、`/pathfinder` 或任何其他 skill 命令。
2. **只做分析**——阅读项目源码，分析需求的影响面，输出分析文档。不修改任何源代码文件。
3. **模糊需求处理**：用户需求是口语化、模糊的。你需要自行识别模糊点，做出合理假设，并在文档中明确标注哪些是假设、哪些是已确认的事实。
4. 你有完整的文件读取（Read）、搜索（Grep/Glob）、终端（Bash）等工具能力。
5. 不同 case 之间相互独立，不要把前一个 case 的分析结论带到后一个 case。
6. 输出格式自由——不要求特定模板，但分析文档应足够完整，能作为开发依据。

**输出路径规则**：每个任务的产出写到指定路径下，每个 case 一个目录。

---

## Step 0: 环境清理

执行以下命令清理本 cell 的残留产出（不影响其他 cell）：

```bash
rm -rf test-projects/ruoyi-vue/change-impact/p0b-opus-noskill/
rm -rf test-projects/prisma-express-ts/change-impact/p0b-opus-noskill/
```

---

## 任务 1（B1'）— 并发登录限制

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/p0b-opus-noskill/B1/`

用户需求：
"我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录"

请阅读项目源码，分析这个需求的影响面，输出分析文档。文档至少应包含：现状分析（功能是否已实现）、影响面（涉及哪些文件/模块）、风险点、建议方案、假设清单。

**注意**：只做分析，不修改源代码。

---

## 任务 2（B2'）— 请求体大小限制

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/p0b-opus-noskill/B2/`

用户需求：
"API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

请阅读项目源码，分析这个需求的影响面，输出分析文档。文档至少应包含：现状分析（功能是否已实现）、影响面（涉及哪些文件/模块）、风险点、建议方案、假设清单。

**注意**：只做分析，不修改源代码。

---

## 任务 3（B3'）— 邮箱验证强制检查

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/p0b-opus-noskill/B3/`

用户需求：
"注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

请阅读项目源码，分析这个需求的影响面，输出分析文档。文档至少应包含：现状分析（功能是否已实现）、影响面（涉及哪些文件/模块）、风险点、建议方案、假设清单。

**注意**：只做分析，不修改源代码。

---

## 全部完成后

列出所有产出文件清单作为总结：

```bash
echo "=== RuoYi-Vue 产出 ==="
find test-projects/ruoyi-vue/change-impact/p0b-opus-noskill/ -type f | sort

echo "=== Prisma-Express-TS 产出 ==="
find test-projects/prisma-express-ts/change-impact/p0b-opus-noskill/ -type f | sort
```
