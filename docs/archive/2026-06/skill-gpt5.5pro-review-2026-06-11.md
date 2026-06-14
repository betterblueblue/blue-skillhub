
# Claude Code Skill 评审与优化建议

## 适用范围
- 技术栈: Claude Code / MiniMax M3
- Skill: impact, impact-pro
- 使用模式: **人工监督**（不建议无人监督生产）

---

## 当前状态

| Skill | 当前状态 | 是否生产可用 |
|-------|----------|--------------|
| impact | Java/RuoYi 场景设计完整，安全与文档流程成熟 | **灰度可用，需人工监督** |
| impact-pro | 多栈 profile 化，覆盖 Java/Node/React/Go/ASP.NET 等 | **比 impact 更接近生产，但仍需人工监督** |
| vl-vision | CLI/Agent 工具，更偏向实验/辅助 | **未达生产级 Skill** |

---

## 优点

1. **安全设计**  
   - 破坏性操作需逐步确认 Step N  
   - 阻塞恢复安全闸、非 Git 降级保护

2. **证据化流程**  
   - 上下文包、L1-L3 分层探索  
   - V0-V3 验证等级、执行记录

3. **impact-pro 架构合理**  
   - profiles/db-adapters/templates 分层  
   - 易于维护和扩展

4. **回归意识强**  
   - Claude Code + MiniMax M3 已真实复测  
   - 明确未知栈走 generic 兜底

---

## P0 问题（阻止直接生产发布）

1. **OpenAI Skill 包目录不合规**  
   - 缺少 `agents/openai.yaml`  
   - frontmatter 中 `allowed-tools` 不兼容 ChatGPT Skill

2. **SKILL.md 过长** (>500 行)  
   - 需要拆分为 references 控制平面  
   - 减少上下文污染，防止规则漂移

3. **缺少可重复自动化验收**  
   - 应增加 fixtures / scenarios 测试 Step 确认、DB/API/full 判档

4. **DB 写权限默认未收紧**  
   - execute_sql 默认只读，生产 DB 写操作需多重确认

---

## P1 优化建议

1. 缩小触发词范围，避免过度触发  
2. impact 与 impact-pro 用户入口统一  
3. 模板文件名统一 ASCII  
4. 加入 prompt-injection / secret 防护  
5. 验证记录可审计化，生成 release note / 测试矩阵  
6. 拆分 SKILL.md，控制平面 < 500 行，规则细节放 references  
7. DB 写权限分级（只读 / 草案 / staging / prod + 二次确认）

---

## 生产使用策略

- **必须人工监督**  
- 默认读操作，写操作需二次确认  
- Step N 确认为强制执行  
- 长会话 / 多模块 / DB 操作应分阶段执行

---

## 结构示例（优化后）

impact/
├── SKILL.md                 # 控制平面，120-180 行
├── agents/
│   └── openai.yaml
├── references/
│   ├── core-flow.md
│   ├── safety-gates.md
│   ├── context-pack-rules.md
│   └── execution-rules.md
├── templates/
└── tests/
    └── scenarios/

impact-pro/
├── SKILL.md
├── agents/
├── references/
├── profiles/
├── db-adapters/
├── templates/
└── tests/

---

## vl-vision 注意事项

- CLI 工具 + Agent 调用  
- 不包含 frontmatter / agents/openai.yaml  
- 需隐私/PII 保护  
- 需依赖锁定、错误码、mock 测试

---

## 总结

- **灰度可用**：impact / impact-pro 在 Claude Code 内部可人工监督使用  
- **禁止无人监督**：尤其 DB 写操作、跨模块操作  
- **优化方向**：SKILL.md 分层、触发词收紧、自动化回归、权限收紧、审计化 release  
- **vl-vision**：工具可用，Skill 未达生产级
