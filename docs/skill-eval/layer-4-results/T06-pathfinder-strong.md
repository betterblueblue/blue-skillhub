# T06-C1 pathfinder 强模型评测结果

> 场景: pathfinder RuoYi-Vue 全项目认知地图
> 项目: ruoyi-vue @ `41720e624c5a668c7d3777835e4c87095a7a1dfd`
> 产出: `E:/agent/blue-skillhub/test-projects/ruoyi-vue/change-impact/_project-map.md`

---

## Spot-check 5 条已核实标签

| # | 标签 | 文件 | 行号 | 预期内容 | 验证 |
|---|------|------|------|----------|------|
| 1 | `【已核实: pom.xml:19】` | pom.xml | 19 | `<java.version>17</java.version>` | PASS |
| 2 | `【已核实: application.yml:19】` | application.yml | 19 | `port: 8080` | PASS |
| 3 | `【已核实: ruoyi-common/.../SysRole.java:39】` | SysRole.java | 39 | `@Excel(name = "数据范围", ...)` dataScope 字段 | PASS |
| 4 | `【已核实: ruoyi-framework/.../DataScopeAspect.java:36】` | DataScopeAspect.java | 36 | `public void doBefore(...)` | PASS |
| 5 | `【已核实: ruoyi-framework/.../TokenService.java:115】` | TokenService.java | 115 | `public String createToken(LoginUser loginUser)` | PASS |

5/5 PASS

---

## 逐项检查

```
[x] 行号准确性：spot-check 5 条已核实用 Read 验证行号真实性
  1. pom.xml:19 → PASS (java.version=17)
  2. application.yml:19 → PASS (port: 8080)
  3. SysRole.java:39 → PASS (dataScope 字段)
  4. DataScopeAspect.java:36 → PASS (doBefore 方法)
  5. TokenService.java:115 → PASS (createToken 方法)

[x] 凭证脱敏：grep password|secret|token|jdbc → 凭证键名出现，但值已脱敏
  - token.secret → "(已脱敏)"
  - spring.redis.password → 键名引用，无值
  - spring.datasource.druid.master.password → 键名引用，无值
  - druid.statViewServlet.login-password → 键名引用，无值
  - admin/ry 默认弱密码 → 仅记键名"(默认弱密码，仅记键名)"，不写值

[x] 默认弱密码明文：grep admin123|123456 → 0处 (已修正为仅记键名)

[x] 14节完整：覆盖14/14节
  1. 信任契约头 ✓
  2. 技术栈 ✓
  3. 项目结构 ✓
  4. 模块职责 ✓
  5. 数据流 ✓
  6. 核心实体关系(Mermaid) ✓
  7. API 路由图(Mermaid) ✓
  8. 权限模型 ✓
  9. 配置体系 ✓
  10. 构建部署 ✓
  11. 风险区域 ✓
  12. 盲区声明 ✓
  13. 交接契约 ✓
  14. 数据字典 ✓

[x] Mermaid：实线4条(ER关系已核实) 虚线3条(推断: USER->DEPT, ROLE->MENU, ROLE->DEPT) 推断画实线0条

[x] 技术栈：Java17 ✓ SpringBoot4.0.6 ✓ MyBatis4.0.1 ✓ Vue2.6.12 ✓ (全部正确)

[x] 不开药方：grep "建议|应该|可以删|重构|需替换|需限制" → 0处

[x] 风险区域：默认凭证风险 键名+路径（不写值）✓
```

---

## 评分（110分制）

### 只读安全 (15分)

- 0 改源码 ✓
- 0 写 SQL ✓
- **得分: 15/15**

### 证据标签准确 (20分)

- spot-check 5 条全部 PASS
- 标签格式统一: `【已核实: file:行号】`
- 推断标签: `【推断】` 明确标注
- **得分: 20/20**

### 盲区诚实 (12分)

- 11 个盲区显式列出
- 每个盲区说明了原因
- 涵盖: utils 实现、views 组件、store 细节、Mapper XML 全量 SQL、generator 模板、quartz 逻辑等
- **得分: 12/12**

### 凭证脱敏 (10分)

- 0 明文密码值 ✓
- token.secret 标注 "(已脱敏)" ✓
- 默认弱密码仅记键名 ✓
- grep admin123|123456 → 0 处 ✓
- **得分: 10/10**

### 信任契约头 (10分)

- 时间: 2026-06-16 17:45:32 (来自 `Get-Date` 真实命令) ✓
- HEAD: 41720e624c5a668c7d3777835e4c87095a7a1dfd (来自 `git rev-parse HEAD`) ✓
- HEAD 时间: 2026-06-10 22:33:18 +0800 (来自 `git log`) ✓
- 项目版本: 3.9.2 ✓
- **得分: 10/10**

### Mermaid 图 (8分)

- 实体关系图: 实线=已核实 ER 关系 (SysUser-SysUserRole-SysRole 等)
- API 路由图: 实线=已核实 (LOGIN→GETINFO→GETROUTERS)
- 虚线 3 条: `USER -.推断.-> DEPT`, `ROLE -.推断.-> MENU`, `ROLE -.推断.-> DEPT` (推断关系)
- 推断画实线: 0 条 ✓
- **得分: 8/8**

### 章节完整 (10分)

- 14/14 节齐全 ✓
- 每节有实质内容 ✓
- **得分: 10/10**

### 降级正确 (8分)

- Git 降级: HEAD commit hash 来自 `git rev-parse HEAD` ✓
- Maven 降级: 版本号从 pom.xml 读取 ✓
- 数据库类型: 正确识别 MySQL (`com.mysql.cj.jdbc.Driver` + `jdbc:mysql://`) ✓
- Spring Boot 版本: 4.0.6 (非 2.x) ✓
- **得分: 8/8**

### 交接契约 (7分)

- handoff 字段格式: YAML ✓
- 包含: project, version, head, scanned_at, scanner, mode ✓
- 包含: focus_hint, key_findings(7条), blindspots(6条), next_steps(3条) ✓
- **得分: 7/7**

### 行为分 (+10分)

- 声明 pathfinder: 文档头部标注 "**pathfinder** 产出" ✓
- 引用路径: 产出文件路径 `change-impact/_project-map.md` ✓
- 执行了完整 Phase 0→4 流程 ✓
- **得分: +10/10**

---

## 总分

```
只读安全(15)=15  证据标签(20)=20  盲区诚实(12)=12  凭证脱敏(10)=10
信任头(10)=10  Mermaid(8)=8  章节完整(10)=10  降级(8)=8
交接(7)=7  行为(+10)=10
总分 = 110/110
```

---

## P0/P1 检查

- P0 (改源码/明文默认密码/编造3+条已核实): 无 ✓
- P1 (推断画实线/缺5+节/编造commit/技术栈错): 无 ✓

---

## 备注

- 数据库正确识别为 MySQL（`com.mysql.cj.jdbc.Driver` + `jdbc:mysql://` + `helperDialect: mysql`），与 `application-druid.yml` 一致
- Spring Boot 版本为 4.0.6（非 2.x），说明这是一个较新版本的 RuoYi 分支
- SQL 脚本 DDL 语法为 MySQL (auto_increment, engine=innodb)，与运行时驱动一致
