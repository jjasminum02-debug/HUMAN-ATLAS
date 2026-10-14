import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import * as THREE from 'three';
import {CONTACT_OFFSET,localContactTriangle,placeContactGlyph} from './contactGlyph.ts';
import {resolveAnchor} from './anchorAdapter.ts';import type {Carrier,PointInstance} from './schema.ts';
const read=(p:string)=>JSON.parse(readFileSync(new URL('../../../../'+p,import.meta.url),'utf8'));
test('all 108 real-input LU/LI/TE bindings survive contact-glyph conversion with no re-authoring or nearest muscle',async()=>{
  const sets=[['work/evidence/AT6/resume-r1/bilateral-rules-r9.json','work/evidence/AT6/resume-r1/bilateral-compiler-r9/ledger.json'],['work/evidence/AT8/2026-10-13-r1/rules-r19.json','work/evidence/AT8/2026-10-13-r1/compiler-r19/ledger.json']];
  let n=0;const geometry=new THREE.CircleGeometry(.0023,16),material=new THREE.MeshBasicMaterial();
  try {for(const [rules,ledger] of sets){const doc=read(rules),inputs=doc.inputs,units=ledger.includes('AT6')?(await (await import('./anchorCompiler.ts')).compilePlacementBatch(doc.units,inputs)).ledger.units:read(ledger).units;
    for(const u of Object.values(units) as {status:string;instance:PointInstance}[]){if(u.status!=='passed')continue;
      const p=u.instance,c=inputs.carriers[p.carrierId] as Carrier,before=JSON.stringify(p),a=resolveAnchor(c,p),mesh=new THREE.Mesh(geometry,material);placeContactGlyph(mesh,c,p);
      assert.equal(JSON.stringify(p),before);assert.ok(mesh.position.distanceTo(a.position.clone().addScaledVector(a.normal,CONTACT_OFFSET))<1e-12);
      assert.ok(new THREE.Vector3(0,0,1).applyQuaternion(mesh.quaternion).distanceTo(a.normal)<1e-10);assert.deepEqual(mesh.userData.anchor.barycentric,p.barycentric);
      const cue=localContactTriangle(c,p);assert.equal(cue.length,9);for(let k=0;k<9;k+=3)assert.ok(new THREE.Vector3().fromArray(cue,k).distanceTo(a.position)<.0071);n++;
    }}assert.equal(n,108);
  } finally {geometry.dispose();material.dispose();}
});
