# V9 盲测 noskill 组说明 — 复用 V8 C1 产出

> V9 的 noskill 组直接复用 V8 C1 产出，不重新执行。
> 原因：noskill 组不使用 skill，不受 v3.9/v4.0 改进影响。

## 产出位置

V8 C1 产出路径：`eval/runs/blind-2026-06-25-v8/cell-C1/test-projects/`

| Case | 产出文件 |
|------|---------|
| B1' | `ruoyi-vue/change-impact/v8-composer-noskill/B1/impact-analysis.md` |
| B2' | `prisma-express-ts/change-impact/v8-composer-noskill/B2/impact-analysis.md` |
| B3' | `prisma-express-ts/change-impact/v8-composer-noskill/B3/impact-analysis.md` |

## V8 C1 评分（复用）

| Case | D1 | D2 | D3 | D4 | D5 | D6 | D7 | 总分 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| B1' | 18 | 12 | 17 | 8 | 0 | 8 | 8 | 71 |
| B2' | 19 | 13 | 19 | 9 | 0 | 8 | 8 | 76 |
| B3' | 19 | 13 | 18 | 8 | 0 | 8 | 8 | 74 |
| 均分 | 18.7 | 12.7 | 18.0 | 8.3 | 0 | 8.0 | 8.0 | 73.7 |
