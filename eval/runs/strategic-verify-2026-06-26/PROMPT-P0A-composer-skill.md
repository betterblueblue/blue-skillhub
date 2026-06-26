# P0 Cell A — Composer 2.5 + skill 战略定位验证

> 复制下面 `---` 之后的内容发给 Composer 2.5 执行。
> 本 cell 是战略定位验证的「有 skill」组：加载 CLAUDE.md（自动）+ /impact skill（v4.1 合并版）。
> 目标：验证 Composer 2.5 + skill 的分析质量是否接近 Opus + CLAUDE.md（仅行为准则）。
> 三个 cell（P0-A / P0-B / P1）在不同会话中并行运行，互不干扰。

---

你接下来要连续完成 3 个分析任务，按顺序逐个执行。全部使用 `/impact` skill。

**工作目录**：`e:\agent\blue-skillhub`

**测试项目路径**（共享，只读，不修改源代码）：
- RuoYi-Vue 项目：`test-projects/ruoyi-vue`
- Prisma/Express 项目：`test-projects/prisma-express-ts`

**关键前置步骤**：
任务开始前，你必须先 Read `skills/impact/SKILL.md`，再 Read 它引用的所有 `skills/impact/references/*.md` 文件。不要使用缓存的旧版协议——以当前文件内容为准。如果 SKILL.md 中提到 Phase 2 会自动探测技术栈并加载 `profiles/` 下的规则文件，请在 Phase 2 执行时也 Read 相关 profile 文件。

**重要 — 通用规则**：
1. 每个任务用 `/impact` skill 走完整 Phase 1-4 流程（意图捕获 → 上下文发现 → 风险预判 → 苏格拉底探索 → 定级 → 文档输出）。
2. **只做分析和文档输出，不进入 Phase 5 执行**——不修改任何源代码文件，不运行 build/test 命令。走到 Phase 4 文档输出完成即结束。
3. **模糊需求处理**：本次测试的用户需求是口语化、模糊的。如果 skill 在 Phase 3 提出澄清问题，你**不需要等待用户回答**。请自行做出**合理假设**，并明确标注为 `[假设]`。例如："[假设] 限制大小为 1MB"。所有假设必须在产出文档中集中列出。
4. 不同 case 之间相互独立，不要把前一个 case 的分析结论带到后一个 case。

**输出路径规则**：每个任务的产出写到指定路径下的 `change-impact/p0a-composer-skill/<case-id>/` 目录。

---

## Step 0: 环境清理

执行以下命令清理本 cell 的残留产出（不影响其他 cell）：

```bash
rm -rf test-projects/ruoyi-vue/change-impact/p0a-composer-skill/
rm -rf test-projects/prisma-express-ts/change-impact/p0a-composer-skill/
```

---

## 任务 1（B1'）— impact 分析并发登录限制

先 Read `skills/impact/SKILL.md`（如已读过可跳过），然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/p0a-composer-skill/B1/`

用户原话："我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录"

**注意**：只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行。

---

## 任务 2（B2'）— impact 分析请求体大小限制

Read `skills/impact/SKILL.md`（如已读过可跳过，但需确认内容是最新的），然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/p0a-composer-skill/B2/`

用户原话："API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

**注意**：只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行。

---

## 任务 3（B3'）— impact 分析邮箱验证强制检查

Read `skills/impact/SKILL.md`（如已读过可跳过），然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/p0a-composer-skill/B3/`

用户原话："注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

**注意**：只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行。

---

## 全部完成后

列出所有产出文件清单作为总结：

```bash
echo "=== RuoYi-Vue 产出 ==="
find test-projects/ruoyi-vue/change-impact/p0a-composer-skill/ -type f | sort

echo "=== Prisma-Express-TS 产出 ==="
find test-projects/prisma-express-ts/change-impact/p0a-composer-skill/ -type f | sort
```
