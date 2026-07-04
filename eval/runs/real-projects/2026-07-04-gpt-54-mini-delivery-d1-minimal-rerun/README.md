# D1 GPT-5.4-mini Minimal Rerun

## 基本信息

| 项 | 值 |
|---|---|
| 场景 | D1-java-pathfinder-map |
| Runner | gpt-54-mini-subagent / GPT-5.4-mini |
| Fixture | `E:\agent\real-project-fixtures\java-ruoyi-d1-gpt54mini-minimal-20260704` |
| Prompt | `eval/runs/real-projects/2026-07-04-d1-gpt54mini-minimal-rerun/prompts/d1-gpt-54-mini-subagent.txt` |
| 产物 | `change-impact/_project-map.md` + `change-impact/_project-map/facts/{scan.json,git.json}` |
| 判定 | PASS |

## Prompt 口径

本轮按 GLM5.2 口径，只给 runner 两段式 prompt：

```text
[评测环境]
工作目录：E:\agent\real-project-fixtures\java-ruoyi-d1-gpt54mini-minimal-20260704
Skill：E:\agent\blue-skillhub\skills\pathfinder\SKILL.md
输出归档：E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d1-minimal-rerun\README.md

---

[用户输入]
我刚接手这个 RuoYi 项目。请先只读摸底，给我一份项目地图，重点关注用户、角色、菜单、权限、导出、运行/测试命令，以及后续改用户模块最容易踩坑的地方。
```

没有验收答案、validator 命令、Step 规则、评分口径或旧产物路径。

## 独立验分

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py `
  E:\agent\real-project-fixtures\java-ruoyi-d1-gpt54mini-minimal-20260704\change-impact\_project-map.md `
  --repo-root E:\agent\real-project-fixtures\java-ruoyi-d1-gpt54mini-minimal-20260704
```

结果：

```text
PASS: V1: line-number claims verified
PASS: V2: no credential leakage detected
PASS: V3: SVG safety check passed
PASS: V4: uncovered section has entries
PASS: V5: Mermaid solid-arrow consistency passed
PASS: V6: facts file content validated
PASS: V7: section [14] code style observation exists
PASS: V8: evidence path format sane
PASS: V9: map header commit matches git.json
PASS: V10: credibility tags sufficient
SUMMARY: 10 passed, 0 failed, 0 warnings
```

`git status --short --branch --untracked-files=all`：

```text
## HEAD (no branch)
?? change-impact/_project-map.md
?? change-impact/_project-map/facts/git.json
?? change-impact/_project-map/facts/scan.json
```

## 关键证据

- Git facts 正确：`is_git_repo=true`、`is_independent_repo=true`、`toplevel` 指向本轮 fixture，未读父仓库。
- 地图覆盖用户、角色、菜单、权限、SQL、Thymeleaf、导出导入和运行脚本。
- 凭证扫描无 WARN；默认账号只记来源路径，没有写明文值。
- 没有源码、测试、配置 diff；只新增 `change-impact/` 下 Pathfinder 产物。

## 结论

GPT-5.4-mini 子代理在 D1 Pathfinder 只读场景下可以按最小 prompt 完成产物，且 validator 首次通过。这个结果只证明只读项目地图场景可用；不改变 D20 已暴露的 Phase 5 `step_protocol_escape` 结论。
