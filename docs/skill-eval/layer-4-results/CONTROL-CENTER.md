# 并行跑测控制中心

> 读完本文 → 跑 setup → 开 6 终端 → 收结果。

---

## Step 1：环境准备（一次性）

在 blue-skillhub 根目录执行：

```bash
bash docs/skill-eval/layer-4-results/setup-parallel.sh
```

这会创建 4 个 ruoyi-vue 副本（A1/A2/B3/C1 各一份），B3 的 PG 配置已预先改好。

---

## Step 2：并行执行（6 终端 × 1 条命令）

打开 **6 个 Claude Code 终端**，每个执行一条命令。6 个任务互不冲突（不同项目副本 × 不同 skill），可以同时跑。

| 终端 | 任务 | 命令 |
|------|------|------|
| 1 | A1 impact light | `cd E:/agent/blue-skillhub/test-projects/ruoyi-vue-a1 && 读 docs/skill-eval/layer-4-results/tasks/T01-A1-impact-light.md 并执行` |
| 2 | A2 impact full | `cd E:/agent/blue-skillhub/test-projects/ruoyi-vue-a2 && 读 docs/skill-eval/layer-4-results/tasks/T02-A2-impact-full.md 并执行` |
| 3 | B1 impact-pro Go | `cd E:/agent/blue-skillhub/test-projects/go-admin && 读 docs/skill-eval/layer-4-results/tasks/T03-B1-impact-pro-go.md 并执行` |
| 4 | B2 impact-pro Python | `cd E:/agent/blue-skillhub/test-projects/full-stack-fastapi-template && 读 docs/skill-eval/layer-4-results/tasks/T04-B2-impact-pro-python.md 并执行` |
| 5 | B3 adapter选择 | `cd E:/agent/blue-skillhub/test-projects/ruoyi-vue-b3 && 读 docs/skill-eval/layer-4-results/tasks/T05-B3-adapter-selection.md 并执行` |
| 6 | C1 pathfinder | `cd E:/agent/blue-skillhub/test-projects/ruoyi-vue-c1 && 读 docs/skill-eval/layer-4-results/tasks/T06-C1-pathfinder.md 并执行` |

**每个终端的 agent 只需要：**
1. 读对应的 task 文件
2. cd 到对应项目
3. 发指令
4. 记录行为
5. 评分
6. 把结果写到 `E:/agent/blue-skillhub/docs/skill-eval/layer-4-results/T0x-*.md`

---

## Step 3：收结果

6 个终端全部完成后，确认结果文件就位：

```bash
ls E:/agent/blue-skillhub/docs/skill-eval/layer-4-results/T0*-strong.md
```

应看到 6 个文件：
```
T01-impact-light-strong.md
T02-impact-full-strong.md
T03-impact-pro-go-strong.md
T04-impact-pro-python-strong.md
T05-adapter-selection-strong.md
T06-pathfinder-strong.md
```

然后可以清理 ruoyi-vue 副本：
```bash
rm -rf E:/agent/blue-skillhub/test-projects/ruoyi-vue-a1
rm -rf E:/agent/blue-skillhub/test-projects/ruoyi-vue-a2
rm -rf E:/agent/blue-skillhub/test-projects/ruoyi-vue-b3
rm -rf E:/agent/blue-skillhub/test-projects/ruoyi-vue-c1
```

---

## 弱模型版本

强模型 6 场跑完后，切到 minimax m3，同样方式跑 WEAK-MANUAL.md 的 6 场。弱模型需要另外 4 个 ruoyi-vue 副本（重新跑 setup-parallel.sh 即可）。

---

## 时间估算

- Step 1（setup）：~3 分钟
- Step 2（6 并行）：~15-25 分钟（最长的一场决定总时间）
- Step 3（收结果）：~1 分钟

总计约 **20-30 分钟**，比串行 2h 快 4-6 倍。
