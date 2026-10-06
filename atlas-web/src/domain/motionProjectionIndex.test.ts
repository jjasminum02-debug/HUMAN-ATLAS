import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { projectLearnerMotionActionOptions, type MotionLearningBundle } from './motionLearning.ts';
function fixture() {
  const input = JSON.parse(readFileSync(new URL('../../../atlas-data/motion/motion-learning.json', import.meta.url), 'utf8')) as MotionLearningBundle;
  const asset = input.motionAssets.find(row => row.representationType === 'source_bound_surface')!;
  const definition = input.motionDefinitions.find(row => row.id === asset.motionDefinitionId)!;
  const action = input.muscleActions.find(row => row.id === definition.actionId)!;
  return { bundle: { ...input, muscleActions: [action], motionDefinitions: [definition], motionAssets: [asset] },
    selector: action.sourceSubjectKeys?.[0] ?? action.subjectIds[0], action, asset };
}
test('indexed projection preserves ambiguity instead of picking the first matching asset', () => {
  const { bundle, selector, asset } = fixture();
  assert.ok(projectLearnerMotionActionOptions(selector, bundle, [])[0].candidate);
  bundle.motionAssets.push({ ...asset, id: `${asset.id}-ambiguous` });
  const options = projectLearnerMotionActionOptions(selector, bundle, []);
  assert.equal(options.length, 1); assert.equal(options[0].candidate, null);
  assert.equal(options[0].learningIntent, 'text_only');
});
test('a later input edit or wrong side cannot reuse a stale compatible candidate', () => {
  const { bundle, selector, asset } = fixture();
  assert.ok(projectLearnerMotionActionOptions(selector, bundle, [])[0].candidate);
  asset.staticBinding.side = asset.staticBinding.side === 'left' ? 'right' : 'left';
  assert.equal(projectLearnerMotionActionOptions(selector, bundle, [])[0].candidate, null);
});
