import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateNerveRegistry, nerveCard, nerveVisible, selectNerve, innervatedMuscleIds,
} from '../src/domain/nerveContract.ts';
import type { NerveRegistry } from '../src/domain/nerveContract.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const load = (path: string) => JSON.parse(readFileSync(resolve(root, path), 'utf8')) as any;
const digest = (path: string) => createHash('sha256').update(readFileSync(resolve(root, path))).digest('hex');
const rawPath = 'work/evidence/T98/blender-raw-object-inventory.json';
const handoffPath = 'work/evidence/T61/T62-handoff.json';
const referencePath = 'work/evidence/T62/source-references.json';
const overlayPath = 'atlas-data/overlays/za-local-integration.json';
const registryPath = 'atlas-data/overlays/nerve-support-t62.json';

const registryInput = load(registryPath);
const registry = validateNerveRegistry(registryInput) as NerveRegistry;
const raw = load(rawPath);
const handoff = load(handoffPath);
const references = load(referencePath);
const za = load(overlayPath);
const actualHashes = new Map<string, string>();
const rawByPointer = new Map(raw.allObjects.map((o: any, index: number) => [o.sourceObjectLocator.objectDataBlockPointer, { o, index }]));

assert.equal(registry.schemaVersion, 'nerve-support-v1');
assert.equal(registry.instances.length, 8, 'six priority objects plus two hierarchy-only parents');
assert.equal(registry.instances.filter(n => n.localSelection === 'text_only').length, 6);
assert.equal(registry.instances.filter(n => n.localSelection === 'unsupported').length, 2);
assert.equal(registry.instances.filter(n => n.geometry !== null).length, 0);
assert.equal(registry.relations.filter(e => e.kind === 'branch_of' && e.status === 'verified_local').length, 6);
assert.equal(registry.relations.filter(e => e.kind === 'motor_innervation' && e.status === 'verified_local').length, 2);
assert.equal(registry.targets.length, 2);
assert.equal(registryInput.regionalBindings.length, 6, 'only six supported nerve nodes receive a leg display-context binding');
assert.ok(registryInput.regionalBindings.every((b: any) => b.regionIds.length === 1 && b.regionIds[0] === 'leg'
  && b.extentMeaning === 'display_context_only'), 'region association does not assert full nerve course extent');
assert.ok(registry.targets.every(t => !t.id.startsWith('HA-')), 'no new canonical HA target IDs');
assert.ok(registryInput.registrationScope.sourceOnly);
assert.equal(registryInput.registrationScope.publicRedistribution, 'held');
assert.equal(registryInput.registrationScope.humanReview, 'not_performed');
assert.equal(registryInput.registrationScope.canonicalHaIdsCreated, 0);
assert.deepEqual(registryInput.registrationScope.denominatorsPreserved, {
  targets: 542, memberships: 563, regions: 12, existingCanonicalHaBindings: 130,
  historical163: { total: 163, classes: [6, 20, 135, 2] },
});

const expectedSelected = [
  'Common fibular nerve.l', 'Common fibular nerve.r',
  'Deep fibular nerve.l', 'Deep fibular nerve.r',
  'Superficial fibular nerve.l', 'Superficial fibular nerve.r',
];
const handoffIds = new Set(handoff.prioritizedSourceObservations.map((x: any) => x.id));
const byObjectName = new Map<string, (typeof registry.instances)[number]>();
for (const n of registry.instances) {
  const rawEntry = rawByPointer.get(n.sourceObjectId) as any;
  const rawObj = rawEntry?.o;
  assert.ok(rawObj, `exact source pointer ${n.sourceObjectId}`);
  byObjectName.set(rawObj.sourceObjectLocator.objectIdName, n);
  const side = rawObj.sourceObjectLocator.objectIdName.endsWith('.l') ? 'left' : 'right';
  assert.equal(n.side, side, 'source label side preserved');
  assert.ok(rawObj.collectionPaths.some((p: string[]) => p.at(-1) === (side === 'left' ? 'Left lower limb' : 'Right lower limb')));
  assert.ok(n.sourceOnly && n.publicRedistribution === 'held' && n.humanReview === 'not_performed');
  assert.equal(n.geometry, null, 'source curve is not accepted geometry');
  assert.equal(n.names.en, rawObj.sourceObjectLocator.objectIdName.replace(/\.[lr]$/, ''), 'learner name remains exact source base label');
  assert.equal(n.names.koTraditional, null, 'Korean historical term not established by this evidence set');
  assert.equal(n.names.koModern, null, 'Korean modern term not established by this evidence set');
  for (const evidenceId of n.evidenceIds) {
    const e = registry.evidence.find(x => x.id === evidenceId);
    assert.ok(e, `nerve evidence ${evidenceId}`);
    const actual = actualHashes.get(e.sourcePath) ?? digest(e.sourcePath);
    actualHashes.set(e.sourcePath, actual);
    assert.equal(e.sourceSha256, actual, `current source hash ${e.sourcePath}`);
  }
}
for (const name of expectedSelected) {
  const entry = byObjectName.get(name);
  assert.ok(entry, `registered source object ${name}`);
  assert.ok(handoffIds.has(`za-c7010a9:raw:${entry.sourceObjectId}`), `T61 priority input ${name}`);
  assert.equal(entry.localSelection, 'text_only');
}
assert.ok(byObjectName.get('Sciatic nerve.l')?.localSelection === 'unsupported');
assert.ok(byObjectName.get('Sciatic nerve.r')?.localSelection === 'unsupported');

for (const binding of registryInput.regionalBindings) {
  const instance = registry.instances.find(n => n.id === binding.instanceId)!;
  const rawEntry = rawByPointer.get(instance.sourceObjectId) as any;
  const evidence = registry.evidence.find(e => binding.evidenceIds.includes(e.id))!;
  assert.ok(['Common fibular nerve.l', 'Common fibular nerve.r', 'Deep fibular nerve.l', 'Deep fibular nerve.r',
    'Superficial fibular nerve.l', 'Superficial fibular nerve.r'].includes(rawEntry.o.sourceObjectLocator.objectIdName));
  assert.equal(binding.regionIds.join(','), 'leg');
  assert.equal(evidence.sourcePath, rawPath);
  assert.match(evidence.locator, new RegExp(`/allObjects/${rawEntry.index}/collectionPaths`));
  assert.match(evidence.value ?? '', /display context|text-only teaching context/i);
}

const lookupPointer = (object: any, pointer: string) => pointer.split('/').filter(Boolean).reduce((v, part) => v?.[part.replaceAll('~1', '/').replaceAll('~0', '~')], object);
for (const e of registry.evidence) {
  const actual = actualHashes.get(e.sourcePath) ?? digest(e.sourcePath);
  actualHashes.set(e.sourcePath, actual);
  assert.equal(e.sourceSha256, actual, `evidence source hash ${e.sourcePath}`);
  if (e.sourcePath === referencePath) {
    const target = lookupPointer(references, e.locator);
    assert.ok(target, `opened source claim locator ${e.locator}`);
  }
}
assert.equal(digest(handoff.inventory), handoff.inventorySha256, 'T61 inventory freeze remains unchanged');

for (const edge of registry.relations) {
  const from = registry.instances.find(n => n.id === edge.fromId)!;
  if (edge.kind === 'branch_of') {
    const to = registry.instances.find(n => n.id === edge.toId)!;
    assert.equal(from.side, to.side, 'branch relation is same-side');
    assert.equal(from.identity, 'verified_local');
    assert.equal(to.identity, 'verified_local');
    const childRaw = (rawByPointer.get(from.sourceObjectId) as any).o;
    assert.equal(childRaw.parentObjectPointer, to.sourceObjectId, 'branch parent follows exact source parent pointer');
    assert.ok(edge.evidenceIds.some(id => {
      const e = registry.evidence.find(row => row.id === id)!;
      return e.sourcePath === rawPath && e.predicate === 'branch' && e.subjectId === from.id && e.objectId === to.id;
    }), 'branch edge carries exact pinned parent evidence');
    assert.ok(edge.evidenceIds.some(id => registry.evidence.find(row => row.id === id)?.sourcePath === referencePath),
      'branch topology carries opened academic claim evidence');
  } else {
    assert.equal(edge.targetSide, from.side, 'motor relation is same-side');
    assert.ok(registry.targets.some(t => t.id === edge.toId && t.kind === 'muscle' && t.side === edge.targetSide));
    assert.ok(from.names.en === 'Deep fibular nerve', 'only the deep fibular node receives the TA motor relation');
    assert.ok(edge.evidenceIds.some(id => {
      const e = registry.evidence.find(row => row.id === id)!;
      return e.sourcePath === referencePath && e.subjectId === from.id && e.predicate === 'motor_innervation' && e.objectId === edge.toId;
    }), 'motor relation carries the opened study claim');
  }
}
for (const side of ['left', 'right']) {
  const nerve = registry.instances.find(n => n.names.en === 'Deep fibular nerve' && n.side === side)!;
  const target = registry.targets.find(t => t.side === side)!;
  assert.deepEqual(innervatedMuscleIds(registry, nerve), [target.id]);
  const card = nerveCard(registry, nerve)!;
  assert.equal(card.courseAvailable, false);
  assert.deepEqual(card.muscleIds, [target.id]);
  assert.equal(nerveVisible(nerve, { nerves: true, poseId: 'unverified', frameId: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', regionIds: ['leg'], hiddenIds: [] }), false);
  assert.equal(selectNerve(registry, { kind: 'nerve', instanceId: nerve.id }, {
    nerves: true, poseId: 'unverified', frameId: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', regionIds: ['leg'], hiddenIds: [],
  }), null, 'text-only record cannot be 3D picked');
}
for (const nerve of registry.instances.filter(n => n.localSelection === 'text_only')) {
  const card = nerveCard(registry, nerve);
  assert.ok(card, `${nerve.names.en} text card DTO`);
  assert.equal(card.courseAvailable, false);
  assert.equal(card.kind, 'nerve');
  assert.ok(!('sourceNamespace' in card) && !('sourceObjectId' in card) && !('evidenceIds' in card)
    && !('humanReview' in card) && !('publicRedistribution' in card), 'learner DTO omits internal provenance fields');
}
assert.equal(za.objects.filter((o: any) => o.targetId === 'TA2:2644' && o.haConceptId === 'HA-M-000003').length >= 2, true,
  'existing HA tibialis anterior mapping remains present for both sides');

console.log(JSON.stringify({
  status: 'passed', sourceHashesChecked: actualHashes.size, selectedTextOnly: 6, contextAncestors: 2,
  branchRelations: 6, sideMatchedMotorRelations: 2, evaluatedGeometry: 0, newCanonicalIds: 0,
  preserved: { targets: 542, memberships: 563, regions: 12, haBindings: 130, historic163: [6, 20, 135, 2] },
}, null, 2));
