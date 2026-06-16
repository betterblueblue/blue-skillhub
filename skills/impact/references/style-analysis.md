# 代码风格分析

## 基础层（始终执行，Git 可用时优先）

- Git 可用：
  1. `git log --oneline -20 -- <module_path>` 获取 commit 列表
  2. 对每条 commit 先跑 `git show --stat <hash>` 预筛：跳过无关 commit（如仅改文档/配置的 commit）
  3. 对筛选后的 commit 跑 `git show <hash>` 取 diff，**每条 diff 限制 <= 200 行**，超出则截断并记录
  4. 从 diff 中提取：类/方法命名、Lombok 使用、依赖注入方式、`@Transactional` 位置、异常风格、日志框架+占位符、API 响应包装、分层模式、DTO/VO 使用
- Git 不可用：扫描代表性文件（Service/Controller/Entity/Config 各 1-2 个）+ `.editorconfig`/`checkstyle`/`pmd`
- **Token 上限**：<= 20 条 diff（每条 <= 200 行）或 <= 6 个文件，超出提示用户

## 深入层（仅本次涉及的维度，每维度 <= 3 文件）

代码、数据库、接口、配置、日志、事务、安全、测试、包结构、空值处理、常量定义、时间处理等。

提取内容：命名规范、Lombok 使用、依赖注入方式、`@Transactional` 位置、异常风格、日志框架+占位符、API 响应包装、分层模式、DTO/VO 使用。

## Phase 4 衔接约束

Phase 2 风格发现的 200 行截断是合理的 token 预算控制。但 **Phase 4 设计文档**中的代码风格报告要求**完整、未截断**的参考代码片段（见 SKILL.md Phase 4 "设计文档的「代码风格报告」"段）。从 Phase 2 到 Phase 4 的衔接规则：Phase 2 可截断采样，但写入设计文档时必须回读原始文件取完整片段，不得直接复制 Phase 2 的截断结果。
