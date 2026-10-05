import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {loadNerveAssets} from '../../../plugins/nerveAssets.ts';
import {assessMotionCapability, type MotionLearningBundle} from '../../domain/motionLearning.ts';
const root=fileURLToPath(new URL('../../../../',import.meta.url));
const sha=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function glb(b:Buffer){
 const size=b.readUInt32LE(12),doc=JSON.parse(b.subarray(20,20+size).toString()),binary=b.subarray(28+size);
 return {doc,accessor:(id:number)=>{const a=doc.accessors[id],v=doc.bufferViews[a.bufferView],step=a.componentType===5123?2:4;return binary.subarray((v.byteOffset??0)+(a.byteOffset??0),(v.byteOffset??0)+(a.byteOffset??0)+a.count*(a.type==='VEC3'?3:1)*step);}};
}
test('T66 all native nerve resources retain finite unit-normal topology, source side, frame, rights and bounded native overview',async()=>{
 const x=await loadNerveAssets(root);assert.equal(x.manifest.objects.length,195);
 const proof=JSON.parse(await readFile(root+'work/evidence/T66/implementation-2026-10-02/nerve-evaluated-surfaces.json','utf8'));
 const by=new Map<string,any>(proof.rows.map((r:any)=>[r.sourceKey,r]));
 const packed=JSON.parse(await readFile(root+x.manifest.datasetPath,'utf8'));assert.equal(packed.metrics.overviewTriangles,177840);assert.ok(packed.metrics.overviewBytes<4*1024*1024);
 for(const o of x.manifest.objects){
  const n=x.registry.instances.find(n=>n.id===o.instanceId)!;assert.equal(n.localSelection,'verified_geometry');assert.equal(n.sourceOnly,true);assert.equal(n.humanReview,'not_performed');assert.equal(n.publicRedistribution,'held');assert.equal(n.geometry!.validatedPoseIds.length,1);
  const b=await readFile(root+o.path);assert.equal(sha(b),o.sha256);const g=glb(b),p=g.doc.meshes[0].primitives[0],positions=g.accessor(p.attributes.POSITION),normals=g.accessor(p.attributes.NORMAL),indices=g.accessor(p.indices),count=positions.length/12;
  const step=g.doc.accessors[p.indices].componentType===5123?2:4,u32=Buffer.alloc(indices.length/step*4);
  for(let j=0;j<indices.length/step;j++){const id=step===2?indices.readUInt16LE(j*step):indices.readUInt32LE(j*step);assert.ok(id<count);u32.writeUInt32LE(id,j*4);}
  assert.equal(sha(Buffer.concat([positions,normals,u32])),o.topologySha256);
  for(let i=0;i<count;i++){
   const p=[0,4,8].map(j=>positions.readFloatLE(i*12+j)),normal=[0,4,8].map(j=>normals.readFloatLE(i*12+j));assert.ok(p.every(Number.isFinite)&&normal.every(Number.isFinite));assert.ok(Math.abs(Math.hypot(...normal)-1)<1e-5);assert.ok(n.side==='left'?p[0]>0:p[0]<0);
  }
  const row=by.get(o.sourceKey)!;assert.equal(proof.sourceFrame,0);assert.equal(row.modifiers,0);assert.equal(row.constraints,0);assert.equal(row.animationData,false);
  assert.ok(row.overview);assert.ok(row.overview.sampledSymmetricSurfaceErrorMeters<=.0015,'native overview has explicit sampled 1.5mm distance bound');
  assert.equal(row.overview.nativeControlPointsPreserved,true);assert.equal(row.overview.nativeRadiusPreserved,true);assert.equal(row.overview.nativeSplineCountPreserved,true);
 }
});
test('T66 typed bones share the validated clip and cannot accept a muscle, wrong side or nonmoving primary binding',async()=>{
 const b=JSON.parse(await readFile(root+'atlas-data/motion/motion-learning.json','utf8')) as MotionLearningBundle;
 const actions=b.muscleActions.filter(a=>a.subjectKind==='bone');
 // Preserve original source-bone contracts while allowing later verified family bindings.
 assert.ok(actions.length >= 199);
 assert.equal(new Set(actions.map(a=>a.id)).size,actions.length);
 for(const a of actions){
  const d=b.motionDefinitions.find(d=>d.actionId===a.id)!,asset=b.motionAssets.find(s=>s.motionDefinitionId===d.id)!;
  assert.equal(assessMotionCapability(a,d,asset).hasTechnicallyCompatibleClip,true);
  const primary=asset.sourceBinding!.members.find(m=>m.sourceKey===asset.sourceBinding!.subjectSourceKey)!;assert.ok(['moving_structure','fixed_structure'].includes(primary.role));
  assert.ok(primary.role==='moving_structure'?d.movingStructureIds.includes(d.instanceId):d.fixedStructureIds.includes(d.instanceId));
  assert.equal(assessMotionCapability({...a,subjectKind:'muscle'},d,asset).hasTechnicallyCompatibleClip,false);
  assert.equal(assessMotionCapability(a,d,{...asset,staticBinding:{...asset.staticBinding,side:d.side==='left'?'right':'left'}}).hasTechnicallyCompatibleClip,false);
  const bad=structuredClone(asset);bad.sourceBinding!.members.find(m=>m.sourceKey===bad.sourceBinding!.subjectSourceKey)!.role='deforming_muscle_surface';assert.equal(assessMotionCapability(a,d,bad).hasTechnicallyCompatibleClip,false);
 }
});
