# README 演示素材

`gate-demo.gif` 是首页那张写入门禁演示图。

## 内容出处

动画里的每一句话都来自真实评测记录，不是编的：

- 用户输入「都行，你定，继续吧」和 ImpactRadar 把它拆成两半处理（接受「你定」的委托、拒绝「都行 / 继续」当作写入授权），出自 `eval/runs/real-projects/2026-07-27-sonnet-d21-style-trap/trial-b-runner-report.md` 第二轮。
- 结尾的 `22 passed, 0 failed, 0 warnings` 是同一次运行中 `impact_validate.py` 的实际输出。

为了控制在十几秒内，原文做了压缩，句子顺序未变。**动画本身是重演，不是屏幕录像**——用途是让人一眼看懂门禁长什么样，不作为证据；证据在上面那份运行记录里。

## 怎么重新生成

需要 Node（含 Playwright）和 ffmpeg。

```bash
node gate-demo-capture.js          # 渲染确定性帧到 frames/
cd frames
ffmpeg -y -f concat -safe 0 -i list.txt \
  -vf "fps=20,scale=900:-1:flags=lanczos,palettegen=stats_mode=diff" palette.png
ffmpeg -y -f concat -safe 0 -i list.txt -i palette.png \
  -lavfi "fps=20,scale=900:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  ../gate-demo.gif
```

改台词只需编辑 `gate-demo.html` 里的 `SCRIPT` 数组：`print` 是整行直接出现，`type` 是逐字打出，`hold` 是这一帧停留的毫秒数。帧是按脚本确定性展开的，同样的输入每次生成结果一致。
