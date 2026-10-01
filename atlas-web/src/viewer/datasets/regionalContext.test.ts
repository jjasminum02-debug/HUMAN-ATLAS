import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { demandedStructureKeys, observingNerves } from './presentation.ts';
import { attachmentBoneKeys, inRegionalRoute } from './regionalContext.ts';
import { readDatasetRoute, searchStructures, type RuntimeStructureRecord } from './integration.ts';
import { framingRecords } from './framing.ts';
import type { BodyView } from '../wholeBody/contract.ts';
const rows = JSON.parse(readFileSync(new URL('../../../../work/evidence/T63/browser/runtime.json', import.meta.url), 'utf8')).objects as RuntimeStructureRecord[];
const view: BodyView = { region: null, bones: true, muscles: true, selectedId: null, dim: true, supplements: false };
const visible = (region: string, extra: Partial<BodyView> = {}) => rows.filter(r => demandedStructureKeys(rows, { ...view, regionIds: [region], ...extra }).includes(r.sourceKey));

test('regional skeletons: cervical, thoracic and lumbar cores plus explicit principal-attachment context, never the entire spine', () => {
  const neck = visible('neck');
  assert.equal(neck.filter(r => r.kind === 'bone' && /^(?:Atlas|Axis|Vertebra C)/.test(r.names.en)).length, 7);
  assert.equal(neck.some(r => /^Vertebra [TL]/.test(r.names.en) || r.names.en === 'Rotatores'), false);
  assert.ok(neck.some(r => r.names.en === 'Clavicle') && neck.some(r => r.names.en === 'Scapula'));
  const thorax = visible('thorax');
  assert.equal(thorax.filter(r => r.kind === 'bone' && /^Vertebra T/.test(r.names.en)).length, 12);
  assert.equal(thorax.filter(r => / rib$/.test(r.names.en)).length, 24);
  assert.equal(thorax.some(r => /^Vertebra [CL]/.test(r.names.en)), false);
  const lumbar = visible('abdomen-lumbar');
  assert.equal(lumbar.filter(r => /^Vertebra L/.test(r.names.en)).length, 5);
  assert.deepEqual(lumbar.filter(r => /^Vertebra T/.test(r.names.en)).map(r => r.names.en), ['Vertebra T12']);
  assert.equal(lumbar.some(r => /^Vertebra C/.test(r.names.en)), false);
  assert.equal(lumbar.filter(r => r.names.en === 'Hip bone').length, 2);
  assert.equal(lumbar.filter(r => r.names.en === 'Femur').length, 2);
});
test('context cannot override layer-off, hidden or held geometry, and does not reframe the region to a complete femur', () => {
  assert.equal(visible('abdomen-lumbar', { bones: false }).some(r => r.kind === 'bone'), false);
  const bone = rows.find(r => r.names.en === 'Femur' && r.side === 'left')!;
  assert.equal(visible('abdomen-lumbar', { hiddenSourceKeys: [bone.sourceKey], selectedId: bone.sourceKey }).includes(bone), false);
  const heldRows = rows.map(r => r.sourceKey === bone.sourceKey ? { ...r, localDisplayEligible: false } : r);
  assert.equal(demandedStructureKeys(heldRows, { ...view, regionIds: ['abdomen-lumbar'] }).includes(bone.sourceKey), false);
  assert.equal(framingRecords(rows, { ...view, regionIds: ['abdomen-lumbar'] }, ['abdomen-lumbar']).includes(bone), false);
  assert.ok(visible('abdomen-lumbar', { muscles: false }).some(r => r.names.en === 'Hip bone'));
});
test('same-side context bones retain regional card/history routes, unrelated bones cannot enter them', () => {
  const left = rows.find(r => r.names.en === 'Psoas major' && r.side === 'left')!;
  const bones = attachmentBoneKeys(left.sourceKey);
  assert.ok(bones.every(key => rows.find(r => r.sourceKey === key)!.side !== 'right'));
  const femur = rows.find(r => r.names.en === 'Femur' && r.side === 'left')!;
  assert.equal(inRegionalRoute(femur, rows, ['abdomen-lumbar']), true);
  assert.equal(readDatasetRoute('?regions=abdomen-lumbar&source=' + femur.sourceKey, rows, ['abdomen-lumbar']).selected, femur.sourceKey);
  const humerus = rows.find(r => r.names.en === 'Humerus' && r.side === 'left')!;
  assert.equal(readDatasetRoute('?regions=abdomen-lumbar&source=' + humerus.sourceKey, rows, ['abdomen-lumbar']).selected, null);
  assert.ok(searchStructures(rows, '', ['abdomen-lumbar']).some(r => r.names.en === 'Femur'));
  const rotator = rows.find(r => r.names.en === 'Rotatores' && r.localDisplayEligible)!;
  assert.ok(visible('neck', { selectedId: rotator.sourceKey }).some(r => r.sourceKey === rotator.sourceKey));
  assert.equal(searchStructures(rows, '', ['neck']).some(r => r.names.en === 'Rotatores'), false);
  assert.ok(searchStructures(rows, 'Rotatores', ['neck']).some(r => r.names.en === 'Rotatores'));
});
test('nerve observation respects all six static-pose, hidden, layer and muscle-selection gates', () => {
  const nerves = rows.filter(r => r.kind === 'nerve'); assert.equal(nerves.length, 6);
  for (const nerve of nerves) {
    const v = { ...view, regionIds: ['leg'], nerves: true, poseId: nerve.nerve!.poseId, selectedId: nerve.sourceKey, observeNerves: true };
    const observe = (next: BodyView) => observingNerves(rows, next, new Set(demandedStructureKeys(rows, next)));
    assert.equal(observe(v), true);
    for (const next of [{ ...v, nerves: false }, { ...v, observeNerves: false }, { ...v, poseId: 'walking' }, { ...v, hiddenSourceKeys: [nerve.sourceKey] }, { ...v, regionIds: ['head'] }, { ...v, selectedId: rows.find(r => r.kind === 'muscle' && r.regionIds.includes('leg') && r.localDisplayEligible)!.sourceKey }]) assert.equal(observe(next), false);
  }
});
