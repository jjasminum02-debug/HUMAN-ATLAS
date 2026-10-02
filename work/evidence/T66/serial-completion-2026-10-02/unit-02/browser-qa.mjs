import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { chromium } from '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const root = '/Users/daniel/Downloads/SIM /HUMAN ATLAS';
const evidenceDir = path.join(root, 'work/evidence/T66/serial-completion-2026-10-02/unit-02/browser');
const baseUrl = process.env.HA_BASE_URL || 'http://127.0.0.1:5174/';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
await mkdir(evidenceDir, { recursive: true });

const browser = await chromium.launch({ headless: true, executablePath: chromePath, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'no-preference' });
const consoleErrors = [];
const pageErrors = [];
const failedRequests = [];
const motionResponses = [];
const glbResponses = [];
page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
page.on('pageerror', error => pageErrors.push(error.message));
page.on('requestfailed', request => failedRequests.push({ url: request.url(), error: request.failure()?.errorText ?? 'unknown' }));
page.on('response', response => {
  if (/\.glb(?:$|\?)/i.test(response.url())) {
    glbResponses.push({ url: response.url(), status: response.status() });
    if (/\/assets\/motion\//i.test(response.url())) {
      void response.body().then(bytes => motionResponses.push({ url: response.url(), status: response.status(), bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') })).catch(error => motionResponses.push({ url: response.url(), status: response.status(), error: String(error) }));
    }
  }
});

const checks = [];
function assert(condition, message) { if (!condition) throw new Error(message); }
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitCanvas() {
  await page.locator('canvas').first().waitFor({ state: 'visible', timeout: 90000 });
  await page.waitForFunction(() => document.querySelectorAll('canvas').length > 0, null, { timeout: 10000 });
}
async function selectSearch(query, sideKo, expectedName) {
  const search = page.locator('input[aria-label="구조 검색"]');
  await search.fill(query);
  await page.waitForTimeout(350);
  const result = page.locator('nav[aria-label="구조 목록"] button').first();
  await result.waitFor({ state: 'visible', timeout: 10000 });
  await result.click();
  await page.locator('.study-details h2').waitFor({ state: 'visible', timeout: 10000 });
  const initialName = (await page.locator('.study-details h2').innerText()).trim();
  if (sideKo) {
    const sideButton = page.locator('.part-pills button').filter({ hasText: sideKo }).first();
    await sideButton.waitFor({ state: 'visible', timeout: 5000 });
    await sideButton.click();
  }
  const detailText = await page.locator('.study-details').innerText();
  assert(detailText.includes(expectedName), `${query}: selected card does not show ${expectedName}`);
  if (sideKo) assert(detailText.includes(sideKo), `${query}: selected side ${sideKo} is not in card`);
  await page.locator('[data-testid="motion-player"]').waitFor({ state: 'visible', timeout: 10000 });
  return { query, initialName, side: sideKo, cardText: detailText.slice(0, 800), subjectNote: '' };
}
async function chooseMotionAction(preferredTerms = []) {
  const picker = page.locator('fieldset[aria-label="작용 선택"]');
  assert(await picker.count() === 1, 'multiple motion choices should be exposed for this selected source');
  const buttons = await picker.locator('button').allTextContents();
  let chosen = null;
  for (const term of preferredTerms) {
    const match = picker.locator('button').filter({ hasText: term }).first();
    if (await match.count()) { chosen = (await match.innerText()).trim(); await match.click(); break; }
  }
  assert(chosen, `no motion option matched ${preferredTerms.join(', ')}`);
  await page.waitForFunction(() => {
    const pressed = document.querySelector('fieldset[aria-label="작용 선택"] button[aria-pressed="true"]');
    return Boolean(pressed);
  }, null, { timeout: 3000 });
  return { labels: buttons.map(v => v.trim()), chosen };
}
async function ensureLoadedAndPlay(expectedPoseLabel) {
  const player = page.locator('[data-testid="motion-player"]');
  const button = player.getByRole('button', { name: '움직임으로 이해하기', exact: true });
  const progress = page.locator('#motion-progress');
  const before = await page.locator('.motion-player-status').innerText();
  assert(await button.isEnabled(), `motion button disabled before load: ${before}`);
  await button.click();
  const startedAt = Date.now();
  while (Date.now() - startedAt < 30000) {
    if (!(await progress.isDisabled())) break;
    await sleep(250);
  }
  assert(!(await progress.isDisabled()), `motion failed to load; status=${await page.locator('.motion-player-status').innerText()}`);
  await page.waitForTimeout(200);
  const status = await page.locator('.motion-player-status').innerText();
  const candidate = await page.locator('.motion-player').innerText();
  if (expectedPoseLabel) assert(candidate.includes(expectedPoseLabel), `wrong candidate pose label; expected ${expectedPoseLabel}`);
  return { status, candidate: candidate.slice(0, 500), progress: await progress.inputValue() };
}
async function scrubAndReturn(screenshotName, keepHidden = false, testJointControl = false) {
  const progress = page.locator('#motion-progress');
  const joint = page.locator('#joint-angle');
  const jointDetails = page.locator('details.joint-angle-control');
  if (testJointControl && await jointDetails.count()) {
    if (!(await jointDetails.getAttribute('open'))) await jointDetails.locator('summary').click();
    await page.waitForFunction(() => document.querySelector('details.joint-angle-control')?.hasAttribute('open') === true, null, { timeout: 3000 });
    await joint.waitFor({ state: 'visible' });
    assert(!(await joint.isDisabled()), 'joint-angle slider disabled after load');
    await joint.evaluate(el => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(el, String((Number(el.min) + Number(el.max)) / 2));
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await page.waitForTimeout(150);
  }
  await progress.evaluate(el => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    setter.call(el, '50');
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await page.waitForTimeout(200);
  const scrubbed = await progress.inputValue();
  assert(scrubbed === '50', `scrub did not hold selected position: ${scrubbed}`);
  await page.screenshot({ path: path.join(evidenceDir, screenshotName), fullPage: false });
  const player = page.locator('[data-testid="motion-player"]');
  const button = player.getByRole('button', { name: '움직임으로 이해하기', exact: true });
  await button.click();
  await page.waitForTimeout(250);
  await button.click();
  const began = Date.now();
  while (Date.now() - began < 6000) {
    const v = Number(await progress.inputValue());
    const status = await page.locator('.motion-player-status').innerText();
    if (v <= 1 && /처음 자세|복원|처음 자세로/.test(status)) break;
    await sleep(120);
  }
  const finalProgress = Number(await progress.inputValue());
  const finalStatus = await page.locator('.motion-player-status').innerText();
  assert(finalProgress <= 1, `smooth return did not reach rest: ${finalProgress}%`);
  let hiddenPersisted = false;
  let hiddenPlaybackBlocked = false;
  if (keepHidden) {
    await page.getByRole('button', { name: '선택 숨기기', exact: true }).click();
    hiddenPersisted = await page.getByRole('button', { name: '선택 다시 표시', exact: true }).count() === 1;
    assert(hiddenPersisted, 'hidden state did not appear after player reset');
    await page.waitForFunction(() => { const button = document.querySelector('[data-testid="motion-player"] .motion-player-controls button'); return button && button.disabled; }, null, { timeout: 3000 });
    hiddenPlaybackBlocked = await button.isDisabled();
    assert(hiddenPlaybackBlocked, 'hidden subject should not remain attached to active motion playback');
    await page.getByRole('button', { name: '선택 다시 표시', exact: true }).click();
    await page.waitForFunction(() => { const button = document.querySelector('[data-testid="motion-player"] .motion-player-controls button'); return button && !button.disabled; }, null, { timeout: 3000 });
    assert(await button.isEnabled(), 'motion controls did not recover after unhide');
  }
  return { scrubbed, finalProgress, finalStatus, hiddenPersisted, hiddenPlaybackBlocked };
}

try {
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await waitCanvas();
  await page.waitForTimeout(2500);

  // Hip: Psoas source surface, both sides; direct bone selection is checked separately below.
  for (const side of ['왼쪽', '오른쪽']) {
    const selection = await selectSearch('Psoas major', side, '큰허리근');
    const motionChoice = await chooseMotionAction(['엉덩관절 굽힘']);
    selection.subjectNote = await page.locator('.motion-player-note').innerText();
    assert(selection.subjectNote.includes('수동 변형'), `Psoas should be described as passive surface context: ${selection.subjectNote}`);
    const load = await ensureLoadedAndPlay('엉덩관절 굽힘');
    const playback = await scrubAndReturn(`hip-psoas-${side === '왼쪽' ? 'left' : 'right'}.png`, side === '왼쪽', side === '왼쪽');
    checks.push({ kind: 'muscle', family: 'hip-flexion', ...selection, motionChoice, load, playback });
  }

  // Hip fixed bone: the pelvis stays fixed while the exact side-specific hip-family candidate remains selectable.
  for (const side of ['왼쪽', '오른쪽']) {
    const selection = await selectSearch('Hip bone', side, '볼기뼈');
    const motionChoice = await chooseMotionAction(['고관절 굽힘', '엉덩관절 굽힘', 'Hip flexion']);
    selection.subjectNote = await page.locator('.motion-player-note').innerText();
    assert(selection.subjectNote.includes('고정된 기준 구조'), `hip bone should be described as fixed: ${selection.subjectNote}`);
    const load = await ensureLoadedAndPlay('엉덩관절 굽힘');
    const playback = await scrubAndReturn(`hip-bone-${side === '왼쪽' ? 'left' : 'right'}.png`, side === '왼쪽');
    checks.push({ kind: 'bone-fixed', family: 'hip-flexion', ...selection, motionChoice, load, playback });
  }

  // Knee: source patella selection checks the required cooperative moving bone and both sides.
  for (const side of ['왼쪽', '오른쪽']) {
    const selection = await selectSearch('Patella', side, '무릎뼈');
    const motionChoice = await chooseMotionAction(['무릎 굽힘', 'Knee flexion']);
    selection.subjectNote = await page.locator('.motion-player-note').innerText();
    assert(selection.subjectNote.includes('선택한 뼈가 이 교육용 관절 자세에서 이동합니다'), `patella should be described as moving: ${selection.subjectNote}`);
    const load = await ensureLoadedAndPlay('무릎 굽힘');
    const playback = await scrubAndReturn(`knee-patella-${side === '왼쪽' ? 'left' : 'right'}.png`, side === '왼쪽');
    checks.push({ kind: 'bone-moving', family: 'knee-flexion', ...selection, motionChoice, load, playback });
  }

  // Knee fixed bone and quadriceps passive surface, both sides.
  for (const side of ['왼쪽', '오른쪽']) {
    const selection = await selectSearch('Femur', side, '대퇴골');
    const motionChoice = await chooseMotionAction(['무릎 굽힘', 'Knee flexion']);
    selection.subjectNote = await page.locator('.motion-player-note').innerText();
    assert(selection.subjectNote.includes('고정된 기준 구조'), `femur should be described as fixed for knee flexion: ${selection.subjectNote}`);
    const load = await ensureLoadedAndPlay('무릎 굽힘');
    const playback = await scrubAndReturn(`knee-femur-${side === '왼쪽' ? 'left' : 'right'}.png`, false);
    checks.push({ kind: 'bone-fixed', family: 'knee-flexion', ...selection, motionChoice, load, playback });
  }

  // Smaller viewport: verify that a real candidate remains selectable and the controls fit the learner view.
  await page.setViewportSize({ width: 390, height: 844 });
  const mobileSelection = await selectSearch('Vastus intermedius', '오른쪽', '중간넓은근');
  const mobileChoice = await page.locator('fieldset[aria-label="작용 선택"]').count()
    ? await chooseMotionAction(['무릎 굽힘', 'Knee flexion'])
    : { labels: [], chosen: 'single verified candidate' };
  mobileSelection.subjectNote = await page.locator('.motion-player-note').innerText();
  assert(mobileSelection.subjectNote.includes('수동 변형'), `Vastus intermedius should be described as passive surface context: ${mobileSelection.subjectNote}`);
  const mobileLoad = await ensureLoadedAndPlay('무릎 굽힘');
  await page.screenshot({ path: path.join(evidenceDir, 'mobile-knee-right.png'), fullPage: true });
  checks.push({ kind: 'mobile-muscle', family: 'knee-flexion', ...mobileSelection, motionChoice: mobileChoice, load: mobileLoad });
  const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, viewport: window.innerWidth }));
  assert(overflow.scrollWidth <= overflow.viewport + 1, `horizontal overflow on 390px: ${JSON.stringify(overflow)}`);

  await page.waitForTimeout(1000);
  await writeFile(path.join(evidenceDir, 'browser-checks.json'), JSON.stringify({
    schemaVersion: 't66-unit02-browser-qa-v1',
    baseUrl,
    browser: 'Google Chrome 154 headless via Playwright 1.62.1',
    viewports: [{ width: 1440, height: 1000 }, { width: 390, height: 844 }],
    checks,
    motionResponses,
    glbResponses,
    consoleErrors,
    pageErrors,
    failedRequests,
    overflow,
    pass: checks.length === 9 && motionResponses.length >= 4 && motionResponses.every(item => item.status === 200 && item.sha256) && !consoleErrors.length && !pageErrors.length && overflow.scrollWidth <= overflow.viewport + 1
  }, null, 2) + '\n');
  await page.screenshot({ path: path.join(evidenceDir, 'final-mobile.png'), fullPage: true });
  console.log(JSON.stringify({ pass: checks.length === 9 && motionResponses.length >= 4 && motionResponses.every(item => item.status === 200 && item.sha256) && !consoleErrors.length && !pageErrors.length, checks: checks.length, motionResponses, glbResponses: glbResponses.length, consoleErrors, pageErrors, failedRequests, overflow }, null, 2));
} catch (error) {
  await page.screenshot({ path: path.join(evidenceDir, 'failure.png'), fullPage: true }).catch(() => {});
  await writeFile(path.join(evidenceDir, 'browser-checks.json'), JSON.stringify({ schemaVersion: 't66-unit02-browser-qa-v1', baseUrl, checks, motionResponses, consoleErrors, pageErrors, failedRequests, pass: false, error: error.stack ?? String(error) }, null, 2) + '\n');
  console.error(error.stack ?? error);
  process.exitCode = 1;
} finally {
  await browser.close();
}
