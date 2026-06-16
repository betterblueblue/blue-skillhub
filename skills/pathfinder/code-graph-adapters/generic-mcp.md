# Code Graph Adapter: Pathfinder generic MCP

> Optional Phase 2 enhancer for read-only repository structure indexes.
> If no suitable tool is visible at runtime, skip this adapter and continue with
> normal Glob/Grep/Read discovery.

## Capability contract

Use a code-graph or repo-map MCP only when the visible tools can answer at least
one of these read-only questions with paths, line numbers, or explicit graph
metadata:

- project overview, high-signal files, entry points, scripts, or served roots
- bounded directory tree for a path/depth
- import/export/dependency edges between files or modules
- reverse dependents / impact set for a file or module
- hubs / central modules / likely reading entry points
- route, handler, middleware, CLI, job, or registration locations

Do not assume availability from a vendor name. Decide from the visible tool
capabilities and returned evidence.

## Runtime probe

During Phase 2, after stack manifest detection and before manual breadth scan:

1. Inspect available MCP tools/resources for read-only repository graph
   capability.
2. If a candidate exists, call the smallest structure query first:
   - project context / overview if available
   - otherwise bounded tree for the project root
   - then hubs / entry points / imports for likely core directories
3. Record adapter status:
   - `code_graph: used` with tool name, query, and evidence
   - `code_graph: unavailable` when no matching MCP exists
   - `code_graph: failed` when the tool errors or returns unusable evidence
   - `code_graph: degraded` when results are stale, partial, or truncated
4. Verify every map fact that will be labeled `【已核实】` by reading the
   referenced file/manifest snippet. Graph output is a candidate set, not final
   proof.
5. If unavailable/failed/degraded, continue with normal Glob/Grep/Read and note
   the downgrade in the map's blind spots or discovery notes.

## Freshness and result integrity

- If the MCP exposes status/freshness tools, call them before trusting graph
  output. If status says stale, warming, pending changes, or "refresh first",
  refresh only when the refresh is read-only and does not change project files.
- If results include `total`, `truncated`, `limit`, `offset`, or similar paging
  metadata, record it. Page or narrow the query for core modules; do not treat a
  truncated first page as full project coverage.
- Treat graph edges as lower-bound evidence. Dynamic imports, reflection,
  framework routing, generated code, SQL strings, config keys, templates, and
  non-code assets still require text/file verification.
- Empty dependents/callers does not prove "unused". Mark it as an observation and
  keep the item in `【13】没挖深的部分` unless fallback search also supports it.

## Read-only boundary

- Pathfinder is read-only except for `change-impact/_project-map.md`.
- Do not initialize or update a project-local index such as `.codegraph/`,
  `.repomapper/`, `.cache/`, or similar under the target project.
- Tool-managed caches outside the target project may be used only when the tool
  performs them implicitly and no target project files are changed.
- Never run generators, dependency installers, formatters, migrations, or build
  commands as part of graph discovery.

## Map output

Add a concise discovery note to `_project-map.md` when graph tools are used:

```text
结构索引辅助:
  status: used | unavailable | failed | degraded
  tool: <visible tool name or "none">
  query: <overview/tree/hubs/imports/dependents query>
  coverage: <complete / truncated / scoped path / unknown>
  verified_by:
    - Read <path>:<line-range>
  downgrade_reason: <only when unavailable/failed/degraded>
```

Use graph evidence to improve these sections first:

- 【3】架构分层 / 模块地图
- 【5】关键入口
- 【8】构建·运行·测试
- 【9】风险区域 / 风险区
- 【11】典型主流程
- 【13】没挖深的部分
