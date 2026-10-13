import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateLearningPackage, type LearningPackage } from './learningPackage.ts';
import { resolveAnchor, validateCarrier, verifyCarrierHash } from './anchorAdapter.ts';
import { decodeCarrierChunk, type CarrierManifest } from './carrierSample.ts';
const p=JSON.parse(readFileSync(new URL('../../../../atlas-data/acupoints/learner/lung.json',import.meta.url),'utf8')) as LearningPackage;
const catalog=JSON.parse(readFileSync(new URL('../../../../atlas-data/acupoints/observation/catalog-r1.json',import.meta.url),'utf8'));
const context={datasetRevision:p.datasetRevision,frameId:p.frameId,unit:'m',poseId:p.poseId};
test('actual 11 concepts/22 unavailable locations are distinct; no proposal or fixture export',()=>{
  validateLearningPackage(p,context,catalog);assert.equal(p.concepts.length,11);assert.equal(p.availability.length,22);assert.deepEqual(p.projections,[]);
  assert.equal(p.concepts[8].nameKo,'태연');assert.equal(p.concepts[10].nameKo,'소상');
  assert.deepEqual(p.precisionCounts,{precise:0,educationalApproximation:0,unresolved:22});
});
test('stale pose/dataset/frame, fake availability, wrong name and invented count fail closed',()=>{
  for(const change of [{datasetRevision:'new'},{poseId:'deformed'},{frameId:'wrong'},{unit:'mm'}])assert.throws(()=>validateLearningPackage(p,{...context,...change},catalog));
  const q=structuredClone(p);q.availability[0].display='educational_approximation';assert.throws(()=>validateLearningPackage(q,context,catalog));
  q.availability[0]=structuredClone(p.availability[0]);q.precisionCounts.unresolved=0;assert.throws(()=>validateLearningPackage(q,context,catalog));
  const n=structuredClone(p);n.concepts[8].nameKo='소상';assert.throws(()=>validateLearningPackage(n,context,catalog));
  const d=structuredClone(p);d.availability[1]=structuredClone(d.availability[0]);assert.throws(()=>validateLearningPackage(d,context,catalog));
});
test('fixture cannot bypass availability/count checking',()=>{
  const q=structuredClone(p);q.projections=[{schemaVersion:2,usage:'local_learner_eligible',...context,unit:'m',carrierId:'fake',carrierHash:'0'.repeat(64),carrierRevision:'r1',instances:[{code:'LU1',side:'right',triangle:0,barycentric:[1,0,0],originScope:'technical_fixture',precision:'educational_approximation',author:'ai',inputSha256:'0'.repeat(64),professorReview:'not_performed',publicRedistribution:'held'}]}] as unknown as LearningPackage['projections'];
  assert.throws(()=>validateLearningPackage(q,context,catalog));
});
test('actual shared trunk carrier replays bilateral addresses without reflection and rejects swapped side',async()=>{
  const m=JSON.parse(readFileSync(new URL('../../../../atlas-data/acupoints/carriers/education-r1/manifest.json',import.meta.url),'utf8')) as CarrierManifest;
  const chunk=m.chunks.find(c=>c.id==='trunk-2')!;
  const raw=readFileSync(new URL('../../../../atlas-data/acupoints/carriers/education-r1/'+chunk.file,import.meta.url));
  const {carrier:c}=await decodeCarrierChunk(m,chunk,raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength));
  validateCarrier(c,context);await verifyCarrierHash(c);assert.equal(c.side,'midline');
  for(const side of ['right','left'] as const){const face=Array.from({length:c.indices.length/3},(_,i)=>i).find(i=>c.indices.slice(i*3,i*3+3).every(v=>side==='right'?c.positions[v*3]<0:c.positions[v*3]>0))!;
    const a={carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,frameId:c.frameId,unit:c.unit,poseId:c.poseId,side,triangle:face,barycentric:[1/3,1/3,1/3] as [number,number,number]};
    assert.equal(resolveAnchor(c,a).position.x<0,side==='right');assert.throws(()=>resolveAnchor(c,{...a,side:side==='right'?'left':'right'}));}
});

test('lossless observation delivery replays actual LI/TE source bytes and coordinates',async()=>{
 const {decodeLearningDocument}=await import('./learningPackage.ts');const {gunzipSync}=await import('node:zlib');
 for(const channel of ['li','te']){
  const bytes=readFileSync(new URL(`../../../../atlas-data/acupoints/observation/${channel}-context-r1.bin`,import.meta.url));const raw=readFileSync(new URL(`../../../../work/evidence/AT8/2026-10-13-r1/delivery-r19/${channel}-context-r1.json`,import.meta.url));assert.deepEqual(gunzipSync(bytes),raw);const decoded=await decodeLearningDocument(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),true);assert.deepEqual(decoded.document,JSON.parse(raw.toString()));assert.equal(decoded.decodedBytes,raw.length);
 }
});
