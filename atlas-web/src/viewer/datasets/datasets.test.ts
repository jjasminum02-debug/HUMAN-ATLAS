import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {ResourceQueue} from '../wholeBody/resources.ts';
import {validateDataset,planLods,DATASET_BUDGET} from './schema.ts';
const tick=()=>new Promise(r=>setTimeout(r,5));
const dataset=JSON.parse(await readFile(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json',import.meta.url),'utf8'));
test('960 preserved instances, separate kinds, no rights/binding promotions',()=>{
 const d=validateDataset(dataset);assert.equal(d.instances.length,960);
 for(const [kind,n]of [['muscle_surface_or_part',509],['skeletal_surface',277],['musculoskeletal_accessory',174]]as const)assert.equal(d.instances.filter(i=>i.kind===kind).length,n);
 assert.equal(dataset.canonicalTargetCount,542);assert.equal(dataset.regionMembershipCount,563);
});
test('reject changed unit, duplicate instance, missing LOD, hold promotion and oversized chunk',()=>{
 for(const change of [(d:any)=>d.unit='mm',(d:any)=>d.instances.push(d.instances[0]),(d:any)=>d.instances[0].lods.detail.resource='missing',(d:any)=>d.instances[0].defaultLearnerVisible=true,(d:any)=>d.chunks[0].bytes=9*1024*1024]){const d=structuredClone(dataset);change(d);assert.throws(()=>validateDataset(d));}
});
test('all-detail demand retains every surface and stays within triangles and bytes',()=>{
 const d=validateDataset(dataset);const all=new Set(d.instances.map(i=>i.sourceKey));const plan=planLods(d,all,all);
 assert.equal(plan.choices.size,960);assert.ok(plan.triangles<=DATASET_BUDGET.triangles);assert.ok(plan.bytes<=DATASET_BUDGET.geometryBytes);
});
test('LRU evicts oldest unwanted only; twenty cycles stay bounded and release once',async()=>{
 const released:string[]=[];const q=new ResourceQueue(async(id)=>id,id=>released.push(id),()=>{},2,{maxBytes:3,measure:()=>1});
 for(let k=0;k<20;k++){q.demand([String(k)],['pin']);await tick();assert.ok(q.bytes<=3);assert.ok(q.loaded.has('pin'));}
 assert.ok(q.evictions>=18);q.dispose();q.dispose();assert.equal(q.bytes,0);assert.equal(new Set(released).size,released.length);
});
test('late cancelled decode is released; re-demand can subsequently load same key',async()=>{
 let resolve!: (v:string)=>void;let calls=0;const released:string[]=[];
 const q=new ResourceQueue(()=>++calls===1?new Promise<string>(r=>resolve=r):Promise.resolve('new'),v=>released.push(v),()=>{},1,{maxBytes:2,measure:()=>1});
 q.demand(['a']);await tick();q.demand([]);q.demand(['a']);resolve('old');await tick();await tick();assert.deepEqual(released,['old']);assert.equal(q.loaded.get('a'),'new');q.dispose();
});
test('oversized load fails once without retry loop, disposal cancels pending',async()=>{
 let calls=0;let signal:AbortSignal|undefined;const released:string[]=[];
 const q=new ResourceQueue(async(_,s)=>{calls++;signal=s;return 'x';},x=>released.push(x),()=>{},1,{maxBytes:1,measure:()=>2});
 q.demand(['x']);await tick();assert.equal(calls,1);assert.ok(q.failed.has('x'));assert.deepEqual(released,['x']);q.dispose();assert.equal(q.loaded.size,0);assert.ok(signal);
});
