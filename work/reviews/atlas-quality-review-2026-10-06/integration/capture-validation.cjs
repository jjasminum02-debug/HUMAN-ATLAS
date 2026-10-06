const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const baseUrl = 'http://127.0.0.1:5183/';
const outputRoot = path.resolve(__dirname);
const screenshotRoot = path.join(outputRoot, 'screenshots');
fs.mkdirSync(screenshotRoot, { recursive: true });

const result = {
  schemaVersion: 'atlas-quality-review-integration-browser-validation-v1',
  date: '2026-10-06',
  url: baseUrl,
  browser: { executable: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true },
  cases: {},
  viewports: [],
  consoleErrors: [],
  pageErrors: [],
  failedRequests: [],
};

const record = async (name, fn) => {
  try {
    result.cases[name] = { status: 'passed', ...(await fn()) };
  } catch (error) {
    result.cases[name] = { status: 'failed', error: String(error?.stack || error) };
  }
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--enable-unsafe-swiftshader'],
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'no-preference' });
  const page = await context.newPage();
  page.on('console', message => { if (message.type() === 'error') result.consoleErrors.push(message.text()); });
  page.on('pageerror', error => result.pageErrors.push(String(error?.stack || error)));
  page.on('requestfailed', request => result.failedRequests.push({ url: request.url(), error: request.failure()?.errorText || 'unknown' }));
  const response = await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
  result.httpStatus = response?.status() ?? null;
  await page.locator('.region-picker-trigger').waitFor({ state: 'visible', timeout: 120000 });
  await page.locator('#atlas-stage canvas, #atlas-stage [role="img"]').first().waitFor({ state: 'visible', timeout: 120000 }).catch(() => {});
  await sleep(2500);

  const viewportRecord = async (expectedWidth, expectedHeight) => {
    const actual = await page.evaluate(() => ({
      innerWidth, innerHeight,
      clientWidth: document.documentElement.clientWidth,
      clientHeight: document.documentElement.clientHeight,
      dpr: devicePixelRatio,
      sidebar: (() => { const r = document.querySelector('#atlas-explorer')?.getBoundingClientRect(); return r ? { x: r.x, y: r.y, width: r.width, height: r.height } : null; })(),
      stage: (() => { const r = document.querySelector('#atlas-stage')?.getBoundingClientRect(); return r ? { x: r.x, y: r.y, width: r.width, height: r.height } : null; })(),
    }));
    result.viewports.push({ expectedWidth, expectedHeight, actual, physicalDevice: false });
    return actual;
  };

  await record('regionPickerHoverSlideAndKeyboard', async () => {
    const trigger = page.locator('.region-picker-trigger');
    assert.equal(await trigger.getAttribute('aria-expanded'), 'false');
    await trigger.hover();
    const menu = page.locator('#atlas-region-menu');
    await menu.waitFor({ state: 'visible', timeout: 5000 });
    assert.equal(await trigger.getAttribute('aria-expanded'), 'true');
    const animation = await menu.evaluate(element => getComputedStyle(element).animationName);
    assert.equal(animation, 'region-picker-reveal');
    const regions = await menu.locator('button').allInnerTexts();
    assert(regions.length >= 13, `expected whole body and 12 regions, found ${regions.length}`);
    await sleep(300);
    await page.screenshot({ path: path.join(screenshotRoot, 'region-picker-hover-1440.png'), fullPage: false });
    await page.mouse.move(900, 500);
    await menu.waitFor({ state: 'hidden', timeout: 5000 });
    await trigger.focus();
    await page.keyboard.press('Space');
    await menu.waitFor({ state: 'visible', timeout: 5000 });
    await page.keyboard.press('Escape');
    await menu.waitFor({ state: 'hidden', timeout: 5000 });
    const focusRestored = await trigger.evaluate(element => document.activeElement === element);
    assert(focusRestored, 'Escape should restore focus to the picker trigger');
    return { hoverOpenedWithoutClick: true, menuRegionButtons: regions.length, animation, pointerLeaveClosed: true, keyboardSpaceEscapeFocusRestore: focusRestored, screenshot: 'screenshots/region-picker-hover-1440.png' };
  });

  await record('nameAliasSearchCardAndBilateralSelection', async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await sleep(250);
    const explore = page.locator('.explore-trigger');
    if (await explore.isVisible()) await explore.click();
    const search = page.getByRole('searchbox', { name: '구조 검색' });
    await search.fill('손 · 단무지신근');
    const rows = page.locator('.region-structure-list button');
    await rows.first().waitFor({ state: 'visible', timeout: 5000 });
    const count = await rows.count();
    const rowNames = await rows.allInnerTexts();
    assert.equal(count, 1, `expected one exact grouped result, found ${count}: ${rowNames.join(' | ')}`);
    await rows.first().click();
    const card = page.locator('.study-detail-content .names-card').first();
    await card.waitFor({ state: 'visible', timeout: 5000 });
    const cardText = await card.innerText();
    assert(cardText.includes('짧은엄지폄근'));
    assert(cardText.includes('단무지신근'));
    assert(cardText.includes('Extensor pollicis brevis'));
    assert.equal(await page.getByRole('tab', { name: '구조' }).getAttribute('aria-selected'), 'true', 'ordinary search selection opens the structure tab');
    const rightButton = page.locator('.part-pills button').filter({ hasText: '오른쪽' }).first();
    await rightButton.click();
    const side = await rightButton.getAttribute('aria-pressed');
    assert.equal(side, 'true');
    await page.screenshot({ path: path.join(screenshotRoot, 'name-alias-card-390.png'), fullPage: false });
    await search.fill('Buccinator muscle');
    await rows.first().waitFor({ state: 'visible', timeout: 5000 });
    const buccinatorCount = await rows.count();
    assert.equal(buccinatorCount, 1);
    await rows.first().click();
    const buccinatorCardText = await page.locator('.study-detail-content .names-card').first().innerText();
    assert(buccinatorCardText.includes('볼근'));
    assert(buccinatorCardText.includes('협근'));
    assert(buccinatorCardText.includes('Bucinator'));
    await page.screenshot({ path: path.join(screenshotRoot, 'buccinator-alias-card-390.png'), fullPage: false });
    await page.locator('.explore-trigger').click();
    const mobilePicker = page.locator('.region-picker-trigger');
    await mobilePicker.click();
    const mobileMenu = page.locator('#atlas-region-menu');
    await mobileMenu.waitFor({ state: 'visible', timeout: 5000 });
    const menuRect = await mobileMenu.evaluate(element => element.getBoundingClientRect().toJSON());
    assert(menuRect.bottom <= 844, `region menu exceeds the CSS viewport: ${JSON.stringify(menuRect)}`);
    assert.equal((await search.inputValue()), 'Buccinator muscle', 'region picker remains available during search');
    await sleep(350);
    await page.screenshot({ path: path.join(screenshotRoot, 'region-picker-390-search.png'), fullPage: false });
    const actual = await viewportRecord(390, 844);
    return { search: '손 · 단무지신근', resultCount: count, cardText, ordinarySearchDefaultsToStructureTab: true, rightSideSelected: side === 'true', secondSearch: 'Buccinator muscle', secondResultCount: buccinatorCount, secondCardText: buccinatorCardText, menuAvailableDuringSearch: true, mobileMenuBounds: menuRect, actualViewport: actual, screenshots: ['screenshots/name-alias-card-390.png', 'screenshots/buccinator-alias-card-390.png', 'screenshots/region-picker-390-search.png'] };
  });

  await record('nerveCourseAndExactMotorRelationToFunction', async () => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.locator('.region-picker-trigger').waitFor({ state: 'visible', timeout: 120000 });
    await sleep(250);
    const search = page.getByRole('searchbox', { name: '구조 검색' });
    await search.fill('깊은종아리신경');
    const nerveSearchResult = page.locator('.nerve-search-result');
    await nerveSearchResult.waitFor({ state: 'visible', timeout: 5000 });
    const found = await nerveSearchResult.locator('strong,small').allInnerTexts();
    assert(found.includes('깊은종아리신경') && found.includes('Deep fibular nerve'), `unexpected nerve result: ${found.join(' | ')}`);
    await nerveSearchResult.getByRole('button', { name: '오른쪽 모형' }).click();
    const nerveCard = page.locator('.nerve-card').first();
    await nerveCard.waitFor({ state: 'visible', timeout: 5000 });
    const branchTitle = await nerveCard.locator('h3').allInnerTexts();
    assert(branchTitle.includes('모형에서 연결된 분지'));
    const routeLinks = nerveCard.getByRole('button', { name: /이 근육의 (작용 설명|움직임) 보기/ });
    const routeLabels = await routeLinks.allInnerTexts();
    assert(routeLabels.includes('이 근육의 작용 설명 보기'));
    assert(routeLabels.includes('이 근육의 움직임 보기'));
    const summary = nerveCard.locator('details.nerve-learning-context > summary');
    if (await summary.count()) await summary.click();
    const nerveText = await nerveCard.innerText();
    assert(nerveText.includes('주행·포착 맥락'));
    await page.screenshot({ path: path.join(screenshotRoot, 'deep-fibular-nerve-card-1024.png'), fullPage: false });
    const exactActionRoute = nerveCard.getByRole('button', { name: '이 근육의 움직임 보기' }).first();
    await exactActionRoute.waitFor({ state: 'visible', timeout: 10000 });
    await exactActionRoute.click();
    await page.getByRole('tab', { name: '구조' }).waitFor({ state: 'visible' });
    const functionTab = page.getByRole('tab', { name: '기능' });
    assert.equal(await functionTab.getAttribute('aria-selected'), 'true', 'explicit nerve action route should open the function tab');
    const player = page.locator('[data-testid="motion-player"]');
    await player.waitFor({ state: 'visible', timeout: 10000 });
    const initialText = await player.innerText();
    assert(initialText.includes('움직임으로 이해하기'));
    const cta = player.getByRole('button', { name: '움직임으로 이해하기' });
    assert.equal(await cta.isEnabled(), true);
    assert.equal(await page.locator('button:has-text("멈춤"), button:has-text("처음 자세")').count(), 0);
    await page.screenshot({ path: path.join(screenshotRoot, 'tibialis-action-rest-1024.png'), fullPage: false });
    await cta.click();
    await sleep(600);
    const playingText = await player.innerText();
    const playingPressed = await cta.getAttribute('aria-pressed');
    await page.screenshot({ path: path.join(screenshotRoot, 'tibialis-action-playing-1024.png'), fullPage: false });
    await cta.click();
    await sleep(900);
    const restText = await player.innerText();
    const restPressed = await cta.getAttribute('aria-pressed');
    assert(playingText.includes('반복해서 보여 줍니다') || playingText.includes('움직임을 반복'));
    assert(restText.includes('서서히 돌아갑니다') || restText.includes('움직임으로 이해하기'));
    assert.equal(playingPressed, 'true');
    assert.equal(restPressed, 'false');
    await page.screenshot({ path: path.join(screenshotRoot, 'tibialis-action-restored-1024.png'), fullPage: false });
    const actual = await viewportRecord(1024, 768);
    return { selectedNerve: found[0], branchHeading: branchTitle, actionRouteLabels: routeLabels, exactLinkedMuscleSelected: await page.locator('.study-detail-content .names-card').first().innerText(), explicitNerveToActionRouteOpensFunctionTab: await functionTab.getAttribute('aria-selected') === 'true', actionPlayerBeforeCta: initialText, playingObserved: playingPressed === 'true', reclickRestObserved: restPressed === 'false', actualViewport: actual, screenshots: ['screenshots/deep-fibular-nerve-card-1024.png', 'screenshots/tibialis-action-rest-1024.png', 'screenshots/tibialis-action-playing-1024.png', 'screenshots/tibialis-action-restored-1024.png'] };
  });

  await record('longListRegionSwitchAndResponsiveLayout', async () => {
    await page.setViewportSize({ width: 1440, height: 900 });
    const search = page.getByRole('searchbox', { name: '구조 검색' });
    await search.fill('');
    await sleep(300);
    const list = page.locator('.region-structure-list');
    const scrollContainer = page.locator('.explorer-results-body');
    const before = await scrollContainer.evaluate(element => ({ scrollHeight: element.scrollHeight, clientHeight: element.clientHeight, count: element.querySelectorAll('.region-structure-list button').length }));
    await scrollContainer.evaluate(element => { element.scrollTop = element.scrollHeight; });
    await sleep(100);
    const scrolled = await scrollContainer.evaluate(element => element.scrollTop);
    assert(scrolled > 0);
    const trigger = page.locator('.region-picker-trigger');
    await trigger.hover();
    await page.locator('#atlas-region-menu').waitFor({ state: 'visible', timeout: 5000 });
    const labels = await page.locator('#atlas-region-menu button').allInnerTexts();
    const neck = labels.find(text => /목/.test(text));
    assert(neck, `head/neck region absent: ${labels.join(' | ')}`);
    await page.locator('#atlas-region-menu button').filter({ hasText: neck.trim() }).first().click();
    await sleep(300);
    const regionLabel = await trigger.innerText();
    assert(regionLabel.includes(neck.trim()));
    await page.screenshot({ path: path.join(screenshotRoot, 'head-neck-after-long-list-1440.png'), fullPage: false });
    const actual = await viewportRecord(1440, 900);
    return { longList: before, scrolledTo: scrolled, switchedRegion: neck.trim(), currentPickerLabel: regionLabel, actualViewport: actual, screenshot: 'screenshots/head-neck-after-long-list-1440.png' };
  });

  result.snapshotId = 'local-20261006101936364-bf4218bb';
  result.completedAt = new Date().toISOString();
  await browser.close();
  fs.writeFileSync(path.join(outputRoot, 'browser-validation.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
})().catch(error => {
  console.error(error?.stack || error);
  process.exitCode = 1;
});
