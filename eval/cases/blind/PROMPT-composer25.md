# Composer 2.5 盲测 Prompt

> 复制下面整段内容发给 Composer 2.5 执行。

---

你接下来要连续完成 6 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/pathfinder`、`/impact`、`/impact-pro`）。

**输出目录规则**：所有产出写到 `test-projects/<项目>/change-impact/blind-composer25/<case-id>/` 下，带上模型名方便区分。

**重要**：每个任务请完整走完 skill 的流程（分析 → 提问 → 出文档），不要省略。如果 skill 要求确认，你在 prompt 里自行模拟用户回答"继续"即可，不要停下来等我确认。

---

## 任务 1（B5）— pathfinder 摸底 FastAPI 全栈项目

先运行 `/pathfinder`，然后处理以下需求：

项目路径：`test-projects/full-stack-fastapi-template`
输出到：`test-projects/full-stack-fastapi-template/change-impact/blind-composer25/B5/`

用户原话："我刚接手这个项目，之前没见过。帮我摸一下整体架构是什么，用了什么技术栈，数据库里有哪些核心表，前后端是怎么配合的，怎么在本地跑起来做开发。"

---

## 任务 2（B6）— pathfinder 摸底 Prisma/Express 项目

运行 `/pathfinder`，然后处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/blind-composer25/B6/`

用户原话："帮我摸一下这个 Node 项目的整体情况，重点看两个东西：一是数据模型有哪些表、关系是什么样的，二是认证流程是怎么走的，从登录到鉴权完整串一遍。"

---

## 任务 3（B1）— impact 分析操作日志加响应耗时

运行 `/impact`，然后处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/blind-composer25/B1/`

用户原话："我想给系统的操作日志加一个响应耗时记录功能。每次接口请求都要记录从进入到返回花了多少毫秒，然后在操作日志列表页面能看到这个耗时。"

---

## 任务 4（B2）— impact 分析密码加密方案变更

运行 `/impact`，然后处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/blind-composer25/B2/`

用户原话："我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。"

---

## 任务 5（B3）— impact-pro 分析 Prisma 用户加手机号

运行 `/impact-pro`，然后处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/blind-composer25/B3/`

用户原话："我想给用户加一个手机号字段。注册的时候可以选填，但如果填了必须是中国手机号格式（1开头的11位数字），而且手机号要唯一不能重复。"

---

## 任务 6（B4）— impact-pro 分析 go-admin 重置密码

运行 `/impact-pro`，然后处理以下需求：

项目路径：`test-projects/go-admin`
输出到：`test-projects/go-admin/change-impact/blind-composer25/B4/`

用户原话："管理员需要在用户管理页面重置任意用户的密码。点一下重置按钮，输入新密码就行，不需要旧密码验证。重置后用户用新密码登录。"

---

全部完成后，在 `test-projects/` 下列出所有 `blind-composer25/` 目录的文件清单作为总结。
