import { createHash } from 'node:crypto';
import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import type { Plugin } from 'vite';

/** Deliver registered, hashed local motion packages lazily; unknown paths never fall through as HTML. */
export function motionAssetsPlugin(root: string): Plugin {
  const prefix = '/atlas-data/assets/motion/';
  async function entries() {
    const bundle = JSON.parse(await readFile(resolve(root, 'atlas-data/motion/motion-learning.json'), 'utf8'));
    return bundle.motionAssets as Array<{ uri: string; sha256: string }>;
  }
  async function verified(entry: { uri: string; sha256: string }) {
    if (!entry.uri.startsWith(prefix.slice(1)) || entry.uri.includes('..') || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw Error('motion asset path/hash');
    const path = await realpath(resolve(root, entry.uri));
    if (!path.startsWith(await realpath(resolve(root, 'atlas-data/assets/motion')) + sep)) throw Error('motion asset containment');
    const bytes = await readFile(path);
    if (bytes.length > 8 * 1024 * 1024 || createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw Error('motion asset integrity/budget');
    return bytes;
  }
  return {
    name: 'registered-local-motion-assets',
    configureServer(server) {
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
      for (const entry of await entries()) this.emitFile({ type: 'asset', fileName: entry.uri, source: await verified(entry) });
    },
  };
}
