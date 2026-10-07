import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { attachmentBoneKeys, attachmentText } from '../src/viewer/datasets/regionalContext.ts';
import { attachmentObservationKeys, demandedStructureKeys } from '../src/viewer/datasets/presentation.ts';
import type { RuntimeStructureRecord } from '../src/viewer/datasets/integration.ts';
const root=fileURLToPath(new URL('../../',import.meta.url));
const out=resolve(root,'work/reviews/atlas-ui-graphics-and-hosting-2026-10-07/04-attachments');
const current=JSON.parse(readFileSync(resolve(root,'atlas-web/dist-local/CURRENT.json'),'utf8'));
const publicRoot=resolve(root,'atlas-web/dist-local',current.snapshotDirectory,'public/__atlas');
const files={integration:resolve(publicRoot,'integration.json'),dataset:resolve(publicRoot,'datasets/human-atlas-local/manifest.json'),
  text:resolve(root,'atlas-data/terminology/learner-card-runtime.json'),contexts:resolve(root,'atlas-data/terminology/learner-attachment-context.json')};
const hashes=Object.fromEntries(Object.entries(files).map(([key,path])=>[key,{path:path.slice(root.length),sha256:createHash('sha256').update(readFileSync(path)).digest('hex')}]));
const rows=JSON.parse(readFileSync(files.integration,'utf8')).objects as RuntimeStructureRecord[];
const dataset=JSON.parse(readFileSync(files.dataset,'utf8'));
const instances=new Map<string,any>(dataset.instances.map((i:any)=>[i.sourceKey,i]));
const resources=new Map<string,any>(Object.entries(dataset.resources));
const contexts=JSON.parse(readFileSync(files.contexts,'utf8'));
const byKey=new Map(rows.map(r=>[r.sourceKey,r]));
const supported=rows.filter(r=>r.kind==='muscle'&&r.localDisplayEligible&&r.defaultVisible&&r.inspectionEligible&&r.routeAudience==='learner');
const priority=/Tibialis anterior|Rectus femoris|Pectoralis major|pectoralis major|Levator scapulae|Rhomboid (?:major|minor)|Rectus abdominis|External abdominal oblique/;
const errors:unknown[]=[];const ledger:any[]=[];
for(const muscle of supported)for(const role of ['origin','insertion'] as const){
 const text=attachmentText(muscle,role); const keys=attachmentBoneKeys(muscle.sourceKey,role,rows);
 const before=contexts[muscle.sourceKey]?.[role]??[];
 const bones=keys.map(key=>{const b=byKey.get(key);const i=instances.get(key);const m=instances.get(muscle.sourceKey);
  const valid=Boolean(b&&b.kind==='bone'&&b.localDisplayEligible&&b.defaultVisible&&!b.hardHoldReasons.length
   &&(b.side===muscle.side||b.side===null||b.side==='midline')&&i&&m&&i.sourceNamespace===m.sourceNamespace
   &&dataset.frameContract.targetFrameId==='HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR'
   &&dataset.unit==='m'&&i.matrix.length===16&&i.matrix.every(Number.isFinite)
   &&i.lods.detail?.triangles>0&&resources.has(i.lods.detail.resource));
  if(!valid||!text)errors.push({sourceKey:muscle.sourceKey,role,boneKey:key,reason:!text?'missing_valid_text':'identity_side_frame_surface_or_hold'});
  return {sourceKey:key,name:b?.names.en,side:b?.side,valid,resourceSha256:i?.lods.detail?.sha256,precision:'whole_bone_context_not_footprint',resolutionBasis:before.includes(key)?'existing_explicit_context':'existing_verified_text_named_bone_or_parent_component'};
 });
 const view={region:null,selectedId:muscle.sourceKey,bones:true,muscles:true,supplements:false,dim:true,attachmentObservation:{sourceKey:muscle.sourceKey,role}};
 const emitted=attachmentObservationKeys(rows,view);
 if(emitted.length!==keys.length)errors.push({sourceKey:muscle.sourceKey,role,reason:'presentation_missing_link'});
 for(const boneKey of keys)if(attachmentObservationKeys(rows,{...view,hiddenSourceKeys:[boneKey]}).includes(boneKey))errors.push({sourceKey:muscle.sourceKey,role,reason:'hidden_bypass'});
 if(attachmentObservationKeys(rows,{...view,bones:false}).length)errors.push({sourceKey:muscle.sourceKey,role,reason:'layer_bypass'});
 if(demandedStructureKeys(rows,{...view,muscles:false}).includes(muscle.sourceKey))errors.push({sourceKey:muscle.sourceKey,role,reason:'muscle_layer_bypass'});
 ledger.push({sourceKey:muscle.sourceKey,name:muscle.names.en,side:muscle.side,priority:priority.test(muscle.names.en),
   textSupported:Boolean(text),textSha256:text?createHash('sha256').update(text).digest('hex'):null,previousBoneCount:before.length,
   boneContextSupported:keys.length>0,bones,preciseRegionSupport:0,
   disposition:!text?'text_unavailable':keys.length?'whole_bone_context':'text_only_no_unambiguous_bone_or_non_bony_attachment'});
}
const counts={supportedMuscleSurfaces:supported.length,roles:ledger.length,textRoles:ledger.filter(r=>r.textSupported).length,
 textSurfaces:new Set(ledger.filter(r=>r.textSupported).map(r=>r.sourceKey)).size,
 wholeBoneContextRoles:ledger.filter(r=>r.boneContextSupported).length,wholeBoneContextSurfaces:new Set(ledger.filter(r=>r.boneContextSupported).map(r=>r.sourceKey)).size,
 previousWholeBoneContextRoles:ledger.filter(r=>r.previousBoneCount>0).length,
 boneRoleLinks:ledger.reduce((n,r)=>n+r.bones.length,0),previousBoneRoleLinks:ledger.reduce((n,r)=>n+r.previousBoneCount,0),
 preciseRegionRoles:0,preciseRegionSurfaces:0,prioritySurfaces:new Set(ledger.filter(r=>r.priority).map(r=>r.sourceKey)).size,
 priorityRoles:ledger.filter(r=>r.priority).length,priorityBoneContextRoles:ledger.filter(r=>r.priority&&r.boneContextSupported).length};
const t13Path=resolve(root,'atlas-data/manifests/attachment-context-t13.json');
// Frozen annotations and crosschecks describe whole-bone search context; no geometric footprint exists in these contracts.
const t13=JSON.parse(readFileSync(t13Path,'utf8'));
if(t13.records.some((r:any)=>r.spatialAnnotationId!==null||r.geometry!==null||r.precision!==null)) throw Error('New spatial data requires individual source/frame/region adoption');
const spatial={frozenT13Records:t13.records.length, frozenLocatedRegions:t13.records.filter((r:any)=>r.geometry!==null).length, preciseRegionSupport:0,regionOverlayCreated:0,originalGeometryModified:0,
 consulted:['atlas-web/src/viewer/attachmentContext.ts','atlas-web/src/domain/attachmentCrosschecks.ts','atlas-web/src/domain/sourceAttachments.ts',
 'atlas-data/terminology/muscle-attachment-content-t90.json','atlas-data/terminology/muscle-attachment-content-t65.json',
 'atlas-data/terminology/muscle-attachment-content-2026-10-02.json'],
 distinction:'motion masks deform muscle surfaces; they are not measured bone attachment regions',t13ManifestExists:existsSync(t13Path)};
writeFileSync(resolve(out,'attachment-audit.json'),JSON.stringify({schemaVersion:'attachment-observation-audit-v1',inputs:hashes,
 scope:'exact_supported_source_side_part; principal_text_and_whole_bone_context_only',sourceOnly:true,humanReview:'not_performed',publicRedistribution:'held',counts,spatial,errors,ledger},null,2)+'\n');
console.log(JSON.stringify({counts,errors},null,2));if(errors.length)process.exitCode=1;
