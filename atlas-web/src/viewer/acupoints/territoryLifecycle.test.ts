import test from 'node:test';import assert from 'node:assert/strict';import * as THREE from 'three';
import {AcupunctureOverlay} from './AcupunctureOverlay.ts';
import {readFileSync} from 'node:fs';
function deferred<T>(){let resolve!:(v:T)=>void;const promise=new Promise<T>(r=>{resolve=r;});return {promise,resolve};}
function harness(){let allocated=0,released=0,requests:AbortSignal[]=[];
 const pending=deferred<{masks:never[];encodedBytes:number}>();
 class Layer {group=new THREE.Group();constructor(){allocated++;}show(){}diagnostics(){return {additionalBufferBytes:8,triangles:1,drawCalls:0};}dispose(){released++;this.group.removeFromParent();}}
 const module={loadTerritoryPackage:(_c:unknown,_context:unknown,signal:AbortSignal)=>{requests.push(signal);return pending.promise;},TerritoryMaskLayer:Layer};
 const o=Object.assign(Object.create(AcupunctureOverlay.prototype),{dead:false,territoryGeneration:0,territoryLayer:null,territoryRequest:null,territoryEncodedBytes:0,sharedCarriers:new Map(),group:new THREE.Group(),carrier:{datasetRevision:'test',frameId:'frame',poseId:'pose',unit:'m'},adapter:{resources:{dataset:{chunks:[],instances:[]},queue:{bytes:0}},scene:{requestRender(){}}},inspect(){},cost(){return {geometryBufferBytes:0,encodedBytes:0,triangles:0};},loadTerritoryModule:async()=>module});
 return {o,pending,module,counts:()=>({allocated,released,requests})};
}
test('OFF during module import cannot start a data request or allocate/restart camera',async()=>{
 const h=harness(),imported=deferred<typeof h.module>();h.o.loadTerritoryModule=()=>imported.promise;
 const on=h.o.showTerritories(true);await h.o.showTerritories(false);imported.resolve(h.module);await on;
 assert.equal(h.counts().allocated,0);assert.equal(h.counts().requests.length,0);assert.equal(h.o.territoryLayer,null);assert.equal(h.o.territoryLoading,false);
});
test('OFF aborts in-flight mask fetch; late parse cannot create a layer',async()=>{
 const h=harness(),on=h.o.showTerritories(true);await Promise.resolve();await Promise.resolve();assert.equal(h.counts().requests.length,1);
 await h.o.showTerritories(false);assert.equal(h.counts().requests[0].aborted,true);h.pending.resolve({masks:[],encodedBytes:10});await on;
 assert.equal(h.counts().allocated,0);assert.equal(h.o.territoryLayer,null);
});
test('last selection owns the one installed layer; OFF disposes it and releases encoded cost',async()=>{
 const h=harness(),a=h.o.showTerritories(true,'selected','LU');await Promise.resolve();
 const b=h.o.showTerritories(true,'comparison','LI');await Promise.resolve();h.pending.resolve({masks:[],encodedBytes:10});await Promise.all([a,b]);
 assert.equal(h.counts().allocated,1);assert.equal(h.counts().requests[0].aborted,true);assert.equal(h.o.territoryChannel,'LI');assert.equal(h.o.territoryMode,'comparison');assert.equal(h.o.territoryEncodedBytes,10);
 await h.o.showTerritories(false);assert.equal(h.counts().released,1);assert.equal(h.o.territoryEncodedBytes,0);assert.equal(h.o.group.children.length,0);
});
test('overlay disposal cancels pending territory completion independently of remaining points',async()=>{
 const h=harness(),on=h.o.showTerritories(true);await Promise.resolve();h.o.releaseGeometry();h.o.dead=true;
 h.pending.resolve({masks:[],encodedBytes:10});await on;assert.equal(h.counts().allocated,0);assert.equal(h.counts().requests[0].aborted,true);
});
test('an already sufficient real LU composition flushes inertia and cancels the previous tween without animation',()=>{
 const read=(p:string)=>JSON.parse(readFileSync(new URL('../../../../'+p,import.meta.url),'utf8'));
 const context=read('atlas-data/acupoints/observation/lung-context-r1.json').contexts.find((c:{code:string;side:string})=>c.code==='LU7'&&c.side==='right');
 const proof=read('work/evidence/AT21/run-r1/area-1440-LU7-right-r7.json'),state=proof.territory.currentCamera;
 let cancelled=0,flushed=0;const canvas={getBoundingClientRect:()=>proof.canvas};
 const scene={cameraOwner:'acupoint',renderer:{domElement:canvas},camera:{fov:35},controls:{enableDamping:true,update(){assert.equal(this.enableDamping,false);flushed++;}},cameraState:()=>structuredClone(state),moveCamera(held:unknown,smooth:boolean){assert.equal(smooth,false);assert.deepEqual(held,state);cancelled++;},requestRender(){}};
 const o=Object.assign(Object.create(AcupunctureOverlay.prototype),{dead:false,adapter:{scene,resources:{nodes:new Map()}},options:{contexts:[context]},markers:new Map(),safeRect:()=>proof.review.safeViewport,selected:'LU7',inspect(){}});
 o.frameContexts([context]);assert.equal(o.observation.retained,true);assert.equal(cancelled,1);assert.equal(flushed,1);assert.equal(scene.controls.enableDamping,true);assert.deepEqual(o.observation.cameraTarget,state);
});
test('a late context observer cannot touch a foreign camera owner or a disposed overlay',()=>{
 for(const [owner,dead] of [['motion',false],['acupoint',true]]){
  const o=Object.assign(Object.create(AcupunctureOverlay.prototype),{dead,adapter:{scene:{cameraOwner:owner}},safeRect(){throw Error('must not read stale UI');}});assert.doesNotThrow(()=>o.frameContexts([]));
 }
});
