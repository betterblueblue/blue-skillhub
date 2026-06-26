#!/usr/bin/env python3
"""Generate v8 composer-skill blind test documents for cell-C2."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TS = "2026-06-25 17:53:11"
GEN = "impact + Composer 2.5"

NAV_FULL = (
    "**000-context-pack.md** → [010-requirements.md](010-requirements.md) → "
    "[020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → "
    "[060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | "
    "[040-light.md](040-light.md) (light 模式) | [_active-state.md](_active-state.md)"
)
HDR = lambda title, nav=NAV_FULL: f"""# {title}

> 生成时间：{TS}  |  版本：1.0  |  生成者：{GEN}
>
> 导航：{nav}

"""

B1 = REPO / "eval/runs/blind-2026-06-25-v8/cell-C2/test-projects/ruoyi-vue/change-impact/B1"
B2 = REPO / "eval/runs/blind-2026-06-25-v8/cell-C2/test-projects/prisma-express-ts/change-impact/B2"
B3 = REPO / "eval/runs/blind-2026-06-25-v8/cell-C2/test-projects/prisma-express-ts/change-impact/B3"

for d in (B1, B2, B3):
    d.mkdir(parents=True, exist_ok=True)


def w(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO)}")


# ---------- B1 full ----------
w(B1 / "000-context-pack.md", HDR("B1 并发登录限制 Context Pack") + """## 1. 变更意图

- 用户原话：我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录
- 当前假设：「一个地方」指同一账号全局仅保留一个有效登录会话；后登录踢掉先登录；被踢设备后续业务请求失败
- 已识别技术栈：Java 17 + Spring Boot + Spring Security + JWT + Redis + Vue 2（RuoYi-Vue 3.9.2）
- 已加载技术栈规则：impact 内置 Java/Spring/MyBatis 规则
- 任务规模：大（安全架构变更，跨登录/鉴权/缓存链路）
- 成功标准：A 登录后 B 同账号登录，A 受保护接口失败；B 正常；反向互踢有效
- 长期目标模式：否
- 项目地图状态：非 Git（测试副本）

## 3. 分层上下文

| 层级 | 内容 | 结论 |
|------|------|------|
| L1 项目地图 | ruoyi-admin / ruoyi-framework / ruoyi-system / ruoyi-ui | RuoYi 标准分层 |
| L2 变更邻域 | TokenService、SysLoginService、SecurityConfig、JwtAuthenticationTokenFilter | 登录鉴权全链路 |
| L3 精准证据 | 见第 4 节 | 已核实 |

## 4. 相关文件和对象

| 文件/对象 | 类型 | 相关性 | 为什么相关 | 证据 |
|-----------|------|--------|------------|------|
| `ruoyi-framework/.../TokenService.java` | service | 3 直接修改候选 | token 创建/删除/刷新 | `createToken`/`delLoginUser` 【已核实: ruoyi-framework/src/main/java/com/ruoyi/framework/web/service/TokenService.java:100-156】 |
| `ruoyi-framework/.../SysLoginService.java` | service | 2 影响判断候选 | 登录入口 | `tokenService.createToken` 【已核实: ruoyi-framework/src/main/java/com/ruoyi/framework/web/service/SysLoginService.java:99】 |
| `ruoyi-framework/.../SecurityConfig.java` | config | 1 背景参考 | STATELESS 策略 | 【已核实: ruoyi-framework/src/main/java/com/ruoyi/framework/config/SecurityConfig.java:98】 |
| `ruoyi-framework/.../JwtAuthenticationTokenFilter.java` | config | 2 影响判断候选 | 请求鉴权 | `getLoginUser` 【已核实: ruoyi-framework/src/main/java/com/ruoyi/framework/security/filter/JwtAuthenticationTokenFilter.java:34-40】 |
| `ruoyi-common/.../CacheConstants.java` | config | 3 直接修改候选 | Redis 键前缀 | `LOGIN_TOKEN_KEY` 【已核实: ruoyi-common/src/main/java/com/ruoyi/common/constant/CacheConstants.java:13】 |
| `ruoyi-ui/src/utils/request.js` | ui | 2 影响判断候选 | 401 重登 UX | 【已核实: ruoyi-ui/src/utils/request.js:85-97】 |

## 5. 关键上下文

### 入口

- 登录：`POST /login` → `SysLoginService.login` → `TokenService.createToken`
- 鉴权：非匿名请求 → `JwtAuthenticationTokenFilter` → `TokenService.getLoginUser`
- 登出：`POST /logout` → `LogoutSuccessHandlerImpl` → `delLoginUser`

### 数据结构

- Redis：`login_tokens:{uuid}` → `LoginUser` 【已核实: TokenService.java:229-232】
- JWT claims 含 uuid（`LOGIN_USER_KEY`）【已核实: TokenService.java:122-125】

### 关键链路追踪

| 链路类型 | 入口 | 追踪路径 | 发现的二级影响 |
|---------|------|---------|--------------|
| 错误处理链 | 被踢设备带旧 token 请求 | JwtFilter → getLoginUser → Redis 无记录 → null → Security 未认证 → 401 | 前端 request.js 已有 401 弹窗重登，无需新错误码即可工作 【已核实: ruoyi-ui/src/utils/request.js:85-97】 |
| 中间件管线 | 登录写 Redis | SysLoginService → createToken → refreshToken | kickOut 必须在 refreshToken 前执行，否则旧 token 仍有效至 TTL 过期 |
| 数据流路径 | 用户→token 映射 | createToken 写映射 / refreshToken 续期 / delLoginUser 清映射 | 若 refreshToken 不同步续期 `login_user_token:{userId}`，映射可能先于 token 过期导致误踢 【待核实: 需 Step 2 同步 TTL】 |

## 6. 引用检查结果

| 分类 | 文件/对象 | 影响 | 处理方式 |
|------|-----------|------|----------|
| 必须同步修改 | `TokenService.createToken` | 不踢旧 token 则多设备并存 | Step 2 |
| 必须同步修改 | `TokenService.delLoginUser` | 登出需清用户映射 | Step 2 |
| 需要用户决策 | 被踢提示文案 | 复用 401 或专用文案 | [假设] 复用现有 401 |
| 需要用户决策 | admin 是否豁免 | 角色权限刷新跳过 admin | [假设] 不豁免，统一单会话 |
| 只需验证 | `JwtAuthenticationTokenFilter` | Redis 删除后自然失效 | 手工互踢验收 |
| 暂不纳入 | Quartz `concurrent` 字段 | 与会话无关 | 排除 |

## 7. 已确认事实

- STATELESS JWT + Redis 缓存 LoginUser，无 Spring Session 并发控制 【已核实: SecurityConfig.java:98】
- 每次登录新建 uuid 写入 Redis，不清理同用户旧 token 【已核实: TokenService.java:115-125】
- 全库无 `maximumSessions` / SessionRegistry 实现

## 8. 待确认问题

- [ ] 被踢提示是否区分「过期」— [假设] 不区分，复用 401
- [ ] admin 是否豁免 — [假设] 不豁免

## 9. 暂不纳入范围

| 文件/对象 | 排除原因 |
|-----------|----------|
| `ruoyi-quartz/**` | 任务 concurrent 字段与会话无关 |
""")

w(B1 / "010-requirements.md", HDR("B1 并发登录限制 需求文档", "010-requirements.md** → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [040-light.md](040-light.md) (light 模式) | [_active-state.md](_active-state.md)") + """## 1. 变更背景

同一账号可在多个终端同时保持有效登录，存在账号共享与会话劫持持续访问风险。需收紧为同一账号同一时刻仅允许一个有效登录会话，后登录顶替先登录。

## 2. 需求描述

实现单账号单会话（互踢）：用户在 B 设备登录成功后，A 设备已有会话立即失效；被踢设备再次调用需登录的业务功能时应被拒绝。

## 2.1 当前假设与歧义

- 当前假设：「一个地方」= 全局唯一有效会话，不区分 Web/App/接口客户端
- 可能歧义：是否允许多子系统并存 — 本系统为单一 RuoYi 后台，按全局唯一理解
- 更简单的方案：无 — 现有无状态多 token 模型本身不支持互踢
- 任务规模：大
- 成功标准：双设备互踢后旧设备无法继续操作，新设备正常

## 2.2 模糊点处理清单

| 模糊点（用户原话） | 处理方式 | 结果 |
|-------------------|---------|------|
| 「一个地方」具体范围 | `[假设]` — 依据：常见单点登录语义 | 全局唯一会话，不区分终端类型 |
| 被踢后提示方式 | `[假设]` — 依据：现有 401 重登流程 | 复用现有未认证/会话过期提示，不新增专用文案 |
| 管理员是否豁免 | `[假设]` — 依据：安全一致性 | 所有账号统一单会话，含管理员 |

## 2.3 本次做什么、不做什么

- **本次做**：单会话互踢、被踢后无法继续访问、主动登出正常
- **本次不做**：HttpSession 改造、可配置 N 设备在线、WebSocket 实时推送被踢

## 2.4 非功能需求

- **安全**：旧 token 被踢后不可继续访问
- **可用性**：单设备登录/登出/刷新不受影响
- **性能**：登录踢人 Redis 操作毫秒级

## 2.5 未确认项

- [ ] 被踢专用文案 — [假设] 已按复用 401 处理
- [ ] admin 豁免 — [假设] 已按不豁免处理

## 4. 验收标准

- [ ] A 登录后 B 同账号登录，A 调用需登录功能失败
- [ ] B 登录后业务功能正常
- [ ] A 再登录则 B 被踢、A 正常
- [ ] 主动登出仅影响当前设备
- [ ] 单设备登录→操作→登出全流程正常

## 5. 依赖关系

- 依赖 Redis 在线 token 缓存
- 前置条件：登录链路正常
""")

w(B1 / "020-design.md", HDR("B1 并发登录限制 设计文档", "[010-requirements.md](010-requirements.md) → **020-design.md** → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md)") + """## 1. 现状分析

RuoYi 使用 STATELESS + JWT + Redis 缓存 LoginUser【已核实: SecurityConfig.java:98】。`createToken` 每次生成新 uuid 写入 `login_tokens:{uuid}`，不删除同用户旧 token【已核实: TokenService.java:115-125】— **并发登录限制未实现**。

## 2. 方案概述

增加 Redis 映射 `login_user_token:{userId}` → 当前有效 uuid；登录前 kickOut 旧 token。

## 3. 详细设计

### 3.1 Redis 键

| 键 | 值 | TTL |
|----|-----|-----|
| `login_tokens:{uuid}` | LoginUser | token.expireTime（现有） |
| `login_user_token:{userId}` | uuid 字符串 | 与 token 同步（新增） |

### 3.2 TokenService 变更

- 新增 `kickOutPreviousSessions(userId)`：读映射 → delLoginUser(oldUuid) → 删映射
- `createToken`：kickOut → 新 uuid → refreshToken → 写映射
- `delLoginUser`：删 token 后若映射指向该 uuid 则清映射
- `refreshToken`：同步续期 `login_user_token:{userId}`

### 3.3 判档决策表

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|--------------|---------------|------|---------|
| 只能在一个地方登录 | 无用户级仲裁 | 缺 kickOut + 映射 | full |
| 好几个地方登录 | 多 token 并存 | 每登录独立 uuid | full |

## 4. 代码风格报告

```java
public void refreshToken(LoginUser loginUser)
{
    loginUser.setLoginTime(System.currentTimeMillis());
    loginUser.setExpireTime(loginUser.getLoginTime() + expireTime * MILLIS_MINUTE);
    String userKey = getTokenKey(loginUser.getToken());
    redisCache.setCacheObject(userKey, loginUser, expireTime, TimeUnit.MINUTES);
}
```

来源：`ruoyi-framework/src/main/java/com/ruoyi/framework/web/service/TokenService.java:149-156`

## 5. 未确认项

- admin 豁免 — [假设] 不豁免
- 被踢专用文案 — [假设] 复用 401
""")

w(B1 / "030-implementation.md", HDR("B1 并发登录限制 实施文档", "[010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → **030-implementation.md** → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md)") + """## 实施步骤总览

| Step | 操作 | 文件 | 验证 |
|------|------|------|------|
| 1 | 新增 Redis 键常量 | `CacheConstants.java` | 编译 |
| 2 | kickOut + 映射逻辑 | `TokenService.java` | 编译 + 手工互踢 |

## Step 1：CacheConstants

在 `LOGIN_TOKEN_KEY` 后新增 `LOGIN_USER_TOKEN_KEY = "login_user_token:"`。

## Step 2：TokenService

### 2.1 新增 `kickOutPreviousSessions(Long userId)`

读 `login_user_token:{userId}` → 若存在则 `delLoginUser(oldUuid)` → 删映射键。

### 2.2 修改 `createToken`

在 `IdUtils.fastUUID()` **之前**调用 `kickOutPreviousSessions`；在 `refreshToken` **之后**写映射。

### 2.3 修改 `delLoginUser`

删 token 前先 get LoginUser；删 token 后若映射 uuid 匹配则清映射。

### 2.4 修改 `refreshToken`

同步 `setCacheObject` 到 `login_user_token:{userId}`。

> **方法名预检**：`delLoginUser`、`refreshToken`、`getTokenKey`、`redisCache.*` 均已存在于 TokenService【已核实: TokenService.java:100-156】

## 验证

```bash
cd ruoyi-vue && mvn compile -pl ruoyi-admin -am -DskipTests
```

手工：双浏览器同账号互踢验收。

## 改动完整性自检

| 验收标准 | 对应 Step |
|---------|----------|
| A 被 B 踢 | Step 2 kickOut |
| B 正常 | Step 2 createToken |
| 反向互踢 | Step 2 |
| 主动登出 | Step 2 delLoginUser |
| 单设备正常 | Step 2 不破坏现有流程 |

## 方法名验证标记

- [x] Step 2 所调已有方法均已 grep 核实
""")

w(B1 / "_active-state.md", HDR("B1 并发登录限制 活跃状态").replace("Context Pack", "活跃状态") + """## 状态头

- 更新时间：""" + TS + """
- skill：impact
- 需求目录：`change-impact/B1/`
- 当前阶段：Phase 4 完成
- 模式：full
- 执行方式：auto（盲测自主产出）
- 待执行 Step：none

## 文档状态

| 文档 | 状态 |
| --- | --- |
| 000-context-pack.md | 草稿 |
| 010-requirements.md | 草稿 |
| 020-design.md | 草稿 |
| 030-implementation.md | 草稿 |
""")

# ---------- B2 light ----------
w(B2 / "040-light.md", HDR("B2 API 请求体大小限制 影响摘要", "[010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | **040-light.md** (light 模式) | [_active-state.md](_active-state.md)") + """## 变更概述

为 API 增加显式请求体大小限制，防止超大 payload 拖垮服务；并修复 production 下 413 被错误降级为 500 的问题。

## 影响范围

### 分析依据

| 类型 | 证据 | 结论 |
|------|------|------|
| 已确认 | `src/app.ts:27-30` | json/urlencoded 未设 limit，Express 默认 100kb |
| 已确认 | `src/middlewares/error.ts:8-27` | PayloadTooLarge 转 ApiError 时 isOperational=false，production 变 500 |
| 已确认 | `src/middlewares/xss.ts:24-26` | body 解析后再 JSON 序列化，大 body 有内存放大风险 |

### 代码

- `src/app.ts`：为 `express.json` / `express.urlencoded` 增加 `limit`
- `src/middlewares/error.ts`：识别 `entity.too.large` / statusCode 413，返回 operational 413

### 接口

- 超限请求返回 HTTP 413，message 明确提示请求体过大
- 不破坏正常小 body 请求

## 模糊点处理（[假设]）

| 模糊点 | 结果 |
|--------|------|
| 限制多大 | `[假设]` JSON/urlencoded 均为 **1mb** |
| 文件上传 | `[假设]` 本次不做 multipart 上传限制（项目无 upload 路由） |

## 未确认项

- [ ] 1mb 是否满足业务 — [假设] 已按常见 API 默认

## 回滚方案

还原 `src/app.ts` 与 `src/middlewares/error.ts` 修改。

## 实施步骤

1. `app.ts`：`express.json({ limit: '1mb' })`，`express.urlencoded({ extended: true, limit: '1mb' })`
2. `error.ts`：在 errorConverter 中若 `err.type === 'entity.too.large'` 或 `err.statusCode === 413`，构造 `new ApiError(413, 'Request entity too large', true)`

## 验证

```bash
cd prisma-express-ts && npm run build
```

- 发送 >1mb JSON → 413（production 环境亦应为 413 非 500）
- 正常小 body → 200/201

## Out of Scope

- multipart 文件上传（无 multer 路由）
- nginx client_max_body_size
- env 可配置化（可选后续）

## 关键链路深度检查

- [x] **错误处理链**：已识别 errorConverter 将 413 标为非 operational → production 500；Step 2 修复
- [x] **中间件管线**：limit 在 xss 之前生效，超限不会进入 xss 放大路径
- [x] **数据流路径**：仅影响 body 解析阶段，不涉及 DB

## Agent 自检

### 现状核查结果

- 现状核查：**部分实现**（隐式 100kb 默认，无业务级配置，413 响应不正确）
- 缺口：显式 limit、413 正确返回

### 定级证据

- 建议档位：**light**
- 允许 light 的证据：局部 2 文件改动，无 schema/API 契约破坏
- 触发 full 的证据：无
- 未确认项：limit 数值 — [假设] 1mb

### 判档决策表

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|--------------|---------------|------|---------|
| 请求体没有限制 | Express 隐式 100kb | 无显式配置、无友好 413 | light |
| 超大东西服务器差点挂了 | 100kb 仍可能经 xss 放大 | 需显式 limit + 413 修复 | light |
""")

w(B2 / "_active-state.md", f"""# B2 活跃状态

> 生成时间：{TS}

- skill：impact
- 模式：light
- 阶段：Phase 4 完成
""")

# ---------- B3 full ----------
w(B3 / "000-context-pack.md", HDR("B3 邮箱验证强制检查 Context Pack") + """## 1. 变更意图

- 用户原话：注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧
- 当前假设：注册后自动发验证邮件；未验证用户不能调用业务 API，但可登录/刷新 token 以完成验证流程
- 已识别技术栈：Node.js + Express 4 + Prisma + PostgreSQL + JWT
- 已加载技术栈规则：`profiles/node-express-prisma.md`
- 任务规模：中
- 成功标准：未验证用户无法访问受保护业务接口；验证后可正常使用

## 4. 相关文件

| 文件 | 相关性 | 证据 |
|------|--------|------|
| `prisma/schema.prisma` | 3 | `isEmailVerified @default(false)` 【已核实: prisma/schema.prisma:20】 |
| `src/controllers/auth.controller.ts` | 3 | 注册发 token 不发邮件 【已核实: auth.controller.ts:7-12】 |
| `src/services/auth.service.ts` | 3 | 登录查字段不检查 【已核实: auth.service.ts:27-35】 |
| `src/middlewares/auth.ts` | 3 | 无 isEmailVerified 检查 【已核实: auth.ts:15-31】 |
| `src/config/passport.ts` | 3 | select 缺 role/isEmailVerified 【已核实: passport.ts:16-23】 |
| `src/routes/v1/auth.route.ts` | 2 | verify/send 路由 【已核实: auth.route.ts:27-28】 |

## 5. 关键链路追踪

| 链路类型 | 入口 | 追踪路径 | 二级影响 |
|---------|------|---------|---------|
| 数据流 | POST /register | controller → createUser → generateAuthTokens | 注册即拿 token，绕过验证 |
| 错误处理链 | 未验证访问 /v1/users | auth middleware | 需返回 403 而非 401，且 passport 必须先加载 isEmailVerified |
| 中间件管线 | auth() | passport jwt → verifyCallback | 白名单需放行 verify-email、send-verification-email、refresh-tokens |

## 7. 已确认事实

- verifyEmail 逻辑完整【已核实: auth.service.ts:102-115】
- 注册不自动发验证邮件【已核实: auth.controller.ts:7-12】
- refreshAuth 不检查验证状态【已核实: auth.service.ts:62-70】
""")

w(B3 / "010-requirements.md", HDR("B3 邮箱验证强制检查 需求文档", "010-requirements.md** → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [040-light.md](040-light.md) (light 模式) | [_active-state.md](_active-state.md)") + """## 1. 变更背景

系统已有邮箱验证能力，但用户注册后即使未完成邮箱验证仍可正常使用业务功能，不符合安全预期。

## 2. 需求描述

用户注册后应收到验证邮件；在完成邮箱验证之前，不能使用需要登录的业务功能；验证完成后恢复正常访问。

## 2.2 模糊点处理清单

| 模糊点 | 处理方式 | 结果 |
|--------|---------|------|
| 注册是否自动发邮件 | `[假设]` — 用户认为「注册时有发」 | 注册成功后自动发送验证邮件 |
| 未验证能否登录 | `[假设]` — 需完成验证流程 | 允许登录拿 token，但业务 API 拦截 |
| 拦截范围 | `[假设]` — 最小可用闭环 | 白名单：verify-email、send-verification-email、refresh-tokens、logout |

## 2.3 本次做什么、不做什么

- **本次做**：注册自动发验证邮件、未验证拦截业务 API、refresh 时检查验证状态
- **本次不做**：改造为注册后直接 403 禁止登录、历史用户批量验证

## 4. 验收标准

- [ ] 注册后用户收到验证邮件（或 token 生成逻辑被调用）
- [ ] 未验证用户调用受保护业务接口被拒绝并提示需验证邮箱
- [ ] 点击验证链接后业务接口可正常访问
- [ ] 已验证用户不受影响
- [ ] 未验证用户仍可调用验证相关接口完成验证

## 5. 依赖关系

- 依赖邮件发送配置（开发环境可 mock）
- 依赖现有 VERIFY_EMAIL token 机制
""")

w(B3 / "020-design.md", HDR("B3 邮箱验证强制检查 设计文档", "[010-requirements.md](010-requirements.md) → **020-design.md** → [030-implementation.md](030-implementation.md)") + """## 1. 现状

- Schema 有 `isEmailVerified` 默认 false【已核实: prisma/schema.prisma:20】
- 验证 API 完整但注册不触发、鉴权不检查

## 2. 方案

1. **注册**：createUser 后 `generateVerifyEmailToken` + `sendVerificationEmail`（仍返回 tokens 以便前端引导）
2. **passport.ts**：select 增加 `role: true, isEmailVerified: true`
3. **auth.ts**：verifyCallback 中若 `!user.isEmailVerified` 且非白名单路径 → 403
4. **refreshAuth**：generateAuthTokens 前检查 isEmailVerified
5. **白名单**：`/v1/auth/verify-email`、`/v1/auth/send-verification-email`、`/v1/auth/refresh-tokens`、`/v1/auth/logout`

### 判档决策表

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|--------------|---------------|------|---------|
| 不验证也能用 | 登录+鉴权均不检查 | 执行层缺失 | full |
| 注册发验证邮件 | 仅手动 API | 注册未自动触发 | full |

## 3. 代码风格

```typescript
const login = catchAsync(async (req, res) => {
  const { email, password } = req.body;
  const user = await authService.loginUserWithEmailAndPassword(email, password);
  const tokens = await tokenService.generateAuthTokens(user);
  res.send({ user, tokens });
});
```

来源：`src/controllers/auth.controller.ts:15-19`
""")

w(B3 / "030-implementation.md", HDR("B3 邮箱验证强制检查 实施文档", "[010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → **030-implementation.md**") + """## Step 总览

| Step | 文件 | 内容 |
|------|------|------|
| 1 | `src/config/passport.ts` | select 增加 role, isEmailVerified |
| 2 | `src/middlewares/auth.ts` | 未验证拦截 + 白名单 |
| 3 | `src/controllers/auth.controller.ts` | 注册后自动发验证邮件 |
| 4 | `src/services/auth.service.ts` | refreshAuth 检查 isEmailVerified |
| 5 | `tests/integration/auth.test.ts` | 更新/新增未验证拦截用例 |

## Step 1：passport.ts

```typescript
select: { id: true, email: true, name: true, role: true, isEmailVerified: true }
```

## Step 2：auth.ts

在 `req.user = user` 后：

```typescript
const whitelist = ['/v1/auth/verify-email', '/v1/auth/send-verification-email',
  '/v1/auth/refresh-tokens', '/v1/auth/logout'];
if (!user.isEmailVerified && !whitelist.some(p => req.originalUrl.startsWith(p))) {
  return reject(new ApiError(httpStatus.FORBIDDEN, 'Please verify your email'));
}
```

## Step 3：auth.controller.ts register

createUser 后：

```typescript
const verifyEmailToken = await tokenService.generateVerifyEmailToken(user);
await emailService.sendVerificationEmail(user.email, verifyEmailToken);
```

## Step 4：auth.service.ts refreshAuth

generateAuthTokens 前：

```typescript
const user = await userService.getUserById(userId, ['id', 'isEmailVerified']);
if (!user?.isEmailVerified) {
  throw new ApiError(httpStatus.FORBIDDEN, 'Please verify your email');
}
```

> **方法名预检**：`generateVerifyEmailToken`【已核实: token.service.ts】、`sendVerificationEmail`【已核实: email.service.ts:52】、`getUserById`【已核实: user.service.ts】

## 改动完整性自检

| 验收标准 | Step |
|---------|------|
| 注册发邮件 | Step 3 |
| 未验证拦截业务 API | Step 2 |
| 验证后可用 | Step 2 条件放行 |
| 已验证不受影响 | Step 2 |
| 验证接口可用 | Step 2 白名单 |
| refresh 不绕过 | Step 4 |

## 方法名验证标记

- [x] 已有方法均已 grep 核实
""")

w(B3 / "_active-state.md", f"""# B3 活跃状态

> 生成时间：{TS}
- skill：impact
- 模式：full
- 阶段：Phase 4 完成
""")

print("Done generating documents.")
