import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { createHash } from 'node:crypto';
import { validateNerveRegistry } from '../src/domain/nerveContract.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';
import type { NerveLocalRights, NerveSceneManifest } from '../src/viewer/datasets/nerveScene.ts';
const sha = (b: Buffer) => createHash('sha256').update(b).digest('hex');
/** No ambient filesystem access from asset URLs: delivery uses this fixed, hash-checked manifest. */
export async function loadNerveAssets(root: string) {
  const bytes = await readFile(resolve(root, 'atlas-data/manifests/nerve-scene-t63.json'));
  const manifest = JSON.parse(bytes.toString()) as NerveSceneManifest;
  const inputs = new Map<string, Buffer>();
  for (const [relative, hash] of Object.entries(manifest.inputSha256)) {
    if (!/^(atlas-data|work)\//.test(relative) || relative.split('/').includes('..')) throw Error('nerve input containment');
    const path = await realpath(resolve(root, relative));
    if (!path.startsWith(resolve(root) + sep)) throw Error('nerve input symlink containment');
    const input = await readFile(path);
    if (sha(input) !== hash) throw Error('nerve stale input: ' + relative);
    inputs.set(relative, input);
  }
  const json = (path: string) => {
    const b = inputs.get(path); if (!b) throw Error('nerve unpinned manifest reference');
    return JSON.parse(b.toString());
  };
  const registry = validateNerveRegistry(json(manifest.registryPath));
  const dataset = validateDataset(json(manifest.datasetPath));
  const rights = json(manifest.rightsPath) as NerveLocalRights;
  for (const n of registry.instances) if (n.geometry) {
    if (sha(inputs.get(n.geometry.assetPath) ?? Buffer.alloc(0)) !== n.geometry.assetSha256) throw Error('nerve asset hash');
    for (const id of n.geometry.evidenceIds) {
      const e = registry.evidence.find(e => e.id === id)!;
      if (!inputs.has(e.sourcePath) || sha(inputs.get(e.sourcePath)!) !== e.sourceSha256) throw Error('nerve geometry proof hash');
    }
  }
  for (const e of registry.evidence) {
    if (!inputs.has(e.sourcePath) || sha(inputs.get(e.sourcePath)!) !== e.sourceSha256) throw Error('nerve evidence hash: ' + e.id);
  }
  const files = dataset.chunks.map(c => {
    const path = 'atlas-data/assets/derived-glb/za-nerve-t63/chunks/' + c.id + '.glb';
    const b = inputs.get(path);
    if (!b || sha(b) !== c.sha256 || b.length !== c.bytes) throw Error('nerve chunk hash/bytes');
    return { id: c.id, path: resolve(root, path), sha256: c.sha256, bytes: c.bytes };
  });
  return { manifest, registry, dataset, rights, files, sha256: sha(bytes), rightsSha256: sha(inputs.get(manifest.rightsPath)!) };
}
