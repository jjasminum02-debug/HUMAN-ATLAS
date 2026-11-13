// Serves the v2 runtime data (ROADMAP D2). Registered before the legacy whole-body plugin, so the app's
// two runtime URLs and all anatomy chunks come from atlas-data/runtime + source-cache/datasets/za-v2 only.
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { Plugin } from 'vite';
import { precompress, projectRuntime, staticRuntimeMiddleware, writeStaticRuntime } from './atlasV2Static.ts';

const PROJECTED = new Set(['/__atlas/integration.json', '/__atlas/datasets/human-atlas-local/manifest.json']);
const RAW: Record<string, string> = { '/__atlas/v2/structures.json': 'structures.json', '/__atlas/v2/relations.json': 'relations.json',
  '/__atlas/v2/cards.json': 'structure-cards.json', '/__atlas/v2/rig.json': 'rig.json',
  '/__atlas/v2/actions.json': 'muscle-actions.json', '/__atlas/v2/attachments.json': 'attachments.json',
  '/__atlas/v2/muscle-cards.json': 'muscle-cards.json', '/__atlas/v2/vessel-branches.json': 'vessel-branches.json', '/__atlas/v2/acupoints.json': 'acupoints.json',
  '/__atlas/v2/sinews.json': 'sinews.json' };
const CHUNK = /^\/__atlas\/datasets\/(za-c7010a9|za-v2)\/([a-f0-9]{64})\.glb$/;
const SKIN = /^\/__atlas\/v2\/skin\/([a-f0-9]{64})\.bin$/;
const CONTACTS = /^\/__atlas\/v2\/attachments\/(ZA-[A-Za-z0-9-]+)\.json$/;

export function atlasV2Plugin(root: string): Plugin {
  const runtime = resolve(root, 'atlas-data/runtime');
  const geometryDir = resolve(root, 'atlas-data/source-cache/datasets/za-v2');
  type Built = { manifest: Buffer; integration: Buffer; chunks: Map<string, string> };
  let built: Promise<Built> | undefined;
  let outDir = resolve(root, 'atlas-web/dist');
  const build = () => built ??= (async () => {
    const { geometry, manifest, integration } = await projectRuntime(root);
    const chunks = new Map(geometry.chunks.map(c => [`${c.namespace}/${c.id}`, c.sha256]));
    return { manifest, integration, chunks };
  })().catch(error => { built = undefined; throw error; });
  return {
    name: 'atlas-v2-runtime',
    configResolved(config) { outDir = resolve(config.root, config.build.outDir); },
    async writeBundle() {
      await writeStaticRuntime(root, outDir);
      const { files, raw, encoded } = await precompress(outDir);
      console.log(`atlas v2 runtime: ${files} files, ${(raw / 1e6).toFixed(0)} MB, ${(encoded / 1e6).toFixed(0)} MB with brotli`);
    },
    configurePreviewServer(server) { server.middlewares.use(staticRuntimeMiddleware(outDir)); },
    configureServer(server) {
      server.watcher.add([runtime, resolve(geometryDir, 'geometry.json')]);
      const invalidate = (path: string) => { if (path.startsWith(runtime) || path.startsWith(geometryDir)) built = undefined; };
      server.watcher.on('change', invalidate).on('add', invalidate).on('unlink', invalidate);
      server.middlewares.use(async (req, res, next) => {
        const path = req.url?.split('?')[0] ?? '';
        const chunk = CHUNK.exec(path), skin = SKIN.exec(path), contacts = CONTACTS.exec(path);
        if (!PROJECTED.has(path) && !RAW[path] && !chunk && !skin && !contacts) { next(); return; }
        try {
          res.setHeader('Cache-Control', 'no-store');
          if (skin) {
            res.setHeader('Content-Type', 'application/octet-stream');
            res.end(await readFile(resolve(geometryDir, 'skin', `${skin[1]}.bin`))); return;
          }
          if (contacts) {
            res.setHeader('Content-Type', 'application/json');
            res.end(await readFile(resolve(geometryDir, 'attachments', `${contacts[1]}.json`))); return;
          }
          if (RAW[path]) {
            res.setHeader('Content-Type', 'application/json'); res.end(await readFile(resolve(runtime, RAW[path]))); return;
          }
          const data = await build();
          if (PROJECTED.has(path)) {
            res.setHeader('Content-Type', 'application/json');
            res.end(path === '/__atlas/integration.json' ? data.integration : data.manifest); return;
          }
          const sha = data.chunks.get(`${chunk![1]}/${chunk![2]}`);
          if (!sha) { res.statusCode = 404; res.end(); return; }
          const etag = `"${sha}"`;
          res.setHeader('Cache-Control', 'private, no-cache'); res.setHeader('ETag', etag);
          if (req.headers['if-none-match'] === etag) { res.statusCode = 304; res.end(); return; }
          const bytes = await readFile(resolve(geometryDir, 'chunks', `${sha}.glb`));
          res.setHeader('Content-Type', 'model/gltf-binary'); res.setHeader('Content-Length', String(bytes.length)); res.end(bytes);
        } catch (error) {
          console.error('atlas v2 runtime unavailable', error);
          res.statusCode = 503; res.end('Atlas v2 runtime unavailable; run atlas-data/pipeline/build_runtime_v2.py');
        }
      });
    },
  };
}
