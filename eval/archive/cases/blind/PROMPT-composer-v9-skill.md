# Composer 2.5 盲测 v9 Prompt — 有 skill 组（C2）+ 人工交互

> 复制下面整段内容发给 Composer 2.5 执行。
> 本 prompt 是「有 skill」实验组：每个任务前 Read 对应 skill 的 SKILL.md，走完整 Phase 流程。
> v9 使用 v4.0 改进后的最新 SKILL.md（v3.9 全部改进 + 配置依赖链路追踪 + light 配置化提示）。
> 本 cell 使用独立测试项目副本。
> **v9 核心变化：澄清问题由真实开发者回答，agent 不自问自答。模拟完全真实的生产场景。**

---

你接下来要连续完成 3 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/impact`、`/impact-pro`）。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/prisma-express-ts`
- RuoYi-Vue 项目：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/ruoyi-vue`

**Skill 文件路径**（共享，只读）：
- impact：`skills/impact/SKILL.md`
- impact-pro：`skills/impact-pro/SKILL.md`

**输出路径规则**：
- 每个任务使用 skill 的默认输出路径，不指定自定义子目录
- impact/impact-pro 输出到项目目录下的 `change-impact/B1/`、`change-impact/B2/`、`change-impact/B3/`（用 case-id 作为需求名称）
- 所有任务完成后，统一归档到 `change-impact/v9-composer-skill/` 目录（见最后一步）

**重要 — 模糊需求处理规则（v9 核心变化）**：
本次测试的用户需求是**口语化、模糊的**，缺少具体数值、状态码、技术细节。当 skill 在 Phase 3 提出澄清问题时，你**必须暂停等待用户回答**。不要自行假设、不要自问自答。

具体规则：
1. 提出澄清问题后，**停止输出**，等待用户在下一条消息中回答
2. 收到用户回答后，将回答记录在 010-requirements.md §2.2 模糊点处理清单中，处理方式标注为"已提问 → 用户确认"
3. 如果用户回答模糊（如"你看着办"、"差不多就行"），你可以做出 `[假设]`，但必须标注为 `[假设]` 并说明"用户未明确，基于 XX 做出假设"
4. 如果用户回答的内容超出了你问的范围，也要记录下来
5. **不要因为"知道答案"就跳过提问**——如果需求中有模糊表述，必须提出澄清

**关键前置步骤**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。具体来说：
- impact 任务前 Read `skills/impact/SKILL.md`
- impact-pro 任务前 Read `skills/impact-pro/SKILL.md`

读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。不要使用缓存的旧版协议——以当前文件内容为准。

---

## 任务 1（B1'）— impact 分析并发登录限制

先 Read `skills/impact/SKILL.md`，然后运行 `/impact`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/ruoyi-vue/change-impact/B1/`

用户原话："我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录"

> 当 skill 进入 Phase 3 需要澄清时，提出你的问题然后**停下来等用户回答**。

---

## 任务 2（B2'）— impact-pro 分析请求体大小限制

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/prisma-express-ts/change-impact/B2/`

用户原话："API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

> 当 skill 进入 Phase 3 需要澄清时，提出你的问题然后**停下来等用户回答**。

---

## 任务 3（B3'）— impact-pro 分析邮箱验证强制检查

先 Read `skills/impact-pro/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v9/cell-C2/test-projects/prisma-express-ts/change-impact/B3/`

用户原话："注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

> 当 skill 进入 Phase 3 需要澄清时，提出你的问题然后**停下来等用户回答**。

---

## 归档步骤

全部 3 个任务完成后，将产出归档到模型专属目录：

```bash
CELL_DIR="eval/runs/blind-2026-06-25-v9/cell-C2"

# ruoyi-vue（B1）
mkdir -p "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v9-composer-skill/"
mv "$CELL_DIR/test-projects/ruoyi-vue/change-impact/B1/" "$CELL_DIR/test-projects/ruoyi-vue/change-impact/v9-composer-skill/B1/"

# prisma-express-ts（B2 + B3）
mkdir -p "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v9-composer-skill/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B2/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v9-composer-skill/B2/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B3/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v9-composer-skill/B3/"
```

归档完成后，列出所有 `v9-composer-skill/` 目录的文件清单作为总结。
