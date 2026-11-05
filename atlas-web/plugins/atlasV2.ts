// Serves the v2 runtime data (ROADMAP D2). Registered before the legacy whole-body plugin, so the app's
// two runtime URLs and all anatomy chunks come from atlas-data/runtime + source-cache/datasets/za-v2 only.
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { Plugin } from 'vite';
import { projectLegacyRuntime, type V2GeometryFile } from '../src/data/atlasV2.ts';

const PROJECTED = new Set(['/__atlas/integration.json', '/__atlas/datasets/human-atlas-local/manifest.json']);
const RAW: Record<string, string> = { '/__atlas/v2/structures.json': 'structures.json', '/__atlas/v2/relations.json': 'relations.json',
  '/__atlas/v2/cards.json': 'structure-cards.json', '/__atlas/v2/rig.json': 'rig.json',
  '/__atlas/v2/actions.json': 'muscle-actions.json', '/__atlas/v2/attachments.json': 'attachments.json',
  '/__atlas/v2/muscle-cards.json': 'muscle-cards.json' };
const CHUNK = /^\/__atlas\/datasets\/(za-c7010a9|za-v2)\/([a-f0-9]{64})\.glb$/;
const SKIN = /^\/__atlas\/v2\/skin\/([a-f0-9]{64})\.bin$/;
const CONTACTS = /^\/__atlas\/v2\/attachments\/(ZA-[A-Za-z0-9-]+)\.json$/;

export function atlasV2Plugin(root: string): Plugin {
  const runtime = resolve(root, 'atlas-data/runtime');
  const geometryDir = resolve(root, 'atlas-data/source-cache/datasets/za-v2');
  type Built = { manifest: Buffer; integration: Buffer; chunks: Map<string, string> };
  let built: Promise<Built> | undefined;
  const build = () => built ??= (async () => {
    const [structures, relations, geometry] = await Promise.all([
      readFile(resolve(runtime, 'structures.json'), 'utf8'), readFile(resolve(runtime, 'relations.json'), 'utf8'),
      readFile(resolve(geometryDir, 'geometry.json'), 'utf8')]).then(texts => texts.map(text => JSON.parse(text)));
    const { dataset, integration } = projectLegacyRuntime(structures, relations, geometry);
    const chunks = new Map((geometry as V2GeometryFile).chunks.map(c => [`${c.namespace}/${c.id}`, c.sha256]));
    return { manifest: Buffer.from(JSON.stringify(dataset)), integration: Buffer.from(JSON.stringify(integration)), chunks };
  })().catch(error => { built = undefined; throw error; });
  return {
    name: 'atlas-v2-runtime',
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
