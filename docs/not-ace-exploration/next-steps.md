# Next Steps

建议下一轮不要马上扩大到更多模型，而是先把 V3 pilot 做成更稳定的 V3.2。

## 优先级 1: 重复性

对关键组做 3 次重复运行：

- M3 + `rg`
- M3 + Not ACE
- GLM-5.1 + `rg`
- GLM-5.1 + Not ACE

优先复跑任务：

- `go-story-origin`: 因为 V3 中 M3 + `rg` 在这里出现 P0 漏召回和链路误判。
- `ruoyi-permission-chain`: 权限链路适合观察 agent 是否能跨后端注解、权限字符串、前端 directive 和菜单配置。

## 优先级 2: 日志结构化

当前成本、耗时和 turns 能记录，但工具调用还不够细。

建议补充：

- Search Calls。
- File Reads。
- Not ACE Calls。
- `rg` Calls。
- 无关文件读取数量。
- 是否出现 hallucination。
- 是否提出正向 + 错误用例。

## 优先级 3: 指标固定

继续使用：

- P0 Recall。
- Overall Recall。
- P@5 / P@10。
- Noise。
- Time。
- Token / Cost。
- Analysis Quality。
- Plan Correctness。
- Verification Coverage。

同时把 expected files 固定为 P0 / P1 / P2，避免每次评分口径漂移。

## 优先级 4: 补 D 组

D 组是 Codex + Not ACE。

它不建议作为第一轮主线，因为 Codex + 常规工具已经很强，Not ACE 的增益可能被模型能力吃掉。但补 D 组仍然有价值：

- 看强模型是否减少探索成本。
- 看 Not ACE 是否能减少无关文件读取。
- 看 semantic entry 是否让 Codex 更快进入正确链路。

## 暂缓项

暂时不建议马上做：

- 引入更多模型。
- 加很多新项目。
- 把 benchmark 变成写代码任务。
- 把原始 transcript 直接提交到仓库。

更好的顺序是先把 V3.2 的重复性和日志结构化做扎实，再扩大样本面。
