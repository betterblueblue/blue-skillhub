# T29 Go RealWorld Phase 5 执行演练包（待确认）

- 测试日期：2026-06-07
- 测试人：Codex
- 测试方式：真实项目 Phase 5 执行包准备
- 项目路径：`E:\agent\impact-pro-validation-work\go-gin-realworld`
- 项目栈：Go / Gin / GORM
- 目标：准备一次低风险真实写操作全流程，用于验证 Phase 5 的逐项确认、执行、验证和 `090-execution-record.md` 追加。
- 当前状态：待用户确认后执行；本轮未修改外部项目源码。
- 失败等级：无 P0/P1。

## 基线验证

T30 已在执行任何写操作前复跑验证命令，当前 Go RealWorld 基线通过：

```text
?    github.com/gothinkster/golang-gin-realworld-example-app [no test files]
ok   github.com/gothinkster/golang-gin-realworld-example-app/articles
ok   github.com/gothinkster/golang-gin-realworld-example-app/common
ok   github.com/gothinkster/golang-gin-realworld-example-app/users
```

外部验证仓源码保持干净。

## 候选变更

将 profile follow/unfollow 中“用户不存在”的错误文案从：

```text
Invalid username
```

调整为：

```text
Invalid profile username
```

## 定级

建议档位：light。

允许 light 的证据：

- 只涉及 API 错误文案，不改 DB schema、GORM model、migration、权限、认证、状态机或外部服务。
- 代码证据：
  - `users/routers.go` 中 `ProfileFollow` / `ProfileUnfollow` 返回 `common.NewError("profile", errors.New("Invalid username"))`。
  - `users/unit_test.go` 中对应断言期望 `{"errors":{"profile":"Invalid username"}}`。
- 验证命令已有 T24 运行时证据：Docker `golang:1.21` + 非 root + 临时 DB + `go test -p 1 ./...` 可全量通过。

触发 full 的证据：无。

未确认项：文案是否符合产品语气仍需用户确认。

## Phase 5 执行步骤

### Step 1: 修改 API 错误文案

- 确认类型：改代码
- 文件：`users/routers.go`
- 操作：将 `Invalid username` 改为 `Invalid profile username`
- 影响范围：仅影响 follow/unfollow 目标用户不存在时的 `profile` 错误文案
- 回滚方式：将文案改回 `Invalid username`
- 语义约定：不涉及 status/enum/权限/配置键；错误 key 保持 `profile`
- 验证方式：运行 `go test -p 1 ./...`
- 是否需要确认：是

### Step 2: 更新对应测试断言

- 确认类型：测试修复 / 改代码
- 文件：`users/unit_test.go`
- 操作：将两个期望响应中的 `Invalid username` 同步改为 `Invalid profile username`
- 影响范围：仅测试断言，不改变业务逻辑
- 回滚方式：将测试断言改回 `Invalid username`
- 语义约定：与 Step 1 的 API 文案保持一致
- 验证方式：运行 `go test -p 1 ./...`
- 是否需要确认：是

### Step 3: 自动验证

- 确认类型：只读/测试命令，无需额外确认
- 命令：

```powershell
docker run --rm -v "E:/agent/impact-pro-validation-work/go-gin-realworld:/src" -w /src --user 1000:1000 -e GOCACHE=/tmp/gocache -e GOPATH=/tmp/gopath -e DB_PATH=/tmp/go-realworld-phase5.db -e TEST_DB_PATH=/tmp/go-realworld-phase5-test.db golang:1.21 bash -lc "/usr/local/go/bin/go test -p 1 ./..."
```

- 预期：`articles`、`common`、`users` 通过
- 失败处理：只自动诊断；任何修复操作必须再次确认

### Step 4: 追加执行记录

- 确认类型：写文件
- 文件：外部验证仓 `change-impact/profile-invalid-username-copy/090-execution-record.md`
- 操作：按 `templates/090-execution-record.md` 记录确认、执行、验证和收尾状态
- 回滚方式：删除本次新增的 `change-impact/profile-invalid-username-copy/` 目录或追加回滚记录
- 验证方式：检查执行记录包含每步确认、影响、回滚和验证结果
- 是否需要确认：是

## 验收标准

本次演练只有在用户确认后实际执行，且满足下列条件，才能把第 6 条升级为”完整执行链路已有真实项目完成证据”：

- 每个写操作执行前均有独立确认。
- 外部项目源码变更与测试断言变更均可追溯到本次需求。
- Docker 全量测试通过，或失败后只诊断、不自动修复。
- `090-execution-record.md` 追加记录完整，不覆盖历史。
- 外部验证仓最终状态可解释：保留演练分支/变更，或按回滚方案清理。

## 当前结论

T29 已完成真实执行演练包准备，T30 已证明演练前基线为绿，但尚未执行写操作。

下一步需要用户明确确认是否允许在 `E:\agent\impact-pro-validation-work\go-gin-realworld` 中执行上述 Step 1、Step 2 和 Step 4。

可复制确认语句：

```text
确认 Step 1
确认 Step 2
确认 Step 4
```

模糊表述（如“可以”“继续”“都行”）不得触发写操作，必须按 Step 编号确认。
