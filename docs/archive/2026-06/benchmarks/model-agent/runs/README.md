# Runs

这里用于本地保存模型评测输出。

默认规则：

- 原始 agent 输出、score JSON、summary markdown 不自动提交。
- 需要作为论文/博客证据的结果，可以筛选后复制到 `docs/` 或单独建立可审阅的报告文件。
- 每批 run 建议按日期、项目、阶段建目录，例如 `20260609-papermark-phase1/`。

推荐结构：

```text
runs/
└── 20260609-papermark-phase1/
    ├── raw/
    ├── scored/
    └── summary.md
```

这样做是为了让 benchmark 框架保持干净，同时保留本地复盘材料。
