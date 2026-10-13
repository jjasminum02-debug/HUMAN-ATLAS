import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compilerFixture } from '../../../scripts/anchorCompilerFixtures.ts';
import { compilePlacementUnit, compilePlacementBatch, projectCompiledBatch } from './anchorCompiler.ts';
import { anchorBinding, projectLearnerInstances, resolveLearnerProjection } from './placementPolicy.ts';
import { migratePlacementDocument, sha256 } from './placementMigration.ts';
import { productInstances, type PointInstance } from './schema.ts';
import { resolveAnchor } from './anchorAdapter.ts';

for(const kind of ['landmark','B-cun','F-cun','midline'] as const)test(`${kind}: explicit input replays deterministically; fixture never exports`,async()=>{
  const f=await compilerFixture(kind),a=await compilePlacementUnit(f.unit,f.inputs),b=await compilePlacementUnit(f.unit,f.inputs);
  assert.equal(a.status,'passed');assert.deepEqual(a,b);assert.equal(a.assessment.author,'ai');
  assert.equal(a.assessment.precision,'educational_approximation');assert.equal(productInstances(f.carrier,[a.instance!]).length,0);
  const p=await projectCompiledBatch({version:2,compilerVersion:a.assessment.compilerVersion,units:{[a.id]:a}},f.inputs,{...f.context,motionActive:false});
  assert.equal(p.length,0);
  if(kind==='B-cun')assert.ok(Math.abs(resolveAnchor(f.carrier,a.instance!).position.x-(-.2+.1/3))<1e-9);
  if(kind==='F-cun')assert.ok(Math.abs(resolveAnchor(f.carrier,a.instance!).position.distanceTo(resolveAnchor(f.carrier,{...a.instance!,triangle:0,barycentric:[1,0,0]}).position)-.01)<1e-9);
  if(kind==='midline')assert.equal(resolveAnchor(f.carrier,a.instance!).position.x,0);
});

test('policy contract: verified AI can qualify without professor/public approval; authorship cannot be erased',async()=>{
  const f=await compilerFixture('landmark');
  assert.equal((await compilePlacementUnit({...f.unit,scope:'real_input'},f.inputs)).status,'failed');
  const fixture=await compilePlacementUnit(f.unit,f.inputs),renamed=structuredClone(fixture.instance!);renamed.assessment!.scope='real_input';
  assert.equal(productInstances(f.carrier,[renamed]).length,0);
  // Contract simulation only. This record is never saved or exported as actual human data.
  const result=await compilePlacementUnit({...f.unit,scope:'real_input'},{...f.inputs,domain:'real_input'}),i=result.instance!;
  assert.equal(productInstances(f.carrier,[i]).length,1);
  const projection=await projectLearnerInstances(f.carrier,[i],{...f.context,motionActive:false});
  const replay=await resolveLearnerProjection(f.carrier,projection,{...f.context,motionActive:false});
  assert.deepEqual(replay[0].position.toArray(),resolveAnchor(f.carrier,i).position.toArray());
  assert.equal(replay[0].point.author,'ai');assert.equal(replay[0].point.publicRedistribution,'held');
  await assert.rejects(resolveLearnerProjection(f.carrier,{...projection,poseId:'flexed'},{...f.context,motionActive:false}),/Stale/);
  assert.equal(i.aiProposal,true);assert.equal(i.assessment!.author,'ai');assert.equal(i.professorReview,'not_performed');
  i.assessment!.author='human';assert.equal(productInstances(f.carrier,[i]).length,0);
  i.assessment!.author='ai';i.barycentric=[0,1,0];assert.equal(productInstances(f.carrier,[i]).length,0);
});

test('wrong side/frame/pose/unit/hash and altered native bytes isolate individually',async()=>{
  const f=await compilerFixture();
  for(const patch of [{side:'left'},{context:{...f.context,frameId:'wrong'}},{context:{...f.context,poseId:'flexed'}},{context:{...f.context,unit:'mm'}}]) {
    const r=await compilePlacementUnit({...f.unit,...patch} as typeof f.unit,f.inputs);assert.equal(r.status,'failed');assert.equal(r.instance,null);
  }
  for(const native of [false,true]) {
    const bad=structuredClone(f.inputs);const c=native?bad.native['fixture-native']:bad.carriers[f.carrier.id];c.positions[0]+=.01;
    const r=await compilePlacementUnit(f.unit,bad);assert.equal(r.status,'failed');assert.equal(r.assessment.technical,'failed');assert.match(r.errors.join(),/hash/);
  }
  const stale=structuredClone(f.unit);stale.landmarks[0].native.carrierHash='0'.repeat(64);
  assert.equal((await compilePlacementUnit(stale,f.inputs)).status,'failed');
});

test('bounds, nearest, unresolved, mirrored and meaningless landmarks never approve',async()=>{
  const f=await compilerFixture();
  for(const kind of ['bounds','nearest','unresolved'] as const)assert.equal((await compilePlacementUnit({...f.unit,rule:{kind}},f.inputs)).status,'failed');
  for(const acquisition of ['bounds','nearest','mirror','unresolved'] as const) {
    const u=structuredClone(f.unit);u.landmarks[0].acquisition=acquisition;assert.equal((await compilePlacementUnit(u,f.inputs)).status,'failed');
  }
  const u=structuredClone(f.unit);u.landmarks[0].anatomy=' ';assert.equal((await compilePlacementUnit(u,f.inputs)).status,'failed');
});

test('proportion evidence, surface/path continuity and native registration are required',async()=>{
  const f=await compilerFixture();
  const inputs=structuredClone(f.inputs);inputs.evidence.find(e=>e.id==='proportion')!.measurement!.value=13;
  assert.match((await compilePlacementUnit(f.unit,inputs)).errors.join(),/denominator/);
  const u=structuredClone(f.unit);if(u.rule.kind==='B-cun')u.rule.path[1].from=[1,0,0];
  assert.match((await compilePlacementUnit(u,f.inputs)).errors.join(),/disconnected/);
  const bad=structuredClone(f.unit);bad.landmarks[0].surface.barycentric=[0,1,0];
  assert.match((await compilePlacementUnit(bad,f.inputs)).errors.join(),/gap/);
});

test('F-cun rejects non-finger calibration and extrapolation',async()=>{
  const f=await compilerFixture('F-cun'),a=structuredClone(f.unit);a.landmarks[2].role='anatomical_landmark';
  assert.match((await compilePlacementUnit(a,f.inputs)).errors.join(),/finger references/);
  const b=structuredClone(f.unit);if(b.rule.kind==='F-cun')b.rule.value=10;
  assert.match((await compilePlacementUnit(b,f.inputs)).errors.join(),/exceeds/);
});

test('coincident disconnected surfaces cannot substitute the annotated path component',async()=>{
  const f=await compilerFixture();f.carrier.positions.push(...f.carrier.positions);
  f.carrier.indices.push(4,5,6,5,7,6);
  const positions=new Float32Array(f.carrier.positions),indices=new Uint32Array(f.carrier.indices),bytes=new Uint8Array(positions.byteLength+indices.byteLength);
  bytes.set(new Uint8Array(positions.buffer));bytes.set(new Uint8Array(indices.buffer),positions.byteLength);
  f.carrier.topologySha256=await sha256(bytes);f.inputs.native['fixture-native'].topologySha256=f.carrier.topologySha256;
  f.unit.landmarks.forEach(l=>l.native.carrierHash=f.carrier.topologySha256);f.inputs.evidence.forEach(e=>e.carrierHash=f.carrier.topologySha256);
  if(f.unit.rule.kind==='B-cun')f.unit.rule.path.forEach(s=>s.triangle+=2);
  assert.match((await compilePlacementUnit(f.unit,f.inputs)).errors.join(),/disconnected topology/);
});

test('missing oral/perineal surface is not relocated; off-midline anchor fails',async()=>{
  const f=await compilerFixture('midline'),missing={...f.unit,carrierId:'absent-mucosa'};
  assert.equal((await compilePlacementUnit(missing,f.inputs)).instance,null);
  const bad=structuredClone(f.unit);bad.landmarks[0].surface.barycentric=[0,0,1];bad.landmarks[0].native.barycentric=[0,0,1];
  assert.match((await compilePlacementUnit(bad,f.inputs)).errors.join(),/midline/);
});

test('held local source rights block that unit; held public rights do not block local policy',async()=>{
  const f=await compilerFixture();const bad=structuredClone(f.inputs);bad.evidence[0].rights.localObservation='held';
  assert.equal((await compilePlacementUnit(f.unit,bad)).status,'failed');
  const native=structuredClone(f.inputs);native.native['fixture-native'].rights.localObservation='held';
  assert.match((await compilePlacementUnit(f.unit,native)).errors.join(),/rights held/);
});

test('failed-only resume preserves successful result and failure history; input changes invalidate checkpoint',async()=>{
  const f=await compilerFixture(),ok=f.unit,bad={...structuredClone(f.unit),id:'retry',rule:{kind:'unresolved' as const}};
  const first=await compilePlacementBatch([ok,bad],f.inputs);
  const corrected={...bad,rule:ok.rule},second=await compilePlacementBatch([ok,corrected],f.inputs,first.ledger);
  assert.deepEqual(second.executed,['retry']);assert.deepEqual(second.reused,[ok.id]);assert.equal(second.history[0].status,'failed');
  assert.deepEqual(second.ledger.units[ok.id],first.ledger.units[ok.id]);assert.equal(second.ledger.units.retry.status,'passed');
  const repeat=await compilePlacementBatch([ok,corrected],f.inputs,second.ledger);assert.equal(repeat.executed.length,0);
  const changed=structuredClone(f.inputs);changed.evidence[0].originalText+=' new annotation revision';
  const third=await compilePlacementBatch([ok],changed,second.ledger);assert.deepEqual(third.executed,[ok.id]);
});

test('static runtime projection rejects motion, stale topology and cancellation',async()=>{
  const f=await compilerFixture('landmark'),r=await compilePlacementUnit(f.unit,f.inputs);
  await assert.rejects(projectLearnerInstances(f.carrier,[r.instance!],{...f.context,motionActive:true}),/Static/);
  await assert.rejects(projectLearnerInstances(f.carrier,[r.instance!],{...f.context,motionActive:false},()=>true),/Cancelled/);
  const c=structuredClone(f.carrier);c.positions[0]+=.01;
  await assert.rejects(projectLearnerInstances(c,[r.instance!],{...f.context,motionActive:false}),/hash/);
});

for(const side of ['right','left'])test(`actual ${side} LU input: additive migration preserves all original fields and 11 unresolved positions`,async()=>{
  const bytes=readFileSync(new URL(`../../../../work/evidence/acupoint-AC2/${side}-learning.json`,import.meta.url)),original=JSON.parse(bytes.toString());
  const before=await sha256(bytes),m=await migratePlacementDocument(bytes);
  assert.equal(m.sourceSha256,before);assert.equal(await sha256(bytes),before);assert.equal(m.document.instances.length,11);
  for(let k=0;k<11;k++) {
    const {assessment,...legacy}=m.document.instances[k];assert.deepEqual(legacy,original.instances[k]);
    assert.equal(assessment!.author,'ai');assert.equal(assessment!.precision,'unresolved');assert.equal(assessment!.technical,'not_checked');
  }
  assert.deepEqual(productInstances(original.carrier,m.document.instances),[]);
  const again=await migratePlacementDocument(new TextEncoder().encode(JSON.stringify(m.document)));assert.equal(again.migrated,false);assert.deepEqual(again.document,m.document);
});

test('policy rejects incomplete/forged checks and stale binding rather than trusting old flags',async()=>{
  const f=await compilerFixture('landmark'),r=await compilePlacementUnit({...f.unit,scope:'real_input'},{...f.inputs,domain:'real_input'}),i=structuredClone(r.instance!);
  i.assessment!.checkedBinding=anchorBinding(i);
  assert.equal(productInstances(f.carrier,[i]).length,1);
  const incomplete=structuredClone(i);delete (incomplete.assessment!.checks as {pose?:boolean}).pose;
  assert.equal(productInstances(f.carrier,[incomplete]).length,0);
  const legacy={...i,assessment:undefined} as PointInstance;assert.equal(productInstances({...f.carrier,precision:'landmarks_verified'},[legacy]).length,0);
});

test('shared midline native context retains source side, validates addressed hemisphere and cannot reflect',async()=>{
 const f=await compilerFixture('landmark');const native=f.inputs.native['fixture-native'];native.side='midline';f.unit.landmarks.forEach(l=>l.native.side='midline');
 assert.equal((await compilePlacementUnit(f.unit,f.inputs)).status,'passed');
 const wrong=structuredClone(f.unit);wrong.landmarks[0].native.side='left';assert.equal((await compilePlacementUnit(wrong,f.inputs)).status,'failed');
 const reflected=structuredClone(f.inputs);reflected.native['fixture-native'].positions=reflected.native['fixture-native'].positions.map((v,i)=>i%3===0?-v:v);
 const p=new Float32Array(reflected.native['fixture-native'].positions),idx=new Uint32Array(reflected.native['fixture-native'].indices),bytes=new Uint8Array(p.byteLength+idx.byteLength);bytes.set(new Uint8Array(p.buffer));bytes.set(new Uint8Array(idx.buffer),p.byteLength);reflected.native['fixture-native'].topologySha256=await sha256(bytes);f.unit.landmarks.forEach(l=>l.native.carrierHash=reflected.native['fixture-native'].topologySha256);
 assert.match((await compilePlacementUnit(f.unit,reflected)).errors.join(),/side mismatch/);
});
test('named CV midline technical fixture still exports zero product locations',async()=>{
 const f=await compilerFixture('midline');f.unit.code='CV1';f.inputs.evidence.forEach(e=>e.pointCode='CV1');const r=await compilePlacementUnit(f.unit,f.inputs);assert.equal(r.status,'passed');assert.equal(r.instance!.side,'midline');
 assert.deepEqual(await projectCompiledBatch({version:2,compilerVersion:r.assessment.compilerVersion,units:{[r.id]:r}},f.inputs,{...f.context,motionActive:false}),[]);
});

test('surface fraction requires its own source denominator and connected path; never exports fixture',async()=>{
 const f=await compilerFixture('B-cun');if(f.unit.rule.kind!=='B-cun')throw Error('fixture');
 f.unit.rule={...f.unit.rule,kind:'surface_fraction',value:1,denominator:3};f.inputs.evidence.find(e=>e.id==='proportion')!.measurement={kind:'surface_fraction',value:3};
 const passed=await compilePlacementUnit(f.unit,f.inputs);assert.equal(passed.status,'passed');assert.equal(productInstances(f.carrier,[passed.instance!]).length,0);
 const bad=structuredClone(f.inputs);bad.evidence.find(e=>e.id==='proportion')!.measurement={kind:'B-cun',value:3};assert.match((await compilePlacementUnit(f.unit,bad)).errors.join(),/surface-fraction/);
 const broken=structuredClone(f.unit);if(broken.rule.kind==='surface_fraction')broken.rule.path[1].from=[1,0,0];assert.match((await compilePlacementUnit(broken,f.inputs)).errors.join(),/disconnected/);
});
test('source orientation rejects the wrong surface without allowing nearest approval',async()=>{
 const f=await compilerFixture('landmark');const surface=f.inputs.evidence.find(e=>e.purpose==='surface_registration')!;const normal=resolveAnchor(f.carrier,{...f.unit.landmarks[0].surface,carrierId:f.carrier.id,carrierRevision:f.carrier.revision,carrierHash:f.carrier.topologySha256,frameId:f.context.frameId,unit:'m',poseId:f.context.poseId,side:f.unit.side}).normal;
 surface.surfaceOrientation={direction:normal.toArray(),minimumDot:.9};assert.equal((await compilePlacementUnit(f.unit,f.inputs)).status,'passed');surface.surfaceOrientation.direction=normal.negate().toArray();assert.match((await compilePlacementUnit(f.unit,f.inputs)).errors.join(),/orientation/);
});
