import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import type { RigFile } from './rig.ts';
import { actionKeyframes, groupDofs, groupOfJoint, MOVEMENT_GROUPS, movementRoles, rigJointForBones, sampleKeyframes, type MuscleActionsFile } from './movement.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const rig = read('runtime/rig.json') as RigFile;
const actions = read('runtime/muscle-actions.json') as MuscleActionsFile;
const structures = read('runtime/structures.json').structures as { key: string; side: string; names: { en: string }; learner: { visible: boolean } }[];
const byKey = new Map(structures.map(s => [s.key, s]));
const names = (list: { key: string }[]) => new Set(list.map(r => byKey.get(r.key)!.names.en));

test('every action names a settable rig dof and a visible muscle', () => {
  const dofs = new Map(Object.values(rig.joints).flatMap(j => j.dofs.map(d => [d.id, d])));
  for (const [key, row] of Object.entries(actions.muscles)) {
    assert.ok(byKey.get(key)?.learner.visible, key);
    for (const a of row.actions) { assert.ok(dofs.has(a.dof) && !dofs.get(a.dof)!.coupledTo, `${key} ${a.dof}`); assert.ok(a.sign === 1 || a.sign === -1); }
  }
});

test('every joint group has primary movers in both directions on both sides', () => {
  for (const group of MOVEMENT_GROUPS) for (const side of ['l', 'r'] as const) {
    const primary = groupDofs(rig, group.id, side).filter(({ dof }) => !['back:rotation', `wrist_${side}:deviation`, `mtp_${side}:extension`].includes(dof.id));
    for (const { dof } of primary) for (const sign of [1, -1] as const) {
      const { agonists } = movementRoles(actions, dof.id, sign);
      assert.ok(agonists.some(a => a.role === 'primary'), `${dof.id} ${sign > 0 ? dof.positive : dof.negative}`);
    }
  }
});

test('hip internal rotation: gluteus medius and minimus lead (OpenSim anterior parts), TFL assists (OpenSim with the hip flexed)', () => {
  const roles = movementRoles(actions, 'hip_r:rotation', 1).agonists.map(a => `${byKey.get(a.key)?.names.en}:${a.role}`).sort();
  assert.deepEqual(roles, ['Gluteus medius muscle:primary', 'Gluteus minimus muscle:primary', 'Tensor fasciae latae:assist']);
});

test('textbook movers and opposers come out of the table', () => {
  const knee = movementRoles(actions, 'knee_r:flexion', 1);
  assert.ok(names(knee.agonists).has('Long head of biceps femoris') && names(knee.antagonists).has('Vastus lateralis muscle'));
  const elbow = movementRoles(actions, 'elbow_l:flexion', 1);
  assert.ok(names(elbow.agonists).has('Brachialis muscle') && names(elbow.antagonists).has('Lateral head of triceps brachii'));
  // Same-side bending: the right quadratus lumborum bends the trunk to the right (rig back bending - ).
  const right = movementRoles(actions, 'back:bending', -1);
  assert.ok(right.agonists.some(a => byKey.get(a.key)!.names.en === 'Quadratus lumborum muscle' && byKey.get(a.key)!.side === 'right'));
  assert.ok(!right.agonists.some(a => byKey.get(a.key)!.names.en === 'Quadratus lumborum muscle' && byKey.get(a.key)!.side === 'left'));
});

test('left and right muscles carry the same limb actions', () => {
  const sig = (key: string) => actions.muscles[key].actions.filter(a => !/^(back|neck|head):/.test(a.dof)).map(a => `${a.dof.replace(/_[lr]:/, ':')}${a.sign}${a.role}`).sort().join();
  for (const s of structures.filter(s => s.side === 'left' && actions.muscles[s.key])) {
    const twin = structures.find(t => t.side === 'right' && t.names.en === s.names.en && actions.muscles[t.key]);
    if (twin) assert.equal(sig(s.key), sig(twin.key), s.names.en);
  }
});

test('joint lookup, targets and the playback curve', () => {
  const femur = rig.segments.femur_r.bones[0], tibia = rig.segments.tibia_r.bones[0], patella = rig.segments.patella_r.bones[0];
  assert.equal(rigJointForBones(rig, [femur, tibia, patella]), 'knee_r');
  assert.deepEqual(groupOfJoint('subtalar_l'), { group: 'ankle', side: 'l' });
  const knee = rig.joints.knee_r.dofs[0];
  const flex = actionKeyframes(knee, 1);
  assert.deepEqual(flex.map(f => f.to), [84, 84, 0]);
  assert.equal(sampleKeyframes(flex, 0).value, 0); assert.equal(sampleKeyframes(flex, .5).value, 84); assert.ok(Math.abs(sampleKeyframes(flex, 1).value) < 1e-6);
  // Rest is full knee extension: bend first (uncoloured), then extend (coloured).
  const extend = actionKeyframes(knee, -1);
  assert.deepEqual(extend.map(f => [f.to, f.active]), [[84, false], [84, false], [0, true], [0, true]]);
  assert.equal(sampleKeyframes(extend, .1).active, false); assert.equal(sampleKeyframes(extend, .6).active, true);
});
