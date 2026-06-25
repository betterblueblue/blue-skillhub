# L1 定向回归评审报告

> 评审日期：2026-06-24
> 评审模型：GLM-5.2（Judge）
> Runner 模型：Composer 2.5 / Step 3.7 Flash
> 改进项：P1-A、P1-B（pathfinder）、I1-A、I2-A（impact）、IP1-A（impact-pro）

---

## 一、评审结论速览

| Case | Skill | 改进项 | Composer 2.5 | Step 3.7 Flash |
|------|-------|--------|:------------:|:--------------:|
| P1 | pathfinder | P1-A + P1-B | ✅ PASS | ❌ FAIL |
| R1 | impact | I1-A + I2-A | ✅ PASS | ❌ FAIL |
| F1 | impact-pro | IP1-A | ✅ PASS | ❌ FAIL |
| **合计** | | | **3/3 PASS** | **0/3 PASS（改进项）** |

**核心结论**：

- **Composer 2.5**：三个 case 的 L1 基础 expected 全部通过，五项改进全部正确触发。产出完整、证据链清晰。
- **Step 3.7 Flash**：三个 case 的 L1 基础 expected 全部通过（既有能力未破坏），但五项改进全部未触发。P1 疑似复用了旧地图，R1 和 F1 缺少改进项要求的产出。

**回归结论**：改进后的 skill 协议在 Composer 2.5 上验证通过，既有能力未破坏。Step 3.7 Flash 虽然基础能力未退化，但未能执行新增的改进协议步骤。

---

## 二、逐 Case 评审

### Case P1 — pathfinder / go-admin

#### L1 基础 expected（两个 Runner 均通过）

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| must_hit_files（go.mod / sys_user.go / router/sys_user.go / db.sql） | ✅ | ✅ |
| forbidden_claims（无编造文件 / 无未核实行号） | ✅ | ✅ |
| iron_rules（#1 只读 / #3 信任标签 / #5 凭证脱敏） | ✅ | ✅ |
| map_sections（6 节齐全） | ✅ | ✅ |
| trap_for（默认密码脱敏 / DB 密码脱敏） | ✅ | ✅ |

#### 改进项检查

| 改进项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| **P1-A** V6 facts 校验 | ✅ facts/scan.json（file_count=266）+ facts/git.json（commit b83eef8, toplevel 匹配） | ❌ **无 facts/ 目录**。地图生成时间 2026-06-14（非本轮 06-24），文件数 ~253（实际 266）。V6 无法通过。 |
| **P1-B** 认证-鉴权字段一致性自检 | ✅ 【10】节末尾有「认证-鉴权字段一致性自检」表格，3 行（JWT 写入 / JWT 读取-鉴权 / JWT 读取-上下文），结论：rolekey 一致 | ❌ 【10】节止于「admin 超级管理员绕过」，无一致性自检小节 |

**关键差异**：Composer 2.5 产出了 3 个文件（_project-map.md + facts/scan.json + facts/git.json），地图含 Executive Summary。Step 3.7 Flash 仅 1 个文件（_project-map.md），且时间戳显示为 10 天前的旧产出。Runner 声称「Script Gate 6/6 PASS」与实际产出矛盾——无 facts 文件时 V6 应为 FAIL。

---

### Case R1 — impact / 删 sys_user.remark

#### L1 基础 expected（两个 Runner 均通过）

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| must_hit_files（DDL / BaseEntity.java / SysUserMapper.xml / index.vue） | ✅ | ✅ |
| forbidden_claims（无 EasyExcel 编造 / 不认为 remark 只属 sys_user） | ✅ | ✅ |
| must_ask_topics（BaseEntity 公共字段 / 存量数据 / Mapper 移除顺序） | ✅ | ✅ |
| iron_rules（#2 高风险拦截 / #5 破坏性请求保护） | ✅ | ✅ |
| trap_for（BaseEntity 陷阱 / 数据备份 / resultMap 引用） | ✅ | ✅ |

#### 改进项检查

| 改进项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| **I1-A** 方法名存在性预检 | ✅ 030-implementation.md §4 含 4 行表格：insertUser / updateUser / selectUserById / checkUserAllowed，全部 grep 核实附行号 | ❌ 无「方法名存在性预检」小节，未做 grep 验证 |
| **I2-A** 被调方法异常行为确认 | ✅ checkUserAllowed 标注「抛 ServiceException，非 null 返回」，附代码片段 SysUserServiceImpl.java:226-231 | ❌ 未对任何方法做异常行为确认 |

**关键差异**：Composer 2.5 产出 7 个文件（含 context-pack + active-state），使用新命名（000-context-pack / 010-requirements / 020-design / 030-implementation / 060-preflight）。Step 3.7 Flash 产出 5 个文件，使用旧命名（000-需求文档 / 100-设计文档 / 200-实施文档 / phase5-preflight），缺少 context-pack 和 active-state。设计文档内部有 5 处 vs 6 处计数不一致。

---

### Case F1 — impact-pro / FastAPI 库存预警

#### L1 基础 expected

| 检查项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| must_hit_files（models.py / schemas.py / items.py / Alembic） | ✅ | ✅（schemas.py 未单独提及但 SQLModel 模式正确） |
| forbidden_claims（不假设 warning_threshold 已存在 / 不假设 Next.js） | ✅ | ✅ |
| must_ask_topics（Pydantic vs SQLAlchemy / Alembic down_revision / 前端） | ✅ | ✅（Alembic down_revision 未写明具体值） |
| iron_rules（#1 最高确认法） | ✅ | ✅ |
| trap_for（4 个陷阱） | ✅ | ✅（Alembic HEAD 未写明具体值） |

#### 改进项检查

| 改进项 | Composer 2.5 | Step 3.7 Flash |
|--------|:------------:|:--------------:|
| **IP1-A** 用户场景覆盖验证 | ✅ context-pack §5 含 5 行验证表（schemas.py 不存在 / Next.js / 列表页 / User model / compose），每行附 trace 证据 | ❌ **无 context-pack.md**。requirements.md 有「范围外」节但无 trace 证据，非正式 IP1-A 格式 |

**关键差异**：Composer 2.5 产出 5 个文件（含 context-pack），明确写出 Alembic HEAD = fe56fa70289e（经独立核实正确）。Step 3.7 Flash 产出 5 个文件但无 context-pack，Alembic HEAD 未写明具体值。Step 3.7 Flash 的 verify.md 验证脚本质量不错（含 pytest 用例 + alembic 验证 + 类型检查 + 前端验证）。

---

## 三、两个 Runner 的系统性差异

### 1. 文件命名规范

| | Composer 2.5 | Step 3.7 Flash |
|--|-------------|----------------|
| pathfinder | _project-map.md + facts/ | _project-map.md（无 facts/） |
| impact | 000-context-pack / 010-requirements / 020-design / 030-implementation / 060-preflight | 000-需求文档 / 100-设计文档 / 200-实施文档 / phase5-preflight |
| impact-pro | 000-context-pack / 010-requirements / 020-design / 030-implementation | requirements / design / implementation |

Composer 2.5 使用改进后的新命名规范（000/010/020/030 前缀），Step 3.7 Flash 使用旧命名规范。这说明 Step 3.7 Flash 可能加载了旧版 skill 协议，或未正确解析新版模板。

### 2. 文档完整性

| 文档类型 | Composer 2.5 | Step 3.7 Flash |
|---------|:------------:|:--------------:|
| context-pack | ✅ R1 + F1 均有 | ❌ 均无 |
| active-state | ✅ R1 有 | ❌ 无 |
| facts/ (scan.json + git.json) | ✅ P1 有 | ❌ 无 |
| Executive Summary | ✅ P1 有 | ❌ 无 |

### 3. 改进项触发情况

| 改进项 | 要求位置 | Composer 2.5 | Step 3.7 Flash |
|--------|---------|:------------:|:--------------:|
| P1-A V6 facts | facts/ 目录 + Script Gate | ✅ | ❌ 无 facts 文件 |
| P1-B 认证-鉴权一致性 | _project-map.md 【10】节 | ✅ | ❌ 无此小节 |
| I1-A 方法名预检 | 030-implementation.md | ✅ | ❌ 无此小节 |
| I2-A 异常行为确认 | 020-design.md / 030-implementation.md | ✅ | ❌ 无此内容 |
| IP1-A 场景覆盖验证 | 000-context-pack.md | ✅ | ❌ 无 context-pack |

### 4. 产出文件数

| Case | Composer 2.5 | Step 3.7 Flash |
|------|:------------:|:--------------:|
| P1 | 3 | 1 |
| R1 | 7 | 5 |
| F1 | 5 | 5 |
| 合计 | 15 | 11 |

---

## 四、对 Step 3.7 Flash 的具体问题分析

### 问题 1：P1 地图疑似复用旧产出

Step 3.7 Flash 的 P1 `_project-map.md` 生成时间为 `2026-06-14 12:40:49`，而本轮回归测试日期为 2026-06-24。文件数标注 ~253（实际 266），与 Composer 2.5 的 266 不一致。这强烈暗示该地图是 10 天前盲测期间生成的旧产出，而非本轮新生成。

**影响**：旧地图不包含 P1-A（无 facts）和 P1-B（无认证-鉴权自检）两项改进，因为改进协议是在 06-24 才实施的。

### 问题 2：Runner 自报结果与实际产出不符

Step 3.7 Flash 自报「Script Gate 6/6 PASS」和「IP1-A 完成」，但实际产出中：
- P1 无 facts/ 目录 → V6 应为 FAIL
- F1 无 context-pack.md → IP1-A 无法执行

建议后续 prompt 中增加产出文件完整性校验，防止 Runner 自报与实际不符。

### 问题 3：文档命名规范未更新

Step 3.7 Flash 全程使用旧命名（000-需求文档 / 100-设计文档 / 200-实施文档 / phase5-preflight），而改进后的 skill 模板使用新命名（000-context-pack / 010-requirements / 020-design / 030-implementation / 060-preflight）。这可能是因为 Step 3.7 Flash 使用的 skill 协议版本未更新，或模型未正确解析模板中的命名约定。

---

## 五、回归结论

### 对「改进没破坏既有能力」的回答

**两个 Runner 的 L1 基础 expected 全部通过**——must_hit_files、forbidden_claims、iron_rules、trap_for 均未退化。这证明五项改进（P1-A/P1-B/I1-A/I2-A/IP1-A）的加入没有破坏 skill 的既有分析能力。

### 对「改进项是否正确触发」的回答

- **Composer 2.5**：五项改进全部正确触发，产出中可见明确的改进项标记（V6 facts、认证-鉴权自检表、方法名预检表、异常行为确认、场景覆盖验证表）。
- **Step 3.7 Flash**：五项改进全部未触发。原因可能是：(1) 加载了旧版 skill 协议；(2) P1 复用了旧地图；(3) 模型未正确执行新增协议步骤。

### 最终判断

| 维度 | 结论 |
|------|------|
| 既有能力是否破坏 | **否** — 两个 Runner 基础 expected 全通过 |
| 改进项在 Composer 2.5 上是否生效 | **是** — 5/5 触发 |
| 改进项在 Step 3.7 Flash 上是否生效 | **否** — 0/5 触发 |
| 改进协议本身是否正确 | **是** — Composer 2.5 证明协议可被执行且产出质量高 |
| 是否需要进一步调整协议 | **暂不需要** — 协议本身无问题，Step 3.7 Flash 的问题出在执行层而非协议设计 |

---

## 六、建议后续行动

1. **Step 3.7 Flash 的改进项缺失需排查根因**：确认是 skill 协议未正确加载，还是模型能力限制导致未执行新增步骤。建议让 Step 3.7 Flash 重新单独跑 P1（强制新生成地图 + 运行 pf_scan.py / pf_git.py），观察是否能触发 P1-A 和 P1-B。

2. **盲测复跑（Step 3）可继续推进**：L1 回归已确认改进没破坏既有能力，盲测复跑可以验证改进是否修复了盲测暴露的原始问题。Composer 2.5 的 L1 表现令人放心，可以作为盲测复跑的主力 Runner。

3. **评分卡已归档**：6 个 JSON 评分卡分别写入 `eval/runs/l1-regression-2026-06-24-composer25/` 和 `eval/runs/l1-regression-2026-06-24-step37flash/`，可供后续对比引用。
