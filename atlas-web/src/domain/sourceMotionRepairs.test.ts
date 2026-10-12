import test from 'node:test';
import assert from 'node:assert/strict';
import runtime from '../data/learnerMotionRuntime.generated.ts';
import repairs from '../../../atlas-data/motion/source-motion-repairs-r1.json' with { type: 'json' };
import { applySourceMotionRepair } from './sourceMotionRepairs.ts';
import type { MotionAsset } from './motionLearning.ts';

const all = Object.values(runtime.actions).flat() as unknown as Array<{candidate: {definition: unknown; asset: MotionAsset} | null}>;
for (const row of repairs.rows) test(`${row.assetId}: exact repair retains camera, playback and complete source binding`, () => {
  const base = all.find(o => o.candidate?.asset.id === row.assetId)!.candidate!;
  const result = applySourceMotionRepair(base, repairs.rows)!;
  assert.equal(result.asset.uri, row.uri); assert.equal(result.asset.sha256, row.sha256);
  assert.equal(result.definition, base.definition);
  assert.equal(result.asset.poseControl, base.asset.poseControl);
  assert.equal(result.asset.sourceBinding, base.asset.sourceBinding);
  for (const mutate of [
    (a: MotionAsset) => {a.sha256 = '0'.repeat(64);},
    (a: MotionAsset) => {a.staticBinding.side = a.staticBinding.side === 'left' ? 'right' : 'left';},
    (a: MotionAsset) => {a.staticBinding.referencePoseId += '-drift';},
    (a: MotionAsset) => {a.sourceBinding!.members[0].instanceMatrix[12] += .01;},
    (a: MotionAsset) => {a.sourceBinding!.members[0].geometrySha256 = '0'.repeat(64);},
    (a: MotionAsset) => {a.poseControl!.endDegrees = 10;},
  ]) {
    const candidate = structuredClone(base); mutate(candidate.asset);
    assert.equal(applySourceMotionRepair(candidate, repairs.rows), null, 'changed contract fails closed');
  }
});
test('unrelated candidates and null retain their original identity', () => {
  const base = all.find(o => o.candidate && !repairs.rows.some(r => r.assetId === o.candidate!.asset.id))!.candidate;
  assert.equal(applySourceMotionRepair(base, repairs.rows), base);
  assert.equal(applySourceMotionRepair(null, repairs.rows), null);
});

test('the same rectus source in hip-flexion keeps its independent asset and weights', () => {
  for (const row of repairs.rows) {
    const knee = all.find(o => o.candidate?.asset.id === row.assetId)!.candidate!;
    const hip = all.find(o => o.candidate?.asset.sourceBinding?.subjectSourceKey === knee.asset.sourceBinding!.subjectSourceKey
      && o.candidate?.asset.id !== row.assetId)!.candidate!;
    assert.equal(applySourceMotionRepair(hip, repairs.rows), hip);
  }
});
