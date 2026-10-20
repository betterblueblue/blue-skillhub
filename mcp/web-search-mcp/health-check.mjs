#!/usr/bin/env node
// web-search-mcp 引擎自检。
//
// 用途：搜索引擎的解析器依赖对方页面结构，对方改版就会静默失效；而搜索本身
// 因为有兜底引擎，整体看起来仍然"能用"。这个脚本逐台单独测，把「解析器坏了」
// 和「被限流」分开报告 —— 两者处理方式完全不同。
//
// 用法：
//   node health-check.mjs            # 检查全部引擎
//   node health-check.mjs --quiet    # 只在有故障时输出（适合定时任务）
//   node health-check.mjs --json     # 机器可读
//   node health-check.mjs --engine google   # 只测一台
//
// 退出码：0 = 无引擎故障；1 = 至少一台引擎「解析失效」或「报错」。

import { SearchEngine } from './dist/search-engine.js';

const QUIET = process.argv.includes('--quiet');
const JSON_OUT = process.argv.includes('--json');
const ENGINE_FILTER = (() => {
  const i = process.argv.indexOf('--engine');
  return i >= 0 ? process.argv[i + 1]?.toLowerCase() : null;
})();

const PROBE_QUERY = process.env.HEALTH_CHECK_QUERY || 'bimetallic thermometer calibration';
// 同一台引擎连测两次：单次失败可能只是限流抖动，两次都解析不出才判定失效。
const PROBES = 2;

const ENGINES = [
  { key: 'google', name: 'Browser Google', method: 'tryBrowserGoogleSearch' },
  { key: 'ddg', name: 'Axios DuckDuckGo', method: 'tryDuckDuckGoSearch' },
  { key: 'bing', name: 'Browser Bing', method: 'tryBrowserBingSearch' },
  { key: 'brave', name: 'Browser Brave', method: 'tryBrowserBraveSearch' },
].filter(e => !ENGINE_FILTER || e.key === ENGINE_FILTER);

const engine = new SearchEngine();
const results = [];

for (const spec of ENGINES) {
  const attempts = [];
  let lastStatus = 'ok';
  let lastDetail = '';

  for (let i = 0; i < PROBES; i++) {
    const startedAt = Date.now();
    let status, detail = '', count = 0;
    engine.lastEngineBlocked = false;
    try {
      const found = await engine[spec.method](PROBE_QUERY, 3, 15000);
      count = found.length;
      if (count > 0) {
        status = 'ok';
        detail = `${count} 条结果`;
      } else if (engine.lastEngineBlocked) {
        status = 'blocked';
        detail = '被限流或反爬拦截，等一段时间会恢复';
      } else {
        status = 'broken';
        detail = '拿到了页面但解析出 0 条结果，解析器很可能已失效';
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      // An external block is not a code fault; never report it as a broken parser.
      status = engine.lastEngineBlocked || /bot-check|captcha|rate limit/i.test(message) ? 'blocked' : 'error';
      detail = message.slice(0, 200);
    }
    attempts.push({ status, detail, count, ms: Date.now() - startedAt });
    lastStatus = status;
    lastDetail = detail;
    // 第一次就成功、或已被拦截，无需再打一次（避免自己把人家打成限流）。
    if (status === 'ok' || status === 'blocked') break;
  }

  // 只有每次都解析不出、且没有一次是被拦截，才认定解析器失效。
  const allBroken = attempts.length > 0 && attempts.every(a => a.status === 'broken' || a.status === 'error');
  const anyBlocked = attempts.some(a => a.status === 'blocked');
  const finalStatus = allBroken ? (anyBlocked ? 'blocked' : 'broken') : lastStatus;

  results.push({
    engine: spec.name,
    status: finalStatus,
    detail: lastDetail,
    attempts: attempts.length,
    ms: attempts.reduce((s, a) => s + a.ms, 0),
  });
}

await engine.closeAll();

const broken = results.filter(r => r.status === 'broken' || r.status === 'error');
const blocked = results.filter(r => r.status === 'blocked');
const healthy = results.filter(r => r.status === 'ok');

if (JSON_OUT) {
  console.log(JSON.stringify({
    query: PROBE_QUERY,
    results,
    summary: { healthy: healthy.length, blocked: blocked.length, broken: broken.length },
  }, null, 2));
} else if (!QUIET || broken.length > 0) {
  console.log(`web-search-mcp 引擎自检  查询="${PROBE_QUERY}"\n`);
  for (const r of results) {
    const mark = { ok: '正常', blocked: '被拦截', broken: '解析失效', error: '报错' }[r.status] || r.status;
    console.log(`  ${r.engine.padEnd(18)} ${mark.padEnd(6)} ${r.detail}  (${r.ms}ms)`);
  }
  console.log('');
  if (broken.length > 0) {
    console.log(`需要处理：${broken.map(r => r.engine).join('、')} 已不可用。`);
    console.log('若判定为「解析失效」，说明对方页面结构变了，需要更新 dist/search-engine.js 里对应的 parse*Results。');
  } else if (blocked.length === results.length) {
    console.log('全部引擎被限流或反爬拦截，检查代理 / 出口 IP，等一段时间再试。');
  } else {
    console.log(`可用引擎：${healthy.map(r => r.engine).join('、') || '无'}`);
    if (blocked.length > 0) console.log(`被拦截（外部原因，非代码问题）：${blocked.map(r => r.engine).join('、')}`);
  }
}

process.exit(broken.length > 0 ? 1 : 0);
