import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { performance } from 'node:perf_hooks';
import ts from 'typescript';
import { Mesh } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Build QA only: the learner uses the strict single parser in glb.ts.
const root = resolve(import.meta.dirname, '../..');
const source = await readFile(resolve(root, 'atlas-web/src/viewer/glb.ts'), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext } }).outputText;
const { decodeT07Glb } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);
const cases = [
  { manifest: 'atlas-data/manifests/derived-assets-t07.json', nodes: 'meshNodes' },
  { manifest: 'atlas-data/manifests/derived-bones-t13.json', nodes: 'viewerNodes' },
];
const results = [];

for (const item of cases) {
  const manifest = JSON.parse(await readFile(resolve(root, item.manifest), 'utf8'));
  const buffer = await readFile(resolve(root, manifest.glb.uri));
  const bytes = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
  const expected = manifest[item.nodes];
  const rawTimes = [];
  const gltfTimes = [];
  for (let iteration = 0; iteration < 5; iteration += 1) {
    let start = performance.now();
    const raw = decodeT07Glb(bytes, expected);
    rawTimes.push(performance.now() - start);
    start = performance.now();
    const parsed = await new Promise((yes, no) => new GLTFLoader().parse(bytes, '', yes, no));
    gltfTimes.push(performance.now() - start);
    const loaded = new Map();
    parsed.scene.traverse((object) => { if (object instanceof Mesh) loaded.set(object.name, object); });
    if (loaded.size !== raw.length) throw new Error(`${item.manifest}: mesh count differs`);
    for (const mesh of raw) {
      const other = loaded.get(mesh.meshAssetId);
      if (!other || other.userData.stableMeshAssetId !== mesh.meshAssetId || other.parent !== parsed.scene) throw new Error(`${mesh.meshAssetId}: stable node mismatch`);
      for (const [name, values] of [['position', mesh.positions], ['normal', mesh.normals], ['index', mesh.indices]]) {
        const target = name === 'index' ? other.geometry.index?.array : other.geometry.getAttribute(name)?.array;
        if (!target || target.length !== values.length || values.some((value, index) => value !== target[index])) throw new Error(`${mesh.meshAssetId}: ${name} differs`);
      }
      other.geometry.dispose();
      if (Array.isArray(other.material)) other.material.forEach((material) => material.dispose());
      else other.material.dispose();
    }
  }
  const median = (values) => [...values].sort((a, b) => a - b)[2];
  results.push({ manifest: item.manifest, glbBytes: buffer.byteLength, meshes: expected.length, parserEquivalence: 'pass', rawMs: rawTimes, gltfMs: gltfTimes, rawMedianMs: median(rawTimes), gltfMedianMs: median(gltfTimes) });
}
const output = { task: 'T15e', runtimeNode: process.version, iterations: 5, results, decision: 'single strict GLB decoder at runtime; independent GLTFLoader equivalence in build QA' };
const report = process.argv.indexOf('--report');
if (report >= 0) {
  if (!process.argv[report + 1]) throw new Error('--report requires a path');
  await writeFile(resolve(process.argv[report + 1]), JSON.stringify(output, null, 2) + '\n');
}
console.log(report >= 0 ? JSON.stringify(output, null, 2) : `Scene decoder QA passed: ${results.map((item) => `${item.meshes} meshes/${item.glbBytes} bytes`).join(', ')}`);
