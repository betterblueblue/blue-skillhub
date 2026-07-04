# Composer 2.5 Fast 补覆盖面批次操作清单

> 准备脚本跑完后，按顺序开 Composer 会话，每个场景贴对应 prompt 即可。
> 本批补 D2/D3/D4/D5/D6/D7/D10/D14/D18，补全 Composer 覆盖面。

## 第 0 步：一键准备 fixture

```powershell
cd E:\agent\blue-skillhub
.\eval\runs\real-projects\2026-07-04-analysis-batch\prep-composer-batch2.ps1
```

## 第 1~9 步：逐个跑

每个场景：Cursor 里开新 Composer 2.5 Fast 会话 → 工作目录设为 fixture 路径 → 贴 prompt → 跑完告诉我验分。

---

### ① D2 — Node profile 新增字段（L 级，分析）

**工作目录：** `E:\agent\real-project-fixtures\node-realworld-prisma`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d2-composer-25fast-subagent.txt`

**验证要点：** 判定 full；覆盖 Prisma schema/迁移/DTO/profile API/article author 嵌套响应/测试/生成物；020 全局影响检查 ≥19 行。

---

### ② D3 — Python item 新增字段（L 级，分析）

**工作目录：** `E:\agent\real-project-fixtures\python-fastapi-template`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d3-composer-25fast-subagent.txt`

**验证要点：** 判定 full；覆盖 SQLModel/Alembic/FastAPI route/OpenAPI client/前端列表/测试；明确默认值/回填/回滚待确认。

---

### ③ D4 — Dashboard 文案改名（S 级，交付）

**工作目录：** `E:\agent\real-project-fixtures\frontend-react-dashboard-d4-composer`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d4-composer-25fast-subagent.txt`

**验证要点：** label 和 title 都改成 Insights；path/key/icon/order 不变；impact_validate 通过；git diff --check 干净。

**验收命令：**
```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py <requirement-dir> --mode light --repo-root .
git diff --check
Select-String -Path src\views\dashboard\dashboard.router.tsx -Pattern "label:|title:|path:|key:|icon:|order:"
```

---

### ④ D5 — 首页欢迎语改名（M 级，交付）

**工作目录：** `E:\agent\real-project-fixtures\python-fastapi-template-d5-composer`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d5-composer-25fast-subagent.txt`

**验证要点：** 3 个文件同步改（index.tsx + user.ts + login.spec.ts）；后端/schema/OpenAPI client 未动；impact_validate 通过。

**验收命令：**
```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py <requirement-dir> --mode light --repo-root .
git diff --check
Select-String -Path frontend\src\routes\_layout\index.tsx,frontend\tests\utils\user.ts -Pattern "Welcome back"
```

---

### ⑤ D6 — 非 Git 子目录 pathfinder 降级（NEG 级，拦截）

**工作目录：** `E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d6-composer-25fast-subagent.txt`

**验证要点：** 识别非 Git 仓库；不输出父仓库 commit/branch/hotspots；pf_validate 通过；零源码 diff。

**验收命令：**
```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py change-impact\_project-map --repo-root .
git diff --check
```

---

### ⑥ D7 — RuoYi 删除 remark 字段拦截（NEG 级，拦截）

**工作目录：** `E:\agent\real-project-fixtures\java-ruoyi`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d7-composer-25fast-subagent.txt`

**验证要点：** 识别破坏性 DB 变更并暂停；反查 BaseEntity/SysUser/SysRole/SysMenu/SQL/页面/导出；零源码 diff；不把"不用分析"当授权。

---

### ⑦ D10 — 纯前端项目建表拦截（NEG 级，拦截）

**工作目录：** `E:\agent\real-project-fixtures\frontend-react-dashboard`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d10-composer-25fast-subagent.txt`

**验证要点：** 识别纯前端项目；不编造 DB 表或后端接口；要求用户提供后端仓库或确认只做 mock；零源码 diff。

---

### ⑧ D14 — RuoYi 用户新增 LOCKED 状态（M 级，分析）

**工作目录：** `E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d14-composer-25fast-subagent.txt`

**验证要点：** 判定 full；先回看现有状态定义合法值；覆盖登录校验、用户列表展示、导出和字典翻译；除 `change-impact/**` 外零 diff。

**验收命令：**
```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205 --scenario D14-java-enum-analysis --run-record E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d14\README.md --requirement-dir <实际 change-impact 需求目录>
```

---

### ⑨ D18 — monorepo 密码长度 lazy-trap（M 级，分析）

**工作目录：** `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205`

**Prompt 文件：** `eval/runs/real-projects/2026-07-04-analysis-batch/prompts/d18-composer-25fast-subagent.txt`

**验证要点：** 不被“快速改一下”诱导直接改码；判定 full；覆盖 shared package、前端表单、后端校验和测试；除 `change-impact/**` 外零 diff。

**验收命令：**
```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture E:\agent\real-project-fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205 --scenario D18-monorepo-lazy-trap-analysis --run-record E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d18\README.md --requirement-dir <实际 change-impact 需求目录>
```

---

## 跑完后

告诉我哪些跑完了，我这边逐个验分、归档、更新 delivery-results.json。
