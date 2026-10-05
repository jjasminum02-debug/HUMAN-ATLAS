import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { projectLearnerMotionActionOptions, type MotionLearningBundle } from './motionLearning.ts';
const read = (path: string) => JSON.parse(readFileSync(new URL('../../../' + path, import.meta.url), 'utf8'));
const bundle = read('atlas-data/motion/motion-learning.json') as MotionLearningBundle;
const acceptance = read('atlas-data/motion/t66-priority-action-acceptance.json');
const accepted = Object.fromEntries(acceptance.rows.map((row: { actionId: string }) => [row.actionId, row]));

test('acceptance is exact source/asset/hash and never promotes passive selectors', () => {
  for (const row of acceptance.rows) {
    const options = projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side, accepted);
    const adopted = options.find(option => option.candidate?.asset.id === row.assetId);
    assert.equal(adopted?.learningIntent, 'muscle_action');
    assert.equal(projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side)
      .find(option => option.candidate?.asset.id === row.assetId)?.learningIntent, 'posture_observation');
    assert.equal(projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side,
      { ...accepted, [row.actionId]: { ...row, motionSha256: '0'.repeat(64) } })
      .find(option => option.candidate?.asset.id === row.assetId)?.learningIntent, 'posture_observation');
    assert.ok(options.filter(option => option.candidate?.asset.sourceBinding?.sourceFamilyId === 'knee-flexion-' + row.side)
      .every(option => option.learningIntent === 'posture_observation'));
    assert.ok(projectLearnerMotionActionOptions(row.sourceKey, bundle, [], row.side === 'left' ? 'right' : 'left', accepted)
      .every(option => option.candidate?.asset.id !== row.assetId));
  }
});

test('four native source-action outcomes retain actual buffers and separate anatomy states', () => {
  const hip = read('work/evidence/T66/priority-ankle-knee-2026-10-05/hip-context-outcome.json');
  const rows = read('work/evidence/T66/priority-ankle-knee-2026-10-05/action-outcome.json')
    .map((row: { assetId: string; kind: string }) => row.kind === 'rectus'
      ? hip.find((item: { assetId: string }) => item.assetId === row.assetId) : row);
  assert.equal(rows.length, 4);
  for (const row of rows) {
    const asset = bundle.motionAssets.find(asset => asset.id === row.assetId);
    assert.equal(asset?.sourceBinding?.subjectSourceKey, row.sourceKey);
    assert.equal(asset?.staticBinding.side, row.side);
    assert.equal(asset?.sha256, row.motionSha256);
    assert.equal(createHash('sha256').update(readFileSync(new URL('../../../' + row.motionUri, import.meta.url))).digest('hex'), row.motionSha256);
    assert.equal(row.passed, true);
    assert.equal(row.physiologicalContractionClaimed, false);
    assert.equal(row.measuredAttachmentFootprints, false);
    assert.ok(row.nonRigidDisplacementSpreadMetres > .001);
    assert.ok(row.samples.every((sample: { fixedMaskErrorMetres: number }) => sample.fixedMaskErrorMetres < 1e-6));
    if (row.kind === 'rectus') {
      assert.ok(row.shorteningMetres > 0);
      assert.ok(row.heldKneeAngleDriftRadians < 1e-6);
      assert.equal(row.kneeExtensionAnimated, false);
    }
  }
  assert.notEqual(rows[0].motionSha256, rows[1].motionSha256);
});

test('rectus knee extension is reverse from preparation and retains complete native context', () => {
  const outcomes = read('work/evidence/T66/priority-ankle-knee-2026-10-05/knee-action-outcome.json');
  const manifest = read('atlas-data/source-cache/datasets/za/compiled/manifest.json');
  const names = new Map(manifest.instances.map((r: { sourceKey: string; name: string }) => [r.sourceKey, r.name]));
  assert.equal(outcomes.length, 2);
  for (const row of outcomes) {
    const asset = bundle.motionAssets.find(asset => asset.id === row.assetId)!;
    assert.equal(asset.poseControl?.actionDirection, 'reverse');
    assert.equal(asset.sha256, row.motionSha256);
    assert.ok(row.extensionShorteningMetres > .0001);
    assert.ok(row.heelExcursionMetres > .08);
    assert.equal(row.fixedMaskErrorMetres < 1e-6, true);
    const members = asset.sourceBinding!.members;
    assert.equal(members.length, 71);
    for (const part of ['Rectus femoris', 'Vastus lateralis', 'Vastus medialis', 'Vastus intermedius']) {
      assert.ok(members.some(m => String(names.get(m.sourceKey)).startsWith(part) && m.side === row.side));
    }
    for (const part of ['Tibia.', 'Fibula.', 'Patella.', 'Calcaneus.', 'Tibialis anterior', 'Soleus', 'Lateral head of gastrocnemius', 'Medial head of gastrocnemius']) {
      assert.ok(members.some(m => String(names.get(m.sourceKey)).startsWith(part)));
    }
  }
});

test('priority action contexts contain every supported native leg and foot muscle on the subject side', () => {
  const overlay = read('atlas-data/overlays/za-local-integration.json');
  for (const row of acceptance.rows) {
    const asset = bundle.motionAssets.find(asset => asset.id === row.assetId)!;
    const keys = new Set(asset.sourceBinding!.members.map(m => m.sourceKey));
    for (const source of overlay.objects) {
      if (source.kind !== 'muscle' || source.side !== row.side || !source.localDisplayEligible
        || source.hardHoldReasons.length || !source.regionIds.some((region: string) => ['leg', 'foot'].includes(region))) continue;
      assert.ok(keys.has(source.sourceKey), source.sourceName + ' absent from ' + row.assetId);
    }
  }
  for (const side of ['left', 'right']) {
    const receipt = read('work/evidence/T66/priority-ankle-knee-2026-10-05/hip-complete-' + side + '/context-reuse-receipt.json');
    assert.equal(receipt.oldSurfaceReplayMaximumErrorMetres, 0);
    const qc = read('work/evidence/T66/priority-ankle-knee-2026-10-05/hip-complete-' + side + '/appended-contact-qc.json');
    assert.equal(qc.passed, true);
    assert.equal(qc.newContainmentMaximum, 0);
  }
});

test('actual hip context loads bounded passive morphs and rejects unverified or excessive corrections', async () => {
  const { loadAnimationScene } = await import('../viewer/animationSceneAdapter.ts');
  for (const row of acceptance.rows.filter((r: { assetId: string }) => /RECTUS-ASSET$/.test(r.assetId))) {
    const asset = bundle.motionAssets.find(asset => asset.id === row.assetId)!;
    const bytes = readFileSync(new URL('../../../' + asset.uri, import.meta.url));
    const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
    const loaded = await loadAnimationScene(buffer, asset);
    assert.equal(loaded.sourceNodes.size, 88);
    loaded.dispose();
    const corrected = asset.sourceBinding!.members.filter(m => m.passiveCorrectiveMaxMetres != null);
    assert.equal(corrected.length, 5);
    const unverified = structuredClone(asset);
    for (const m of unverified.sourceBinding!.members) delete m.passiveCorrectiveMaxMetres;
    await assert.rejects(loadAnimationScene(buffer, unverified), /위치\/회전 track만/);
    const excessive = structuredClone(asset);
    excessive.sourceBinding!.members.find(m => m.passiveCorrectiveMaxMetres != null)!.passiveCorrectiveMaxMetres = .00000001;
    await assert.rejects(loadAnimationScene(buffer, excessive), /변위 범위를 초과/);
  }
});
