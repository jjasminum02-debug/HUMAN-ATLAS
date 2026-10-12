import {readFile,writeFile} from 'node:fs/promises';import {resolve} from 'node:path';import assert from 'node:assert/strict';
import {Vector3,Mesh} from '../../../../atlas-web/node_modules/three/build/three.module.js';
import {motionActionOptionsForLearner} from '../../../../atlas-web/src/data/motionLearningData.ts';
import {loadAnimationScene} from '../../../../atlas-web/src/viewer/animationSceneAdapter.ts';
import {AnimationPlaybackController} from '../../../../atlas-web/src/viewer/animationPlayback.ts';
const root=process.cwd(), e=resolve(root,'work/evidence/MV2/2026-10-12-q01-learning-quality-r1'),rows=[];
const sources={left:'ZA-c7010a9-afb0624c66f652ea012c7534',right:'ZA-c7010a9-eb0a993e09d73159468116ce'};
function mesh(node){let found;node.traverse(n=>{if(n instanceof Mesh)found=n;});assert.ok(found);return found;}
function points(n){const m=mesh(n);return Array.from({length:m.geometry.attributes.position.count},(_,i)=>m.getVertexPosition(i,new Vector3()).applyMatrix4(m.matrixWorld).toArray());}
for(const [side,key] of Object.entries(sources)){
 const c=motionActionOptionsForLearner(null,side,key).find(o=>o.label.startsWith('무릎 폄')).candidate;assert.ok(c.asset.uri.includes('mv2-q01'));
 assert.equal(c.asset.sha256,JSON.parse(await readFile(resolve(e,side+'-candidate-r8/record.json'),'utf8')).sha256);const raw=await readFile(resolve(root,c.asset.uri));const res=await loadAnimationScene(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),c.asset);let update;const phases=[];
 const p=new AnimationPlaybackController(res,c.asset.clip.id,{repeat:true,pingPong:true,actionDirection:'reverse',disposeResource:false,registerUpdate:u=>{update=u;return()=>{update=null;}}});
 const repair=JSON.parse(await readFile(resolve(e,side+'-candidate-r8/record.json'),'utf8'));const rest=points(res.sourceNodes.get(key)), samples=[];let maxFixed=0;
 for(let i=0;i<=192;i++){p.seek(3*i/192);res.scene.updateMatrixWorld(true);const v=points(res.sourceNodes.get(key));for(const j of repair.fixedVertexIndices)maxFixed=Math.max(maxFixed,new Vector3(...v[j]).distanceTo(new Vector3(...rest[j])));samples.push({seconds:3*i/192,positions:v});}
 assert.ok(maxFixed<1e-8);p.seek(0);p.play();for(let i=0;i<430;i++){update(.02);if(i%15===0)phases.push({phase:p.phase,time:p.currentTime});}
 assert.ok(phases.some(x=>x.phase==='preparation'));assert.ok(phases.some(x=>x.phase==='action'));p.pause();p.seek(1.5);let restored=false;p.returnToRest(.7,()=>{restored=true;});for(let i=0;i<40;i++)update?.(.02);assert.ok(restored);res.scene.updateMatrixWorld(true);assert.deepEqual(points(res.sourceNodes.get(key)),rest);
 p.play();update(.11);p.pause();p.seek(2.95);p.play();update(.1);p.pause();assert.ok(p.currentTime<3);p.resetPose();res.scene.updateMatrixWorld(true);assert.deepEqual(points(res.sourceNodes.get(key)),rest);const report={side,sourceKey:key,assetUri:c.asset.uri,sha256:c.asset.sha256,sourceNodes:res.sourceNodes.size,morphMeshCount:res.morphMeshCount,sourceBytes:res.sourceBytes,geometryBytes:res.geometryBytes,animationBytes:res.animationBytes,memoryEstimateBytes:res.memoryEstimateBytes,maxFixedErrorMetres:maxFixed,worldSamples:samples.length,phaseSamples:phases,restored};rows.push(report);
 await writeFile(resolve(e,'loader-world/real-loader-world-'+side+'.json'),JSON.stringify(samples)+'\n');p.dispose();res.dispose();
}
await writeFile(resolve(e,'real-loader-validation.json'),JSON.stringify({loader:'loadAnimationScene + AnimationPlaybackController + Mesh.getVertexPosition/matrixWorld',passed:true,rows},null,2)+'\n');console.log(rows.map(({phaseSamples,...r})=>r));
