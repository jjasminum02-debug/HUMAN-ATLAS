import type {Carrier,TerritoryMask} from './schema.ts';
import {maskContentHash,validateTerritoryMask} from './territoryMask.ts';
export const jsonHash=async(value:unknown)=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(value))))].map(v=>v.toString(16).padStart(2,'0')).join('');
export interface EditBindings {carrierHash:string;pointHash:string;routeHash:string}
export interface TerritoryRevision {schemaVersion:1;usage:'development_review_only';kind:'triangle_mask_revision';parentContentSha256:string;bindings:EditBindings;mask:TerritoryMask;createdAt:string;operator:'unassigned_review_operator';reviewApproval:false}
const equal=(a:Set<number>,b:Set<number>)=>a.size===b.size&&[...a].every(v=>b.has(v));
/** One topology-based editor. Strokes are atomic; original mask and geometry stay immutable. */
export class TerritoryEditSession {
  readonly base:TerritoryMask;
  private faces:Set<number>;private undoStack:Set<number>[]=[];private redoStack:Set<number>[]=[];private stroke:Set<number>|null=null;private epoch=0;private restoredMask:TerritoryMask|null=null;
  private centers:number[][]=[];private neighbors:number[][]=[];
  readonly carrier:Carrier;readonly bindings:EditBindings;
  constructor(carrier:Carrier,mask:TerritoryMask,bindings:EditBindings) {
    this.carrier=carrier;this.bindings=bindings;
    if(mask.carrierHash!==carrier.topologySha256||bindings.carrierHash!==carrier.topologySha256)throw Error('Editor carrier binding');
    this.base=structuredClone(mask);this.faces=new Set(mask.triangleIds);
    const edges=new Map<string,number[]>();
    for(let f=0;f<carrier.indices.length/3;f++) {const t=carrier.indices.slice(f*3,f*3+3);this.centers.push([0,1,2].map(k=>t.reduce((n,v)=>n+carrier.positions[v*3+k],0)/3));this.neighbors.push([]);
      for(let j=0;j<3;j++){const a=t[j],b=t[(j+1)%3],key=a<b?`${a}:${b}`:`${b}:${a}`;const faces=edges.get(key)??[];faces.push(f);edges.set(key,faces);}}
    for(const faces of edges.values())for(const a of faces)for(const b of faces)if(a!==b)this.neighbors[a].push(b);
  }
  get faceIds(){return [...this.faces].sort((a,b)=>a-b);}
  get canUndo(){return this.undoStack.length>0;}get canRedo(){return this.redoStack.length>0;}get inStroke(){return this.stroke!==null;}
  get changed(){return !equal(this.faces,new Set(this.base.triangleIds));}
  /** Geodesic adjacency expansion cannot jump to a spatially close disconnected component. */
  brushFaces(seed:number,radius:number) {
    if(!Number.isInteger(seed)||seed<0||seed>=this.centers.length||!Number.isFinite(radius)||radius<0||radius>.05)throw Error('Brush face/radius');
    const distances=new Map([[seed,0]]),queue:[number,number][]=[[seed,0]],result:number[]=[];
    while(queue.length){queue.sort((a,b)=>b[1]-a[1]);const [f,d]=queue.pop()!;if(d!==distances.get(f))continue;result.push(f);
      for(const next of this.neighbors[f]){const length=Math.hypot(...this.centers[f].map((v,k)=>v-this.centers[next][k])),nd=d+length;if(nd<=radius&&nd<(distances.get(next)??Infinity)){distances.set(next,nd);queue.push([next,nd]);}}}
    return result;
  }
  beginStroke(){if(this.stroke)throw Error('Stroke already active');this.stroke=new Set(this.faces);}
  apply(faces:readonly number[],erase:boolean){if(!this.stroke)throw Error('Begin stroke first');for(const f of faces){if(!Number.isInteger(f)||f<0||f>=this.centers.length)throw Error('Invalid face');if(erase)this.faces.delete(f);else this.faces.add(f);}this.epoch++;}
  endStroke(){if(!this.stroke)return;const before=this.stroke;this.stroke=null;if(!equal(before,this.faces)){this.undoStack.push(before);if(this.undoStack.length>100)this.undoStack.shift();this.redoStack=[];}}
  cancelStroke(){if(this.stroke){this.faces=this.stroke;this.stroke=null;this.epoch++;}}
  undo(){this.cancelStroke();const previous=this.undoStack.pop();if(previous){this.redoStack.push(this.faces);this.faces=previous;this.epoch++;}}
  redo(){this.cancelStroke();const next=this.redoStack.pop();if(next){this.undoStack.push(this.faces);this.faces=next;this.epoch++;}}
  async snapshot():Promise<TerritoryMask> {
    if(this.restoredMask&&this.restoredMask.triangleIds.join()===this.faceIds.join())return structuredClone(this.restoredMask);
    const m=structuredClone(this.base);m.triangleIds=this.faceIds;
    const weights=new Map(this.base.vertexWeights),used=[...new Set(m.triangleIds.flatMap(f=>this.carrier.indices.slice(f*3,f*3+3)))].sort((a,b)=>a-b);
    m.vertexWeights=used.map(v=>[v,weights.get(v)??1]);
    m.faceSetSha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint32Array(m.triangleIds)))].map(v=>v.toString(16).padStart(2,'0')).join('');
    if(m.faceSetSha256!==this.base.faceSetSha256){m.revision=`${this.base.revision}/edit-${m.faceSetSha256.slice(0,16)}`;m.boundaryRevision=`${this.base.boundaryRevision}/edit-${m.faceSetSha256.slice(0,16)}`;}
    m.contentSha256=await maskContentHash(m);return m;
  }
  async revision():Promise<TerritoryRevision> {if(this.inStroke)throw Error('Finish the stroke before saving');const epoch=this.epoch,mask=await this.snapshot();await this.validate(mask);if(epoch!==this.epoch||this.inStroke)throw Error('Editing changed during revision save');return {schemaVersion:1,usage:'development_review_only',kind:'triangle_mask_revision',parentContentSha256:this.base.contentSha256,bindings:{...this.bindings},mask,createdAt:new Date().toISOString(),operator:'unassigned_review_operator',reviewApproval:false};}
  async loadRevision(value:unknown) {
    if(this.inStroke)throw Error('Finish the stroke before loading');const epoch=this.epoch;const r=value as TerritoryRevision;if(!r||r.schemaVersion!==1||r.usage!=='development_review_only'||r.kind!=='triangle_mask_revision'||r.reviewApproval!==false||r.parentContentSha256!==this.base.contentSha256||JSON.stringify(r.bindings)!==JSON.stringify(this.bindings))throw Error('Revision source/point/route/carrier drift');
    await this.validate(r.mask);if(epoch!==this.epoch)throw Error('Editing changed during revision load');
    // Only mask content/revision may change. Metadata edits cannot grant rights or approval.
    const strip=(m:TerritoryMask)=>{const copy=structuredClone(m) as Partial<TerritoryMask>;for(const k of ['triangleIds','vertexWeights','revision','boundaryRevision','contentSha256','faceSetSha256'] as const)delete copy[k];return copy;};
    if(JSON.stringify(strip(r.mask))!==JSON.stringify(strip(this.base)))throw Error('Revision provenance changed');
    this.cancelStroke();this.undoStack.push(this.faces);this.redoStack=[];this.faces=new Set(r.mask.triangleIds);this.restoredMask=structuredClone(r.mask);this.epoch++;
  }
  private validate(mask:TerritoryMask){const c=this.carrier;return validateTerritoryMask(mask,c,{datasetRevision:c.datasetRevision,frameId:c.frameId,poseId:c.poseId,unit:c.unit},mask.scope==='technical_fixture');}
}
