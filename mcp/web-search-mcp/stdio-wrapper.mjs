// stdio 净化壳：web-search-mcp 会把启动日志写到 stdout，污染 MCP 协议。
// 本壳只把 JSON-RPC 行（以 { 开头）转发给 MCP host，其余输出转到 stderr。
import { spawn } from "node:child_process";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const dir = dirname(fileURLToPath(import.meta.url));
const child = spawn(process.execPath, [join(dir, "dist", "index.js")], {
  env: process.env,
  stdio: ["pipe", "pipe", "inherit"],
});

const rl = readline.createInterface({ input: child.stdout });
rl.on("line", (line) => {
  const t = line.trim();
  if (t.startsWith("{") && t.endsWith("}")) {
    process.stdout.write(line + "\n");
  } else {
    process.stderr.write("[web-search-log] " + line + "\n");
  }
});

process.stdin.pipe(child.stdin);

child.on("exit", (code, sig) => process.exit(code ?? 0));
process.on("exit", () => { try { child.kill(); } catch {} });
