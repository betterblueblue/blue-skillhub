# 目录结构参考

> 从 SKILL.md 移出，供需要时查阅。

```
impact/
├── SKILL.md              # 通用内核
├── profiles/             # 技术栈规则（按需加载）
│   ├── _schema.md        # 技术栈规则接口定义
│   ├── _template.md      # 新技术栈规则模板
│   ├── generic.md         # 通用备用规则
│   ├── java-spring-mybatis.md
│   ├── node-express-prisma.md
│   ├── python-fastapi-sqlmodel.md
│   ├── frontend-react-vite.md
│   ├── frontend-nextjs.md
│   ├── frontend-nuxt-vue.md
│   ├── go-gin-gorm.md
│   └── dotnet-aspnet-efcore.md
├── db-adapters/          # 数据库适配器
│   ├── generic-sql.md
│   ├── mysql.md
│   └── postgresql.md
├── code-graph-adapters/  # 可选代码图适配器
│   └── generic-mcp.md
├── references/           # 详细执行规则（按需加载）
├── templates/            # 文档模板
└── README.md
```
