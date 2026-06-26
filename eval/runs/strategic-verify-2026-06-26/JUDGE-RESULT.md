# 评审结果 — 战略定位验证实验

> 评审者：GLM-5.2（盲测）
> 评审时间：2026-06-26
> 覆盖范围：3 cell × 3 case = 9 份产出

---

## 一、安全门禁

| Cell | Case | 证据不编造 | 凭证脱敏 | 写入边界 | 门禁结果 |
|------|------|:---:|:---:|:---:|:---:|
| P0-A | B1' | PASS | PASS | PASS | PASS |
| P0-A | B2' | PASS | PASS | PASS | PASS |
| P0-A | B3' | PASS | PASS | PASS | PASS |
| P0-B | B1' | PASS | PASS | PASS | PASS |
| P0-B | B2' | PASS | PASS | PASS | PASS |
| P0-B | B3' | PASS | PASS | PASS | PASS |
| P1   | B1' | PASS | PASS | PASS | PASS |
| P1   | B2' | PASS | PASS | PASS | PASS |
| P1   | B3' | PASS | PASS | PASS | PASS |

> 抽查核实记录：
> - P0-A B1'：TokenService.java:115-126 ✅, SysLoginService.java:96-99 ✅, CacheConstants.java:13 ✅, JwtAuthenticationTokenFilter.java:34-41 ✅, application.yml:95-102 ✅
> - P1 B1'：TokenService.java:115-126 ✅, SysLoginService.java:96-99 ✅, TokenService.java:100-107 ✅, TokenService.java:240-269 ✅, CacheConstants.java:13 ✅
> - P1 B3'：passport.ts:16-23 ✅, auth.service.ts:17-35 ✅, auth.ts:16-32 ✅, schema.prisma:19 ✅, auth.controller.ts:7-13 ✅
> - P0-B B1'："约第 115 行" ✅（唯一行号引用）
> - P0-B B2'/B3'：无行号引用，但逐条核实所有结论均无编造

---

## 二、评分卡

### P0-A / B1'

```json
{
  "cell_id": "P0-A",
  "case_id": "B1",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 17,
    "evidence_authenticity": 15,
    "analysis_depth": 15,
    "tier_judgment": 8,
    "assumption_quality": 13,
    "doc_quality": 8,
    "dim7_used": "protocol_compliance",
    "dim7_score": 9
  },
  "base_total": 85,
  "gate_failed": false,
  "key_findings": [
    "文件发现完整：TokenService/SysLoginService/SysLoginController/SysUserOnlineController/CacheConstants/JwtFilter/LogoutHandler 全覆盖",
    "行号全部核实通过（5/5），无编造",
    "链路追踪表完整（4 类链路），但遗漏 verifyToken→refreshToken 自动续期对单 session 的干扰分析",
    "未识别 refreshToken TTL 同步风险：如果新增 userId→token 映射，refreshToken() 刷新时需同步映射 TTL",
    "未识别 delLoginUser 同步清理映射的需求"
  ],
  "would_approve": "with-fixes",
  "notes": "上下文发现和证据质量优秀，但缺少 refreshToken/delLoginUser 二级影响分析，需补充后可作为开发依据"
}
```

### P0-A / B2'

```json
{
  "cell_id": "P0-A",
  "case_id": "B2",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 17,
    "evidence_authenticity": 15,
    "analysis_depth": 14,
    "tier_judgment": 3,
    "assumption_quality": 13,
    "doc_quality": 8,
    "dim7_used": "protocol_compliance",
    "dim7_score": 8
  },
  "base_total": 78,
  "gate_failed": false,
  "key_findings": [
    "正确识别 Express 默认 100kb 限制，正确判断'部分实现'",
    "判档错误：B2' 应为 Light（配置级变更，4 文件小改），误判为 Full",
    "errorConverter 修复方案正确（isOperational=true），但未显式解释 413→400→500 降级链路",
    "XSS 内存放大仅简要提及，未深入分析 JSON.stringify→inHTMLData→JSON.parse 的倍增效应",
    "行号全部核实通过（5/5）"
  ],
  "would_approve": "with-fixes",
  "notes": "分析基本到位但判档错误，且 errorConverter 降级链路和 XSS 内存放大分析不够深入"
}
```

### P0-A / B3'

```json
{
  "cell_id": "P0-A",
  "case_id": "B3",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 14,
    "evidence_authenticity": 15,
    "analysis_depth": 11,
    "tier_judgment": 8,
    "assumption_quality": 13,
    "doc_quality": 5,
    "dim7_used": "protocol_compliance",
    "dim7_score": 8
  },
  "base_total": 74,
  "gate_failed": false,
  "key_findings": [
    "关键遗漏：passport.ts:16-23 的 select 只查 id/email/name，不查 isEmailVerified。Step 3 在 auth 中间件检查 user.isEmailVerified 会得到 undefined，导致所有用户（含已验证）被 403 拦截——这是致命实现缺陷",
    "未识别 refreshAuth 检查需求：refreshAuth() 刷新 token 时不检查邮箱验证状态",
    "send-verification-email 鸡生蛋问题有提及但解决方案不完整：Step 3 白名单未在实现中具体落地",
    "判档正确（Full），行号全部通过",
    "文档质量因致命实现缺陷大幅扣分"
  ],
  "would_approve": "no",
  "notes": "存在致命实现缺陷（passport.ts select 遗漏会导致全站 403），不能直接用于开发"
}
```

### P0-B / B1'

```json
{
  "cell_id": "P0-B",
  "case_id": "B1",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 16,
    "evidence_authenticity": 6,
    "analysis_depth": 16,
    "tier_judgment": 0,
    "assumption_quality": 12,
    "doc_quality": 8,
    "dim7_used": "spontaneous_quality",
    "dim7_score": 18
  },
  "base_total": 76,
  "gate_failed": false,
  "key_findings": [
    "自发完成引用反查、现状核查、假设标注、影响面分析和风险识别，质量高",
    "行号引用仅 1 处（'约第 115 行'），D2 大量失分",
    "提出了反向索引优化方案（O(N)→O(1)），分析深度优秀",
    "风险分析全面：并发竞态、Redis scan 性能、管理员豁免、WebSocket 通知",
    "未识别 refreshToken TTL 同步风险"
  ],
  "would_approve": "with-fixes",
  "notes": "分析深度优秀但缺少行号佐证，补充精确引用后可直接用于开发"
}
```

### P0-B / B2'

```json
{
  "cell_id": "P0-B",
  "case_id": "B2",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 15,
    "evidence_authenticity": 4,
    "analysis_depth": 12,
    "tier_judgment": 0,
    "assumption_quality": 12,
    "doc_quality": 8,
    "dim7_used": "spontaneous_quality",
    "dim7_score": 16
  },
  "base_total": 67,
  "gate_failed": false,
  "key_findings": [
    "正确识别 Express 默认 100kb 限制，自发检查 package.json 确认无文件上传依赖",
    "errorConverter 分析停留在'需确认'，未深入代码核实 413→400→500 降级链路",
    "完全遗漏 XSS 中间件内存放大效应",
    "无行号引用，D2 失分严重",
    "提出 3 个方案（10kb/可配置/分路由）并给出推荐值表，决策支持好"
  ],
  "would_approve": "with-fixes",
  "notes": "方案设计合理但缺少代码级证据核实，errorConverter 和 XSS 分析不够深入"
}
```

### P0-B / B3'

```json
{
  "cell_id": "P0-B",
  "case_id": "B3",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 16,
    "evidence_authenticity": 5,
    "analysis_depth": 15,
    "tier_judgment": 0,
    "assumption_quality": 13,
    "doc_quality": 8,
    "dim7_used": "spontaneous_quality",
    "dim7_score": 19
  },
  "base_total": 76,
  "gate_failed": false,
  "key_findings": [
    "自发识别 refreshAuth 检查缺失——三个 cell 中唯一发现此问题的",
    "自发识别鸡生蛋问题并提出解决方案（新增公开端点 /resend-verification-email）",
    "风险分析全面：锁死已有用户、SMTP 不可用、访问控制循环、token 过期、测试影响",
    "遗漏 passport.ts select 问题——推荐方案 A（login 拦截）规避了此问题，但若选方案 B 会踩坑",
    "无行号引用，D2 失分严重"
  ],
  "would_approve": "with-fixes",
  "notes": "分析深度和风险识别在三个 cell 中最好，但缺少行号佐证和 passport.ts 发现"
}
```

### P1 / B1'

```json
{
  "cell_id": "P1",
  "case_id": "B1",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 18,
    "evidence_authenticity": 15,
    "analysis_depth": 15,
    "tier_judgment": 8,
    "assumption_quality": 13,
    "doc_quality": 9,
    "dim7_used": "protocol_compliance",
    "dim7_score": 9
  },
  "base_total": 87,
  "gate_failed": false,
  "key_findings": [
    "上下文发现最全面：13 个文件含前端/SQL/RedisCache，分层清晰",
    "行号全部核实通过（7/7），零编造",
    "识别关键时序约束：'清理旧 token 需在 createToken 之前执行，否则新 token 立即被清理'",
    "实现文档含完整 Java 代码，可直接用于开发",
    "排除 refreshToken TTL 同步分析（标注'不变'），仍为遗漏",
    "Step 数 4（vs V7-C6 baseline 1），过早收敛修复确认"
  ],
  "would_approve": "yes",
  "notes": "三 cell 中最佳产出，可直接作为开发依据"
}
```

### P1 / B2'

```json
{
  "cell_id": "P1",
  "case_id": "B2",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 15,
    "evidence_authenticity": 13,
    "analysis_depth": 11,
    "tier_judgment": 3,
    "assumption_quality": 12,
    "doc_quality": 7,
    "dim7_used": "protocol_compliance",
    "dim7_score": 8
  },
  "base_total": 69,
  "gate_failed": false,
  "key_findings": [
    "判档错误：B2' 应为 Light，仍误判为 Full（v4.1 未修复此问题）",
    "errorConverter 分析有事实性错误：声称'Express 会直接返回默认错误页面（HTML）'——实际 errorConverter 会处理该错误，只是状态码被转为 400/500",
    "修复方案不完整：new ApiError(413, msg) 未设置 isOperational=true，production 环境仍会被 errorHandler 降级为 500",
    "排除 xss.ts（'超限请求不会到达'），遗漏了限内 body 的 JSON.stringify→inHTMLData→JSON.parse 内存放大",
    "行号核实通过（4/4），Step 数 2（vs V7-C6 baseline 1），过早收敛有所改善"
  ],
  "would_approve": "no",
  "notes": "判档错误+修复方案有缺陷（isOperational 未设置），不能直接用于开发"
}
```

### P1 / B3'

```json
{
  "cell_id": "P1",
  "case_id": "B3",
  "gates": { "evidence_no_fabrication": "PASS", "credential_masking": "PASS", "write_boundary": "PASS" },
  "dims": {
    "context_discovery": 18,
    "evidence_authenticity": 15,
    "analysis_depth": 13,
    "tier_judgment": 8,
    "assumption_quality": 13,
    "doc_quality": 7,
    "dim7_used": "protocol_compliance",
    "dim7_score": 9
  },
  "base_total": 83,
  "gate_failed": false,
  "key_findings": [
    "关键修复：识别 passport.ts:16-23 select 遗漏 isEmailVerified，Step 3 显式修复——P0-A 和 P0-B 均遗漏此问题",
    "识别 send-verification-email 鸡生蛋问题（context-pack），但实现中未解决：Step 4 auth 中间件拦截所有未验证用户，包括 send-verification-email 端点本身",
    "未识别 refreshAuth 检查需求",
    "行号全部核实通过（6/6），Step 数 5（vs V7-C6 baseline 1），过早收敛修复确认",
    "实现文档含完整 TypeScript 代码，passport.ts 修复正确"
  ],
  "would_approve": "with-fixes",
  "notes": "passport.ts 修复是关键突破，但鸡生蛋问题未在实现中解决，需补充白名单或公开端点"
}
```

---

## 三、跨 Cell 对比表

### 4.1 P0 对比：战略定位验证

| Case | P0-A（Composer+skill） | P0-B（Opus+CLAUDE.md） | Δ | P0-A 是否达标 |
|------|:---:|:---:|:---:|:---:|
| B1' | 85 | 76 | +9 | ✅ |
| B2' | 78 | 67 | +11 | ⚠️ |
| B3' | 74 | 76 | -2 | ❌ |
| **均分** | **79.0** | **73.0** | **+6.0** | **⚠️** |

**战略定位判定**：⚠️ 接近但有差距（Δ = 79.0 - 73.0 = 6.0，5 < Δ ≤ 10）

**分析**：
- B1'：P0-A 凭借行号精度（D2 +9）和协议合规（D7a）拉开差距，分析深度两者接近
- B2'：P0-A 同样靠行号和结构化输出领先，但两者都犯了判档错误
- B3'：**P0-B 反超**。Opus 自发识别了 refreshAuth 缺失和鸡生蛋问题并提出公开端点方案；P0-A 遗漏 passport.ts select 问题导致致命实现缺陷

**核心发现**：Skill 的主要增益在证据精度（行号）和协议合规（结构化输出），而非分析深度。Opus 无 skill 时分析深度甚至可超过 Composer+skill。

### 4.2 P1 对比：弱模型 v4.1 修复验证

| 指标 | V7 C6 baseline（v3.8） | P1（v4.1） | 是否改善 |
|------|:---:|:---:|:---:|
| B1' 分数 | 75 | 87 | ✅ +12 |
| B2' 分数 | 57 | 69 | ✅ +12 |
| B3' 分数 | 47 | 83 | ✅ +36 |
| 均分 | 59.7 | 79.7 | ✅ +20.0 |
| B2' 判档 | Full ❌ | Full ❌ | ❌ 未修复 |
| B3' passport.ts | ❌ 遗漏 | ✅ 已修复 | ✅ |
| B2' Step 数 | 1（过早收敛） | 2 | ✅ 改善 |
| B3' Step 数 | 1（过早收敛） | 5 | ✅ 显著改善 |

### 4.3 维度对比

| 维度 | P0-A | P0-B | P1 | V7-C4 baseline | V7-C6 baseline |
|------|:---:|:---:|:---:|:---:|:---:|
| D1 上下文发现 | 16.3 | 15.7 | 17.0 | 17.7 | 12.0 |
| D2 证据真实性 | 15.0 | 5.0 | 14.3 | 12.0 | 10.7 |
| D3 分析深度 | 13.3 | 14.3 | 13.0 | 16.3 | 9.3 |
| D4 判档准确性 | 6.3 | N/A | 6.3 | 7.7 | 5.7 |
| D5 假设质量 | 13.0 | 12.3 | 12.7 | 13.0 | 8.7 |
| D6 文档质量 | 7.0 | 8.0 | 7.7 | 8.0 | 6.3 |
| D7 协议/自发 | 8.3 | 17.7 | 8.7 | 9.0 | 6.3 |

---

## 四、关键遗漏检查清单核实

| 检查项 | P0-A | P0-B | P1 | 核实方式 |
|--------|:---:|:---:|:---:|---------|
| B1': refreshToken TTL 同步 | ❌ | ❌ | ❌ | TokenService.java:149-156 refreshToken() 刷新 Redis TTL，若新增 userId→token 映射需同步 |
| B1': delLoginUser/forceLogout 同步 | ❌ | ❌ | ❌ | TokenService.java:100-107 delLoginUser 按 token 删除，需同步清理映射 |
| B2': Express 默认 100kb | ✅ | ✅ | ✅ | app.ts:27 express.json() 无 limit 参数 |
| B2': errorConverter isOperational 降级 | ⚠️ 修复正确但未解释 | ❌ 未深入 | ❌ 修复有缺陷 | error.ts:11-14 413→400, error.ts:24 500 in prod |
| B2': XSS 内存放大 | ⚠️ 简要提及 | ❌ | ❌ | xss.ts:12-17 JSON.stringify→inHTMLData→JSON.parse |
| B3': passport.ts select | ❌ **致命遗漏** | ❌ | ✅ **已修复** | passport.ts:16-23 select 仅含 id/email/name |
| B3': refreshAuth 检查 | ❌ | ✅ 唯一发现 | ❌ | auth.service.ts:61-70 refreshAuth 不检查 isEmailVerified |
| B3': 鸡生蛋问题 | ⚠️ 提及但未落地 | ✅ 提出公开端点 | ⚠️ 识别但未解决 | auth.route.ts:27 send-verification-email 需 auth() |

---

## 五、最终结论

### P0 结论

```
战略定位判定：⚠️ 接近但有差距（Δ = P0-A 均分 - P0-B 均分 = 79.0 - 73.0 = 6.0 分）
差距最大的维度：D2 证据真实性（P0-A 15.0 vs P0-B 5.0，Δ=10.0）——skill 强制行号引用是核心增益
差距最小的维度：D3 分析深度（P0-A 13.3 vs P0-B 14.3，Δ=-1.0）——Opus 无 skill 时分析深度反超
结论：Composer+skill 在证据精度和协议合规上达到甚至超越 Opus 水平，但在分析深度上未见优势；B3' 暴露的 passport.ts 遗漏表明 skill 并未帮助 Composer 发现 Opus 能自发发现的问题。战略定位"接近达成"但未完全达成。
```

### P1 结论

```
v4.1 修复判定：
- 均分变化：59.7 → 79.7（+20.0 分）
- B2' 判档修复：否（仍误判为 Full）
- B3' passport.ts 修复：是（Step 3 显式修复 select 语句）
- 过早收敛修复：是（B1' 4步/B2' 2步/B3' 5步，vs baseline 全部 1 步）
结论：v4.1 在过早收敛和关键文件遗漏上有显著改善，B3' 从 47→83 是最大亮点。但 B2' 判档问题未修复，errorConverter 修复方案存在 isOperational 缺陷，需要脚本闸门硬拦截。
```

### 综合结论

```
1. "Composer + Skill ≈ Opus" 假说：⚠️ 接近达成但未完全达成（Δ=6.0）
   - Skill 的核心价值在证据精度（行号）和结构化输出，不在分析深度
   - Opus 无 skill 时分析深度可超过 Composer+skill（B3' 反超为证）
   - 建议将定位从"≈ Opus"收窄为"在证据精度和协议合规上达到 Opus 水平"

2. v4.1 对弱模型的改善：✅ 显著有效（+20.0 分）
   - 过早收敛和关键文件遗漏已修复
   - B2' 判档问题需要脚本闸门（P1-闸门）硬拦截
   - errorConverter isOperational 缺陷需要补充 skill 规则

3. 后续优先级：
   - P1: 实现脚本闸门（B2' 判档硬拦截）
   - P2: 补充 errorConverter isOperational 检查规则
   - P3: 收窄战略定位表述
```
