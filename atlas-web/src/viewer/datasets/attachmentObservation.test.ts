import { Color } from 'three';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { attachmentBoneKeys, attachmentText } from './regionalContext.ts';
import { attachmentObservationKeys, demandedStructureKeys, observationFrameKeys } from './presentation.ts';
import { anatomyMaterialParameters, ANATOMY_PALETTE } from '../anatomyMaterials.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type { BodyView } from '../wholeBody/contract.ts';
const rows = JSON.parse(readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json', import.meta.url), 'utf8')).objects as RuntimeStructureRecord[];
const find = (name: string, side: string | null) => rows.find(r => r.names.en === name && r.side === side)!;
const rectus = find('Rectus femoris muscle', 'left');
const view: BodyView = {region:'neck', selectedId:rectus.sourceKey, bones:true, muscles:true, supplements:false, dim:true,
  attachmentObservation:{sourceKey:rectus.sourceKey, role:'origin'}};
test('bijoint rectus keeps exact left hip origin separate from patella/tibia insertion', () => {
  assert.match(attachmentText(rectus, 'origin')!, /엉덩뼈/);
  assert.deepEqual(attachmentBoneKeys(rectus.sourceKey, 'origin', rows), [find('Hip bone','left').sourceKey]);
  assert.deepEqual(new Set(attachmentBoneKeys(rectus.sourceKey, 'insertion', rows)), new Set([find('Patella','left').sourceKey,find('Tibia','left').sourceKey]));
  assert.deepEqual(new Set(demandedStructureKeys(rows, view)),new Set([rectus.sourceKey,find('Hip bone','left').sourceKey]));
  assert.deepEqual(new Set(observationFrameKeys(rows, view)),new Set(demandedStructureKeys(rows, view)));
});
test('attachment observation never revives hidden, layer-off, held, wrong-side or foreign-source bones', () => {
  const hip = find('Hip bone','left');
  assert.deepEqual(attachmentObservationKeys(rows,{...view,bones:false}),[]);
  assert.deepEqual(attachmentObservationKeys(rows,{...view,hiddenSourceKeys:[hip.sourceKey]}),[]);
  for (const patch of [{side:'right'}, {localDisplayEligible:false}, {hardHoldReasons:['held']}, {sourceHiddenStatePreserved:{hideViewport:true,hideRender:true}}]) {
    const changed = rows.map(r => r.sourceKey === hip.sourceKey ? {...r,...patch} : r);
    assert.deepEqual(attachmentObservationKeys(changed,view),[]);
  }
  assert.deepEqual(attachmentObservationKeys(rows,{...view,selectedId:find('Rectus femoris muscle','right').sourceKey}),[]);
});
test('wide/part/midline context stays source scoped and non-bone origins are not filled', () => {
  for (const side of ['left','right']) {
    const tibialis=find('Tibialis anterior muscle',side);
    assert.deepEqual(attachmentBoneKeys(tibialis.sourceKey,'origin',rows),[find('Tibia',side).sourceKey]);
    assert.equal(attachmentBoneKeys(tibialis.sourceKey,'insertion',rows).length,2);
    const oblique=find('External abdominal oblique muscle',side);
    assert.equal(attachmentBoneKeys(oblique.sourceKey,'origin',rows).length,8);
    const abdominal=find('(Abdominal part of pectoralis major muscle)',side);
    assert.deepEqual(attachmentBoneKeys(abdominal.sourceKey,'origin',rows),[]);
    assert.deepEqual(attachmentBoneKeys(abdominal.sourceKey,'insertion',rows),[find('Humerus',side).sourceKey]);
  }
});
test('origin/insertion whole-bone cues differ with depth checks; source tissue palette is preserved', () => {
  const origin=anatomyMaterialParameters('bone',{mode:'originContext'});
  const insertion=anatomyMaterialParameters('bone',{mode:'insertionContext'});
  assert.equal(new Color(origin.color).getHexString(),'476eb4');assert.equal(new Color(insertion.color).getHexString(),'bc7135');
  assert.equal(origin.depthTest,true);assert.equal(insertion.depthWrite,true);
  const translucent=anatomyMaterialParameters('bone',{mode:'originContext',userTranslucent:true});
  assert.equal(translucent.opacity,.3);assert.equal(translucent.depthWrite,false);
  assert.equal(new Color(translucent.color).getHexString(),'476eb4');
  assert.equal(new Color(anatomyMaterialParameters('muscle',{mode:'originContext'}).color).getHexString(),ANATOMY_PALETTE.muscle.slice(1));
});
