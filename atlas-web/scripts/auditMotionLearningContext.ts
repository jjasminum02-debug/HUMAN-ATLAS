import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { PropertyBinding } from 'three';
import runtime from '../src/data/learnerMotionRuntime.generated.ts';
import type { MotionAsset } from '../src/domain/motionLearning.ts';
import { selectedMotionSubjectRole } from '../src/domain/motionSubjectPresentation.ts';
import { motionFrameSourceKeys } from '../src/viewer/datasets/motionFrameContext.ts';
import { contextBoneFollowers, limbMotionContextKeys } from '../src/viewer/datasets/motionContextBonePose.ts';
import { motionContextVisibility } from '../src/viewer/datasets/motionContextVisibility.ts';
import type { RuntimeStructureRecord } from '../src/viewer/datasets/integration.ts';
const root = resolve(import.meta.dirname, '../..');
const read = (path:string) => JSON.parse(readFileSync(resolve(root,path),'utf8'));
const records = read('atlas-data/overlays/za-local-integration.json').objects as RuntimeStructureRecord[];
const byKey = new Map(records.map(row=>[row.sourceKey,row]));
const attachment = read('atlas-data/terminology/learner-attachment-context.json') as Record<string,{origin:string[];insertion:string[]}>;
const candidates = new Map<string,MotionAsset>();
let unavailableOptions = 0;
for (const options of [...Object.values(runtime.actions),...Object.values(runtime.wave1Actions)]) for (const option of options) {
  const asset = option.candidate?.asset as unknown as MotionAsset | undefined;
  if (!asset) { unavailableOptions++; continue; }
  if (asset.sourceBinding?.subjectKind==='muscle') candidates.set(asset.id,asset);
}
const documents = new Map<string,{document:any,bytes:Buffer,hash:string}>();
const rows:any[]=[];
for (const asset of candidates.values()) {
  const binding=asset.sourceBinding!;const subject=byKey.get(binding.subjectSourceKey);
  const expectedAttachments=[...new Set([...(attachment[binding.subjectSourceKey]?.origin??[]),...(attachment[binding.subjectSourceKey]?.insertion??[])])];
  const attachments=expectedAttachments.filter(key=> {const bone=byKey.get(key);return bone?.kind==='bone' && (bone.side===subject?.side || bone.side===null);});
  const extraContext=limbMotionContextKeys(asset,records,key=>attachment[key]?.origin.length && attachment[key]?.insertion.length ? [...attachment[key].origin,...attachment[key].insertion] : []);
  const frame=[...new Set([...motionFrameSourceKeys(binding.members,asset.poseControl?.framingSourceKeys,binding.subjectSourceKey,key=>byKey.get(key)?.kind,attachments),...extraContext])];
  const visible=motionContextVisibility([...binding.members,...extraContext.map(sourceKey=>({sourceKey,role:'co_moving_context'}))],frame,key=>byKey.get(key),{region:null,bones:true,muscles:true,selectedId:binding.subjectSourceKey,supplements:false,dim:true});
  const bones=visible.filter(key=>byKey.get(key)?.kind==='bone');const muscles=visible.filter(key=>byKey.get(key)?.kind==='muscle');
  const missingAttachments=attachments.filter(key=>!visible.includes(key));
  const failures:string[]=[];
  if (!subject || !visible.includes(binding.subjectSourceKey) || !selectedMotionSubjectRole(asset,binding.subjectSourceKey)) failures.push('selected_surface_not_visible_or_exact');
  if (!bones.length) failures.push('no_skeletal_context');
  if (missingAttachments.length) failures.push('named_attachment_context_missing');
  if (!documents.has(asset.uri)) {
    const bytes=readFileSync(resolve(root,asset.uri));const hash=createHash('sha256').update(bytes).digest('hex');
    if (bytes.readUInt32LE(0)!==0x46546c67 || bytes.readUInt32LE(4)!==2) throw Error('Expected real GLB');
    const length=bytes.readUInt32LE(12);const document=JSON.parse(bytes.subarray(20,20+length).toString('utf8'));
    documents.set(asset.uri,{document,bytes,hash});
  }
  const {document,bytes,hash}=documents.get(asset.uri)!;
  if (hash!==asset.sha256) failures.push('actual_glb_hash_mismatch');
  const nodes=new Map<string,number>(document.nodes.map((node:any,index:number)=>[PropertyBinding.sanitizeNodeName(node.name??''),index]));
  const clip=document.animations?.find((animation:any)=>animation.name===asset.clip.id);
  if (!clip) failures.push('actual_clip_missing');
  const parents = new Map<number,number>();document.nodes.forEach((node:any,index:number)=>node.children?.forEach((child:number)=>parents.set(child,index)));
  const binOffset=20+bytes.readUInt32LE(12)+8;
  function changes(accessorIndex:number) {
    const a=document.accessors[accessorIndex];const b=document.bufferViews[a.bufferView];
    if (a.componentType!==5126 || a.sparse) throw Error('Unexpected motion accessor');
    const components=({SCALAR:1,VEC3:3,VEC4:4} as Record<string,number>)[a.type];
    const stride=b.byteStride??components*4;const offset=binOffset+(b.byteOffset??0)+(a.byteOffset??0);
    for(let i=1;i<a.count;i++) for(let c=0;c<components;c++) if(Math.abs(bytes.readFloatLE(offset+i*stride+c*4)-bytes.readFloatLE(offset+c*4))>1e-8) return true;
    return false;
  }
  const movingNodes=new Set<number>(clip?.channels.filter((channel:any)=>changes(clip.samplers[channel.sampler].output)).map((channel:any)=>channel.target.node)??[]);
  function nodeMoves(index:number|undefined):boolean {
    if(index===undefined)return false;
    return movingNodes.has(index) || (parents.has(index) && nodeMoves(parents.get(index)));
  }
  const missingMembers=binding.members.filter(member=>!nodes.has(member.nodeId)).map(member=>member.sourceKey);
  const movingBones=binding.members.filter(member=>byKey.get(member.sourceKey)?.kind==='bone' && (member.role==='moving_structure'||member.role==='co_moving_context'));
  const missingMovingTracks=movingBones.filter(member=>!nodeMoves(nodes.get(member.nodeId))).map(member=>member.sourceKey);
  if(missingMembers.length)failures.push('actual_member_node_missing');
  if(missingMovingTracks.length)failures.push('moving_bone_has_no_actual_pose_change');
  const postureOnlyAttachments=attachments.filter(key=>!binding.members.some(member=>member.sourceKey===key));
  const followers=contextBoneFollowers(asset,extraContext,key=>byKey.get(key));
  if (followers.length !== extraContext.length || extraContext.some(key=>!visible.includes(key))) failures.push('distal_context_incomplete');
  if (followers.some(follower=>!nodeMoves(nodes.get(binding.members.find(member=>member.sourceKey===follower.anchorSourceKey)?.nodeId??'')))) failures.push('context_anchor_has_no_actual_pose_change');
  rows.push({authoredContextBoneFollowers:followers,assetId:asset.id,sourceKey:binding.subjectSourceKey,side:asset.staticBinding.side,name:subject?.names.en,action:asset.poseControl?.label??asset.id,uri:asset.uri,sha256:asset.sha256,boneCount:bones.length,muscleCount:muscles.length,movingBoneCount:movingBones.length,attachmentCounts:{origin:attachment[binding.subjectSourceKey]?.origin.length??0,insertion:attachment[binding.subjectSourceKey]?.insertion.length??0},postureOnlyAttachments,missingMovingTracks,failures,passed:!failures.length});
}
const summary={scope:'All current runtime muscle motion candidates, including passive posture; unsupported options stay separate',registeredMuscleBindings:rows.length,uniqueSourceSurfaces:new Set(rows.map(row=>row.sourceKey)).size,uniqueGlbUris:documents.size,uniqueGlbHashes:new Set([...documents.values()].map(row=>row.hash)).size,passed:rows.filter(row=>row.passed).length,failed:rows.filter(row=>!row.passed).length,unavailableOptionRowsNotUniqueMuscles:unavailableOptions,attachmentRoleGaps:rows.filter(row=>!row.attachmentCounts.origin || !row.attachmentCounts.insertion).map(row=>({assetId:row.assetId,sourceKey:row.sourceKey,name:row.name,counts:row.attachmentCounts})),note:'Automatic context/hash/node/pose-channel verification is not exhaustive visual QA, anatomy extent, muscle activation or human review approval'};
const output=process.argv[2];if(output)writeFileSync(resolve(output),JSON.stringify({summary,rows},null,2)+'\n');
console.log(JSON.stringify({...summary,attachmentRoleGaps:summary.attachmentRoleGaps.length}));
if(summary.failed)process.exitCode=1;
