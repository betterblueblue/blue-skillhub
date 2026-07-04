# 影响分析：`PROJECT_NAME` -> `APP_NAME`

## 结论
这次变更不是单点替换，而是一个跨配置、启动入口、邮件内容和项目生成器的环境变量重命名。

我的判断是：**倾向 full**。理由很简单，`PROJECT_NAME` 不是只出现在一处文案里，而是同时被 FastAPI 启动配置、邮件主题/正文、部署说明、Copier 生成流程引用；如果只改代码不改生成器，新项目的 `.env` 还会继续落出旧键名。

本次只做只读分析，没有改源码、测试、配置或数据库。

## 已确认事实
- 后端配置里直接定义了 `PROJECT_NAME`，并且在缺省邮件发件人名称里回填它。证据：`E:\agent\real-project-fixtures\python-fastapi-template\backend\app\core\config.py:50-82`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\backend\app\core\config.py:50-82】
- FastAPI 应用标题直接取自 `settings.PROJECT_NAME`，所以这个键改名后，`/docs` 和 OpenAPI 标题会跟着变。证据：`E:\agent\real-project-fixtures\python-fastapi-template\backend\app\main.py:17-19`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\backend\app\main.py:17-19】
- 三类邮件都把 `settings.PROJECT_NAME` 拼进了主题或模板上下文。证据：`E:\agent\real-project-fixtures\python-fastapi-template\backend\app\utils.py:58-100`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\backend\app\utils.py:58-100】
- 邮件模板源文件里使用的上下文变量名是 `project_name`。这不是环境变量本身，但如果你想把命名一起统一，模板源和生成后的 HTML 也要跟着改。证据：`E:\agent\real-project-fixtures\python-fastapi-template\backend\app\email-templates\src\test_email.mjml:5`、`reset_password.mjml:5`、`new_account.mjml:5`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\backend\app\email-templates\src\test_email.mjml:5】
- 部署文档明确把 `PROJECT_NAME` 当成需要设置的环境变量。证据：`E:\agent\real-project-fixtures\python-fastapi-template\deployment.md:176-180`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\deployment.md:176-180】
- 顶层 README 里也把 `project_name` 作为生成项目时的输入变量说明了一遍。证据：`E:\agent\real-project-fixtures\python-fastapi-template\README.md:195-199`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\README.md:195-199】
- Copier 的问答键会被 `.copier/update_dotenv.py` 直接转成大写环境变量名写回 `.env`。证据：`E:\agent\real-project-fixtures\python-fastapi-template\copier.yml:1-4`、`E:\agent\real-project-fixtures\python-fastapi-template\.copier\update_dotenv.py:7-21`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\copier.yml:1-4】

## 影响范围
| 维度 | 现状 | 影响 | 处理建议 |
|---|---|---|---|
| 数据产生点 | `settings.PROJECT_NAME` 从环境变量读取 | 改名后所有读取点都要换成 `APP_NAME` | 必须同步修改 |
| 状态/字段定义 | 没有数据库字段 | 无表结构影响 | 可排除 |
| 持久化位置 | `.env` 由 Copier 生成或更新 | 生成器如果不改，仍会写旧键名 | 必须同步修改 |
| 对外接口 | FastAPI 标题和邮件内容会展示这个值 | 用户可见文案会变 | 必须同步修改 |
| 前端展示 | 未找到前端直接读取该键的代码 | 前端无需改动 | 可排除 |
| 导出/报表 | 未找到相关链路 | 无影响证据 | 可排除 |
| 测试入口 | 未找到直接断言 `PROJECT_NAME` 的测试 | 回归要靠启动和静态检查补上 | 需要验证 |

## 需要同步改的地方
1. `backend/app/core/config.py`
   - 把设置字段 `PROJECT_NAME` 改成 `APP_NAME`。
   - 继续保持邮箱默认发件人名字跟应用名一致。

2. `backend/app/main.py`
   - `FastAPI(title=...)` 改为取 `settings.APP_NAME`。

3. `backend/app/utils.py`
   - 邮件主题和模板上下文都要从 `settings.APP_NAME` 取值。
   - 如果你想把模板变量名也统一，`project_name` 这个上下文键要一并改掉；如果不统一，运行时也能工作，只是内部命名还保留旧字样。

4. `backend/app/email-templates/src/*.mjml`
   - 只有在你决定连模板上下文键一起改名时才需要改。
   - 如果只改环境变量和 Python 端映射，这些模板可以保留。

5. `copier.yml`
   - 生成器输入键现在是 `project_name`，它会继续导出 `PROJECT_NAME`。
   - 如果目标是让新项目从一开始就写 `APP_NAME`，这里需要把输入键也改成 `app_name`，或者在生成脚本里加显式映射。

6. `.copier/update_dotenv.py`
   - 这是生成 `.env` 的最后一道门。
   - 只改 `.env` 文案不改这里，新项目还是会被回写成旧变量名。

7. `deployment.md` 和 `README.md`
   - 这两处是对外说明，必须跟着改，不然文档会继续教人填旧键名。

## 明确排除项
- 数据库 schema、迁移、索引、外键：未找到任何关联证据。
- 前端页面和前端客户端生成物：未找到直接读取 `PROJECT_NAME` 的代码。
- 权限、状态机、错误码：本次没有触及。
- `backend/tests`、`frontend/tests`：我没有找到直接锁定 `PROJECT_NAME` 的断言，所以现阶段更像是运行回归，而不是改测试逻辑本身。`backend/tests/conftest.py` 只是导入了 `settings`，没有直接引用这个键。证据：`E:\agent\real-project-fixtures\python-fastapi-template\backend\tests\conftest.py:7-41`【已核实: E:\agent\real-project-fixtures\python-fastapi-template\backend\tests\conftest.py:7-41】

## 风险判断
这个变更的坑点不在代码量，而在“名字要改干净”。

最容易漏的是 Copier 这条线：代码里换成 `APP_NAME` 以后，如果生成器还在写 `PROJECT_NAME`，新创建的项目会出现旧键名回流。另一个容易漏的是部署文档，文档不改会直接误导后续部署配置。

我没有发现需要用户拍板的业务选择，只有一个实现层面的统一口径问题：
- 要不要把邮件模板里的上下文键 `project_name` 也一起改成 `app_name`？

如果只追求运行一致性，这不是必须项。
如果追求命名一致性，这一组模板也该一起换。

## 验证情况
当前是只读分析，已完成的验证属于静态证据层，等级可以算 **V1**。

已运行的命令：
- `git status --short`，退出码 `0`
- `rg -n "PROJECT_NAME|APP_NAME|os\\.getenv\\(|os\\.environ\\[|Settings|BaseSettings|pydantic_settings" .`，退出码 `0`
- `rg -n "PROJECT_NAME" backend deployment.md README.md frontend .copier copier.yml compose.yml compose.override.yml compose.traefik.yml scripts hooks tests`，退出码 `1`
- `rg -n "APP_NAME" backend deployment.md README.md frontend .copier copier.yml compose.yml compose.override.yml compose.traefik.yml scripts hooks tests`，退出码 `1`
- `rg -n "project_name|PROJECT_NAME|APP_NAME" .copier hooks backend deployment.md README.md frontend compose.yml compose.override.yml compose.traefik.yml scripts`，退出码 `0`
- 若干 `Get-Content` 取证命令，均退出码 `0`

## 最终判断
**UNVERIFIED**

原因不是证据不够，而是这次按你的要求只做了影响分析，没有进入实现，也没有跑 `impact_validate.py` 或任何写入后的回归验证。
