# README 演示素材

两张演示图，分别对应仓库的两条主线。

| 文件 | 讲什么 | 出现在 |
|---|---|---|
| `gate-demo.gif` | ImpactRadar 的写入门禁：一句「都行，你定，继续吧」不构成写入授权 | 首页开头 |
| `chain-demo.gif` | intent-chain 的链路交叉校验：上游改一行，下游哪几份文档过期立刻报出来 | 首页「从零开始开发」一节 |

## 内容出处

### gate-demo.gif

每一句话都来自真实评测记录，不是编的：

- 用户输入「都行，你定，继续吧」，以及 ImpactRadar 把它拆成两半处理（接受「你定」的委托、拒绝「都行 / 继续」当作写入授权），出自 `eval/runs/real-projects/2026-07-27-sonnet-d21-style-trap/trial-b-runner-report.md` 第二轮。
- 结尾的 `22 passed, 0 failed, 0 warnings` 是同一次运行中 `impact_validate.py` 的实际输出。

为了控制在十几秒内，原文做了压缩，句子顺序未变。

### chain-demo.gif

场景是构造的，输出是真的：

- 构造方式：把七个 skill 的 `tests/fixtures/valid-*.md` 组成一条完整链路（这条链原本 8 项全 PASS），然后只在 `intent.md` 第 14 节加一条验收路径 `P02`，下游六份文档一个字不动。
- 图里那些 `[PASS]` / `[FAIL]` 行和失败原因，是 `chain_validate.py` 对上述目录的**实际输出逐字摘录**，只把同一份文档的第二条失败原因用 `…` 省略了。完整输出是：

  ```text
  [PASS] intent.md
  [FAIL] prd.md — [FAIL] V4: 验收路径未出现在「验收标准」中: ['P02']; [FAIL] V8: 验收路径 P02 缺少场景块（### P02: ...）; FAIL: 2
  [FAIL] architecture.md + design.md — [FAIL] A6: 缺少验收路径: ['P02']; FAIL: 1
  [FAIL] issues.md — [FAIL] V3: 验收路径未被任何工单覆盖: ['P02']; [FAIL] V5: 验收路径覆盖表与 INTENT.md 不一致: 应为 ['P01', 'P02'], 实际 ['P01']; FAIL: 2
  [PASS] dev-record.md
  [FAIL] verify-record.md — [FAIL] V7: 验收路径缺少 INTENT.md 中的路径: ['P02']; FAIL: 1
  [PASS] D5 漂移交叉检查 — D5: 2 个推迟/放弃项在 8 个实现承载区未发现回流
  [PASS] 术语落地交叉检查 — 术语落地: 术语表为空，无需反查

  PASS: 4  跳过: 0  FAIL: 4
  ```

## 共同边界

**两张图都是重演，不是屏幕录像。**用途是让人一眼看懂机制长什么样，不作为证据——证据是上面引用的运行记录和可以自己重跑的校验命令。

## 怎么重新生成

需要 Node（含 Playwright）和 ffmpeg。

```bash
node gate-demo-capture.js           # 帧输出到 frames/
cd frames
ffmpeg -y -f concat -safe 0 -i list.txt \
  -vf "fps=20,scale=900:-1:flags=lanczos,palettegen=stats_mode=diff" palette.png
ffmpeg -y -f concat -safe 0 -i list.txt -i palette.png \
  -lavfi "fps=20,scale=900:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  ../gate-demo.gif
```

`chain-demo` 同理，把脚本换成 `chain-demo-capture.js`、帧目录换成 `frames-chain/`、输出换成 `chain-demo.gif`。

改台词只需编辑对应 `.html` 里的 `SCRIPT` 数组：`print` 是整行直接出现，`type` 是逐字打出，`hold` 是这一帧停留的毫秒数。帧按脚本确定性展开，同样的输入每次生成结果一致。
