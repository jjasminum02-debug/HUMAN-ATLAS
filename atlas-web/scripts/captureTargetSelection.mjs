/** Development-only, resumable real-browser raster evidence. Never grants
 * anatomy/extent/human-review acceptance or changes the learner application.
 * Usage: node scripts/captureTargetSelection.mjs --packages <bundled node_modules>
 *        --chrome <Chrome executable> [--targets TA2:1512,TA2:2196] [--limit N]
 */
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRuntimeIntegration, readDatasetRoute } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const args = process.argv.slice(2);
const arg = (key, fallback) => { const n = args.indexOf(key); return n < 0 ? fallback : args[n + 1]; };
if (!arg('--packages') || !arg('--chrome')) throw Error('Pass the existing bundled packages and browser executable; no installation/profile reuse.');
const require = createRequire(resolve(arg('--packages'), 'task-capture.cjs'));
const { chromium } = require('playwright');
const sharp = require('sharp');
const json = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const baselinePath = arg('--baseline', 'work/evidence/T100/parallel-resolution-2026-09-30/integration/qa-baseline.json');
const baselineBytes = await readFile(resolve(root, baselinePath));
const baseline = JSON.parse(baselineBytes);
const overlayBytes = await readFile(resolve(root, baseline.overlay.path));
if (hash(overlayBytes) !== baseline.overlay.sha256) throw Error('Overlay changed; do not mix QA revisions.');
const overlay = JSON.parse(overlayBytes);
const scopeBytes = await readFile(resolve(root, 'atlas-data/catalog/target-scope-t96.json'));
const scope = JSON.parse(scopeBytes);
const contextBytes = await readFile(resolve(root, 'work/evidence/T78/reference/ta2-scope.json'));
const dataset = validateDataset(await json('atlas-data/source-cache/datasets/za/compiled/manifest.json'));
const runtime = buildRuntimeIntegration(overlay, dataset, hash(overlayBytes),
    hash(await readFile(resolve(root, overlay.policy.rightsEvidence))),
    { sha256: hash(scopeBytes), supportContext: { sha256: hash(contextBytes), terms: JSON.parse(contextBytes) }, targets: scope.targets });
const regionIds = scope.regions.map(r => r.regionId);
const targetFilter = new Set((arg('--targets', '')).split(',').filter(Boolean));
const cases = new Map(), routeFailures = [];
for (const row of baseline.routeCoverage.memberships) for (const path of row.paths) {
    if (targetFilter.size && !targetFilter.has(row.targetId)) continue;
    const params = new URLSearchParams({ regions: row.regionId, concept: path.conceptKey });
    if (path.side) params.set('side', path.side);
    const query = params.toString();
    const actual = readDatasetRoute('?' + query, runtime.objects, regionIds);
    const ref = { targetId: row.targetId, regionId: row.regionId, conceptKey: path.conceptKey, query };
    if (actual.selected !== path.sourceKey || !actual.regions.includes(row.regionId)) {
        routeFailures.push({ ...ref, expectedSourceKey: path.sourceKey, actual });
        continue;
    }
    const key = row.regionId + '|' + path.sourceKey;
    if (!cases.has(key)) cases.set(key, { caseKey: key, sourceKey: path.sourceKey,
        regionId: row.regionId, side: path.side, sourceName: path.sourceName, references: [] });
    cases.get(key).references.push(ref);
}
const out = resolve(root, arg('--out', 'work/evidence/T100/closure-audit-2026-09-30/browser-raster'));
await mkdir(resolve(out, 'screenshots'), { recursive: true });
let rows = [], messages = [], browserRuntime = null;
try {
    const previous = await json(resolve(out, 'raster-ledger.json'));
    if (previous.summary.overlaySha256 !== baseline.overlay.sha256
        || previous.summary.qaBaselineSha256 !== hash(baselineBytes)) throw Error('Existing captures use a different baseline; preserve them and choose a new output directory.');
    rows = previous.rows;
    messages = previous.summary.consoleErrors ?? [];
    browserRuntime = previous.summary.browserRuntime ?? null;
} catch (error) { if (error.code !== 'ENOENT') throw error; }
const completedKeys = new Set(rows.map(r => r.caseKey));
const summary = () => ({ overlaySha256: baseline.overlay.sha256, qaBaselineSha256: hash(baselineBytes),
    qaBaselinePath: baselinePath, browserRuntime,
    plannedPhysicalCases: cases.size, completedCases: rows.length,
    renderObserved: rows.filter(r => r.status === 'render_observed').length,
    failedOrUnverified: rows.filter(r => r.status !== 'render_observed').length,
    routeFailures, consoleErrors: messages, fullTargetExtentPass: false, humanReview: 'not_performed',
    claimBoundary: 'Route/card/source and isolated raster evidence only. Raster presence is not anatomical correspondence, side geometry, full target extent or exhaustive visual acceptance.' });
const checkpoint = async () => {
    await writeFile(resolve(out, 'raster-ledger.json'), JSON.stringify({ summary: summary(), rows }, null, 2) + '\n');
};
async function rasterEvidence(page, png) {
    const regions = await page.evaluate(() => {
        const canvas = document.querySelector('.whole-body-canvas canvas').getBoundingClientRect();
        const masks = [...document.querySelectorAll('.study-header,.study-sidebar,.study-details,.body-tools,.selection-view-options,.body-status,.stage-caption')]
            .map(el => el.getBoundingClientRect()).filter(r => r.width && r.height)
            .map(r => ({ x: r.x - canvas.x, y: r.y - canvas.y, width: r.width, height: r.height }));
        return { width: canvas.width, height: canvas.height, masks };
    });
    const { data, info } = await sharp(png).removeAlpha().raw().toBuffer({ resolveWithObject: true });
    const masks = regions.masks.map(r => ({ x: r.x * info.width / regions.width, y: r.y * info.height / regions.height,
        width: r.width * info.width / regions.width, height: r.height * info.height / regions.height }));
    let teal = 0;
    for (let y = 0; y < info.height; y++) for (let x = 0; x < info.width; x++) {
        if (masks.some(r => x >= r.x && x < r.x + r.width && y >= r.y && y < r.y + r.height)) continue;
        const n = (y * info.width + x) * info.channels;
        const [r, g, b] = data.subarray(n, n + 3);
        if (g > r + 15 && b > r + 10 && g > 40 && Math.abs(g - b) < 70) teal++;
    }
    return { selectedColorPixelCount: teal, uiPixelMaskApplied: true, pixelMasks: masks };
}
const browser = await chromium.launch({ executablePath: arg('--chrome'), headless: true,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => messages.push(String(e)));
    await page.goto(arg('--base-url', 'http://127.0.0.1:5173/'), { waitUntil: 'domcontentloaded', timeout: 30000 });
    const delivered = await page.evaluate(async () => {
        const bytes = await (await fetch('/__atlas/integration.json')).arrayBuffer();
        return { sha256: [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(v => v.toString(16).padStart(2, '0')).join(''), bytes: bytes.byteLength };
    });
    if (delivered.sha256 !== baseline.runtime.sha256 || delivered.bytes !== baseline.runtime.bytes) throw Error('Browser response differs from immutable QA baseline.');
    browserRuntime = { ...delivered, verified: true, endpoint: baseline.runtime.route, checkedAt: new Date().toISOString() };
    await page.locator('.whole-body-canvas canvas').waitFor({ timeout: 30000 });
    for (const item of [...cases.values()].slice(0, Number(arg('--limit', cases.size)))) {
        if (completedKeys.has(item.caseKey)) continue;
        const row = { ...item, overlaySha256: baseline.overlay.sha256, checkedAt: new Date().toISOString(),
            cardMatch: false, routeAliasesChecked: 0, localizedRasterObserved: false, anatomicalVisualQA: 'pending',
            targetExtent: 'not_asserted', sideClaim: 'source label only; anatomical side review separate' };
        try {
            for (const ref of item.references) {
                await page.evaluate(query => { history.pushState(null, '', '/?' + query); window.dispatchEvent(new PopStateEvent('popstate')); }, ref.query);
                await page.waitForFunction(expected => {
                    const canvas = document.querySelector('.whole-body-canvas canvas');
                    if (!canvas?.dataset.dataset) return false;
                    const state = JSON.parse(canvas.dataset.dataset);
                    return state.selected === expected && state.visible.includes(expected) && !state.failed.length;
                }, item.sourceKey, { timeout: 20000 });
                row.routeAliasesChecked++;
            }
            const expected = runtime.objects.find(r => r.sourceKey === item.sourceKey);
            const card = await page.locator('#study-details').innerText();
            row.cardMatch = [expected.names.en, expected.names.koModern, expected.names.koTraditional].every(v => v && card.includes(v));
            const details = page.locator('.body-tools details');
            await details.evaluate(el => { el.open = true; });
            const isolate = page.getByRole('button', { name: '선택만 보기', exact: true });
            if (await isolate.getAttribute('aria-pressed') !== 'true') await isolate.click();
            await page.getByRole('button', { name: '선택 부위 맞춤', exact: true }).click();
            await page.waitForFunction(expected => {
                const state = JSON.parse(document.querySelector('.whole-body-canvas canvas').dataset.dataset);
                return state.visible.length === 1 && state.visible[0] === expected;
            }, item.sourceKey, { timeout: 20000 });
            await page.evaluate(() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done))));
            row.sceneState = await page.locator('.whole-body-canvas canvas').evaluate(el => JSON.parse(el.dataset.dataset));
            const screenshot = 'screenshots/' + hash(Buffer.from(item.caseKey)).slice(0, 20) + '.png';
            const png = await page.locator('.whole-body-canvas canvas').screenshot({ path: resolve(out, screenshot) });
            Object.assign(row, await rasterEvidence(page, png));
            row.localizedRasterObserved = row.selectedColorPixelCount > 20;
            row.screenshotLocator = resolve(out, screenshot);
            row.screenshotSha256 = hash(png);
            row.status = row.cardMatch && row.localizedRasterObserved ? 'render_observed' : 'needs_visual_investigation';
            if (!rows.length) {
                const hide = page.getByRole('button', { name: '선택 숨기기', exact: true });
                await hide.click();
                await page.waitForFunction(() => JSON.parse(document.querySelector('.whole-body-canvas canvas').dataset.dataset).visible.length === 0);
                await page.evaluate(() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done))));
                const hidden = await page.locator('.whole-body-canvas canvas').screenshot({ path: resolve(out, 'screenshots/hidden-control.png') });
                const check = await rasterEvidence(page, hidden);
                row.hiddenControlPixelCount = check.selectedColorPixelCount;
                if (check.selectedColorPixelCount > 20) throw Error('UI-only negative raster control failed');
                row.hiddenControlPassed = true;
                await hide.click();
            }
        } catch (error) { row.status = 'unverified'; row.reason = String(error); }
        rows.push(row); await checkpoint();
        console.log(JSON.stringify({ case: rows.length, planned: cases.size, source: item.sourceName,
            status: row.status, pixels: row.selectedColorPixelCount, aliases: row.routeAliasesChecked }));
    }
} finally { await checkpoint(); await browser.close(); }
console.log(JSON.stringify(summary()));
