import assert from 'node:assert/strict';
import test from 'node:test';
import { motionActionOptionsForLearner } from './motionLearningData.ts';
import runtime from './learnerMotionRuntime.generated.ts';
import type { LearnerMotionActionOption } from '../domain/motionLearning.ts';

test('deferred resolver retains exact source and side for every playable candidate', () => {
  const keys = new Set([...Object.keys(runtime.actions), ...Object.keys(runtime.wave1Actions)]);
  let playable = 0;
  for (const key of keys) for (const side of ['left', 'right']) {
    const options = motionActionOptionsForLearner(null, side, key);
    assert.equal(new Set(options.map(o => o.id)).size, options.length);
    for (const option of options) if (option.candidate) {
      playable++;
      assert.equal(option.candidate.asset.sourceBinding?.subjectSourceKey, key);
      assert.ok(!option.sideApplicability || [side, 'bilateral', 'midline'].includes(option.sideApplicability));
    }
  }
  assert.ok(playable > 0);
});

test('deferred wave actions retain their candidate objects and learning intent', () => {
  const waves = runtime.wave1Actions as unknown as Record<string, LearnerMotionActionOption[]>;
  let checked = 0;
  for (const [key, rows] of Object.entries(waves)) for (const row of rows) {
    const result = motionActionOptionsForLearner(null, row.sideApplicability, key).find(o => o.id === row.id);
    assert.ok(result);
    assert.equal(result.candidate, row.candidate);
    assert.equal(result.learningIntent, row.learningIntent);
    checked++;
  }
  assert.ok(checked > 0);
});

test('missing selectors do not invent content and canonical text remains available', () => {
  assert.deepEqual(motionActionOptionsForLearner(null, 'left', 'missing-source'), []);
  const canonical = motionActionOptionsForLearner('HA-M-000001', 'right');
  assert.ok(canonical.length);
  assert.ok(canonical.every(row => row.text.explanation.length));
});
