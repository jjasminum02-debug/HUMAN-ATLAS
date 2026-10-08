import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import runtime from '../src/data/learnerMotionRuntime.generated.ts';
import {attachmentBoneKeys} from '../src/viewer/datasets/regionalContext.ts';
import {motionFrameSourceKeys} from '../src/viewer/datasets/motionFrameContext.ts';
import {motionContextVisibility} from '../src/viewer/datasets/motionContextVisibility.ts';
import {limbMotionContextKeys} from '../src/viewer/datasets/motionContextBonePose.ts';
import {conceptForExactNerveName,relationsForNerve} from '../src/domain/nerveRelations.ts';
import {innervationHighlightKeys,demandedStructureKeys} from '../src/viewer/datasets/presentation.ts';
const root=fileURLToPath(new URL('../../',import.meta.url)),out=process.argv[2];if(!out)throw Error('Output JSON required');
const json=async p=>JSON.parse(await readFile(resolve(root,p),'utf8')),sha=b=>createHash('sha256').update(b).digest('hex');
const pointer=await json('atlas-web/dist-local/CURRENT.json'),snapshot=resolve(root,'atlas-web/dist-local',pointer.snapshotDirectory);
const integration=JSON.parse(await readFile(resolve(snapshot,'public/__atlas/integration.json'),'utf8')),dataset=JSON.parse(await readFile(resolve(snapshot,'public/__atlas/datasets/human-atlas-local/manifest.json'),'utf8'));
const rows=integration.objects,byKey=new Map(rows.map(r=>[r.sourceKey,r])),instances=new Map(dataset.instances.map(r=>[r.sourceKey,r]));
const graph=await json('atlas-data/terminology/learner-nerve-graph-t66.json'),ledger=await json('work/evidence/T66/nerve-learning-2026-10-05/nerve-relation-ledger.json');
const support=await json('atlas-data/overlays/nerve-support-t66.json');
const errors=[],check=(pass,message)=>{if(!pass)errors.push(message);};
const relationAudit=graph.motorRelations.map(relation=>{
 const e=ledger.relations.find(r=>r.relationId===relation.relationId);
 check(e&&e.basis===relation.basis&&e.scope===relation.scope&&JSON.stringify(e.targetSourceKeys)===JSON.stringify(relation.targetSourceKeys)&&e.sourceIds?.length,`relation evidence ${relation.relationId}`);
 if(e)check(sha(Buffer.from(relation.displayNote))===e.displayNoteSha256,`relation note ${relation.relationId}`);
 for(const key of relation.targetSourceKeys){const row=byKey.get(key);check(row?.kind==='muscle'&&row.localDisplayEligible&&!row.hardHoldReasons.length,`relation target ${key}`);if(relation.scope==='exact_side_matched_source_instance')check(row?.side===relation.targetSide,`relation side ${key}`);}
 return {relationId:relation.relationId,basis:relation.basis,scope:relation.scope,sourceIds:e?.sourceIds,targetSourceKeys:relation.targetSourceKeys,targetNames:relation.targetSourceKeys.map(k=>byKey.get(k)?.names.en)};
});
const nerves=rows.filter(r=>r.kind==='nerve'&&r.localDisplayEligible);
const nerveAudit=nerves.map(n=>{
 const i=instances.get(n.sourceKey),concept=conceptForExactNerveName(graph.concepts,n.names.en),rels=concept?relationsForNerve(graph.motorRelations,concept.key,n.side):[];
 const keys=rels.flatMap(r=>r.targetSourceKeys).filter(k=>byKey.get(k)?.side===n.side);
 const view={region:null,regionIds:[],bones:true,muscles:true,nerves:true,poseId:n.nerve?.poseId,selectedId:n.sourceKey,dim:true,supplements:false,highlightInnervation:true,observeNerves:true,nerveConceptMuscleKeys:keys};
 const source=support.instances.find(r=>r.sourceObjectId==='0x'+n.sourceKey.replace('ZA-NERVE-',''));
 check(i&&concept&&n.nerve?.poseId&&i.sourceNamespace&&n.side===source?.side&&n.names.en===source?.names.en,`nerve identity ${n.sourceKey}`);
 check(n.sourceOnly&&n.publicRedistribution==='held'&&n.humanReview==='not_performed',`nerve authority ${n.sourceKey}`);
 for(const key of n.nerve?.branchKeys??[]){const b=byKey.get(key);check(b?.kind==='nerve'&&b.side===n.side&&b.nerve?.poseId===n.nerve.poseId,`branch ${key}`);}
 const highlights=innervationHighlightKeys(rows,view,new Set(demandedStructureKeys(rows,view)));
 check(highlights.every(k=>keys.includes(k)||n.nerve.muscleKeys.includes(k)),`invented relation ${n.sourceKey}`);
 for(const off of [{...view,nerves:false},{...view,muscles:false},{...view,poseId:'unsupported'},{...view,hiddenSourceKeys:[n.sourceKey]}])check(innervationHighlightKeys(rows,off,new Set(demandedStructureKeys(rows,off))).length===0,`nerve policy ${n.sourceKey}`);
 return {sourceKey:n.sourceKey,name:n.names.en,side:n.side,conceptKey:concept?.key,branchKeys:n.nerve?.branchKeys??[],exactMuscleKeys:n.nerve?.muscleKeys??[],conceptHighlights:highlights,poseId:n.nerve?.poseId};
});
function options(row){const selector=runtime.actions[row.sourceKey]?.length?row.sourceKey:row.haConceptId??row.sourceKey;const source=(runtime.actions[selector]??[]).filter(r=>!r.candidate||r.candidate.asset.sourceBinding?.subjectSourceKey===row.sourceKey).map(r=>({...r,id:r.actionKey}));return [...new Map([...source,...runtime.wave1Actions[row.sourceKey]??[]].map(r=>[r.id,r])).values()].filter(r=>!r.sideApplicability||['bilateral','midline',row.side].includes(r.sideApplicability));}
const actionAudit=[],assets=new Map();for(const row of rows.filter(r=>r.kind==='muscle'&&r.localDisplayEligible&&r.routeAudience==='learner'))for(const o of options(row).filter(r=>r.candidate&&r.learningIntent==='muscle_action')){
 const asset=o.candidate.asset,b=asset.sourceBinding,ms=b.members;
 check(b.subjectSourceKey===row.sourceKey&&asset.staticBinding.side===row.side,`action subject ${row.sourceKey}/${o.id}`);
 check(ms.some(m=>m.sourceKey===row.sourceKey&&m.role==='deforming_muscle_surface'),`action deformation ${row.sourceKey}/${o.id}`);
 for(const m of ms){const r=byKey.get(m.sourceKey),i=instances.get(m.sourceKey),c=dataset.chunks.find(c=>c.id===i?.lods[m.lod]?.chunk);check(r&&i&&r.side===m.side&&c?.sha256===m.sourceChunkSha256&&JSON.stringify(i.matrix)===JSON.stringify(m.instanceMatrix),`member ${o.id}/${m.sourceKey}`);}
 const attachments=attachmentBoneKeys(row.sourceKey,undefined,rows).filter(k=>{const r=byKey.get(k);return r?.kind==='bone'&&r.localDisplayEligible&&r.defaultVisible&&!r.hardHoldReasons.length&&!r.sourceHiddenStatePreserved.hideViewport&&(r.side===row.side||r.side===null||r.side==='midline');});
 const extras=limbMotionContextKeys(asset,rows,k=>attachmentBoneKeys(k,'origin').length&&attachmentBoneKeys(k,'insertion').length?attachmentBoneKeys(k):[]);
 const frameKeys=[...new Set([...motionFrameSourceKeys(ms,asset.poseControl?.framingSourceKeys,row.sourceKey,k=>byKey.get(k)?.kind,attachments),...extras])];
 const v={region:null,bones:true,muscles:true,nerves:true,poseId:'rest',selectedId:row.sourceKey,dim:true,supplements:false};
 const visible=motionContextVisibility([...ms,...extras.map(sourceKey=>({sourceKey,role:'co_moving_context'}))],frameKeys,k=>byKey.get(k),v),movingBones=ms.filter(m=>['moving_structure','co_moving_context'].includes(m.role)&&byKey.get(m.sourceKey)?.kind==='bone').map(m=>m.sourceKey);
 check(visible.includes(row.sourceKey)&&movingBones.length&&movingBones.every(k=>visible.includes(k))&&attachments.every(k=>visible.includes(k)),`motion context ${row.sourceKey}/${o.id}`);
 check(visible.filter(k=>byKey.get(k)?.kind==='muscle').length>1,`companion ${row.sourceKey}/${o.id}`);
 check(motionContextVisibility(ms,frameKeys,k=>byKey.get(k),{...v,muscles:false}).every(k=>byKey.get(k)?.kind!=='muscle'),`layer ${o.id}`);
 check(motionContextVisibility(ms,frameKeys,k=>byKey.get(k),{...v,hiddenSourceKeys:[row.sourceKey]}).every(k=>k!==row.sourceKey),`hidden ${o.id}`);
 check(visible.every(k=>byKey.get(k)?.kind!=='nerve'),`static nerve pose ${o.id}`);
 assets.set(asset.uri,asset);actionAudit.push({sourceKey:row.sourceKey,name:row.names.en,side:row.side,actionId:o.id,label:o.label,assetUri:asset.uri,assetSha256:asset.sha256,companionMuscles:visible.filter(k=>byKey.get(k)?.kind==='muscle'&&k!==row.sourceKey),movingBones,attachmentBones:attachments,frameKeys,visibleKeys:visible});
}
for(const a of assets.values())check(sha(await readFile(resolve(root,a.uri)))===a.sha256,`asset SHA ${a.uri}`);
const priority=/^(?:Tibialis anterior muscle|Rectus femoris muscle|Rectus abdominis muscle|External abdominal oblique muscle|Levator scapulae|Rhomboid (?:major|minor) muscle|\(?Abdominal part of pectoralis major muscle\)?|(?:Clavicular|Sternocostal) head of pectoralis major muscle)$/;
const priorityRows=rows.filter(r=>r.kind==='muscle'&&r.localDisplayEligible&&priority.test(r.names.en));for(const row of priorityRows)check(actionAudit.some(a=>a.sourceKey===row.sourceKey),`priority action ${row.sourceKey}`);
const wrist=rows.filter(r=>r.names.en==='Extensor carpi radialis longus'&&r.localDisplayEligible).map(r=>({sourceKey:r.sourceKey,side:r.side,options:options(r).filter(o=>/손목 굽힘/.test(o.label)).map(o=>({id:o.id,intent:o.learningIntent,members:o.candidate?.asset.sourceBinding.members.map(m=>({sourceKey:m.sourceKey,name:byKey.get(m.sourceKey)?.names.en,role:m.role}))}))}));for(const r of wrist)for(const o of r.options)check(o.intent==='posture_observation',`passive promoted ${o.id}`);
const inputHashes={};for(const p of ['atlas-web/src/data/learnerMotionRuntime.generated.ts','atlas-data/terminology/learner-nerve-graph-t66.json','atlas-data/terminology/nerve-learning-t66.json','work/evidence/T66/nerve-learning-2026-10-05/nerve-relation-ledger.json','atlas-data/overlays/nerve-support-t66.json'])inputHashes[p]=sha(await readFile(resolve(root,p)));
const report={snapshotId:pointer.snapshotDirectory,inputHashes,counts:{nerveSurfaces:nerves.length,nerveDisplayConcepts:graph.concepts.length,motorRelations:relationAudit.length,exactGeometryRelations:relationAudit.filter(r=>r.basis==='exact_geometry_motor_relation').length,branchEdges:nerveAudit.reduce((n,r)=>n+r.branchKeys.length,0),exactSourceActionPairs:actionAudit.length,actionSurfaces:new Set(actionAudit.map(r=>r.sourceKey)).size,uniqueActionGlbs:assets.size,prioritySurfaces:priorityRows.length,priorityActionPairs:actionAudit.filter(r=>priority.test(r.name)).length},nerveAudit,relationAudit,actionAudit,wristPassiveAudit:wrist,errors,geometryChanged:false,geometryQAReuse:'unchanged GLB SHA; source/frame/member contracts checked; previous emitted key/mid/contact/outcome QA reused, not newly claimed'};
await writeFile(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({counts:report.counts,errors},null,2));if(errors.length)process.exitCode=1;
