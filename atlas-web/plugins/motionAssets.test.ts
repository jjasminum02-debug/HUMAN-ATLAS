import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { motionAssetsPlugin, motionAssetByteBudget } from './motionAssets.ts';
import { NATIVE_TRUNK_BASE } from '../src/domain/motionAssetBudget.ts';
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
    const repairsPath = join(root, 'atlas-data/motion/source-motion-repairs-r1.json');
    const repairs = { schemaVersion: 'source-motion-repairs-v1', sourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', rows: [] as any[] };
    await writeFile(repairsPath, JSON.stringify(repairs));
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
    const repairUri = 'atlas-data/assets/motion/repaired/motion.glb';
    await mkdir(join(root, 'atlas-data/assets/motion/repaired'), { recursive: true });
    await writeFile(join(root, repairUri), bytes);
    repairs.rows.push({ assetId: 'repaired-asset', bindingSignature: 'pinned-binding', baseUri: uri,
      baseSha256: sha(bytes), uri: repairUri, sha256: sha(bytes), bytes: bytes.length });
    await writeFile(repairsPath, JSON.stringify(repairs));
    for (const callback of listeners.get('change') ?? []) callback(repairsPath);
    assert.equal((await call('/' + repairUri)).statusCode, 200, 'verified repair is delivered');
    repairs.rows[0].bytes += 1;
    await writeFile(repairsPath, JSON.stringify(repairs));
    for (const callback of listeners.get('change') ?? []) callback(repairsPath);
    assert.equal((await call('/' + repairUri, { 'if-none-match': `"${sha(bytes)}"` })).statusCode, 503,
      'actual repair length must match the declared length before 304');
    repairs.rows[0].bytes = bytes.length;
    repairs.rows[0].baseSha256 = '0'.repeat(64);
    await writeFile(repairsPath, JSON.stringify(repairs));
    for (const callback of listeners.get('change') ?? []) callback(repairsPath);
    assert.equal((await call('/' + repairUri)).statusCode, 503, 'drifted base cannot authorize a repair');
    repairs.rows = []; await writeFile(repairsPath, JSON.stringify(repairs));
    for (const callback of listeners.get('change') ?? []) callback(repairsPath);
    await writeFile(join(root, uri), 'changed-file');
    assert.equal((await call('/' + uri, { 'if-none-match': `"${sha(bytes)}"` })).statusCode, 503, '304 never conceals a changed asset');
    await writeFile(join(root, uri), bytes);
    await writeFile(join(root, inputs[0].path), inputs[0].value + ' ');
    for (const callback of listeners.get('change') ?? []) callback(join(root, inputs[0].path));
    assert.equal((await call('/' + uri)).statusCode, 503, 'stale source hash fails closed');
    await writeFile(join(root, inputs[0].path), inputs[0].value);
    const oversized = Buffer.alloc(8 * 1024 * 1024 + 1);
    await writeFile(join(root, uri), oversized);
    index.entries[0] = { uri, sha256: sha(oversized), byteBudget: NATIVE_TRUNK_BASE.bytes } as any;
    await writeFile(indexPath, JSON.stringify(index));
    for (const callback of listeners.get('change') ?? []) callback(indexPath);
    assert.equal((await call('/' + uri)).statusCode, 503, 'index metadata cannot expand an unrelated asset budget');
    index.entries[0] = { uri, sha256: sha(bytes) }; await writeFile(join(root, uri), bytes);
    index.authority.publicRedistribution = 'approved'; await writeFile(indexPath, JSON.stringify(index));
    for (const callback of listeners.get('change') ?? []) callback(indexPath);
    assert.equal((await call('/' + uri)).statusCode, 503, 'no rights promotion');
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('actual 365-surface trunk bytes pass as a direct replacement within the unchanged source budget', async () => {
  const root = await mkdtemp(join(tmpdir(), 'atlas-trunk-budget-'));
  try {
    const bytes = await readFile(new URL('../../' + NATIVE_TRUNK_BASE.uri, import.meta.url));
    assert.equal(bytes.length, NATIVE_TRUNK_BASE.bytes); assert.equal(sha(bytes), NATIVE_TRUNK_BASE.sha256);
    const repairUri = 'atlas-data/assets/motion/test-only-repair/motion.glb';
    for (const uri of [NATIVE_TRUNK_BASE.uri, repairUri]) {
      await mkdir(join(root, uri, '..'), { recursive: true }); await writeFile(join(root, uri), bytes);
    }
    await mkdir(join(root, 'atlas-data/motion'), { recursive: true });
    const authority = { sourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', canonicalTargetMembershipApproved: false };
    const paths = ['atlas-data/motion/motion-learning.json', 'atlas-data/motion/t66-wave1-registration.json'];
    for (const p of paths) await writeFile(join(root, p), '{}');
    const index = { schemaVersion: 'local-motion-delivery-index-v1', authority,
      dependencies: paths.map(path => ({ path, bytes: 2, sha256: sha('{}') })), entries: [NATIVE_TRUNK_BASE] };
    await writeFile(join(root, 'atlas-data/motion/local-motion-delivery-index.json'), JSON.stringify(index));
    const repairPath = join(root, 'atlas-data/motion/source-motion-repairs-r1.json');
    const row = { assetId: 'test-only', bindingSignature: 'test-only', baseUri: NATIVE_TRUNK_BASE.uri,
      baseSha256: NATIVE_TRUNK_BASE.sha256, uri: repairUri, sha256: sha(bytes), bytes: bytes.length };
    const repairs = { schemaVersion: 'source-motion-repairs-v1', sourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', rows: [row] };
    await writeFile(repairPath, JSON.stringify(repairs));
    let handler: any; const listeners: Array<(p: string) => void> = [];
    const watcher = { add() {}, on(e: string, f: (p: string) => void) { if (e === 'change') listeners.push(f); return this; }, off() {} };
    const plugin = motionAssetsPlugin(root);
    (plugin.configureServer as Function)({ watcher, middlewares: { use(f: any) { handler = f; } } });
    const request = async (cached = false) => {
      const res = { statusCode: 200, body: undefined as Buffer | undefined, setHeader() {}, removeHeader() {}, end(v: Buffer) { this.body = v; } };
      await handler({ url: '/' + repairUri, headers: cached ? { 'if-none-match': `"${row.sha256}"` } : {} }, res, () => {}); return res;
    };
    assert.equal((await request()).body?.length, NATIVE_TRUNK_BASE.bytes);
    assert.equal((await request(true)).statusCode, 304);
    const emitted: Array<{fileName: string; source: Buffer}> = [];
    await (plugin.generateBundle as Function).call({ emitFile(a: any) { emitted.push(a); } });
    assert.equal(emitted.find(a => a.fileName === repairUri)?.source.length, NATIVE_TRUNK_BASE.bytes);
    await writeFile(join(root, NATIVE_TRUNK_BASE.uri), 'tampered-original');
    assert.equal((await request(true)).statusCode, 503, 'original identity is checked on actual bytes before cached repair');
    await writeFile(join(root, NATIVE_TRUNK_BASE.uri), bytes);
    row.bytes += 1; await writeFile(repairPath, JSON.stringify(repairs)); listeners.forEach(f => f(repairPath));
    assert.equal((await request()).statusCode, 503, 'source ceiling cannot expand');
    row.bytes = bytes.length; row.baseUri = repairUri; await writeFile(repairPath, JSON.stringify(repairs)); listeners.forEach(f => f(repairPath));
    assert.equal((await request()).statusCode, 503, 'a repair cannot become another repair base');
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('larger native trunk delivery is restricted to its exact URI and verified hash', () => {
  const uri = 'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb';
  const sha256 = 'fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf';
  assert.equal(motionAssetByteBudget({ uri, sha256 }), 31_306_820);
  assert.equal(motionAssetByteBudget({ uri, sha256: '0'.repeat(64) }), 8 * 1024 * 1024);
  assert.equal(motionAssetByteBudget({ uri: uri.replace('s04-flex', 'other'), sha256 }), 8 * 1024 * 1024);
});
