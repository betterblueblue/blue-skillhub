# Composer 2.5 盲测 v5 Prompt — 无 skill 组（C3）

> 复制下面整段内容发给 Composer 2.5 执行。
> 本 prompt 是「无 skill」对照组：不加载任何 skill 协议，不读 SKILL.md，不使用模板。
> 模型仍有文件读写、grep、终端等工具能力。
> 本 cell 使用独立测试项目副本，可与其他 cell 并行执行。

---

你接下来要连续完成 4 个分析任务，按顺序逐个执行。每个任务都是阅读项目源码、分析需求影响面、输出分析文档。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/prisma-express-ts`
- RuoYi-Vue 项目：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/ruoyi-vue`

**输出目录规则**：每个任务的产出写到该项目目录下的 `change-impact/v5-composer-noskill/[case-id]/`。

---

## 任务 1（B6）— 摸底 Prisma/Express 项目

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/prisma-express-ts/change-impact/v5-composer-noskill/B6/`

用户需求：
"帮我摸一下这个 Node 项目的整体情况，重点看两个东西：一是数据模型有哪些表、关系是什么样的，二是认证流程是怎么走的，从登录到鉴权完整串一遍。"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

## 任务 2（B1）— 操作日志加响应耗时

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/ruoyi-vue/change-impact/v5-composer-noskill/B1/`

用户需求：
"我想给系统的操作日志加一个响应耗时记录功能。每次接口请求都要记录从进入到返回花了多少毫秒，然后在操作日志列表页面能看到这个耗时。"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

## 任务 3（B2）— 密码加密方案变更

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/ruoyi-vue/change-impact/v5-composer-noskill/B2/`

用户需求：
"我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

## 任务 4（B3）— 用户加手机号字段

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C3/test-projects/prisma-express-ts/change-impact/v5-composer-noskill/B3/`

用户需求：
"我想给用户加一个手机号字段。注册的时候可以选填，但如果填了必须是中国手机号格式（1开头的11位数字），而且手机号要唯一不能重复。"

请阅读项目源码，分析这个需求的影响面，输出分析文档。

---

全部完成后，列出所有 `v5-composer-noskill/` 目录的文件清单作为总结。
