import { createHash } from 'node:crypto';
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
  async function entries() {
    if (entriesPromise) return entriesPromise;
    entriesPromise = (async () => {
      const [bundleBytes, wave1Bytes] = await Promise.all([
        readFile(learnerRegistryPath, 'utf8'), readFile(wave1RegistryPath, 'utf8'),
      ]);
      const bundle = JSON.parse(bundleBytes);
      const wave1 = JSON.parse(wave1Bytes);
      if (wave1.schemaVersion !== 't66-wave1-source-motion-registration-v2'
        || wave1.authority?.sourceOnly !== true
        || wave1.authority?.publicRedistribution !== 'held'
        || wave1.authority?.humanReview !== 'not_performed'
        || wave1.authority?.canonicalTargetMembershipApproved !== false
        || !Array.isArray(wave1.packages)) throw Error('wave-1 motion registration contract');
      const rows = [
        ...(bundle.motionAssets as Array<{ uri: string; sha256: string }>),
        ...wave1.packages.map((row: { uri: string; sha256: string }) => ({ uri: row.uri, sha256: row.sha256 })),
      ];
      const unique = new Map<string, { uri: string; sha256: string }>();
      for (const row of rows) {
        const existing = unique.get(row.uri);
        if (existing && existing.sha256 !== row.sha256) throw Error(`conflicting motion hashes for ${row.uri}`);
        unique.set(row.uri, row);
      }
      return [...unique.values()];
    })().catch((error) => {
      entriesPromise = null;
      throw error;
    });
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
      server.watcher.add([learnerRegistryPath, wave1RegistryPath]);
      server.watcher.on('change', (file) => {
        if (resolve(file) === learnerRegistryPath || resolve(file) === wave1RegistryPath) entriesPromise = null;
      });
      server.middlewares.use(async (req, res, next) => {
        const path = req.url?.split('?')[0];
        if (!path?.startsWith(prefix)) return next();
        try {
          const entry = (await entries()).find(row => '/' + row.uri === path);
          if (!entry) { res.statusCode = 404; res.end('Unregistered motion package'); return; }
          const bytes = await verified(entry);
          res.setHeader('Content-Type', 'model/gltf-binary'); res.setHeader('Content-Length', bytes.length);
          res.setHeader('Cache-Control', 'no-cache'); res.end(bytes);
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
