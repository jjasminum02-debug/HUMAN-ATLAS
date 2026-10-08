import test from 'node:test';
import assert from 'node:assert/strict';
import {nerveLearningTargets} from './nerveRelations.ts';
const rows=['empty','text','play','wrong','held'].map((sourceKey,i)=>({sourceKey,kind:'muscle',side:i===3?'left':'right',localDisplayEligible:i!==4,inspectionEligible:true}));
const relation={nerveKey:'nerve',targetSourceKeys:rows.map(r=>r.sourceKey),targetSide:null,scope:'concept'};
const action=(id:string,learningIntent:string,candidate?:unknown)=>({id,learningIntent,candidate,text:{explanation:'검증된 설명'}});
test('playable actions, then real text, then relation-only; exact side and deduplicated source/actions',()=>{
 const result=nerveLearningTargets([relation,relation],key=>rows.find(r=>r.sourceKey===key),row=>row.sourceKey==='play'?[action('a','muscle_action',{}),action('a','muscle_action',{})]:row.sourceKey==='text'?[action('t','text_only')]:[action('p','posture_observation',{})],'right');
 assert.deepEqual(result.map(r=>r.row.sourceKey),['play','text','empty']);assert.equal(result[0].actions.length,1);assert.equal(result[2].actions.length,0);
});
test('blank content, posture and bone motion cannot become nerve-linked muscle actions',()=>{
 const result=nerveLearningTargets([relation],key=>rows.find(r=>r.sourceKey===key),()=>[action('p','posture_observation',{}),action('b','bone_motion',{}),{...action('blank','text_only'),text:{explanation:'  '}}],'right');
 assert.equal(result.length,3);assert.ok(result.every(r=>r.actions.length===0));
});
