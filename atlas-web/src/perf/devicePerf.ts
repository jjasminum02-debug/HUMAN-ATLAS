// On-device performance check (ROADMAP 4-1 step 2 left-over: real iPad / low-end laptop numbers).
// Loaded only when the address has ?perf=1. Same measures as scripts/perfProfiles.mjs: first screen, transfer,
// a 4-second orbit with the default layers and again with every layer on. Results stay on the device; the learner
// copies them by hand. Plain DOM, outside the React tree.
type Scene = {
  controls: { target: { x: number; y: number; z: number; clone(): unknown } };
  camera: { position: { clone(): { sub(v: unknown): Orbit }; copy(v: unknown): { add(v: unknown): void } }; lookAt(v: unknown): void };
  renderer: { getPixelRatio(): number; info: { render: { calls: number; triangles: number } } };
  requestRender(): void;
};
type Orbit = { applyAxisAngle(axis: unknown, angle: number): Orbit };
type Result = { fps: number; p50: number; p95: number; ratio: number; calls: number; triangles: number };

const started = performance.now();
const scene = () => (window as unknown as { __atlasScene?: Scene }).__atlasScene;
const busy = () => /불러오는 중|준비하고/.test(document.querySelector('.body-status')?.textContent ?? '');
const wait = (ms: number) => new Promise(r => setTimeout(r, ms));
async function until(test: () => boolean, timeout = 240000) {
  const end = performance.now() + timeout;
  while (!test()) { if (performance.now() > end) throw new Error('시간 초과'); await wait(200); }
}
async function settle() { for (let quiet = 0; quiet < 3;) { await wait(250); if (busy()) { quiet = 0; await until(() => !busy()); } else quiet++; } }
function transferredMB() {
  const entries = [...performance.getEntriesByType('navigation'), ...performance.getEntriesByType('resource')] as PerformanceResourceTiming[];
  // Safari may report transferSize 0; the encoded body size is the closest stand-in.
  return entries.reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0) / 1e6;
}
function orbit(s: Scene): Promise<Result> {
  return new Promise(resolve => {
    const target = s.controls.target, offset = s.camera.position.clone().sub(target), times: number[] = [];
    let last = performance.now(); const end = last + 4000;
    const step = (now: number) => {
      times.push(now - last); last = now;
      offset.applyAxisAngle({ x: 0, y: 1, z: 0, isVector3: true }, .02); s.camera.position.copy(target).add(offset); s.camera.lookAt(target); s.requestRender();
      if (now < end) { requestAnimationFrame(step); return; }
      times.shift(); times.sort((a, b) => a - b);
      const info = s.renderer.info.render;
      resolve({ fps: times.length / 4, p50: times[Math.floor(times.length * .5)], p95: times[Math.floor(times.length * .95)], ratio: s.renderer.getPixelRatio(), calls: info.calls, triangles: info.triangles });
    };
    requestAnimationFrame(step);
  });
}
const line = (label: string, o: Result) =>
  `${label}: ${o.fps.toFixed(0)}fps · 프레임 p50 ${o.p50.toFixed(0)}ms p95 ${o.p95.toFixed(0)}ms · 픽셀 비율 ${o.ratio.toFixed(2)} · draw ${o.calls} · 삼각형 ${(o.triangles / 1e6).toFixed(2)}M`;

const panel = document.createElement('div');
panel.setAttribute('role', 'status');
panel.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:9999;max-width:min(460px,calc(100vw - 24px));padding:10px 12px;border-radius:10px;'
  + 'background:rgba(20,32,28,.92);color:#eef6f2;font:12px/1.5 -apple-system,system-ui,sans-serif;white-space:pre-wrap;box-shadow:0 4px 16px rgba(0,0,0,.25)';
const text = document.createElement('div'); text.textContent = '성능 측정: 모형을 불러오는 중…';
const run = document.createElement('button'), copy = document.createElement('button');
for (const b of [run, copy]) b.style.cssText = 'margin:8px 8px 0 0;padding:6px 10px;border-radius:8px;border:0;background:#14b8a6;color:#062b26;font-weight:600';
run.textContent = '측정 시작'; copy.textContent = '결과 복사'; run.disabled = true; copy.hidden = true;
panel.append(text, run, copy); document.body.append(panel);

let firstScreen = 0;
void until(() => Boolean(scene() && document.querySelector('.body-tools') && !(document.querySelector('.body-tools') as HTMLElement & { inert?: boolean }).inert))
  .then(async () => { firstScreen = (performance.now() - started) / 1000; await settle(); run.disabled = false; text.textContent = `첫 화면 ${firstScreen.toFixed(1)}s. 측정 중에는 화면을 만지지 마세요(약 20초).`; })
  .catch(() => { text.textContent = '모형을 불러오지 못했습니다. 주소가 https인지 확인하세요.'; });

run.onclick = async () => {
  const s = scene(); if (!s) return;
  run.disabled = true; copy.hidden = true;
  try {
    const lines = [`기기: ${navigator.userAgent}`, `화면 ${screen.width}×${screen.height} · DPR ${devicePixelRatio} · 창 ${innerWidth}×${innerHeight}`,
      `첫 화면 ${firstScreen.toFixed(1)}s · 전송 ${transferredMB().toFixed(1)}MB`];
    text.textContent = '기본 층으로 4초 회전 중…';
    lines.push(line('기본 층', await orbit(s)));
    text.textContent = '모든 층을 켜는 중…';
    const t = performance.now();
    for (const b of document.querySelectorAll<HTMLButtonElement>('.layer-row button[aria-pressed="false"]')) b.click();
    await wait(300); await settle();
    lines.push(`모든 층 켜기 ${((performance.now() - t) / 1000).toFixed(1)}s · 누적 전송 ${transferredMB().toFixed(1)}MB`);
    text.textContent = '모든 층으로 4초 회전 중…';
    lines.push(line('모든 층', await orbit(s)));
    text.textContent = lines.join('\n'); copy.hidden = false;
    copy.onclick = async () => {
      try { await navigator.clipboard.writeText(lines.join('\n')); copy.textContent = '복사됨'; }
      catch { copy.textContent = '길게 눌러 직접 복사하세요'; }
    };
  } catch (error) { text.textContent = `측정 실패: ${error instanceof Error ? error.message : String(error)}`; }
  finally { run.disabled = false; run.textContent = '다시 측정'; }
};
