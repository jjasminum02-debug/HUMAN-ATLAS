import type { PointInstance } from './schema.ts';

export async function sha256(bytes: Uint8Array): Promise<string> {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(bytes).buffer))].map(n=>n.toString(16).padStart(2,'0')).join('');
}
/** Additive migration. Never change legacy missing/AI/review fields or overwrite source bytes. */
export async function migratePlacementDocument(bytes: Uint8Array) {
  const sourceSha256=await sha256(bytes);
  const source=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes)) as {schemaVersion:number;instances:PointInstance[];[key:string]:unknown};
  if(![1,2].includes(source.schemaVersion)||!Array.isArray(source.instances))throw Error('Unsupported placement schema');
  if(source.schemaVersion===2) {
    if(source.instances.some(i=>i.assessment?.schemaVersion!==2))throw Error('Incomplete V2 placement assessment');
    return {document:source,sourceSha256,migrated:false};
  }
  const document={...source,schemaVersion:2,migration:{from:1,sourceSha256,policy:'landmark-evidence-v2',originalPreserved:true},
    instances:source.instances.map(i=>({...i,assessment:{schemaVersion:2 as const,policyVersion:'landmark-evidence-v2' as const,
      scope:'real_input' as const,inputDomain:'real_input' as const,technical:'not_checked' as const,precision:'unresolved' as const,basis:'legacy_unresolved' as const,
      author:i.aiProposal?'ai' as const:'unknown' as const,inputSha256:sourceSha256,compilerVersion:'migration-only-v2',checkedBinding:null,
      landmarks:[],relation:[],checks:{side:false,pose:false,frame:false,topology:false,surface:false,anatomicalRelation:false},
      failures:['legacy placement has no independently verified landmark/proportion rule',...i.missing],
      rights:{localObservation:'held' as const,publicRedistribution:'held' as const,sourceIds:[]}}}))};
  return {document,sourceSha256,migrated:true};
}
