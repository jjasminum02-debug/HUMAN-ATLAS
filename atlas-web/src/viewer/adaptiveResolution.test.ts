import assert from 'node:assert/strict';
import test from 'node:test';
import { AdaptiveResolution } from './adaptiveResolution.ts';

const run = (a: AdaptiveResolution, frames: number, ms: number) => { let r = 0; for (let i = 0; i < frames; i++) r = a.moving(ms, true); return r; };

test('a fast machine stays at full resolution', () => {
  const a = new AdaptiveResolution(1.75);
  assert.equal(run(a, 600, 16.7), 1.75); assert.equal(a.degraded, false);
});

test('slow frames step down to the floor and no further', () => {
  const a = new AdaptiveResolution(1);
  assert.equal(run(a, 8, 60), .75); assert.equal(a.degraded, true);
  assert.equal(run(a, 400, 170), .5);
});

test('sparse redraws never lower the resolution, however far apart', () => {
  const a = new AdaptiveResolution(1);
  for (let i = 0; i < 200; i++) a.moving(120, false);
  assert.equal(a.degraded, false);
});

test('one slow gap (tab switch) is ignored', () => {
  const a = new AdaptiveResolution(1);
  run(a, 4, 16); a.moving(30000, true); run(a, 7, 16);
  assert.equal(a.degraded, false);
});

test('recovers one step when frames become fast, and stops probing after a failed raise', () => {
  const a = new AdaptiveResolution(1);
  run(a, 8, 60); assert.equal(a.moving(16, true), .75);
  assert.equal(run(a, 104, 16), 1);
  run(a, 8, 60); assert.equal(a.moving(16, true), .75);
  assert.equal(run(a, 400, 16), .75);
});
