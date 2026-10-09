import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
const dist = new URL('../dist/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('.vite/manifest.json', dist), 'utf8'));
const feature = 'src/ui/motionFeature.ts';
assert.ok(manifest[feature]?.isDynamicEntry, 'motion feature must be a separate async entry');
assert.ok(manifest['src/ui/App.tsx']?.dynamicImports?.includes(feature));
const initial = new Set();
function visit(key) {
  if (initial.has(key)) return;
  assert.ok(manifest[key], `missing manifest entry ${key}`);
  initial.add(key);
  for (const dependency of manifest[key].imports ?? []) visit(dependency);
}
visit('index.html'); visit('src/ui/App.tsx');
assert.ok(!initial.has(feature), 'home must not statically load the motion feature');
const chunks = await Promise.all([...initial].map(async key => ({file:manifest[key].file, bytes:(await stat(new URL(manifest[key].file, dist))).size})));
const initialBytes = chunks.reduce((sum, chunk) => sum + chunk.bytes, 0);
// A regression guard on initial JS, independent of the optional 3D/data asset budgets.
assert.ok(initialBytes < 2 * 1024 * 1024, `initial JS grew to ${initialBytes} bytes; inspect eager feature imports`);
console.log(JSON.stringify({initialChunks:chunks, initialBytes, deferredMotionFile:manifest[feature].file,
  deferredMotionBytes:(await stat(new URL(manifest[feature].file, dist))).size, passed:true}));
