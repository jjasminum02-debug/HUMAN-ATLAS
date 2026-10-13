import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {compilePlacementUnit,compilePlacementBatch,projectCompiledBatch,type CompilerInputs,type PlacementUnit} from './anchorCompiler.ts';
import {resolveAnchor} from './anchorAdapter.ts';
import {validateLearningPackage,type LearningPackage} from './learningPackage.ts';
const read=(path:string)=>JSON.parse(readFileSync(new URL('../../../../'+path,import.meta.url),'utf8'));
const doc=read('work/evidence/AT6/resume-r1/bilateral-rules-r9.json') as {units:PlacementUnit[];inputs:CompilerInputs;context:PlacementUnit['context']};
const get=(code:string,side='right')=>doc.units.find(u=>u.code===code&&u.side===side)!;
test('actual 22 source-addressed placements replay; raw concepts, AI provenance and independent side geometries remain distinct',async()=>{
  const batch=await compilePlacementBatch(doc.units,doc.inputs);assert.equal(doc.units.length,22);
  assert.equal(Object.values(batch.ledger.units).filter(u=>u.status==='passed').length,22);
  const p=await projectCompiledBatch(batch.ledger,doc.inputs,{...doc.context,motionActive:false});assert.equal(p.flatMap(p=>p.instances).length,22);
  for(const u of Object.values(batch.ledger.units)){assert.equal(u.assessment.precision,'educational_approximation');assert.equal(u.assessment.author,'ai');assert.equal(u.instance!.professorReview,'not_performed');assert.equal(u.assessment.rights.publicRedistribution,'held');assert.ok(u.assessment.landmarks.every(l=>l.modelIndicator?.observedSkinLandmark===false));}
  const pkg=read('atlas-data/acupoints/learner/lung-r7.json') as LearningPackage;validateLearningPackage(pkg,doc.context,read('atlas-data/acupoints/observation/catalog-r1.json'));
  assert.deepEqual(pkg.concepts,read('atlas-data/acupoints/learner/lung.json').concepts);assert.deepEqual(pkg.precisionCounts,{precise:0,educationalApproximation:22,unresolved:0});
  for(const code of ['LU1','LU5','LU7','LU9','LU11'])assert.notEqual(get(code).landmarks[0].sourceKey,get(code,'left').landmarks[0].sourceKey);
});
test('multiple native carrier references enforce rights, bytes, pose and side; no disconnected shared-seam substitution',async()=>{
  const u=get('LU3'),main=u.carrierId,ref=u.landmarks.find(l=>l.surface.carrierId&&l.surface.carrierId!==main)!.surface.carrierId!;
  for(const variant of ['bytes','side','pose','rights']){
    const inputs=structuredClone(doc.inputs);const c=inputs.carriers[ref];
    if(variant==='bytes')c.positions[0]+=.001;if(variant==='side')c.side='left';if(variant==='pose')c.poseId='deformed';if(variant==='rights')c.rights.localObservation='held';
    assert.equal((await compilePlacementUnit(u,inputs)).status,'failed',variant);
  }
  const bad=structuredClone(u);if(bad.rule.kind==='B-cun')bad.rule.path[1].carrierId='arm-left-0';assert.equal((await compilePlacementUnit(bad,doc.inputs)).status,'failed');
});
test('context-only observations validate real source binding but cannot establish a point; model indicators cannot assert observed skin',async()=>{
  const u=get('LU2'),inputs=structuredClone(doc.inputs);inputs.native[u.observedReferences![0].sourceKey].positions[0]+=.001;
  assert.equal((await compilePlacementUnit(u,inputs)).status,'failed');
  const bad=structuredClone(u);bad.landmarks=[];assert.equal((await compilePlacementUnit(bad,doc.inputs)).status,'failed');
  const claim=structuredClone(u);claim.landmarks[0].modelIndicator!.observedSkinLandmark=true as false;
  assert.equal((await compilePlacementUnit(claim,doc.inputs)).status,'failed');
});
test('actual nail side-edge detour is rejected; proximal nail-base corner and calibrated F-cun result progress proximally',async()=>{
  const before=read('work/evidence/AT6/resume-r1/bilateral-rules-r4.json');
  for(const side of ['right','left']){
    const rejected=before.units.find((u:PlacementUnit)=>u.code==='LU11'&&u.side===side);assert.match((await compilePlacementUnit(rejected,before.inputs)).errors.join(),/opposes annotated direction/);
    const u=get('LU11',side),r=await compilePlacementUnit(u,doc.inputs);assert.equal(r.status,'passed');const c=doc.inputs.carriers[u.carrierId];
    const anchor=(a:PlacementUnit['landmarks'][number]['surface'])=>resolveAnchor(c,{...r.instance!,...a}).position;
    const start=anchor(u.landmarks[0].surface),end=anchor(u.landmarks[1].surface),result=resolveAnchor(c,r.instance!).position;
    assert.ok(result.y>start.y);assert.ok(result.clone().sub(start).dot(end.clone().sub(start))>0);assert.equal(u.landmarks[0].native.triangle,151);
    const native=(id:string)=>{const l=u.landmarks.find(l=>l.id===id)!;return resolveAnchor(doc.inputs.native[l.sourceKey],l.native).position;};
    assert.equal(u.rule.kind,'F-cun');if(u.rule.kind==='F-cun'){
      assert.equal(u.rule.nativeDirections!.length,2);
      for(const d of u.rule.nativeDirections!)assert.ok(result.clone().sub(native(d.origin)).dot(native(d.to).sub(native(d.from)))>0);
    }
    const coarse=read('work/evidence/AT6/resume-r1/bilateral-rules-r5-native-rejected.json');
    assert.match((await compilePlacementUnit(coarse.units.find((u:PlacementUnit)=>u.code==='LU11'&&u.side===side),coarse.inputs)).errors.join(),/opposes native anatomical direction/);
  }
});
test('failed unit correction resumes independently and unchanged successful twenty locations remain byte-identical',async()=>{
  const before=read('work/evidence/AT6/resume-r1/bilateral-rules-r4.json');const first=await compilePlacementBatch(before.units,before.inputs);
  assert.equal(Object.values(first.ledger.units).filter(u=>u.status==='failed').length,2);
  const corrected=read('work/evidence/AT6/resume-r1/bilateral-rules-r6.json');const second=await compilePlacementBatch(corrected.units,corrected.inputs,first.ledger);assert.equal(second.executed.length,2);assert.equal(second.reused.length,20);
  for(const id of second.reused)assert.deepEqual(second.ledger.units[id],first.ledger.units[id]);
  assert.equal(second.history.length,2);assert.ok(second.history.every(u=>u.status==='failed'));
});
test('B-cun measures an annotated native endpoint axis, not a circumferential carrier detour',async()=>{
  for(const u of doc.units.filter(u=>u.rule.kind==='B-cun')){
    const r=u.rule;if(r.kind!=='B-cun')continue;assert.ok(r.measurementAxis);
    const compiled=await compilePlacementUnit(u,doc.inputs);assert.equal(compiled.status,'passed');
    const l=(id:string)=>u.landmarks.find(l=>l.id===id)!;
    const n=(id:string)=>resolveAnchor(doc.inputs.native[l(id).sourceKey],l(id).native).position;
    const s=(id:string)=>{const a=l(id).surface,c=doc.inputs.carriers[a.carrierId??u.carrierId];return resolveAnchor(c,{...compiled.instance!,...a,carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256}).position;};
    const axis=n(r.measurementAxis!.to).sub(n(r.measurementAxis!.from)).normalize(),origin=s(r.from);
    const q=resolveAnchor(doc.inputs.carriers[u.carrierId],compiled.instance!).position;
    assert.ok(Math.abs(q.clone().sub(origin).dot(axis)/s(r.to).sub(origin).dot(axis)-r.value/r.totalCun)<1e-9);
  }
  const u=get('LU8');assert.equal(u.carrierId,'arm-right-0');
  const inputs=structuredClone(doc.inputs);delete inputs.evidence.find(e=>e.id===(u.rule as {evidenceId:string}).evidenceId)!.measurementAxis;
  assert.match((await compilePlacementUnit(u,inputs)).errors.join(),/lacks matching proportion evidence/);
  const bad=structuredClone(u);if(bad.rule.kind==='B-cun')bad.rule.measurementAxis={from:bad.rule.to,to:bad.rule.from};
  assert.match((await compilePlacementUnit(bad,doc.inputs)).errors.join(),/opposes proportional endpoints/);
  for(const side of ['right','left']){
    const positions=[];for(const code of ['LU9','LU8','LU7']){const u=get(code,side),r=await compilePlacementUnit(u,doc.inputs);positions.push(resolveAnchor(doc.inputs.carriers[u.carrierId],r.instance!).position.y);}
    assert.ok(positions[0]<positions[1]&&positions[1]<positions[2]);
  }
});
test('a measured LU8 plane crossing on the existing AT3 chunk cannot export with the old wrist target identity',async()=>{
  const before=read('work/evidence/AT6/resume-r1/bilateral-rules-r8.json'),first=await compilePlacementBatch(before.units,before.inputs);
  assert.equal(Object.values(first.ledger.units).filter(u=>u.status==='failed').length,2);
  const next=await compilePlacementBatch(doc.units,doc.inputs,first.ledger);assert.equal(next.reused.length,20);assert.equal(next.executed.length,2);
  for(const id of next.reused)assert.deepEqual(next.ledger.units[id],first.ledger.units[id]);
});
