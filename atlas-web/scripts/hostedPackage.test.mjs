import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { buildHostedPackage, openHostedPreview } from './hostedPackage.mjs';
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
async function fixture() {
  const root = await mkdtemp(join(tmpdir(), 'atlas-hosted-test-'));
  const source = join(root, 'snapshot'), output = join(root, 'hosted');
  const files = [];
  for (const [url, bytes, category] of [['/index.html', Buffer.from('verified app'), 'app'], ['/atlas-data/motion/teaching.glb', Buffer.alloc(10000, 42), 'motion']]) {
    const path = 'public' + url;
    await mkdir(dirname(join(source, path)), { recursive: true }); await writeFile(join(source, path), bytes);
    files.push({ url, path, category, bytes: bytes.length, sha256: sha(bytes), contentType: url.endsWith('.glb') ? 'model/gltf-binary' : 'text/html' });
  }
  await mkdir(join(source, '.internal'), { recursive: true }); await writeFile(join(source, '.internal/private.json'), 'private');
  return { source, output, manifest: { snapshotId: 'fixture', deliveryBasis: 'fixture', files,
    authority: { sourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed' } } };
}
test('public gzip transport preserves decoded bytes, URLs and held authority without copying private inputs', async () => {
  const f = await fixture(), result = await buildHostedPackage(f.source, f.manifest, f.output);
  assert.equal(result.files.length, 2); assert.equal(result.privateInputsUploaded, false); assert.deepEqual(result.authority, f.manifest.authority);
  const row = result.files[1], compressed = await readFile(join(f.output, row.path));
  assert.equal(sha(gunzipSync(compressed)), row.sha256); assert.ok(row.transportBytes < row.bytes);
  await assert.rejects(readFile(join(f.output, 'public/.internal/private.json')), /ENOENT/);
  const headers = await readFile(join(f.output, 'public/_headers'), 'utf8');
  assert.match(headers, /Content-Encoding: gzip/); assert.match(headers, /immutable/);
});
test('changed source bytes, escaped paths and promoted authority fail instead of producing a ready deployment', async () => {
  const f = await fixture();
  await writeFile(join(f.source, f.manifest.files[1].path), 'changed');
  await assert.rejects(buildHostedPackage(f.source, f.manifest, f.output), /changed/);
  const other = await fixture(); other.manifest.files[0].path = 'public/../.internal/private.json';
  await assert.rejects(buildHostedPackage(other.source, other.manifest, other.output), /Invalid/);
  const held = await fixture(); held.manifest.authority.publicRedistribution = 'approved';
  await assert.rejects(buildHostedPackage(held.source, held.manifest, held.output), /authority/);
});
test('a symlink cannot import an external file into the public package', async () => {
  const f = await fixture(); const external = join(f.source, '.internal/private.json');
  await symlink(external, join(f.source, 'public/private.json'));
  f.manifest.files.push({ url: '/private.json', path: 'public/private.json', category: 'projection', bytes: 7, sha256: sha(Buffer.from('private')) });
  await assert.rejects(buildHostedPackage(f.source, f.manifest, f.output), /escaped/);
});
test('HTTP browsers recover original bytes and unknown/private paths remain 404, including after cache tampering', async () => {
  const f = await fixture(), built = await buildHostedPackage(f.source, f.manifest, f.output);
  const { server } = await openHostedPreview(f.output);
  await new Promise((ok, fail) => { server.once('error', fail); server.listen(0, '127.0.0.1', ok); });
  try {
    const origin = 'http://127.0.0.1:' + server.address().port, row = built.files[1];
    const response = await fetch(origin + row.url);
    assert.equal(response.headers.get('content-encoding'), 'gzip'); assert.equal(sha(Buffer.from(await response.arrayBuffer())), row.sha256);
    const tag = response.headers.get('etag');
    assert.equal((await fetch(origin + row.url, { headers: { 'if-none-match': tag } })).status, 304);
    for (const path of ['/.internal/private.json', '/work/EXECUTION.json', '/review', '/hosting-manifest.json', '/_headers'])
      assert.equal((await fetch(origin + path)).status, 404);
    await writeFile(join(f.output, row.path), 'changed');
    assert.equal((await fetch(origin + row.url, { headers: { 'if-none-match': tag } })).status, 503);
  } finally { await new Promise(ok => server.close(ok)); }
});
