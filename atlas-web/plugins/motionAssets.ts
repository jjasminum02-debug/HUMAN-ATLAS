import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import type { Plugin } from 'vite';
import { motionAssetByteBudget, motionRepairByteBudget, motionRepairBytesEligible } from '../src/domain/motionAssetBudget.ts';
export { motionAssetByteBudget } from '../src/domain/motionAssetBudget.ts';

interface DeliveryEntry {
  uri: string;
  sha256: string;
  bytes?: number;
  byteBudget?: number;
  base?: { uri: string; sha256: string };
}

/** Deliver registered, hashed local motion packages lazily; unknown paths never fall through as HTML. */
export function motionAssetsPlugin(root: string): Plugin {
  const prefix = '/atlas-data/assets/motion/';
  const learnerRegistryPath = resolve(root, 'atlas-data/motion/motion-learning.json');
  const wave1RegistryPath = resolve(root, 'atlas-data/motion/t66-wave1-registration.json');
  let entriesPromise: Promise<DeliveryEntry[]> | null = null;
  const deliveryPath = resolve(root, 'atlas-data/motion/local-motion-delivery-index.json');
  const repairsPath = resolve(root, 'atlas-data/motion/source-motion-repairs-r1.json');
  async function entries() {
    if (entriesPromise) return entriesPromise;
    entriesPromise = (async () => {
      // The compiler projects the complete registry into a small exact allowlist.
      // Stream-check both original inputs; avoid parsing the ~98 MB geometry ledger
      // a second time on the user's first playback request.
      const index = JSON.parse(await readFile(deliveryPath, 'utf8'));
      if (index.schemaVersion !== 'local-motion-delivery-index-v1'
        || index.authority?.sourceOnly !== true || index.authority?.publicRedistribution !== 'held'
        || index.authority?.humanReview !== 'not_performed' || index.authority?.canonicalTargetMembershipApproved !== false
        || !Array.isArray(index.entries) || index.dependencies?.length !== 2) throw Error('motion delivery index contract');
      const expectedPaths = ['atlas-data/motion/motion-learning.json', 'atlas-data/motion/t66-wave1-registration.json'];
      for (const relative of expectedPaths) {
        const dependency = index.dependencies.find((row: { path: string }) => row.path === relative);
        if (!dependency || !Number.isSafeInteger(dependency.bytes) || !/^[a-f0-9]{64}$/.test(dependency.sha256)) throw Error('motion delivery dependency');
        const digest = createHash('sha256'); let bytes = 0;
        for await (const chunk of createReadStream(resolve(root, relative))) { digest.update(chunk); bytes += chunk.length; }
        if (bytes !== dependency.bytes || digest.digest('hex') !== dependency.sha256) throw Error('stale motion delivery index');
      }
      const unique = new Map<string, DeliveryEntry>();
      for (const row of index.entries as Array<{ uri: string; sha256: string }>) {
        if (typeof row.uri !== 'string' || !row.uri.startsWith(prefix.slice(1)) || row.uri.includes('..')
          || !/^[a-f0-9]{64}$/.test(row.sha256) || unique.has(row.uri)) throw Error('motion delivery entry');
        unique.set(row.uri, { uri: row.uri, sha256: row.sha256 });
      }
      const registeredBases = new Map(unique);
      // Versioned repairs retain the original registry/WIP and require its exact
      // base hash. The browser also pins the complete source binding contract.
      const repairs = JSON.parse(await readFile(repairsPath, 'utf8'));
      if (repairs.schemaVersion !== 'source-motion-repairs-v1' || repairs.sourceOnly !== true
        || repairs.publicRedistribution !== 'held' || repairs.humanReview !== 'not_performed'
        || !Array.isArray(repairs.rows)) throw Error('motion repair contract');
      for (const row of repairs.rows) {
        if (registeredBases.get(row.baseUri)?.sha256 !== row.baseSha256
          || typeof row.assetId !== 'string' || typeof row.bindingSignature !== 'string'
          || typeof row.uri !== 'string' || !row.uri.startsWith(prefix.slice(1)) || row.uri.includes('..')
          || !/^[a-f0-9]{64}$/.test(row.sha256) || unique.has(row.uri)
          || !motionRepairBytesEligible(row)) throw Error('motion repair base/path/hash/budget');
        unique.set(row.uri, { uri: row.uri, sha256: row.sha256, bytes: row.bytes,
          byteBudget: motionRepairByteBudget(row), base: { uri: row.baseUri, sha256: row.baseSha256 } });
      }
      return [...unique.values()];
    })().catch((error) => { entriesPromise = null; throw error; });
    return entriesPromise;
  }
  async function verified(entry: DeliveryEntry): Promise<Buffer> {
    if (!entry.uri.startsWith(prefix.slice(1)) || entry.uri.includes('..') || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw Error('motion asset path/hash');
    const path = await realpath(resolve(root, entry.uri));
    if (!path.startsWith(await realpath(resolve(root, 'atlas-data/assets/motion')) + sep)) throw Error('motion asset containment');
    // Recheck the actual registered original before authorizing its replacement.
    // Only original index entries may be bases; repair chains are rejected above.
    if (entry.base) await verified(entry.base);
    const bytes = await readFile(path);
    if (bytes.length > (entry.byteBudget ?? motionAssetByteBudget(entry))
      || (entry.bytes !== undefined && bytes.length !== entry.bytes)
      || createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw Error('motion asset integrity/budget');
    return bytes;
  }
  return {
    name: 'registered-local-motion-assets',
    configureServer(server) {
      server.watcher.add([learnerRegistryPath, wave1RegistryPath, deliveryPath, repairsPath]);
      const invalidate = (file: string) => {
        if ([learnerRegistryPath, wave1RegistryPath, deliveryPath, repairsPath].includes(resolve(file))) entriesPromise = null;
      };
      server.watcher.on('change', invalidate).on('unlink', invalidate).on('add', invalidate);
      server.httpServer?.once('close', () => {
        server.watcher.off('change', invalidate).off('unlink', invalidate).off('add', invalidate);
        entriesPromise = null;
      });
      server.middlewares.use(async (req, res, next) => {
        const path = req.url?.split('?')[0];
        if (!path?.startsWith(prefix)) return next();
        try {
          const entry = (await entries()).find(row => '/' + row.uri === path);
          if (!entry) { res.statusCode = 404; res.end('Unregistered motion package'); return; }
          const bytes = await verified(entry);
          res.setHeader('Content-Type', 'model/gltf-binary'); res.setHeader('Content-Length', bytes.length);
          res.setHeader('Cache-Control', 'private, no-cache');
          const etag = `"${entry.sha256}"`; res.setHeader('ETag', etag);
          // Verify the current bytes before acknowledging a cached response.
          if (req.headers['if-none-match'] === etag) { res.statusCode = 304; res.removeHeader('Content-Length'); res.end(); return; }
          res.end(bytes);
        } catch { res.statusCode = 503; res.end('Motion package integrity verification failed'); }
      });
    },
    async generateBundle() {
      const unique = new Map<string, DeliveryEntry>();
      for (const entry of await entries()) {
        const previous = unique.get(entry.uri);
        if (previous && previous.sha256 !== entry.sha256) throw Error('Conflicting motion asset hashes');
        unique.set(entry.uri, entry);
      }
      for (const entry of unique.values()) this.emitFile({ type: 'asset', fileName: entry.uri, source: await verified(entry) });
    },
  };
}
