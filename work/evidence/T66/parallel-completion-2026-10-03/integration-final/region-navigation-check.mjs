import { chromium } from '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'work/evidence/T66/parallel-completion-2026-10-03/integration-final');
const categories = ['머리', '목', '등', '어깨·어깨뼈', '가슴우리', '배·허리', '골반·샅', '볼기·깊은엉덩이', '넙다리', '종아리', '발', '팔·손'];
const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const consoleErrors = [];
const pageErrors = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => pageErrors.push(String(e)));
const rows = [];
let failure = null;
try {
  const baseUrl = process.env.HA_BASE_URL || 'http://127.0.0.1:5175/';
  const startUrl = `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}source=ZA-c7010a9-0f56fb6c5633c34da16a6eda`;
  await page.goto(startUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.getByRole('button', { name: 'Human Atlas 전신 홈', exact: true }).waitFor({ timeout: 90000 });
  await page.locator('canvas').first().waitFor({ state: 'visible', timeout: 90000 });
  await page.locator('.study-details h2').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(1500);
  const regionNav = page.getByRole('navigation', { name: '12개 해부학 부위' });
  await regionNav.waitFor({ state: 'visible' });
  for (const label of categories) {
    await page.getByRole('button', { name: '전신', exact: true }).click();
    const control = regionNav.getByRole('button', { name: label, exact: true });
    await control.click();
    await page.waitForFunction(name => [...document.querySelectorAll('nav[aria-label="12개 해부학 부위"] button')]
      .some(button => button.textContent?.trim() === name && button.getAttribute('aria-pressed') === 'true'), label);
    const snapshot = await page.evaluate(() => ({
      selectedRegionLabels: [...document.querySelectorAll('nav[aria-label="12개 해부학 부위"] button[aria-pressed="true"]')].map(x => x.textContent?.trim()),
      structureRowCount: document.querySelectorAll('nav[aria-label="구조 목록"] button').length,
      route: location.search,
      canvasCount: document.querySelectorAll('canvas').length,
      playerCount: document.querySelectorAll('[data-testid="motion-player"]').length,
    }));
    rows.push({ label, selected: snapshot.selectedRegionLabels.includes(label), exactlyOneRegion: snapshot.selectedRegionLabels.length === 1,
      hasStructureRows: snapshot.structureRowCount > 0, ...snapshot });
  }
  await page.getByRole('button', { name: '전신', exact: true }).click();
  const homeRegionReset = await page.getByRole('button', { name: '전신', exact: true }).getAttribute('aria-pressed') === 'true'
    && await regionNav.locator('button[aria-pressed="true"]').count() === 0;
  await regionNav.getByRole('button', { name: '발', exact: true }).focus();
  await page.keyboard.press('Enter');
  const keyboardRegionSelection = await regionNav.getByRole('button', { name: '발', exact: true }).getAttribute('aria-pressed') === 'true';
  const result = {
    schemaVersion: 't66-final-region-navigation-check-v1',
    testedAt: new Date().toISOString(),
    baseUrl: startUrl,
    categoriesExpected: categories,
    expectedCount: 12,
    observedCount: rows.length,
    rows,
    homeRegionReset,
    keyboardRegionSelection,
    consoleErrors,
    pageErrors,
    pass: rows.length === 12 && rows.every(x => x.selected && x.exactlyOneRegion && x.hasStructureRows && x.canvasCount === 1)
      && homeRegionReset && keyboardRegionSelection && consoleErrors.length === 0 && pageErrors.length === 0,
  };
  await mkdir(out, { recursive: true });
  await writeFile(path.join(out, 'region-navigation-validation.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({ pass: result.pass, observedCount: rows.length, homeRegionReset, keyboardRegionSelection,
    rows: rows.map(x => ({ label: x.label, selected: x.selected, exactlyOneRegion: x.exactlyOneRegion, structureRows: x.structureRowCount, canvasCount: x.canvasCount })), consoleErrors, pageErrors }, null, 2));
} catch (error) {
  failure = { name: error.name, message: error.message };
  console.error(JSON.stringify({ failure, rows, consoleErrors, pageErrors }, null, 2));
  process.exitCode = 1;
} finally {
  await browser.close();
}
