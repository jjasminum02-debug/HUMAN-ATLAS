import { createRequire } from 'node:module';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../../', import.meta.url));
const output = root + 'work/evidence/T90/browser/';
const require = createRequire(process.env.ATLAS_QA_DEPENDENCIES || '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t90.cjs');
const { chromium } = require('playwright');
const runtime = JSON.parse(await readFile(output + 'runtime.json'));
const key = runtime.objects.find(row => row.kind === 'nerve' && row.names.en === 'Deep fibular nerve' && row.side === 'left').sourceKey;
const browser = await chromium.launch({ executablePath: process.env.ATLAS_QA_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const checks = [], captures = [], errors = [], profiles = {};
const check = (name, pass, detail) => { checks.push({ name, pass, detail }); if (!pass) throw Error(name); };
const capture = async (page, name) => { const path = 'work/evidence/T90/browser/' + name + '.png'; await page.screenshot({ path: root + path }); captures.push({ path, sha256: createHash('sha256').update(await readFile(root + path)).digest('hex') }); };
const wait = async page => {
  await page.waitForFunction(() => { const c = document.querySelector('.whole-body-canvas canvas'); if (!c?.dataset.dataset || !c?.dataset.scene) return false; const d = JSON.parse(c.dataset.dataset), s = JSON.parse(c.dataset.scene); return d.pending === 0 && d.failed.length === 0 && s.root === d.root && s.visibleMeshes === d.visible.length && !document.querySelector('.whole-body-canvas').inert; });
  // Scene counters are reported every 500ms. Sample after the presentation settled.
  await page.waitForTimeout(750);
};
const state = page => page.locator('.whole-body-canvas canvas').evaluate(c => ({ dataset: JSON.parse(c.dataset.dataset), scene: JSON.parse(c.dataset.scene) }));
try {
  const p = await browser.newPage({ viewport: { width: 390, height: 844 } });
  p.on('pageerror', e => errors.push(e.message)); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto('http://127.0.0.1:5184/?regions=leg&source=' + key); await wait(p);
  await p.getByRole('button', { name: '신경', exact: true }).click(); await wait(p);
  await p.getByRole('button', { name: '선택 맞춤', exact: true }).click(); await wait(p);
  check('390 fitted actual nerve with open card', await p.locator('.study-details').getAttribute('open') !== null && await p.locator('.study-detail-content').isVisible(), (await state(p)).dataset.selected);
  await capture(p, '390-deep-selection-fit');
  await p.locator('.mobile-detail-summary').click();
  await p.waitForFunction(() => !document.querySelector('.study-details').open);
  await p.getByRole('button', { name: '선택 맞춤', exact: true }).click(); await wait(p);
  check('390 card collapse remains learner controlled', await p.locator('.study-details').getAttribute('open') === null, null);
  await capture(p, '390-deep-expanded-scene');
  const identity = await state(p);
  await p.setViewportSize({ width: 1024, height: 900 });
  await p.waitForFunction(() => document.querySelector('.study-details').open);
  await wait(p);
  const restored = await state(p);
  check('mobile collapse then desktop resize restores readable card', await p.locator('.study-detail-content').isVisible() && (await p.locator('.study-details').boundingBox()).height > 100, null);
  check('responsive card restoration retains scene selection and camera', restored.dataset.root === identity.dataset.root && restored.dataset.selected === key && JSON.stringify(restored.scene.camera) === JSON.stringify(identity.scene.camera), null);
  await capture(p, '1024-deep-selection-fit');
  await p.setViewportSize({ width: 1440, height: 1000 }); await wait(p);
  check('1440 readable card after responsive resize', await p.locator('.study-detail-content').isVisible(), null);
  await capture(p, '1440-deep-selection-fit');
  await p.close();
  // Fresh page per case keeps CPU/frame sample history scoped to that case.
  for (const region of ['neck', 'thorax', 'abdomen-lumbar', 'leg']) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:5184/?regions=' + region + (region === 'leg' ? '&source=' + key : '')); await wait(page);
    if (region === 'leg') { await page.getByRole('button', { name: '신경', exact: true }).click(); await wait(page); }
    profiles[region] = await state(page);
    check('fresh profile counters agree: ' + region, profiles[region].scene.visibleMeshes === profiles[region].dataset.visible.length && profiles[region].scene.root === profiles[region].dataset.root, null);
    await capture(page, '1440-final-profile-' + region); await page.close();
  }
  check('responsive and fresh profile console errors', errors.length === 0, errors);
} finally {
  await writeFile(output + 'responsive-fit.json', JSON.stringify({ checks, captures, profiles, errors, selected: key, limitations: ['Desktop Chrome at CSS viewport widths, not mobile physical device', 'CPU render() call duration differs from GPU execution and frame interval', 'GPU/VRAM/total process memory not observed'] }, null, 2) + '\n');
  await browser.close();
}
console.log(JSON.stringify({ passed: checks.filter(c => c.pass).length, failed: checks.filter(c => !c.pass).length, captures: captures.length, errors }));
