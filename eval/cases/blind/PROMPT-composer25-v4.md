# Composer 2.5 盲测 v4 Prompt

> 复制下面整段内容发给 Composer 2.5 执行。
> v4 跑 4 个 case（B6/B1/B2/B3），验证 v3 后续优化（优化 6-8）是否生效且不退步。
> v4 新增：每个任务开始前先 Read 对应 skill 的 SKILL.md，确保加载含优化 6-8 的最新协议。

---

你接下来要连续完成 4 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/pathfinder`、`/impact`、`/impact-pro`）。

**输出目录规则**：所有产出写到 `test-projects/<项目>/change-impact/blind-v4-composer25/<case-id>/` 下。

**重要**：每个任务请完整走完 skill 的流程（分析 → 提问 → 出文档），不要省略。如果 skill 要求确认，你在 prompt 里自行模拟用户回答"继续"即可，不要停下来等我确认。

**关键前置步骤（v4 新增）**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。具体来说：
- pathfinder 任务前 Read `skills/pathfinder/SKILL.md`
- impact 任务前 Read `skills/impact/SKILL.md`
- impact-pro 任务前 Read `skills/impact-pro/SKILL.md`

读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。不要使用缓存的旧版协议——以当前文件内容为准。

---

## 任务 1（B6）— pathfinder 摸底 Prisma/Express 项目

先 Read `skills/pathfinder/SKILL.md`，然后运行 `/pathfinder`，处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/blind-v4-composer25/B6/`

用户原话："帮我摸一下这个 Node 项目的整体情况，重点看两个东西：一是数据模型有哪些表、关系是什么样的，二是认证流程是怎么走的，从登录到鉴权完整串一遍。"

---

## 任务 2（B1）— impact 分析操作日志加响应耗时

先 Read `skills/impact/SKILL.md`，然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/blind-v4-composer25/B1/`

用户原话："我想给系统的操作日志加一个响应耗时记录功能。每次接口请求都要记录从进入到返回花了多少毫秒，然后在操作日志列表页面能看到这个耗时。"

---

## 任务 3（B2）— impact 分析密码加密方案变更

先 Read `skills/impact/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/blind-v4-composer25/B2/`

用户原话："我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。"

---

## 任务 4（B3）— impact-pro 分析 Prisma 用户加手机号

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/blind-v4-composer25/B3/`

用户原话："我想给用户加一个手机号字段。注册的时候可以选填，但如果填了必须是中国手机号格式（1开头的11位数字），而且手机号要唯一不能重复。"

---

全部完成后，在 `test-projects/` 下列出所有 `blind-v4-composer25/` 目录的文件清单作为总结。
