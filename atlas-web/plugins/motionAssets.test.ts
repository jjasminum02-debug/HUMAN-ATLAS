import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { motionAssetsPlugin, motionAssetByteBudget } from './motionAssets.ts';
const sha = (value: Buffer | string) => createHash('sha256').update(value).digest('hex');
test('compact delivery verifies dependencies, cached bytes and invalidation without weakening containment', async () => {
  const root = await mkdtemp(join(tmpdir(), 'atlas-motion-delivery-'));
  try {
    const uri = 'atlas-data/assets/motion/fixture/motion.glb'; const bytes = Buffer.from('fixture-bytes');
    const authority = { sourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', canonicalTargetMembershipApproved: false };
    await mkdir(join(root, 'atlas-data/assets/motion/fixture'), { recursive: true });
    await mkdir(join(root, 'atlas-data/motion'), { recursive: true });
    await writeFile(join(root, uri), bytes);
    const inputs = [ { path: 'atlas-data/motion/motion-learning.json', value: JSON.stringify({ motionAssets: [{ uri, sha256: sha(bytes) }] }) },
      { path: 'atlas-data/motion/t66-wave1-registration.json', value: JSON.stringify({ authority, packages: [] }) } ];
    for (const input of inputs) await writeFile(join(root, input.path), input.value);
    const index = { schemaVersion: 'local-motion-delivery-index-v1', authority,
      dependencies: inputs.map(input => ({ path: input.path, sha256: sha(input.value), bytes: Buffer.byteLength(input.value) })),
      entries: [{ uri, sha256: sha(bytes) }] };
    const indexPath = join(root, 'atlas-data/motion/local-motion-delivery-index.json'); await writeFile(indexPath, JSON.stringify(index));
    const listeners = new Map<string, ((path: string) => void)[]>(); let handler: any;
    const watcher = { add() {}, on(event: string, callback: (path: string) => void) { listeners.set(event, [...listeners.get(event) ?? [], callback]); return this; }, off() {} };
    (motionAssetsPlugin(root).configureServer as Function)({ watcher, middlewares: { use(callback: any) { handler = callback; } } });
    const call = async (url: string, headers = {}) => {
      const result = { statusCode: 200, headers: {} as Record<string, unknown>, body: undefined as Buffer | undefined };
      const response = { get statusCode() { return result.statusCode; }, set statusCode(value) { result.statusCode = value; },
        setHeader(key: string, value: unknown) { result.headers[key] = value; }, removeHeader(key: string) { delete result.headers[key]; },
        end(value: Buffer) { result.body = value; } };
      await handler({ url, headers }, response, () => { result.statusCode = 404; }); return result;
    };
    assert.equal((await call('/' + uri)).statusCode, 200);
    assert.equal((await call('/atlas-data/assets/motion/unknown.glb')).statusCode, 404);
    assert.equal((await call('/atlas-data/assets/motion/../outside.glb')).statusCode, 404);
    assert.equal((await call('/' + uri, { 'if-none-match': `"${sha(bytes)}"` })).statusCode, 304);
    await writeFile(join(root, uri), 'changed-file');
    assert.equal((await call('/' + uri, { 'if-none-match': `"${sha(bytes)}"` })).statusCode, 503, '304 never conceals a changed asset');
    await writeFile(join(root, uri), bytes);
    await writeFile(join(root, inputs[0].path), inputs[0].value + ' ');
    for (const callback of listeners.get('change') ?? []) callback(join(root, inputs[0].path));
    assert.equal((await call('/' + uri)).statusCode, 503, 'stale source hash fails closed');
    await writeFile(join(root, inputs[0].path), inputs[0].value);
    index.authority.publicRedistribution = 'approved'; await writeFile(indexPath, JSON.stringify(index));
    for (const callback of listeners.get('change') ?? []) callback(indexPath);
    assert.equal((await call('/' + uri)).statusCode, 503, 'no rights promotion');
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('larger native trunk delivery is restricted to its exact URI and verified hash', () => {
  const uri = 'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb';
  const sha256 = 'fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf';
  assert.equal(motionAssetByteBudget({ uri, sha256 }), 31_306_820);
  assert.equal(motionAssetByteBudget({ uri, sha256: '0'.repeat(64) }), 8 * 1024 * 1024);
  assert.equal(motionAssetByteBudget({ uri: uri.replace('s04-flex', 'other'), sha256 }), 8 * 1024 * 1024);
});
