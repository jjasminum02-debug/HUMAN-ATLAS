import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolveAnchor, validateCarrier, verifyCarrierHash, withinOverlayBudget } from './anchorAdapter.ts';
import { productInstances, type Carrier, type PointInstance } from './schema.ts';
const data=JSON.parse(readFileSync(new URL('../../../../work/evidence/acupoint-AC1/prototype.json',import.meta.url),'utf8')) as {carrier:Carrier;instances:PointInstance[]};
const c=data.carrier,ctx={datasetRevision:c.datasetRevision,frameId:c.frameId,unit:'m',poseId:c.poseId};
test('frozen topology hash, subject-right and three anchors reproduce',async()=>{
  validateCarrier(c,ctx);await verifyCarrierHash(c);assert.deepEqual(data.instances.map(i=>i.code),['LU1','LU9','LU11']);
  for(const i of data.instances){const a=resolveAnchor(c,i),b=resolveAnchor(c,i);assert.deepEqual(a.position.toArray(),b.position.toArray());assert.ok(a.position.x<0);assert.ok(Math.abs(a.normal.length()-1)<1e-10);}
});
test('wrong frame, mm, changed pose, side and dataset revision are rejected',()=>{
  for(const change of [{frameId:'other'},{unit:'mm'},{poseId:'flexed'},{datasetRevision:'other'}]) assert.throws(()=>validateCarrier(c,{...ctx,...change}));
  assert.throws(()=>validateCarrier({...c,side:'left'},ctx));
  for(const change of [{carrierHash:'0'.repeat(64)},{carrierRevision:'LOD2'},{side:'left'},{poseId:'flexed'}])assert.throws(()=>resolveAnchor(c,{...data.instances[0],...change} as PointInstance));
});
test('tampered geometry, index range, barycentric and degenerate faces fail closed',async()=>{
  const p=[...c.positions];p[0]+=.001;await assert.rejects(verifyCarrierHash({...c,positions:p}));
  assert.throws(()=>validateCarrier({...c,indices:[999999,0,1]},ctx));
  for(const barycentric of [[NaN,0,1],[-.1,.6,.5],[.2,.2,.2]])assert.throws(()=>resolveAnchor(c,{...data.instances[0],barycentric} as PointInstance));
  assert.throws(()=>resolveAnchor({...c,indices:c.indices.map(()=>0)},data.instances[0]));
});
test('development proposals never become product placements',()=>{
  assert.deepEqual(productInstances(c,data.instances),[]);
  assert.deepEqual(productInstances({...c,precision:'landmarks_verified'},data.instances),[]);
});
test('carrier cost consumes existing byte and triangle ceilings',()=>{
  assert.ok(withinOverlayBudget({overviewBytes:20_042_516,geometryBytes:30_000_000,triangles:897_212},{bytes:44_280,triangles:2040}));
  assert.equal(withinOverlayBudget({overviewBytes:20*1024*1024,geometryBytes:0,triangles:0},{bytes:1,triangles:0}),false);
  assert.equal(withinOverlayBudget({overviewBytes:0,geometryBytes:96*1024*1024,triangles:0},{bytes:1,triangles:0}),false);
  assert.equal(withinOverlayBudget({overviewBytes:0,geometryBytes:0,triangles:1_000_000},{bytes:0,triangles:1}),false);
});
