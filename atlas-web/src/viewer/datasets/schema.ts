export const DATASET_BUDGET = {overviewBytes:20*1024*1024,geometryBytes:96*1024*1024,triangles:1_000_000,chunkBytes:8*1024*1024} as const;
export type Level = 'overview'|'detail';
export interface Lod {resource:string;chunk:string;triangles:number;vertices:number;geometryBytes:number}
export interface Instance {sourceKey:string;sourceName:string;kind:string;matrix:number[];lods:Record<Level,Lod>;
  canonicalConceptId:null|string;learnerBinding:string;defaultLearnerVisible:boolean;appDisplayRights:string;
  publicRedistribution:string;humanReview:string;sourceHiddenStatePreserved:{hideRender:boolean;hideViewport:boolean};}
export interface Chunk {id:string;url:string;sha256:string;bytes:number;geometryBytes:number;resources:string[];level:Level}
export interface Dataset {schemaVersion:1;namespace:string;revision:string;unit:'m';geometrySpace:'source_local';localOnly:true;publicRedistribution:'held';
  instances:Instance[];chunks:Chunk[];resources:Record<string,{triangles:number;vertices:number;geometryBytes:number}>;budgetPass:boolean}
export function validateDataset(value:unknown):Dataset {
  const d=value as Dataset;
  if(!d||d.schemaVersion!==1||d.unit!=='m'||d.geometrySpace!=='source_local'||d.localOnly!==true||d.publicRedistribution!=='held'||!d.budgetPass||!Array.isArray(d.instances)||!Array.isArray(d.chunks))throw Error('dataset contract');
  const chunks=new Map(d.chunks.map(c=>[c.id,c]));const ids=new Set<string>();
  if(chunks.size!==d.chunks.length)throw Error('duplicate chunk');
  for(const c of d.chunks) if(!/^[a-f0-9]{64}$/.test(c.sha256)||c.bytes<=0||c.bytes>DATASET_BUDGET.chunkBytes||!c.url.startsWith(`/__atlas/datasets/${d.namespace}/`))throw Error('chunk contract');
  for(const i of d.instances) {
    if(ids.has(i.sourceKey)||!i.sourceKey.startsWith('ZA-')||i.matrix.length!==16||!i.matrix.every(Number.isFinite))throw Error('instance identity/frame');
    ids.add(i.sourceKey);
    // T99 technical dataset cannot promote holds, bindings, or visibility.
    if(i.canonicalConceptId!==null||i.learnerBinding!=='source_only_unbound'||i.defaultLearnerVisible||i.appDisplayRights!=='held_not_approved_by_this_task'||i.publicRedistribution!=='held')throw Error('source policy promotion');
    for(const level of ['overview','detail'] as const) {const lod=i.lods[level];if(!chunks.get(lod.chunk)?.resources.includes(lod.resource)||!d.resources[lod.resource])throw Error('missing resource');}
  }
  if(d.chunks.filter(c=>c.level==='overview').reduce((n,c)=>n+c.bytes,0)>DATASET_BUDGET.overviewBytes||d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)>DATASET_BUDGET.triangles)throw Error('overview budget');
  return d;
}
/** Stable fallback-first planning. Detail upgrades never displace another visible structure. */
export function planLods(dataset:Dataset,visible:Set<string>,details:Set<string>) {
  const instances=dataset.instances.filter(i=>visible.has(i.sourceKey));
  const choices=new Map(instances.map(i=>[i.sourceKey,i.lods.overview]));
  let triangles=instances.reduce((n,i)=>n+i.lods.overview.triangles,0);
  const chunks=new Set(instances.map(i=>i.lods.overview.chunk));
  let bytes=dataset.chunks.filter(c=>chunks.has(c.id)).reduce((n,c)=>n+c.geometryBytes,0);
  for(const i of instances) if(details.has(i.sourceKey)) {
    const extra=i.lods.detail.triangles-i.lods.overview.triangles;
    const chunk=dataset.chunks.find(c=>c.id===i.lods.detail.chunk)!;
    const cost=chunks.has(chunk.id)?0:chunk.geometryBytes;
    if(triangles+extra>DATASET_BUDGET.triangles||bytes+cost>DATASET_BUDGET.geometryBytes)continue;
    triangles+=extra;bytes+=cost;chunks.add(chunk.id);choices.set(i.sourceKey,i.lods.detail);
  }
  return {choices,chunks:[...chunks],triangles,bytes};
}
