import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { decodeCarrierChunk, validateCarrierManifest, validateCarrierSample, type CarrierManifest } from './carrierSample.ts';
import { CarrierSampleOverlay } from './CarrierSampleOverlay.ts';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
const root=new URL('../../../../atlas-data/acupoints/carriers/education-r1/',import.meta.url);
const manifest=JSON.parse(readFileSync(new URL('manifest.json',root),'utf8')) as CarrierManifest;
const context={datasetRevision:manifest.datasetRevision,frameId:manifest.frameId,unit:'m',poseId:manifest.poseId};
const bytes=(file:string)=>{const b=readFileSync(new URL(file,root));return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength) as ArrayBuffer;};
test('registered binary set reuses carrier hashes, actual bilateral topology and static frame',async()=>{
  validateCarrierManifest(manifest,context);assert.equal(manifest.chunks.filter(c=>['trunk','arm','leg'].includes(c.family)).length,11);
  assert.deepEqual([...new Set(manifest.chunks.map(c=>c.family))].sort(),['arm','foot','hand','head','leg','nail','oral','perineum','trunk']);
  for(const chunk of manifest.chunks)await validateCarrierSample(await decodeCarrierChunk(manifest,chunk,bytes(chunk.file)),context);
  assert.deepEqual([...new Set(manifest.chunks.map(c=>c.side))].sort(),['left','midline','right']);
});
test('stale registry, duplicate ids, unsafe paths and falsified costs fail closed',()=>{
  assert.throws(()=>validateCarrierManifest(manifest,{...context,poseId:'moving'}));
  for(const mutate of [(m:CarrierManifest)=>m.chunks.push(m.chunks[0]),(m:CarrierManifest)=>m.chunks[0].file='../private.bin',(m:CarrierManifest)=>m.totalBytes--]) {
    const m=structuredClone(manifest);mutate(m);assert.throws(()=>validateCarrierManifest(m,context));
  }
});
test('truncated or tampered binary data and cancelled multi-chunk validation never allocate geometry',async()=>{
  const c=manifest.chunks[0],b=bytes(c.file);await assert.rejects(decodeCarrierChunk(manifest,c,b.slice(1)));
  new Uint8Array(b)[0]^=1;await assert.rejects(decodeCarrierChunk(manifest,c,b),/hash/);
  const data=await decodeCarrierChunk(manifest,c,bytes(c.file));
  const adapter={resources:{dataset:{revision:context.datasetRevision,unit:'m',frameContract:{targetFrameId:context.frameId,staticReferencePose:{id:context.poseId}}}},scene:{cameraOwner:'motion'}} as unknown as DatasetSceneAdapter;
  await assert.rejects(CarrierSampleOverlay.createMany(adapter,[data],c.bytes,()=>true,()=>{}),/Cancelled/);
  await assert.rejects(CarrierSampleOverlay.createMany(adapter,[data],c.bytes,()=>false,()=>{}),/정지 자세/);
  // Manual camera takeover can release motion camera ownership while deformed nodes remain.
  const manualMotionAdapter={resources:{dataset:adapter.resources.dataset,motionOverrides:new Set(['native-moving-source'])},scene:{cameraOwner:undefined}} as unknown as DatasetSceneAdapter;
  await assert.rejects(CarrierSampleOverlay.createMany(manualMotionAdapter,[data],c.bytes,()=>false,()=>{}),/정지 자세/);
});
