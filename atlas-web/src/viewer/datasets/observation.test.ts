import { test } from 'node:test';
import assert from 'node:assert/strict';
import { observationContextKeys, demandedStructureKeys, observationFrameKeys } from './presentation.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type { BodyView } from '../wholeBody/contract.ts';
const row = (sourceKey: string, extra: Partial<RuntimeStructureRecord> = {}) => ({ sourceKey, names: {en: sourceKey}, regionIds: ['abdomen'], side: 'left', kind: 'muscle', localDisplayEligible: true, defaultVisible: true, ...extra } as RuntimeStructureRecord);
const rows = [row('deep'), row('external'), row('bone', {kind:'bone'}), row('held', {localDisplayEligible:false}), row('otherSide', {side:'right'})];
const view: BodyView = { region: null, regionIds:['neck'], selectedId:'deep', bones:true, muscles:true, supplements:false, dim:true, focusObservation:true, hiddenSourceKeys:['external'] };
test('temporary focus retains eligible context and never revives explicit hidden, held or layer-off surfaces', () => {
  assert.deepEqual(observationContextKeys(rows, view), ['deep','bone']);
  assert.deepEqual(demandedStructureKeys(rows, view), ['deep','bone']);
  assert.deepEqual(observationContextKeys(rows, {...view, bones:false}), ['deep']);
  assert.deepEqual(observationContextKeys(rows, {...view, muscles:false}), ['bone']);
  assert.deepEqual(demandedStructureKeys(rows, {...view, focusObservation:false}), []);
  assert.deepEqual(view.hiddenSourceKeys, ['external']);
});
test('nerve camera fits existing course and confirmed related structures while retaining broader visible context', () => {
  const sources = [row('nerve',{kind:'nerve',nerve:{poseId:'rest',muscleKeys:['motor'],branchKeys:[]}}), row('motor'),row('unrelatedLeg',{kind:'bone'})];
  const nerveView = {...view, selectedId:'nerve',nerves:true,poseId:'rest',hiddenSourceKeys:[]};
  assert.deepEqual(observationContextKeys(sources,nerveView),['nerve','motor','unrelatedLeg']);
  assert.deepEqual(observationFrameKeys(sources,nerveView),['nerve','motor']);
  assert.deepEqual(observationFrameKeys(sources,{...nerveView,hiddenSourceKeys:['motor']}),['nerve']);
  assert.deepEqual(observationFrameKeys(sources,{...nerveView,nerves:false}),['motor']);
});
