# Step 3.7 Flash 盲测 v4 评审报告（干净环境）

> 日期：2026-06-25
> 评审方式：源码级检查（实际文件内容 + facts JSON + 产出完整性验证）
> 环境：v4 修正 prompt（Step 0 清理 + 默认路径 + 归档）
> 基线：v3 盲测结果（3/5 PASS，P1-A 和 I2-A 仍 FAIL）

---

## 环境隔离验证

| 指标 | v3（污染环境） | v4（干净环境） | 结论 |
|------|---------------|---------------|------|
| scan.json file_count | 106 | **65** | ✅ 修复生效 |
| .md 文件数 | 31 | **2** | ✅ 仅 README + CONTRIBUTING |
| dir_tree 含 change-impact/ | 是 | **否** | ✅ 目录树干净 |
| facts 路径 | 自定义子目录（V6 假 PASS） | **默认路径**（V6 真 PASS） | ✅ pf_validate.py 正确找到 |
| git.json head_short | `346d60f` | `346d60f` | ✅ 一致 |

---

## 三项优化验证

### 优化 6（P1-A）— B6 facts 文件强制：✅ PASS（v3 FAIL → v4 修复）

- `scan.json`：`file_count: 65`，`dir_tree` 含根 `/`，`budget_tier: "small"` — 内容真实
- `git.json`：`head_short: "346d60f"`，`toplevel` 指向 prisma-express-ts — 一致
- 地图【0】节引用 facts：「文件数: 65 个」
- **v3 对比**：v3 中 Step 3.7 Flash 跳过 Phase 1.5 不产出 facts，Script Gate 仍 5/5 通过（V6 当时是 WARN 不是 FAIL）。v4 优化 6 将 V6 改为 FAIL + 强制 Read SKILL.md 后，Step 3.7 Flash 正确产出了 facts。**这是 v3 剩余 2/5 失败项之一的修复。**

### 优化 7（I2-A）— B1 覆盖范围语义核查：❌ FAIL（v3 FAIL → v4 仍未修复）

Step 3.7 Flash 在 B1 仍然判了 **light**，产出 `040-light.md`，结论是「功能已完整实现，无需改动」。

**关键问题**：用户原话含全量词「每次接口请求都要记录」。light.md 第 19 行写道：

> 用户描述的"每次接口请求记录响应耗时 + 操作日志列表展示"功能在代码库中已完整实现

但 Step 3.7 Flash **没有核实 LogAspect 的实际覆盖范围**。light.md 中完全没有提到 `@Log` 注解、覆盖缺口、未覆盖的端点数量等信息。它只看到 LogAspect.java 有 `setCostTime` 就认为"已完整实现"。

**与 DeepSeek 对比**：DeepSeek 至少识别到了覆盖缺口（写了"约 63 个端点未覆盖"），只是没触发 full。Step 3.7 Flash 连缺口都没识别到，直接说"已完整实现"。

**与 Composer 对比**：Composer 识别到缺口后判了 full，并产出了完整的设计方案（OperLogTimingFilter + 共享 OperLogContext）。

**结论**：优化 7 在 Step 3.7 Flash 上未生效。可能原因：
1. 模型对 Phase 2.5 的覆盖范围语义核查规则理解不足
2. 模型在 Read SKILL.md 后可能没有深入读 references 中的完整规则
3. 模型能力限制——对全量词的条件反射不够敏感

**v3 对比**：v3 中 Step 3.7 Flash 也是判 light，I2-A FAIL。v4 仍未修复。**这是 v3 剩余 2/5 失败项中仍未修复的那个。**

### 优化 8（需求文档边界）：✅ PASS（B3）

Step 3.7 Flash 在 B3 产出了独立的 `010-requirements.md`，检查内容边界：

| 检查项 | 结果 |
|--------|------|
| 表名（sys_user 等） | ✅ 未出现 |
| 类名/方法名 | ✅ 未出现 |
| 文件路径 | ✅ 未出现 |
| 代码片段 | ✅ 未出现 |
| 字段类型定义 | ✅ 未出现 |
| 业务场景 | ✅ 有 |
| 功能需求 | ✅ 有 |
| 非功能需求 | ✅ 有 |
| 验收标准 | ✅ 有 |

`010-requirements.md` 纯业务语言，技术细节（Prisma schema、Joi 校验器代码、TypeScript 方法签名）全部在 `020-design.md` 和 `030-implementation.md` 中。

**注意**：B1/B2 判 light 只产出了 `040-light.md`，没有 `010-requirements.md`，因此优化 8 只在 B3 上可验证。B3 是 Step 3.7 Flash v3 已修复的项目，v4 保持。

---

## v3 五项回归检查

| 检查项 | Case | v3 结果 | v4 结果 | 详情 |
|--------|------|---------|---------|------|
| P1-A（facts 强制） | B6 | ❌ FAIL | ✅ **PASS** | facts 存在且内容真实——**v3 失败项已修复** |
| P1-B（认证-鉴权自检） | B6 | ✅ | ✅ | 【9】R1 记录认证-鉴权不一致；【10】有专门的交叉检查（4 步）；【11】主流程展示 RBAC 失败链路 |
| I1-A（方法名验证） | B2 | ✅ | ⚠️ PARTIAL | B2 判 light，light.md 引用了 SecurityUtils.encryptPassword/matchesPassword，但未 grep 验证 resetPwd/resetUserPwd |
| I2-A（覆盖范围核查） | B1 | ❌ FAIL | ❌ **FAIL** | 未识别覆盖缺口，直接判 light——**v3 失败项仍未修复** |
| IP1-A（Prisma 项目分析） | B3 | ✅ | ✅ | 正确识别全链路；产出 010/020/030 三文档；设计质量高（P2002 冲突处理、代码风格报告、风险回滚） |

---

## B3 产出质量详细评估

Step 3.7 Flash 在 B3 上的表现相当不错：

**010-requirements.md**：纯业务语言，5 条验收标准，约束条件清晰。

**020-design.md**：质量很高：
- 变更范围表（7 个文件）
- Prisma schema 变更含设计理由
- P2002 唯一冲突处理（PrismaClientKnownRequestError 捕获 → ApiError 转换）
- 代码风格报告（与现有模式对齐）
- 风险与回滚方案

**030-implementation.md**：6 个 Step，每个含维度、操作、影响范围、回滚方式、语义约定、验证方式。比 Composer 少了 preflight 和验证脚本，但核心实施文档质量合格。

**与 Composer B3 对比**：Composer 产出了 8 个文件（含 context-pack + preflight + 验证脚本），Step 产出了 3 个。文档质量上 Step 不逊色，但完整度有差距（缺 context-pack 和 preflight）。

---

## 产出完整性对比

| Case | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|------|-------------|----------------|-------------------|
| B6 | _project-map.md + facts/ | _project-map.md + facts/ ✅ | _project-map.md + facts/ ✅ |
| B1 | 8 文件（full） | 1 文件（light）❌ | 1 文件（light）❌ |
| B2 | 8 文件（full） | 1 文件（light）❌ | 1 文件（light）❌ |
| B3 | 8 文件（full） | 3 文件（full）⚠️ | 1 文件（混合）❌ |

---

## 整体判定

| 维度 | 判定 | v3 对比 |
|------|------|---------|
| 优化 6（P1-A） | ✅ PASS | **v3 FAIL → v4 修复** ✅ |
| 优化 7（I2-A） | ❌ FAIL | v3 FAIL → v4 仍未修复 |
| 优化 8（需求文档） | ✅ PASS（B3） | v3 已修复，v4 保持 |
| P1-B | ✅ PASS | 不退步 |
| I1-A | ⚠️ PARTIAL | 轻微退步（v3 有 grep 验证，v4 light.md 未体现） |
| IP1-A | ✅ PASS | 不退步 |

**v3 五项回归**：4/5 不退步 + 1/5 修复（P1-A）。I1-A 从 PASS 到 PARTIAL 是轻微退步（B2 判 light 导致没做方法名 grep），但不严重。

**总结**：Step 3.7 Flash 在 v4 中修复了 P1-A（facts 强制产出），从 v3 的 3/5 提升到 **4/5**。但 I2-A（覆盖范围核查）仍未修复——它在 B1 上既没有识别到覆盖缺口，也没有触发 full。这大概率是模型能力限制：Step 3.7 Flash 对全量词的条件反射和覆盖范围分析不够敏感。

**建议评级**：Runner（有限场景）。B6（pathfinder）和 B3（impact-pro 简单场景）可用；B1/B2（涉及覆盖范围判断的场景）不建议独立使用，需要人工复核判档。
