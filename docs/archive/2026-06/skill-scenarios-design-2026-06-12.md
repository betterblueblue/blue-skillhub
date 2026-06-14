# impact / impact-pro scenarios 自动化验收体系

> 日期: 2026-06-12
> 配套: `skills/impact/tests/` + `skills/impact-pro/tests/`
> 跑法: `cd skills/impact/tests && ./run.sh` (同理 impact-pro)
> 状态: ✅ v1 上线（静态层），LLM 集成层留待 v2

## 背景

gpt5.5pro 评审 P0 #3「缺可重复自动化验收」指出，v3.7 之前没有任何 fixtures / scenarios 跑通"如果用户说 X，skill 是否能产出 Y"的回归。

本次工作把 T-R1（impact on RuoYi-Vue）和 T-R2（impact-pro on go-admin）的真实测试场景**固化成可重放的 scenarios 套件**，并加上可重入的 runner 脚本。

## 设计

### 目录结构

```
skills/impact/tests/
├── README.md
├── run.sh                          # 主 runner
├── lib/validate.sh                 # 校验函数库
├── fixtures/README.md              # fixture 来源
└── scenarios/
    └── java-spring-mybatis/
        ├── 001-delete-sys-user-remark.json
        ├── 002-add-last-login-ip.json
        └── 003-change-login-remember-me.json

skills/impact-pro/tests/
├── README.md
├── run.sh
├── lib/validate.sh
├── fixtures/README.md
└── scenarios/
    └── go-gin-gorm/
        ├── 001-modify-user-status-enum.json
        └── 002-change-api-msg-text.json
```

### Scenario JSON Schema

每个 scenario JSON 描述：

| 字段 | 含义 | 来源 |
|------|------|------|
| `id` | 唯一 ID（栈-动词-对象-NNN） | 命名 |
| `title` | 场景标题（含陷阱提示） | 文档化 |
| `skill` | impact / impact-pro | SKILL 名称 |
| `stack` | 栈标识（java-spring-mybatis / go-gin-gorm） | profile 名称 |
| `difficulty` | low / medium / high | 任务规模 |
| `fixture.project` | 项目名 | 真实开源项目 |
| `fixture.url` | 仓库 URL | fixture 来源 |
| `fixture.commit` | 锁定 commit 哈希 | 防漂移 |
| `query` | 模拟用户输入 | 真实场景 |
| `expected.phase_3_5_classification` | 期望判档 | light / full |
| `expected.iron_rules_triggered` | 期望触发的铁律编号 | 铁律区 #1-#7 |
| `expected.iron_rule_2_specific_match` | 铁律 #2 具体命中条目 | 反向定位 |
| `expected.p0_questions_min` | 最少 P0 追问数 | 业务期望 |
| `expected.references_loaded` | 期望加载的 references | 引用检查 |
| `trap_for` | 这条场景要抓的现实陷阱 | 人类可读 |
| `files_to_inspect[]` | fixture 中必须存在的文件 + 字符串 | 静态校验 |

### Runner 静态校验能力

`run.sh` 对每个 scenario 跑 6 类检查：

1. **JSON schema 完整性**：含 id/title/skill/stack/fixture/query/expected
2. **Fixture 存在**：项目路径 + commit 哈希匹配
3. **铁律存在**：`expected.iron_rules_triggered` 中的每条 #N 都在 SKILL.md 铁律区可定位
4. **References 存在**：`expected.references_loaded` 中的每个文件都在 `references/` 目录
5. **Phase 3.5 判档合法**：`light` 或 `full`
6. **Fixture 证据存在**：`files_to_inspect` 中每个文件存在 + 含 `must_contain` 字符串

每条 PASS / FAIL 通过 `ok()` / `fail()` 函数递增全局计数器，结束时打印总数。

## 5 个场景概览

### impact / RuoYi-Vue (3 场景)

| ID | Query | 期望 | 陷阱 |
|----|-------|------|------|
| `001-delete-sys-user-remark` | "删 sys_user.remark 字段" | 铁律 #2 + #5 触发 / 判 full | BaseEntity 共享字段波及 7+ 实体 |
| `002-add-last-login-ip` | "sys_user 加 last_login_ip VARCHAR(64)" | 铁律 #2 触发 / 判 full | 现有 login_ip 已存在，重复 |
| `003-change-login-remember-me` | "改登录页 checkbox 文案" | 铁律无触发 / 判 light | 用户口述与代码原文不一致 |

### impact-pro / go-admin (2 场景)

| ID | Query | 期望 | 陷阱 |
|----|-------|------|------|
| `001-modify-user-status-enum` | "user.status 删 frozen 加 disabled" | 铁律 #2 触发 / 判 full | frozen 全仓 0 命中（空操作） |
| `002-change-api-msg-text` | "改 API msg 文案'操作成功'→'请求成功'" | 铁律无触发 / 判 light | 实际是"查询成功"在 sys_user.go:58 |

## 跑通结果

```
$ cd skills/impact/tests && ./run.sh
═══════════════════════════════════════
  impact skill — scenarios runner
═══════════════════════════════════════
  找到 3 个 scenario
...
  PASS: 32
  FAIL: 0
  🟢 ALL PASS

$ cd skills/impact-pro/tests && ./run.sh
═══════════════════════════════════════
  impact-pro skill — scenarios runner
═══════════════════════════════════════
  找到 2 个 scenario
...
  PASS: 21
  FAIL: 0
  🟢 ALL PASS
```

## v2 留待

- **LLM 集成层**：调用 Claude API 跑 skill，对比实际输出 vs `expected.phase_3_5_classification` — 需要 API key + cost 控制
- **CI 集成**：GitHub Actions / pre-commit hook 跑 `./run.sh`
- **场景扩展**：vl-vision skill（按 gpt5.5pro 评审需先达生产级）、其他栈 profile（python-fastapi / frontend-nextjs 等）

## 实施过程踩到的坑（写给未来 review 的人）

1. **Git Bash + Python 路径**：`/e/...` 这种 MSYS 路径 Python 读不到，需用 `cygpath -w` 转换成 `E:\...`
2. **Python 3 vs Python 2 入口**：`python3` 在 Windows 上是 WindowsApp 包装器，bash 子进程里 exit 49；改用 `python`（已自带 3.11.9）解决
3. **Bash pipe-subshell 计数丢失**：`python ... | grep ... | while read; do fail(); done` 中 `fail()` 不会更新父 shell 的 `FAIL_COUNT`（subshell 隔离）。用 `< <(process substitution)` 替代 `|` 修复
4. **场景 must_contain 写太死**：实际 SQL 是多空格对齐（`remark            varchar(500)`），不能用单空格。改用更宽松的关键字匹配
