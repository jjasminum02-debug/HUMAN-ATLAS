import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateNerveRegistry as validateContract, nerveVisible, selectNerve, nerveCard, innervatedMuscleIds, nervePoseDecision, nerveMuscleHighlights, nerveFrameSignature } from './nerveContract.ts';
import type { NerveRegistry, NerveEvidence, NerveViewContext } from './nerveContract.ts';
const validateNerveRegistry = (value: unknown) => validateContract(value, { allowFixtures: true });

/** Synthetic contract fixture ONLY. No anatomical claims, assets or production bindings. */
function fixture(): NerveRegistry {
  const n = 'fixture:nerve:right'; const asset = 'a'.repeat(64);
  const facts: Array<[NerveEvidence['predicate'], string | null]> = [['identity', null], ['side', null], ['scope', null],
    ['frame', asset], ['placement', asset], ['pose', 'fixture-rest'], ['motor_innervation', 'fixture:muscle:right']];
  const evidence = facts.map(([predicate, objectId]) => ({ id: `fixture:${predicate}`, predicate, objectId,
    subjectId: n, sourcePath: 'work/evidence/T61/synthetic-fixture.json', sourceSha256: 'f'.repeat(64), locator: `fixture ${predicate}`, status: 'verified_local' as const, fixtureOnly: true as const }));
  const targets: NerveRegistry['targets'] = ['muscle', 'muscle_part'].map((kind, i) => {
    const id = i ? 'fixture:part:right' : 'fixture:muscle:right';
    const evidenceIds = ['identity', 'scope', 'side'].map(p => `${id}:${p}`);
    for (const predicate of ['identity', 'scope', 'side'] as const) evidence.push({ ...evidence[0], id: `${id}:${predicate}`, subjectId: id, predicate, objectId: null });
    return { id, kind: kind as 'muscle' | 'muscle_part', side: 'right', evidenceIds };
  });
  const registry: NerveRegistry = { schemaVersion: 'nerve-support-v1', targets, evidence, relations: [{ id: 'fixture:edge', fromId: n, toId: 'fixture:muscle:right',
    kind: 'motor_innervation', targetKind: 'muscle', targetSide: 'right', evidenceIds: ['fixture:motor_innervation'], status: 'verified_local' }],
    instances: [{ id: n, sourceNamespace: 'fixture', sourceObjectId: 'raw-object', conceptId: null, side: 'right', scope: 'branch',
      names: { koTraditional: null, koModern: null, en: 'Synthetic test nerve' }, regionIds: ['leg'], identity: 'verified_local',
      evidenceIds: ['fixture:identity', 'fixture:side', 'fixture:scope'], localSelection: 'verified_geometry', hardHolds: [],
      sourceOnly: true, humanReview: 'not_performed', publicRedistribution: 'held', geometry: { kind: 'curve',
        assetPath: 'atlas-data/assets/synthetic-test-only.glb', assetSha256: asset, topologySha256: asset, sourceNamespace: 'fixture',
        sourceFrameId: 'fixture-native', sourcePoseId: 'fixture-rest', sourceUnit: 'm', targetFrameId: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',
        geometrySpace: 'source_world', sourceObjectToWorld: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
        sourceToAtlas: [1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1], transformKind: 'same_source_axis_conversion',
        evidenceIds: ['fixture:frame', 'fixture:placement', 'fixture:pose'], registrationEvidenceIds: [], validatedPoseIds: ['fixture-rest'] } }] };
  registry.evidence.find(e => e.id === 'fixture:frame')!.value = nerveFrameSignature(registry.instances[0].geometry!);
  return registry;
}
const view: NerveViewContext = { nerves: true, poseId: 'fixture-rest', frameId: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', regionIds: ['leg'], hiddenIds: [] };
test('verified fixture uses typed picking/card and explicit many-muscle relations without granting rights', () => {
  const r = validateNerveRegistry(fixture()); const n = r.instances[0];
  assert.equal(selectNerve(r, { kind: 'nerve', instanceId: n.id }, view), n);
  assert.equal(selectNerve(r, { kind: 'muscle', sourceKey: n.id }, view), null);
  assert.deepEqual(innervatedMuscleIds(r, n), ['fixture:muscle:right']);
  const card = nerveCard(r, n)!; assert.equal(card.kind, 'nerve'); assert.equal(card.courseAvailable, true);
  assert(!/source|evidence|review|task|publicRedistribution/i.test(JSON.stringify(card)));
  assert.equal(n.publicRedistribution, 'held'); assert.equal(n.humanReview, 'not_performed'); assert.equal(n.conceptId, null);
});
test('production validation rejects synthetic software evidence', () => {
  assert.throws(() => validateContract(fixture()), /fixture promotion/);
});
test('off/hidden/wrong region/frame/pose cannot be bypassed by a selected or restored route', () => {
  const r = fixture(); const n = r.instances[0];
  for (const context of [{ ...view, nerves: false }, { ...view, hiddenIds: [n.id] }, { ...view, poseId: 'animated' },
    { ...view, frameId: 'another-person' }, { ...view, regionIds: ['head'] }]) {
    assert.equal(nerveVisible(n, context), false); assert.equal(selectNerve(r, { kind: 'nerve', instanceId: n.id }, context), null);
  }
  n.hardHolds = ['identity_conflict']; assert.equal(nerveVisible(n, view), false); assert.equal(nerveCard(r, n), null);
});
test('raw metadata candidate can be retained but creates no card, geometry or inferred innervation', () => {
  const r = fixture(); const n = r.instances[0]; n.identity = 'candidate'; n.localSelection = 'unsupported'; n.geometry = null; n.side = 'unknown';
  r.relations = []; validateNerveRegistry(r); assert.equal(nerveCard(r, n), null); assert.equal(nerveVisible(n, view), false);
  assert.deepEqual(innervatedMuscleIds(r, n), []);
});
test('text-only identity card is distinct from 3D picking or course support', () => {
  const r = fixture(); const n = r.instances[0]; n.geometry = null; n.localSelection = 'text_only';
  validateNerveRegistry(r); assert.equal(nerveCard(r, n)!.courseAvailable, false); assert.equal(nerveVisible(n, view), false);
});
test('regional context is explicitly not full course extent and requires same-instance scope evidence', () => {
  const r = fixture();
  r.regionalBindings = [{ instanceId: r.instances[0].id, regionIds: ['leg'], evidenceIds: ['fixture:scope'], extentMeaning: 'display_context_only' }];
  validateNerveRegistry(r);
  r.regionalBindings[0].extentMeaning = 'course_extent' as 'display_context_only';
  assert.throws(() => validateNerveRegistry(r), /regional context/);
  r.regionalBindings[0].extentMeaning = 'display_context_only';
  r.regionalBindings[0].evidenceIds = ['fixture:frame'];
  assert.throws(() => validateNerveRegistry(r), /regional context/);
  r.regionalBindings[0].evidenceIds = ['fixture:scope'];
  r.regionalBindings[0].regionIds = ['head'];
  assert.throws(() => validateNerveRegistry(r), /regional context/);
});
test('identity, side and exact scope need subject-specific evidence, not names or parent evidence', () => {
  for (const change of [(r: NerveRegistry) => { r.instances[0].evidenceIds = []; },
    (r: NerveRegistry) => { r.evidence[0].subjectId = 'parent'; },
    (r: NerveRegistry) => { r.evidence[1].status = 'candidate'; },
    (r: NerveRegistry) => { r.instances[0].side = 'unknown'; }]) {
    const r = fixture(); change(r); assert.throws(() => validateNerveRegistry(r));
  }
});
test('wrong units, mirror, invalid hashes, missing geometry and stale pose evidence reject registration', () => {
  for (const mutate of [(r: NerveRegistry) => { r.instances[0].geometry = null; },
    (r: NerveRegistry) => { r.instances[0].geometry!.sourceToAtlas[0] = -1; },
    (r: NerveRegistry) => { r.instances[0].geometry!.assetSha256 = 'old'; },
    (r: NerveRegistry) => { r.instances[0].geometry!.validatedPoseIds.push('motion'); },
    (r: NerveRegistry) => { (r.instances[0].geometry as unknown as {sourceUnit: string}).sourceUnit = 'cm'; },
    (r: NerveRegistry) => { r.instances[0].geometry!.sourceNamespace = 'bp3d-r4'; }]) {
    const r = fixture(); mutate(r); assert.throws(() => validateNerveRegistry(r));
  }
});
test('matching axis conventions do not establish inter-person registration', () => {
  const r = fixture(); r.instances[0].geometry!.transformKind = 'inter_model_registration';
  assert.throws(() => validateNerveRegistry(r), /registration evidence/);
});
test('source millimeters must be converted exactly once; curve and mesh share this contract', () => {
  const r = fixture(); const g = r.instances[0].geometry!; g.sourceUnit = 'mm';
  assert.throws(() => validateNerveRegistry(r), /scale/);
  for (let i=0; i<12; i++) g.sourceToAtlas[i] *= 0.001;
  r.evidence.find(e => e.id === 'fixture:frame')!.value = nerveFrameSignature(g);
  g.kind = 'mesh'; validateNerveRegistry(r);
  g.sourceToAtlas[3] = 0.1; assert.throws(() => validateNerveRegistry(r), /scale/);
});
test('frame proof is invalidated by changed transforms/frame/topology; baked source-world data cannot be transformed twice', () => {
  for (const change of [(r: NerveRegistry) => { r.instances[0].geometry!.sourceFrameId = 'another'; },
    (r: NerveRegistry) => { r.instances[0].geometry!.topologySha256 = 'b'.repeat(64); },
    (r: NerveRegistry) => { r.instances[0].geometry!.sourceObjectToWorld[3] = 1; }]) {
    const r = fixture(); change(r); assert.throws(() => validateNerveRegistry(r));
  }
});
test('source names, collections and candidate claims do not establish motor links', () => {
  const r = fixture(); r.relations[0].status = 'candidate'; r.evidence.find(e => e.id === 'fixture:motor_innervation')!.status = 'candidate'; validateNerveRegistry(r);
  assert.deepEqual(innervatedMuscleIds(r, r.instances[0]), []);
  r.relations[0].status = 'verified_local'; assert.throws(() => validateNerveRegistry(r), /relation evidence/);
});
test('multiple verified targets retained; wrong side and whole-part substitutions need different evidence', () => {
  const r = fixture(); const e = { ...r.evidence.find(e => e.id === 'fixture:motor_innervation')!, id: 'second', objectId: 'fixture:part:right' }; r.evidence.push(e);
  r.relations.push({ ...r.relations[0], id: 'second', toId: 'fixture:part:right', targetKind: 'muscle_part', targetSide: 'right', kind: 'motor_innervation', evidenceIds: ['second'] });
  validateNerveRegistry(r); assert.equal(innervatedMuscleIds(r, r.instances[0]).length, 2);
  r.relations[1].toId = 'fixture:whole'; assert.throws(() => validateNerveRegistry(r));
  const wrong = fixture(); (wrong.relations[0] as {targetSide: string}).targetSide = 'left'; assert.throws(() => validateNerveRegistry(wrong));
});
test('innervation cannot highlight an unregistered or differently scoped target', () => {
  const r = fixture(); r.targets = []; assert.throws(() => validateNerveRegistry(r), /unregistered target/);
});
test('pose incompatibility requests explicit rest restoration without mutating user layer state', () => {
  const r = fixture(); const context = { ...view, poseId: 'animated' };
  assert.equal(nervePoseDecision(r.instances[0], context), 'return_to_validated_pose'); assert.equal(context.nerves, true);
});
test('relationship highlighting respects both nerve and existing muscle layer/hold/hidden policy', () => {
  const r = validateNerveRegistry(fixture()); const selection = { kind: 'nerve' as const, instanceId: r.instances[0].id };
  assert.deepEqual(nerveMuscleHighlights(r, selection, view, new Set(['fixture:muscle:right'])), ['fixture:muscle:right']);
  assert.deepEqual(nerveMuscleHighlights(r, selection, view, new Set()), []);
  assert.deepEqual(nerveMuscleHighlights(r, selection, { ...view, nerves: false }, new Set(['fixture:muscle:right'])), []);
});
test('cutaneous territory, dermatome, proprioception and traditional areas cannot occupy a motor slot', () => {
  for (const kind of ['cutaneous_territory', 'root_dermatome', 'muscle_proprioception', 'traditional_meridian']) {
    const r = fixture(); (r.relations[0] as {kind: string}).kind = kind;
    assert.throws(() => validateNerveRegistry(r));
  }
});
test('source hierarchy branch claims require exact endpoints/side; cycles and missing nodes rejected', () => {
  const r = fixture(); const child = structuredClone(r.instances[0]); child.id = 'fixture:child'; child.sourceObjectId = 'child-source'; child.localSelection = 'unsupported'; child.geometry = null;
  r.instances.push(child); r.relations.push({ id: 'branch', fromId: child.id, toId: r.instances[0].id, kind: 'branch_of', targetKind: 'nerve', evidenceIds: [], status: 'candidate' });
  validateNerveRegistry(r); r.relations[1].status = 'verified_local'; assert.throws(() => validateNerveRegistry(r));
  r.relations[1].status = 'candidate'; r.relations.push({ ...r.relations[1], id: 'cycle', fromId: r.instances[0].id, toId: child.id });
  assert.throws(() => validateNerveRegistry(r), /cycle/); r.relations.pop(); r.relations[1].toId = 'missing'; assert.throws(() => validateNerveRegistry(r));
});
test('independent policy flags cannot be promoted by valid local geometry', () => {
  for (const field of ['sourceOnly', 'humanReview', 'publicRedistribution']) {
    const r = fixture(); (r.instances[0] as unknown as Record<string, unknown>)[field] = field === 'sourceOnly' ? false : 'approved';
    assert.throws(() => validateNerveRegistry(r));
  }
});
