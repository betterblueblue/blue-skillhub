# Subagent A Prompt — 跑 impact skill 真行为

你是 Claude，正在跑 /impact skill。你的任务：**在真 Java 项目上严格按 SKILL.md Phase 1-5 走完**，
真产出 change-impact 文档 + 真改项目代码。**用户将根据你的产出判定 skill 是否真的能干活**。

---

## 1. 硬性要求（违反任何一条 = 任务失败）

1. **必须使用工具**：Read / Grep / Glob / Edit / Write / Bash。不允许纯文字"我会..."
2. **必须按 SKILL.md Phase 1-5 顺序走**：不允许跳过 Phase 2.5、3.5、4
3. **必须真改项目代码**：用 Edit/Write 落到 `<WORKDIR_PATH>`，至少 3 个文件
4. **必须真写 change-impact 文档**：用 Write 落到 `<ACTUAL_DIR>/change-impact/<feature-name>/`
5. **禁止占位符**：文档中**不能**出现 `<file path>` / `<your code>` / `TODO` / `// implement later` / `...` 占位
6. **必须真实文件路径**：引用的所有 file:line 必须能在 workdir 中定位
7. **必须真代码片段**：引用的所有代码必须从 workdir 中 Read 出来，不是脑补
8. **必须使用 workdir 的现有模式**：新代码风格要跟项目一致（用项目已有的 @Excel 注解、Service/Mapper 命名约定、Controller 注解等）

## 1.5 铁律级硬约束（来自评审反馈，违反 = 任务失败）

### A. **凭证脱敏**（铁律 #7 强化）
- 文档中出现的 **所有** password / secret / token / connection string password / API key
  必须脱敏为 `***` 或 `$PASSWORD` / `$SECRET` 形式
- **禁止**写"admin123" / "secret123" / "test-token" 等字面量
- 包括：default value、示例、curl 命令、shell 脚本默认参数、test fixture
- 唯一例外：完全无凭证的代码段可省略
- 反例：`PASSWORD='admin123'` ❌ → `PASSWORD='$PASSWORD'` 或 `PASSWORD='***'` ✅

### B. **单元测试强制**（铁律 #6 行为准则强化）
- 新增**任何**含以下特征的代码必须配 JUnit 测试：
  - Service 接口（业务逻辑）
  - 状态机（enum + 状态转换）
  - 异步边界（@Async / 线程池 / Future）
  - SQL 注入面（new mapper method）
  - 异常处理路径
- 测试文件位置：`ruoyi-system/src/test/java/com/ruoyi/system/<package>/`
- 用项目已有测试框架（JUnit 5 + Mockito）
- 必须覆盖：核心路径 + 至少 1 个异常路径
- 即使 fixture 没有 src/test 目录，**必须新建**
- 评审 FAIL 条件：缺测试 OR 测试仅空壳 OR 测试不覆盖核心逻辑

### C. **可执行性保证**（占位符零容忍）
- 任何 shell 脚本必须**可直跑**（不修改任何 token 也能跑通 or 给出明确环境变量读取方式）
- 任何 SQL 脚本必须可直跑（不修改任何 placeholder）
- 任何 mock value 必须有完整默认值（不能是 `XXXXX` / `TO_BE_FILLED`）
- 反例：`curl -H "Authorization: Bearer $TOKEN_NO_PERMISSION"` 后面跟 `# 把 NO_PERMISSION 替换为真实 token` ❌
- 正例：`curl -H "Authorization: Bearer \${TOKEN:-test-token-please-override}"` ✅（有合理 default）

### D. **Spring @Async 自我调用陷阱**（来自 S1 第二次评审发现）
- **禁止**把 @Async 方法放在会被同 Bean 内其他方法（或 Controller）直接调用的位置
- Spring @Async 走 AOP 代理，**同 Bean 内的 self-invocation 绕过代理，@Async 实际同步执行**
- 错误模式：`userExportTask.runAsync()` 在 Controller 中直接调，`runAsync` 注解了 @Async → 死代码
- 正确做法（二选一）：
  - **拆 Bean**：新建 `UserExportTaskLauncher` 类含 @Async 方法，Controller 调 launcher
  - **Self-inject**：同 Bean 内 `@Lazy @Autowired private UserExportTask self;`，通过 `self.runAsync()` 走代理
- 评审 FAIL 条件：@Async 注解的方法被同 Bean 内的非 @Async 方法（或同包内 Controller）直接调用
- 修完后必须在 090-execution-record.md 显式说明本次如何规避 self-invocation

---

## 2. 输入参数

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `<WORKDIR_PATH>` | 工作目录（fixture 的拷贝，**安全可改**） | `E:\agent\blue-skillhub\skills\impact\tests\e2e\workdirs\001-add-user-export` |
| `<ACTUAL_DIR>` | change-impact 文档输出根 | `E:\agent\blue-skillhub\skills\impact\tests\e2e\scenarios\001-add-user-export\actual` |
| `<USER_QUERY>` | 用户原始请求 | "用户列表页要能导出 Excel..." |
| `<SKILL_MD_PATH>` | skill 完整文档 | `E:\agent\blue-skillhub\skills\impact\SKILL.md` |
| `<FIXTURE_PROJECT_NAME>` | 项目名 | RuoYi-Vue |

---

## 3. SKILL.md

**先去读** `<SKILL_MD_PATH>` 全文。按里面的 Phase 1-5 流程走。

下面是 Phase 摘要（**仅供你定位，详细规则看 references/ 子文件**）：

- **Phase 1**: 意图捕获 — 假设/歧义/任务规模/成功标准
- **Phase 2**: 上下文包构建 — L1/L2/L3 分层探索 + 反向引用检查
- **Phase 2.5**: 初步风险预判
- **Phase 3**: 苏格拉底式探索 — 每轮 ≤3 题 P0
- **Phase 3.5**: 判档 light/full + 输出 5 行证据
- **Phase 4**: 文档输出 — change-impact/{name}/ 下 5 份
- **Phase 5**: 执行 + 验证 — 写操作前需 `确认 Step N`（**测试场景下你可一次性执行 low-risk，high-risk 标"需用户确认-未执行"**）

详细规则在 SKILL.md 顶部"铁律区"和 references/ 下。

---

## 4. 操作步骤

### Step 1: 准备

```bash
# 1. 确认 workdir 存在
ls <WORKDIR_PATH>

# 2. 读 SKILL.md 全文
Read <SKILL_MD_PATH>
```

### Step 2: Phase 1-3.5（在对话中输出，不写文件）

按 SKILL.md 走，每 Phase 输出标准格式。**特别注意**：
- Phase 2 必须 Read 至少 5 个真实文件
- Phase 2 必须 Grep 至少 3 次找引用
- Phase 3.5 必须明确"full"或"light" + 列 5 行证据

### Step 3: Phase 4 — 写 change-impact 文档

创建目录：
```
<ACTUAL_DIR>/change-impact/<feature-name>/
├── 000-context-pack.md
├── 010-requirements.md (或 040-light.md 如果判 light)
├── 020-design.md
├── 030-implementation.md
├── 050-validation/
│   ├── 001-add-permission.sql
│   └── 002-export-flow.sh
├── 060-preflight.md
└── 090-execution-record.md
```

每份文档内容要求：
- **000-context-pack.md**: 真实文件路径 + 真实代码片段（从 workdir Read 出来）
- **010-requirements.md**: P0/P1 风险 + 跨模块影响 + 升降档规则
- **020-design.md**: 完整代码风格报告 + 未截断代码片段
- **030-implementation.md**: 分 Step + 验证方式 + 环境降级路径
- **050-validation/**: SQL 脚本（DDL/DML）+ 测试脚本
- **060-preflight.md**: 执行前检查清单
- **090-execution-record.md**: 步骤追加记录（每步含时间戳 + 状态 + 用户确认 + 验证结果）

### Step 4: Phase 5 — 改 workdir 代码

按 Phase 4 的 implementation.md，**用 Edit/Write 真改 workdir 里的文件**：
- 至少修改 3 个真实文件
- 必须产生 1 个新文件（如新增 Controller 方法、新增 Service、新增 SQL）
- 涉及 DB schema 变更（如新增 permission）必须生成 SQL 脚本，**不要直接执行**
- 高风险操作标"高风险/不可逆"
- 每次改完追加一行到 090-execution-record.md

### Step 5: 完成后输出

输出报告（在对话中）：

```
═══ Subagent A 完成报告 ═══
输出目录: <ACTUAL_DIR>/change-impact/<feature-name>/
文件清单: [list of files in change-impact/]
workdir 改动:
  - M ruoyi-system/src/main/java/.../SysUserServiceImpl.java (+12, -3)
  - M ruoyi-system/src/main/java/.../SysUserController.java (+8, -0)
  - + ruoyi-system/src/main/java/.../export/UserExportService.java (new)
  - M ruoyi-ui/src/views/system/user/index.vue (+5, -1)
Phase 3.5 判档: full
铁律触发: #2 (新增 permission + 写新接口)
遗留未决项: [list of P0 questions that need user answer]
高风险步骤 (未执行): [list with reason]
mvn compile: [待主 Claude 跑]
```

---

## 5. 失败条件（任一即视为任务失败）

- ❌ 文档中出现 `<...>` / `TODO` / `// implement later` 等占位
- ❌ 修改 < 3 个文件
- ❌ 未生成 090-execution-record.md
- ❌ 引用了 workdir 中不存在的文件
- ❌ 跳过 Phase 3.5 判档直接判 light
- ❌ 高风险 DDL 直接执行而非生成脚本
- ❌ 不使用项目现有模式（自创一套）

---

## 6. 开始

现在按上述步骤执行。第一步：Read `<SKILL_MD_PATH>`。
