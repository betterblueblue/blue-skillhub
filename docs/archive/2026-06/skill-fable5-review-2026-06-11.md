
# impact / impact-pro Claude Fable5 文档评审意见

评审日期：2026-06-11
适用范围：Claude Code + 人工监督模式
参考文档：
- `skill-gap-list-2026-06-11.md`
- `skill-gap-fix-plan-2026-06-11.md`
- 90-问题清单、eval 数据、SKILL.md / templates

---

## 1. 总体评价

- 文档整体质量高，可作为修复施工单使用。
- P0/P1/P2 分级合理，施工顺序可执行。
- 对阻塞项 (#1) 定义清楚，改动方案明确。
- 施工收益清楚，便于团队执行与验收。
- 说明了哪些项划掉（agents/openai.yaml、未 CI 化验收）

### 优点
1. P0 高危门禁铁律化明确，R3 三次重跑验证一致性。
2. DB 写保护采用双层防护（prompt + 只读连接）。
3. MCP 能力声明对账流程规范，避免误分类。
4. 双 skill 漂移治理可选方案合理，减少未来维护风险。
5. references 下沉方法明确，安全门禁保留在正文。
6. trigger 词收紧、greenfield check、模板补段、Grep 假阳性规则化等优化都落实到位。

### 风险/可改进点
1. **缺少 `disable-model-invocation: true`**：建议加到 frontmatter，防止自动触发高副作用 skill。
2. **allowed-tools 说明不够明确**：需要补充“仅预批准，不等同安全边界”。
3. **生产 DB 写执行应禁止 Agent 直接执行**：只允许生成脚本/回滚，由用户或有权限连接执行。
4. **安全协议共享与 references 下沉可能冲突**：共享只能 build-time，运行时安全门禁必须内联。
5. **高危 Step 建议增加显式条目**：如 TRUNCATE、ALTER TABLE、权限变更、批量回填等。
6. **V1-only 计数粒度需补充说明**：按 Step 计数而非文件数，连续计数、计数清零规则明确。
7. **Grep 假阳性规则需抽样验证而非阈值直接排除**。
8. **时间戳命令需兼容 Windows/PowerShell**。
9. **P0 完成后描述建议降调**：明确有人值守，其他 P1 限制仍有效。

### 阶段执行建议
- **P0** (#1): 高危门禁铁律化，立即执行。
- **P1** (#2-#5c, 新增 disable-model-invocation): DB 写保护硬约束、MCP 能力对账、V1-only 通用计数、双 skill 漂移对齐。
- **P2** (#6-#11): secret/凭证脱敏、references 下沉、安全触发优化、greenfield check、模板补段。
- **P3** (#12): 时间戳、migration head、ASCII 文件名。
- **CI runner** (#13): 可选，但建议完成以实现改动回归验证。

### 总结
- 文档无大的方向性错误，可直接用于团队施工。
- 阻塞项唯一：#1 评测残留段铁律化。
- 完善上述风险/改进点后，即可成为工程级可执行修复方案。
- 文档与现有 eval 数据、SKILL.md、模板引用、MCP 实测一致。

---
【评审完成】
