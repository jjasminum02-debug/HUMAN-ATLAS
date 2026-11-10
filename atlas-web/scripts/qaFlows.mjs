// Q1 quality audit: ten learner flows in a real browser, then performance numbers (ROADMAP Q1).
//   pnpm qa:flows                 starts its own dev server (dev-only scene hooks are needed) and runs headless Chrome
//   pnpm qa:flows --url http://127.0.0.1:5173 --headed
// Uses the installed Google Chrome through playwright-core (no browser download). Exit code 1 if a flow fails.
import { chromium } from 'playwright-core';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const flag = name => args.includes(name);
const option = name => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const only = option('--only');

let server, base = option('--url');
if (flag('--preview')) {
  // The built app from `pnpm build:qa`: production code plus the two scene hooks these flows read.
  const { preview } = await import('vite');
  const previewServer = await preview({ root: fileURLToPath(new URL('..', import.meta.url)), mode: 'qa', logLevel: 'error', preview: { host: '127.0.0.1', port: 5197, strictPort: false } });
  server = { close: () => previewServer.close(), label: '빌드본' };
  base = previewServer.resolvedUrls.local[0].replace(/\/$/, '');
} else if (!base) {
  const { createServer } = await import('vite');
  server = await createServer({ root: fileURLToPath(new URL('..', import.meta.url)), logLevel: 'error', server: { host: '127.0.0.1', port: 5199, strictPort: false } });
  await server.listen();
  base = server.resolvedUrls.local[0].replace(/\/$/, '');
}
const browser = await chromium.launch({ channel: 'chrome', headless: !flag('--headed') });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, locale: 'ko-KR' });

// ── helpers ─────────────────────────────────────────────────────────────────
const errors = [];
const watch = page => {
  page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
  page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
};
async function open(page, path = '/') {
  const started = Date.now();
  await page.goto(base + path);
  await page.waitForFunction(() => document.querySelector('.body-tools') && !document.querySelector('.body-tools').inert, null, { timeout: 60000 });
  await settle(page);
  return Date.now() - started;
}
/** Wait until every requested model has loaded and the scene has drawn. */
async function settle(page) {
  // A selection can turn a layer on a frame later and start new loads: require two quiet checks in a row.
  for (let quiet = 0; quiet < 2;) {
    await page.evaluate(() => new Promise(r => setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(r)), 120)));
    const loading = await page.evaluate(() => /불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''));
    if (loading) { quiet = 0; await page.waitForFunction(() => !/불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? ''), null, { timeout: 60000 }); }
    else quiet++;
  }
}
/** Scene facts by structure key: visible, material name (encodes tissue:mode:phase:role…). */
const scene = page => page.evaluate(() => {
  const out = {};
  window.__atlasScene.root.traverse(o => { if (o.isMesh && o.userData.sourceKey) out[o.userData.sourceKey] = { visible: o.visible && (o.parent?.visible ?? true), material: o.material?.name ?? '' }; });
  return out;
});
const runtime = page => page.evaluate(() => fetch('/__atlas/integration.json').then(r => r.json()).then(d => d.objects.map(o => ({ key: o.sourceKey, label: o.label, en: o.names.en, side: o.side, kind: o.kind }))));
async function search(page, text, label) {
  const input = page.getByRole('searchbox', { name: '구조 검색' });
  await input.fill(text);
  const result = page.locator('nav.region-structure-list button').filter({ hasText: label }).first();
  await result.waitFor({ timeout: 10000 });
  await result.click();
  await settle(page);
}
const card = page => page.locator('#study-details').innerText();
const pressed = (page, scope, name) => page.locator(`${scope} button`, { hasText: name }).first().getAttribute('aria-pressed');
function expect(condition, message) { if (!condition) throw new Error(message); }

// ── flows ───────────────────────────────────────────────────────────────────
const flows = [
  ['첫 화면: 전신 모형과 기본 층, 퀴즈·북마크', async page => {
    await open(page);
    expect(await pressed(page, '.layer-row', '얕은 근육') === 'true' && await pressed(page, '.layer-row', '뼈') === 'true', '기본 층(얕은 근육·뼈)이 켜져 있지 않음');
    const visible = Object.values(await scene(page)).filter(n => n.visible).length;
    expect(visible > 300, `보이는 구조 ${visible}개`);
    // Q2-3 name quiz: exactly one drawn structure is highlighted (not selected: no card); its label is one of four choices.
    await page.getByRole('button', { name: '퀴즈·북마크' }).click();
    await page.getByRole('button', { name: '문제 내기' }).click();
    await page.locator('.quiz-choices button').first().waitFor();
    const highlighted = Object.entries(await scene(page)).filter(([, n]) => n.visible && n.material.includes(':selected:')).map(([key]) => key);
    expect(highlighted.length === 1 && !(await page.locator('#study-details').count()), `퀴즈 강조 ${highlighted.length}개`);
    const target = (await runtime(page)).find(r => r.key === highlighted[0]);
    const choices = await page.locator('.quiz-choices button').allInnerTexts();
    expect(choices.length === 4 && choices.includes(target.label), `보기 ${choices.join('/')} · 정답 ${target.label}`);
    await page.locator('.quiz-choices').getByRole('button', { name: target.label, exact: true }).click();
    await page.locator('.quiz-result.is-right').waitFor({ timeout: 5000 }).catch(() => { throw new Error(`이름 퀴즈 채점 실패: ${target.label}`); });
    // Find quiz: selecting the named structure (here through search) is graded as the answer.
    await page.locator('.quiz-kinds button', { hasText: '모형에서 찾기' }).click();
    const name = (await page.locator('.quiz-prompt').innerText()).match(/^모형에서 (?:왼쪽 |오른쪽 )?(.+)을\(를\) 찾아/)[1];
    await search(page, name, name);
    await page.locator('.quiz-result.is-right').waitFor({ timeout: 5000 }).catch(async () => { throw new Error(`찾기 퀴즈 채점 실패: ${name} → ${await page.locator('.quiz').innerText()}`); });
    // Bookmark the found structure from its card; the panel lists it.
    await page.locator('.bookmark-toggle').click();
    await page.getByRole('tab', { name: /북마크/ }).click();
    expect((await page.locator('.bookmarks li').allInnerTexts()).some(t => t.includes(name)), '북마크 목록에 없음');
    const score = await page.locator('.quiz-score').count() ? '' : (await page.getByRole('tab', { name: '퀴즈' }).click(), await page.locator('.quiz-score').innerText());
    return `보이는 구조 ${visible}개 · 이름 퀴즈(${target.label})·찾기 퀴즈(${name}) 정답 · 북마크 · ${score}`;
  }],
  ['검색으로 근육 찾기: 넙다리곧은근 이름·기시·정지', async page => {
    await open(page);
    await search(page, '넙다리곧은근', '대퇴직근'); // modern name finds the Sino-Korean title
    const text = await card(page);
    expect(text.includes('Rectus femoris') && text.includes('기시') && text.includes('정지'), '카드에 영어명·기시·정지 없음');
    const key = new URL(page.url()).searchParams.get('source');
    expect((await scene(page))[key]?.material.includes(':selected:'), '3D에서 선택 표시 안 됨');
    // C4: the origin (Z-Anatomy patch) and insertion (contact estimate) areas are drawn on the bones.
    await page.locator('.attachment-areas li').first().waitFor({ timeout: 10000 });
    const areas = await page.evaluate(() => { const roles = []; window.__atlasScene.root.traverse(o => { if (o.isMesh && o.visible && o.userData.attachmentPatch) roles.push(o.material.name.match(/attachment(\w+)/)?.[1]); }); return roles.sort(); });
    expect(areas.join() === 'Insertion,Origin', `뼈 위 부착 면: ${areas.join() || '없음'}`);
    // C2: blood supply from the two-source muscle card table.
    const supply = await page.locator('.attachment-section', { hasText: '혈액공급' }).innerText({ timeout: 10000 });
    expect(supply.includes('가쪽넙다리휘돌이동맥'), `혈액공급: ${supply.replace(/\s+/g, ' ').slice(0, 200)}`);
    // Q2-1: the supplying artery opens in the vessel layer, and its card lists the muscle back.
    await page.locator('.attachment-section', { hasText: '혈액공급' }).getByRole('button', { name: /가쪽넙다리휘돌이동맥/ }).click();
    await page.locator('.vessel-supplied').waitFor({ timeout: 10000 });
    expect(await pressed(page, '.layer-row', '혈관') === 'true', '혈관 층이 자동으로 켜지지 않음');
    const supplied = await page.locator('.vessel-supplied').innerText();
    expect(supplied.includes('대퇴직근'), `혈액을 받는 근육: ${supplied.replace(/\s+/g, ' ').slice(0, 200)}`);
    await settle(page);
    const vessels = await page.evaluate(() => { let n = 0; window.__atlasScene.root.traverse(o => { if (o.isMesh && o.visible && /^vessel:/.test(o.material.name)) n++; }); return n; });
    expect(vessels > 600, `보이는 혈관 ${vessels}개`);
    return `카드·3D 선택 일치, 기시·정지 면·혈액공급 표시 → 동맥 카드, 혈관 ${vessels}개`;
  }],
  ['무릎 인대 구조 보기: 앞십자인대 → 무릎 움직여 보기', async page => {
    await open(page);
    await search(page, '앞십자인대', '전십자인대'); // modern name finds the traditional label
    expect(await pressed(page, '.layer-row', '인대·관절') === 'true', '인대·관절 층이 자동으로 켜지지 않음');
    await page.locator('.attachment-section h3', { hasText: '잇는 뼈' }).waitFor({ timeout: 10000 });
    const text = await card(page);
    expect(text.includes('대퇴골') && text.includes('경골'), '잇는 뼈에 대퇴골·경골 없음');
    // C3: the card lists who moves the knee, per movement.
    const movers = await page.locator('.joint-movers').innerText({ timeout: 10000 });
    expect(/굽힘/.test(movers) && /폄/.test(movers) && movers.includes('대퇴직근'), `무릎을 움직이는 근육 목록: ${movers.replace(/\s+/g, " ").slice(0, 300)}`);
    await page.getByRole('button', { name: /무릎관절 .* 움직여 보기/ }).click();
    await page.locator('#movement-panel .movement-dofs').waitFor();
    expect(await pressed(page, '.movement-joints', '무릎') === 'true', '움직임 창이 무릎으로 열리지 않음');
    return '인대 카드(움직이는 근육 목록) → 무릎 움직임 창';
  }],
  ['회전근개 작용 보기: 극하근 가쪽돌림 재생과 색', async page => {
    await open(page);
    await search(page, '극하근', '극하근');
    await page.getByRole('tab', { name: '기능' }).click();
    const summary = await page.locator('.muscle-action-summary').innerText({ timeout: 10000 });
    expect(summary.includes('가쪽으로 돌'), `작용 요약: ${summary.replace(/\s+/g, ' ')}`);
    const play = page.locator('.rig-actions button', { hasText: '가쪽돌림' }).first();
    await play.waitFor({ timeout: 10000 });
    const rows = await runtime(page), side = new URL(page.url()).searchParams.get('source');
    const me = rows.find(r => r.key === side);
    await play.click();
    await page.waitForTimeout(1300);
    const nodes = await scene(page);
    const byLabel = (label, role) => rows.filter(r => r.label === label && r.side === me.side).some(r => nodes[r.key]?.material.includes(`:${role}:`));
    expect(byLabel('소원근', 'agonist'), '같은 쪽 소원근이 주동근 색이 아님');
    expect(byLabel('견갑하근', 'antagonist'), '같은 쪽 견갑하근이 길항근 색이 아님');
    await page.waitForFunction(() => !document.querySelector('.rig-actions [aria-pressed="true"]'), null, { timeout: 8000 });
    const after = await scene(page);
    expect(!Object.values(after).some(n => /:(agonist|antagonist):/.test(n.material)), '재생 뒤 색이 남음');
    return '소원근 빨강·견갑하근 파랑, 끝나면 해제';
  }],
  ['관절 움직임 창: 팔꿉 90° 주동근·길항근 목록', async page => {
    await open(page);
    await page.getByRole('button', { name: '관절 움직임' }).click();
    await page.locator('.movement-joints button', { hasText: '팔꿉' }).click();
    const slider = page.locator('.movement-dofs label', { hasText: '굽힘 / 폄' }).locator('input');
    await slider.fill('90');
    await page.locator('.movement-roles').waitFor();
    const roles = await page.locator('.movement-roles').innerText();
    expect(roles.includes('상완근') && /삼두근/.test(roles), `목록에 상완근·삼두근 없음: ${roles.slice(0, 120)}`);
    await page.getByRole('button', { name: '처음 자세로' }).click();
    expect((await page.locator('.movement-dofs output').first().innerText()) === '중립', '처음 자세로 돌아가지 않음');
    // 4-1 step 4: shoulder girdle, fingers and neck have their own sliders and movers.
    const movers = async (group, dof, value) => {
      await page.locator('.movement-joints button', { hasText: group }).click();
      await page.locator('.movement-dofs label', { hasText: dof }).locator('input').first().fill(String(value));
      await page.locator('.movement-roles').waitFor();
      return page.locator('.movement-roles').innerText();
    };
    const girdle = await movers('어깨뼈', '올림 / 내림', 25);
    expect(girdle.includes('견갑거근'), `어깨뼈 올림 주동근: ${girdle.slice(0, 120)}`);
    const fingers = await movers('손가락', '몸쪽마디 굽힘', 60);
    expect(fingers.includes('천지굴근'), `손가락 몸쪽마디 굽힘 주동근: ${fingers.slice(0, 120)}`);
    const neck = await movers('목·머리', '왼쪽 돌림 / 오른쪽 돌림', 30);
    expect(neck.includes('흉쇄유돌근'), `목 돌림 주동근: ${neck.slice(0, 160)}`);
    await page.getByRole('button', { name: '처음 자세로' }).click();
    return '굽힘 주동근(상완근)·길항근(삼두근), 어깨뼈 올림(견갑거근)·손가락 굽힘(천지굴근)·목 돌림(흉쇄유돌근), 처음 자세 복귀';
  }],
  ['층 벗기기: 근막 → 얕은 근육, 되돌리기, 투명도, 단면', async page => {
    await open(page);
    await page.locator('.layer-row button', { hasText: '근막' }).click();
    await settle(page);
    await page.getByRole('button', { name: '한 겹 벗기기' }).click();
    expect(await pressed(page, '.layer-row', '근막') === 'false', '첫 벗기기에서 근막이 꺼지지 않음');
    await page.getByRole('button', { name: '한 겹 벗기기' }).click();
    expect(await pressed(page, '.layer-row', '얕은 근육') === 'false', '두 번째 벗기기에서 얕은 근육이 꺼지지 않음');
    await page.getByRole('button', { name: '벗긴 층 되돌리기' }).click();
    expect(await pressed(page, '.layer-row', '얕은 근육') === 'true', '되돌리기에서 얕은 근육이 돌아오지 않음');
    await page.getByRole('button', { name: '더보기' }).click();
    await page.locator('.layer-opacity label', { hasText: '뼈' }).locator('input').fill('50');
    const translucent = await page.evaluate(() => { let n = 0; window.__atlasScene.root.traverse(o => { if (o.isMesh && o.visible && o.material?.name?.startsWith('bone:') && o.material.opacity < .6) n++; }); return n; });
    expect(translucent > 50, `반투명 뼈 ${translucent}개`);
    // Q2-2: an axial section clips every pass and fills cut faces (double-sided opaque tissue); 끄기 restores both.
    const sectionState = () => page.evaluate(() => { const s = window.__atlasScene; let both = 0, opaque = 0;
      s.root.traverse(o => { if (o.isMesh && o.visible && !o.material.transparent) { opaque++; if (o.material.side === 2) both++; } });
      return { planes: s.renderer.clippingPlanes.length, both, opaque }; });
    await page.getByRole('button', { name: '단면', exact: true }).click();
    await page.locator('#section-panel button', { hasText: '가로면' }).click();
    const on = await sectionState();
    expect(on.planes === 1 && on.both === on.opaque && on.opaque > 0, `단면 켬: ${JSON.stringify(on)}`);
    expect(/바닥에서 \d+cm/.test(await page.locator('.section-position output').innerText()), '단면 위치 표시 없음');
    await page.locator('#section-panel button', { hasText: '끄기' }).click();
    const off = await sectionState();
    expect(off.planes === 0 && off.both === 0, `단면 끔: ${JSON.stringify(off)}`);
    return `벗기기·되돌리기, 뼈 50% (${translucent}개), 가로 단면 ${on.both}개 면 채움 후 해제`;
  }],
  ['신경 보기: 좌골신경 주행', async page => {
    await open(page);
    await page.getByRole('searchbox', { name: '구조 검색' }).fill('좌골신경');
    const model = page.locator('.nerve-search-result button', { hasText: '오른쪽 모형' }).first();
    const listed = page.locator('nav.region-structure-list button', { hasText: '좌골신경' }).first();
    await Promise.race([model.waitFor({ timeout: 10000 }), listed.waitFor({ timeout: 10000 })]);
    await (await model.count() ? model : listed).click();
    await settle(page);
    expect(await pressed(page, '.layer-row', '신경') === 'true', '신경 층이 켜지지 않음');
    const status = await page.locator('.body-status').innerText();
    expect(status.includes('신경 주행 보기'), `상태: ${status.split('\n')[0]}`);
    return '신경 층 자동, 주행 관찰 상태';
  }],
  ['기시·정지 관찰: 넙다리곧은근 기시 뼈', async page => {
    await open(page);
    await search(page, '넙다리곧은근', '대퇴직근'); // modern name finds the Sino-Korean title
    const button = page.locator('.attachment-origin .attachment-observe');
    await button.click();
    await settle(page);
    expect(await button.getAttribute('aria-pressed') === 'true', '기시 관찰이 켜지지 않음');
    const origin = Object.values(await scene(page)).filter(n => n.visible && /^bone:origin(Area)?Context/.test(n.material)).length;
    expect(origin >= 1, '기시 뼈 색이 없음');
    await button.click();
    expect(await button.getAttribute('aria-pressed') === 'false', '기시 관찰이 끝나지 않음');
    return `기시 뼈 ${origin}개 표시 후 해제`;
  }],
  ['부위 탐색: 넙다리 부위 목록과 시점', async page => {
    await open(page);
    const before = await page.evaluate(() => window.__atlasScene.camera.position.toArray());
    await page.locator('.explore-rail').click();
    await page.locator('.region-picker-trigger').click();
    await page.locator('.region-picker-menu button', { hasText: '넙다리' }).click();
    await settle(page);
    await page.waitForTimeout(900); // camera transition
    expect(new URL(page.url()).searchParams.get('regions') === 'thigh', `주소: ${page.url()}`);
    const count = await page.locator('nav.region-structure-list button').count();
    expect(count > 20, `목록 ${count}개`);
    const after = await page.evaluate(() => window.__atlasScene.camera.position.toArray());
    expect(Math.hypot(...after.map((v, i) => v - before[i])) > .05, '시점이 부위로 이동하지 않음');
    // D3 part 2: browsing by movement comes from the rig action table (no clips).
    await page.locator('.explorer-mode button', { hasText: '근육 작용 찾기' }).click();
    const knee = page.locator('.motion-library details', { hasText: '무릎관절 굽힘' }).first();
    await knee.waitFor({ timeout: 10000 }).catch(async error => { throw new Error(`무릎관절 굽힘 항목 없음: ${(await page.locator('.motion-library summary').allInnerTexts()).slice(0, 8).join(', ')} / ${await page.locator('.result-count').first().innerText()}`); });
    await knee.locator('summary').click();
    const movers = await knee.innerText();
    expect(/대퇴이두근|반건양근/.test(movers), `넙다리 무릎 굽힘 근육: ${movers.replace(/\s+/g, ' ').slice(0, 160)}`);
    await knee.locator('button').first().click();
    await page.locator('.rig-actions').waitFor({ timeout: 10000 }).catch(async () => { throw new Error(`기능 탭 재생 없음: tab=${await page.locator('[role=tab][aria-selected=true]').allInnerTexts()} selected=${new URL(page.url()).searchParams.get('source')} rig=${await page.locator('.rig-actions').count()} title=${await page.locator('.study-detail-header h2').innerText().catch(() => '-')}`); });
    // A bone opens the joints that move it (back to the structure list first).
    await page.evaluate(() => [...document.querySelectorAll('.explorer-mode button')].find(b => b.textContent === '구조 찾기')?.click());
    await search(page, '경골', '경골');
    const joints = await page.locator('.bone-joints').innerText({ timeout: 10000 });
    expect(joints.includes('무릎관절') && joints.includes('발목관절'), `경골 관절: ${joints.replace(/\s+/g, ' ')}`);
    return `목록 ${count}개, 시점 이동, 움직임별 근육(무릎 굽힘) → 기능 탭, 경골 → 무릎·발목 관절`;
  }],
  ['모형 클릭으로 선택 → 숨기기 → 뒤로 가기', async page => {
    await open(page);
    const box = await page.locator('.whole-body-canvas canvas').boundingBox();
    // Aim 30 cm above the orbit centre (pelvis), off the midline: the right chest wall.
    const target = await page.evaluate(() => {
      const s = window.__atlasScene, rect = s.renderer.domElement.getBoundingClientRect(), v = s.controls.target.clone().add({ x: -.07, y: .3, z: .08 }).project(s.camera);
      return [(v.x + 1) / 2 * rect.width, (1 - v.y) / 2 * rect.height];
    });
    await page.mouse.click(box.x + target[0], box.y + target[1]);
    await page.waitForFunction(() => new URL(location.href).searchParams.get('source'), null, { timeout: 5000 });
    await settle(page);
    const key = new URL(page.url()).searchParams.get('source');
    await page.getByRole('button', { name: '선택 숨기기' }).click();
    await settle(page);
    const hidden = await scene(page);
    expect(!hidden[key]?.visible, '선택 숨기기 뒤에도 보임'); // hidden meshes leave the scene graph
    await page.goBack();
    await page.waitForFunction(k => new URL(location.href).searchParams.get('source') !== k, key, { timeout: 5000 });
    return `클릭 선택 (${(await runtime(page)).find(r => r.key === key)?.label}), 숨김, 뒤로 가기`;
  }],
];

// ── performance ─────────────────────────────────────────────────────────────
async function performance(page) {
  const coldMs = await open(page);
  const transfer = await page.evaluate(() => {
    const entries = performance.getEntriesByType('resource').filter(e => e.name.includes('/__atlas/'));
    return { requests: entries.length, mb: entries.reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0) / 1e6 };
  });
  // Orbit for 3 s: every frame turns the camera and asks for a render.
  const orbit = await page.evaluate(() => new Promise(resolve => {
    const s = window.__atlasScene, target = s.controls.target, offset = s.camera.position.clone().sub(target), times = [];
    let last = performance.now(); const end = last + 3000;
    const step = now => {
      times.push(now - last); last = now;
      offset.applyAxisAngle({ x: 0, y: 1, z: 0, isVector3: true }, .02); s.camera.position.copy(target).add(offset); s.camera.lookAt(target); s.requestRender();
      if (now < end) requestAnimationFrame(step);
      else {
        times.shift(); times.sort((a, b) => a - b);
        const info = s.renderer.info, render = [...s.renderDurationsMs].sort((a, b) => a - b);
        resolve({ renderP50Ms: render[Math.floor(render.length * .5)], renderP95Ms: render[Math.floor(render.length * .95)], frames: times.length, p50Ms: times[Math.floor(times.length * .5)], p95Ms: times[Math.floor(times.length * .95)],
          calls: info.render.calls, triangles: info.render.triangles, geometries: info.memory.geometries });
      }
    };
    requestAnimationFrame(step);
  }));
  const pose = await page.evaluate(async () => {
    const rig = await window.__atlasRig.load(), samples = [];
    for (let i = 0; i < 6; i++) {
      if (i === 1) await new Promise(r => setTimeout(r, 1500)); // first pose fetches the skin weights
      const started = performance.now();
      window.__atlasRig.set(rig, { 'hip_r:flexion': 10 + i * 8, 'knee_r:flexion': 20 + i * 10, 'elbow_l:flexion': 30 + i * 10, 'shoulder_r:abduction': 40, 'back:flexion': 10 });
      samples.push(performance.now() - started);
    }
    window.__atlasRig.reset(rig);
    return { firstMs: samples[0], steadyMs: samples.slice(1).reduce((a, b) => a + b, 0) / (samples.length - 1) };
  });
  const heapMb = await page.evaluate(() => (performance.memory?.usedJSHeapSize ?? 0) / 1e6);
  return { coldLoadMs: coldMs, ...transfer, orbit, pose, heapMb };
}

// ── run ─────────────────────────────────────────────────────────────────────
let failed = 0;
const selected = flows.filter((_, i) => !only || only.split(',').map(Number).includes(i + 1));
for (const [name, run] of selected) {
  const page = await context.newPage(); watch(page); errors.length = 0;
  const started = Date.now();
  try {
    const note = await run(page);
    if (errors.length) throw new Error(errors.slice(0, 3).join(' | '));
    console.log(`✔ ${name} — ${note} (${((Date.now() - started) / 1000).toFixed(1)}s)`);
  } catch (error) {
    failed++;
    console.log(`✖ ${name} — ${error.message.split('\n')[0]}`);
  }
  await page.close();
}
if (!only) {
  const page = await context.newPage();
  const p = await performance(page);
  console.log(`\n성능 (1440×900, DPR 2, ${server?.label ?? (server ? '개발 서버' : base)}):`);
  console.log(`  처음 로딩 ${(p.coldLoadMs / 1000).toFixed(2)}s · 모형 요청 ${p.requests}개 ${p.mb.toFixed(1)}MB`);
  console.log(`  회전 ${p.orbit.frames}프레임/3s · 프레임 간격 p50 ${p.orbit.p50Ms.toFixed(1)}ms p95 ${p.orbit.p95Ms.toFixed(1)}ms (화면 주사율 상한) · 렌더 CPU p50 ${p.orbit.renderP50Ms.toFixed(1)}ms p95 ${p.orbit.renderP95Ms.toFixed(1)}ms · draw ${p.orbit.calls} · 삼각형 ${(p.orbit.triangles / 1e6).toFixed(2)}M`);
  console.log(`  자세 변경 첫 ${p.pose.firstMs.toFixed(1)}ms(뼈만, 가중치 요청) · 가중치 로딩 후 뼈+연조직 ${p.pose.steadyMs.toFixed(1)}ms · JS heap ${p.heapMb.toFixed(0)}MB`);
  await page.close();
}
await browser.close();
await server?.close();
console.log(failed ? `\n${failed}/${selected.length} 흐름 실패` : `\n${selected.length}개 흐름 모두 통과`);
process.exit(failed ? 1 : 0);
