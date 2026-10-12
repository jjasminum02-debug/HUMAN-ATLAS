import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {Vector3,Mesh} from '../../../../atlas-web/node_modules/three/build/three.module.js';
import {motionActionOptionsForLearner} from '../../../../atlas-web/src/data/motionLearningData.ts';
import {loadAnimationScene} from '../../../../atlas-web/src/viewer/animationSceneAdapter.ts';
import {AnimationPlaybackController} from '../../../../atlas-web/src/viewer/animationPlayback.ts';
const root=process.cwd(),e=resolve(root,'work/evidence/MV2/2026-10-12-q02-r1');
const auth=JSON.parse(await readFile(resolve(root,'work/evidence/T66/priority-trunk-2026-10-05/flex/authored-input.json'),'utf8'));
const rows=[];const sources={left:'ZA-c7010a9-d75abb958e1463ceecb5430b',right:'ZA-c7010a9-eb0bd1853a90acada85e9177'};
function mesh(node){let m;node.traverse(n=>{if(n instanceof Mesh)m=n;});assert.ok(m);return m;}
function points(node){const m=mesh(node);return Array.from({length:m.geometry.attributes.position.count},(_,i)=>m.getVertexPosition(i,new Vector3()).applyMatrix4(m.matrixWorld).toArray());}
for(const [side,key] of Object.entries(sources)){
 const candidate=motionActionOptionsForLearner(null,side,key).find(o=>o.label==='양측 협응 몸통 굽힘').candidate;
 const raw=await readFile(resolve(root,candidate.asset.uri));assert.equal(createHash('sha256').update(raw).digest('hex'),candidate.asset.sha256);
 assert.equal(candidate.asset.poseControl.endDegrees,14);assert.equal(candidate.asset.poseControl.actionDirection,'forward');
 const res=await loadAnimationScene(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),candidate.asset);assert.equal(res.sourceNodes.size,365);
 let update;const p=new AnimationPlaybackController(res,candidate.asset.clip.id,{repeat:true,pingPong:true,actionDirection:'forward',disposeResource:false,registerUpdate:u=>{update=u;return()=>{update=null;}}});
 const target=res.sourceNodes.get(key),rest=points(target),fixed=auth.surfaceFields.find(v=>v.sourceKey===key).fixedVertexIndices;
 let maxFixed=0,maxDisplacement=0;const perSample=[];
 for(let i=0;i<=128;i++){
  p.seek(2.5*i/128);res.scene.updateMatrixWorld(true);const posed=points(target);
  for(const j of fixed)maxFixed=Math.max(maxFixed,new Vector3(...posed[j]).distanceTo(new Vector3(...rest[j])));
  let disp=0;for(let j=0;j<posed.length;j++)disp=Math.max(disp,new Vector3(...posed[j]).distanceTo(new Vector3(...rest[j])));maxDisplacement=Math.max(maxDisplacement,disp);
  perSample.push({seconds:p.currentTime,maximumDisplacementMm:disp*1000});
 }
 assert.ok(maxFixed<1e-8);assert.ok(maxDisplacement>.02);
 p.seek(0);p.play();const phases=[];
 for(let i=0;i<440;i++){update(.02);if(i%5===0)phases.push({seconds:p.currentTime,phase:p.phase});}
 assert.ok(phases.some(s=>s.phase==='action'));assert.ok(phases.some(s=>s.phase==='return'));
 p.pause();p.seek(1.25);let restored=false;p.returnToRest(.7,()=>{restored=true;});for(let i=0;i<40;i++)update?.(.02);assert.ok(restored);
 res.scene.updateMatrixWorld(true);assert.deepEqual(points(target),rest);
 p.play();update(.1);p.pause();p.seek(2.49);p.play();update(.06);p.pause();assert.ok(p.currentTime<2.5);
 p.resetPose();res.scene.updateMatrixWorld(true);assert.deepEqual(points(target),rest);
 rows.push({side,sourceKey:key,uri:candidate.asset.uri,sha256:candidate.asset.sha256,sourceNodes:res.sourceNodes.size,morphMeshCount:res.morphMeshCount,sourceBytes:res.sourceBytes,geometryBytes:res.geometryBytes,animationBytes:res.animationBytes,memoryEstimateBytes:res.memoryEstimateBytes,maxFixedErrorMetres:maxFixed,maxDisplacementMm:maxDisplacement*1000,worldSamples:perSample.length,perSample,phaseSamples:phases,restored});p.dispose();res.dispose();
}
await writeFile(resolve(e,'real-loader-validation.json'),JSON.stringify({passed:true,loader:'actual loadAnimationScene/AnimationPlaybackController/Mesh.getVertexPosition',rows},null,2)+'\n');
console.log(rows.map(({perSample,phaseSamples,...r})=>r));
