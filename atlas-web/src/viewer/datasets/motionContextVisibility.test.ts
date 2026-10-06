import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { motionContextVisibility } from './motionContextVisibility.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type { BodyView } from '../wholeBody/contract.ts';
const rows = JSON.parse(readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json', import.meta.url), 'utf8')).objects as RuntimeStructureRecord[];
const muscle = rows.find(r => r.names.en === 'Extensor carpi radialis longus' && r.side === 'left')!;
const bone = rows.find(r => r.names.en === 'Humerus' && r.side === 'left')!;
const view: BodyView = { region: null, selectedId:muscle.sourceKey, bones:true, muscles:true, supplements:false, dim:true };
const members = [{sourceKey:muscle.sourceKey,role:'deforming_passive_surface'},{sourceKey:bone.sourceKey,role:'fixed_structure'}];
const lookup = (key:string) => rows.find(r => r.sourceKey===key);
test('passive posture and muscle action keep the same complete skeletal context across region filters', () => {
  assert.deepEqual(motionContextVisibility(members, [muscle.sourceKey], lookup, {...view, regionIds:['leg']}), [muscle.sourceKey,bone.sourceKey]);
});
test('explicit isolation, hidden structures, layer-off and actual hard holds remain authoritative', () => {
  assert.deepEqual(motionContextVisibility(members, [], lookup, {...view,bones:false}), [muscle.sourceKey]);
  assert.deepEqual(motionContextVisibility(members, [], lookup, {...view,isolate:true}), [muscle.sourceKey]);
  assert.deepEqual(motionContextVisibility(members, [], lookup, {...view,hiddenSourceKeys:[bone.sourceKey]}), [muscle.sourceKey]);
  assert.deepEqual(motionContextVisibility(members, [], key => key===bone.sourceKey ? {...bone,hardHoldReasons:['held']} : lookup(key), view),[muscle.sourceKey]);
});
