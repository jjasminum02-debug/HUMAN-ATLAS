import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { AnimationMixer, LoopOnce, Matrix4, Mesh, Vector3 } from 'three';
import { loadAnimationScene } from './animationSceneAdapter.ts';
import { sourceGeometrySha256 } from './datasets/sourceMotionGeometry.ts';
import type { MotionAsset } from '../domain/motionLearning.ts';
const root = new URL('../../../', import.meta.url);
async function candidate() {
  const bundle = JSON.parse(await readFile(new URL('atlas-data/motion/motion-learning.json', root), 'utf8'));
  const asset: MotionAsset = bundle.motionAssets.find((a: MotionAsset) => a.id === 'T59-ASSET-ZA-R-TIBANT-DF');
  const bytes = await readFile(new URL(asset.uri, root));
  return { asset, bytes: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer };
}
test('real source clip preserves base buffers, fixed bones and exact reset', async () => {
  const { asset, bytes } = await candidate();
  const resource = await loadAnimationScene(bytes, asset);
  try {
    assert.equal(resource.sourceNodes.size, 58);
    for (const member of asset.sourceBinding!.members) {
      const mesh = resource.sourceNodes.get(member.sourceKey) as Mesh;
      assert.equal(await sourceGeometrySha256(mesh.geometry), member.geometrySha256);
    }
    const selected = resource.sourceNodes.get(asset.sourceBinding!.subjectSourceKey) as Mesh;
    const moving = resource.sourceNodes.get(asset.sourceBinding!.members.find(m => m.role === 'moving_structure')!.sourceKey) as Mesh;
    const fixed = resource.sourceNodes.get(asset.sourceBinding!.members.find(m => m.role === 'fixed_structure')!.sourceKey) as Mesh;
    const fixedMatrix = fixed.matrix.clone(); const basePosition = selected.geometry.getAttribute('position').array.slice();
    const start = moving.position.clone(); const mixer = new AnimationMixer(resource.scene);
    mixer.clipAction(resource.animations[0]).play(); mixer.setTime(1); resource.scene.updateMatrixWorld(true);
    const influences = selected.morphTargetInfluences!;
    const phase = influences.reduce((sum,w,i)=>sum+w*(i+1)/influences.length,0);
    assert.ok(Math.abs(phase-.5)<1e-6);
    assert.ok(moving.position.distanceTo(start) > .0001);
    assert.deepEqual(fixed.matrix.toArray(), fixedMatrix.toArray());
    mixer.setTime(0); resource.scene.updateMatrixWorld(true);
    assert.ok(moving.position.distanceTo(start) < 1e-7); assert.equal(selected.morphTargetInfluences![0], 0);
    assert.deepEqual(selected.geometry.getAttribute('position').array, basePosition);
    assert.ok(selected.geometry.morphAttributes.normal!.length > 0);
    const offset = selected.geometry.morphAttributes.position![0];
    let nonzero = 0, zero = 0;
    for (let i = 0; i < offset.count; i++) {
      const length = new Vector3().fromBufferAttribute(offset, i).length(); if (length > 1e-9) nonzero++; else zero++;
    }
    assert.ok(nonzero > 100 && zero > 100);
    mixer.stopAllAction(); mixer.uncacheRoot(resource.scene);
  } finally { resource.dispose(); }
});
test('real clip rejects an animated member falsely declared fixed', async () => {
  const { asset, bytes } = await candidate();
  const bad = structuredClone(asset);
  bad.sourceBinding!.members.find(m => m.role === 'moving_structure')!.role = 'fixed_structure';
  await assert.rejects(loadAnimationScene(bytes, bad), /fixed\/passive/);
});

test('dorsiflexion raises the actual anterior foot in the head-positive source frame', async () => {
  const { asset, bytes } = await candidate();
  const manifest = JSON.parse(await readFile(new URL('atlas-data/source-cache/datasets/za/compiled/manifest.json', root), 'utf8'));
  const source = manifest.instances.find((row: { sourceName: string }) => row.sourceName === 'First metatarsal bone.r');
  const resource = await loadAnimationScene(bytes, asset);
  try {
    const foot = resource.sourceNodes.get(source.sourceKey) as Mesh;
    function centroid() {
      resource.scene.updateMatrixWorld(true);
      const positions = foot.geometry.getAttribute('position');
      const point = new Vector3(), result = new Vector3();
      for (let i = 0; i < positions.count; i++) result.add(point.fromBufferAttribute(positions, i).applyMatrix4(foot.matrixWorld));
      return result.divideScalar(positions.count);
    }
    const initial = centroid();
    const mixer = new AnimationMixer(resource.scene);
    const action = mixer.clipAction(resource.animations[0]);
    action.setLoop(LoopOnce, 0); action.clampWhenFinished = true; action.play();
    mixer.setTime(asset.clip.durationSeconds);
    assert.ok(centroid().y > initial.y + .003, 'anterior foot must rise, not plantarflex');
    mixer.stopAllAction(); mixer.uncacheRoot(resource.scene);
  } finally { resource.dispose(); }
});

test('unit-01 bilateral flexion observations preserve signed source frames at keys and between keys in the real loader/mixer', async () => {
  const bundle = JSON.parse(await readFile(new URL('atlas-data/motion/motion-learning.json', root), 'utf8'));
  const authoringRegistry = JSON.parse(await readFile(new URL('atlas-data/motion/authoring/registry.json', root), 'utf8'));
  const assets = bundle.motionAssets.filter((a: MotionAsset) => a.sourceBinding?.sourceFamilyId) as MotionAsset[];
  const allUnique = [...new Map(assets.map(a => [a.uri, a])).values()];
  const unitFamilies = ['shoulder-flexion-left','shoulder-flexion-right','elbow-flexion-left','elbow-flexion-right'];
  const families = new Set(allUnique.map((asset) => asset.sourceBinding!.sourceFamilyId!));
  for (const family of unitFamilies) assert.ok(families.has(family), `missing source-family clip ${family}`);
  const unique = allUnique.filter((asset) => unitFamilies.includes(asset.sourceBinding!.sourceFamilyId!));
  assert.equal(unique.length, unitFamilies.length);
  for (const asset of unique) {
    const family = asset.sourceBinding!.sourceFamilyId!;
    const authoringEntry = authoringRegistry.records.find((row: { id: string }) => row.id === `T66-FAMILY-${family}-AUTHORING`);
    assert.ok(authoringEntry, `missing registered authoring evidence for ${family}`);
    const record = JSON.parse(await readFile(new URL(authoringEntry.path, root), 'utf8'));
    const geometryRecord = JSON.parse(await readFile(new URL(record.geometryRecordPath, root), 'utf8'));
    const bytes = await readFile(new URL(asset.uri, root));
    const resource = await loadAnimationScene(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer, asset);
    const mixer = new AnimationMixer(resource.scene);
    try {
      const action = mixer.clipAction(resource.animations[0]);
      action.setLoop(LoopOnce, 0); action.clampWhenFinished = true; action.play();
      const axis = new Vector3(...record.poseRange.axis as [number, number, number]);
      const pivot = new Vector3(...record.poseRange.pivotMetres as [number, number, number]);
      const phaseSteps = geometryRecord.family.samples * 8;
      for (let key = 0; key <= phaseSteps; key++) {
        const phase = key / phaseSteps;
        mixer.setTime(asset.clip.durationSeconds * phase); resource.scene.updateMatrixWorld(true);
        const rotation = new Matrix4().makeRotationAxis(axis, record.poseRange.endDegrees * Math.PI / 180 * phase);
        for (const member of asset.sourceBinding!.members.filter(m => ['moving_structure', 'co_moving_context'].includes(m.role))) {
          const mesh = resource.sourceNodes.get(member.sourceKey) as Mesh;
          const original = new Matrix4().fromArray(member.instanceMatrix);
          const positions = mesh.geometry.getAttribute('position');
          for (let vertex = 0; vertex < positions.count; vertex++) {
            const local = new Vector3().fromBufferAttribute(positions, vertex);
            const expected = local.clone().applyMatrix4(original).sub(pivot).applyMatrix4(rotation).add(pivot);
            const actual = local.applyMatrix4(mesh.matrixWorld);
            const error = actual.distanceTo(expected);
            assert.ok(error <= 1e-6, `${family}/${member.sourceKey}/sample${key}/${phase}/vertex${vertex} source frame drift (${error} m)`);
          }
        }
      }
    } finally { mixer.stopAllAction(); mixer.uncacheRoot(resource.scene); resource.dispose(); }
  }
});
