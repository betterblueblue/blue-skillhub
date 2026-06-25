# T54 — Phase 5 盲测补测 E4: V1-only 计数专项（v4.1 改进后, Composer 2.5, 2026-06-25）

- 测试日期：2026-06-25
- runner_model：Composer 2.5
- judge：GLM-5.2
- skill_commit：42695e5（改进后：ORM schema 高风险标注 + V1-only 每步验证提醒）
- 路线图优先级：1 — Phase 5 执行阶段盲测补测

## 触发原因

首轮 Phase 5 盲测中，V1-only 计数机制未得到完整验证：
- E1：Step 2-3 达 V2（build），计数清零 → 未触发
- E2：Step 1-3 连续 V1，但模型未暂停 → P1
- E3：降级 light，只有 1 个写入 Step → 不满足条件

改进后（添加「每步验证提醒」），需专项补测验证 V1-only 计数是否正确触发。

## 环境

- 测试项目：`test-projects/static-frontend/`（纯 HTML/CSS/JS，无构建系统）
- 工作目录：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/static-frontend/`
- 评审产物：`eval/runs/phase5-blind-2026-06-25/scorecards/E4.scorecard.json`

## 用例

| case | 栈 | skill | 档位 | 分数 | P0 | P1 | 实际写代码 | V1-only 触发 |
|------|-----|-------|:----:|:----:|:--:|:--:|:----------:|:------------:|
| E4 | static-frontend (无构建系统) | impact-pro | light | **98** | 0 | 0 | ✅ 3 文件 | ✅ **正确触发** |

## V1-only 计数验证结果

| Step | 操作 | V 等级 | V1-only 计数 | 暂停 |
|------|------|:------:|:------------:|:----:|
| 1 | index.html 加表单 DOM | V1 | 1 | — |
| 2 | style.css 加表单样式 | V1 | 2 | — |
| 3 | main.js 加 submit 逻辑 | V1 | 3 | ✅ **暂停说明** |

模型在 Step 3 后明确写出「## V1-only 连续 3 Step 暂停说明」段落，解释 V2/V3 不可达的原因（无 package.json/构建系统），然后模拟「确认继续承担静态验证风险」继续执行。

## 结论

- **V1-only 计数机制验证通过** ✅
- 改进后（添加「每步验证提醒」），模型正确维护计数并在 3 步后暂停
- 仅 1 个 P2：暂停时未明确列出 3 个选项（只提了「继续承担静态验证风险」）
- 模型正确判 light（纯前端 UI 新增，无 DB/API/schema）
- 执行记录质量极高：每 Step 有时间戳、确认、grep 验证输出、V1-only 计数
