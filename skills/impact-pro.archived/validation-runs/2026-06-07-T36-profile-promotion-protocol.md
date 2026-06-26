# T36 Profile 晋级协议补强

- 测试日期：2026-06-07
- 测试人：Codex
- 测试方式：profile Level / generic 备用方案规则审计
- 目标：补强第 7 条成功标准，避免新技术栈只因 matcher 命中或 demo 项目 happy path 就升级为专属 profile。
- 当前状态：规则补强完成；后续新增 profile 时需持续执行。
- 失败等级：无 P0/P1。

## 背景

用户目标要求：

```text
新技术栈必须先走 generic 备用方案，再通过真实项目验收后升级 profile Level。
```

原 `profiles/_schema.md` 对 Level 1 的定义偏轻，只要求能识别栈、找到主文件、给候选命令和 limitations。这个定义不足以防止“文件名命中即升级 profile”的误用。

## 本轮补强

更新 `profiles/_schema.md`：

- Level 1 必须先经过 generic 备用方案。
- Level 1 必须在至少 1 个真实项目完成 full + light 双变更验收。
- 验证命令必须来自项目证据，能运行的必须实际运行。
- 验收记录必须写入 `validation-runs/`。
- Level 2 / Level 3 明确要求更多真实项目或生产级项目证据。

新增 `Profile 晋级协议`：

1. generic 备用方案
2. 候选 profile
3. 双变更验收
4. 运行时验证
5. 记录归档

同步更新：

- `profiles/_template.md`
- `README.md`
- `VALIDATION.md`

## 一票否决

- 不能只因文件名或依赖命中就把新栈标成 Level 1。
- 不能把 generic 备用方案结果描述成专属 profile 已验证。
- 不能写未验证的命令、glob、目录结构或风格结论。
- 不能用 demo 项目的单一 happy path 覆盖生产级限制说明。

## 结论

T36 通过。第 7 条现在从“原则描述”升级为可执行晋级协议。

当前整体结论不变：

```text
impact-pro = 多栈可试用增强版，不是已验收的成熟通用完成态。
```
