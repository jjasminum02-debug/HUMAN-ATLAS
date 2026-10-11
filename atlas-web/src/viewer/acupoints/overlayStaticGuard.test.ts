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
