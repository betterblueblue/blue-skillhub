# 独立验收指令：intent 系列 Skill 链路改造

## 工作区

- 项目绝对路径：`e:\agent\blue-skillhub`
- 当前分支：`master`
- 验收基线：`bc6511b`（任务 A）→ `783d263`（任务 A2）→ `a11f12d`（任务 A3）→ `388d3fb`（文档修复）
- 验收目标：确认三个任务的所有改动都已正确落地，没有遗漏和残留。

## 任务概要

| 任务 | 提交 | 内容 |
|---|---|---|
| A | `bc6511b` | intent-anchor 加设计标准识别（Step 7）、术语标记（Step 8）、第 12/13 节、S6/S7、V10/V11 |
| A2 | `783d263` | intent-anchor 加验收路径（Step 9、第 14 节、S8、V12）；新建 intent-prd（8 项校验）和 intent-issues（7 项校验） |
| A3 | `a11f12d` | intent-anchor 加性能/安全要求（Step 10/11、第 15/16 节、S9/S10、V13/V14）；新建 intent-dev（4 项校验）和 intent-verify（6 项校验）；Stage Gate Check → 最终复核；`stage-gate-check.md` → `阶段核对表.md` |
| 修复 | `388d3fb` | SKILL.md 和 README.md 中 3 处 S1-S8 文本遗漏更新为 S1-S10 |

## 完整链路

```text
intent-anchor → INTENT.md（16 节：意图、能力、验收路径、设计标准、术语表、性能/安全要求）
    ↓ 强制输入
intent-prd → PRD.md（原生引用能力表和验收路径，Acceptance Criteria 用 Given/When/Then 结构）
    ↓ 强制输入
intent-issues → 工单文件（自动引用路径编号，自动检查覆盖）
    ↓ 强制输入
intent-dev → dev-record.md（TDD 循环开发，工单级 V0/V1/V2 验证）
    ↓ 强制输入
intent-verify → verify-record.md（全量回归 + 端到端 V3 验收 + 条件性验证 + 最终复核）
```

每个 Skill 的前置条件强制要求上游产物通过校验。Skill 之间不依赖交接 Prompt 串联，而是各自独立读取上游文件。约束传递通过 INTENT.md 的结构化字段（第 12-16 节）和校验器的交叉检查实现。

## 验收要求

1. 重新读取原始需求和后续确认，逐项列出验收项。
2. 查看当前 git status、实际 diff 和相关文件；改动已经提交时比较相关 commit 或基线与当前状态。不要直接采信上述任务概要。
3. 对修改过的函数、字段、接口、配置和公开行为反查调用方、引用方、注册点、生成物与测试；找不到引用时明确写"未找到"。
4. 检查是否存在漏改、误改、只改一半、无关改动，或者覆盖用户原有改动的情况。
5. 检查测试是否真正覆盖本次需求。能安全判断时，确认测试在旧错误仍存在时会失败；无法验证时如实说明。
6. 重新运行必要的验证命令，记录实际命令、退出码和关键结果。不要引用实现会话的结果代替复验。
7. 测试全部通过也不能直接判定完成；必须回到原始需求逐项核对。

## 验收项

### 一、intent-anchor（14 项校验 V1-V14）

#### 检查 1：校验器覆盖 V1-V14

```bash
cd e:\agent\blue-skillhub
python -c "import sys; sys.path.insert(0, 'skills/intent-anchor/scripts'); from intent_validate import validate; results = validate(open('skills/intent-anchor/tests/fixtures/valid-intent.md', encoding='utf-8').read()); print([r[0] for r in results]); assert len(results) == 14, f'Expected 14, got {len(results)}'; assert all(r[1] == 'PASS' for r in results), [r for r in results if r[1] != 'PASS']"
```

预期输出：`['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14']`，无异常。

#### 检查 2：REQUIRED_SECTIONS 包含 16 节

```bash
python -c "import sys; sys.path.insert(0, 'skills/intent-anchor/scripts'); from intent_validate import REQUIRED_SECTIONS; assert len(REQUIRED_SECTIONS) == 16, f'Expected 16, got {len(REQUIRED_SECTIONS)}'; print('16 sections:', [s.split('. ')[1] for s in REQUIRED_SECTIONS])"
```

预期：16 节，包含"性能要求"和"安全要求"。

#### 检查 3：SKILL.md Phase 2 有性能要求和安全要求的询问步骤

```bash
findstr /C:"询问性能要求" /C:"询问安全要求" skills\intent-anchor\SKILL.md
```

预期：找到 2 行，分别包含"询问性能要求"和"询问安全要求"。

#### 检查 4：SKILL.md 强制规则 #4 和 Phase 2.5 标题已更新为 S1-S10

```bash
findstr /C:"S1-S10" skills\intent-anchor\SKILL.md
```

预期：找到 2 行（强制规则 #4 和 Phase 2.5 标题）。

#### 检查 5：README.md 文件结构注释已更新为 S1-S10

```bash
findstr /C:"S1-S10" skills\intent-anchor\README.md
```

预期：找到至少 1 行（semantic-audit.md 注释）。

#### 检查 6：语义复核规则文件包含 S9 和 S10

```bash
findstr /C:"## S9" /C:"## S10" skills\intent-anchor\references\semantic-audit.md
```

预期：找到 2 行。

#### 检查 7：测试 fixture 包含第 15/16 节和 S9/S10

```bash
findstr /C:"## 15. 性能要求" /C:"## 16. 安全要求" /C:"### S9 性能要求" /C:"### S10 安全要求" skills\intent-anchor\tests\fixtures\valid-intent.md
```

预期：找到 4 行。

#### 检查 8：模板文件已重命名

```bash
dir skills\intent-anchor\templates\阶段核对表.md
```

预期：文件存在。

```bash
dir skills\intent-anchor\templates\stage-gate-check.md 2>&1
```

预期：文件不存在。

### 二、intent-dev（4 项校验 V1-V4）

#### 检查 9：SKILL.md 存在且描述正确

```bash
findstr /C:"name: intent-dev" skills\intent-dev\SKILL.md
```

预期：找到 1 行。

#### 检查 10：dev_validate.py 有 4 项检查

```bash
python -c "import sys; sys.path.insert(0, 'skills/intent-dev/scripts'); from dev_validate import validate; results = validate(open('skills/intent-dev/tests/fixtures/valid-dev-record.md', encoding='utf-8').read(), open('skills/intent-dev/tests/fixtures/valid-issues.md', encoding='utf-8').read()); assert len(results) == 4, f'Expected 4, got {len(results)}'; assert all(r[1] == 'PASS' for r in results), [r for r in results if r[1] != 'PASS']; print('4 checks all PASS:', [r[0] for r in results])"
```

预期：4 项全部 PASS。

#### 检查 11：dev-record 模板包含 TDD 过程段

```bash
findstr /C:"### TDD 过程" /C:"#### Red" /C:"#### Green" /C:"#### Refactor" skills\intent-dev\templates\dev-record.md
```

预期：找到 4 行。

#### 检查 12：验证等级 V0/V1/V2 在 SKILL.md 中定义

```bash
findstr /C:"V0" /C:"V1" /C:"V2" skills\intent-dev\SKILL.md
```

预期：找到包含验证等级表的行。

### 三、intent-verify（6 项校验 V1-V6）

#### 检查 13：SKILL.md 存在且 Phase 5 标题为"最终复核"

```bash
findstr /C:"Phase 5：最终复核" skills\intent-verify\SKILL.md
```

预期：找到 1 行。

#### 检查 14：verify_validate.py GATE_HEADING 为"最终复核"

```bash
python -c "import sys; sys.path.insert(0, 'skills/intent-verify/scripts'); from verify_validate import GATE_HEADING; assert GATE_HEADING == '## 最终复核', f'Got: {GATE_HEADING!r}'; print('GATE_HEADING =', GATE_HEADING)"
```

预期：`GATE_HEADING = ## 最终复核`。

#### 检查 15：verify_validate.py 有 6 项检查

```bash
python -c "import sys; sys.path.insert(0, 'skills/intent-verify/scripts'); from verify_validate import validate; results = validate(open('skills/intent-verify/tests/fixtures/valid-verify-record.md', encoding='utf-8').read()); assert len(results) == 6, f'Expected 6, got {len(results)}'; assert all(r[1] == 'PASS' for r in results), [r for r in results if r[1] != 'PASS']; print('6 checks all PASS:', [r[0] for r in results])"
```

预期：6 项全部 PASS。

#### 检查 16：verify-record 模板包含条件性验证段

```bash
findstr /C:"### 性能验证" /C:"### 安全验证" skills\intent-verify\templates\verify-record.md
```

预期：找到 2 行。

#### 检查 17：SKILL.md 不含"Stage Gate Check"

```bash
findstr /C:"Stage Gate Check" skills\intent-verify\SKILL.md 2>&1
```

预期：无输出（找不到）。

#### 检查 18：测试类名已从 TestStageGateCheck 改为 TestFinalReview

```bash
findstr /C:"TestFinalReview" /C:"TestStageGateCheck" skills\intent-verify\tests\test_verify_validate.py
```

预期：找到 `TestFinalReview`，找不到 `TestStageGateCheck`。

### 四、intent-issues（7 项校验 V1-V7）

#### 检查 19：issues_validate.py 有 7 项检查

```bash
python -c "import sys; sys.path.insert(0, 'skills/intent-issues/scripts'); from issues_validate import validate; intent = open('skills/intent-anchor/tests/fixtures/valid-intent.md', encoding='utf-8').read(); issues = open('skills/intent-issues/tests/fixtures/valid-issues.md', encoding='utf-8').read(); results = validate(issues, intent); assert len(results) == 7, f'Expected 7, got {len(results)}'; assert all(r[1] == 'PASS' for r in results), [r for r in results if r[1] != 'PASS']; print('7 checks all PASS:', [r[0] for r in results])"
```

预期：7 项全部 PASS。

#### 检查 20：V6 和 V7 检查存在

```bash
findstr /C:"V6" /C:"V7" skills\intent-issues\scripts\issues_validate.py
```

预期：找到 V6（设计标准传递检查）和 V7（术语表传递检查）。

### 五、全量测试

#### 检查 21：全量测试通过

```bash
cd e:\agent\blue-skillhub && python -m pytest skills/ -q
```

预期：`243 passed, 5 subtests passed`，退出码 0。

#### 检查 22：intent 系列单独测试通过

```bash
cd e:\agent\blue-skillhub && python -m pytest skills/intent-anchor/tests/ skills/intent-dev/tests/ skills/intent-verify/tests/ skills/intent-issues/tests/ -q
```

预期：`107 passed`，退出码 0。

各 skill 测试数量分布：
- intent-anchor：41 个测试
- intent-dev：16 个测试
- intent-verify：26 个测试
- intent-issues：24 个测试

### 六、残留检查

#### 检查 23：Skill 源码中不含"Stage Gate Check"

```bash
cd e:\agent\blue-skillhub && findstr /S /I "Stage Gate Check" skills\intent-verify\ skills\intent-dev\ skills\intent-anchor\templates\ skills\intent-anchor\references\ skills\intent-anchor\scripts\ skills\intent-anchor\SKILL.md skills\intent-anchor\README.md
```

预期：无输出。

说明：`skills/intent-anchor/INTENT.md` 中仍引用 `stage-gate-check.md`，这是 skillhub 项目自身的历史意图记录（不是模板），记录的是项目设计初期的决策，不改。

#### 检查 24：Skill 之间不依赖交接 Prompt 串联

逐个检查每个 SKILL.md 的最后一个 Phase：

- `intent-anchor/SKILL.md` Phase 4：给用户一段提示文本，指引用户使用 intent-prd / intent-issues。这是给用户看的导航，不是 Skill 间自动串联的 Prompt。
- `intent-prd/SKILL.md` Phase 4：交接指引用户使用 intent-issues。
- `intent-issues/SKILL.md` Phase 5：交接指引用户使用 intent-dev。
- `intent-dev/SKILL.md` Phase 3：交接指引用户使用 intent-verify。
- `intent-verify/SKILL.md` Phase 6：交接告知用户验收完成。

每个 Skill 的前置条件都是"必须存在通过校验的上游文件"，不依赖上游 Skill 的交接 Prompt 注入约束。约束传递通过 INTENT.md 的结构化字段（第 12-16 节）和校验器的交叉检查实现。

`intent-prd/SKILL.md` 中"不需要交接 prompt 注入约束"和 `intent-issues/README.md` 中"使用第三方 to-issues 时只能通过交接 prompt 注入"是在说明为什么自建 Skill 而不用第三方，不是在要求使用交接 Prompt。

### 七、文档修复记录

#### 检查 25：SKILL.md 和 README.md 中 S1-S8 已全部更新为 S1-S10

```bash
cd e:\agent\blue-skillhub && git diff a11f12d..388d3fb -- skills/intent-anchor/SKILL.md skills/intent-anchor/README.md
```

预期 diff：
- `SKILL.md`：2 处 `S1-S8` → `S1-S10`（强制规则 #4、Phase 2.5 标题）
- `README.md`：1 处 `S1-S8` → `S1-S10`（文件结构注释）

原因：A3 提交新增了 S9/S10，但漏改了这 3 处文本引用。`semantic-audit.md` 参考文件、`intent_validate.py` 校验器、测试 fixture 和 Phase 2.5 表格内容都已正确更新为 S1-S10，只有这 3 处描述性文本遗漏。

## 输出要求

- 总结论只能是 PASS、FAIL 或证据不足。
- 每项检查都要给出结论和具体文件、代码位置或命令证据。
- 单独列出漏改、误改、无关改动、未验证内容和剩余风险；没有也要明确写"未发现"。
- 本轮不要修复发现的问题。先提交验收报告，等待用户决定下一步。

## 验收结论标准

全部 25 项检查通过 → 验收通过。

任一检查不通过 → 记录问题编号、实际输出和预期输出的差异，返回修复后重新验收。
