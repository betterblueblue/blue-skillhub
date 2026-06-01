# Blue SkillHub

> 个人 AI 技能库 —— 存放自用的 Claude Code Skill 与项目级行为准则

## 目录结构

```
.
├── ruleblade/          # 律刃 —— AI 编码行为准则
│   ├── CLAUDE.md       # 可直接用于 Claude Code 的项目级行为准则
│   └── README.md       # 律刃的迭代历程与设计文档
└── README.md           # 本文件
```

## 项目说明

这个仓库是我个人的 AI 技能与工具集合，主要包含：

- **ruleblade/** —— 经过实验验证的 AI 编码行为准则（律刃 v3），用于指导 Claude Code 等 AI 助手在编码任务中的精准行为

## 使用方式

将 `ruleblade/CLAUDE.md` 复制到你的项目根目录，Claude Code 会自动读取并遵循其中的行为准则。

## 关于律刃

律刃是一套经过 A/B 实验淬炼的 7 条中文祈使句规则，核心设计原则：

- **实验验证**：每条规则都有可归因的实验证据，不是拍脑袋
- **写法优先**：祈使句 > 描述句，短指令 > 长解释
- **ROI 甜点**：7 条规则是边际效益最优点
- **分级适用**：按任务规模决定检查哪些规则

详见 [`ruleblade/README.md`](ruleblade/README.md)。
