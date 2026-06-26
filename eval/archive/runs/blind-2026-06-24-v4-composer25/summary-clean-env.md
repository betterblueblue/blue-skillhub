# Composer 2.5 盲测 v4 评审报告（干净环境）

> 日期：2026-06-25
> 评审方式：源码级检查（实际文件内容 + facts JSON + 路径验证）
> 环境：v4 修正 prompt（Step 0 清理 + 默认路径 + 归档）

---

## 环境隔离验证

| 指标 | v4 初版（污染环境） | v4 修正（干净环境） | 结论 |
|------|-------------------|-------------------|------|
| scan.json file_count | 106 | **65** | ✅ 修复生效，不再计入 change-impact/ 产出 |
| .md 文件数 | 31 | **2** | ✅ 仅 README.md + CONTRIBUTING.md |
| dir_tree 含 change-impact/ | 是 | **否** | ✅ 目录树干净 |
| facts 路径 | 自定义子目录（V6 假 PASS） | **默认路径**（V6 真 PASS） | ✅ pf_validate.py 能正确找到 |

---

## 三项优化验证

### 优化 6（P1-A）— B6 facts 文件强制：✅ PASS

- `scan.json`：`file_count: 65`，`dir_tree` 含根 `/`，`budget_tier: "small"` — 内容真实
- `git.json`：`head_short: "346d60f"`，`toplevel` 指向 prisma-express-ts — 一致
- 地图【0】节正确引用 facts：「预算档位: 小仓(tracked 文件 65)」
- **与 v3 对比**：不退步。v3 已 PASS，v4 干净环境下仍然 PASS，且 file_count 更准确

### 优化 7（I2-A）— B1 覆盖范围语义核查：✅ PASS

context-pack 明确识别了覆盖范围缺口：

- 第 21 行：「差距证据：`LogAspect` 切点仅 `@annotation(controllerLog)`，登录/验证码等 Controller 无 `@Log` 注解」
- 第 94 行：「**GAP**：用户要全部 API，LogAspect 仅覆盖 @Log 方法，不含 login/captcha」
- 判档：**full**（正确，因覆盖范围缺口触发 full）
- 引用检查：CaptchaController 无 @Log 被列为「影响判断候选」

**与 v3 对比**：不退步。v3 已识别覆盖缺口并判 full，v4 保持。

### 优化 8（需求文档边界）：2/3 PASS + 1/3 PARTIAL

| Case | 结果 | 检查详情 |
|------|------|---------|
| B1 | ✅ PASS | 纯业务语言，无表名/类名/文件路径/代码片段/字段类型 |
| B2 | ⚠️ PARTIAL | 第 68 行「前置条件：可写 `sys_user` 表」— `sys_user` 是表名，不应出现。其余部分干净 |
| B3 | ✅ PASS | 纯业务语言，无技术细节渗入 |

**B2 瑕疵详情**：
- 位置：`010-requirements.md` 第 68 行，依赖关系 → 前置条件
- 内容：「可写 sys_user 表；具备构造 MD5 测试账号的手段」
- 严重程度：低（在依赖关系节，非需求主体；但 `sys_user` 是设计文档中明确列为不应出现的表名）
- 修复建议：改为「可写用户数据表」或移到 `020-design.md`

**与 v3 对比**：改进。v3 中 B1/B2/B3 都有技术细节渗入；v4 中 B1/B3 已完全干净，B2 仅残留 1 处表名。

---

## v3 五项回归检查

| 检查项 | Case | v3 结果 | v4 结果 | 详情 |
|--------|------|---------|---------|------|
| P1-A（facts 强制） | B6 | ✅ | ✅ | facts 存在且内容真实 |
| P1-B（认证-鉴权自检） | B6 | ✅ | ✅ | 风险 #1 明确标注 passport select 缺 role；【10】节有完整 authn/authz 链路 + Mermaid 流程图展示 gap |
| I1-A（方法名验证） | B2 | ✅ | ✅ | grep 验证 resetPwd/resetUserPwd/encryptPassword/matchesPassword；确认 updateUserPassword 不存在 |
| I2-A（覆盖范围核查） | B1 | ✅ | ✅ | 识别 LogAspect 仅覆盖 @Log，判 full |
| IP1-A（Prisma 项目分析） | B3 | ✅ | ✅ | 正确识别 schema/validation/controller/service 全链路；admin 接口正确排除 |

**回归结论**：5/5 不退步。

---

## 整体判定

| 维度 | 判定 |
|------|------|
| 优化 6（P1-A） | ✅ PASS |
| 优化 7（I2-A） | ✅ PASS |
| 优化 8 | ⚠️ 2/3 PASS + 1/3 PARTIAL（B2 残留 1 处表名） |
| v3 五项回归 | ✅ 5/5 不退步 |
| 环境隔离 | ✅ 修复生效（file_count 106→65，dir_tree 干净） |

**总结**：Composer 2.5 在干净环境下维持了 Production-grade Runner 水准。环境隔离修复使得 P1-A 的验证从"可能假 PASS"变为"确认真 PASS"。优化 8 在 B2 有一处轻微退步（表名残留），但整体比 v3 明显改善。

**与 v4 初版（污染环境）的对比**：核心结论不变（Composer 2.5 仍是 5/5 水准），但 P1-A 的 PASS 现在是可信的，不再依赖旧 facts 残留。
