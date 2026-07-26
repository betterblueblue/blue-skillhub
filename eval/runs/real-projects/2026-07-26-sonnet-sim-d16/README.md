# D16 复跑（Sonnet 模拟 runner）— 搜索盲区规则修复验证

> **runner 身份声明**：本记录的两个试次由 Claude Sonnet 5（Claude Code Agent 子代理，编排层显式指定 `model: sonnet`）执行，是 2026-07-26 用户决策下的替代 runner——原 runner_scope 中 gpt-5.4-mini（额度不可用）与 MiniMax M3（403）放弃补跑，Sonnet 作为"相对弱模型"验证 skill 规则的有效性。本记录不冒充原 runner 数据，不写入 `delivery-results.json` 的历史 runner 条目。
>
> 注意：试次 B 的使用记录自报模型名先后出现"Claude Sonnet 5"与"Claude Fable 5"两个版本——子代理自报模型名不可靠，runner 身份以编排层设置为准（本声明即依据）。

## 目的

验证 `skills/impact/references/phase-2-context-discovery.md` Step 2.3 第 9 条「搜索盲区强制检查」（2026-07-26 落地）是否堵住 D16 原 FAIL 的两个漏项：被搜索工具默认跳过的 `.env` 键值、未核查的 `.github/` CI。即执行 delivery-matrix D16 `repair_loop` 的"补配置入口检查规则后复跑"。

## 运行条件

- fixture：`test-projects/full-stack-fastapi-template` 的两份隔离副本（scratchpad，含 `.git`，排除历史 `change-impact.bak`；原 `E:\agent\real-project-fixtures\` 路径已不存在）
- 启动文本：runbook 两段式原文（评测环境 + case prompt），无监考词
- 确认协议：脚本化用户，业务岔路只给最小决定（Q1 Copier 连改 / Q2 硬切），写授权仅回 `确认 Step N` 原话

## 结果

### 试次 A：覆盖满分，未产出 Phase 4 文档

- ✅ 盲区双中：按规则执行 `--no-ignore --hidden` 全量补查（与普通搜索比对 13 文件无漏网）；`.github/workflows/*.yml` 明确核查并记录零引用
- ✅ 超出历史 PASS 水平的发现：`.copier/update_dotenv.py` 无 PROJECT_NAME 字面量、靠 key 大写动态匹配——grep 不可达，靠读文件抓到
- ✅ 全程零写入，明确说明"业务岔路确认 ≠ 写授权"（硬规则 #8）
- ❌ 把 case prompt 的"先不要写代码"解读为"什么都不写"，交付止于对话分析——按 D14 先例的 phase4_artifacts_missing 口径判 **FAIL（产物缺失）**
- ❌ 精确性缺陷 1 处：声称 `README.md:178` 有环境变量说明，实测该行不存在此内容（`deployment.md:178` 行号错位），属幻觉引用

### 试次 B：全链 PASS

- ✅ 盲区双中：`git check-ignore` + 命中数比对核实 `.env` 实为 Git 跟踪（纠正"被 gitignore"的想当然，写入 020「不采用的推断」）；`.github/` 核查结论进 000 已确认事实
- ✅ 判 full；覆盖 config.py/main.py/utils.py、`.env:16`、deployment.md、Copier 生成链（copier.yml + update_dotenv.py 联动）、README:197；识别邮件模板 context key 与 `.mjml` 占位符为原子组合
- ✅ 部署同步说明：`env_file: - .env` 注入链路核实，代码与 `.env` 同提交原子切换（D04）
- ✅ 确认门禁实测两道：模糊确认"继续"被拒收并要求带编号确认；`确认 Step 1` 后才写入
- ✅ Phase 4 五件套 + `.git-baseline.json` 写入，源码零改动（git status 仅 `?? change-impact/`）
- ✅ `impact_validate.py --mode full` 最终 **31 passed / 0 failed / 0 warnings**；判分方独立复跑同结果，退出码 0
- ⚠️ 首跑 1 个 V24 FAIL 经 1 轮修复清零——归因为**校验器假阳性**（见发现 1），非 runner 覆盖缺口
- 结论：**PASS**（含 1 次校验器假阳性修复）

## 判分方独立核验

- `impact_validate.py` 独立复跑：31/0/0，退出码 0
- fixture git status：仅新增 `change-impact/` 文档，无源码 diff
- 文档抽查：`.env:16`、`.github` 核查记录、`--no-ignore --hidden` 反查命令均在 000/020 落档

## 本轮发现（待处理）

1. **校验器缺陷（backlog 候选）**：V24 Check E 从 Step 标题起取固定 500 字符窗口探测源码引用，正文短的 Step 会把下一节标题 token（如 `impact_validate.py`）误判为源码，产生假 FAIL。建议截断到节边界。
2. **case prompt 歧义（case/SKILL 措辞候选）**："先不要写代码，只做完整影响分析"导致 2/2 Sonnet 试次不主动进入 Phase 4 文档（与 D14 的 gpt-5.4-mini 行为同型；composer 历史上则会主动进入）。建议 case prompt 或 SKILL.md 写明分析文档不属于"写代码"。
3. **归因措辞修正**：D16 原归因"漏查被 gitignore 的 .env"机制不准确——该 fixture 的 `.env` 被 Git 跟踪，真实盲区是 rg 默认跳过点开头隐藏文件；现行规则的 `--no-ignore --hidden` 同时覆盖两种机制，规则本身无需修改。

## 结论

搜索盲区规则**验证有效**：2/2 试次执行强制补查并覆盖 D16 原两个漏项；进入完整交付的 1/1 试次校验器清零。D16 repair_loop 已执行完毕（替代 runner）。
