// 4-3 U8: tag placement never overlaps and hides a tag with no free room.
import assert from 'node:assert/strict';
import test from 'node:test';
import { placeLabels } from './labelLayer.ts';

test('tags placed around their spots do not overlap', () => {
  const items = [0, 1, 2, 3].map(i => ({ id: `t${i}`, at: { x: 300, y: 300 + i * 4 }, w: 90, h: 24, leader: true }));
  const boxes = [...placeLabels(items, { w: 800, h: 600 }).values()].filter((b): b is NonNullable<typeof b> => Boolean(b));
  assert.equal(boxes.length, 4);
  for (const a of boxes) for (const b of boxes) if (a !== b)
    assert.ok(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y, 'overlap');
});
test('a tag with no room is hidden, an off-screen spot has no tag', () => {
  const crowd = Array.from({ length: 12 }, (_, i) => ({ id: `c${i}`, at: { x: 60, y: 40 }, w: 50, h: 20, leader: true }));
  const boxes = placeLabels([...crowd, { id: 'off', at: null, w: 50, h: 20, leader: true }], { w: 200, h: 120 });
  assert.ok([...boxes.values()].some(b => b === null));
  assert.equal(boxes.get('off'), null);
});
