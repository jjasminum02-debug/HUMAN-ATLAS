import test from 'node:test';
import assert from 'node:assert/strict';
import { entranceFrame, ENTRANCE_SECONDS, ENTRANCE_YAW } from './sceneEntrance.ts';

test('entrance is a bounded left-facing camera orbit with a smooth exact end', () => {
  assert.deepEqual(entranceFrame(0), { yaw: 0, opacity: 0.2, finished: false });
  let previous = entranceFrame(0);
  for (let i = 1; i <= 100; i++) {
    const frame = entranceFrame(ENTRANCE_SECONDS * i / 100);
    assert.ok(frame.yaw >= previous.yaw && frame.yaw <= ENTRANCE_YAW);
    assert.ok(frame.opacity >= previous.opacity && frame.opacity <= 1);
    previous = frame;
  }
  assert.deepEqual(previous, { yaw: ENTRANCE_YAW, opacity: 1, finished: true });
  assert.deepEqual(entranceFrame(100), previous);
  assert.deepEqual(entranceFrame(-1), entranceFrame(0));
});

test('entrance eases both ends instead of abruptly starting or stopping rotation', () => {
  const step = 0.01;
  const start = entranceFrame(step).yaw - entranceFrame(0).yaw;
  const middle = entranceFrame(ENTRANCE_SECONDS / 2 + step).yaw - entranceFrame(ENTRANCE_SECONDS / 2).yaw;
  const end = entranceFrame(ENTRANCE_SECONDS).yaw - entranceFrame(ENTRANCE_SECONDS - step).yaw;
  assert.ok(start < middle / 100 && end < middle / 100);
});
