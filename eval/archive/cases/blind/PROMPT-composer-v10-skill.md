# Composer 2.5 盲测 v10 Prompt — 有 skill 组 + 人工交互

> 复制下面整段内容发给 Composer 2.5 执行。
> 本 prompt 是「有 skill」实验组：先 Read impact-pro 的 SKILL.md，走完整 Phase 流程。
> v10 使用 v4.1 改进后的最新 SKILL.md（v4.0 全部改进 + 多轮触发条件 + 链路追踪发现回流 Phase 3）。
> 本 cell 使用独立测试项目副本。
> **v10 核心验证：v4.1 多轮触发条件 + 链路追踪发现回流 Phase 3 是否生效。**

---

你接下来要完成 1 个测试任务。使用 impact-pro skill。

**测试项目路径**（本 cell 专属副本）：
- Prisma/Express 项目：`eval/runs/blind-2026-06-25-v10/cell-C2/test-projects/prisma-express-ts`

**Skill 文件路径**（共享，只读）：
- impact-pro：`skills/impact-pro/SKILL.md`

**输出路径规则**：
- 输出到项目目录下的 `change-impact/B3/`（用 case-id 作为需求名称）

**重要 — 模糊需求处理规则**：
本次测试的用户需求是**口语化、模糊的**，缺少具体数值、状态码、技术细节。当 skill 在 Phase 3 提出澄清问题时，你**必须暂停等待用户回答**。不要自行假设、不要自问自答。

具体规则：
1. 提出澄清问题后，**停止输出**，等待用户在下一条消息中回答
2. 收到用户回答后，将回答记录在 010-requirements.md §2.2 模糊点处理清单中，处理方式标注为"已提问 → 用户确认"
3. 如果用户回答模糊（如"你看着办"、"差不多就行"），你可以做出 `[假设]`，但必须标注为 `[假设]` 并说明"用户未明确，基于 XX 做出假设"
4. 如果用户回答的内容超出了你问的范围，也要记录下来
5. **不要因为"知道答案"就跳过提问**——如果需求中有模糊表述，必须提出澄清

**关键前置步骤**：任务开始前，你必须先 Read `skills/impact-pro/SKILL.md` 文件，确保你使用的是最新版协议。读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。不要使用缓存的旧版协议——以当前文件内容为准。

---

## 任务（B3'）— impact-pro 分析邮箱验证强制检查

先 Read `skills/impact-pro/SKILL.md`，然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-2026-06-25-v10/cell-C2/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-2026-06-25-v10/cell-C2/test-projects/prisma-express-ts/change-impact/B3/`

用户原话："注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧"

> 当 skill 进入 Phase 3 需要澄清时，提出你的问题然后**停下来等用户回答**。

---

## 归档步骤

任务完成后，将产出归档到模型专属目录：

```bash
CELL_DIR="eval/runs/blind-2026-06-25-v10/cell-C2"

# prisma-express-ts（B3）
mkdir -p "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v10-composer-skill/"
mv "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B3/" "$CELL_DIR/test-projects/prisma-express-ts/change-impact/v10-composer-skill/B3/"
```

归档完成后，列出 `v10-composer-skill/` 目录的文件清单作为总结。
