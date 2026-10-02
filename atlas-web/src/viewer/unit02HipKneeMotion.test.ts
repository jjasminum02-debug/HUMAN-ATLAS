import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { AnimationMixer, Matrix4, Mesh } from 'three';
import { loadAnimationScene } from './animationSceneAdapter.ts';
import type { MotionAsset } from '../domain/motionLearning.ts';
import learnerMotionRuntime from '../data/learnerMotionRuntime.generated.ts';

const root = new URL('../../../', import.meta.url);
const cases = [
  { family: 'hip-flexion-left', side: 'left', moving: 'Femur.l', fixed: 'Hip bone.l', muscles: ['Psoas major.l', 'Iliacus muscle.l', 'Rectus femoris muscle.l'] },
  { family: 'hip-flexion-right', side: 'right', moving: 'Femur.r', fixed: 'Hip bone.r', muscles: ['Psoas major.r', 'Iliacus muscle.r', 'Rectus femoris muscle.r'] },
  { family: 'knee-flexion-left', side: 'left', moving: 'Tibia.l', fixed: 'Femur.l', patella: 'Patella.l', muscles: ['Rectus femoris muscle.l', 'Vastus intermedius muscle.l'] },
  { family: 'knee-flexion-right', side: 'right', moving: 'Tibia.r', fixed: 'Femur.r', patella: 'Patella.r', muscles: ['Rectus femoris muscle.r', 'Vastus intermedius muscle.r'] },
];

function sideFromSourceLabel(name: string): 'left' | 'right' | null {
  return name.endsWith('.l') ? 'left' : name.endsWith('.r') ? 'right' : null;
}

function matrixNear(actual: Matrix4, expected: Matrix4, tolerance = 1e-6): boolean {
  return actual.elements.every((value, index) => Math.abs(value - expected.elements[index]) <= tolerance);
}

test('unit-02 actual GLBs preserve exact bilateral hip/knee source frame, passive muscle deformation, patella motion and fixed structures', async () => {
  const sourceManifest = JSON.parse(await readFile(new URL('atlas-data/source-cache/datasets/za/compiled/manifest.json', root), 'utf8')) as {
    instances: Array<{ name: string; sourceKey: string }>;
  };
  const registry = JSON.parse(await readFile(new URL('atlas-data/motion/authoring/registry.json', root), 'utf8'));
  const sourceByName = new Map<string, string>(sourceManifest.instances.map(row => [row.name, row.sourceKey]));
  const uniquePackages = new Map<string, MotionAsset>();
  for (const sample of cases) {
    const subjectKey = sourceByName.get(sample.muscles[0]);
    assert.ok(subjectKey, `missing exact source member ${sample.muscles[0]}`);
    const options = (learnerMotionRuntime as any).actions[subjectKey] ?? [];
    const actionOption = options.find((row: any) => row.candidate?.definition?.sourceFamilyId === sample.family);
    assert.ok(actionOption, `no learner selector for ${sample.family}/${sample.muscles[0]}`);
    assert.equal(actionOption.candidate.asset.staticBinding.side, sample.side);
    assert.match(actionOption.label, /굽힘 자세에서 관찰/);
    uniquePackages.set(sample.family, actionOption.candidate.asset as MotionAsset);

    for (const name of [sample.moving, sample.fixed, ...(sample.patella ? [sample.patella] : []), ...sample.muscles]) {
      const key = sourceByName.get(name);
      assert.ok(key, `missing source row ${name}`);
      const directOptions = (learnerMotionRuntime as any).actions[key] ?? [];
      assert.ok(directOptions.some((row: any) => row.candidate?.definition?.sourceFamilyId === sample.family),
        `direct selection missing for ${sample.family}/${name}`);
      if (name === sample.fixed || name === sample.patella) {
        const boneOption = directOptions.find((row: any) => row.candidate?.definition?.sourceFamilyId === sample.family
          && row.candidate?.asset?.sourceBinding?.subjectSourceKey === key
          && row.candidate?.asset?.sourceBinding?.subjectKind === 'bone');
        assert.ok(boneOption, `direct bone selection must bind its exact source role for ${sample.family}/${name}`);
        const boneBytes = await readFile(new URL(boneOption.candidate.asset.uri, root));
        const boneResource = await loadAnimationScene(boneBytes.buffer.slice(boneBytes.byteOffset, boneBytes.byteOffset + boneBytes.byteLength) as ArrayBuffer,
          boneOption.candidate.asset as MotionAsset);
        assert.ok(boneResource.sourceNodes.has(key), `direct bone candidate did not load ${sample.family}/${name}`);
        boneResource.dispose();
      }
    }
  }
  assert.equal(uniquePackages.size, 4, 'the four source-frame GLBs must remain four unique family packages');

  for (const sample of cases) {
    const asset = uniquePackages.get(sample.family)!;
    const selectedSurfaceRole = asset.sourceBinding?.members.find(row =>
      row.sourceKey === sourceByName.get(sample.muscles[0]!) && row.side === sample.side)?.role;
    assert.equal(selectedSurfaceRole, 'deforming_passive_surface', `${sample.family}: observation muscles must remain passive, not active-role claims`);
    const authoringEntry = registry.records.find((row: { id: string }) => row.id === `T66-U02-${sample.family}-AUTHORING`);
    assert.ok(authoringEntry, `missing authoring record for ${sample.family}`);
    const authoring = JSON.parse(await readFile(new URL(authoringEntry.path, root), 'utf8'));
    assert.equal(authoring.rights.sourceOnly, true);
    assert.equal(authoring.rights.publicRedistribution, 'held');
    assert.equal(authoring.rights.humanReview, 'not_performed');
    assert.equal(authoring.measuredAnatomicalAxis, false);
    assert.equal(authoring.measuredAttachmentFootprints, false);
    if (sample.patella) {
      assert.ok(authoring.cooperativeMotionLimits.some((line: string) => line.includes('No independent patellar glide')));
      assert.ok(authoring.qualitativeAttachmentContext.some((row: any) => row.sourceKey === sourceByName.get('Rectus femoris muscle.' + (sample.side === 'left' ? 'l' : 'r'))));
      assert.ok(authoring.qualitativeAttachmentContext.some((row: any) => row.sourceKey === sourceByName.get('Vastus intermedius muscle.' + (sample.side === 'left' ? 'l' : 'r'))));
    }

    const bytes = await readFile(new URL(asset.uri, root));
    const resource = await loadAnimationScene(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer, asset);
    const mixer = new AnimationMixer(resource.scene);
    try {
      const movingKey = sourceByName.get(sample.moving)!;
      const fixedKey = sourceByName.get(sample.fixed)!;
      const moving = resource.sourceNodes.get(movingKey) as Mesh;
      const fixed = resource.sourceNodes.get(fixedKey) as Mesh;
      assert.ok(moving && fixed, `${sample.family}: moving/fixed structures must be in the actual loaded scene`);
      resource.scene.updateMatrixWorld(true);
      const movingStart = moving.matrixWorld.clone();
      const fixedStart = fixed.matrixWorld.clone();
      const selectedMuscles = sample.muscles.map(name => {
        const mesh = resource.sourceNodes.get(sourceByName.get(name)!) as Mesh;
        assert.ok(mesh?.morphTargetInfluences, `${sample.family}/${name}: exact deforming surface and morphs`);
        return { name, mesh, baseline: mesh.geometry.getAttribute('position').array.slice() };
      });
      const patella = sample.patella ? resource.sourceNodes.get(sourceByName.get(sample.patella)!) as Mesh : null;
      const patellaStart = patella?.matrixWorld.clone();
      const action = mixer.clipAction(resource.animations[0]);
      action.play();
      for (const seconds of [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]) {
        mixer.setTime(seconds);
        resource.scene.updateMatrixWorld(true);
        assert.ok(fixed.matrixWorld.equals(fixedStart), `${sample.family}/${seconds}s fixed structure moved`);
      }
      mixer.setTime(1);
      resource.scene.updateMatrixWorld(true);
      assert.ok(!moving.matrixWorld.equals(movingStart), `${sample.family}: joint bone did not move at mid-pose`);
      if (sample.patella) assert.ok(!patella!.matrixWorld.equals(patellaStart!), `${sample.family}: patella stayed fixed`);
      for (const { name, mesh } of selectedMuscles) {
        assert.ok(mesh.morphTargetInfluences!.some(weight => weight > 1e-6), `${sample.family}/${name}: no intermediate surface deformation`);
      }
      for (const { name, mesh, baseline } of selectedMuscles) {
        const side = sideFromSourceLabel(name);
        if (side === 'right') {
          const member = asset.sourceBinding!.members.find(row => row.sourceKey === sourceByName.get(name));
          assert.ok(member, `${sample.family}/${name}: missing signed instance matrix`);
          const original = new Matrix4().fromArray(member.instanceMatrix);
          assert.equal(Math.sign(mesh.matrixWorld.determinant()), Math.sign(original.determinant()),
            `${sample.family}/${name}: reflected source-side determinant changed`);
        }
        assert.deepEqual(mesh.geometry.getAttribute('position').array, baseline,
          `${sample.family}/${name}: source base positions must remain immutable under morph playback`);
      }
      mixer.setTime(0);
      resource.scene.updateMatrixWorld(true);
      assert.ok(matrixNear(moving.matrixWorld, movingStart), `${sample.family}: rest pose not restored`);
      if (sample.patella) assert.ok(matrixNear(patella!.matrixWorld, patellaStart!), `${sample.family}: patella not restored`);
      for (const { name, mesh } of selectedMuscles) {
        assert.ok(mesh.morphTargetInfluences!.every(weight => weight === 0), `${sample.family}/${name}: morph weights not restored`);
      }
    } finally {
      mixer.stopAllAction();
      mixer.uncacheRoot(resource.scene);
      resource.dispose();
    }
  }
});
