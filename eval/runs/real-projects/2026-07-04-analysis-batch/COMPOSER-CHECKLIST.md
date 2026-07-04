# Composer 2.5 Fast 批次操作清单

> 准备脚本跑完后，按顺序开 Composer 会话，每个场景贴对应 prompt 即可。

## 第 0 步：一键准备 fixture

```powershell
cd E:\agent\blue-skillhub
.\eval\runs\real-projects\2026-07-04-analysis-batch\prep-composer-batch.ps1
```

## 第 1~8 步：逐个跑

每个场景：Cursor 里开新 Composer 2.5 Fast 会话 → 工作目录设为 fixture 路径 → 贴 prompt → 跑完告诉我验分。

---

### ① D8 — light 判档（S 级）

**工作目录：** `E:\agent\real-project-fixtures\node-realworld-prisma`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

把登录失败时返回的错误提示文案改得更清楚。先只做影响分析，判断 light/full，并说明要查哪些文件。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d8\README.md
```

---

### ② D9 — monorepo 字段变更（L 级）

**工作目录：** `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d9-composer`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

给用户资料新增 organization 字段，后端存储和返回，前端注册/资料页可填写，shared type 也要同步。先不要写代码，只做完整影响分析。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d9\README.md
```

---

### ③ D11 — RuoYi 新增字段（L 级）

**工作目录：** `E:\agent\real-project-fixtures\java-ruoyi`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

给系统用户新增一个"外部工号 external_id"字段，要求新增/编辑能维护，列表能展示，导出也带上。先不要写代码，只做完整影响分析。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d11\README.md
```

---

### ④ D12 — monorepo pathfinder（M 级，无 Git）

**工作目录：** `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\pathfinder\SKILL.md 里的流程帮我摸底。

我准备改这个 full-stack-starter-kit。请先在仓库根目录只读生成项目地图，然后在删除 .git 的副本里再跑一次，重点关注 workspace 边界、shared types、API、Prisma、前端，以及无 Git 时哪些信息必须降级。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d12\README.md
```

---

### ⑤ D13 — RuoYi 权限分析（M 级）

**工作目录：** `E:\agent\real-project-fixtures\java-ruoyi`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

现在所有用户都能导出用户列表，需要改成只有管理员角色才能导出。先不要写代码，只做完整影响分析。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d13\README.md
```

---

### ⑥ D15 — tags 功能删除（L 级）

**工作目录：** `E:\agent\real-project-fixtures\node-realworld-prisma`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

tags 功能没人用了，把它整个删掉。先不要写代码，只做完整影响分析。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d15\README.md
```

---

### ⑦ D16 — 配置变量改名（M 级）

**工作目录：** `E:\agent\real-project-fixtures\python-fastapi-template`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

环境变量 PROJECT_NAME 改成 APP_NAME，项目里用到的地方都改掉。先不要写代码，只做完整影响分析。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d16\README.md
```

---

### ⑧ D17 — lazy-trap（M 级）

**工作目录：** `E:\agent\real-project-fixtures\python-fastapi-template`

```
我刚接手这个项目，用 E:\agent\blue-skillhub\skills\impact\SKILL.md 里的流程帮我分析。

item 的 title 最大长度从 50 改成 100 就行，快速改一下。

分析完把结果写到 E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-composer-25fast-delivery-d17\README.md
```

---

## 跑完后

告诉我哪些跑完了，我这边逐个验分、归档、更新 delivery-results.json。
