# Pathfinder 迭代历史

> 本文件是 pathfinder skill 的版本历史。README 只放当前版本和入口，详细变更在这里。
>
> 版本方案：pathfinder 在 2026-07-26 发布线达标时首次定版为 v1.0；此前的演进按日期记录里程碑（当时未定版本号）。

## v1.0（2026-07-26，首个发布基线）

- release-gate 五条硬标准全部达标，进入可发布状态（判定依据见 `docs/skill-eval/release-gate.md`）
- references 最后抽查修复 7 条文档同步缺口：review-checklist 自动检查表 V1-V8 → V1-V11（含期望输出与打分卡）、SKILL.md 与 phase-3-depth-fill 可选集 3 节 → 7 节、模板头注释与【14】可跳过口径统一、V7 概述补"合理跳过降 WARN"分支、facts-schema 补 `file_count_source`/`physical_file_count`、stack-detection 补 `Pipfile`/`mix.exs`、review-checklist H9 对齐模板【8】实际行
- README 面向外部工程师重排动线（快速开始前置、触发方式收拢）
- 基线能力：校验器 `pf_validate.py` V1-V11、模板核心 15 节 + 可选 7 节、facts 脚本 `pf_scan.py`/`pf_git.py`、8 个 references、L0 测试 43 项

## 定版前里程碑（2026-06 ~ 2026-07）

- **2026-07-12**：改进反馈流程简化（运行发现可改进问题时，收尾一句话询问是否记录）
- **2026-07-10**：核心校验门禁加固
- **2026-07-05**：新增 V11——facts/地图记录的 HEAD 必须与当前仓库一致，过期地图强制重跑 facts 后刷新
- **2026-07-04**：加固发布——新增 V9（地图头部 commit 与 git.json 一致）、V10（可信度标签密度不足 FAIL + 疑似修复建议词 WARN）
- **2026-07-01 ~ 07-03**：三轮外部评审修复（8 个设计/代码问题、5 个问题、8 个 bug）；凭证脱敏改为逐命中处理；V8 证据路径格式检查落地；facts 与退出码测试补齐
- **2026-06-28 ~ 06-29**：两轮 bug 修复（14 个 + 5 个）；README 结构重构，迭代流水账迁出
- **2026-06-17**：模板可选集扩至 7 节（新增 CI/CD 流水线、代码所有权 CODEOWNERS、测试覆盖率、性能基线）
- **2026-06-14**：首个评测基线（P1/P2/P3D 三用例平均 97.7/100）；控制变量测试暴露执行模型方差（同版本 99.5 vs 61），推动后续脚本门禁建设
- **2026-06-13**：初版设计与创建，设计记录见 `docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md`
