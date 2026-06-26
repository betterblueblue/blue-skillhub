# Composer 2.5 盲测 v8 Prompt — 无 skill 组（C1）

> 复制下面整段内容发给 Composer 2.5 执行。
> 本 prompt 是「无 skill」对照组：不加载任何 skill 协议，不读 SKILL.md，不使用模板。
> 模型仍有文件读写、grep、终端等工具能力。
> 本 cell 使用独立测试项目副本，可与其他 cell 并行执行。

---

你接下来要连续完成 3 个分析任务，按顺序逐个执行。每个任务都是阅读项目源码、分析需求影响面、输出分析文档。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/prisma-express-ts`
- RuoYi-Vue 项目：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/ruoyi-vue`

**输出目录规则**：每个任务的产出写到该项目目录下的 `change-impact/v8-composer-noskill/[case-id]/`。

---

## 任务 1（B1'）— 并发登录限制

项目路径：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/ruoyi-vue/change-impact/v8-composer-noskill/B1/`

用户需求：
"我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

## 任务 2（B2'）— 请求体大小限制

项目路径：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/prisma-express-ts/change-impact/v8-composer-noskill/B2/`

用户需求：
"API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

## 任务 3（B3'）— 邮箱验证强制检查

项目路径：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/prisma-express-ts/change-impact/v8-composer-noskill/B3/`

用户需求：
"注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

全部完成后，列出所有 `v8-composer-noskill/` 目录的文件清单作为总结。
