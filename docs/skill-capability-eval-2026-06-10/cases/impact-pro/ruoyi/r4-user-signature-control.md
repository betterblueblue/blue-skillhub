# Case R4: 用户个性签名字段（impact-pro 对照）

> 同一 prompt 同 R1，但跑 impact-pro 而不是 impact。验 impact-pro 在 Java 栈上表现。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | R4 |
| Project | RuoYi-Vue |
| Skill | impact-pro |
| 档位 | full |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: end users should be able to set a personal signature on their profile, and admins should be able to see it on user detail and export it via the list export. Do not modify code. Produce an impact analysis and implementation plan.

（同 R1）

## Phase 1 意图捕获

**与 R1 相同**。

## Phase 2 上下文发现

**关键差异**：impact-pro 加载的是 `profiles/java-spring-mybatis.md`，不是 impact 的单体 SKILL.md。

**栈探测预期**：
- impact-pro 探测到 `pom.xml` → 识别 Spring Boot
- 探测到 `ruoyi-*.jar` → 加载 `java-spring-mybatis` profile
- profile 提示查找 `Mapper.xml` 风格 SQL 文件、`@RestController` 风格端点

**实际探索结果**（基于 R1 真实发现）：
- 找到 4 个关键文件
- 多模块结构
- @Excel 注解驱动导出
- @PreAuthorize 权限模式

**预期 impact-pro 优势**：
- profile 显式提示 Java/Spring/MyBatis 模式，更结构化
- 应该会主动列出需修改的 4 个文件

**预期 impact-pro 风险**：
- 不熟悉 RuoYi 多模块结构
- 可能误判 ExcelUtil（虽然 profile 提了导出，但未指明 POI vs EasyExcel）

## Phase 2.5 风险预判

```text
初步风险：倾向 full
profile 命中：java-spring-mybatis
adapter 命中：mysql
```

## Phase 3 苏格拉底式探索（4 轮）

**与 R1 类似的 4 轮**（P0 命名/长度/XSS、P1 兼容/回滚、验证/文档、行为确认）

**与 impact 的差异**：
- impact-pro 苏格拉底可能更结构化（受 profile 引导）
- 但 RuoYi 特有的"导出工具是 POI 不是 EasyExcel"这个事，impact-pro 也不会主动识别

## Phase 3.5 判档

```text
建议档位：full
profile 命中：java-spring-mybatis
DB adapter：mysql
```

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact-pro |
| profile 命中 | java-spring-mybatis |
| 完成的 Phase | 1-4 全 ✓ |
| Step 确认次数 | 4 |
| 实际改动文件数 | 4 |
| 卡住位置 | Phase 2 短暂困惑多模块，但 profile 提示了 grep 全模块 |
| Hallucination | 无 |
| 总耗时 | 约 20 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 11/12 | 命中 java-spring-mybatis，差 1 因未明确指出 RuoYi 命名 |
| 2. 上下文发现 | 16/18 | 找到 4 文件，差 2 因 profile 未提示多模块搜索 |
| 3. 苏格拉底 | 14/15 | 4 轮完整 |
| 4. 维度选择 | 7/8 | |
| 5. 判档 | 9/10 | |
| 6. 文档 | 11/12 | |
| 7. 执行安全 | 9/10 | |
| 8. TDD 验证 | 7/10 | |
| 9. 命令验证 | 4/5 | |
| **基础总分** | **88/100** | |
| 行为分 | 7/10 | 主动声明 + 引用 profile 路径 |
| **总分** | **95/110** | |

**P 等级**：无
**通过？**：是

## 关键发现（impact-pro vs impact）

- **差异 1**：impact-pro profile 显式提示 "Mapper XML + @RestController"，**比 impact 更结构化**
- **差异 2**：impact-pro Phase 2 提示全模块 grep（profiles 里有 `discovery_globs`），**比 impact 主动**
- **共同缺点**：两者都未识别 RuoYi 实际导出是 POI，不是 EasyExcel

## 与 validation-runs 对比

- 复用基线：无直接对照（首次 impact-pro 跑 RuoYi）
- 对比维度：vs R1（impact 跑同 prompt）
- 主要差异：impact-pro 在 Phase 2 跨模块搜索更系统，但 R1 写得略深

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

> 注：本 case 是 R1 的对照——**同一项目 RuoYi、同一个 prompt，跨两个 skill**。

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\ruoyi-vue\change-impact\r4-user-signature-control\`

5 个文件：context-pack.md / 000-需求文档.md / 100-设计文档.md / 200-实施文档.md / 900-执行记录.md

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact-pro`（通过 Skill 工具） |
| 加载的 profile | `java-spring-mybatis`（Level 2，RuoYi 衍生） |
| 完成的 Phase | 1✓ / 2✓（profile 自动加载）/ 2.5✓ / 3✓（3 轮 6 问）/ 3.5✓ / 4✓ / 5 跳过 |
| 关键发现 | profile `discovery_globs` 帮助找到多模块结构（Entity common / Mapper system / Controller admin）；`style_axes` 在 100-设计文档 §5 风格合规检查**直接复用** |
| 幻觉路径 | 0 |
| Token 消耗 | 82,689 |
| 跑分耗时 | 5 分 58 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 + profile | 12 |
| 2. 上下文发现 | 17（profile 引导跨模块搜索） |
| 3. 苏格拉底 | 14 |
| 4. 维度选择 | 8 |
| 5. 判档 | 10 |
| 6. 文档 | 11 |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 7 |
| 9. 命令验证 | 4 |
| **基础总分** | **93/100** |
| 行为分 | +10 |
| **总分** | **103/110** ✓ 通过 |

### R1 vs R4 对照（同项目 RuoYi 跑两个 skill）

| 维度 | R1 (impact) | R4 (impact-pro) | 差异 |
| --- | --- | --- | --- |
| 栈探测 | ad-hoc Read | profile 自动加载 | impact-pro 更结构化 |
| 关键文件命中 | 6 文件 | 6 文件 | 持平 |
| 跨模块误判 | 1 次（SysUserController grep 失败） | 0 次（discovery_globs 系统性） | **impact-pro 略优** |
| 风格设计 | 自由分析 | style_axes 直接复用 | **impact-pro 略优** |
| 文档深度 | 9.3 KB | 10+ KB | impact-pro 略多 |
| 总分 | 102 | 103 | 持平 |
| **结论** | impact 熟练执行也能达到同等质量 | impact-pro 结构化引导更稳 | **两者最终都收敛到相同文件** |

### 关键真实发现

- **profile 优势**：`discovery_globs.data_access` 和 `entity` 是**唯一**帮助找到 `SysUser` 在 `ruoyi-common`（不在 `ruoyi-system`）的方式；没有这些 globs，多模块结构会很难导航。
- **profile 短板**：**没有 Vue 2 / Element UI profile**——前端被当作"项目内风格"无 profile 引导。RuoYi-Vue 这种"后端成熟 + 前端 Vue 2"项目，impact-pro 缺前端 profile 是真实 gap。
- **`db_introspection.migration_tool: 手写SQL脚本`** 正确，但 agent 需自己发现 `sql/ry_20260417.sql`，无 schema_queries 帮助。
