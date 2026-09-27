import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';

/** Local engineering only. Intentionally no preview hook or production asset emission. */
export function wholeBodyPlugin(root: string): Plugin {
  const directory = `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t56/`;
  return {
    name: 'local-whole-body-held-assets',
    configureServer(server) {
      server.middlewares.use('/__atlas/body', async (req, res) => {
        res.setHeader('Cache-Control', 'no-store');
        try {
          const raw = await readFile(`${directory}manifest.json`);
          const manifest = JSON.parse(raw.toString()) as { localOnly: boolean; publicRedistribution: string; chunks: { id: string; sha256: string }[] };
          if (!manifest.localOnly || manifest.publicRedistribution !== 'held') throw new Error('license gate');
          const path = req.url?.split('?')[0];
          if (path === '/manifest.json') {
            res.setHeader('Content-Type', 'application/json'); res.end(raw); return;
          }
          const chunk = manifest.chunks.find(c => path === `/${c.id}.glb`);
          if (!chunk || !/^[a-z0-9-]+$/.test(chunk.id)) { res.statusCode = 404; res.end(); return; }
          const data = await readFile(`${directory}${chunk.id}.glb`);
          if (createHash('sha256').update(data).digest('hex') !== chunk.sha256) throw new Error('asset hash');
          res.setHeader('Content-Type', 'model/gltf-binary'); res.end(data);
        } catch {
          res.statusCode = 503; res.end('Local anatomy assets unavailable');
        }
      });
    },
  };
}
