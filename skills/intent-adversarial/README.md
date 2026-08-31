# Intent-Adversarial

> 所有工单开发完成后、验收之前，把系统当敌人打：安全攻击实测、性能压测三步法、并发一致性断言。

这是 intent-chain 链路的第 7 步：intent-anchor → intent-prd → intent-design → intent-visual（仅 UI 项目）→ intent-issues → intent-dev → **intent-adversarial** → intent-verify。

## 为什么需要它

intent-dev 验证「正常用户能用的功能对」，intent-verify 验证「用户路径走得通」，本 skill 验证的是第三件事：「**恶意输入和高并发打不穿**」。有两类缺陷靠正常流程永远抓不到：

1. **越权与逻辑漏洞**：串行测试和代码审查证明不了防线存在——实战发现，注册提权、缺失归属校验这类问题在"代码里有校验"的静态确认下零命中，只有双身份攻击实测才能暴露。
2. **并发一致性**：超卖、重复抢单、重复支付这类缺陷在串行调用下永远不会出现，必须真实并发执行（Promise.all / 线程池）加 DB 断言才能抓住。

## 快速开始

```text
/intent-adversarial
对 intent-chain/todo-cli/ 做对抗性验证。
```

结果写入同一链路目录下的 `adversarial-record.md`，发现的缺陷生成 `FIX-*` 工单写入 `defects.md` 交回 intent-dev 修复，修复后回到本 skill 定向复验。`adversarial_validate.py` 做 6 项检查（见下文）；**高危缺陷未全部修复，结论不得为通过，链级校验 FAIL，不得交付**。

## 攻击用例六类（必须全部覆盖）

| 类别 | 例 |
|---|---|
| 垂直越权 | 低权限 token 逐个调用管理接口，预期 401/403 |
| 横向越权 | 用户 A 的 token 操作用户 B 的按 id 资源，调后查库确认数据未变 |
| 跨角色越权 | 门店操作他店订单、摄影师交付他人订单 |
| 未授权访问 | 无 token 访问全部非公开接口，预期 401 |
| 业务逻辑攻击 | 冒用他人优惠券、重复支付同一单、负数参数污染、并发库存 |
| 暴力破解与滥用 | 连续登录失败触发锁定、开放注册提权测试 |

INTENT.md 第 16 节每条 SF 要求至少被一类中的用例覆盖；第 15 节每条 CC 要求逐条构造并发场景实测并断言最终数据状态。

## 性能压测三步法

1. **数据放大**：按性能要求推导规模批量灌数据（如并发 1000 → 万级业务行）——空库压测无意义。
2. **基准采集**：核心接口串行 N 次，记录 avg / p50 / p95。
3. **并发压测**：每接口 200 请求 / 20 并发，记录 rps / p95 / 5xx，同时执行 CC 类一致性断言。

攻击实测产生的一切数据变更，跑完必须恢复干净演示态。

## 什么时候使用

适合：

- dev-record 通过 `dev_validate.py` 校验且所有工单标 done。
- INTENT.md、issues.md、architecture.md 通过各自校验器。
- 系统可在本机或测试环境运行。

不适合：

- 还有工单未完成（先回 intent-dev）。
- 寻找功能 bug 或路径验收问题（那是 intent-verify 的事）。
- 自己动手修代码——发现的缺陷生成 `FIX-*` 工单，由 intent-dev 承接修复后回到本 skill 定向复验（只重跑与缺陷相关的用例，全绿才关闭）。

**轻量档**：轻量档降的是上游文档厚度和确认次数；六类攻击全覆盖、SF/CC 逐条实测、真实并发执行这些强制规则一概不降级。

## 校验

`adversarial_validate.py` 运行 6 项检查：

| 检查项 | 检查内容 |
|---|---|
| A1 | 文件非空 |
| A2 | 六个必需章节齐全（数据准备 / 安全攻击结果 / 并发一致性结果 / 性能基准 / 缺陷清单 / 结论） |
| A3 | INTENT 第 16 节每条 SF 在安全攻击结果中有至少一条关联用例 |
| A4 | INTENT 第 15 节每条 CC 有实测记录且通过 |
| A5 | 缺陷清单中高危缺陷未全部修复 → FAIL（阻止交付） |
| A6 | 结论与缺陷状态一致——存在未修复缺陷时结论不得为「通过」 |

```bash
python skills/intent-adversarial/scripts/adversarial_validate.py intent-chain/{链路目录}/adversarial-record.md intent-chain/{链路目录}/intent.md
```

## 文件结构

```text
intent-adversarial/
├── SKILL.md
├── README.md
├── templates/
│   └── adversarial-record.md        ← 验证记录模板
├── scripts/
│   └── adversarial_validate.py      ← 6 项结构检查与 SF/CC 交叉校验
└── tests/
    └── test_adversarial_validate.py ← 行为回归测试
```

## 能力边界

Intent-Adversarial 能够：

- 六类安全攻击实测，每条 SF 有攻击用例关联，每条 CC 真实并发断言。
- 性能三步法基线（数据放大 → 基准采集 → 并发压测）。
- 缺陷工单生成（FIX-* 写入 defects.md）与修复后的定向复验。
- 通过校验器检查 adversarial-record 的结构完整性，并与 INTENT.md 交叉校验 SF/CC 覆盖。

Intent-Adversarial 做不到：

- 修复代码（缺陷交 intent-dev 承接）。
- 替代 intent-verify 的路径验收、页面走查与漂移复核。
- 静态代码确认（"代码里有校验"）不构成通过证据——必须实测。
