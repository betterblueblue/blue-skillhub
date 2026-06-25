# Opus 4.6 盲测 v5 Prompt — 有 skill 组（C2）

> 复制下面整段内容发给 Opus 4.6 执行。
> 本 prompt 是「有 skill」实验组：每个任务前 Read 对应 skill 的 SKILL.md，走完整 Phase 流程。
> v5 使用优化完成后的最新 SKILL.md（E1-E4 + S1-S3 + Q1-Q18 实施后）。
> 本 cell 使用独立测试项目副本，可与其他 cell 并行执行。

---

你接下来要连续完成 4 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/pathfinder`、`/impact`、`/impact-pro`）。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/prisma-express-ts`
- RuoYi-Vue 项目：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/ruoyi-vue`

**Skill 文件路径**（共享，只读）：
- pathfinder：`skills/pathfinder/SKILL.md`
- impact：`skills/impact/SKILL.md`
- impact-pro：`skills/impact-pro/SKILL.md`

**输出路径规则**：
- 每个任务使用 skill 的默认输出路径，不指定自定义子目录
- pathfinder 输出到项目目录下的 `change-impact/_project-map.md`（SKILL.md 默认路径）
- impact/impact-pro 输出到项目目录下的 `change-impact/B1/`、`change-impact/B2/`、`change-impact/B3/`（用 case-id 作为需求名称）
- 所有任务完成后，统一归档到 `change-impact/v5-opus-skill/` 目录（见最后一步）

**重要**：每个任务请完整走完 skill 的流程（分析 → 提问 → 出文档），不要省略。如果 skill 要求确认，你在 prompt 里自行模拟用户回答"继续"即可，不要停下来等我确认。

**关键前置步骤**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。具体来说：
- pathfinder 任务前 Read `skills/pathfinder/SKILL.md`
- impact 任务前 Read `skills/impact/SKILL.md`
- impact-pro 任务前 Read `skills/impact-pro/SKILL.md`

读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。不要使用缓存的旧版协议——以当前文件内容为准。

---

## 任务 1（B6）— pathfinder 摸底 Prisma/Express 项目

先 Read `skills/pathfinder/SKILL.md`，然后运行 `/pathfinder`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/prisma-express-ts`

用户原话："帮我摸一下这个 Node 项目的整体情况，重点看两个东西：一是数据模型有哪些表、关系是什么样的，二是认证流程是怎么走的，从登录到鉴权完整串一遍。"

注意：使用 SKILL.md 中定义的默认输出路径（`change-impact/_project-map.md`），不要指定自定义子目录。这样 pf_validate.py 才能在 `change-impact/_project-map/facts/` 找到 facts 文件。

---

## 任务 2（B1）— impact 分析操作日志加响应耗时

先 Read `skills/impact/SKILL.md`，然后运行 `/impact`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/ruoyi-vue/change-impact/B1/`

用户原话："我想给系统的操作日志加一个响应耗时记录功能。每次接口请求都要记录从进入到返回花了多少毫秒，然后在操作日志列表页面能看到这个耗时。"

---

## 任务 3（B2）— impact 分析密码加密方案变更

先 Read `skills/impact/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/ruoyi-vue/change-impact/B2/`

用户原话："我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。"

---

## 任务 4（B3）— impact-pro 分析 Prisma 用户加手机号

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v5/cell-C2/test-projects/prisma-express-ts/change-impact/B3/`

用户原话："我想给用户加一个手机号字段。注册的时候可以选填，但如果填了必须是中国手机号格式（1开头的11位数字），而且手机号要唯一不能重复。"

---

## 归档步骤

全部 4 个任务完成后，将产出归档到模型专属目录：

```bash
CELL_DIR="eval/runs/blind-2026-06-25-v5/cell-C2"

# prisma-express-ts（B6 + B3）
mkdir -p "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v5-opus-skill/B6/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/_project-map.md" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v5-opus-skill/B6/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/_project-map/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v5-opus-skill/B6/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B3/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v5-opus-skill/B3/"

# ruoyi-vue（B1 + B2）
mkdir -p "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v5-opus-skill/"
mv "$CELL_DIR/test-projects/ruoyi-vue/change-impact/B1/" "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v5-opus-skill/B1/"
mv "$CELL_DIR/test-projects/ruoyi-vue/change-impact/B2/" "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v5-opus-skill/B2/"
```

归档完成后，列出所有 `v5-opus-skill/` 目录的文件清单作为总结。
