import { chromium } from '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const out = 'work/evidence/T66/serial-completion-2026-10-02/unit-03/continuation-2026-10-03/browser-u01';
await mkdir(`${out}/screenshots`, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
const consoleErrors = [];
const pageErrors = [];
page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
page.on('pageerror', error => pageErrors.push(String(error)));

const checks = [];
const button = name => page.getByRole('button', { name, exact: true });
const range = page.locator('input[type="range"][aria-label="시범 진행 위치"]');
async function waitProgress(predicate, timeoutMs = 5000) {
  const start = Date.now();
  let value = null;
  while (Date.now() - start < timeoutMs) {
    value = Number(await range.inputValue());
    if (predicate(value)) return value;
    await page.waitForTimeout(80);
  }
  return value;
}
async function state() {
  return await page.evaluate(() => ({
    url: location.href,
    viewport: { width: innerWidth, height: innerHeight },
    pageWidth: document.documentElement.scrollWidth,
    card: document.querySelector('#study-details')?.innerText || '',
    sourceButtons: [...document.querySelectorAll('button')].map(node => node.innerText.replace(/\s+/g, ' ').trim()).filter(text => /Short head of biceps brachii|움직임으로 이해하기|어깨 앞쪽 굽힘|팔꿈치 굽힘/.test(text)),
    sideControls: [...document.querySelectorAll('button')].map(node => ({ text: node.innerText.replace(/\s+/g, ' ').trim(), pressed: node.getAttribute('aria-pressed') })).filter(item => /^(왼쪽|오른쪽)$/.test(item.text)),
    progress: document.querySelector('input[aria-label="시범 진행 위치"]')?.value ?? null,
    canvas: [...document.querySelectorAll('canvas')].map(node => ({ width: node.width, height: node.height, rect: node.getBoundingClientRect().toJSON() })),
    internalMetadataVisible: /(ZA-|T66-|sourceKey|evidence|authoring)/i.test(document.querySelector('#study-details')?.innerText || ''),
  }));
}
async function selectSource() {
  const search = page.getByRole('searchbox', { name: '구조 검색' });
  await search.fill('Short head of biceps brachii');
  await page.waitForTimeout(450);
  await page.getByRole('button', { name: /상완이두근 단두.*Short head of biceps brachii/ }).last().click();
  await page.waitForTimeout(700);
}

let failure = null;
try {
  await page.goto('http://127.0.0.1:5175/?source=ZA-c7010a9-2d15cee81610b0809f565954', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await button('Human Atlas 전신 홈').waitFor({ timeout: 60000 });
  await page.waitForTimeout(9000);

  for (const side of ['left', 'right']) {
    await selectSource();
    await button(side === 'left' ? '왼쪽' : '오른쪽').click();
    await page.waitForTimeout(500);
    for (const action of [
      { id: 'shoulder-flexion', label: '어깨 앞쪽 굽힘 자세에서 관찰' },
      { id: 'elbow-flexion', label: '팔꿈치 굽힘 자세에서 관찰' },
    ]) {
      const actionButton = page.getByRole('button', { name: new RegExp(action.label) });
      await actionButton.click();
      await page.waitForTimeout(350);
      const before = await state();
      const cardMatches = before.card.includes('Short head of biceps brachii')
        && before.card.includes(side === 'left' ? '왼쪽' : '오른쪽')
        && before.sideControls.some(item => item.text === (side === 'left' ? '왼쪽' : '오른쪽') && item.pressed === 'true');
      const actionMatches = before.card.includes(action.label);
      const prefix = `u01-${action.id}-${side}`;
      await page.locator('canvas').first().screenshot({ path: `${out}/screenshots/${prefix}-rest.png` });
      await button('움직임으로 이해하기').click();
      const midProgress = await waitProgress(value => value >= 30 && value <= 70, 10000);
      const playingState = await state();
      await page.screenshot({ path: `${out}/screenshots/${prefix}-mid-page.png`, fullPage: true });
      const midCanvas = await page.locator('canvas').first().screenshot({ path: `${out}/screenshots/${prefix}-mid-canvas.png` });
      const restCanvas = await import('node:fs/promises').then(({ readFile }) => readFile(`${out}/screenshots/${prefix}-rest.png`));
      const restHash = createHash('sha256').update(restCanvas).digest('hex');
      const midHash = createHash('sha256').update(midCanvas).digest('hex');
      const playbackStarted = midProgress >= 30 && Number(playingState.progress) > 0;
      await button('움직임으로 이해하기').click();
      const restoredProgress = await waitProgress(value => value === 0, 5000);
      await page.waitForTimeout(250);
      const after = await state();
      await page.locator('canvas').first().screenshot({ path: `${out}/screenshots/${prefix}-returned.png` });
      checks.push({
        candidate: `${action.id}-${side}`,
        sourceKey: side === 'left' ? 'ZA-c7010a9-b20b574e456449c5d571c7a1' : 'ZA-c7010a9-a0c2ea00609e874a7faa926d',
        sourceName: 'Short head of biceps brachii',
        side,
        action: action.label,
        cardMatchesSourceAndSide: cardMatches,
        actionMatchesSelection: actionMatches,
        playbackStarted,
        midProgress,
        canvasRestSha256: restHash,
        canvasMidSha256: midHash,
        canvasChangedAtMidpoint: restHash !== midHash,
        reClickReturnedProgressToZero: restoredProgress === 0,
        returnedCardStillMatches: after.card.includes('Short head of biceps brachii') && after.card.includes(side === 'left' ? '왼쪽' : '오른쪽'),
        internalMetadataVisible: before.internalMetadataVisible || playingState.internalMetadataVisible || after.internalMetadataVisible,
        viewport: before.viewport,
        pageWidth: before.pageWidth,
        canvas: before.canvas,
        screenshots: [`${prefix}-rest.png`, `${prefix}-mid-page.png`, `${prefix}-mid-canvas.png`, `${prefix}-returned.png`],
      });
    }
  }
} catch (error) {
  failure = { name: error.name, message: error.message, stack: error.stack };
}

const result = {
  schemaVersion: 't66-u03-u01-browser-supplement-v1',
  baseUrl: page.url(),
  browser: 'Google Chrome headless through bundled Playwright',
  viewport: { width: 1440, height: 960 },
  checks,
  consoleErrors,
  pageErrors,
  failure,
  allFourCandidatesPassed: checks.length === 4 && checks.every(check => check.cardMatchesSourceAndSide && check.actionMatchesSelection && check.playbackStarted && check.canvasChangedAtMidpoint && check.reClickReturnedProgressToZero && check.returnedCardStillMatches && !check.internalMetadataVisible),
  limitations: ['This verifies the exact source surface, selected side, action card and same-scene rendered playback for these four U01 source/action/side candidates only; it is not an anatomical review or a full-family extent approval.'],
};
await writeFile(`${out}/browser-validation.json`, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
await browser.close();
