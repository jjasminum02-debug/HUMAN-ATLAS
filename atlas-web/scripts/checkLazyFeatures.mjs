// Initial JavaScript budget of the built app (ROADMAP 4-1 step 2): what the home page loads before any interaction.
import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
const dist = new URL('../dist/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('.vite/manifest.json', dist), 'utf8'));
const initial = new Set();
function visit(key) {
  if (initial.has(key)) return;
  assert.ok(manifest[key], `missing manifest entry ${key}`);
  initial.add(key);
  for (const dependency of manifest[key].imports ?? []) visit(dependency);
}
visit('index.html'); visit('src/ui/App.tsx');
for (const lazy of ['src/viewer/skin/SkinControls.tsx', 'src/viewer/acupoints/AcupointEntry.tsx'])
  assert.ok(!initial.has(lazy), `${lazy} (held work) must stay out of the home page bundle`);
const chunks = await Promise.all([...initial].map(async key => ({ file: manifest[key].file, bytes: (await stat(new URL(manifest[key].file, dist))).size })));
const initialBytes = chunks.reduce((sum, chunk) => sum + chunk.bytes, 0);
assert.ok(initialBytes < 2 * 1024 * 1024, `initial JS grew to ${initialBytes} bytes; inspect eager feature imports`);
console.log(JSON.stringify({ initialChunks: chunks, initialBytes, passed: true }));
