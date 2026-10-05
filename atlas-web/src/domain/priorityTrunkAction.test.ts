import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { projectLearnerMotionActionOptions, type MotionLearningBundle } from './motionLearning.ts';
import { loadAnimationScene } from '../viewer/animationSceneAdapter.ts';
const read = (p: string) => JSON.parse(readFileSync(new URL('../../../' + p, import.meta.url), 'utf8'));
const bundle = read('atlas-data/motion/motion-learning.json') as MotionLearningBundle;
const outcomes = read('work/evidence/T66/priority-trunk-2026-10-05/action-outcome.json');
const accepted = Object.fromEntries(read('atlas-data/motion/t66-priority-action-acceptance.json').rows.map((r: {actionId: string}) => [r.actionId, r]));
test('bilateral trunk flexion actions bind exact native surfaces and state external-oblique cooperation', () => {
  assert.equal(outcomes.length, 4);
  assert.equal(new Set(outcomes.map((r: {sourceKey: string}) => r.sourceKey)).size, 4);
  for (const r of outcomes) {
    const a = bundle.motionAssets.find(a => a.id === r.assetId)!;
    assert.equal(a.sourceBinding!.subjectSourceKey, r.sourceKey);
    assert.equal(a.staticBinding.side, r.side);
    assert.equal(a.poseControl!.actionDirection, 'forward');
    assert.ok(r.shorteningMetres > .0005 && r.fixedMaskErrorMetres < 1e-6 && r.pelvisFixedErrorMetres < 1e-6);
    assert.equal(a.poseControl!.endDegrees, 14);
    if (r.kind === 'OBLIQUE') {
      const definition = bundle.motionDefinitions.find(d => d.id === a.motionDefinitionId)!;
      const action = bundle.muscleActions.find(x => x.id === definition.actionId)!;
      assert.match(action.actionLabel, /양측 협응 몸통 굽힘/);
      assert.match(action.explanation, /반대 방향 몸통 돌림과 구분/);
    }
    assert.equal(projectLearnerMotionActionOptions(r.sourceKey, bundle, [], r.side, accepted).find(o => o.candidate?.asset.id === r.assetId)?.learningIntent, 'muscle_action');
    assert.equal(projectLearnerMotionActionOptions(r.sourceKey, bundle, [], r.side).find(o => o.candidate?.asset.id === r.assetId)?.learningIntent, 'posture_observation');
    assert.ok(projectLearnerMotionActionOptions(r.sourceKey, bundle, [], r.side === 'left' ? 'right' : 'left', accepted).every(o => o.candidate?.asset.id !== r.assetId));
    assert.equal(r.physiologicalContractionClaimed, false);
  }
});
test('one shared trunk family loads intact native skeletal and passive-muscle context', async () => {
  const seen = new Set<string>();
  for (const r of outcomes) {
    const a = bundle.motionAssets.find(a => a.id === r.assetId)!;
    const bytes = readFileSync(new URL('../../../' + a.uri, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), a.sha256);
    if (seen.has(a.uri)) continue;
    seen.add(a.uri);
    const resource = await loadAnimationScene(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer, a);
    assert.equal(resource.sourceNodes.size, r.contextSurfaceCount);
    const members = a.sourceBinding!.members;
    const sources = read('atlas-data/source-cache/datasets/za/compiled/manifest.json').instances;
    for (const name of ['Hip bone.l', 'Hip bone.r', 'Sacrum', 'Vertebra L1', 'Vertebra L5', 'Vertebra T1', 'Vertebra T12', 'Body of sternum', 'Rectus abdominis muscle.l', 'Rectus abdominis muscle.r', 'External abdominal oblique muscle.l', 'External abdominal oblique muscle.r']) {
      const key = sources.find((s: {name: string}) => s.name === name).sourceKey;
      assert.ok(members.some(m => m.sourceKey === key), name);
    }
    const ar = accepted[bundle.muscleActions.find(x => x.id === bundle.motionDefinitions.find(d => d.id === a.motionDefinitionId)!.actionId)!.id];
    const author = read(ar.authoringPath);
    assert.equal(author.rights.publicRedistribution, 'held');
    assert.equal(author.rights.humanReview, 'not_performed');
    assert.equal(author.measuredAnatomicalAxis, false);
    assert.equal(author.measuredAttachmentFootprints, false);
    resource.dispose();
  }
  assert.equal(seen.size, 1);
});
