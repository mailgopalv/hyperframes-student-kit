const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2560, height: 1440 } });
  const url = require('url').pathToFileURL(require('path').resolve('video-projects/ai-mcp-handson/index.html')).href;
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  for (const [t, k] of [[0.35,0],[1.2,0],[2.4,0],[6.6,1],[10.8,2],[12.2,2]]) {
    await p.evaluate(([t,k]) => {
      document.querySelectorAll('.card').forEach((c,i)=>c.style.display = i===k?'':'none');
      document.querySelectorAll('.ref').forEach((c,i)=>c.style.display = i===k?'':'none');
      window.__timelines['chapter-cards'].seek(t, false);
    }, [t,k]);
    await p.screenshot({ path: `video-projects/ai-mcp-handson/work/pw_${t}.png`, clip: { x: 0, y: 560, width: 1100, height: 880 } });
  }
  await b.close();
})();
