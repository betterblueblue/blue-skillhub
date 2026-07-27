const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const dir = __dirname;
  const outDir = path.join(dir, 'frames-chain');
  fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 900, height: 560 },
    deviceScaleFactor: 2,
  });
  await page.goto('file://' + path.join(dir, 'chain-demo.html').replace(/\\/g, '/'));
  await page.waitForFunction(() => window.FRAMES > 0);

  const total = await page.evaluate(() => window.FRAMES);
  const holds = await page.evaluate(() => window.HOLDS);
  const el = await page.$('#win');

  for (let i = 0; i < total; i++) {
    await page.evaluate((n) => window.setFrame(n), i);
    await el.screenshot({ path: path.join(outDir, String(i).padStart(4, '0') + '.png') });
  }
  await browser.close();

  // ffmpeg concat 清单：每帧带自己的停留时长
  const lines = [];
  holds.forEach((ms, i) => {
    const f = String(i).padStart(4, '0') + '.png';
    lines.push(`file '${f}'`);
    lines.push(`duration ${(Math.max(ms, 40) / 1000).toFixed(3)}`);
  });
  lines.push(`file '${String(total - 1).padStart(4, '0') + '.png'}'`);
  fs.writeFileSync(path.join(outDir, 'list.txt'), lines.join('\n') + '\n');

  const totalMs = holds.reduce((a, b) => a + Math.max(b, 40), 0);
  console.log(`帧数 ${total}，总时长 ${(totalMs / 1000).toFixed(1)}s`);
})();
