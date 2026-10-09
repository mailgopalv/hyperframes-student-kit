const { chromium } = require('playwright');
const path = require('path'), url = require('url');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto(url.pathToFileURL(path.resolve('video-projects/ai-mcp-short1/index.html')).href, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1000);
  const T = process.argv.slice(2).map(Number);
  for (const t of T) {
    await p.evaluate(async (t) => {
      window.__timelines['short1'].seek(t, false);
      const v = document.getElementById('panel-video');
      await new Promise(r => { v.addEventListener('seeked', r, { once: true }); v.currentTime = t; setTimeout(r, 1500); });
    }, t);
    await p.waitForTimeout(150);
    await p.screenshot({ path: `video-projects/ai-mcp-short1/work/ss_${t}.png` });
  }
  await b.close();
})();
