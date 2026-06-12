# impact skill — tests/scenarios/

回应 gpt5.5pro 评审 P0 #3「缺可重复自动化验收」。

## 设计

`skills/impact/tests/scenarios/` 下的每个 JSON 文件是一个**可重放的回归场景**：

- **fixture**：真实开源项目（已 clone 到 `test-projects/`，含 commit 哈希）
- **query**：模拟用户输入的变更请求
- **expected**：期望 skill 在 Phase 3.5 给出的判档 + 铁律触发 + 引用加载
- **trap_for**：这条场景要抓的现实陷阱（未来 reviewer 知道在测什么）
- **files_to_inspect**：fixture 中必须存在的关键证据

## 跑法

```bash
cd skills/impact/tests
./run.sh
```

**当前能力（v1，静态层）**：
- 校验每个 scenario JSON 格式
- 校验 fixture 存在 + commit 哈希匹配
- 校验 SKILL.md 中含期望的 iron rule
- 校验 references 实际存在
- 校验 fixture 中"必须存在"的文件/字符串
- 校验 scenario 中 `expected.iron_rules_triggered` 至少 1 条

**未来能力（v2，LLM 集成层）**：
- 调用 Claude API 跑 skill，对比实际输出 vs `expected.phase_3_5_classification`
- 这部分需要 API key + cost 控制，**暂不实现**

## 目录结构

```
skills/impact/tests/
├── README.md                        # 本文件
├── scenarios/
│   └── java-spring-mybatis/         # 按栈分目录
│       ├── 001-*.json
│       ├── 002-*.json
│       └── ...
├── fixtures/
│   └── README.md                    # fixture 来源与版本
├── run.sh                           # 主 runner
└── lib/
    └── validate.sh                  # 校验函数
```

## 编写新场景

参考 `scenarios/java-spring-mybatis/001-*.json` 的字段，遵循：

1. `id` 用 `栈-动词-对象-NNN` 命名
2. `query` 必须**真实可发音**（用户真会这么问）
3. `expected.iron_rules_triggered` 必须从 SKILL.md 铁律区**真实存在**的条目中选
4. `expected.phase_3_5_classification` 必须是 `light` 或 `full`，且**附 rationale**
5. `trap_for` 至少写一条，描述这条场景要抓的现实陷阱
6. `files_to_inspect[].must_contain` 至少 1 个真实字符串（不要"should contain"占位）

## 版本基线

- 当前场景基于 `E:\agent\blue-skillhub\test-projects\ruoyi-vue` @ commit `41720e6`
- fixture 必须先 clone 到该路径才能跑
- 跑之前用 `git -C test-projects/ruoyi-vue rev-parse HEAD` 校验
