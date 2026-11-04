import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import * as THREE from 'three';
import { boneSegments, clampPose, segmentTransforms, type RigFile } from './rig.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/runtime/${path}`, import.meta.url), 'utf8'));
const rig = read('rig.json') as RigFile;
const structures = read('structures.json').structures as { key: string; layer: string | null; learner: { visible: boolean } }[];
const centre = (joint: string) => new THREE.Vector3(...rig.joints[joint].centre);
// Where a joint centre (carried by its own segment) ends up under a pose.
const moved = (joint: string, pose: Record<string, number>) => {
  const segment = Object.entries(rig.segments).find(([, s]) => s.joint === joint)![0];
  return centre(joint).applyMatrix4(segmentTransforms(rig, pose).get(segment)!);
};

test('every visible bone belongs to exactly one segment', () => {
  const segmentOf = boneSegments(rig);
  const bones = structures.filter(s => s.layer === 'bone' && s.learner.visible).map(s => s.key);
  assert.equal(segmentOf.size, bones.length);
  for (const key of bones) assert.ok(segmentOf.has(key), key);
});

test('left and right joint centres mirror across the midline', () => {
  for (const id of Object.keys(rig.joints).filter(id => id.endsWith('_l'))) {
    const l = centre(id), r = centre(id.replace(/_l$/, '_r'));
    assert.ok(Math.abs(l.x + r.x) < .005 && Math.abs(l.y - r.y) < .005 && Math.abs(l.z - r.z) < .005, id);
  }
});

test('rest pose is the identity for every segment', () => {
  for (const matrix of segmentTransforms(rig, {}).values()) assert.ok(matrix.equals(new THREE.Matrix4()));
});

test('joint motions move distal joints in the anatomical direction', () => {
  const ankle = centre('ankle_r'), knee = centre('knee_r');
  const bent = moved('ankle_r', { 'knee_r:flexion': 90 });
  assert.ok(bent.z < ankle.z - .2 && bent.y > ankle.y + .25, 'knee flexion carries the ankle backward and up');
  assert.ok(Math.abs(bent.distanceTo(knee) - ankle.distanceTo(knee)) < 1e-6, 'shank length is preserved');
  const patella = rig.segments['patella_r'], patellaMatrix = segmentTransforms(rig, { 'knee_r:flexion': 60 }).get('patella_r')!;
  assert.equal(patella.parent, 'femur_r');
  assert.ok(!patellaMatrix.equals(new THREE.Matrix4()), 'patella follows knee flexion through its coupled dof');
  assert.ok(moved('knee_r', { 'hip_r:flexion': 45 }).z > knee.z + .2, 'hip flexion swings the knee forward');
  assert.ok(moved('mtp_r', { 'ankle_r:dorsiflexion': 20 }).y > centre('mtp_r').y + .02, 'dorsiflexion lifts the forefoot');
  assert.ok(moved('wrist_l', { 'elbow_l:flexion': 90 }).z > centre('wrist_l').z + .15, 'elbow flexion brings the hand forward');
  assert.ok(moved('elbow_r', { 'shoulder_r:abduction': 90 }).x < centre('elbow_r').x - .2, 'right shoulder abduction moves the elbow outward (−x)');
  assert.ok(moved('shoulder_l', { 'back:flexion': 40 }).z > centre('shoulder_l').z + .2, 'trunk flexion tips the shoulders forward');
});

test('poses are clamped to each dof range', () => {
  assert.deepEqual(clampPose(rig, { 'knee_r:flexion': 400, 'knee_l:flexion': -20, 'unknown:dof': 5 }), { 'knee_r:flexion': 120, 'knee_l:flexion': 0 });
});
