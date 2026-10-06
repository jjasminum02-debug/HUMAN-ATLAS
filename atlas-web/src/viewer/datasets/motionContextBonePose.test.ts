import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { AnimationMixer, Matrix4 } from 'three';
import { contextBoneFollowers, followContextBone, limbMotionContextKeys } from './motionContextBonePose.ts';
import { loadAnimationScene } from '../animationSceneAdapter.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type { MotionAsset } from '../../domain/motionLearning.ts';
const rows=JSON.parse(readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json',import.meta.url),'utf8')).objects as RuntimeStructureRecord[];
const instances=JSON.parse(readFileSync(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json',import.meta.url),'utf8')).instances;
const attachments=JSON.parse(readFileSync(new URL('../../../../atlas-data/terminology/learner-attachment-context.json',import.meta.url),'utf8'));
const bundle=JSON.parse(readFileSync(new URL('../../../../atlas-data/motion/motion-learning.json',import.meta.url),'utf8'));
test('both forearm bones keep their native relationship at actual shoulder/elbow key and intermediate poses, then restore exactly',async()=>{
  let count=0;
  for(const asset of bundle.motionAssets as MotionAsset[]) {
    const radius=rows.find(row=>row.names.en==='Radius'&&row.side===asset.staticBinding.side)!;
    if(!radius)continue;
    const followers=contextBoneFollowers(asset,[radius.sourceKey],key=>rows.find(row=>row.sourceKey===key));
    if(!followers.length)continue;
    const bytes=readFileSync(new URL('../../../../'+asset.uri,import.meta.url));
    const resource=await loadAnimationScene(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength) as ArrayBuffer,asset);
    const anchor=resource.sourceNodes.get(followers[0].anchorSourceKey)!;
    const restAnchor=anchor.matrix.clone();const rest=new Matrix4().fromArray(instances.find((row:any)=>row.sourceKey===radius.sourceKey).matrix);
    const relative=restAnchor.clone().invert().multiply(rest);
    const mixer=new AnimationMixer(resource.scene);const clip=resource.animations.find(clip=>clip.name===asset.clip.id)!;mixer.clipAction(clip).play();
    for(const fraction of [0,.25,.5,.75,1]) {
      mixer.setTime(clip.duration*fraction);anchor.updateMatrix();
      const result=followContextBone(rest,restAnchor.clone().invert(),anchor.matrix,new Matrix4());
      const actualRelative=anchor.matrix.clone().invert().multiply(result);
      assert.ok(actualRelative.elements.every((value,index)=>Math.abs(value-relative.elements[index])<1e-6));
      assert.ok(Math.abs(result.determinant()-rest.determinant())<1e-5,'rigid teaching delta never scales or reflects the whole bone');
    }
    const restored=followContextBone(rest,restAnchor.clone().invert(),restAnchor,new Matrix4());
    assert.ok(restored.elements.every((value,index)=>Math.abs(value-rest.elements[index])<1e-6));
    mixer.stopAllAction();resource.dispose();count++;
  }
  assert.equal(count,4);
});

test('context completes the native hand chain only with a unique valid moving ulna and distal-only muscle attachments',()=>{
  const asset=(bundle.motionAssets as MotionAsset[]).find(row=>row.id.startsWith('T66-FAMILY-elbow-flexion-left-'))!;
  const fixtureAttachments={...attachments};
  const bone=(name:string)=>rows.find(row=>row.side==='left' && row.names.en===name)!.sourceKey;
  const passive=rows.find(row=>row.side==='left' && row.names.en==='Abductor pollicis longus')!;
  const crossing=rows.find(row=>row.side==='left' && row.names.en==='Extensor carpi radialis longus')!;
  fixtureAttachments[passive.sourceKey]={origin:[bone('Radius'),bone('Ulna')],insertion:[bone('First metacarpal bone')]};
  fixtureAttachments[crossing.sourceKey]={origin:[bone('Humerus')],insertion:[bone('Second metacarpal bone')]};
  const resolver=(key:string)=>fixtureAttachments[key]?.origin.length && fixtureAttachments[key]?.insertion.length ? [...fixtureAttachments[key].origin,...fixtureAttachments[key].insertion] : [];
  const keys=limbMotionContextKeys(asset,rows,resolver);
  const radius=rows.find(row=>row.names.en==='Radius'&&row.side==='left')!;
  assert.ok(keys.includes(radius.sourceKey));
  assert.ok(keys.some(key=>rows.find(row=>row.sourceKey===key)?.names.en==='Second metacarpal bone'));
  assert.ok(keys.includes(passive.sourceKey));
  assert.ok(!keys.includes(crossing.sourceKey));
  for(const key of keys){
    const row=rows.find(row=>row.sourceKey===key)!; assert.equal(row.side,'left');
    if(row.kind==='muscle') assert.ok(resolver(key).every(key=>rows.find(row=>row.sourceKey===key)?.names.en!=='Humerus'));
  }
  assert.equal(contextBoneFollowers(asset,keys,key=>rows.find(row=>row.sourceKey===key)).length,keys.length);
  assert.deepEqual(limbMotionContextKeys({...asset,id:'UNRELATED'},rows,resolver),[]);
  assert.deepEqual(limbMotionContextKeys({...asset,sourceBinding:{...asset.sourceBinding!,members:asset.sourceBinding!.members.filter(member=>rows.find(row=>row.sourceKey===member.sourceKey)?.names.en!=='Ulna')}},rows,resolver),[]);
});
