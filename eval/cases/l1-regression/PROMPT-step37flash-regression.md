# Step 3.7 Flash L1 回归 Prompt

> 复制下面整段内容发给 Step 3.7 Flash 执行。
> 用途：Skill 协议改进后的 L1 定向回归，验证 P1-A/P1-B（pathfinder）、I1-A/I2-A（impact）、IP1-A（impact-pro）三条改进链路没破坏现有能力。

---

你接下来要连续完成 3 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/pathfinder`、`/impact`、`/impact-pro`）。

**输出目录规则**：所有产出写到 `test-projects/<项目>/change-impact/l1-regression-step37flash/<case-id>/` 下，带上模型名方便区分。

**重要**：每个任务请完整走完 skill 的流程（分析 → 提问 → 出文档），不要省略。如果 skill 要求确认，你在 prompt 里自行模拟用户回答"继续"即可，不要停下来等我确认。

---

## 任务 1（P1）— pathfinder 摸底 go-admin 项目

先运行 `/pathfinder`，然后处理以下需求：

项目路径：`test-projects/go-admin`
输出到：`test-projects/go-admin/change-impact/l1-regression-step37flash/P1/`

用户原话："帮我看看 go-admin 这个项目的大致结构和关键模块，重点关注数据模型和 API 路由"

---

## 任务 2（R1）— impact 分析删 sys_user.remark 字段

运行 `/impact`，然后处理以下需求：

项目路径：`test-projects/ruoyi-vue`
输出到：`test-projects/ruoyi-vue/change-impact/l1-regression-step37flash/R1/`

用户原话："我要把 sys_user 表的 remark 字段删了"

---

## 任务 3（F1）— impact-pro 分析 FastAPI 商品库存预警阈值

运行 `/impact-pro`，然后处理以下需求：

项目路径：`test-projects/full-stack-fastapi-template`
输出到：`test-projects/full-stack-fastapi-template/change-impact/l1-regression-step37flash/F1/`

用户原话："A product manager says: items should have a warning threshold. When stock falls below it, the item detail API should return low_stock: true. Do not modify code. Produce an impact analysis and implementation plan."

---

全部完成后，在 `test-projects/` 下列出所有 `l1-regression-step37flash/` 目录的文件清单作为总结。
