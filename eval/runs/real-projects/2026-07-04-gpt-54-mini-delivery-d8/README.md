# 影响分析结论

这次需求是“把登录失败时返回的错误提示文案改得更清楚”。按当前仓库现状，我判断为 **light**。

理由很直接：

- 登录失败的错误文案是服务层里直接抛出的字符串，不涉及数据库结构、接口参数、权限、状态机或枚举值。
- 现有登录失败路径集中在 `src/services/auth.service.ts` 的 `login()`。
- 控制器只是把服务层结果原样返回，`src/controllers/auth.controller.ts` 不额外改文案。
- 统一错误处理中间件在 `src/index.ts`，只负责把 `HttpException` 转成 HTTP 响应，不需要改业务语义。
- 相关测试已经在 `tests/services/auth.service.test.ts` 覆盖了“账号或密码无效”这条失败路径，适合只做局部更新。

## 建议重点检查的文件

1. `src/services/auth.service.ts`
   - `login()` 里的 `throw new HttpException(403, { errors: { 'email or password': ['is invalid'] } })`
   - 这里就是登录失败提示文案的来源。

2. `src/controllers/auth.controller.ts`
   - `/users/login` 路由只是调用 `login()`，一般不用改，但要确认没有二次包装错误信息。

3. `src/index.ts`
   - 统一错误处理中间件决定 `HttpException` 怎么被转成响应。
   - 如果文案格式要改，这里是确认返回形态的地方。

4. `tests/services/auth.service.test.ts`
   - `login` 相关用例里已经有“用户不存在”和“密码错误”的断言。
   - 改文案时，需要同步看这些断言是否还匹配。

5. `docs/swagger.json`
   - 这里只是接口说明，当前看不到登录失败的具体错误文案，但可以顺手确认文档有没有写死旧提示。

## 结论

- 档位：**light**
- 影响范围：主要是 `src/services/auth.service.ts` 的登录失败返回文案
- 不确定项：没有发现会牵动 DB、接口契约或前端展示层的证据

