// U0 (ROADMAP 4-3): the same screens at the three sizes students use, plus the numbers the screen redesign is judged by.
//   pnpm qa:screens                      starts its own dev server, writes PNGs and screens.json to .qa-screens/<date>/
//   pnpm qa:screens --out .qa-screens/after --url http://127.0.0.1:5173
// Numbers: how much of the model is visible, what a muscle card shows without scrolling, notices, buttons.
import { chromium } from 'playwright-core';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

const args = process.argv.slice(2);
const option = name => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const root = fileURLToPath(new URL('..', import.meta.url));
const out = join(root, option('--out') ?? `.qa-screens/${new Date().toISOString().slice(0, 10)}`);
mkdirSync(out, { recursive: true });

let server, base = option('--url');
if (!base) {
  const { createServer } = await import('vite');
  server = await createServer({ root, logLevel: 'error', server: { host: '127.0.0.1', port: 5198, strictPort: false } });
  await server.listen();
  base = server.resolvedUrls.local[0].replace(/\/$/, '');
}

const SIZES = [
  { id: 'tablet-landscape', label: '태블릿 가로', width: 1180, height: 820, touch: true },
  { id: 'tablet-portrait', label: '태블릿 세로', width: 820, height: 1180, touch: true },
  { id: 'laptop', label: '노트북', width: 1440, height: 900, touch: false },
];
const MUSCLES = [{ query: '어깨밑근', label: '견갑하근' }, { query: '넙다리곧은근', label: '대퇴직근' }];

async function settle(page) {
  for (let quiet = 0; quiet < 2;) {
    await page.evaluate(() => new Promise(r => setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(r)), 150)));
    const loading = await page.evaluate(() => /불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''));
    if (loading) { quiet = 0; await page.waitForFunction(() => !/불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''), null, { timeout: 60000 }); }
    else quiet++;
  }
}
async function open(page) {
  await page.goto(base + '/');
  await page.waitForFunction(() => document.querySelector('.body-tools') && !document.querySelector('.body-tools').inert, null, { timeout: 60000 });
  await settle(page);
}
async function pick(page, query, label) {
  await page.getByRole('searchbox', { name: '구조 검색' }).fill(query);
  const result = page.locator('nav.region-structure-list button').filter({ hasText: label }).first();
  await result.waitFor({ timeout: 10000 });
  await result.click();
  await settle(page);
  await page.keyboard.press('Escape').catch(() => {});
}

/** Share of the 3D canvas not covered by panels (sampled on a grid with elementFromPoint). */
const modelVisible = page => page.evaluate(() => {
  const canvas = document.querySelector('canvas'); if (!canvas) return 0;
  const r = canvas.getBoundingClientRect(), vw = innerWidth, vh = innerHeight;
  let seen = 0, total = 0;
  for (let y = 0; y < 30; y++) for (let x = 0; x < 30; x++) {
    const px = (x + .5) / 30 * vw, py = (y + .5) / 30 * vh;
    if (px < r.left || px > r.right || py < r.top || py > r.bottom) { total++; continue; }
    total++; if (document.elementFromPoint(px, py) === canvas) seen++;
  }
  return Math.round(seen / total * 100);
});

/** What the muscle card shows as opened: the four facts, where content starts, notices, tab switches. */
const cardFacts = page => page.evaluate(() => {
  const card = document.querySelector('#study-details'); if (!card) return null;
  for (const el of card.querySelectorAll('*')) if (el.scrollTop) el.scrollTop = 0;
  const box = card.getBoundingClientRect(), bottom = Math.min(box.bottom, innerHeight);
  const FACTS = { 기시: /^기시/, 정지: /^정지/, 신경: /^운동신경/, 작용: /^작용 요약/ };
  const heads = [...card.querySelectorAll('h3, h4')];
  const facts = {};
  for (const [name, re] of Object.entries(FACTS)) {
    const h = heads.find(el => re.test(el.textContent.trim()));
    const panel = h?.closest('.study-tab-panel');
    const shown = Boolean(h) && !(panel?.hidden);
    const top = h ? h.getBoundingClientRect().top : Infinity;
    facts[name] = { panel: panel?.id ?? 'card', visibleWithoutScroll: shown && top < bottom && top >= box.top };
  }
  // U2: the key lines under the title carry the four facts (붙는 곳 = 기시 + 정지) without a tab.
  for (const row of card.querySelectorAll('.key-facts [data-fact]')) {
    const top = row.getBoundingClientRect().top, seen = top < bottom && top >= box.top;
    const names = { attach: ['기시', '정지'], nerve: ['신경'], action: ['작용'] }[row.dataset.fact] ?? [];
    for (const name of names) if (seen) facts[name] = { panel: 'card', visibleWithoutScroll: true };
  }
  const openPanel = [...card.querySelectorAll('.study-tab-panel')].find(p => !p.hidden)?.id ?? 'card';
  const panels = new Set(Object.values(facts).map(f => f.panel));
  panels.delete(openPanel); panels.delete('card'); // facts on the card itself need no tab
  const firstSection = card.querySelector('.study-section, .study-tab-panel:not([hidden]) section, .study-tab-panel:not([hidden]) h3');
  // U3: section bars visible without scrolling (title + summary readable at a glance).
  const bars = [...card.querySelectorAll('.study-section-head button')].filter(b => { const t = b.getBoundingClientRect().top; return t >= box.top && t < bottom - 20; }).length;
  return {
    cardWidth: Math.round(box.width),
    factsWithoutScroll: Object.values(facts).filter(f => f.visibleWithoutScroll).length,
    tabSwitchesForFacts: panels.size,
    contentStartsAt: firstSection ? Math.round(firstSection.getBoundingClientRect().top - box.top) : null,
    notices: card.querySelectorAll('.quiet-note').length,
    buttons: card.querySelectorAll('button').length,
    sectionBarsWithoutScroll: bars, sections: card.querySelectorAll('.study-section').length,
  };
});
/** Notices across every tab of the card (each tab's panel renders when opened), then back to the first tab. */
async function noticesAllTabs(page) {
  const tabs = page.locator('#study-details .study-section-head button'), n = await tabs.count(); // U3: sections replace tabs
  if (!n) return page.evaluate(() => document.querySelectorAll('#study-details .quiet-note').length);
  const seen = new Set();
  for (let i = 0; i < n; i++) {
    if (await tabs.nth(i).getAttribute('aria-expanded') !== 'true') await tabs.nth(i).click(); await page.waitForTimeout(400);
    for (const t of await page.evaluate(() => [...document.querySelectorAll('#study-details .quiet-note')].filter(e => e.offsetParent).map(e => e.textContent.trim()))) seen.add(t);
  }
  const opened = page.locator('#study-details .study-section-head button[aria-expanded=true]'); if (await opened.count()) { await opened.first().click(); await page.waitForTimeout(200); }
  return seen.size;
}
const toolbarButtons = page => page.evaluate(() => [...document.querySelectorAll('.body-tools button')].filter(b => b.offsetParent).length);

const browser = await chromium.launch({ channel: 'chrome', headless: true });
const report = { takenAt: new Date().toISOString(), sizes: {} };
for (const size of SIZES) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 2, hasTouch: size.touch, locale: 'ko-KR' });
  const page = await context.newPage();
  const shot = name => page.screenshot({ path: join(out, `${size.id}-${name}.png`) });
  await open(page);
  const r = { label: size.label, home: { modelVisiblePct: await modelVisible(page), toolbarButtons: await toolbarButtons(page) }, muscles: {} };
  await shot('home');
  // U9: a close view of the thighs for material and light (same camera every run).
  await page.evaluate(() => { const sc = window.__atlasScene; sc.stopEntrance(); sc.moveCamera({ target: [0.1, 0.62, 0.05], position: [0.22, 0.74, 0.72], zoom: 1 }, false); sc.requestRender(); });
  await page.waitForTimeout(2200);
  await shot('closeup-thigh');
  await page.evaluate(() => { const sc = window.__atlasScene; sc.moveCamera({ target: [0, 0.86, 0], position: [0, 0.86, 3.5], zoom: 1 }, false); });
  await settle(page);
  for (const m of MUSCLES) {
    await pick(page, m.query, m.label);
    r.muscles[m.label] = { modelVisiblePct: await modelVisible(page), ...await cardFacts(page), toolbarButtons: await toolbarButtons(page) };
    r.muscles[m.label].notices = await noticesAllTabs(page);
    await shot(`card-${m.label}`);
  }
  // Acupoint panel on lung channel, with the subscapularis card still selected.
  await pick(page, MUSCLES[0].query, MUSCLES[0].label);
  await page.getByRole('button', { name: '경혈·경근' }).click();
  await page.locator('.acupoint-panel').waitFor({ timeout: 10000 });
  await settle(page);
  r.acupoint = {
    modelVisiblePct: await modelVisible(page),
    panelButtons: await page.evaluate(() => document.querySelectorAll('.acupoint-panel button').length),
    openPanels: await page.evaluate(() => ['#study-details', '.acupoint-panel'].filter(s => { const el = document.querySelector(s); return el && el.getBoundingClientRect().height > 80; }).length),
  };
  await shot('acupoint-LU');
  report.sizes[size.id] = r;
  await context.close();
}
await browser.close();
await server?.close();
writeFileSync(join(out, 'screens.json'), JSON.stringify(report, null, 1) + '\n');
for (const [id, r] of Object.entries(report.sizes)) {
  console.log(`${r.label} (${id}): 첫 화면 모형 ${r.home.modelVisiblePct}% · 도구 버튼 ${r.home.toolbarButtons}개`);
  for (const [name, m] of Object.entries(r.muscles)) console.log(`  ${name} 카드: 모형 ${m.modelVisiblePct}% · 폭 ${m.cardWidth}px · 핵심 4개 중 스크롤 없이 ${m.factsWithoutScroll}개 · 탭 전환 ${m.tabSwitchesForFacts}번 · 본문 시작 ${m.contentStartsAt}px · 칸 ${m.sections}개 중 스크롤 없이 ${m.sectionBarsWithoutScroll}개 · 안내문(탭 전부) ${m.notices}개 · 카드 버튼 ${m.buttons}개 · 도구 버튼 ${m.toolbarButtons}개`);
  console.log(`  경혈 창(폐경): 모형 ${r.acupoint.modelVisiblePct}% · 창 버튼 ${r.acupoint.panelButtons}개 · 동시에 열린 창 ${r.acupoint.openPanels}개`);
}
console.log(`\n캡처: ${out}`);
