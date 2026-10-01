import {test} from 'node:test';
import assert from 'node:assert/strict';
import {framingRecords} from './framing.ts';
import type {RuntimeStructureRecord} from './integration.ts';
import type {BodyView} from '../wholeBody/contract.ts';
const view:BodyView={region:null,bones:true,muscles:true,supplements:false,selectedId:null,dim:true};
const row=(sourceKey:string,extra:Partial<RuntimeStructureRecord>={}):RuntimeStructureRecord=>({sourceKey,localDisplayEligible:true,defaultVisible:true,kind:'muscle',regionIds:['neck'],names:{en:'Neck muscle',koModern:'',koTraditional:''},...extra} as RuntimeStructureRecord);
test('neck framing retains cervical bones and neck muscles without the full cross-regional rotator group',()=>{
 const bone=row('c3',{kind:'bone'}), muscle=row('neck'), wholeGroup=row('rotators',{regionIds:['back','neck'],names:{en:'Rotatores',koModern:'돌림근',koTraditional:'회선근'}});
 assert.deepEqual(framingRecords([bone,muscle,wholeGroup],view,['neck']),[bone,muscle]);
 assert.deepEqual(framingRecords([bone,muscle,wholeGroup],view,[]),[bone,muscle,wholeGroup]);
 assert.deepEqual(framingRecords([wholeGroup],view,['back']),[wholeGroup]);
});
test('invisible unregistered supplement cannot change default camera framing; explicit eligible inspection stays independent',()=>{
 const visible=row('visible'), inspection=row('inspection',{defaultVisible:false}), held=row('held',{localDisplayEligible:false});
 assert.deepEqual(framingRecords([visible,inspection,held],view,[]),[visible]);
 assert.deepEqual(framingRecords([visible,inspection,held],{...view,selectedId:'inspection'},[]),[visible,inspection]);
 assert.deepEqual(framingRecords([visible,inspection,held],{...view,selectedId:'held'},[]),[visible]);
 assert.deepEqual(framingRecords([visible,inspection],{...view,hiddenSourceKeys:['visible'],muscles:false,selectedId:'inspection'},[]),[]);
});
