import { chromium } from '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'work/evidence/T66/parallel-completion-2026-10-03/integration-final');
const shots = path.join(out, 'screenshots');
const baseUrl = process.env.HA_BASE_URL || 'http://127.0.0.1:5175/';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
await mkdir(shots, { recursive: true });
const registration = JSON.parse(await readFile(path.join(root, 'atlas-data/motion/t66-wave1-registration.json'), 'utf8'));
const packageById = new Map(registration.packages.map(row => [row.id, row]));
const target = registration.selectors.find(row => row.subjectKind === 'muscle'
  && row.sourceSubjectKey === 'ZA-c7010a9-0f56fb6c5633c34da16a6eda' && row.side === 'right');
if (!target) throw new Error('Pinned W1 right abductor pollicis brevis selector was not found');
const targetPackage = packageById.get(target.packageId);
if (!targetPackage) throw new Error('Pinned W1 package missing');

const browser = await chromium.launch({ headless: true, executablePath: chromePath, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'no-preference' });
const consoleErrors = [];
const pageErrors = [];
const failedRequests = [];
const motionResponses = [];
const motionResponsePromises = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => pageErrors.push(String(e)));
page.on('requestfailed', r => failedRequests.push({ url: r.url(), error: r.failure()?.errorText ?? 'unknown' }));
page.on('response', response => {
  if (/\/assets\/motion\/t66-wave1\//.test(response.url())) {
    const capture = response.body().then(bytes => motionResponses.push({ url: response.url(), status: response.status(), bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') }))
      .catch(e => motionResponses.push({ url: response.url(), error: String(e) }));
    motionResponsePromises.push(capture);
  }
});

const button = name => page.getByRole('button', { name, exact: true });
const waitCanvas = async () => page.locator('canvas').first().waitFor({ state: 'visible', timeout: 90000 });
const waitStudy = async () => page.locator('.study-details h2').waitFor({ state: 'visible', timeout: 15000 });
const results = {};
const steps = [];
let failure = null;
try {
  await page.goto(`${baseUrl}?source=${encodeURIComponent(target.sourceSubjectKey)}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await button('Human Atlas 전신 홈').waitFor({ timeout: 90000 });
  await waitCanvas();
  await waitStudy();
  await page.waitForTimeout(2500);

  const search = page.getByRole('searchbox', { name: '구조 검색' });
  await search.fill('Abductor pollicis brevis');
  await page.waitForTimeout(350);
  const resultButtons = page.locator('nav[aria-label="구조 목록"] button');
  const resultNames = await resultButtons.allTextContents();
  const card = page.locator('.study-details');
  const cardText = await card.innerText();
  results.searchResults = resultNames.map(x => x.trim());
  results.exactSourceRoute = new URL(page.url()).searchParams.get('source') === target.sourceSubjectKey;
  results.threeNameCard = cardText.includes('짧은엄지벌림근') && cardText.includes('단무지외전근') && cardText.includes('Abductor pollicis brevis');
  results.learnerHasNoInternalMetadata = !/(ZA-|T66-|sourceKey|evidenceHash|\.json)/i.test(await page.locator('body').innerText());

  const sideButtons = page.locator('.part-pills button');
  const right = sideButtons.filter({ hasText: '오른쪽' }).first();
  const left = sideButtons.filter({ hasText: '왼쪽' }).first();
  if (await left.count()) await left.click();
  await right.focus();
  await page.keyboard.press('Enter');
  results.keyboardSideSwitch = await right.getAttribute('aria-pressed') === 'true';
  results.rightSideCard = (await card.innerText()).includes('오른쪽');

  const actionField = page.locator('fieldset[aria-label="작용 선택"]');
  const actionButtons = actionField.locator('button');
  results.w1ActionOptions = (await actionButtons.allTextContents()).map(x => x.trim());
  const motionPlayer = page.locator('[data-testid="motion-player"]');
  await motionPlayer.getByText(target.label, { exact: true }).waitFor({ state: 'visible', timeout: 10000 });
  results.singleActionPresented = (await motionPlayer.innerText()).includes(target.label)
    && ((await actionButtons.count()) === 0 || (await actionButtons.count()) === 1);
  if (!results.singleActionPresented) throw new Error('W1 selected action is not represented by the learner motion card');
  const playerButton = button('움직임으로 이해하기');
  if (await playerButton.count() !== 1 || !(await playerButton.isEnabled())) throw new Error('Expected one enabled motion CTA for the W1 action');
  await playerButton.focus();
  await page.keyboard.press('Enter');
  const progress = page.getByLabel('시범 진행 위치');
  await page.waitForFunction(() => {
    const el = document.querySelector('input[aria-label="시범 진행 위치"]');
    return el && Number(el.value) > 0;
  }, null, { timeout: 15000 });
  results.motionStarted = Number(await progress.inputValue()) > 0;
  results.keyboardMotionStart = results.motionStarted;
  results.ctaCount = await page.getByRole('button', { name: '움직임으로 이해하기', exact: true }).count();
  await page.waitForTimeout(450);
  for (const width of [390, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.waitForTimeout(400);
    const layout = await page.evaluate(() => {
      const canvas = [...document.querySelectorAll('canvas')].map(el => { const r = el.getBoundingClientRect(); return { x: r.x, right: r.right, width: r.width, height: r.height }; });
      const box = (selector) => { const el = document.querySelector(selector); if (!el) return null; const r = el.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, height: r.height, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight, overflowY: getComputedStyle(el).overflowY, scrollTop: el.scrollTop }; };
      return { width: innerWidth, height: innerHeight, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight,
        bodyScrollHeight: document.body.scrollHeight, canvas, details: box('.study-details'), motionPlayer: box('[data-testid="motion-player"]'),
        cta: box('.motion-player-controls button'), playerCount: document.querySelectorAll('[data-testid="motion-player"]').length };
    });
    const screenshot = path.join(shots, `w1-hand-${width}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });
    steps.push({ width, layout, screenshot: path.relative(root, screenshot) });
    results[`responsive${width}`] = layout.scrollWidth <= width + 1 && layout.canvas.length > 0 && layout.canvas.every(x => x.x >= -1 && x.right <= width + 1) && layout.playerCount === 1;
    if (width === 390) {
      const details = page.locator('.study-details');
      await details.evaluate(el => {
        const button = el.querySelector('.motion-player-controls button');
        if (!button) return;
        const cardBounds = el.getBoundingClientRect();
        const ctaBounds = button.getBoundingClientRect();
        el.scrollTop += Math.max(0, ctaBounds.top - cardBounds.top - 70);
      });
      const mobileCta = await page.evaluate(() => {
        const details = document.querySelector('.study-details');
        const button = document.querySelector('.motion-player-controls button');
        if (!details || !button) return null;
        const bounds = button.getBoundingClientRect();
        const container = details.getBoundingClientRect();
        return { ctaTop: bounds.top, ctaBottom: bounds.bottom, containerTop: container.top, containerBottom: container.bottom,
          visibleInsideScrollableCard: bounds.top >= container.top + 46 && bounds.bottom <= container.bottom && bounds.height > 0,
          scrollTop: details.scrollTop, scrollHeight: details.scrollHeight, clientHeight: details.clientHeight };
      });
      results.mobileCtaAccessibleAfterDetailScroll = mobileCta?.visibleInsideScrollableCard === true;
      steps.push({ width, mobileCta, screenshot: path.relative(root, path.join(shots, 'w1-hand-390-cta.png')) });
      await page.screenshot({ path: path.join(shots, 'w1-hand-390-cta.png'), fullPage: true });
      await details.evaluate(el => { el.scrollTop = 0; });
    }
  }

  await playerButton.click();
  await page.waitForFunction(() => document.querySelector('.motion-player-status')?.textContent?.includes('처음 자세로 서서히 돌아갑니다.') === true, null, { timeout: 5000 });
  results.smoothRestReturnStarted = true;
  await page.waitForTimeout(1200);
  results.finalRestProgress = await progress.inputValue();
  results.finalRestStatus = await page.locator('.motion-player-status').innerText();
  results.finalRestCtaDisabled = await playerButton.isDisabled();
  results.smoothRestReturn = Number(results.finalRestProgress) === 0
    && !results.finalRestStatus.includes('처음 자세로 서서히 돌아갑니다.') && !results.finalRestCtaDisabled;
  const restScreenshot = path.join(shots, 'w1-hand-1440-rest.png');
  await page.screenshot({ path: restScreenshot, fullPage: true });
  results.restScreenshot = path.relative(root, restScreenshot);
  await page.waitForTimeout(250);
  await Promise.allSettled(motionResponsePromises);
  results.motionResponses = motionResponses;
  results.expectedW1Glb = motionResponses.some(row => row.status === 200 && row.sha256 === targetPackage.sha256 && row.bytes > 0);
  results.expectedW1GlbHash = targetPackage.sha256;
} catch (e) {
  failure = { name: e.name, message: e.message, stack: e.stack };
} finally {
  results.consoleErrors = consoleErrors;
  results.pageErrors = pageErrors;
  results.failedRequests = failedRequests;
  results.motionResponses = motionResponses;
  results.failure = failure;
  results.pass = !failure && results.exactSourceRoute && results.threeNameCard && results.learnerHasNoInternalMetadata
    && results.keyboardSideSwitch && results.rightSideCard && results.singleActionPresented && results.keyboardMotionStart
    && results.motionStarted && results.ctaCount === 1 && results.smoothRestReturnStarted && results.smoothRestReturn
    && results.responsive390 && results.responsive1024 && results.responsive1440 && results.mobileCtaAccessibleAfterDetailScroll
    && results.expectedW1Glb && consoleErrors.length === 0 && pageErrors.length === 0;
  const output = { schemaVersion: 't66-final-integration-browser-v1', baseUrl, browser: 'Google Chrome headless via Playwright', viewportSequence: [390, 1024, 1440], selectedScope: 'single right abductor pollicis brevis W1 source/action; not full hand extent', results, steps, recordedAt: new Date().toISOString() };
  await writeFile(path.join(out, 'final-browser-validation.json'), JSON.stringify(output, null, 2));
  await browser.close();
  console.log(JSON.stringify({ results, steps, recordedAt: output.recordedAt }, null, 2));
}
