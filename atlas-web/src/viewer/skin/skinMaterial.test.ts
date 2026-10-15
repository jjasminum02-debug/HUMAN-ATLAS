import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as THREE from 'three';
import {loadSkinMaterial,disposeSkinMaterial,validateSkinMaterial,textureMipBytes,type SkinMaterialPackage} from './skinMaterial.ts';
import {skinWithinBudget} from './skinContract.ts';
const dir=new URL('../../../../atlas-data/anatomy/skin/at10-appearance-v1/',import.meta.url);
const data=JSON.parse(readFileSync(new URL('material.json',dir),'utf8'));
const p:SkinMaterialPackage={...data,maps:Object.fromEntries(Object.entries(data.maps).map(([k,m])=>[k,{...(m as object),url:new URL((m as {file:string}).file,dir).href}]))};
const glb=readFileSync(new URL('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-f2c3.glb',import.meta.url));
const n=glb.readUInt32LE(12),doc=JSON.parse(glb.subarray(20,20+n).toString()),bv=doc.bufferViews[2];
const uvBytes=glb.subarray(28+n+bv.byteOffset,28+n+bv.byteOffset+bv.byteLength);
const uv=new THREE.BufferAttribute(new Float32Array(uvBytes.buffer.slice(uvBytes.byteOffset,uvBytes.byteOffset+uvBytes.byteLength)),2);
test('actual source maps and exact F2 UV are hash-bound; decoded mip memory fits unchanged budget',()=>{
 validateSkinMaterial(p,createHash('sha256').update(glb).digest('hex'));
 assert.equal(createHash('sha256').update(uvBytes).digest('hex'),p.uvSha256);
 for(const m of Object.values(p.maps)){const b=readFileSync(new URL(m.url));assert.equal(b.length,m.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),m.sha256);assert.equal(textureMipBytes(m.width,m.height),m.gpuBytes);}
 const base={encodedBytes:20042516,geometryBytes:17437548,triangles:897212};
 const skin={encodedBytes:626576+p.encodedBytes,geometryBytes:625080,triangles:26756,textureBytes:p.textureBytes};
 assert.ok(skinWithinBudget(base,skin));assert.equal(skinWithinBudget(base,{...skin,textureBytes:96*1024*1024}),false);
 assert.equal(skinWithinBudget(base,skin,{encodedBytes:813096,geometryBytes:813096,triangles:40520}),false);
});
test('wrong geometry, map bytes, colorspace and dimensions cannot bypass manifest validation',()=>{
 assert.throws(()=>validateSkinMaterial(p,'0'.repeat(64)),/binding/);
 for(const change of [{width:4096},{gpuBytes:0},{colorSpace:'linear'},{flipY:false}])assert.throws(()=>validateSkinMaterial({...p,maps:{...p.maps,color:{...p.maps.color,...change}}},p.geometrySha256));
 assert.throws(()=>validateSkinMaterial({...p,encodedBytes:1},p.geometrySha256),/cost/);
});
test('load applies three owned maps without changing UV, and releases textures/bitmaps exactly once',async()=>{
 const oldFetch=globalThis.fetch,oldBitmap=globalThis.createImageBitmap;let closed=0,disposed=0,index=0;
 globalThis.fetch=async input=>new Response(readFileSync(new URL(String(input))));
 globalThis.createImageBitmap=(async()=>{const spec=Object.values(p.maps)[index++];return {width:spec.width,height:spec.height,close(){closed++;}};}) as typeof createImageBitmap;
 try{const m=await loadSkinMaterial(p,p.geometrySha256,uv,new AbortController().signal);
 assert.ok(m.map&&m.normalMap&&m.roughnessMap);assert.equal(m.map.colorSpace,THREE.SRGBColorSpace);assert.equal(m.normalMap.colorSpace,THREE.NoColorSpace);
 for(const t of m.userData.skinTextures)t.addEventListener('dispose',()=>disposed++);
 disposeSkinMaterial(m);disposeSkinMaterial(m);assert.equal(closed,3);assert.equal(disposed,3);
 assert.equal(createHash('sha256').update(new Uint8Array(uv.array.buffer)).digest('hex'),p.uvSha256);
 }finally{globalThis.fetch=oldFetch;globalThis.createImageBitmap=oldBitmap;}
});
test('tampered bytes and UV fail, and abort during bitmap decode closes partial resources',async()=>{
 const oldFetch=globalThis.fetch,oldBitmap=globalThis.createImageBitmap;let closed=0,calls=0;const abort=new AbortController();
 globalThis.fetch=async()=>new Response(new Uint8Array([1]));
 try {
 await assert.rejects(loadSkinMaterial(p,p.geometrySha256,uv,abort.signal),/hash\/bytes/);
 await assert.rejects(loadSkinMaterial(p,p.geometrySha256,new THREE.BufferAttribute(new Float32Array(2),2),abort.signal),/UV/);
 globalThis.fetch=async input=>new Response(readFileSync(new URL(String(input))));
 globalThis.createImageBitmap=(async()=>{const spec=Object.values(p.maps)[calls++];if(calls===2)abort.abort();return {width:spec.width,height:spec.height,close(){closed++;}};}) as typeof createImageBitmap;
 await assert.rejects(loadSkinMaterial(p,p.geometrySha256,uv,abort.signal),{name:'AbortError'});assert.equal(calls,2);assert.equal(closed,2);
 } finally{globalThis.fetch=oldFetch;globalThis.createImageBitmap=oldBitmap;}
});

test('full SkinLayer OFF and re-entry dispose maps and never change scene root or source geometry',async()=>{
 const {SkinLayer}=await import('./SkinLayer.ts');
 const node=doc.nodes[0];
 const asset={schemaVersion:1 as const,id:'v1-review-test',revision:'f2c3',url:'http://localhost/skin.glb',datasetRevision:'fixture',frameId:node.extras.frame,unit:'m' as const,poseId:node.extras.poseId,sha256:p.geometrySha256,topologySha256:'34146f987e073e14863c91e0d8003356b1a42235e82f9684611965a140a6d4b2',mappingSha256:'1'.repeat(64),bytes:glb.length,geometryBytes:625080,triangles:26756,landmarkRevision:null,geometryAccepted:false,learnerEligible:false,localObservation:'supported' as const,publicRedistribution:'held' as const,author:'ai' as const,professorReview:'not_performed' as const,staticPoseOnly:true as const,appearance:p};
 const canvas=new EventTarget() as EventTarget&{dataset:Record<string,string>};canvas.dataset={};
 const root=new THREE.Group();let closed=0,decoded=0;
 const adapter={resources:{dataset:{revision:'fixture',unit:'m',frameContract:{targetFrameId:asset.frameId,staticReferencePose:{id:asset.poseId}},chunks:[],instances:[]},queue:{bytes:0},motionOverrides:new Set()},scene:{root,renderer:{domElement:canvas},cameraOwner:null,requestRender(){}},onSourceMotionStart(){return()=>{};}};
 const oldFetch=globalThis.fetch,oldBitmap=globalThis.createImageBitmap;
 globalThis.fetch=async input=>new Response(String(input)===asset.url?glb:readFileSync(new URL(String(input))));
 globalThis.createImageBitmap=(async()=>{const m=Object.values(p.maps)[decoded++%3];return {width:m.width,height:m.height,close(){closed++;}};}) as typeof createImageBitmap;
 const layer=new SkinLayer(adapter as never,asset,true);
 try {
  for(let i=0;i<2;i++){
   await layer.on();assert.equal(root.children.length,1);assert.equal(layer.sharedSurface!.mesh.parent,root);
   assert.equal(layer.sharedSurface!.mesh.material.userData.skinTextures.length,3);
   assert.equal(JSON.parse(canvas.dataset.skinLayer).cost.textureBytes,p.textureBytes);
   layer.off();assert.equal(root.children.length,0);assert.equal(JSON.parse(canvas.dataset.skinLayer).textures,0);
  }
  assert.equal(closed,6);assert.equal(decoded,6);
 }finally{layer.dispose();globalThis.fetch=oldFetch;globalThis.createImageBitmap=oldBitmap;}
});

test('shared reservations retain texture mip costs and release each owner independently',async()=>{
 const {reserveSkinResidency,skinReservationCost}=await import('./skinRegistry.ts');
 const adapter={} as never,a={},b={};
 reserveSkinResidency(adapter,a,{encodedBytes:1,geometryBytes:2,triangles:3,textureBytes:4});
 reserveSkinResidency(adapter,b,{encodedBytes:2,geometryBytes:3,triangles:4,textureBytes:5});
 assert.equal(skinReservationCost(adapter).textureBytes,9);
 reserveSkinResidency(adapter,a,null);assert.equal(skinReservationCost(adapter).textureBytes,5);
 reserveSkinResidency(adapter,b,null);assert.equal(skinReservationCost(adapter).textureBytes??0,0);
});
