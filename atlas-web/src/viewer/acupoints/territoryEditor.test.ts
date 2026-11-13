import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import * as THREE from 'three';
import {decodeCarrierChunk,type CarrierManifest} from './carrierSample.ts';
import {widthFixture,EDITOR_CARRIER} from './territoryEditorFixture.ts';
import {TerritoryEditSession,jsonHash} from './territoryEditor.ts';
import {validateTerritoryMask,TerritoryMaskLayer} from './territoryMask.ts';
const directory=new URL('../../../../atlas-data/acupoints/carriers/education-r1/',import.meta.url);
const manifest=JSON.parse(readFileSync(new URL('manifest.json',directory),'utf8')) as CarrierManifest;
const chunk=manifest.chunks.find(c=>c.id===EDITOR_CARRIER)!;const buffer=readFileSync(new URL(chunk.file,directory));
const {carrier}=await decodeCarrierChunk(manifest,chunk,buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength));
const fixture=await widthFixture(carrier),context={datasetRevision:carrier.datasetRevision,frameId:carrier.frameId,unit:carrier.unit,poseId:carrier.poseId};
const session=()=>new TerritoryEditSession(carrier,fixture.mask,fixture.bindings);
const erase=(s:TerritoryEditSession)=>{s.beginStroke();s.apply(s.brushFaces(fixture.mask.triangleIds[100],.016),true);s.apply(s.brushFaces(fixture.mask.triangleIds[130],.016),true);s.endStroke();};
test('ST specimen is explicitly technical; ordinary learner validation rejects it',async()=>{
 assert.equal(fixture.mask.triangleIds.length,882);await assert.rejects(validateTerritoryMask(fixture.mask,carrier,context));await validateTerritoryMask(fixture.mask,carrier,context,true);
 assert.equal(fixture.points.length,2);assert.ok(fixture.points.every(p=>p.locationValidation==='unresolved'&&p.missing?.includes('technical_fixture_not_an_acupoint')));assert.ok(fixture.route.length>0);
});
test('multi-sample stroke narrows area atomically; undo/redo retain actual carrier, point and nonempty route hashes',async()=>{
 const s=session(),before=await s.snapshot(),positions=await jsonHash(carrier.positions);erase(s);const after=await s.snapshot();assert.ok(after.triangleIds.length<before.triangleIds.length);assert.notEqual(after.contentSha256,before.contentSha256);
 s.undo();assert.deepEqual(await s.snapshot(),before);s.redo();assert.deepEqual(await s.snapshot(),after);
 assert.equal(await jsonHash(carrier.positions),positions);assert.equal(await jsonHash(fixture.points),s.bindings.pointHash);assert.equal(await jsonHash(fixture.route),s.bindings.routeHash);assert.equal(after.carrierHash,before.carrierHash);
 assert.equal(after.rights.publicRedistribution,'held');assert.equal(after.professorReview,'not_performed');assert.equal(after.canonicalBoundaryClaim,false);
});
test('cancelled stroke is atomic; successful branch clears redo and no-op stroke creates no history',()=>{
 const s=session();s.beginStroke();s.apply(s.brushFaces(fixture.mask.triangleIds[0],.016),true);s.cancelStroke();assert.deepEqual(s.faceIds,fixture.mask.triangleIds);assert.equal(s.canUndo,false);
 s.beginStroke();s.apply([fixture.mask.triangleIds[0]],false);s.endStroke();assert.equal(s.canUndo,false);
 erase(s);s.undo();assert.equal(s.canRedo,true);s.beginStroke();s.apply([fixture.mask.triangleIds[0]],true);s.endStroke();assert.equal(s.canRedo,false);
});
test('revision exactly replays edited mask and rejects binding, provenance, face and approval tampering without losing successful state',async()=>{
 const s=session();erase(s);const revision=await s.revision(),target=session();await target.loadRevision(JSON.parse(JSON.stringify(revision)));assert.deepEqual(await target.snapshot(),revision.mask);
 const mutations=[(r:typeof revision)=>{r.bindings.pointHash='stale';},(r:typeof revision)=>{r.bindings.routeHash='stale';},(r:typeof revision)=>{r.bindings.carrierHash='stale';},(r:typeof revision)=>{r.mask.rights.publicRedistribution='supported';},(r:typeof revision)=>{Object.assign(r,{reviewApproval:true});},(r:typeof revision)=>{r.mask.triangleIds[0]=999999;}];
 for(const mutate of mutations){const r=structuredClone(revision);mutate(r);await assert.rejects(target.loadRevision(r));assert.deepEqual(await target.snapshot(),revision.mask);}
});
test('save/load refuse unfinished strokes and asynchronous drift',async()=>{
 const s=session(),revision=await s.revision();s.beginStroke();await assert.rejects(s.revision());await assert.rejects(s.loadRevision(revision));s.cancelStroke();
 const saving=s.revision();erase(s);await assert.rejects(saving,/changed/);
 const loading=s.loadRevision(revision);s.beginStroke();s.apply([fixture.mask.triangleIds[0]],true);s.endStroke();await assert.rejects(loading,/changed/);
});
test('geodesic brush does not cross geometrically coincident disconnected components',()=>{
 const c={...carrier,positions:[0,0,0,.01,0,0,0,.01,0,0,0,0,.01,0,0,0,.01,0],indices:[0,1,2,3,4,5]};const s=new TerritoryEditSession(c,fixture.mask,fixture.bindings);assert.deepEqual(s.brushFaces(0,.04),[0]);assert.throws(()=>s.brushFaces(2,.016));
});
test('edited preview reuses canonical position buffer and never becomes an anatomy raycast target',async()=>{
 const s=session();erase(s);const mask=await s.snapshot(),geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(carrier.positions,3));geometry.setIndex(carrier.indices);geometry.computeVertexNormals();
 const layer=new TerritoryMaskLayer([mask],new Map([[carrier.id,{carrier,geometry}]]));layer.show(true,'selected','ST');assert.equal(layer.diagnostics().sharedPositionBuffers,true);assert.equal(layer.diagnostics().raycastTargets,0);
 const original=geometry.getAttribute('position');layer.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){assert.equal(o.geometry.getAttribute('position'),original);const hits:THREE.Intersection[]=[];o.raycast(new THREE.Raycaster(),hits);assert.equal(hits.length,0);}});layer.dispose();assert.equal(geometry.getAttribute('position'),original);geometry.dispose();
});
