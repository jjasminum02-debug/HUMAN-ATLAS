import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {compilePlacementBatch,projectCompiledBatch,type CompilerInputs,type PlacementUnit} from './anchorCompiler.ts';
import {validateLearningPackage} from './learningPackage.ts';import {resolveAnchor} from './anchorAdapter.ts';
import {decodeCarrierChunk,validateCarrierManifest} from './carrierSample.ts';
const read=(p:string)=>JSON.parse(readFileSync(new URL('../../../../'+p,import.meta.url),'utf8'));
const e='work/evidence/AT8/2026-10-13-r1/',doc=read(e+'rules-r19.json') as {units:PlacementUnit[];inputs:CompilerInputs;context:PlacementUnit['context']};
const catalog=read('atlas-data/acupoints/observation/catalog-r1.json');
test('actual LI/TE 43 concepts /86 decisions: 86 native compiler positions, zero precise or fixtures; LU remains22',async()=>{
 const batch=await compilePlacementBatch(doc.units,doc.inputs);const projected=await projectCompiledBatch(batch.ledger,doc.inputs,{...doc.context,motionActive:false});assert.equal(projected.flatMap(p=>p.instances).length,86);
 const packages=['li','te'].map(c=>read(`atlas-data/acupoints/learner/${c}-r1.json`));for(const p of packages)validateLearningPackage(p,doc.context,catalog);
 assert.equal(packages.reduce((n,p)=>n+p.concepts.length,0),43);assert.equal(packages.reduce((n,p)=>n+p.availability.length,0),86);
 assert.equal(packages.reduce((n,p)=>n+p.precisionCounts.unresolved,0),0);assert.equal(packages.reduce((n,p)=>n+p.precisionCounts.precise,0),0);
 const final=packages.flatMap(p=>p.projections.flatMap((q:{instances:{code:string;side:string}[]})=>q.instances)).map(i=>`${i.code}:${i.side}`).sort();assert.deepEqual(final,projected.flatMap(p=>p.instances).map(i=>`${i.code}:${i.side}`).sort());
 assert.ok(projected.flatMap(p=>p.instances).every(i=>i.author==='ai'&&i.originScope==='real_input'&&i.publicRedistribution==='held'&&i.professorReview==='not_performed'));
 validateLearningPackage(read('atlas-data/acupoints/learner/lung-r7.json'),doc.context,catalog);
});
test('lossless carrier subset preserves every successful world point and supported path; no hole fill',()=>{
 const before=read(e+'rules-r17.json'),old=read(e+'compiler-r17/ledger.json'),now=read(e+'compiler-r18/ledger.json'),packed=read(e+'rules-r18.json');
 for(const [id,u] of Object.entries(now.units) as [string,{status:string;instance:PlacementUnit&{carrierId:string}}][])if(u.status==='passed'){
  assert.equal(old.units[id].status,'passed');const a=resolveAnchor(before.inputs.carriers[old.units[id].instance.carrierId],old.units[id].instance),b=resolveAnchor(packed.inputs.carriers[u.instance.carrierId],u.instance as never);assert.deepEqual(a.position.toArray(),b.position.toArray(),id);assert.deepEqual(a.normal.toArray(),b.normal.toArray(),id);
 }
 assert.ok(read(e+'carrier-compaction-r18.json').every((a:{fillTriangles:number;worldFloat32AndReferenceBitsUnchanged:boolean})=>a.fillTriangles===0&&a.worldFloat32AndReferenceBitsUnchanged));
});
test('encoded compact chunks and metadata replay actual file bytes; sparse topology shares one registry and original rights',async()=>{
 const m=read('atlas-data/acupoints/carriers/upper-yang-final-AT8-r18/manifest.json');validateCarrierManifest(m,doc.context);
 const runtime=read('atlas-data/acupoints/carriers/runtime-registry-r1/upper-yang-final-AT8-r18.json');validateCarrierManifest(runtime,doc.context);assert.deepEqual(runtime.rights,m.rights);
 for(const c of m.chunks){const b=readFileSync(new URL('../../../../atlas-data/acupoints/carriers/upper-yang-final-AT8-r18/'+c.file,import.meta.url));const sample=await decodeCarrierChunk(runtime,c,b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));assert.deepEqual(sample.carrier.positions,doc.inputs.carriers[c.id].positions);assert.deepEqual(sample.carrier.indices,doc.inputs.carriers[c.id].indices);}
});
test('resume reuses all final verified units; raw source text and earlier rejected candidate survive',async()=>{
 const previous=read(e+'compiler-r19/ledger.json');const result=await compilePlacementBatch(doc.units,doc.inputs,previous);assert.deepEqual(result.executed,[]);assert.equal(result.reused.length,86);
 for(const u of doc.units)assert.equal(result.ledger.units[u.id].originalText,u.originalText);
 const rejected=read(e+'compiler-r15/ledger.json');assert.equal(rejected.units['LI19-right'].status,'failed');assert.equal(read(e+'rules-r12.json').units.find((u:PlacementUnit)=>u.id==='TE7-left').code,'TE7');
});
