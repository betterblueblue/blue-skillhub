# 盲测 v4 测试设计

> 日期：2026-06-24
> 基线：v3 盲测结果（`eval/runs/blind-2026-06-24-v3-composer25/summary.md`、`eval/runs/blind-2026-06-24-v3-step37flash/summary.md`）

---

## 一、为什么需要 v4

### 1.1 v3 盲测后的协议优化

v3 盲测跑完后，针对暴露的问题又做了 3 项优化（优化 6-8），但这 3 项优化**没有被任何一轮测试验证过**：

| 优化 | 改哪里 | 改什么 | 解决的问题 |
|------|--------|--------|-----------|
| 优化 6（P1-A 加固） | `pathfinder/scripts/pf_validate.py` + `pathfinder/SKILL.md` | V6 facts 文件缺失从 WARN 改为 FAIL；Phase 1.5 强化"必做不可跳过" | v3 中 Step 3.7 Flash 跳过 Phase 1.5 不产出 facts，Script Gate 仍 5/5 通过 |
| 优化 7（I2-A 新增） | `impact/SKILL.md` Phase 2.5 + `impact-pro/SKILL.md` Phase 2.5 | 覆盖范围语义核查：全量词（每次/所有/全部）场景必须核实现有实现是否真全覆盖 | v3 中 Step 3.7 Flash 把"每次接口请求"误判 light（LogAspect 只覆盖 @Log 注解接口） |
| 优化 8（需求文档边界） | `impact/SKILL.md` Phase 4 + `impact-pro/SKILL.md` Phase 4 | 需求文档内容边界自检：只写业务需求，技术细节下沉到 020/030 | v3 中两个模型的 `010-requirements.md` 都混入了表名、类名、文件路径、代码片段 |

### 1.2 v4 的核心假设

**优化 6-8 落地后：**
- **Composer 2.5**（v3 已 5/5）：优化 7-8 让它的需求文档更干净，不退步即成功
- **Step 3.7 Flash**（v3 是 3/5，P1-A 和 I2-A 仍 FAIL）：优化 6 和 7 直接针对这 2 项失败，预期能修复

验证方式：用和 v3 相同的 4 个 case（B6/B1/B2/B3）重新跑，对比 v3 结果。

### 1.3 v4 测试环境隔离修正

**问题发现**：v4 初版 prompt 让各模型输出到 `change-impact/blind-v4-<model>/<case-id>/` 自定义子目录，但存在三个污染问题：

1. **pf_scan.py 不跳过 `change-impact/`**：扫描器把所有模型的产出文件计入项目文件数（prisma-express-ts 实际源码约 70 个文件，扫描报 106 个，`.md` 文件虚高 31 个）
2. **pf_validate.py V6 路径不匹配**：验证器硬编码检查 `change-impact/_project-map/facts/`，但模型输出到自定义子目录，V6 靠旧 facts 残留假 PASS
3. **跨模型污染**：后跑的模型能读到先跑模型的产出，破坏测试独立性；每个模型的起跑线不同

**修正方案（三项联动）**：

| 修正项 | 改哪里 | 改什么 |
|--------|--------|--------|
| pf_scan.py 永久修复 | `SKIP_DIRS` | 加入 `"change-impact"`，扫描器永不把自己的产出计入项目文件数 |
| 测试前清理 | prompt Step 0 + `eval/scripts/clean-before-run.sh` | 每个模型跑之前删除 `change-impact/`，确保干净起跑线 |
| 使用默认路径 + 完成后归档 | prompt 输出路径规则 + 归档步骤 | 跑的时候用 skill 默认路径（pf_validate.py 能正确找到 facts），跑完后统一归档到 `blind-v4-<model>/<case-id>/` |

**对已有 v4 结果的影响**：Composer 2.5 和 Step 3.7 Flash 的 v4 结果是在污染环境下获得的。其中 V6（facts 检查）的验证结论不可靠（可能假 PASS）。其余维度（优化 7/8）受影响较小但不排除交叉污染。如需严格结论，这两个模型应使用修正后的 prompt 重跑。

---

## 二、测试范围

### 2.1 Case 选择

v4 跑和 v3 完全相同的 4 个 case，便于逐项对比：

| Case | Skill | 验证的优化 | v3 状态 | v4 验证目标 |
|------|-------|-----------|---------|------------|
| B6 | pathfinder | 优化 6（P1-A facts 强制） + P1-B 回归 | Composer ✅ / Step ❌(无 facts) | Composer 保持 ✅ / **Step 要么产出 facts，要么被 Script Gate 拦截** |
| B1 | impact | 优化 7（I2-A 覆盖范围核查） + 优化 8（需求文档） | Composer ✅ / Step ❌(判 light) | Composer 保持 ✅ / **Step 识别"每次"全量词→倾向 full** |
| B2 | impact | I1-A 回归 + 优化 8（需求文档） | Composer ✅ / Step ✅(v3 修复) | 两模型保持 ✅ / **需求文档无技术细节** |
| B3 | impact-pro | IP1-A 回归 + 优化 8（需求文档） | Composer ✅ / Step ✅(v3 修复) | 两模型保持 ✅ / **需求文档无技术细节** |

### 2.2 Runner 模型

**已有基线模型：**
- Composer 2.5（v3 中 5/5 全通过）
- Step 3.7 Flash（v3 中 3/5 修复，P1-A 和 I2-A 仍 FAIL）

**新增模型（首次参与盲测，无 v3 基线）：**
- DeepSeek-V4-Flash
- SenseNova-6.7-Flash-Lite

新增模型使用与已有模型完全相同的 4 个 case（B6/B1/B2/B3）和相同的 prompt 结构（含 Read SKILL.md 前置步骤 + Step 0 环境清理）。v4 结果将作为这两个模型的初始基线，后续可用于横向对比和模型选型。

**环境隔离**：v4 修正后，每个模型跑之前都会清理 `change-impact/` 目录，确保四个模型的测试互不污染。

### 2.3 评审模型

GLM-5.2（与 v2/v3 相同，消除评审者变量）

---

## 三、验证点和成功标准

### 3.1 三项优化验证矩阵

| 优化 ID | Case | 验证点 | v3 结果 | v4 成功标准 |
|---------|------|--------|---------|------------|
| 优化 6（P1-A） | B6 | facts 文件存在且内容真实；或 Script Gate 拦截无 facts 的地图 | Composer ✅ / Step ❌(无 facts，Gate 仍过) | Composer 保持 ✅ / **Step 不再被放行** |
| 优化 7（I2-A） | B1 | 识别"每次接口请求"全量词，核实 LogAspect 覆盖范围，倾向 full | Composer ✅ / Step ❌(判 light) | Composer 保持 ✅ / **Step 不再判 light** |
| 优化 8（需求文档） | B1/B2/B3 | `010-requirements.md` 无表名/类名/文件路径/代码片段 | 两模型都有技术细节 | **两模型需求文档只含业务描述** |

### 3.2 逐项验证细则

#### 优化 6：B6 facts 文件强制 + Script Gate 拦截

- 检查 `facts/scan.json` 的 `file_count > 0`（修复后预计约 70，不再包含 change-impact/ 产出文件）
- 检查 `facts/git.json` 的 `head_short` 非 null（实际 346d60f）
- 检查 `facts/git.json` 的 `toplevel` 指向 prisma-express-ts
- **如果模型跳过 Phase 1.5 不产出 facts**：检查 `pf_validate.py` 是否返回非零退出码、地图是否被拦截不写入
- **Composer 2.5**：v3 已产出 facts，v4 只需确认不退步
- **Step 3.7 Flash**：v3 跳过 Phase 1.5 且 Gate 放行；v4 优化 6 后，要么补产出 facts，要么被 Gate 拦截（两种都算改进，重点是不再"无 facts 却 Gate PASS"）

#### 优化 7：B1 覆盖范围语义核查

- 用户原话含全量词"每次接口请求都要记录"
- 检查 Phase 2.5 是否核实现有 LogAspect 的实际覆盖范围（`@Log` 注解只覆盖标注接口，非全部接口）
- 检查是否因覆盖范围缺口标记"倾向 full"而非 light
- **Composer 2.5**：v3 已识别，v4 只需确认不退步
- **Step 3.7 Flash**：v3 判 light 绕过；v4 必须识别全量词并倾向 full

**关键验证**：用户说"每次接口请求"，但 RuoYi 的 `LogAspect` 通过 `@Log` 注解切面只覆盖标注了 `@Log` 的 Controller 方法，未标注的接口不会记录耗时。这是覆盖范围缺口，应触发 full 而非 light。

#### 优化 8：B1/B2/B3 需求文档内容边界

- 检查 `010-requirements.md` 是否出现以下技术细节（均不应出现）：
  - 表名（如 `sys_user`、`sys_oper_log`）
  - 类名/方法名（如 `SecurityUtils`、`LogAspect`）
  - 文件路径（如 `src/main/java/...`）
  - 代码片段
  - 字段类型定义（如 `varchar(100)`、`bigint`）
  - schema 变更方案、API 契约细节、依赖注入方式、ORM 用法
- 检查需求文档是否只含业务内容：业务场景、功能需求、非功能需求业务指标、业务约束、验收标准
- **两个模型**：v3 都有技术细节渗入；v4 必须移除

---

## 四、执行流程

```
Step 1: 协议优化 6-8（已完成）
  - pf_validate.py V6 facts 缺失 WARN→FAIL
  - pathfinder SKILL.md Phase 1.5 强化 + Phase 4 Script Gate 加 facts 存在性
  - impact/impact-pro SKILL.md Phase 2.5 增加覆盖范围语义核查
  - impact/impact-pro SKILL.md Phase 4 增加需求文档内容边界自检

Step 2: 盲测 v4 执行（每个模型独立跑，跑前清理 change-impact/）
  - 每个模型跑之前执行 Step 0 清理：rm -rf change-impact/
  - 模型用 skill 默认路径输出，跑完后归档到 blind-v4-<model>/<case-id>/
  - Composer 2.5 跑 B6/B1/B2/B3（4 个 case，含 Read SKILL.md + Step 0 清理 + 归档）
  - Step 3.7 Flash 跑 B6/B1/B2/B3（同上）
  - DeepSeek-V4-Flash 跑 B6/B1/B2/B3（同上）
  - SenseNova-6.7-Flash-Lite 跑 B6/B1/B2/B3（同上）
  - prompt 文件：
    - eval/cases/blind/PROMPT-composer25-v4.md
    - eval/cases/blind/PROMPT-step37flash-v4.md
    - eval/cases/blind/PROMPT-deepseek-v4-flash-v4.md
    - eval/cases/blind/PROMPT-sensenova-6.7-flash-lite-v4.md
  - 产出目录：blind-v4-{composer25,step37flash,deepseek-v4-flash,sensenova-6.7-flash-lite}/

Step 3: 评审
  - 评审者：GLM-5.2
  - 评审标准：JUDGE-RUBRIC.md（6 维度 100 分 + 4 项安全门禁）
  - 额外检查：3 项优化验证点（见上文 3.2）
  - 产出评分卡：eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash,sensenova-6.7-flash-lite}/

Step 4: 对比判定
  - v4 vs v3 对比：每项优化是修复/保持/退步（仅 Composer 2.5 和 Step 3.7 Flash）
  - 新增模型：以相同评审标准打分，建立初始基线，与已有模型横向对比
  - 整体判定：3 项优化在各 Runner 上的通过情况
```

---

## 五、判定标准

### 5.1 单项判定

每个优化项的判定分为三档：

| 判定 | 含义 |
|------|------|
| ✅ PASS | 优化触发且产出正确 |
| ❌ FAIL | 优化未触发或产出有错 |
| ⚠️ PARTIAL | 优化触发但产出有瑕疵 |

### 5.2 整体判定

| 场景 | 判定 |
|------|------|
| 3/3 优化在 Composer 2.5 上 PASS（含 v3 五项不退步） | 协议优化完全成功，Composer 2.5 可定版 |
| 优化 6 和 7 在 Step 3.7 Flash 上 PASS（v3 剩余 2/5 修复） | Step 3.7 Flash 达 5/5，prompt 加固 + 优化 6-7 联合生效 |
| 优化 6 或 7 在 Step 3.7 Flash 上仍 FAIL | 需排查是模型能力限制还是协议执行问题 |
| 优化 8 在两模型上都 PASS | 需求文档去技术化生效 |
| 优化 8 仍 FAIL | 需考虑在 Script Gate 或模板层强制拦截技术细节 |
| 新增模型（DeepSeek-V4-Flash / SenseNova-6.7-Flash-Lite）3/3 优化 PASS | 新模型可完整执行 v3.8 协议，具备 Runner 资格 |
| 新增模型优化 6 或 7 FAIL | 该模型无法正确执行 Phase 1.5 或覆盖范围核查，不适合作为 Runner |
| 新增模型优化 8 FAIL | 该模型能执行分析但需求文档去技术化不彻底，需评估是否可接受 |

### 5.3 v3 五项改进的回归检查

v4 同时验证 v3 已通过的 5 项（P1-A/P1-B/I1-A/I2-A/IP1-A）不退步。如果 v4 中任何一项从 PASS 退步到 FAIL，说明优化 6-8 的改动破坏了 v3 成果，需回溯。

---

## 六、文件索引

| 文件 | 说明 |
|------|------|
| `eval/cases/blind/PROMPT-composer25-v4.md` | Composer 2.5 v4 一键执行 prompt（含 Step 0 清理 + Read SKILL.md + 归档） |
| `eval/cases/blind/PROMPT-step37flash-v4.md` | Step 3.7 Flash v4 一键执行 prompt（同上） |
| `eval/cases/blind/PROMPT-deepseek-v4-flash-v4.md` | DeepSeek-V4-Flash v4 一键执行 prompt（同上） |
| `eval/cases/blind/PROMPT-sensenova-6.7-flash-lite-v4.md` | SenseNova-6.7-Flash-Lite v4 一键执行 prompt（同上） |
| `eval/scripts/clean-before-run.sh` | 测试前清理脚本（删除 change-impact/ 目录） |
| `skills/pathfinder/scripts/pf_scan.py` | 项目扫描器（v4 修正：SKIP_DIRS 加入 change-impact） |
| `eval/cases/blind/JUDGE-RUBRIC.md` | 评审标准（v4 复用，不变） |
| `eval/runs/blind-2026-06-24-v3-composer25/summary.md` | v3 Composer 2.5 结果（v4 基线） |
| `eval/runs/blind-2026-06-24-v3-step37flash/summary.md` | v3 Step 3.7 Flash 结果（v4 基线） |
| `docs/archive/2026-06/skill-improvement-2026-06-24.md` | 改进方案文档（含优化 6-8 详情） |
