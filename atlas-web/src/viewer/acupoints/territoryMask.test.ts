import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {TerritoryMaskLayer,validateTerritoryMask,territoryEdges,maskContentHash} from './territoryMask.ts';
import {compositingFixtures} from './territoryCompositingFixture.ts';
import type {Carrier,TerritoryMask} from './schema.ts';
const read=(s:string)=>JSON.parse(readFileSync(new URL('../../../../'+s,import.meta.url),'utf8'));
const p=read('atlas-data/acupoints/territories/lung-r1/masks.json'),rules=read('work/evidence/AT6/resume-r1/bilateral-rules-r9.json');
const masks=p.masks as TerritoryMask[];const carrier=(m:TerritoryMask)=>rules.inputs.carriers[m.carrierId] as Carrier;
const shared=()=>new Map(masks.map(m=>{const c=carrier(m),geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(c.positions,3));geometry.setIndex(c.indices);geometry.computeVertexNormals();return [c.id,{carrier:c,geometry}] as const;}));
for(const m of masks)test(`${m.side} real contour with independent topology and all three actual educational points`,async()=>{
 await validateTerritoryMask(m,carrier(m),rules.context);assert.equal(m.triangleIds.length,351);assert.equal(territoryEdges(m,carrier(m)).length/2,m.side==='right'?65:67);
 assert.equal(m.scope,'real_input');assert.equal(m.author,'ai');assert.equal(m.rights.publicRedistribution,'held');assert.equal(m.professorReview,'not_performed');
 const source=read('work/evidence/AT6/resume-r1/bilateral-compiler-r8/ledger.json');for(const code of ['LU6','LU7','LU8'])assert.ok(m.triangleIds.includes(source.units[code+'-'+m.side].instance.triangle));
});
const failCases:[string,(m:TerritoryMask)=>void][]=[
 ['side',m=>{m.side='left';}],['pose',m=>{m.poseId='stale';}],['frame',m=>{m.frameId='stale';}],['hash',m=>{m.carrierHash='0'.repeat(64);}],['revision',m=>{m.carrierRevision='stale';}],
 ['rights',m=>{m.rights.localObservation='held';}],['fixture promotion',m=>{m.scope='technical_fixture';}],['anatomy certainty',m=>{Object.assign(m,{canonicalBoundaryClaim:true});}],
 ['type conflation',m=>{m.basisKind='cutaneous';}],['missing weight',m=>{m.vertexWeights.pop();}],['invalid density',m=>{m.vertexWeights[0][1]=2;}],['unknown face',m=>{m.triangleIds[0]=999999;}],
 ['unknown channel',m=>{m.channel='EX';}],
 ['face content tamper',m=>{m.triangleIds.shift();}],['weight content tamper',m=>{m.vertexWeights[0][1]=.9;}],['fictitious CV jingjin',m=>{m.channel='CV';m.kind=m.basisKind='sinew_projection';}],
];
for(const [name,mutate] of failCases)test(`mask rejects ${name}`,async()=>{const m=structuredClone(masks[0]);mutate(m);await assert.rejects(validateTerritoryMask(m,carrier(masks[0]),rules.context));});
test('two real masks share canonical positions, retain holes and release GPU bindings without changing CPU topology',()=>{
 const s=shared(),layer=new TerritoryMaskLayer(masks,s);layer.show(true,'selected','LU');const d=layer.diagnostics();assert.equal(d.visibleMasks.length,2);assert.equal(d.sharedPositionBuffers,true);assert.equal(d.raycastTargets,0);assert.equal(d.depthTest,true);assert.equal(d.depthWrite,false);
 let baseDisposed=0,ownedDisposed=0;for(const c of s.values())c.geometry.addEventListener('dispose',()=>baseDisposed++);
 layer.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){o.geometry.addEventListener('dispose',()=>ownedDisposed++);assert.equal(o.geometry.getAttribute('position'),s.get(masks.find(m=>o.name.startsWith(m.id))!.carrierId)!.geometry.getAttribute('position'));const hits:THREE.Intersection[]=[];o.raycast(new THREE.Raycaster(),hits);assert.equal(hits.length,0);}});
 const before=[...s.values()].map(c=>c.geometry.getAttribute('position'));layer.dispose();assert.equal(baseDisposed,2);assert.equal(ownedDisposed,4);assert.equal(layer.group.children.length,0);assert.deepEqual([...s.values()].map(c=>c.geometry.getAttribute('position')),before);for(const c of s.values())c.geometry.dispose();
});
test('selection/comparison preserve separate overlapping masks with stable order; no geometry union',async()=>{
 const fixture=await compositingFixtures(masks,'overlap'),s=shared(),layer=new TerritoryMaskLayer(fixture,s);layer.show(true,'selected','LU');assert.deepEqual(layer.diagnostics().visibleMasks,['technical-overlap-A']);layer.show(true,'comparison','LU');assert.equal(layer.diagnostics().visibleMasks.length,2);assert.equal(layer.diagnostics().fixtureMasks,2);assert.ok(fixture[1].triangleIds.some(f=>fixture[0].triangleIds.includes(f)));
 const reordered=new TerritoryMaskLayer([...fixture].reverse(),s);reordered.show(true,'comparison','LU');assert.deepEqual(layer.group.children.map(o=>[o.name,o.renderOrder]),reordered.group.children.map(o=>[o.name,o.renderOrder]));assert.ok(layer.group.getObjectByName('technical-overlap-A')!.renderOrder>layer.group.getObjectByName('technical-overlap-B')!.renderOrder);layer.dispose();reordered.dispose();for(const c of s.values())c.geometry.dispose();
});
test('mask visual revision changes density independently of carrier/points and leaves public review unchanged',async()=>{
 const m=structuredClone(masks[0]),c=carrier(m),before=JSON.stringify(c);m.revision='visual-r2';m.vertexWeights=m.vertexWeights.map(([v,w])=>[v,w*.8]);m.contentSha256=await maskContentHash(m);await validateTerritoryMask(m,c,rules.context);assert.equal(JSON.stringify(c),before);assert.equal(m.carrierHash,masks[0].carrierHash);assert.equal(m.boundaryRevision,masks[0].boundaryRevision);assert.notEqual(m.contentSha256,masks[0].contentSha256);assert.equal(m.rights.publicRedistribution,'held');
});
test('repeated construction/OFF balances resource disposal and creates no position/normal copies',()=>{
 const s=shared();let disposed=0;
 for(let i=0;i<5;i++){const layer=new TerritoryMaskLayer(masks,s);layer.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line)o.geometry.addEventListener('dispose',()=>disposed++);});layer.show(false,'comparison','LU');assert.equal(layer.diagnostics().drawCalls,0);layer.dispose();}
 assert.equal(disposed,20);for(const c of s.values())c.geometry.dispose();
});
