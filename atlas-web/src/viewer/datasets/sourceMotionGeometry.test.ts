import assert from 'node:assert/strict';
import test from 'node:test';
import { BufferGeometry, Float32BufferAttribute, InterleavedBuffer, InterleavedBufferAttribute } from 'three';
import { sourceGeometrySha256 } from './sourceMotionGeometry.ts';
test('packed interleaved geometry keeps the original digest and detects live edits', async () => {
  const packed = new BufferGeometry().setAttribute('position', new Float32BufferAttribute([0, 1, 2, 3, 4, 5], 3));
  const array = new Float32Array([99, 0, 1, 2, 99, 3, 4, 5]);
  const interleaved = new BufferGeometry().setAttribute('position', new InterleavedBufferAttribute(new InterleavedBuffer(array, 4), 3, 1));
  const original = await sourceGeometrySha256(packed);
  assert.equal(await sourceGeometrySha256(interleaved), original);
  array[2] = 9;
  assert.notEqual(await sourceGeometrySha256(interleaved), original, 'no cache may hide changed bytes');
  packed.dispose(); interleaved.dispose();
});
