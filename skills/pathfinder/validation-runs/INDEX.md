# pathfinder 验证记录索引

> 本目录记录 `skills/pathfinder` 的真实运行验证。

## 当前结论

```text
pathfinder = 陌生项目全项目级只读认知地图,产出 change-impact/_project-map.md 供 impact 家族当 L1 导航。
```

边界：
- 100% 只读、只描述不开药方。
- 地图是导航图不是权威源:【推断】项 impact 接过去须重新取证。

2026-06-25 T04 完成 v4.1 L1 全量回归（runner: Composer 2.5, judge: GLM-5.2）：3 case 均分 100.0，0 P0 / 0 P1，契约全 PASS，`pf_validate.py` 均 6 PASS / 0 FAIL。基线 P1（P3D 信任契约头写父 commit）修复无回归。code graph MCP 降级为 Read/Grep/Glob 扫描，地图如实标注 `status: unavailable`，不影响质量。

## 验证记录

| 记录 | 目标 | 结论 |
|------|------|------|
| T01 | 首轮真实 /pathfinder 验证（go-admin + ruoyi-vue 正向、交接、降级、安全） | PASS（1 P1 + 2 P2） |
| T02 | 二轮验证：Mermaid 图 + P1(凭证脱敏)P2(Git 归属)修复确认 | PASS（0 P1 + 2 P2） |
| T03 | **V3 端到端交接实跑**(pathfinder→impact,RuoYi,opus-4-8) | **PASS(5/5 契约检查,handoff_value=high)**——关闭 T01/T02 遗留的"V3 未实跑"缺口 |
| T04 | v4.1 L1 全量回归（Composer 2.5） | **PASS**——3 case 均分 100.0，0 P0/P1，契约全 PASS，`pf_validate.py` 均 6 PASS/0 FAIL；基线 P1（P3D 信任契约头）修复无回归；code graph 降级处理正确 |

## 关键文件

| 文件 | 作用 |
|------|------|
| `../SKILL.md` | pathfinder 主流程和硬性规则 |
| `../README.md` | 用户入口和用法 |
| `../templates/project-map.md` | 认知地图模板 |
| `../references/handoff-contract.md` | 与 impact 协作约定 |
