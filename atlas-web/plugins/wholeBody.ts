import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';
import { applyProductContextOverlay, type ProductContextOverlay } from '../src/viewer/wholeBody/productContext.ts';
import type { BodyManifest } from '../src/viewer/wholeBody/contract.ts';
import { appendT79SceneExtension, type SourceOnlySceneExtension } from '../src/viewer/wholeBody/taskExtension.ts';
import { appendT101SceneExtension, type T101SceneExtension } from '../src/viewer/wholeBody/t101SceneExtension.ts';
import { appendT102SceneExtension, type T102SceneExtension } from '../src/viewer/wholeBody/t102SceneExtension.ts';
import { appendT103SceneExtension, type T103SceneExtension } from '../src/viewer/wholeBody/t103SceneExtension.ts';
import { appendT104SceneExtension, type T104SceneExtension } from '../src/viewer/wholeBody/t104SceneExtension.ts';

/** Local engineering only. Intentionally no preview hook or production asset emission. */
export function wholeBodyPlugin(root: string): Plugin {
  const directory = `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t77/`;
  const overlayPath = `${root}atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json`;
  const extensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json`;
  const sourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json`;
  const t101ExtensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json`;
  const t101SourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json`;
  const t102ExtensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json`;
  const t102SourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json`;
  const t103ExtensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t103/integration-extension.json`;
  const t103SourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t103/source-manifest.json`;
  const t104ExtensionPath = `${root}atlas-data/manifests/bodyparts3d-r4-t104/integration-extension.json`;
  const t104SourceManifestPath = `${root}atlas-data/manifests/bodyparts3d-r4-t104/source-manifest.json`;
  return {
    name: 'local-whole-body-held-assets',
    configureServer(server) {
      server.middlewares.use('/__atlas/body', async (req, res) => {
        res.setHeader('Cache-Control', 'no-store');
        try {
          const [raw, overlayRaw, extensionRaw, sourceRaw, t101ExtensionRaw, t101SourceRaw, t102ExtensionRaw, t102SourceRaw, t103ExtensionRaw, t103SourceRaw,
            t104ExtensionRaw, t104SourceRaw] = await Promise.all([
            readFile(`${directory}manifest.json`),
            readFile(overlayPath),
            readFile(extensionPath),
            readFile(sourceManifestPath),
            readFile(t101ExtensionPath),
            readFile(t101SourceManifestPath),
            readFile(t102ExtensionPath),
            readFile(t102SourceManifestPath),
            readFile(t103ExtensionPath),
            readFile(t103SourceManifestPath),
            readFile(t104ExtensionPath),
            readFile(t104SourceManifestPath),
          ]);
          const sourceManifest = JSON.parse(raw.toString()) as BodyManifest;
          const overlay = JSON.parse(overlayRaw.toString()) as ProductContextOverlay;
          const extension = JSON.parse(extensionRaw.toString()) as SourceOnlySceneExtension;
          const t79Source = JSON.parse(sourceRaw.toString()) as { task: string; revision: string };
          const t101Extension = JSON.parse(t101ExtensionRaw.toString()) as T101SceneExtension;
          const t101Source = JSON.parse(t101SourceRaw.toString()) as { task: string; revision: string };
          const t102Extension = JSON.parse(t102ExtensionRaw.toString()) as T102SceneExtension;
          const t102Source = JSON.parse(t102SourceRaw.toString()) as { task: string; revision: string };
          const t103Extension = JSON.parse(t103ExtensionRaw.toString()) as T103SceneExtension;
          const t103Source = JSON.parse(t103SourceRaw.toString()) as { task: string; revision: string };
          const t104Extension = JSON.parse(t104ExtensionRaw.toString()) as T104SceneExtension;
          const t104Source = JSON.parse(t104SourceRaw.toString()) as { task: string; revision: string };
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
          if (createHash('sha256').update(t102SourceRaw).digest('hex') !== t102Extension.sourceManifestSha256 || t102Source.task !== 'T102') throw new Error('T102 source manifest hash');
          if (t102Extension.parentSourceManifestSha256 !== createHash('sha256').update(raw).digest('hex')
            || t102Extension.parentProductContextOverlaySha256 !== createHash('sha256').update(overlayRaw).digest('hex')
            || t102Extension.parentT79SourceManifestSha256 !== createHash('sha256').update(sourceRaw).digest('hex')
            || t102Extension.parentT79IntegrationExtensionSha256 !== createHash('sha256').update(extensionRaw).digest('hex')
            || t102Extension.parentT101SourceManifestSha256 !== createHash('sha256').update(t101SourceRaw).digest('hex')
            || t102Extension.parentT101IntegrationExtensionSha256 !== createHash('sha256').update(t101ExtensionRaw).digest('hex')) throw new Error('T102 parent chain hash');
          if (createHash('sha256').update(t103SourceRaw).digest('hex') !== t103Extension.sourceManifestSha256 || t103Source.task !== 'T103') throw new Error('T103 source manifest hash');
          if (t103Extension.parentSourceManifestSha256 !== createHash('sha256').update(raw).digest('hex')
            || t103Extension.parentProductContextOverlaySha256 !== createHash('sha256').update(overlayRaw).digest('hex')
            || t103Extension.parentT79SourceManifestSha256 !== createHash('sha256').update(sourceRaw).digest('hex')
            || t103Extension.parentT79IntegrationExtensionSha256 !== createHash('sha256').update(extensionRaw).digest('hex')
            || t103Extension.parentT101SourceManifestSha256 !== createHash('sha256').update(t101SourceRaw).digest('hex')
            || t103Extension.parentT101IntegrationExtensionSha256 !== createHash('sha256').update(t101ExtensionRaw).digest('hex')
            || t103Extension.parentT102SourceManifestSha256 !== createHash('sha256').update(t102SourceRaw).digest('hex')
            || t103Extension.parentT102IntegrationExtensionSha256 !== createHash('sha256').update(t102ExtensionRaw).digest('hex')) throw new Error('T103 parent chain hash');
          if (createHash('sha256').update(t104SourceRaw).digest('hex') !== t104Extension.sourceManifestSha256 || t104Source.task !== 'T104') throw new Error('T104 source manifest hash');
          if (t104Extension.parentSourceManifestSha256 !== createHash('sha256').update(raw).digest('hex')
            || t104Extension.parentProductContextOverlaySha256 !== createHash('sha256').update(overlayRaw).digest('hex')
            || t104Extension.parentT79SourceManifestSha256 !== createHash('sha256').update(sourceRaw).digest('hex')
            || t104Extension.parentT79IntegrationExtensionSha256 !== createHash('sha256').update(extensionRaw).digest('hex')
            || t104Extension.parentT101SourceManifestSha256 !== createHash('sha256').update(t101SourceRaw).digest('hex')
            || t104Extension.parentT101IntegrationExtensionSha256 !== createHash('sha256').update(t101ExtensionRaw).digest('hex')
            || t104Extension.parentT102SourceManifestSha256 !== createHash('sha256').update(t102SourceRaw).digest('hex')
            || t104Extension.parentT102IntegrationExtensionSha256 !== createHash('sha256').update(t102ExtensionRaw).digest('hex')
            || t104Extension.parentT103SourceManifestSha256 !== createHash('sha256').update(t103SourceRaw).digest('hex')
            || t104Extension.parentT103IntegrationExtensionSha256 !== createHash('sha256').update(t103ExtensionRaw).digest('hex')) throw new Error('T104 parent chain hash');
          const t79Manifest = appendT79SceneExtension(applyProductContextOverlay(sourceManifest, overlay), extension);
          const manifest = appendT101SceneExtension(t79Manifest, t101Extension);
          const t102Manifest = appendT102SceneExtension(manifest, t102Extension);
          const completeManifest = appendT103SceneExtension(t102Manifest, t103Extension);
          const t104Manifest = appendT104SceneExtension(completeManifest, t104Extension);
          const path = req.url?.split('?')[0];
          if (path === '/manifest.json') {
            res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(t104Manifest)); return;
          }
          const chunk = t104Manifest.chunks.find(c => path === `/${c.id}.glb`);
          if (!chunk || !/^[a-z0-9-]+$/.test(chunk.id)) { res.statusCode = 404; res.end(); return; }
          const t79Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T79');
          const t101Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T101');
          const t102Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T102');
          const t103Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T103');
          const t104Chunk = chunk.assets.length > 0 && chunk.assets.every(asset => asset.sourcePackage === 'T104');
          const chunkDirectory = t104Chunk
            ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t104/`
            : t103Chunk
            ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t103/`
            : t102Chunk
            ? `${root}atlas-data/source-cache/bodyparts3d-r4/converted/t102/`
            : t101Chunk
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
