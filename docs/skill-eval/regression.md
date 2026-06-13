# 回归触发矩阵（三 skill 通用）

> 升级自 docs/impact-regression-protocol.md，覆盖 pathfinder。

## 触发矩阵

| 修改类型 | 必跑复测 | 可选复测 | 通过标准 |
|---|---|---|---|
| README / 描述 / 致谢 | RG0 文档一致性 | 无 | 无矛盾、无旧版本结论、链接有效 |
| 铁律措辞（任一 skill） | RG0 + 共享契约检查 + RG1 该铁律相关 case | RG3 真实 agent | 契约在三 SKILL.md 都存在；行为符合新措辞 |
| light/full 判档规则 | RG1 判档回归 | RG3 真实 agent | 简单不过度 full；高风险不得 light |
| 苏格拉底提问规则 | RG1 提问回归 | RG3 真实 agent | ≤3 问/轮；多轮收敛；P0 必问 |
| Context Pack / 引用检查 | RG1 上下文回归 | RG2 多栈 | 完整/分级/排除项齐 |
| Phase 5 / 写操作闭环 | RG2 执行闭环 | RG3 真实写操作 | preflight + 确认 + 执行记录 + 验证等级 |
| impact-pro profile / DB adapter | RG2 对应栈 full + light | RG3 弱模型 | profile 命中正确；generic 降级诚实 |
| Pathfinder 信任标签规则 | RG0 + Pathfinder L1 安全 case | RG2 扩展场景 | 不编造已核实；推断正确标注 |
| Pathfinder 降级规则 | RG0 + Pathfinder L1 降级 case | RG2 降级场景集 | 降级不编造；盲区显式声明 |
| 共享契约（凭证脱敏/仓内文本/写入边界） | RG0 + 三 skill 相关 RG1 case | RG2 跨 skill 验证 | 三 skill 行为一致 |

## 回归包定义

### RG0：文档一致性 + 共享契约检查

```powershell
# 1. 文档一致性（继承原协议）
git diff --check
rg -n "T01-T45|T01-T46|旧版本结论" README.md skills docs --glob "!docs/impact-regression-protocol.md" --glob "!docs/skill-eval/*"

# 2. 共享契约存在性（新增）
bash skills/impact/tests/run.sh          # 含共享契约检查
bash skills/impact-pro/tests/run.sh      # 含共享契约检查
bash skills/pathfinder/tests/run.sh      # 含共享契约检查
```

### RG1：规则定向回归

同原协议，扩展 Pathfinder case。

### RG2：扩展场景回归

同原协议，扩展 Pathfinder 场景。

### RG3：真实 agent / 弱模型复测

同原协议，扩展 Pathfinder 降级场景。

## 复测记录格式

同 [docs/impact-regression-protocol.md 的复测记录格式](../impact-regression-protocol.md)，目录改为 `eval/runs/`。
