// T12a only: compare the existing T07 decoder with Three.js GLTFLoader.
// Install the pinned package outside the app, then set T12_THREE_ROOT to its
// node_modules/three directory. No production renderer is changed here.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '../../..');
const threeRoot = process.env.T12_THREE_ROOT;
if (!threeRoot) throw new Error('Set T12_THREE_ROOT to a pinned Three.js package directory.');
if (!process.env.T12_GLB_JS) throw new Error('Set T12_GLB_JS to a temporary tsc output for atlas-web/src/viewer/glb.ts.');
const { decodeT07Glb } = await import(pathToFileURL(resolve(process.env.T12_GLB_JS)).href);
const three = await import(pathToFileURL(resolve(threeRoot, 'build/three.core.js')).href);
const { GLTFLoader } = await import(pathToFileURL(resolve(threeRoot, 'examples/jsm/loaders/GLTFLoader.js')).href);
const { OrbitControls } = await import(pathToFileURL(resolve(threeRoot, 'examples/jsm/controls/OrbitControls.js')).href);
const manifest = JSON.parse(readFileSync(resolve(root, 'atlas-data/manifests/derived-assets-t07.json'), 'utf8'));
const bytes = readFileSync(resolve(root, manifest.glb.uri));
const hash = createHash('sha256').update(bytes).digest('hex');
assert.equal(hash, manifest.glb.sha256);
assert.equal(bytes.byteLength, manifest.glb.bytes);
assert.equal(manifest.glb.meshCount, 11);
assert.equal(manifest.transform.sourceUnits, 'mm');
assert.equal(manifest.transform.targetUnits, 'm');
assert.equal(manifest.transform.scaleToMeters, 0.001);
assert.equal(manifest.transform.rotationDeterminant, 1);
assert.equal(manifest.transform.reflectionApplied, false);
assert.equal(manifest.transform.triangleWindingReversed, false);
assert.deepEqual(manifest.transform.rotationMatrix, [[1, 0, 0], [0, 0, 1], [0, -1, 0]]);
const expected = manifest.meshNodes.map(node => ({
  meshAssetId: node.meshAssetId,
  nodeIndex: node.nodeIndex,
  meshIndex: node.meshIndex,
  sourceName: node.sourceName,
  sourceFileId: node.sourceFileId,
  targetEntityId: node.targetEntityId,
  targetEntityType: node.targetEntityType,
  relationStatus: node.relationStatus,
  reviewState: 'needs_review',
}));
const raw = decodeT07Glb(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), expected);
const loader = new GLTFLoader();
const gltf = await new Promise((resolveLoaded, reject) => loader.parse(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '', resolveLoaded, reject));
const loaded = [];
gltf.scene.traverse(object => { if (object.isMesh) loaded.push(object); });
assert.equal(loaded.length, 11);
assert.deepEqual(new Set(loaded.map(mesh => mesh.name)), new Set(raw.map(mesh => mesh.meshAssetId)));

const rows = [];
for (const oldMesh of raw) {
  const mesh = loaded.find(candidate => candidate.name === oldMesh.meshAssetId);
  assert.ok(mesh, `${oldMesh.meshAssetId} missing`);
  const node = manifest.meshNodes.find(candidate => candidate.meshAssetId === oldMesh.meshAssetId);
  const asset = manifest.meshAssets.find(candidate => candidate.id === oldMesh.meshAssetId);
  const sourceBytes = readFileSync(resolve(root, node.sourceFile));
  assert.equal(createHash('sha256').update(sourceBytes).digest('hex'), node.sourceSha256);
  assert.equal(mesh.userData.stableMeshAssetId, oldMesh.meshAssetId);
  assert.deepEqual(mesh.position.toArray(), [0, 0, 0]);
  assert.deepEqual(mesh.scale.toArray(), [1, 1, 1]);
  assert.equal(mesh.rotation.x, 0);
  assert.equal(mesh.rotation.y, 0);
  assert.equal(mesh.rotation.z, 0);
  const positions = mesh.geometry.getAttribute('position').array;
  const normals = mesh.geometry.getAttribute('normal').array;
  const indices = mesh.geometry.index.array;
  assert.deepEqual(Array.from(positions), Array.from(oldMesh.positions));
  assert.deepEqual(Array.from(normals), Array.from(oldMesh.normals));
  assert.deepEqual(Array.from(indices), Array.from(oldMesh.indices));
  assert.equal(indices.length / 3, node.triangleCount);
  assert.equal(positions.length / 3, node.vertexCount);
  mesh.geometry.computeBoundingBox();
  const bbox = mesh.geometry.boundingBox;
  assert.deepEqual(bbox.min.toArray(), oldMesh.bounds.min);
  assert.deepEqual(bbox.max.toArray(), oldMesh.bounds.max);
  assert.deepEqual(bbox.min.toArray(), node.atlasBoundsM.min);
  assert.deepEqual(bbox.max.toArray(), node.atlasBoundsM.max);
  const sourceMin = node.sourceBoundsMm.min;
  const sourceMax = node.sourceBoundsMm.max;
  const expectedMin = [sourceMin[0], sourceMin[2], -sourceMax[1]].map(value => value / 1000);
  const expectedMax = [sourceMax[0], sourceMax[2], -sourceMin[1]].map(value => value / 1000);
  assert.ok(bbox.min.toArray().every((value, axis) => Math.abs(value - expectedMin[axis]) < 5e-8));
  assert.ok(bbox.max.toArray().every((value, axis) => Math.abs(value - expectedMax[axis]) < 5e-8));
  assert.ok(bbox.max.x < 0, `${mesh.name} is not on the expected right-side half-space`);
  assert.equal(asset.laterality, 'right');
  assert.equal(asset.units, 'm');
  assert.equal(asset.axes.frameId, manifest.transform.targetFrameId);
  assert.equal(asset.pose.id, manifest.poseId);
  assert.equal(asset.hash, hash);
  const indexBytes = Buffer.from(indices.buffer, indices.byteOffset, indices.byteLength);
  const lengthBytes = Buffer.alloc(16);
  lengthBytes.writeBigUInt64LE(BigInt(positions.length / 3), 0);
  lengthBytes.writeBigUInt64LE(BigInt(indexBytes.byteLength), 8);
  const topologyHash = createHash('sha256').update('HUMAN-ATLAS-T07-TOPOLOGY-V1\0').update(mesh.name).update('\0').update(lengthBytes).update(indexBytes).digest('hex');
  assert.equal(topologyHash, node.topologySha256);
  assert.equal(topologyHash, asset.topologyHash);
  rows.push({ id: mesh.name, vertices: positions.length / 3, triangles: indices.length / 3, topologyHash, boundsM: { min: bbox.min.toArray(), max: bbox.max.toArray() } });
}

// OrbitControls is tested without rendering: its camera frame and key behavior
// are real library calls; pixel parity and picking remain T12b gates.
const listeners = new Map();
const fakeDocument = { addEventListener() {}, removeEventListener() {} };
const element = {
  clientHeight: 600, clientWidth: 800, style: {}, ownerDocument: fakeDocument,
  addEventListener(type, callback) { listeners.set(type, callback); },
  removeEventListener(type) { listeners.delete(type); },
  getRootNode() { return fakeDocument; },
};
const camera = new three.PerspectiveCamera(45, 800 / 600, 0.002, 100);
const controls = new OrbitControls(camera, element);
controls.enablePan = false;
controls.listenToKeyEvents(element);
const allMin = rows[0].boundsM.min.map((_, axis) => Math.min(...rows.map(row => row.boundsM.min[axis])));
const allMax = rows[0].boundsM.max.map((_, axis) => Math.max(...rows.map(row => row.boundsM.max[axis])));
const center = allMin.map((v, axis) => (v + allMax[axis]) / 2);
const radius = Math.hypot(...allMax.map((v, axis) => v - allMin[axis])) / 2;
const distance = Math.max(0.5, radius * 3.1);
controls.target.set(...center);
const presets = { front: [0, 0, 1], back: [0, 0, -1], lateral: [-1, 0, 0] };
const cameraResults = {};
for (const [name, offset] of Object.entries(presets)) {
  camera.position.set(...center.map((v, axis) => v + offset[axis] * distance));
  controls.update();
  const direction = camera.position.clone().sub(controls.target).normalize().toArray();
  assert.ok(direction.every((value, axis) => Math.abs(value - offset[axis]) < 1e-12));
  cameraResults[name] = direction;
}
const beforeKey = camera.position.clone();
listeners.get('keydown')({ code: 'ArrowLeft', ctrlKey: false, metaKey: false, shiftKey: false, preventDefault() {} });
assert.equal(camera.position.distanceTo(beforeKey), 0);
listeners.get('keydown')({ code: 'ArrowLeft', ctrlKey: false, metaKey: false, shiftKey: true, preventDefault() {} });
assert.ok(camera.position.distanceTo(beforeKey) > 0);
const afterKey = camera.position.toArray();
controls.dispose();

console.log(JSON.stringify({
  result: 'pass', threeVersion: three.REVISION, glbSha256: hash,
  meshCount: rows.length, vertexCount: rows.reduce((n, row) => n + row.vertices, 0),
  triangleCount: rows.reduce((n, row) => n + row.triangles, 0),
  frameId: manifest.transform.targetFrameId, units: 'm', laterality: 'right', poseId: manifest.poseId,
  exactPositionNormalIndexParity: true, topologyHashesMatch: true,
  orbitPresets: cameraResults, plainArrowLeftMovedCamera: false, shiftArrowLeftMovedCamera: true,
  keyboardParity: 'requires adapter: raw WebGL rotates on plain arrows; OrbitControls pans by default',
  afterShiftArrowLeft: afterKey, meshes: rows,
}, null, 2));
