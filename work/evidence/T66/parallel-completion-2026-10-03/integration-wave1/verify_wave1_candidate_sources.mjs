import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { GLTFLoader } from '../../../../../atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { sourceGeometrySha256 } from '../../../../../atlas-web/src/viewer/datasets/sourceMotionGeometry.ts';

const root = path.resolve(import.meta.dirname, '../../../../..');
const wave = path.join(root, 'work/evidence/T66/parallel-completion-2026-10-03/wave-1');
const out = path.join(root, 'work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/candidate-source-validation.json');
const manifestPath = path.join(root, 'atlas-data/source-cache/datasets/za/compiled/manifest.json');
const handoffPath = path.join(wave, 'workers/C/handoff.json');

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const readJson = async (file) => JSON.parse(await readFile(file, 'utf8'));
const arrayBuffer = (bytes) => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const parseGlb = async (file) => {
  const bytes = await readFile(file);
  const parsed = await new GLTFLoader().parseAsync(arrayBuffer(bytes), '');
  const bySourceKey = new Map();
  const duplicateSourceKeys = new Set();
  parsed.scene.traverse((node) => {
    const key = node.userData?.sourceKey;
    if (!key) return;
    if (bySourceKey.has(key)) duplicateSourceKeys.add(key);
    bySourceKey.set(key, node);
  });
  if (duplicateSourceKeys.size) throw new Error(`duplicate source keys in ${file}: ${[...duplicateSourceKeys].join(',')}`);
  parsed.scene.updateMatrixWorld(true);
  return { bytes, parsed, bySourceKey };
};
const matrixNear = (actual, expected, tolerance = 1e-6) => actual.length === expected.length
  && actual.every((value, index) => Math.abs(Number(value) - Number(expected[index])) <= tolerance);

const manifest = await readJson(manifestPath);
const handoff = await readJson(handoffPath);
if (handoff.runId !== 'T66-W1-20261003-5dadff8d782b') throw new Error('C handoff runId mismatch');
const instances = new Map(manifest.instances.map((row) => [row.sourceKey, row]));
const chunks = new Map(manifest.chunks.map((row) => [row.id, row]));
const results = [];
for (const candidate of handoff.candidateAssets.filter((row) => row.passed === true)) {
  const candidateRoot = path.join(wave, 'workers/C/candidates', candidate.candidateId);
  const qc = await readJson(path.join(candidateRoot, 'pose-qc.json'));
  const sourceGlb = path.join(candidateRoot, 'motion.glb');
  const { bytes: candidateBytes, parsed: candidateParsed, bySourceKey: candidateNodes } = await parseGlb(sourceGlb);
  if (sha(candidateBytes) !== candidate.motionGlbSha256) throw new Error(`${candidate.candidateId}: candidate GLB hash mismatch`);
  const rows = [];
  for (const qcRow of qc.memberRows) {
    const instance = instances.get(qcRow.sourceKey);
    const candidateNode = candidateNodes.get(qcRow.sourceKey);
    if (!instance || !candidateNode?.isMesh) throw new Error(`${candidate.candidateId}: exact source member missing ${qcRow.sourceKey}`);
    const lod = instance.lods[qcRow.lod];
    const chunk = chunks.get(lod.chunk);
    if (!chunk) throw new Error(`${candidate.candidateId}: compiled source chunk missing ${lod.chunk}`);
    const sourceChunkPath = path.join(root, 'atlas-data/source-cache/datasets/za/compiled', `${chunk.id}.glb`);
    const sourceChunkBytes = await readFile(sourceChunkPath);
    if (sha(sourceChunkBytes) !== chunk.sha256 || sourceChunkBytes.byteLength !== chunk.bytes) throw new Error(`${candidate.candidateId}: source chunk hash/size mismatch ${chunk.id}`);
    const sourceParsed = await new GLTFLoader().parseAsync(arrayBuffer(sourceChunkBytes), '');
    let sourceMesh = null;
    sourceParsed.scene.traverse((node) => {
      if (!node.isMesh) return;
      const resourceKey = node.userData?.resourceKey ?? node.userData?.stableMeshAssetId ?? node.name;
      if (resourceKey === lod.resource) {
        if (sourceMesh) throw new Error(`${candidate.candidateId}: duplicate source resource ${lod.resource}`);
        sourceMesh = node;
      }
    });
    if (!sourceMesh) throw new Error(`${candidate.candidateId}: source resource not found ${lod.resource}`);
    const [sourceGeometryHash, candidateGeometryHash] = await Promise.all([
      sourceGeometrySha256(sourceMesh.geometry), sourceGeometrySha256(candidateNode.geometry),
    ]);
    const candidateInstanceMatrix = candidateNode.userData?.sourceInstanceMatrix ?? candidateNode.matrix.toArray();
    const row = {
      candidateId: candidate.candidateId,
      sourceKey: qcRow.sourceKey,
      sourceLabel: instance.name,
      runtimeNodeId: candidateNode.name,
      role: qcRow.role,
      side: instance.sourceLabelSide,
      lod: qcRow.lod,
      resourceKey: lod.resource,
      sourceChunkSha256: lod.chunk,
      sourceGeometrySha256: sourceGeometryHash,
      candidateGeometrySha256: candidateGeometryHash,
      geometryExact: sourceGeometryHash === candidateGeometryHash,
      sourceChunkVerified: true,
      matrixVerified: matrixNear(candidateInstanceMatrix, instance.matrix),
      sourceInstanceMatrix: instance.matrix,
      candidateInstanceMatrix,
      frameId: manifest.frameContract.targetFrameId,
      units: manifest.unit,
    };
    if (!row.geometryExact || !row.matrixVerified) throw new Error(`${candidate.candidateId}: source correspondence failed ${qcRow.sourceKey}`);
    rows.push(row);
  }
  results.push({
    candidateId: candidate.candidateId,
    candidateGlbSha256: candidate.motionGlbSha256,
    candidateGlbBytes: candidateBytes.byteLength,
    frameId: manifest.frameContract.targetFrameId,
    units: manifest.unit,
    referencePoseCandidate: qc.sourcePose,
    currentRuntimePose: manifest.frameContract.staticReferencePose.id,
    candidateNodeCount: candidateNodes.size,
    sourceMemberCount: rows.length,
    exactGeometryRows: rows.filter((row) => row.geometryExact).length,
    exactMatrixRows: rows.filter((row) => row.matrixVerified).length,
    rows,
  });
}
const result = {
  schemaVersion: 't66-wave1-candidate-source-validation-v1',
  runId: handoff.runId,
  inputs: {
    candidateHandoffSha256: sha(await readFile(handoffPath)),
    compiledManifestSha256: sha(await readFile(manifestPath)),
    sourceFrame: manifest.frameContract.targetFrameId,
    sourceUnits: manifest.unit,
    currentStaticPose: manifest.frameContract.staticReferencePose.id,
  },
  result: 'passed',
  candidateCount: results.length,
  totalMemberRows: results.reduce((sum, row) => sum + row.sourceMemberCount, 0),
  exactGeometryRows: results.reduce((sum, row) => sum + row.exactGeometryRows, 0),
  exactMatrixRows: results.reduce((sum, row) => sum + row.exactMatrixRows, 0),
  candidates: results,
  limits: ['Source-local geometry and frame equivalence only; not target identity/extent approval.', 'Pose alias equivalence is limited to base frame/geometry and instance transform; not human review or rights clearance.'],
};
await writeFile(out, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify({ out, result: result.result, candidateCount: result.candidateCount, totalMemberRows: result.totalMemberRows, exactGeometryRows: result.exactGeometryRows, exactMatrixRows: result.exactMatrixRows }, null, 2));
