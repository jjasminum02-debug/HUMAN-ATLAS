import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { AcupunctureOverlay } from './AcupunctureOverlay.ts';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
const d=JSON.parse(readFileSync(new URL('../../../../work/evidence/acupoint-AC2/right-learning.json',import.meta.url),'utf8'));
test('common overlay rejects source motion even after motion releases camera ownership',async()=>{
  for(const cameraOwner of ['motion',null]) {
    const adapter={resources:{dataset:{revision:d.carrier.datasetRevision,unit:'m',frameContract:{targetFrameId:d.carrier.frameId,
      staticReferencePose:{id:d.carrier.poseId}}},motionOverrides:new Set(cameraOwner===null?['deformed-source']:[])},scene:{cameraOwner}} as unknown as DatasetSceneAdapter;
    await assert.rejects(AcupunctureOverlay.create(adapter,d.carrier,d.instances,()=>{},()=>{},0),/정지 자세/);
  }
});
test('late overlay disposal releases resources without cancelling or moving a foreign camera owner',()=>{
  const oldDocument=globalThis.document;let cancelled=0,moved=0,released=0;
  globalThis.document={removeEventListener(){}} as unknown as Document;
  const canvas={removeEventListener(){},dataset:{}};
  const scene={cameraOwner:'motion',renderer:{domElement:canvas},cancelCameraMotion(){cancelled++;},moveCamera(){moved++;},endObservation(){},requestRender(){}};
  const overlay=Object.assign(Object.create(AcupunctureOverlay.prototype),{
    adapter:{scene},dead:false,removeUpdate(){},removeMotion(){},removeCamera(){},
    label:{remove(){}},group:{removeFromParent(){}},tour:{pause(){}},releaseGeometry(){released++;},moved:true,userMoved:false,
    savedCamera:{position:[0,0,1],target:[0,0,0],zoom:1}}) as AcupunctureOverlay;
  try {overlay.dispose(true);assert.equal(cancelled,0);assert.equal(moved,0);assert.equal(released,1);}
  finally {if(oldDocument)globalThis.document=oldDocument;else delete (globalThis as unknown as {document?:Document}).document;}
});
test('late disposal of an older acupoint request cannot release a newer acupoint camera session',()=>{
 const oldDocument=globalThis.document;let cancelled=0,moved=0,ended=0,released=0;
 globalThis.document={removeEventListener(){}} as unknown as Document;
 const canvas={removeEventListener(){},dataset:{acupointReview:'new-request'}};
 const scene={cameraOwner:'acupoint',isObservationFit(){return false;},renderer:{domElement:canvas},cancelCameraMotion(){cancelled++;},moveCamera(){moved++;},endObservation(){ended++;},requestRender(){}};
 const overlay=Object.assign(Object.create(AcupunctureOverlay.prototype),{adapter:{scene},dead:false,removeUpdate(){},removeMotion(){},removeCamera(){},removeFit(){},label:{remove(){}},group:{removeFromParent(){}},tour:{pause(){}},releaseGeometry(){released++;},moved:true,userMoved:false}) as AcupunctureOverlay;
 try {overlay.dispose(true);assert.equal(cancelled,0);assert.equal(moved,0);assert.equal(ended,0);assert.equal(released,1);assert.equal(canvas.dataset.acupointReview,'new-request');}
 finally {if(oldDocument)globalThis.document=oldDocument;else delete (globalThis as unknown as {document?:Document}).document;}
});
test('touch/pointer contact immediately cancels the tour and return before drag threshold',()=>{
 let cancelled=0,manual=false;const o=Object.assign(Object.create(AcupunctureOverlay.prototype),{adapter:{scene:{cancelCameraMotion(){cancelled++;}}},tour:{pause(value:boolean){manual=value;}},label:{hidden:false},halo:{visible:true}});
 assert.match(readFileSync(new URL('./AcupunctureOverlay.ts',import.meta.url),'utf8'), /private onDown=\(e:PointerEvent\)=>\{this.down=\{x:e.clientX,y:e.clientY\};this.manual\(\);\}/);
 o.manual();assert.equal(manual,true);assert.equal(cancelled,1);assert.equal(o.userMoved,true);
});

test('closing during an explicit return finishes the original snapshot even when moved flag is cleared',()=>{
 const oldDocument=globalThis.document;let restoreValue=false;
 globalThis.document={removeEventListener(){}} as unknown as Document;
 const canvas={removeEventListener(){},dataset:{}};
 const scene={cameraOwner:'acupoint',isObservationFit(){return true;},cameraState(){return {position:[0,0,2],target:[0,0,0],zoom:1};},renderer:{domElement:canvas},cancelCameraMotion(){},endObservation(_owner:string,restore:boolean){restoreValue=restore;},requestRender(){}};
 const overlay=Object.assign(Object.create(AcupunctureOverlay.prototype),{adapter:{scene},dead:false,removeUpdate(){},removeMotion(){},removeCamera(){},removeFit(){},label:{remove(){}},group:{removeFromParent(){}},tour:{pause(){}},releaseGeometry(){},moved:false,userMoved:false,savedCamera:{position:[0,0,3],target:[0,0,0],zoom:1}}) as AcupunctureOverlay;
 try {overlay.dispose(true);assert.equal(restoreValue,true);}
 finally {if(oldDocument)globalThis.document=oldDocument;else delete (globalThis as unknown as {document?:Document}).document;}
});
