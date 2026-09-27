// Developer-only, excluded from build entry points. Hold/fail the real transport;
// successful retries always use the frozen T56 manifest and GLBs, never dummy anatomy.
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '../src/ui/App';
if (!import.meta.env.DEV) throw new Error('Local QA only');
const original = window.fetch.bind(window);
let release: ((fail: boolean) => void) | undefined;
let intercepted = false;
const mode = new URLSearchParams(location.search).get('failure') ?? 'manifest';
window.fetch = async (...args) => {
  const url = String(args[0]);
  const target = mode === 'manifest' ? url.endsWith('/__atlas/body/manifest.json') : url.startsWith('/__atlas/body/') && url.endsWith('.glb');
  if (!target || intercepted) return original(...args);
  intercepted = true; // Reserve exactly one request before concurrent chunk loads start.
  const signal = args[1]?.signal;
  await new Promise<void>((resolve, reject) => {
    const abort = () => { intercepted = false; release = undefined; reject(new DOMException('Aborted', 'AbortError')); };
    if (signal?.aborted) return abort();
    signal?.addEventListener('abort', abort, {once:true});
    release = fail => {
      signal?.removeEventListener('abort', abort); release = undefined;
      intercepted = true;
      if (fail) reject(new Error('T57 intentionally rejected transport')); else resolve();
    };
  });
  return original(...args);
};
const controls = document.createElement('div');
controls.style.cssText = 'position:fixed;bottom:0;right:0;z-index:99;background:#fff;padding:8px;border:1px solid #bbb;font:12px sans-serif';
for (const [label,fail] of [['실제 응답 전달',false],['이번 요청 실패',true]] as const) {
  const button = document.createElement('button'); button.textContent = label;
  button.onclick = () => release?.(fail); controls.append(button);
}
document.body.append(controls);
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
