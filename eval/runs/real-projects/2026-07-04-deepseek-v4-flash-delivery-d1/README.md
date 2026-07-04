# D1-java-pathfinder-map · 交付评测运行记录

## 基本信息

| 字段 | 内容 |
|------|------|
| 场景 ID | D1-java-pathfinder-map |
| Case ID | java-ruoyi-pathfinder |
| 复杂度 | M |
| Stage | pathfinder-map |
| Fixture mode | read-only-original |
| Runner | deepseek-v4-flash (DeepSeek V4 Flash) |
| Runner surface | claude-code-cli (subagent inside Claude Code) |
| 运行日期 | 2026-07-04 |

## Fixture 信息

| 字段 | 内容 |
|------|------|
| Fixture 路径 | `E:\agent\real-project-fixtures\java-ruoyi` |
| HEAD commit | `0d42679bc25576286bf34a156002716ed7de5739` (独立 Git 仓库) |
| 项目版本 | RuoYi v4.8.3 |
| 项目规模 | 693 文件 (285 Java, 148 HTML, 90 JS) |

## pf_validate.py 结果

**最终结果：PASS**

```
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

**迭代修复记录**：首次运行时 V5 报 4 个 FAIL（Mermaid 实线节点 DSP/SVC/FMW/CTRL 未在正文提及）。在架构图和主流程前补充节点说明后，重跑全部通过，无需其他修复。

## git diff 摘要

```
$ git diff --stat
（无输出——change-impact/ 目录为 untracked，未在 git 索引中）
```

源码文件无任何修改。唯一写入文件：
- `change-impact/_project-map.md`（目标产出文件，新文件）
- `change-impact/_project-map/facts/scan.json`（fact 文件，已有但已覆盖）
- `change-impact/_project-map/facts/git.json`（fact 文件，已有但已覆盖）

## 执行记录

| 步骤 | 状态 | 说明 |
|------|------|------|
| Phase 0: 聚焦 | ✅ | 用户 prompt 已明确关注重点 |
| Phase 1: 体量测量 | ✅ | 693 文件，中仓 |
| Phase 1.5: Facts | ✅ | pf_scan.py + pf_git.py 运行成功 |
| Phase 2: 并行专探 | ✅ | 整模块串行扫描：读 pom.xml、Controller、Entity、SQL、配置、Shiro、模板 |
| Phase 3: 深度填充 | ✅ | 15 节全部填充，含权限自检、主流程 trace、风险识别 |
| Phase 4: Script Gate | ✅ | pf_validate 全部 10 项通过 |
| Phase 4: 写入 | ✅ | `change-impact/_project-map.md` 已写入 |

## 最终判定

**GATE-RECOVERED**

说明：首次验证 V5 失败后被 pf_validate 门禁拦住，按照 V5 规则修复（补充 Mermaid 节点在正文中的提及）后重跑通过。门禁有效拦截了不完整的输出。

## case 对照

### success_target

| 要求 | 状态 | 证据 |
|------|------|------|
| 产出能指导用户模块变更的项目地图 | ✅ | 15 节完整覆盖 |
| 用户、角色、菜单、权限、SQL、Thymeleaf、导出链路都有证据 | ✅ | 全部【已核实】标注 |
| 默认口令和连接串只写键名和路径，不写明文值 | ✅ | V2 检查通过 |

### failure_signals

| 红线 | 状态 | 证据 |
|------|------|------|
| 只复述目录名，没有核心链路 | ✅ 未命中 | 有主流程 trace（11 步）、认证-鉴权自检 |
| 把 remark 判断成只属于 sys_user | ✅ 未命中 | 明确标注 remark 在 BaseEntity，跨实体共享 |
| 凭证或默认弱口令明文进入地图 | ✅ 未命中 | V2 检查 + 风险区域标注使用 `***` |
