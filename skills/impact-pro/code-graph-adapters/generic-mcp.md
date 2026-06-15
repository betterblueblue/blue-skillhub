# Code Graph Adapter: generic MCP

> Optional Phase 2 enhancer for structured code graph / tree-sitter MCP tools.
> If no suitable tool is visible at runtime, this adapter is skipped and normal
> `rg` / `git grep` discovery remains the source of truth.

## Capability contract

Use a code-graph MCP only when the currently available tools can answer at
least one of these read-only questions with file/line evidence:

- find definition for a symbol, route, permission key, config key, schema/model,
  component, generated type, or test entry
- find references / callers / callees for a target symbol
- return import/export or dependency edges between files/modules
- return route, handler, middleware, or registration edges

Do not assume availability from a vendor name. Known examples may include
tree-sitter, code-impact, qartez, not-ace, or similar MCPs, but the decision is
based on the visible tool capability, not the label.

## Runtime probe

During Phase 2, before broad text fallback:

1. Inspect the available MCP tools/resources for read-only code graph capability.
2. If a candidate exists, run the smallest query that identifies the target:
   - exact symbol/name first
   - then enclosing file or module
   - then route/config/permission key shape
3. Record the adapter status:
   - `code_graph: used` with tool name, query, and returned evidence
   - `code_graph: unavailable` when no matching MCP exists
   - `code_graph: failed` when the tool errors or returns unusable evidence
   - `code_graph: degraded` when the tool returns partial, stale, or truncated evidence
4. Always verify graph hits by reading the referenced file snippets. Graph output
   is a candidate set, not final proof.
5. If the graph is unavailable, failed, incomplete, or too vague, immediately
   degrade to `rg` / `git grep` / filename search and mark the downgrade.

## Freshness and result integrity

- If the MCP exposes status/freshness tools, call them before trusting graph
  evidence. If status reports stale, warming, pending changes, or an explicit
  "refresh first" action, refresh when it is read-only; otherwise mark
  `code_graph: degraded` and fall back to text search.
- If the MCP returns `total`, `truncated`, `limit`, `offset`, or similar paging
  metadata, record it. Page or narrow the query when the impacted set is large;
  do not silently treat the first page as the complete impact set.
- Treat graph edges as lower-bound evidence. Dynamic dispatch, reflection,
  generated code, framework routing, SQL strings, config keys, templates, and
  front-end string contracts often require `rg` / `git grep` confirmation.
- An empty caller/reference result is never sufficient proof that a symbol,
  route, field, or config key is unused. Write the empty result as evidence and
  still perform the fallback search before declaring no impact.

## Read-only and write boundary

- Only read-only graph queries are allowed in Phase 2.
- If an MCP wants to create or update an index inside the target project, treat
  that as a write operation and do not run it without a `确认 Step N`.
- Tool-managed caches outside the target project may be used only when the tool
  performs them implicitly and no project files are changed.
- Do not run code generators, formatters, dependency installers, or migrations
  as part of code-graph discovery.

## Evidence output

Add a short block to the Context Pack / discovery record:

```text
code_graph:
  status: used | unavailable | failed | degraded
  tool: <visible tool name or "none">
  query: <symbol/route/config key searched>
  evidence:
    - <path>:<line> <relationship>
  verified_by:
    - Read <path>:<line-range>
  downgrade_reason: <only when unavailable/failed/degraded>
```

## Reference classification

Classify graph hits with the same four buckets as text search:

| Bucket | Meaning |
|--------|---------|
| must_sync | skipping it will break compile/runtime/API/test compatibility |
| user_decision | compatibility, old consumer, data, or business wording decision |
| verify_only | referenced but semantics are unchanged |
| out_of_scope | inspected and unrelated; record why |

Never write "no impact" solely because the graph returned nothing. Write
"code graph found no references; `rg` / `git grep` fallback still required" and
then perform the fallback.
