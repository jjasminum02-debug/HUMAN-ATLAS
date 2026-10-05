import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { loadAnimationScene } from '../viewer/animationSceneAdapter.ts';
import { projectLearnerMotionActionOptions, type MotionLearningBundle } from './motionLearning.ts';
const read = (path: string) => JSON.parse(readFileSync(new URL('../../../' + path, import.meta.url), 'utf8'));
const bundle = read('atlas-data/motion/motion-learning.json') as MotionLearningBundle;
const acceptance = read('atlas-data/motion/t66-priority-action-acceptance.json');
const adopted = Object.fromEntries(acceptance.rows.map((r: {actionId: string}) => [r.actionId, r]));
const outcomePaths = [...new Set(acceptance.rows.filter((r: {assetId: string}) => r.assetId.startsWith('T66-PRIORITY-S03-')).map((r: {outcomePath: string}) => r.outcomePath))] as string[];
const outcomes = outcomePaths.flatMap(path => read(path));
test('twelve native parts/sides have emitted shortening, fixed attachment context and exact action selection', () => {
  assert.equal(outcomes.length, 12);
  assert.equal(new Set(outcomes.map((r: {sourceKey: string}) => r.sourceKey)).size, 12);
  for (const row of outcomes) {
    const a = bundle.motionAssets.find(a => a.id === row.assetId)!;
    assert.equal(a.sourceBinding!.subjectSourceKey, row.sourceKey);
    assert.equal(a.staticBinding.side, row.side);
    assert.equal(a.sha256, row.motionSha256);
    assert.equal(a.poseControl!.actionDirection, row.kind === 'LEV' ? 'forward' : 'reverse');
    assert.ok(row.shorteningMetres > .0005 && row.fixedMaskErrorMetres < 1e-6);
    assert.ok(row.inspectedPoseSamples >= 49);
    assert.equal(row.physiologicalContractionClaimed, false);
    const options = projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side, adopted);
    assert.equal(options.find(o => o.candidate?.asset.id === row.assetId)?.learningIntent, 'muscle_action');
    assert.equal(projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side)
      .find(o => o.candidate?.asset.id === row.assetId)?.learningIntent, 'posture_observation');
    assert.ok(projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side === 'left' ? 'right' : 'left', adopted)
      .every(o => o.candidate?.asset.id !== row.assetId));
    assert.ok(options.filter(o => !o.candidate?.asset.id.startsWith('T66-PRIORITY-S03-')).every(o => o.learningIntent !== 'muscle_action'));
  }
});
test('actual six unique shoulder packages load the whole context and retain source rights/review restrictions', async () => {
  const seen = new Set<string>();
  for (const row of outcomes) {
    const a = bundle.motionAssets.find(a => a.id === row.assetId)!;
    const bytes = readFileSync(new URL('../../../' + a.uri, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), a.sha256);
    if (seen.has(a.uri)) continue;
    seen.add(a.uri);
    const resource = await loadAnimationScene(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer, a);
    assert.equal(resource.sourceNodes.size, 117);
    resource.dispose();
    const ar = acceptance.rows.find((r: {assetId: string}) => r.assetId === a.id);
    const author = read(ar.authoringPath);
    assert.equal(author.rights.publicRedistribution, 'held');
    assert.equal(author.rights.humanReview, 'not_performed');
    assert.equal(author.measuredAnatomicalAxis, false);
    assert.equal(author.measuredAttachmentFootprints, false);
    assert.ok(a.poseControl?.observationDirection);
    assert.ok(a.poseControl?.framingSourceKeys?.length);
    assert.ok(a.poseControl!.framingSourceKeys!.every(key => a.sourceBinding!.members.some(m => m.sourceKey === key)));
    if (row.kind !== 'PECT') assert.equal(a.poseControl?.contextOpacity, .25);
  }
  assert.equal(seen.size, 6);
});
