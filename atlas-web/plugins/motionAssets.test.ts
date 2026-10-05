import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { motionAssetByteBudget } from './motionAssets.ts';

test('larger native trunk delivery is restricted to its exact URI and verified hash', () => {
  const uri = 'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb';
  const sha256 = 'fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf';
  assert.equal(motionAssetByteBudget({ uri, sha256 }), 31_306_820);
  assert.equal(motionAssetByteBudget({ uri, sha256: '0'.repeat(64) }), 8 * 1024 * 1024);
  assert.equal(motionAssetByteBudget({ uri: uri.replace('s04-flex', 'other'), sha256 }), 8 * 1024 * 1024);
});
