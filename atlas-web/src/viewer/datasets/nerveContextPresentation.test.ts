import assert from 'node:assert/strict';
import test from 'node:test';
import type { RuntimeStructureRecord } from './integration.ts';
import type { BodyView } from '../wholeBody/contract.ts';
import { demandedStructureKeys, innervationHighlightKeys } from './presentation.ts';

const row = (sourceKey: string, kind: string, side: string, regionIds: string[]) => ({
  sourceKey, kind, side, regionIds, names: { en: sourceKey }, localDisplayEligible: true, defaultVisible: true,
  ...(kind === 'nerve' ? { nerve: { poseId: 'rest', muscleKeys: [], branchKeys: [] } } : {}),
}) as RuntimeStructureRecord;
const rows = [row('nerve-r', 'nerve', 'right', ['neck']), row('related-r', 'muscle', 'right', ['back']),
  row('related-l', 'muscle', 'left', ['back']), row('bone-r', 'bone', 'right', ['back']),
  { ...row('held-r', 'muscle', 'right', ['back']), localDisplayEligible: false }];
const view: BodyView = { region: null, regionIds: ['neck'], bones: true, muscles: true, nerves: true,
  poseId: 'rest', selectedId: 'nerve-r', dim: true, supplements: false, highlightInnervation: true,
  nerveConceptMuscleKeys: ['related-r', 'related-l', 'bone-r', 'held-r'] };
const highlights = (v: BodyView) => innervationHighlightKeys(rows, v, new Set(demandedStructureKeys(rows, v)));

test('a literature concept context displays only same-side eligible muscle, without changing exact nerve bindings', () => {
  assert.deepEqual(highlights(view), ['related-r']);
  assert.deepEqual(rows[0].nerve!.muscleKeys, []);
});
test('concept highlights cannot bypass layer, hidden, isolation, static pose or selected nerve region', () => {
  for (const v of [{ ...view, nerves: false }, { ...view, muscles: false }, { ...view, poseId: 'moving' },
    { ...view, hiddenSourceKeys: ['nerve-r'] }, { ...view, hiddenSourceKeys: ['related-r'] },
    { ...view, isolate: true }, { ...view, highlightInnervation: false }, { ...view, regionIds: ['leg'] }]) {
    assert.deepEqual(highlights(v), []);
  }
});
