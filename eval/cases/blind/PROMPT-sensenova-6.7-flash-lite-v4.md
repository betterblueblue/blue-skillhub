# SenseNova-6.7-Flash-Lite 盲测 v4 Prompt

> 复制下面整段内容发给 SenseNova-6.7-Flash-Lite 执行。
> v4 跑 4 个 case（B6/B1/B2/B3），验证 v3.8 协议（优化 6-8）在新模型上的表现。
> 本模型为首次参与盲测，无 v3 基线，v4 结果将作为初始基线。
> 每个任务开始前先 Read 对应 skill 的 SKILL.md，确保加载含优化 6-8 的最新协议。
> v4 修正：测试前清理 change-impact/ 隔离环境，使用默认输出路径，完成后统一归档。

---

## Step 0: 清理环境（必做）

在开始任何任务之前，必须先清理两个测试项目的 `change-impact/` 目录。这一步确保没有之前测试的残留文件污染扫描结果和 Script Gate 验证：

```bash
rm -rf test-projects/prisma-express-ts/change-impact/
rm -rf test-projects/ruoyi-vue/change-impact/
```

如果不清理，pf_scan.py 会把残留文件计入项目文件数，pf_validate.py 可能因旧 facts 文件假通过。

---

你接下来要连续完成 4 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/pathfinder`、`/impact`、`/impact-pro`）。

**输出路径规则（v4 修正）**：
- 每个任务使用 skill 的默认输出路径，不指定自定义子目录
- pathfinder 输出到 `change-impact/_project-map.md`（SKILL.md 默认路径）
- impact/impact-pro 输出到 `change-impact/B1/`、`change-impact/B2/`、`change-impact/B3/`（用 case-id 作为需求名称）
- 所有任务完成后，统一归档到 `blind-v4-sensenova-6.7-flash-lite/` 目录（见最后一步）

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

用户原话："帮我摸一下这个 Node 项目的整体情况，重点看两个东西：一是数据模型有哪些表、关系是什么样的，二是认证流程是怎么走的，从登录到鉴权完整串一遍。"

注意：使用 SKILL.md 中定义的默认输出路径（`change-impact/_project-map.md`），不要指定自定义子目录。这样 pf_validate.py 才能在 `change-impact/_project-map/facts/` 找到 facts 文件。

---

## 任务 2（B1）— impact 分析操作日志加响应耗时

先 Read `skills/impact/SKILL.md`，然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/B1/`

用户原话："我想给系统的操作日志加一个响应耗时记录功能。每次接口请求都要记录从进入到返回花了多少毫秒，然后在操作日志列表页面能看到这个耗时。"

---

## 任务 3（B2）— impact 分析密码加密方案变更

先 Read `skills/impact/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact`，处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/B2/`

用户原话："我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。"

---

## 任务 4（B3）— impact-pro 分析 Prisma 用户加手机号

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`test-projects/prisma-express-ts`
输出到：`test-projects/prisma-express-ts/change-impact/B3/`

用户原话："我想给用户加一个手机号字段。注册的时候可以选填，但如果填了必须是中国手机号格式（1开头的11位数字），而且手机号要唯一不能重复。"

---

## 归档步骤

全部 4 个任务完成后，将产出归档到模型专属目录：

```bash
# prisma-express-ts（B6 + B3）
mkdir -p test-projects/prisma-express-ts/change-impact/blind-v4-sensenova-6.7-flash-lite/B6/
mv test-projects/prisma-express-ts/change-impact/_project-map.md test-projects/prisma-express-ts/change-impact/blind-v4-sensenova-6.7-flash-lite/B6/
mv test-projects/prisma-express-ts/change-impact/_project-map/ test-projects/prisma-express-ts/change-impact/blind-v4-sensenova-6.7-flash-lite/B6/
mv test-projects/prisma-express-ts/change-impact/B3/ test-projects/prisma-express-ts/change-impact/blind-v4-sensenova-6.7-flash-lite/B3/

# ruoyi-vue（B1 + B2）
mkdir -p test-projects/ruoyi-vue/change-impact/blind-v4-sensenova-6.7-flash-lite/
mv test-projects/ruoyi-vue/change-impact/B1/ test-projects/ruoyi-vue/change-impact/blind-v4-sensenova-6.7-flash-lite/B1/
mv test-projects/ruoyi-vue/change-impact/B2/ test-projects/ruoyi-vue/change-impact/blind-v4-sensenova-6.7-flash-lite/B2/
```

归档完成后，列出所有 `blind-v4-sensenova-6.7-flash-lite/` 目录的文件清单作为总结。
