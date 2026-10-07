import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import { serializeLearnerMotionRuntime } from './serializeLearnerMotionRuntime.mjs';
function decoded(input) {
  const source = serializeLearnerMotionRuntime(input).replace(/ as const;/g, ';').replace('export default learnerMotionRuntime;', 'result = learnerMotionRuntime;');
  const context = { result: null }; vm.runInNewContext(source, context);
  return JSON.parse(JSON.stringify(context.result));
}
test('sharing preserves exact source, side, direction, identities and private bindings', () => {
  const member = { sourceKey: 'source-' + 'a'.repeat(64), geometrySha256: 'b'.repeat(64), role: 'deforming_muscle_surface', weights: [0, .5, 1] };
  const rows = ['left', 'right'].map(side => ({ label: '동작 설명'.repeat(12), candidate: {
    definition: { id: `definition-${side}`, actionId: `action-${side}`, instanceId: `subject-${side}`, side,
      movingStructureIds: [member.sourceKey], staticReference: { frameId: 'original-frame', poseId: 'rest' } },
    asset: { id: `asset-${side}`, motionDefinitionId: `definition-${side}`, sha256: 'c'.repeat(64),
      sourceBinding: { subjectKind: 'muscle', subjectSourceKey: `subject-${side}`, members: [member] },
      poseControl: { actionDirection: side === 'right' ? 'reverse' : 'forward', endDegrees: -14 } },
  }}));
  const input = { schemaVersion: 'fixture', actions: { source: rows }, wave1Actions: { other: rows } };
  const snapshot = structuredClone(input);
  assert.deepEqual(decoded(input), snapshot); assert.deepEqual(input, snapshot);
  assert.equal(serializeLearnerMotionRuntime(input), serializeLearnerMotionRuntime(input));
});
test('a later family can reuse earlier pools without declaration-order errors', () => {
  const binding = { units: 'm', side: null };
  const input = { rows: [{ definition: { staticBinding: binding } }, { asset: { staticBinding: binding } }] };
  assert.deepEqual(decoded(input), input);
  assert.deepEqual(decoded({ actions: {}, wave1Actions: {} }), { actions: {}, wave1Actions: {} });
});
test('reserved strings fail instead of being interpreted as control references', () => {
  assert.throws(() => decoded({ text: '__atlas_motion_ref_0__' }), /Reserved/);
});
test('shared text, matrices and node bindings preserve every nested value across selectors', () => {
  const text = { label: '대표 작용', explanation: '같은 근육의 실제 작용 설명', postureConditions: ['준비 자세'] };
  const matrix = [1,0,0,0,0,1,0,0,0,0,1,0,.5,.3,0,1];
  const bindings = [{ nodeId: 'left-mesh', role: 'muscle_surface' }];
  const input = { actions: { left: [{ text, instanceMatrix: matrix, rig: { id: 'a', nodeBindings: bindings } }],
    right: [{ text: structuredClone(text), instanceMatrix: [...matrix], rig: { id: 'b', nodeBindings: structuredClone(bindings) } }] } };
  assert.deepEqual(decoded(input), input);
  const output = serializeLearnerMotionRuntime(input);
  assert.match(output, /const motion_text =/);
  assert.match(output, /const motion_instanceMatrix =/);
  assert.match(output, /const motion_nodeBindings =/);
});
