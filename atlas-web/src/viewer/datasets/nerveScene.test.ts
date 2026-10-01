import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {loadNerveAssets} from '../../../plugins/nerveAssets.ts';
import {composeNerveScene} from './nerveScene.ts';
import {demandedStructureKeys,innervationHighlightKeys} from './presentation.ts';
import {validateNerveRegistry} from '../../domain/nerveContract.ts';
import type {BodyView} from '../wholeBody/contract.ts';
const root=fileURLToPath(new URL('../../../../',import.meta.url));
const sha=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function glb(b:Buffer){
 const size=b.readUInt32LE(12);const doc=JSON.parse(b.subarray(20,20+size).toString());const binary=b.subarray(28+size);
 return {doc,accessor:(id:number)=>{const a=doc.accessors[id],v=doc.bufferViews[a.bufferView];const bytes=a.componentType===5126||a.componentType===5125?4:2;return binary.subarray((v.byteOffset??0)+(a.byteOffset??0),(v.byteOffset??0)+(a.byteOffset??0)+a.count*(a.type==='VEC3'?3:1)*bytes);}};
}
test('all six original Curve surfaces: pinned files, topology, finite positions/normals, index bounds and pair symmetry',async()=>{
 const x=await loadNerveAssets(root);assert.equal(x.manifest.objects.length,6);assert.equal(x.registry.instances.filter(n=>n.localSelection==='unsupported').length,2);
 const evaluated=JSON.parse(await readFile(root+'work/evidence/T63/evaluated-surfaces.json','utf8'));
 assert.equal(evaluated.scriptsAutoExecute,false);assert.equal(evaluated.sourceModified,false);assert.equal(evaluated.sourceFrame,0);
 const world=new Map<string,number[]>();
 for(const o of x.manifest.objects){
  const b=await readFile(root+o.path);assert.equal(sha(b),o.sha256);const g=glb(b),p=g.doc.meshes[0].primitives[0];
  const positions=g.accessor(p.attributes.POSITION),normals=g.accessor(p.attributes.NORMAL),indices=g.accessor(p.indices);
  const count=positions.length/12;const component=g.doc.accessors[p.indices].componentType;const step=component===5123?2:4;
  const u32=Buffer.alloc(indices.length/step*4);for(let i=0;i<indices.length/step;i++){const id=step===2?indices.readUInt16LE(i*step):indices.readUInt32LE(i*step);assert.ok(id<count);u32.writeUInt32LE(id,i*4);}
  assert.equal(sha(Buffer.concat([positions,normals,u32])),o.topologySha256);
  const n=x.registry.instances.find(n=>n.id===o.instanceId)!;
  for(let i=0;i<count;i++){
   const p=[0,4,8].map(j=>positions.readFloatLE(i*12+j));const normal=[0,4,8].map(j=>normals.readFloatLE(i*12+j));
   assert.ok(p.every(Number.isFinite)&&normal.every(Number.isFinite));assert.ok(Math.abs(Math.hypot(...normal)-1)<1e-5);
   assert.ok(n.side==='left'?p[0]>0:p[0]<0);
  }
  const center=[0,4,8].map(j=>Array.from({length:count},(_,i)=>positions.readFloatLE(i*12+j)).reduce((a,b)=>a+b,0)/count);world.set(o.name,center);
  const row=evaluated.rows.find((r:any)=>r.instanceId===o.instanceId);assert.equal(row.modifiers,0);assert.equal(row.constraints,0);assert.equal(row.animationData,false);assert.equal(row.curve.bevelDepth>0,true);
 }
 for(const [name,p] of world)if(name.endsWith('.l')){const r=world.get(name.replace(/\.l$/,'.r'))!;assert.ok(Math.hypot(p[0]+r[0],p[1]-r[1],p[2]-r[2])<1e-5);}
 const chunk=glb(await readFile(x.files[0].path));assert.equal(chunk.doc.nodes.length,6);
 for(const node of chunk.doc.nodes){const original=glb(await readFile(root+x.manifest.objects.find(o=>o.sourceKey===node.name)!.path));const a=chunk.doc.meshes[node.mesh].primitives[0],b=original.doc.meshes[0].primitives[0];assert.deepEqual(chunk.accessor(a.attributes.POSITION),original.accessor(b.attributes.POSITION));assert.deepEqual(chunk.accessor(a.attributes.NORMAL),original.accessor(b.attributes.NORMAL));assert.deepEqual(chunk.accessor(a.indices),original.accessor(b.indices));}
});
test('geometry promotion rejects missing frame proof, wrong pose and fabricated side',async()=>{
 const x=await loadNerveAssets(root);
 for(const mutate of [(r:any)=>r.instances[0].geometry.evidenceIds=[],(r:any)=>r.instances[0].geometry.validatedPoseIds=['walking'],(r:any)=>r.instances[0].side='right']){
  const r=structuredClone(x.registry);mutate(r);assert.throws(()=>validateNerveRegistry(r));
 }
});
test('shared presentation gates layers/pose/region/hidden before motor highlights, preserves existing source routes',async()=>{
 const x=await loadNerveAssets(root);
 const runtime=JSON.parse(await readFile(root+'work/evidence/T63/browser/runtime.json','utf8'));
 const dataset=JSON.parse(await readFile(root+'work/evidence/T63/browser/dataset.json','utf8'));
 const nerveKeys=new Set(x.manifest.objects.map(o=>o.sourceKey));
 const base={...dataset,instances:dataset.instances.filter((i:any)=>!nerveKeys.has(i.sourceKey)),chunks:dataset.chunks.filter((c:any)=>!x.files.some(f=>f.id===c.id))};
 const baseRuntime={...runtime,objects:runtime.objects.filter((r:any)=>!nerveKeys.has(r.sourceKey))};
 const combined=composeNerveScene(base,baseRuntime,x.manifest,x.registry,x.dataset,x.rights,'a'.repeat(64),'b'.repeat(64));
 const rows=combined.integration.objects;const deep=rows.find(r=>r.kind==='nerve'&&r.names.en==='Deep fibular nerve'&&r.side==='left')!;
 const view:BodyView={region:null,regionIds:['leg'],bones:true,muscles:true,nerves:true,poseId:deep.nerve!.poseId,selectedId:deep.sourceKey,dim:true,supplements:false,highlightInnervation:true};
 const keys=(v:BodyView)=>new Set(demandedStructureKeys(rows,v));
 assert.equal(keys(view).has(deep.sourceKey),true);assert.deepEqual(innervationHighlightKeys(rows,view,keys(view)),deep.nerve!.muscleKeys);
 for(const v of [{...view,nerves:false},{...view,poseId:'unsupported-motion'},{...view,regionIds:['head']},{...view,hiddenSourceKeys:[deep.sourceKey]}]){assert.equal(keys(v).has(deep.sourceKey),false);assert.deepEqual(innervationHighlightKeys(rows,v,keys(v)),[]);}
 for(const v of [{...view,muscles:false},{...view,hiddenSourceKeys:deep.nerve!.muscleKeys},{...view,highlightInnervation:false},{...view,isolate:true}])assert.deepEqual(innervationHighlightKeys(rows,v,keys(v)),[]);
 assert.deepEqual(rows.filter(r=>r.kind!=='nerve').map(r=>[r.sourceKey,r.haConceptId,r.targetRoutes]),baseRuntime.objects.map((r:any)=>[r.sourceKey,r.haConceptId,r.targetRoutes]));
 const bad=structuredClone(x.manifest);bad.objects[0].bounds[0][0]=-1;assert.throws(()=>composeNerveScene(base,baseRuntime,bad,x.registry,x.dataset,x.rights,'a'.repeat(64),'b'.repeat(64)));
});
