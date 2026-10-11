import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {validateCarrier,verifyCarrierHash,resolveAnchor} from './anchorAdapter.ts';import {productInstances} from './schema.ts';import {LUNG_ORDER} from './tour.ts';
const load=(side:string)=>JSON.parse(readFileSync(new URL(`../../../../work/evidence/acupoint-AC2/${side}-learning.json`,import.meta.url),'utf8'));
for(const side of ['right','left'])test(`${side}: native carrier binding, order, safe proposals, and names`,async()=>{
 const d=load(side),c=d.carrier;validateCarrier(c,{datasetRevision:c.datasetRevision,frameId:c.frameId,unit:'m',poseId:c.poseId});await verifyCarrierHash(c);
 assert.deepEqual(d.instances.map((p:{code:string})=>p.code),LUNG_ORDER);assert.deepEqual(d.route.teachingPointOrder,LUNG_ORDER);assert.equal(d.route.kind,'surface_teaching');assert.equal(d.route.carrierHash,c.topologySha256);assert.equal(d.concepts[8].nameKo,'태연');assert.equal(d.concepts[10].nameKo,'소상');assert.equal(productInstances(c,d.instances).length,0);
 for(const p of d.instances){const anchor=resolveAnchor(c,p);assert.ok(side==='right'?anchor.position.x<0:anchor.position.x>0);assert.ok(p.landmarkSourceKeys.length>0);assert.equal(p.locationValidation,'unresolved');}
});
test('left is independently source-bound with separate source keys/hash; no runtime mirror',()=>{const r=load('right'),l=load('left');assert.notEqual(r.carrier.topologySha256,l.carrier.topologySha256);for(let i=0;i<11;i++)assert.notDeepEqual(r.instances[i].landmarkSourceKeys,l.instances[i].landmarkSourceKeys);});
