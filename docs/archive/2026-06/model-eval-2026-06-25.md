# 低成本模型能力评价：Composer 2.5 / Step 3.7 Flash / DeepSeek-V4-Flash

> 日期：2026-06-25
> 评审方式：v4 干净环境源码级核实（读取实际产出文件逐项核对，非仅凭模型自报）
> 测试范围：6 个真实开发场景（Java/Go/Node/Python 四个技术栈），覆盖 pathfinder、impact、impact-pro 三个 Skill
> 数据来源：`eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash}/` 评审报告

---

## 一、总览

三个模型在干净环境下的真实表现差异显著，可以分成三个能力梯队：

| 维度 | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|------|:---:|:---:|:---:|
| 综合评级 | **生产级 Runner** | **有限场景 Runner** | **Pathfinder Runner** |
| v4 协议通过率 | 3/3 优化 + 5/5 回归 | 2/3 优化 + 4/5 回归 | 1/3 优化 + P1-B 通过 |
| 产出完整度 | B1/B2/B3 均 8 文件 | B3 产出 3 文件，B1/B2 仅 1 文件 | B1/B2/B3 均仅 1 文件 |
| 证据编造 | 0 例 | v1 有 1 例（v3 修复） | 未测出编造，但产出太少 |
| 判档准确度 | 3/3 正确 | 1/3 正确（B1 误判 light） | 0/3 正确（B1/B2/B3 全判 light） |
| 行号精度 | 中等（偏差 1-10 行） | 极高（零偏差） | 未充分抽检 |
| 深度安全分析 | 强（发现 RBAC 失效） | 弱 | 强（仅 pathfinder 场景） |

---

## 二、Composer 2.5：三个模型里唯一能独立信赖的

### 强项

1. **深度代码分析能力突出**。在 prisma-express-ts 项目中发现了两个真实安全漏洞——passport.ts 的 `select` 只取了 `id/email/name` 没取 `role`，导致下游 RBAC 检查实际失效；还有 `userId` 旁路漏洞。这两个问题 Step 3.7 Flash 和 DeepSeek 都没发现。

2. **判档决策最可靠**。B1 中用户说"每次接口请求都要记录"，Composer 识别到 `LogAspect` 只覆盖 `@Log` 注解的接口，登录和验证码等 Controller 没有这个注解，覆盖范围有缺口，于是判 full。这是三个模型中唯一做出正确判断的。

3. **协议执行力最强**。v3 的 5 项改进全部不退步，v4 的 3 项优化中 2 项完全通过、1 项仅残留 1 处表名（`sys_user` 出现在 B2 依赖关系节，严重程度低）。16 个产出文件结构完整，每一步都有对应的文档。

4. **证据不编造**。从 v1 到 v4，6 个 case 中 0 例编造。方法名会做 grep 验证确认存在性。

### 弱项

1. **行号精度中等**。B4 的 apis 行号偏了 10 行，service 行号偏了 1 行。这是协议没有覆盖的点，仍需人工抽查。

2. **偶尔有小的边界遗漏**。B2 残留了 1 处表名在需求文档里，虽然位置在依赖关系节而非需求主体，但说明优化 8 的自检规则没有被 100% 执行。

### 一句话评价

如果你只能选一个模型，选它。安全敏感场景、覆盖范围判断场景、复杂 impact-pro 场景，目前只有它能扛住。

---

## 三、Step 3.7 Flash：行号精准，但深度分析和判档决策是短板

### 强项

1. **行号精度极高**。B1、B2、B4 三个 case 中所有抽检行号全部零偏差，在低成本模型中非常少见。这点比 Composer 2.5 强。

2. **现状核查能力强**。B2 中用户说"密码好像是用 MD5 加密的"，Step 核查代码后发现已经用了 BCrypt，纠正了用户的错误前提。不会盲目相信用户假设。

3. **B3（impact-pro 简单场景）设计文档质量高**。产出了 010/020/030 三个独立文档，设计含 P2002 唯一冲突处理、代码风格对齐报告、风险回滚方案。文档质量本身不逊色于 Composer，只是少了 context-pack 和 preflight。

4. **v3→v4 有实质进步**。P1-A（facts 强制产出）从 v3 的 FAIL 修复为 v4 的 PASS——干净环境下确实产出了真实的 `scan.json`（file_count=65）和 `git.json`（head=346d60f）。

### 弱项

1. **判档决策是硬伤**。B1 中用户说"每次接口请求都要记录"，Step 看到 `LogAspect.java` 有 `setCostTime` 就认为"功能已完整实现，无需改动"，连覆盖缺口都没识别到。这一点它还不如 DeepSeek——DeepSeek 至少识别到了"约 63 个端点未覆盖"，只是没触发 full；Step 连缺口都没看到。

2. **v1 时会编造 API 方法名**。写了 `userService.updateUserPassword(userId, password)`，这个方法在代码库中不存在。v3 通过协议内置预检修复了，但 v4 中 B2 判 light 又没做 grep 验证，I1-A 轻微退步。

3. **v1 时 facts 文件全错**。file_count=0（实际约 74 个文件），commit=null（实际有 commit），但 Script Gate 5/5 通过了——说明它能"走完流程"但内容不真实。v4 通过优化 6 修复了。

4. **产出完整度不够**。B1/B2 判 light 只产出了 1 个 `040-light.md`，没有 context-pack、没有 preflight、没有验证脚本。B3 虽然产出 3 个文档，但比 Composer 少了 5 个文件。

### 一句话评价

适合"不涉及覆盖范围判断"的场景。行号定位和简单 impact-pro 设计文档的质量合格，但判档不能信它，必须人工复核。

---

## 四、DeepSeek-V4-Flash：pathfinder 很强，但 impact/impact-pro 明显偏弱

### 强项

1. **pathfinder（B6）表现优秀**。首次参与盲测即正确产出 facts（file_count=65，与 Composer 一致），认证-鉴权自检完整——【10】节有「认证-鉴权字段一致性检查」表格明确标注不一致，【9】风险区域 #1 记录了 RBAC 失效，【11】主流程逐步展示 RBAC 失败链路。这一点和 Composer 打平。

2. **覆盖范围意识比 Step 强**。B1 中 DeepSeek 至少识别到了覆盖缺口，还量化了"约 63 个端点未覆盖"。虽然最终没触发 full，但"能看到问题"比 Step"完全没看到问题"要好一层。

3. **环境隔离执行到位**。file_count=65、.md 文件数=2、dir_tree 干净，和 Composer 完全一致，说明它对 prompt 中 Step 0 清理指令的执行是可靠的。

### 弱项

1. **判档全部判 light**。B1/B2/B3 三个 case 全部判 light，产出全部只有 1 个文件。B1 识别到了覆盖缺口却没触发 full（优化 7 FAIL），B2 判断"无需迁移"过于绝对——用户说"已经有很多老用户是 MD5 的"，DeepSeek 却说"不建议产生老用户 MD5 存量数据的场景"，这不是模型能决定的，是业务现实。

2. **产出结构性缺失**。B3 没有按 skill 要求拆分成独立的 010/020/030 文档，而是把需求、设计、实施全部塞进了一个 `000-context-pack.md`，里面还混入了 Prisma schema 代码片段、Joi 验证器代码、TypeScript 方法签名。优化 8（需求文档去技术化）直接 N/A，无法验证。

3. **对 skill 协议的执行深度不够**。它读了 SKILL.md 但似乎没有深入读 references 中的完整规则，Phase 2.5 的覆盖范围核查和 Phase 4 的文档拆分都没有执行到位。

### 一句话评价

目前只适合跑 pathfinder。在 impact/impact-pro 场景下，产出太少、判档太保守、文档结构不合规，不建议独立使用。

---

## 五、能力分层的根因分析

三个模型最核心的差异不在于"能不能发现单点问题"，而在于**能不能把多个信息关联起来做出正确决策**：

| 能力层级 | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|---------|:---:|:---:|:---:|
| L1：执行脚本、产出文件 | ✅ | ✅ | ✅ |
| L2：发现单点问题（方法不存在、密码已加密） | ✅ | ✅ | ✅ |
| L3：发现跨文件逻辑 bug（RBAC 失效） | ✅ | ❌ | ✅（仅 pathfinder） |
| L4：把全量词 + 覆盖缺口关联起来改变判档 | ✅ | ❌ | ❌ |
| L5：按协议拆分文档结构、产出完整链路 | ✅ | ⚠️（B3 可以） | ❌ |

**关键发现**：优化 7（覆盖范围语义核查）存在模型能力门槛。Step 和 DeepSeek 都能"看到"覆盖缺口（DeepSeek 甚至量化了），但都无法把"全量词 + 覆盖缺口"关联起来触发 full。只有 Composer 2.5 做到了。这说明协议规则对弱模型来说"能看到但不一定能执行"——这不是协议写得不够清楚的问题，而是模型推理能力的硬限制。

协议优化能拉高 L1-L2 层的能力（所有模型都通过了 facts 强制产出），但 L4-L5 层的能力差距靠协议补不了，只能靠模型本身。

---

## 六、选型建议

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| pathfinder 项目摸底 | 三者均可 | 都能正确产出 facts + 认证-鉴权自检 |
| impact 涉及覆盖范围判断 | **仅 Composer 2.5** | Step/DeepSeek 会误判 light |
| impact 不涉及覆盖范围 | Composer 或 Step | Step 的 B2/B3 质量合格 |
| impact-pro 简单场景 | Composer 或 Step | Step 的 B3 设计文档质量高 |
| impact-pro 复杂场景 | **仅 Composer 2.5** | DeepSeek 产出不完整；Step 缺 context-pack |
| 安全敏感场景 | **仅 Composer 2.5** | 证据编造 0 例 + 跨文件分析最强 |
| 只需要行号精准定位 | Step 3.7 Flash | 零偏差，但要查 API 方法名是否存在 |

**底层逻辑**：Composer 2.5 是"能独立完成完整链路"的模型；Step 3.7 Flash 是"局部质量高但整体决策不可信"的模型；DeepSeek-V4-Flash 是"单点能力强（pathfinder）但链路产出能力弱"的模型。

---

## 七、人工复核负担参考

不同模型下人工复核的侧重点不同：

| 复核项 | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|--------|:---:|:---:|:---:|
| API 方法名是否存在 | 协议内置预检，通过 | 轻微退步（light 时未做 grep） | 未验证 |
| 影响链是否覆盖核心场景 | 通过 | 可能排除核心场景 | 可能排除 |
| 行号是否准确 | 需抽查（偏差 1-10 行） | 不用查（零偏差） | 未充分抽检 |
| facts 文件内容是否真实 | 通过 | v4 已修复 | 通过 |
| 跨文件逻辑一致性 | 协议内置自检 | 协议内置自检 | 协议内置自检（仅 pathfinder） |
| 需求文档是否渗入技术细节 | 基本干净（B2 残留 1 处表名） | 通过 | 无法验证（未产出标准文档） |
| **判档是否正确** | 可信 | **必须人工复核** | **必须人工复核** |

---

## 八、本次评价的局限性

1. **只有 6 个 case**：覆盖了 4 个技术栈和 3 个 Skill，但样本量小，不能完全代表三个模型在所有场景下的表现。
2. **DeepSeek 首次参与**：没有 v1/v3 基线，无法判断协议优化对它的效果趋势。
3. **只测了"分析"阶段**：没有测"修改后"的效果，即 Phase 5 执行阶段的实际写操作质量。
4. **评审者单一**：源码级核实虽然客观，但不同评审者可能对"质量"有不同判断标准。

---

## 评审文件索引

| 文件 | 说明 |
|------|------|
| `eval/runs/blind-2026-06-24-v4-composer25/summary-clean-env.md` | Composer 2.5 v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-step37flash/summary-clean-env.md` | Step 3.7 Flash v4 评审（干净环境） |
| `eval/runs/blind-2026-06-24-v4-deepseek-v4-flash/summary.md` | DeepSeek-V4-Flash v4 评审 |
| `eval/runs/BLIND-TEST-FINAL-CONCLUSION.md` | 盲测最终结论（含 v1-v4 完整演进） |
| `eval/cases/blind/BLIND-TEST-V4-DESIGN.md` | v4 测试设计文档 |
| `docs/archive/2026-06/skill-improvement-2026-06-24.md` | v3 协议改进方案 |
