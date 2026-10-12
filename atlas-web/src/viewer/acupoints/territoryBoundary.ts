/** Offline territory input contract. No renderer, loader or acupoint approvals. */
import type { Carrier, Side, SourceRef, Territory, Vec3 } from './schema.ts';
import { resolveAnchor, validateCarrier, verifyCarrierHash } from './anchorAdapter.ts';
import type { AnchorContext, TopologyAnchor } from './anchorAdapter.ts';

export type TerritoryBasisKind = 'surface_learning_connection' | 'cutaneous' | 'sinew_projection' | 'professor_interpretation';
export interface BoundaryControl { id: string; vertex: number; anchor: TopologyAnchor }
export interface TerritoryBoundaryDraft extends Pick<Territory,'id'|'channel'|'side'|'revision'|'kind'|'boundaryRevision'|'sources'|'interpretation'|'professorReview'> {
  schemaVersion: 1; usage: 'offline_authoring_only'; basisKind: TerritoryBasisKind;
  author: 'ai' | 'human'; canonicalBoundaryClaim: false; precision: 'educational_approximation_not_skin';
  context: AnchorContext;
  rights: {localObservation:'supported'|'held'; publicRedistribution:'held'|'supported'; sourceIds:string[]};
  carrierBinding: {id:string; topologySha256:string; manifest:string; manifestSha256:string; component:string; noNewGeometry:true};
  components: {id:string; carrierId:string; seedTriangle:number; loops:{role:'outer'|'hole'; controls:BoundaryControl[]}[]}[];
  limitations: string[];
}
export interface TerritoryDefinitionInput {
  channel:string; nameKo:string; sideRule:'independent_bilateral_annotations'|'midline'; revision:string;
  kind:Territory['kind']; basisKind:TerritoryBasisKind;
  status:'boundary_input_ready_partial'|'evidence_ledger_only';
  canonicalBoundaryClaim:false; interpretation:Territory['interpretation']; author:'ai'|'human';
  professorReview:Territory['professorReview']; publicRedistribution:'held'|'supported';
  sourceRelations:{sourceId:string;summary:string;scope:string}[];
  types:Record<'surfaceLearning'|'sinew'|'cutaneous'|'professorInterpretation',{
    kind:TerritoryBasisKind;status:string;sourceId?:string|null;remaining?:string;reason?:string;indicator?:string;scope?:string;
  }>;
  viewDrafts:Record<'anterior'|'posterior'|'lateral',{indicators:string[];status:string;boundaryRule:string;sourceBoundary:false}>;
  uncertainties:string[]; finalMasks:0;
}
const edgeKey = (a:number,b:number) => a<b ? `${a}:${b}` : `${b}:${a}`;
const sides:Side[]=['right','left','midline'];
const bases:TerritoryBasisKind[]=['surface_learning_connection','cutaneous','sinew_projection','professor_interpretation'];
const channels=['LU','LI','ST','SP','HT','SI','BL','KI','PC','TE','GB','LR','CV','GV'];

/** Validate explicit loops against frozen shared topology. Face IDs are never exported here.
 * The adjacency traversal proves the boundary is executable; AT21 owns mask production.
 */
export async function replayTerritoryBoundary(d:TerritoryBoundaryDraft,c:Carrier,context:AnchorContext) {
  if(d.schemaVersion!==1 || d.usage!=='offline_authoring_only' || !sides.includes(d.side) || !bases.includes(d.basisKind) || !d.components.length) throw Error('boundary input contract');
  if(!channels.includes(d.channel) || (['CV','GV'].includes(d.channel)!==(d.side==='midline'))) throw Error('boundary channel/laterality');
  const kind=d.basisKind==='cutaneous'?'cutaneous':d.basisKind==='sinew_projection'?'sinew_projection':'teaching_region';
  if(d.kind!==kind) throw Error('boundary theory type mismatch');
  if(d.canonicalBoundaryClaim!==false || d.precision!=='educational_approximation_not_skin' || !['ai','human'].includes(d.author) || !d.limitations.length || !d.sources.length) throw Error('boundary provenance');
  if(['CV','GV'].includes(d.channel) && d.basisKind==='sinew_projection') throw Error('CV/GV are not additional jingjin');
  if(d.rights.localObservation!=='supported' || !d.rights.sourceIds.length) throw Error('boundary local rights');
  if(d.carrierBinding.id!==c.id || d.carrierBinding.topologySha256!==c.topologySha256 || d.carrierBinding.noNewGeometry!==true || d.side!==c.side) throw Error('boundary carrier binding');
  validateCarrier(c,context);
  if(Object.keys(context).some(k=>d.context[k as keyof AnchorContext]!==context[k as keyof AnchorContext])) throw Error('boundary context');
  await verifyCarrierHash(c);
  const triangles=Array.from({length:c.indices.length/3},(_,i)=>c.indices.slice(i*3,i*3+3));
  const edges=new Map<string,number[]>();
  triangles.forEach((t,fi)=>t.forEach((a,j)=>{const key=edgeKey(a,t[(j+1)%3]);const fs=edges.get(key)??[];fs.push(fi);edges.set(key,fs);}));
  if([...edges.values()].some(fs=>fs.length>2)) throw Error('nonmanifold carrier edges');
  const adjacency=triangles.map(()=>[] as {face:number;edge:string}[]);
  edges.forEach((fs,key)=>{if(fs.length===2){adjacency[fs[0]].push({face:fs[1],edge:key});adjacency[fs[1]].push({face:fs[0],edge:key});}});
  const occupied=new Set<number>();const componentCounts:number[]=[];const controlPositions:Vec3[]=[];
  for(const component of d.components) {
    if(component.carrierId!==c.id || !Number.isInteger(component.seedTriangle) || !triangles[component.seedTriangle] || component.loops.filter(l=>l.role==='outer').length!==1) throw Error('boundary component');
    const barriers=new Set<string>();const vertices=new Set<number>();
    for(const loop of component.loops) {
      if(!['outer','hole'].includes(loop.role) || loop.controls.length<3) throw Error('boundary loop');
      for(let j=0;j<loop.controls.length;j++) {
        const control=loop.controls[j],next=loop.controls[(j+1)%loop.controls.length];
        if(!Number.isInteger(control.vertex) || control.vertex<0 || control.vertex>=c.positions.length/3 || vertices.has(control.vertex)) throw Error('pinched or duplicate boundary vertex');
        vertices.add(control.vertex);
        const p=resolveAnchor(c,control.anchor).position.toArray() as Vec3;
        if(p.some((n,k)=>Math.abs(n-c.positions[control.vertex*3+k])>1e-9)) throw Error('control is not its addressed vertex');
        controlPositions.push(p);
        const key=edgeKey(control.vertex,next.vertex);
        if(!edges.has(key) || barriers.has(key)) throw Error('boundary jumps across unsupported topology');
        barriers.add(key);
      }
    }
    const inside=new Set<number>([component.seedTriangle]);const stack=[component.seedTriangle];
    while(stack.length) {
      const f=stack.pop()!;
      for(const e of adjacency[f])if(!barriers.has(e.edge)&&!inside.has(e.face)){inside.add(e.face);stack.push(e.face);}
    }
    const boundary=new Set<string>();
    for(const [key,fs] of edges)if(fs.filter(f=>inside.has(f)).length===1)boundary.add(key);
    if(boundary.size!==barriers.size || [...boundary].some(key=>!barriers.has(key))) throw Error('seed leaks beyond boundary or omitted hole');
    if([...inside].some(f=>occupied.has(f))) throw Error('overlapping contour components');
    inside.forEach(f=>occupied.add(f));componentCounts.push(inside.size);
  }
  const bytes=new Uint32Array([...occupied].sort((a,b)=>a-b));
  const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  return {componentCounts,controlPositions,triangleIds:Array.from(bytes),faceSetSha256:digest,maskCreated:false as const,sourceBoundaryConfirmed:false as const};
}

/** Historical AT20 audit remains non-exporting; mask compilation reuses the same traversal. */
export async function validateTerritoryBoundary(d:TerritoryBoundaryDraft,c:Carrier,context:AnchorContext) {
  const {triangleIds:_ids,...audit}=await replayTerritoryBoundary(d,c,context);return audit;
}

/** Converts provenance to the existing Territory vocabulary only after AT21 authors a mask. */
export type TerritoryMaskProvenance = Pick<Territory,'kind'|'interpretation'|'professorReview'> & {
  basisKind:TerritoryBasisKind; author:'ai'|'human'; sources:SourceRef[];
  carrierHash:string; boundaryRevision:string; publicRedistribution:'held'|'supported';
};
