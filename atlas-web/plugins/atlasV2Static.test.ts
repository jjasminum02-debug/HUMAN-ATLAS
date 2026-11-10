import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { brotliDecompressSync } from 'node:zlib';
import { precompress, staticRuntimeMiddleware } from './atlasV2Static.ts';

const sha = 'a'.repeat(64);
async function site() {
  const dir = await mkdtemp(join(tmpdir(), 'atlas-static-'));
  await mkdir(join(dir, '__atlas/datasets/za-v2'), { recursive: true }); await mkdir(join(dir, 'assets'));
  await writeFile(join(dir, '__atlas/integration.json'), JSON.stringify({ rows: Array(500).fill('repeated learner row') }));
  await writeFile(join(dir, `__atlas/datasets/za-v2/${sha}.glb`), Buffer.alloc(4096, 7));
  await writeFile(join(dir, 'assets/app-abc.js'), 'console.log("x");'.repeat(100));
  return dir;
}
function get(dir: string, url: string, accept = 'gzip, br') {
  return new Promise<{ status: number; headers: Record<string, string>; body: Buffer; passed: boolean }>(resolve => {
    const headers: Record<string, string> = {}, parts: Buffer[] = [];
    const res = { statusCode: 200, setHeader: (k: string, v: string) => { headers[k.toLowerCase()] = v; }, write: (c: Buffer) => { parts.push(Buffer.from(c)); return true; },
      end(c?: Buffer) { if (c) parts.push(Buffer.from(c)); resolve({ status: res.statusCode, headers, body: Buffer.concat(parts), passed: false }); }, on() { return res; }, once() { return res; }, emit() { return true; }, removeListener() { return res; } };
    void staticRuntimeMiddleware(dir)({ url, headers: { 'accept-encoding': accept } } as never, res as never, () => resolve({ status: 0, headers, body: Buffer.alloc(0), passed: true }));
  });
}

test('brotli is served when accepted and decodes to the original bytes', async () => {
  const dir = await site();
  try {
    const stats = await precompress(dir); assert.equal(stats.files, 3); assert.ok(stats.encoded < stats.raw);
    const original = await readFile(join(dir, '__atlas/integration.json'));
    const br = await get(dir, '/__atlas/integration.json');
    assert.equal(br.headers['content-encoding'], 'br'); assert.equal(br.headers['content-type'], 'application/json');
    assert.deepEqual(brotliDecompressSync(br.body), original);
    const plain = await get(dir, '/__atlas/integration.json', 'gzip');
    assert.equal(plain.headers['content-encoding'], undefined); assert.deepEqual(plain.body, original);
  } finally { await rm(dir, { recursive: true }); }
});

test('hashed files are cached forever, named data is revalidated', async () => {
  const dir = await site();
  try {
    assert.match((await get(dir, `/__atlas/datasets/za-v2/${sha}.glb`)).headers['cache-control'], /immutable/);
    assert.match((await get(dir, '/assets/app-abc.js')).headers['cache-control'], /immutable/);
    assert.equal((await get(dir, '/__atlas/integration.json')).headers['cache-control'], 'no-cache');
  } finally { await rm(dir, { recursive: true }); }
});

test('missing data is a 404 rather than the app page, and paths cannot leave the build', async () => {
  const dir = await site();
  try {
    assert.equal((await get(dir, '/__atlas/nothing.json')).status, 404);
    assert.equal((await get(dir, '/__atlas/%2e%2e/%2e%2e/etc/passwd')).status, 404);
    assert.equal((await get(dir, '/')).passed, true);
  } finally { await rm(dir, { recursive: true }); }
});
