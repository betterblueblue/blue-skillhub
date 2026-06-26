# Round 17: Next.js DB 前置条件 build 复验

## 背景

T11 和 Round 7 已证明 `next build` 会执行 App Router Server Component 的数据读取：无 Postgres 时编译和 TypeScript 阶段通过，但预渲染 `/dashboard` 因 `ECONNREFUSED` 失败。本轮补齐可用 Postgres，验证该失败是否只是运行前置条件，还是 `frontend-nextjs` profile 的真实缺口。

## 数据库前置条件

由于样本代码中 `postgres(process.env.POSTGRES_URL!, { ssl: 'require' })` 写死了 SSL，本轮使用 Docker 启动开启 SSL 的 Postgres 16：

```powershell
docker run -d --name impact-pro-next-postgres -p 55432:5432 -e POSTGRES_USER=nextuser -e POSTGRES_PASSWORD=nextpass -e POSTGRES_DB=nextlearn --entrypoint bash postgres:16 -lc "export PATH=/usr/lib/postgresql/16/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin && openssl req -new -x509 -days 1 -nodes -text -subj '/CN=localhost' -out /var/lib/postgresql/server.crt -keyout /var/lib/postgresql/server.key >/dev/null 2>&1 && chown postgres:postgres /var/lib/postgresql/server.crt /var/lib/postgresql/server.key && chmod 600 /var/lib/postgresql/server.key && exec docker-entrypoint.sh postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key"
```

随后按 `app/seed/route.ts` 和 `app/lib/placeholder-data.ts` 创建 `users`、`customers`、`invoices`、`revenue` 表并灌入示例数据。

## Build 复验

执行目录：

```text
E:\agent\impact-pro-validation-work\next-learn\dashboard\final-example
```

执行命令：

```powershell
$env:POSTGRES_URL='postgresql://nextuser:nextpass@localhost:55432/nextlearn?sslmode=require'
$env:POSTGRES_PRISMA_URL=$env:POSTGRES_URL
$env:POSTGRES_URL_NON_POOLING=$env:POSTGRES_URL
$env:POSTGRES_USER='nextuser'
$env:POSTGRES_HOST='localhost'
$env:POSTGRES_PASSWORD='nextpass'
$env:POSTGRES_DATABASE='nextlearn'
$env:AUTH_SECRET='impact-pro-validation-secret-impact-pro-validation-secret'
$env:AUTH_URL='http://localhost:3000/api/auth'
pnpm run build
```

结果：通过。

```text
✓ Compiled successfully
Running TypeScript ...
Collecting page data using 19 workers ...
✓ Generating static pages using 19 workers (12/12)
Finalizing page optimization ...
```

路由输出包含 `/dashboard`、`/dashboard/customers`、`/dashboard/invoices`、`/dashboard/invoices/[id]/edit`、`/query`、`/seed` 等页面/Route Handler。

## 警告

构建仍有非阻塞治理警告：

- `baseline-browser-mapping` 数据超过两个月。
- `Browserslist/caniuse-lite` 数据陈旧。
- Next.js 推断 workspace root 时发现多个 lockfile，建议显式配置 `turbopack.root` 或清理无用 lockfile。

这些不是 `frontend-nextjs` profile 的阻塞缺陷，但在真实项目分析中应作为项目治理/构建稳定性提醒记录。

## 结论

T11 从“有条件通过”提升为“通过”：`frontend-nextjs` profile 对 App Router + Server Actions + NextAuth + Postgres 样本的发现和风险判断成立；完整 build 在补齐 SSL Postgres、schema 和 seed 数据后通过。

该结论不等同于 Next.js profile 达到 Level 2：当前仍只有 Next Learn 单项目样本，生产级 Next monorepo、Pages Router、API Routes、不同 DB/ORM 组合仍需继续复验。
