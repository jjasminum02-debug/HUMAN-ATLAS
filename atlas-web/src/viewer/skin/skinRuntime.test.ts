import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { decodeSkin, SkinLayer } from './SkinLayer.ts';
import { registeredSkin, skinWithinBudget, validateSkinAsset, type SkinAsset } from './skinContract.ts';
import { SkinLayerState } from './skinState.ts';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
const asset:SkinAsset={schemaVersion:1,id:'test-not-a-point',revision:'r41',url:'http://localhost/test.glb',datasetRevision:'test',frameId:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',poseId:'za-c7010a9-9f08a17ea011-frame0-static',sha256:'52b23499e52d1b3b0d64448ebe5d1973508e24b419bf1c1e068ad10b00a54e4d',topologySha256:'6980bfdf6a90a1a1bcf23d7462b0c3645f2b5e7ad50a28a93ab555e9d6cc9d14',mappingSha256:'292d80fb1253e8cdcfcc9f3dc1ed57e6360318925de20cde6f374e773523249b',bytes:626572,geometryBytes:625080,triangles:26756,landmarkRevision:null,geometryAccepted:false,learnerEligible:false,localObservation:'supported',publicRedistribution:'held',author:'ai',professorReview:'not_performed',staticPoseOnly:true};
const bytes=()=>{const b=readFileSync(new URL('../../../../atlas-data/anatomy/skin/at10-fit-r5/skin-candidate-r41.glb',import.meta.url));return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);};
test('no rejected local checkpoint is registered or accepted through the learner gate',async()=>{
  assert.equal(registeredSkin,null);assert.throws(()=>validateSkinAsset(asset,asset),/not learner eligible/);
  validateSkinAsset(asset,asset,true);await assert.rejects(decodeSkin(bytes(),asset),/embedded frame/);
  for(const change of [{unit:'mm'},{poseId:'motion'},{frameId:'other'},{datasetRevision:'old'}])assert.throws(()=>validateSkinAsset(asset,{...asset,...change},true));
  assert.throws(()=>validateSkinAsset({...asset,localObservation:'held'},asset,true),/rights/);
});
test('actual frozen GLB uses one reference topology, identity transform and matte material without an added clock',async()=>{
  const d=await decodeSkin(bytes(),asset,true);assert.equal(d.carrier.indices.length/3,26756);assert.equal(d.carrier.positions.length/3,14517);
  assert.equal(d.carrier.coverage,'whole_body');assert.equal(d.carrier.precision,'coarse_not_skin');assert.equal(d.cost.geometryBytes,625080);
  const m=d.mesh.material as THREE.MeshStandardMaterial;assert.equal(m.transparent,false);assert.ok(m.roughness>.9);assert.equal(m.metalness,0);
  assert.deepEqual(d.mesh.matrix.toArray(),new THREE.Matrix4().toArray());const hits:THREE.Intersection[]=[];d.mesh.raycast(new THREE.Raycaster(),hits);assert.equal(hits.length,0);
  d.mesh.geometry.dispose();m.dispose();
});
test('tampered GLB bytes and topology binding fail instead of retargeting the anchor',async()=>{
  const b=bytes();new Uint8Array(b)[b.byteLength-1]^=1;await assert.rejects(decodeSkin(b,asset,true),/hash/);
  await assert.rejects(decodeSkin(bytes(),{...asset,topologySha256:'0'.repeat(64)},true),/topology hash/);
});
test('first mode entry, manual OFF, repeated entry and original skin state restore are independent',()=>{
  const s=new SkinLayerState();s.acupoints(true);assert.equal(s.visible,true);s.manual(false);s.acupoints(true);assert.equal(s.visible,false);
  s.acupoints(false);assert.equal(s.visible,false);s.acupoints(true);assert.equal(s.visible,false);s.acupoints(false);
  s.manual(true);s.acupoints(true);s.manual(false);s.acupoints(false);assert.equal(s.visible,true);assert.equal(s.explicitOff,true);
});
test('combined legacy carrier plus skin cannot quietly exceed 20MiB',()=>{
  const skin={encodedBytes:626572,geometryBytes:625080,triangles:26756},base={encodedBytes:20042516,geometryBytes:17437548,triangles:897212};
  assert.equal(skinWithinBudget(base,skin),true);assert.equal(skinWithinBudget(base,skin,{encodedBytes:813096,geometryBytes:813096,triangles:40520}),false);
});
test('OFF during fetch, repeated OFF and late completion cannot attach; source motion cannot start a static skin',async()=>{
  const oldFetch=globalThis.fetch;let resolve!:(r:Response)=>void,motion=()=>{},renders=0;
  const canvas=new EventTarget() as EventTarget&{dataset:Record<string,string>};canvas.dataset={};
  const adapter={resources:{dataset:{revision:asset.datasetRevision,unit:'m',frameContract:{targetFrameId:asset.frameId,staticReferencePose:{id:asset.poseId}},chunks:[],instances:[]},queue:{bytes:0},motionOverrides:new Set()},scene:{root:new THREE.Group(),renderer:{domElement:canvas},cameraOwner:null,requestRender(){renders++;}},onSourceMotionStart(fn:()=>void){motion=fn;return()=>{};}} as unknown as DatasetSceneAdapter;
  globalThis.fetch=()=>new Promise(r=>{resolve=r;});
  const layer=new SkinLayer(adapter,asset,true);
  try {
    const pending=layer.on();layer.off();resolve(new Response(bytes()));await pending;assert.equal(layer.visible,false);assert.equal(adapter.scene.root.children.length,0);
    globalThis.fetch=async()=>new Response(bytes());await layer.on();assert.equal(layer.visible,true);assert.equal(adapter.scene.root.children.length,1);
    let released=0;layer.sharedSurface!.geometry.addEventListener('dispose',()=>released++);motion();assert.equal(released,1);assert.equal(layer.visible,false);layer.off();assert.equal(released,1);
    adapter.resources.motionOverrides.add('deformed-source');await assert.rejects(layer.on(),/정지 자세/);assert.equal(adapter.scene.root.children.length,0);assert.ok(renders>0);
  }finally{layer.dispose();globalThis.fetch=oldFetch;}
});
