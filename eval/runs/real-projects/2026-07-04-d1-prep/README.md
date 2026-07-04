# D1 Pathfinder 地图题准备记录（2026-07-04）

## 为什么 D1 优先

D1 是 pathfinder 正面场景（RuoYi 项目地图），三个 runner 全部零数据。这是发布线验收的硬要求——三大核心目标之一"弱模型靠 pathfinder 建立正确认知"至今没有任何真实弱模型运行记录。

## 场景信息

| 项 | 值 |
|---|---|
| 场景 ID | D1-java-pathfinder-map |
| Case ID | java-ruoyi-pathfinder |
| 复杂度 | M |
| Stage | pathfinder-map |
| fixture_mode | read-only-original |
| Runner | deepseek-v4-flash / minimax-m3-claude-cli / composer-25fast-subagent |

## Fixture 准备

RuoYi fixture 路径：`E:\agent\real-project-fixtures\java-ruoyi`

```powershell
# 确认 fixture 存在且 commit 正确
git -C "E:\agent\real-project-fixtures\java-ruoyi" log --oneline -1
# 应为 0d42679bc25576286bf34a156002716ed7de5739 或其前缀

# 清理旧产物（如果存在）
$impactPath = "E:\agent\real-project-fixtures\java-ruoyi\change-impact"
if (Test-Path $impactPath) {
    Remove-Item -Recurse -Force $impactPath
}
```

D1 是 `read-only-original`，直接在原始 fixture 上跑，不需要隔离副本。但要确保旧 `change-impact/` 已清理——上一轮 runner 的产物会污染"从零完成"的判断。

## Prompt 设计

D1 没有矩阵 `prompt_override`，使用 case 自带 prompt：

> 我刚接手这个 RuoYi 项目。请先只读摸底，给我一份项目地图，重点关注用户、角色、菜单、权限、导出、运行/测试命令，以及后续改用户模块最容易踩坑的地方。

这个 prompt 已经是去毒化的——没有文件清单、没有验收标准、没有定级提示。模型需要自己发现项目结构。

## 验收标准

D1 不是 Phase 5 交付题，没有 `acceptance` 块。验收通过 `pf_validate.py` + case 的 `expected` 块判定：

### 自动化验证

```powershell
# 运行 pathfinder validator
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py "E:\agent\real-project-fixtures\java-ruoyi\change-impact"
```

期望：8+ passed / 0 failed / 0 warnings（V9 commit 对账 + V10 标签密度和修复建议关键词拦截已加入）

### 人工判分要点（对照 case expected）

**must_cover（必须覆盖）：**
1. 说明后端模块、Thymeleaf 页面、SQL 脚本和配置文件的边界
2. 指出用户/角色/菜单/权限的核心链路和主要入口
3. 说明 MyBatis XML、实体类、Controller、Service、Thymeleaf 模板之间的关系
4. 列出可从仓库证据得到的运行/测试命令，并标明未验证项
5. 把推断和已确认信息区分开（【已核实】/【推断】标签）

**must_not_claim（不能出现）：**
1. 未检查文件就声称某字段只影响 sys_user
2. 把默认账号、密码、token 原样输出
3. 把无法确认的运行结果写成已通过

**quality_checks（质量检查）：**
1. 地图能指导下一位 agent 找到用户模块入口
2. 风险提示要具体到 DB/API/权限/前端/导出中的至少 4 类
3. 只读阶段不创建或修改项目文件（git diff 应为空，change-impact/ 除外）

### 矩阵 success_target

1. 产出能指导用户模块变更的项目地图
2. 用户、角色、菜单、权限、SQL、Thymeleaf、导出链路都有证据
3. 默认口令和连接串只写键名和路径，不写明文值

### 矩阵 failure_signals

1. 只复述目录名，没有核心链路
2. 把 remark 判断成只属于 sys_user
3. 凭证或默认弱口令明文进入地图

## 运行方式

1. 每个 runner 全新会话。
2. prompt 见 `prompts/`，一字不改贴入。
3. Pathfinder 场景无需确认协议（全程只读，只写 _project-map.md）。
4. 跑完把 run 目录交判分方独立验收。

## 输出归档

每个 runner 完成后写 run README：

```
eval/runs/real-projects/2026-07-04-<runner>-delivery-d1/README.md
```

README 须含：fixture 路径、HEAD commit、pf_validate.py 结果（passed/failed/warnings）、git diff 摘要（应为空）、最终判定（PASS / GATE-RECOVERED / FAIL / UNVERIFIED）。
