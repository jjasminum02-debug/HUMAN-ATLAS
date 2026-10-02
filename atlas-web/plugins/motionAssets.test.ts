import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { motionAssetsPlugin } from './motionAssets.ts';

test('registered lazy binary delivery rejects unknown paths and corrupted package bytes', async () => {
  const root = await mkdtemp(join(tmpdir(), 't59-motion-delivery-'));
  try {
    await mkdir(join(root, 'atlas-data/motion'), { recursive: true });
    await mkdir(join(root, 'atlas-data/assets/motion/test'), { recursive: true });
    const uri = 'atlas-data/assets/motion/test/motion.glb';
    const bytes = Buffer.from('glTF-delivery-fixture-only');
    await writeFile(join(root, uri), bytes);
    await writeFile(join(root, 'atlas-data/motion/motion-learning.json'), JSON.stringify({ motionAssets: [{ uri, sha256: createHash('sha256').update(bytes).digest('hex') }] }));
    let middleware: (req: { url: string }, res: { statusCode: number; setHeader(name: string, value: unknown): void; end(body: unknown): void }, next: () => void) => Promise<void>;
    const plugin = motionAssetsPlugin(root);
    (plugin.configureServer as Function)({ middlewares: { use: (handler: typeof middleware) => { middleware = handler; } } });
    async function request(path: string) {
      const headers: Record<string, unknown> = {};
      const result = { statusCode: 200, body: null as unknown, next: false, headers,
        setHeader(name: string, value: unknown) { headers[name] = value; }, end(body: unknown) { this.body = body; } };
      await middleware({ url: path }, result, () => { result.next = true; });
      return result;
    }
    const valid = await request('/' + uri);
    assert.equal(valid.statusCode, 200);
    assert.equal(valid.headers['Content-Type'], 'model/gltf-binary');
    assert.deepEqual(valid.body, bytes);
    assert.equal((await request('/atlas-data/assets/motion/unknown.glb')).statusCode, 404);
    assert.equal((await request('/ordinary-page')).next, true);
    await writeFile(join(root, uri), 'corrupt');
    assert.equal((await request('/' + uri)).statusCode, 503);
  } finally { await rm(root, { recursive: true, force: true }); }
});
