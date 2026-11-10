// Performance of the built app under weaker machines (ROADMAP 4-1, step 2). Run after `pnpm build:qa`.
//   pnpm qa:perf                  every profile
//   pnpm qa:perf --only 2,4       some profiles
// CPU and network are throttled through Chrome. The GPU cannot be throttled, so "GPU 없음" (software rendering) is the
// floor; a real low-end GPU sits between that and the baseline, and real phones and tablets are not measured here.
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const only = args.includes('--only') ? args[args.indexOf('--only') + 1].split(',').map(Number) : null;
const PROFILES = [
  { name: '기준 (1440×900, DPR 2)', viewport: { width: 1440, height: 900 }, dpr: 2, cpu: 1 },
  { name: '저사양 노트북 (1366×768, CPU 1/4, 20Mbps)', viewport: { width: 1366, height: 768 }, dpr: 1, cpu: 4, mbps: 20, latency: 40 },
  { name: '태블릿 (820×1180, DPR 2, 터치, CPU 1/4, 10Mbps)', viewport: { width: 820, height: 1180 }, dpr: 2, cpu: 4, mbps: 10, latency: 60, touch: true },
  { name: 'GPU 없음 (1366×768, 소프트웨어 렌더링)', viewport: { width: 1366, height: 768 }, dpr: 1, cpu: 1, software: true },
];

const server = await preview({ root: fileURLToPath(new URL('..', import.meta.url)), mode: 'qa', logLevel: 'error', preview: { host: '127.0.0.1', port: 5196, strictPort: false } });
const base = server.resolvedUrls.local[0];
const busy = page => page.evaluate(() => /불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''));
async function settle(page) {
  for (let quiet = 0; quiet < 3;) {
    await page.waitForTimeout(250);
    if (await busy(page)) { quiet = 0; await page.waitForFunction(() => !/불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''), null, { timeout: 240000 }); } else quiet++;
  }
}
const orbit = page => page.evaluate(() => new Promise(resolve => {
  const s = window.__atlasScene, target = s.controls.target, offset = s.camera.position.clone().sub(target), times = [];
  let last = performance.now(); const end = last + 4000;
  const step = now => {
    times.push(now - last); last = now;
    offset.applyAxisAngle({ x: 0, y: 1, z: 0, isVector3: true }, .02); s.camera.position.copy(target).add(offset); s.camera.lookAt(target); s.requestRender();
    if (now < end) { requestAnimationFrame(step); return; }
    times.shift(); times.sort((a, b) => a - b);
    const info = s.renderer.info;
    resolve({ ratio: s.renderer.getPixelRatio(), fps: times.length / 4, p50: times[Math.floor(times.length * .5)], p95: times[Math.floor(times.length * .95)], calls: info.render.calls, triangles: info.render.triangles });
  };
  requestAnimationFrame(step);
}));
const transferred = page => page.evaluate(() => {
  const nav = performance.getEntriesByType('navigation')[0];
  return (nav.transferSize + performance.getEntriesByType('resource').reduce((n, e) => n + e.transferSize, 0)) / 1e6;
});
const heap = page => page.evaluate(() => (performance.memory?.usedJSHeapSize ?? 0) / 1e6);
const line = (label, o, extra = '') => `  ${label}: ${o.fps.toFixed(0)}fps · 움직일 때 픽셀 비율 ${o.ratio.toFixed(2)} · 프레임 p50 ${o.p50.toFixed(0)}ms p95 ${o.p95.toFixed(0)}ms · draw ${o.calls} · 삼각형 ${(o.triangles / 1e6).toFixed(2)}M${extra}`;

for (const [index, profile] of PROFILES.entries()) {
  if (only && !only.includes(index + 1)) continue;
  const browser = await chromium.launch({ channel: 'chrome', headless: true, args: profile.software ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] : [] });
  const context = await browser.newContext({ viewport: profile.viewport, deviceScaleFactor: profile.dpr, hasTouch: Boolean(profile.touch), locale: 'ko-KR' });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  if (profile.cpu > 1) await cdp.send('Emulation.setCPUThrottlingRate', { rate: profile.cpu });
  if (profile.mbps) { await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: profile.latency, downloadThroughput: profile.mbps * 125000, uploadThroughput: 625000 }); }
  await page.addInitScript(() => { window.__longest = 0; new PerformanceObserver(list => { for (const e of list.getEntries()) window.__longest = Math.max(window.__longest, e.duration); }).observe({ type: 'longtask', buffered: true }); });
  const started = Date.now();
  await page.goto(base);
  await page.waitForFunction(() => document.querySelector('.body-tools') && !document.querySelector('.body-tools').inert, null, { timeout: 240000 });
  const interactive = Date.now() - started;
  await settle(page);
  const load = await transferred(page), longest = await page.evaluate(() => window.__longest);
  console.log(`\n${profile.name}`);
  console.log(`  첫 화면 ${(interactive / 1000).toFixed(1)}s · 전송 ${load.toFixed(1)}MB · 가장 긴 멈춤 ${longest.toFixed(0)}ms · 픽셀 비율 ${await page.evaluate(() => window.__atlasScene.renderer.getPixelRatio())}`);
  console.log(line('기본 층', await orbit(page), ` · heap ${(await heap(page)).toFixed(0)}MB`));
  const startedLayers = Date.now();
  // Tools may be collapsed on narrow screens, so layers are switched through the same buttons a learner uses, by script.
  await page.evaluate(() => { for (const b of document.querySelectorAll('.layer-row button[aria-pressed="false"]')) b.click(); });
  await page.waitForTimeout(300); await settle(page);
  console.log(`  모든 층 켜기 ${((Date.now() - startedLayers) / 1000).toFixed(1)}s · 누적 전송 ${(await transferred(page)).toFixed(1)}MB`);
  console.log(line('모든 층', await orbit(page), ` · heap ${(await heap(page)).toFixed(0)}MB`));
  await browser.close();
}
await server.close();
process.exit(0);
