import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateCarrierSample, type CarrierSample } from './carrierSample.ts';
import { productInstances } from './schema.ts';
import { CarrierSampleOverlay } from './CarrierSampleOverlay.ts';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
const sample=JSON.parse(readFileSync(new URL('../../../../atlas-data/acupoints/carriers/za-thigh-sample.json',import.meta.url),'utf8')) as CarrierSample;
const c=sample.carrier,context={datasetRevision:c.datasetRevision,frameId:c.frameId,unit:'m',poseId:c.poseId};
test('bounded source/carrier modes verify both hashes and preserve sample-only status',async()=>{
  await validateCarrierSample(sample,context);assert.equal(c.positions.length/3,1024);assert.equal(c.indices.length/3,1920);
  assert.equal(productInstances(c,[]).length,0);assert.equal(c.rights.publicRedistribution,'held');
});
test('stale pose/frame/unit and corrupted source reference cannot be displayed',async()=>{
  for(const patch of [{frameId:'other-body'},{unit:'mm'},{poseId:'deforming'}])await assert.rejects(validateCarrierSample(sample,{...context,...patch}));
  const broken=structuredClone(sample);broken.referencePositions[0]+=.02;await assert.rejects(validateCarrierSample(broken,context));
});
test('a renamed accepted skin fixture and an invalid visual offset are rejected',async()=>{
  for(const patch of [{acceptedAcupoints:1},{clearanceMetres:.6},{carrier:{...c,precision:'landmarks_verified'}}])await assert.rejects(validateCarrierSample({...sample,...patch} as CarrierSample,context));
});
test('late cancelled validation and active motion cannot allocate a static surface',async()=>{
  const adapter={resources:{dataset:{revision:c.datasetRevision,unit:'m',frameContract:{targetFrameId:c.frameId,staticReferencePose:{id:c.poseId}}}},scene:{cameraOwner:'motion'}} as unknown as DatasetSceneAdapter;
  await assert.rejects(CarrierSampleOverlay.create(adapter,sample,148379,()=>true,()=>{}),/Cancelled/);
  await assert.rejects(CarrierSampleOverlay.create(adapter,sample,148379,()=>false,()=>{}),/정지 자세/);
});
