import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';
import { applyProductContextOverlay, type ProductContextOverlay } from '../src/viewer/wholeBody/productContext.ts';
import type { BodyManifest } from '../src/viewer/wholeBody/contract.ts';
import { appendT79SceneExtension, type SourceOnlySceneExtension } from '../src/viewer/wholeBody/taskExtension.ts';

/** Local engineering only. Intentionally no preview hook or production asset emission. */
export function wholeBodyPlugin(root: string): Plugin {
  const directory = `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t77/`;
  const overlayPath = `${root}atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json`;
  const extensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json`;
  const sourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json`;
  return {
    name: 'local-whole-body-held-assets',
    configureServer(server) {
      server.middlewares.use('/__atlas/body', async (req, res) => {
        res.setHeader('Cache-Control', 'no-store');
        try {
          const [raw, overlayRaw, extensionRaw, sourceRaw] = await Promise.all([
            readFile(`${directory}manifest.json`),
            readFile(overlayPath),
            readFile(extensionPath),
            readFile(sourceManifestPath),
          ]);
          const sourceManifest = JSON.parse(raw.toString()) as BodyManifest;
          const overlay = JSON.parse(overlayRaw.toString()) as ProductContextOverlay;
          const extension = JSON.parse(extensionRaw.toString()) as SourceOnlySceneExtension;
          const t79Source = JSON.parse(sourceRaw.toString()) as { task: string; revision: string };
          if (createHash('sha256').update(raw).digest('hex') !== overlay.sourceManifestSha256) throw new Error('source manifest hash');
          if (!sourceManifest.localOnly || sourceManifest.publicRedistribution !== 'held') throw new Error('license gate');
          if (createHash('sha256').update(raw).digest('hex') !== extension.parentSourceManifestSha256) throw new Error('T79 parent manifest hash');
          if (createHash('sha256').update(overlayRaw).digest('hex') !== extension.parentProductContextOverlaySha256) throw new Error('T79 parent overlay hash');
          if (createHash('sha256').update(sourceRaw).digest('hex') !== extension.sourceManifestSha256 || t79Source.task !== 'T79') throw new Error('T79 source manifest hash');
          const manifest = appendT79SceneExtension(applyProductContextOverlay(sourceManifest, overlay), extension);
          const path = req.url?.split('?')[0];
          if (path === '/manifest.json') {
            res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(manifest)); return;
          }
          const chunk = manifest.chunks.find(c => path === `/${c.id}.glb`);
          if (!chunk || !/^[a-z0-9-]+$/.test(chunk.id)) { res.statusCode = 404; res.end(); return; }
          const t79Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T79');
          const chunkDirectory = t79Chunk
            ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t79/`
            : directory;
          const data = await readFile(`${chunkDirectory}${chunk.id}.glb`);
          if (createHash('sha256').update(data).digest('hex') !== chunk.sha256) throw new Error('asset hash');
          res.setHeader('Content-Type', 'model/gltf-binary'); res.end(data);
        } catch {
          res.statusCode = 503; res.end('Local anatomy assets unavailable');
        }
      });
    },
  };
}
