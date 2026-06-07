# T19 next-learn/dashboard/final-example - 搜索框占位文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Next.js / App Router / Server Components / Client Components
- 项目路径：`E:\agent\impact-pro-validation-work\next-learn\dashboard\final-example`
- 变更意图：调整发票列表搜索框 placeholder 文案，不改搜索参数、查询逻辑或 DB。
- 使用档位：light
- 命中 profile：`frontend-nextjs`
- 最终评分：91
- 失败等级：无

## 实际发现

关键文件：

- `app/dashboard/invoices/page.tsx`：Server Component，向 `<Search placeholder="Search invoices..." />` 传入文案。
- `app/ui/search.tsx`：Client Component，使用 `useSearchParams`、`useRouter`、`useDebouncedCallback` 更新 `query` 和 `page`。
- `app/lib/data.ts`：`fetchFilteredInvoices()` 读取 `query` 并访问 DB；本变更不应修改。
- `app/ui/customers/table.tsx`：同一 Search 组件在 customers 场景也有 placeholder，用于判断是否只改 invoices。

## 验收判断

应判定 light。

理由：

- 只改 props 文案，不改 search params、URL 结构、debounce、SQL 查询或 Server Component 数据读取。
- 不需要 DB/migration。
- 需要确认是否同步 customers 搜索框文案，避免误改复用组件。

## 风险追问

1. 只改 invoices 页，还是所有使用 `Search` 的页面都改？
2. 新文案是否需要 i18n 或无障碍 label 同步？
3. 是否需要保留 `aria`/label 语义，避免只改 placeholder？

## 验证方案

- 静态检查：`app/dashboard/invoices/page.tsx` placeholder 更新，`app/ui/search.tsx` 逻辑不变。
- UI：搜索框显示新文案；输入关键字仍更新 `query` 并重置 `page=1`。
- 回归：customers 搜索框未被误改，除非需求明确要求。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | Search 是复用组件 | invoices 和 customers 都调用 `Search` | 文档明确变更范围，避免全局误改 |

## 结论

通过（light）。该用例补充 Next.js 样本第二变更，验证 profile 能在含 Server Component/DB 的项目中识别 UI-only 文案变更。
