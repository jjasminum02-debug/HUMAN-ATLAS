import test from 'node:test';
import assert from 'node:assert/strict';
import { DEFAULT_MOTION_ASSET_BYTES, NATIVE_TRUNK_BASE, motionAssetByteBudget,
  motionRepairByteBudget, motionRepairBytesEligible } from './motionAssetBudget.ts';

test('only the exact trunk original carries its existing measured ceiling into a direct repair', () => {
  const base = { baseUri: NATIVE_TRUNK_BASE.uri, baseSha256: NATIVE_TRUNK_BASE.sha256 };
  assert.equal(motionAssetByteBudget(NATIVE_TRUNK_BASE), NATIVE_TRUNK_BASE.bytes);
  assert.equal(motionRepairByteBudget(base), NATIVE_TRUNK_BASE.bytes);
  assert.equal(motionRepairBytesEligible({ ...base, bytes: NATIVE_TRUNK_BASE.bytes }), true);
  assert.equal(motionRepairBytesEligible({ ...base, bytes: NATIVE_TRUNK_BASE.bytes + 1 }), false);
  for (const drift of [{ ...base, baseSha256: '0'.repeat(64) }, { ...base, baseUri: base.baseUri + '-other' }]) {
    assert.equal(motionRepairByteBudget(drift), DEFAULT_MOTION_ASSET_BYTES);
    assert.equal(motionRepairBytesEligible({ ...drift, bytes: NATIVE_TRUNK_BASE.bytes }), false);
  }
});

test('unrelated repairs retain 8 MiB and require a positive exact integer byte count', () => {
  const base = { baseUri: 'atlas-data/assets/motion/other.glb', baseSha256: NATIVE_TRUNK_BASE.sha256 };
  assert.equal(motionRepairBytesEligible({ ...base, bytes: DEFAULT_MOTION_ASSET_BYTES }), true);
  for (const bytes of [DEFAULT_MOTION_ASSET_BYTES + 1, 0, -1, .5, NaN, Infinity]) {
    assert.equal(motionRepairBytesEligible({ ...base, bytes }), false);
  }
});
