import test from 'node:test';
import assert from 'node:assert/strict';
import {shouldFocusNerveSelection,observationFrameKeys,nerveCourseKeys,demandedStructureKeys} from './presentation.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type {BodyView} from '../wholeBody/contract.ts';
const nerve={names:{en:'nerve'},sourceKey:'nerve',kind:'nerve',side:'right',regionIds:['neck'],bounds:[[0,0,0],[1,1,1]],localDisplayEligible:true,defaultVisible:true,hardHoldReasons:[],sourceHiddenStatePreserved:{hideViewport:false},nerve:{poseId:'rest',muscleKeys:[],branchKeys:[]}} as unknown as RuntimeStructureRecord;
const base={region:null,selectedId:null,nerves:false,bones:true,muscles:true,poseId:'rest',dim:true,supplements:false} as BodyView;
const selected={...base,selectedId:'nerve',nerves:true};
test('one focus for selected visible nerve; layer, hidden, unsupported pose and repeated updates never steal camera',()=>{
 assert.equal(shouldFocusNerveSelection([nerve],base,selected),true);assert.equal(shouldFocusNerveSelection([nerve],selected,{...selected,highlightInnervation:false}),false);
 for(const next of [{...selected,nerves:false},{...selected,poseId:'moving'},{...selected,hiddenSourceKeys:['nerve']},{...selected,selectedPresentation:'hidden' as const}])assert.equal(shouldFocusNerveSelection([nerve],base,next),false);
 assert.equal(shouldFocusNerveSelection([{...nerve,hardHoldReasons:['hold']}],base,selected),false);
 assert.deepEqual(observationFrameKeys([nerve],selected),['nerve']);
});

test('registered branch course expands across region filters but respects side, hidden and static layer/pose',()=>{
 const child={...nerve,sourceKey:'child',regionIds:['leg'],nerve:{poseId:'rest',branchKeys:['nerve'],muscleKeys:[]}};
 const foreign={...child,sourceKey:'left',side:'left'};
 const parent={...nerve,nerve:{...nerve.nerve!,branchKeys:['child','left','missing']}};
 const rows=[parent,child,foreign];const view={...selected,regionIds:['neck']};
 assert.deepEqual(nerveCourseKeys(rows,view),['nerve','child']);assert.ok(demandedStructureKeys(rows,view).includes('child'));
 assert.deepEqual(nerveCourseKeys(rows,{...view,hiddenSourceKeys:['child']}),['nerve']);
 assert.deepEqual(nerveCourseKeys(rows,{...view,nerves:false}),[]);assert.deepEqual(nerveCourseKeys(rows,{...view,poseId:'moving'}),[]);
});
