# Step 3.7 Flash 盲测 v6 Prompt — 有 skill 组（C6）

> 复制下面整段内容发给 Step 3.7 Flash 执行。
> 本 prompt 是「有 skill」实验组：每个任务前 Read 对应 skill 的 SKILL.md，走完整 Phase 流程。
> v6 使用优化完成后的最新 SKILL.md（现状核查门禁 + 证据标签强制化 + Out of Scope 约束 + 接口一致性自检）。
> 本 cell 使用独立测试项目副本，可与其他 cell 并行执行。

---

你接下来要连续完成 3 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/impact`、`/impact-pro`）。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/prisma-express-ts`
- RuoYi-Vue 项目：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/ruoyi-vue`

**Skill 文件路径**（共享，只读）：
- impact：`skills/impact/SKILL.md`
- impact-pro：`skills/impact-pro/SKILL.md`

**输出路径规则**：
- 每个任务使用 skill 的默认输出路径，不指定自定义子目录
- impact/impact-pro 输出到项目目录下的 `change-impact/B1/`、`change-impact/B2/`、`change-impact/B3/`（用 case-id 作为需求名称）
- 所有任务完成后，统一归档到 `change-impact/v6-step-skill/` 目录（见最后一步）

**重要**：每个任务请完整走完 skill 的流程（分析 → 提问 → 出文档），不要省略。如果 skill 要求确认，你在 prompt 里自行模拟用户回答"继续"即可，不要停下来等我确认。

**关键前置步骤**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。具体来说：
- impact 任务前 Read `skills/impact/SKILL.md`
- impact-pro 任务前 Read `skills/impact-pro/SKILL.md`

读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。不要使用缓存的旧版协议——以当前文件内容为准。

---

## 任务 1（B1'）— impact 分析并发登录限制

先 Read `skills/impact/SKILL.md`，然后运行 `/impact`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/ruoyi-vue/change-impact/B1/`

用户原话："系统需要支持同一用户同一时刻只能在一个地方登录。如果用户在A设备登录了，又在B设备登录，A设备要自动下线，就是被踢出去。B设备的登录是正常的。反过来也一样，新登录的踢掉旧的。"

---

## 任务 2（B2'）— impact-pro 分析请求体大小限制

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/prisma-express-ts/change-impact/B2/`

用户原话："目前系统没有对 API 请求体大小做限制，我想加一个全局的请求体大小限制。普通接口限制 1MB，文件上传接口限制 10MB。超过限制的请求直接返回 413 状态码，返回错误信息提示请求体过大。"

---

## 任务 3（B3'）— impact-pro 分析邮箱验证强制检查

先 Read `skills/impact-pro/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v6/cell-C6/test-projects/prisma-express-ts/change-impact/B3/`

用户原话："用户注册后必须验证邮箱才能使用系统功能。现在虽然有发验证邮件的功能，但不验证邮箱也能登录和调用接口，这个安全漏洞要修。要求：未验证邮箱的用户登录时提示请先验证邮箱，已登录但未验证的用户调用受保护接口时也要拦截。"

---

## 归档步骤

全部 3 个任务完成后，将产出归档到模型专属目录：

```bash
CELL_DIR="eval/runs/blind-2026-06-25-v6/cell-C6"

# ruoyi-vue（B1）
mkdir -p "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v6-step-skill/"
mv "$CELL_DIR/test-projects/ruoyi-vue/change-impact/B1/" "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v6-step-skill/B1/"

# prisma-express-ts（B2 + B3）
mkdir -p "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v6-step-skill/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B2/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v6-step-skill/B2/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B3/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v6-step-skill/B3/"
```

归档完成后，列出所有 `v6-step-skill/` 目录的文件清单作为总结。
