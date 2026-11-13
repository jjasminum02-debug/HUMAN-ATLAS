import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {decodeSkinComponents,disposeSkinComponents,validateSkinComponents,validateSkinComponentDocument,type SkinComponents} from './skinComponents.ts';
const root=new URL('../../../../atlas-data/anatomy/skin/at10-f3-head-r1/',import.meta.url);
const metadata=JSON.parse(readFileSync(new URL('ocular-components-r1.json',root),'utf8'));
const asset:SkinComponents={...metadata,url:'http://localhost/eyes.glb',datasetRevision:'test'};
const bytes=()=>{const b=readFileSync(new URL('ocular-components-r1.glb',root));return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);};
const document=()=>{const b=bytes();return JSON.parse(new TextDecoder().decode(new Uint8Array(b,20,new DataView(b).getUint32(12,true))));};
test('actual emitted ocular surfaces preserve fixed frame, side, source roles, and exact delivery cost',async()=>{
 validateSkinComponents(asset,asset);const group=await decodeSkinComponents(bytes(),asset);const meshes:THREE.Mesh[]=[];group.traverse(o=>{if(o instanceof THREE.Mesh)meshes.push(o);});
 assert.equal(meshes.length,8);assert.equal(asset.triangles,999);assert.equal(asset.bytes,28548);
 assert.deepEqual(new Set(meshes.map(x=>x.userData.role)),new Set(['sclera','iris','cornea','lens']));
 let released=0;for(const mesh of meshes){mesh.geometry.addEventListener('dispose',()=>released++);const hits:THREE.Intersection[]=[];mesh.raycast(new THREE.Raycaster(),hits);assert.equal(hits.length,0);if(mesh.userData.role==='cornea')assert.equal((mesh.material as THREE.MeshStandardMaterial).depthWrite,false);}
 disposeSkinComponents(group);assert.equal(released,8);
});
test('tampered payload, pose, wrong measured cost and remote GLB dependencies are rejected',async()=>{
 const b=bytes();new Uint8Array(b)[b.byteLength-1]^=1;await assert.rejects(decodeSkinComponents(b,asset),/hash/);
 await assert.rejects(decodeSkinComponents(bytes(),{...asset,geometryBytes:asset.geometryBytes+4}),/decoded cost/);
 assert.throws(()=>validateSkinComponents({...asset,poseId:'motion'},asset),/frame/);
 const mutations:Array<(d:any)=>void>=[d=>d.buffers[0].uri='https://elsewhere.test/mesh.bin',d=>d.nodes[0].translation=[0,0,1],d=>d.nodes[0].extras.side='right',d=>d.meshes[0].primitives[0].targets=[{}],d=>d.nodes[0].extras.sourceKey='invented'];
 for(const change of mutations){const doc=document();change(doc);assert.throws(()=>validateSkinComponentDocument(doc,asset));}
});

test('OFF during component fetch releases the unattached skin; reentry attaches one group and OFF disposes all nine geometries',async()=>{
 const {SkinLayer}=await import('./SkinLayer.ts');
 const raw=readFileSync(new URL('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-f2c3.glb',import.meta.url));const skinBytes=()=>raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength);
 const skin={...asset,schemaVersion:1 as const,id:'test-source-bound-skin',revision:'f2c3',sha256:'07ab569e3a3a3453ed825e9bc583869394e5e94babdee7edec6b6c437836586f',url:'http://localhost/skin.glb',bytes:626576,geometryBytes:625080,triangles:26756,topologySha256:'34146f987e073e14863c91e0d8003356b1a42235e82f9684611965a140a6d4b2',mappingSha256:'61f329005c20aa523877b0817b1121be39abf0fa7071a6f4e77d3498d6ed3c70',landmarkRevision:null,geometryAccepted:false,learnerEligible:false,localObservation:'supported' as const,publicRedistribution:'held' as const,author:'ai' as const,professorReview:'not_performed' as const,staticPoseOnly:true as const,components:asset};
 const canvas=new EventTarget() as EventTarget&{dataset:Record<string,string>};canvas.dataset={};
 const adapter={resources:{dataset:{sourceHash:asset.nativeSourceSha256,revision:asset.datasetRevision,unit:'m',frameContract:{targetFrameId:asset.frameId,staticReferencePose:{id:asset.poseId}},chunks:[],instances:[]},queue:{bytes:0},motionOverrides:new Set()},scene:{root:new THREE.Group(),renderer:{domElement:canvas},cameraOwner:null,requestRender(){}},onSourceMotionStart(){return()=>{};}};
 assert.throws(()=>new SkinLayer({...adapter,resources:{...adapter.resources,dataset:{...adapter.resources.dataset,sourceHash:'0'.repeat(64)}}} as any,skin,true),/native source hash/);
 const oldFetch=globalThis.fetch;let resolve!:(r:Response)=>void,ready!:()=>void;const componentRequested=new Promise<void>(r=>ready=r);
 globalThis.fetch=async input=>{if(String(input).endsWith('/skin.glb'))return new Response(skinBytes());ready();return new Promise(r=>resolve=r);};
 const layer=new SkinLayer(adapter as any,skin,true);
 try {
  const pending=layer.on();await componentRequested;layer.off();resolve(new Response(bytes()));await pending;assert.equal(adapter.scene.root.children.length,0);assert.equal(layer.visible,false);
  globalThis.fetch=async input=>new Response(String(input).endsWith('/skin.glb')?skinBytes():bytes());await layer.on();assert.equal(adapter.scene.root.children.length,1);
  let released=0;layer.sharedSurface!.mesh.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.addEventListener('dispose',()=>released++);});
  const data=JSON.parse(canvas.dataset.skinLayer);assert.equal(data.cost.encodedBytes,655124);assert.equal(data.cost.geometryBytes,644946);assert.equal(data.cost.triangles,27755);assert.equal(data.frameCallbacks,0);
  layer.off();layer.off();assert.equal(released,9);assert.equal(adapter.scene.root.children.length,0);
 }finally{layer.dispose();globalThis.fetch=oldFetch;}
});
