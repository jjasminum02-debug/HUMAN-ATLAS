import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';
import { applyProductContextOverlay, type ProductContextOverlay } from '../src/viewer/wholeBody/productContext.ts';
import type { BodyManifest } from '../src/viewer/wholeBody/contract.ts';
import { appendT79SceneExtension, type SourceOnlySceneExtension } from '../src/viewer/wholeBody/taskExtension.ts';
import { appendT101SceneExtension, type T101SceneExtension } from '../src/viewer/wholeBody/t101SceneExtension.ts';

/** Local engineering only. Intentionally no preview hook or production asset emission. */
export function wholeBodyPlugin(root: string): Plugin {
  const directory = `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t77/`;
  const overlayPath = `${root}atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json`;
  const extensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json`;
  const sourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json`;
  const t101ExtensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json`;
  const t101SourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json`;
  return {
    name: 'local-whole-body-held-assets',
    configureServer(server) {
      server.middlewares.use('/__atlas/body', async (req, res) => {
        res.setHeader('Cache-Control', 'no-store');
        try {
          const [raw, overlayRaw, extensionRaw, sourceRaw, t101ExtensionRaw, t101SourceRaw] = await Promise.all([
            readFile(`${directory}manifest.json`),
            readFile(overlayPath),
            readFile(extensionPath),
            readFile(sourceManifestPath),
            readFile(t101ExtensionPath),
            readFile(t101SourceManifestPath),
          ]);
          const sourceManifest = JSON.parse(raw.toString()) as BodyManifest;
          const overlay = JSON.parse(overlayRaw.toString()) as ProductContextOverlay;
          const extension = JSON.parse(extensionRaw.toString()) as SourceOnlySceneExtension;
          const t79Source = JSON.parse(sourceRaw.toString()) as { task: string; revision: string };
          const t101Extension = JSON.parse(t101ExtensionRaw.toString()) as T101SceneExtension;
          const t101Source = JSON.parse(t101SourceRaw.toString()) as { task: string; revision: string };
          if (createHash('sha256').update(raw).digest('hex') !== overlay.sourceManifestSha256) throw new Error('source manifest hash');
          if (!sourceManifest.localOnly || sourceManifest.publicRedistribution !== 'held') throw new Error('license gate');
          if (createHash('sha256').update(raw).digest('hex') !== extension.parentSourceManifestSha256) throw new Error('T79 parent manifest hash');
          if (createHash('sha256').update(overlayRaw).digest('hex') !== extension.parentProductContextOverlaySha256) throw new Error('T79 parent overlay hash');
          if (createHash('sha256').update(sourceRaw).digest('hex') !== extension.sourceManifestSha256 || t79Source.task !== 'T79') throw new Error('T79 source manifest hash');
          if (createHash('sha256').update(t101SourceRaw).digest('hex') !== t101Extension.sourceManifestSha256 || t101Source.task !== 'T101') throw new Error('T101 source manifest hash');
          if (t101Extension.parentSourceManifestSha256 !== createHash('sha256').update(raw).digest('hex')
            || t101Extension.parentProductContextOverlaySha256 !== createHash('sha256').update(overlayRaw).digest('hex')
            || t101Extension.parentT79SourceManifestSha256 !== createHash('sha256').update(sourceRaw).digest('hex')
            || t101Extension.parentT79IntegrationExtensionSha256 !== createHash('sha256').update(extensionRaw).digest('hex')) throw new Error('T101 parent chain hash');
          const t79Manifest = appendT79SceneExtension(applyProductContextOverlay(sourceManifest, overlay), extension);
          const manifest = appendT101SceneExtension(t79Manifest, t101Extension);
          const path = req.url?.split('?')[0];
          if (path === '/manifest.json') {
            res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(manifest)); return;
          }
          const chunk = manifest.chunks.find(c => path === `/${c.id}.glb`);
          if (!chunk || !/^[a-z0-9-]+$/.test(chunk.id)) { res.statusCode = 404; res.end(); return; }
          const t79Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T79');
          const t101Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T101');
          const chunkDirectory = t101Chunk
            ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t101/`
            : t79Chunk ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t79/` : directory;
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
