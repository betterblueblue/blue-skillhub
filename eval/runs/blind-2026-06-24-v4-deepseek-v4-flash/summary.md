# DeepSeek-V4-Flash 盲测 v4 评审报告（干净环境）

> 日期：2026-06-25
> 评审方式：源码级检查（实际文件内容 + facts JSON + 产出完整性验证）
> 环境：v4 修正 prompt（Step 0 清理 + 默认路径 + 归档）
> 模型基线：首次参与盲测，无 v3 基线

---

## 环境隔离验证

| 指标 | 值 | 结论 |
|------|-----|------|
| scan.json file_count | **65** | ✅ 与 Composer 一致，change-impact/ 未计入 |
| .md 文件数 | **2** | ✅ 仅 README + CONTRIBUTING |
| dir_tree 含 change-impact/ | **否** | ✅ 目录树干净 |
| facts 路径 | `_project-map/facts/` | ✅ 默认路径，pf_validate.py 能找到 |
| git.json head_short | `346d60f` | ✅ 与 Composer 一致 |

**环境隔离结论**：干净环境，与 Composer 2.5 同等起跑线。

---

## 三项优化验证

### 优化 6（P1-A）— B6 facts 文件强制：✅ PASS

- `scan.json`：`file_count: 65`，`dir_tree` 含根 `/`，`budget_tier: "small"` — 内容真实
- `git.json`：`head_short: "346d60f"`，`toplevel` 指向 prisma-express-ts — 一致
- 地图【0】节引用 facts：「预算档位 | 小仓（small）：65 源文件，37 目录」
- DeepSeek 首次跑即正确产出 facts，说明优化 6 的 Phase 1.5 强化对新模型有效

### 优化 7（I2-A）— B1 覆盖范围语义核查：❌ FAIL

这是 DeepSeek 与 Composer 最大的分歧点。

**DeepSeek 的判断**：B1 判 **light**，结论是「本功能已完整实现，无需新增代码」。

**实际问题**：用户原话含全量词「每次接口请求都要记录」。DeepSeek 自己在 light.md 第 25-34 行也识别到了覆盖缺口：

> `LogAspect` 切面通过 `@Before/@AfterReturning/@AfterThrowing` 拦截所有标有 `@Log` 注解的方法。
> ...
> 目前 `costTime` 记录只作用于带 `@Log` 注解的端点。如果要求"每次接口请求都记录耗时"，当前实现存在覆盖缺口。

**但 DeepSeek 识别到缺口后仍然判了 light**，只是在"建议"里提了一句"如果需要全覆盖需要新增拦截器"。这直接违反了优化 7 的规则：**全量词场景 + 覆盖范围缺口 = 必须倾向 full**。

**与 Composer 对比**：Composer 识别到同样的缺口后判了 **full**，并产出了完整的 `000-context-pack.md` + `010-requirements.md` + `020-design.md` + `030-implementation.md` + `060-preflight.md` + 验证脚本。DeepSeek 只产出了 `040-light.md`。

**根因分析**：DeepSeek 可能对 skill 协议中 Phase 2.5 的覆盖范围语义核查规则理解不充分——它识别到了缺口，但没有把缺口和全量词关联起来触发 full。这可能是模型能力限制（对规则的条件-动作映射不够敏感），也可能是 prompt 中 Read SKILL.md 后对 references 的读取不够深入。

### 优化 8（需求文档边界）：⚠️ N/A（未产出需求文档）

DeepSeek 的 B1 和 B2 都判了 light，只产出了 `040-light.md`，没有 `010-requirements.md`。因此优化 8 无法验证。

B3 产出了 `000-context-pack.md`，但其中混合了需求、设计和实施内容（在一个文件里写了 Phase 1 到 Phase 3.5 + 010 + 020 + 030），没有按 skill 要求拆分成独立文档。context-pack 里直接包含了 Prisma schema 代码片段、Joi 验证器代码、TypeScript 方法签名——这些都是技术细节，不应出现在需求层。

**结论**：优化 8 无法有效验证，标记为 N/A。

---

## v3 五项回归检查（作为初始基线）

| 检查项 | Case | 结果 | 详情 |
|--------|------|------|------|
| P1-A（facts 强制） | B6 | ✅ PASS | facts 存在且内容真实 |
| P1-B（认证-鉴权自检） | B6 | ✅ PASS | 【10】节有「认证-鉴权字段一致性检查」表格，明确标注 ❌ 不一致；【9】风险区域 #1 记录 RBAC 失效；【11】主流程逐步骤展示 RBAC 失败链路 |
| I1-A（方法名验证） | B2 | ⚠️ PARTIAL | B2 判 light 说"无需修改"，没有 grep 验证方法名。但 light.md 中引用了 SecurityUtils.encryptPassword / matchesPassword，路径基本正确。未验证 resetPwd / resetUserPwd 是否存在 |
| I2-A（覆盖范围核查） | B1 | ❌ FAIL | 识别到覆盖缺口但未触发 full |
| IP1-A（Prisma 项目分析） | B3 | ⚠️ PARTIAL | 正确识别了 schema → validation → service → controller → tests 全链路。但产出不完整：只有 context-pack，没有独立的 010/020/030 文档；context-pack 混入了代码片段和技术细节 |

---

## B2 争议分析

DeepSeek 判 B2 为 light（「密码已用 BCrypt，无需迁移」），Composer 判 B2 为 full（「代码已是 BCrypt，但需兼容旧 MD5 存量」）。

**关键分歧**：用户原话是「我看了一下代码，用户密码好像是用 MD5 加密的，我想改成 BCrypt。但是已经有很多老用户了，他们的密码是 MD5 的，不能直接作废，要兼容。」

- **DeepSeek 的逻辑**：代码核查发现已用 BCrypt → 用户假设有误 → 无 MD5 存量 → 无需迁移 → light
- **Composer 的逻辑**：代码核查发现已用 BCrypt → 用户假设有误 → 但用户明确说"已经有很多老用户是 MD5 的" → 保留兼容路径以防外部导入的 MD5 存量 → full

**评判**：两者都有道理，但 Composer 更稳妥。用户说的"老用户是 MD5 的"可能指从旧系统迁移来的数据，即使当前代码用 BCrypt，也不能排除数据库里有历史 MD5 数据。DeepSeek 的 light 判断过于绝对——它说"不建议产生老用户 MD5 存量数据的场景"，但这不是 DeepSeek 能决定的，是业务现实。不过这是判断分歧，不是协议违规。

---

## 产出完整性对比

| Case | Composer 2.5 | DeepSeek-V4-Flash |
|------|-------------|-------------------|
| B6 | _project-map.md + facts/ | _project-map.md + facts/ ✅ 对等 |
| B1 | 8 个文件（context-pack + full 三文档 + preflight + 验证脚本） | 1 个文件（040-light.md）❌ 严重不足 |
| B2 | 8 个文件（同上结构） | 1 个文件（040-light.md）❌ 严重不足 |
| B3 | 8 个文件（context-pack + full 三文档 + preflight + 验证脚本） | 1 个文件（000-context-pack.md，混合内容）❌ 严重不足 |

---

## 整体判定

| 维度 | 判定 |
|------|------|
| 优化 6（P1-A） | ✅ PASS |
| 优化 7（I2-A） | ❌ FAIL |
| 优化 8 | N/A（未产出需求文档） |
| P1-B（认证-鉴权自检） | ✅ PASS |
| I1-A（方法名验证） | ⚠️ PARTIAL |
| IP1-A（Prisma 项目分析） | ⚠️ PARTIAL |
| 产出完整性 | ❌ 严重不足（B1/B2/B3 均缺文档） |

**总结**：DeepSeek-V4-Flash 在 pathfinder（B6）上表现优秀——facts 产出正确、认证-鉴权自检完整、主流程链路追踪到位。但在 impact/impact-pro（B1/B2/B3）上明显偏弱：B1 识别到覆盖缺口但未触发 full（优化 7 FAIL），B2 判断过于绝对，B3 产出不完整。总体来看，DeepSeek 适合做 pathfinder Runner，但不适合独立做 impact/impact-pro Runner——至少在 v3.8 协议下，它对 Phase 2.5 覆盖范围核查和 Phase 4 文档拆分的执行不够到位。

**建议评级**：Pathfinder Runner（仅 B6 场景），不建议作为 impact/impact-pro 的独立 Runner。
