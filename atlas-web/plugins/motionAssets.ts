import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import type { Plugin } from 'vite';

// The native trunk package retains 365 context surfaces and 17 corrected poses.
// Its measured file size is pinned; other assets retain the 8 MiB default.
export function motionAssetByteBudget(entry: { uri: string; sha256: string }): number {
  return entry.uri === 'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb'
    && entry.sha256 === 'fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf'
    ? 31_306_820 : 8 * 1024 * 1024;
}

/** Deliver registered, hashed local motion packages lazily; unknown paths never fall through as HTML. */
export function motionAssetsPlugin(root: string): Plugin {
  const prefix = '/atlas-data/assets/motion/';
  const learnerRegistryPath = resolve(root, 'atlas-data/motion/motion-learning.json');
  const wave1RegistryPath = resolve(root, 'atlas-data/motion/t66-wave1-registration.json');
  let entriesPromise: Promise<Array<{ uri: string; sha256: string }>> | null = null;
  const deliveryPath = resolve(root, 'atlas-data/motion/local-motion-delivery-index.json');
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
      const unique = new Map<string, { uri: string; sha256: string }>();
      for (const row of index.entries as Array<{ uri: string; sha256: string }>) {
        if (typeof row.uri !== 'string' || !row.uri.startsWith(prefix.slice(1)) || row.uri.includes('..')
          || !/^[a-f0-9]{64}$/.test(row.sha256) || unique.has(row.uri)) throw Error('motion delivery entry');
        unique.set(row.uri, row);
      }
      return [...unique.values()];
    })().catch((error) => { entriesPromise = null; throw error; });
    return entriesPromise;
  }
  async function verified(entry: { uri: string; sha256: string }) {
    if (!entry.uri.startsWith(prefix.slice(1)) || entry.uri.includes('..') || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw Error('motion asset path/hash');
    const path = await realpath(resolve(root, entry.uri));
    if (!path.startsWith(await realpath(resolve(root, 'atlas-data/assets/motion')) + sep)) throw Error('motion asset containment');
    const bytes = await readFile(path);
    if (bytes.length > motionAssetByteBudget(entry) || createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw Error('motion asset integrity/budget');
    return bytes;
  }
  return {
    name: 'registered-local-motion-assets',
    configureServer(server) {
      server.watcher.add([learnerRegistryPath, wave1RegistryPath, deliveryPath]);
      const invalidate = (file: string) => {
        if ([learnerRegistryPath, wave1RegistryPath, deliveryPath].includes(resolve(file))) entriesPromise = null;
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
      const unique = new Map<string, { uri: string; sha256: string }>();
      for (const entry of await entries()) {
        const previous = unique.get(entry.uri);
        if (previous && previous.sha256 !== entry.sha256) throw Error('Conflicting motion asset hashes');
        unique.set(entry.uri, entry);
      }
      for (const entry of unique.values()) this.emitFile({ type: 'asset', fileName: entry.uri, source: await verified(entry) });
    },
  };
}
