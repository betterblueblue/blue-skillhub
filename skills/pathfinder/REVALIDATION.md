# Pathfinder 复验手册（给便宜模型/人执行）

> pathfinder 改动后,或要补栈覆盖/验证模型方差时,照本手册复验。目标:让执行者(可以是便宜模型)按客观清单跑,产出可抽查的证据,而非散文感想。impact-pro 的 profile 生产复验见 [../impact-pro/PRODUCTION-REVALIDATION.md](../impact-pro/PRODUCTION-REVALIDATION.md);impact 的见 [../impact/REVALIDATION.md](../impact/REVALIDATION.md)。

## 1. 三层复验(从便宜到贵)

| 层 | 跑什么 | 命令 | 谁能跑 |
|---|---|---|---|
| L0 静态自洽 | 铁律存在、引用完整、fixture 锁定、共享契约 | `bash skills/pathfinder/tests/run.sh` | 任意模型/CI(免费) |
| L1 行为契约 | 3 case(P1 go-admin / P2 ruoyi-vue / P3D 降级)subagent 跑 + 判分 | `bash eval/run-l1.sh pathfinder` + 人工/评委按 rubric 打分 | subagent(便宜模型可跑)+ 判分 |
| 控制变量 | 同 skill 不同 runner_model 跑,隔离模型方差 | 见 §3 | 任意模型(记录 runner_model) |

## 2. L0 复验清单(客观,便宜模型直接填)

跑 `bash skills/pathfinder/tests/run.sh`,填:
```
L0 PASS 计数: ___(应 >0;若 0/0 = run.sh subshell bug 回归)
L0 FAIL 计数: ___(应 0)
fixture 都在(test-projects/{ruoyi-vue,go-admin,...}): ✓/✗
共享契约(信任标签/凭证脱敏/仓内文本/唯一写入)在 SKILL.md 铁律区: ✓/✗
```
**判定**:PASS>0 且 FAIL=0 → L0 过。FAIL>0 → 贴失败项,停。

## 3. L1 + 控制变量复验(核心)

### 3.1 跑 L1
对 P1/P2/P3D 各起 subagent 跑 pathfinder,产 `_project-map.md`,评委按 `docs/skill-eval/rubric-pathfinder.md` 打分,写评分卡到 `eval/runs/<date>-pathfinder@<commit>/`(schema 见 `eval/schemas/scorecard-schema.json`,**必填 runner_model**)。

### 3.2 判分清单(评委/抽查用,逐 case 填)
```
case P_:
  契约 C1 证据不编造: PASS/FAIL  (抽 3-5 条【已核实】打开引用验真,行号对不对?)
  契约 C3 凭证脱敏:    PASS/FAIL  (application-druid.yml 等默认密码有没有明文写出?)
  sql/ 目录描述:       准确/事实错  (Glob 核实,有没有声称"空"但实际有文件?)
  盲区章节:            有/无        (显式列未深入区?)
  Mermaid 实线/虚线:   守纪律/乱画  (推断关系有没有用实线?)
  runner_model:        ___
  base_total:          ___
```

### 3.3 控制变量(回答"分数差是 skill 还是模型")
保持 runner_model 不变,只改 skill 版本,各 cell 跑 ≥2 次:
```
bash eval/scripts/analyze_control.py <scorecards_dir>
```
输出信号比 |Δ|/σ_内:≤3 → 模型方差;显著 → skill 效应。详见 `eval/runs/2026-06-14-pathfinder-control/`(正样本)。

**跨 run 比对前先看 runner_model 是否一致**——不一致或 unknown 不能归 skill(`eval/scripts/diff_baseline.py` 会预警)。

## 4. 栈覆盖复验(补未测栈)

`references/stack-detection.md` 映射表覆盖 10+ 生态,但**只有 Go / Java-Spring-MyBatis / generic Node 有 fixture**。补新栈时:
```
新栈 ___:
  stack-detection 识别正确?  ✓/✗  (探测到的栈名对不对)
  清单文件(glob)命中真实文件? ✓/✗  (贴命中清单)
  地图技术栈节准确?          ✓/✗
  降级路径(非Git/无清单)诚实? ✓/✗
```
新栈 fixture 加到 `tests/fixtures/` + `tests/scenarios/`。

## 5. 已知缺口(2026-06-14 评估)

- ✅ L0 计数失效已修(commit 1a04679)。
- ✅ V3 交接已实跑验证(T03,pass)。
- ✅ README 已补模型敏感性提示。
- ⏳ **栈覆盖**:7 个栈(.NET/Ruby/PHP/Rust/Dart/Python 等)无 fixture,stack-detection 对它们是推断非核实。
- ⚠ **模型敏感性**(固有不可消灭):弱模型下产出会塌方(历史 P2=61)。**复验务必记录 runner_model,弱模型产出需抽查【已核实】行号 + 凭证脱敏**。

## 6. 抽查约定(给人/贵模型)

便宜模型跑完 L1/控制变量后,**人抽查 2 件事**即可判断它有没有走过场:
1. 抽 3 条【已核实】证据,打开引用看行号对不对(便宜模型最易在这里偷懒)。
2. 看凭证节有没有明文默认值(弱模型易漏脱敏)。
这两条客观、秒判。其余维度看评分卡趋势即可。
