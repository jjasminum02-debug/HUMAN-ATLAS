import assert from 'node:assert/strict';
import test from 'node:test';
import { motionLearningIntent } from './atlasMotionExperience.ts';
import { isNerveRelatedActionTextIntent } from './nerveRelations.ts';

test('legacy action text remains available beside a nerve without promoting an unclassified clip', () => {
  assert.equal(isNerveRelatedActionTextIntent(motionLearningIntent({ candidate: null })), true);
  const clip = {} as NonNullable<Parameters<typeof motionLearningIntent>[0]>['candidate'];
  assert.equal(isNerveRelatedActionTextIntent(motionLearningIntent({ candidate: clip })), false);
  assert.equal(isNerveRelatedActionTextIntent(motionLearningIntent({ candidate: clip, learningIntent: 'muscle_action' })), true);
  assert.equal(isNerveRelatedActionTextIntent(motionLearningIntent({ candidate: clip, learningIntent: 'bone_motion' })), false);
});
