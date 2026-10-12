import * as THREE from 'three';
import type { Carrier, TerritoryMask } from './schema.ts';
import { validateCarrier, verifyCarrierHash, type AnchorContext } from './anchorAdapter.ts';
export interface TerritoryPackage extends AnchorContext {schemaVersion:1;usage:'local_learning_areas';masks:TerritoryMask[]}
export type TerritoryMode='selected'|'comparison';
// Muted display colours only; they do not encode anatomy, efficacy or review status.
const colours:Record<string,number>={LU:0x438b9a,LI:0x9a7354,ST:0xaa8955,SP:0x859266,HT:0xa66b6b,SI:0x84779b,BL:0x6f819e,KI:0x708e86,PC:0x967487,TE:0x737da5,GB:0x6c946c,LR:0x938568,CV:0x8d8f70,GV:0x778b94};
const hash=async(bytes:BufferSource)=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
export const maskContentHash=(m:Pick<TerritoryMask,'triangleIds'|'vertexWeights'>)=>hash(new TextEncoder().encode(JSON.stringify([m.triangleIds,m.vertexWeights])));
/** Independent mask provenance never grants a point position or clinical boundary. */
export async function validateTerritoryMask(m:TerritoryMask,c:Carrier,context:AnchorContext) {
  validateCarrier(c,context);await verifyCarrierHash(c);
  if(!['LU','LI','ST','SP','HT','SI','BL','KI','PC','TE','GB','LR','CV','GV'].includes(m.channel)||(['CV','GV'].includes(m.channel)!==(m.side==='midline')))throw Error('territory channel/laterality');
  if(m.schemaVersion!==1||m.scope!=='real_input'||m.carrierId!==c.id||m.carrierRevision!==c.revision||m.carrierHash!==c.topologySha256||m.side!==c.side
    ||m.datasetRevision!==context.datasetRevision||m.frameId!==context.frameId||m.poseId!==context.poseId||m.unit!=='m')throw Error('stale territory binding');
  const kind=m.basisKind==='cutaneous'?'cutaneous':m.basisKind==='sinew_projection'?'sinew_projection':'teaching_region';
  if(m.kind!==kind||!['ai','human'].includes(m.author)||m.canonicalBoundaryClaim!==false||m.precision!=='educational_approximation_not_skin'
    ||m.rights.localObservation!=='supported'||!m.rights.sourceIds.length||!m.sources.length||!m.boundaryRevision||!m.revision
    ||!['surface_learning_connection','cutaneous','sinew_projection','professor_interpretation'].includes(m.basisKind)
    ||(['CV','GV'].includes(m.channel)&&m.basisKind==='sinew_projection'))throw Error('territory provenance/type');
  if(!m.triangleIds.length||new Set(m.triangleIds).size!==m.triangleIds.length||!m.triangleIds.every((f,i)=>Number.isInteger(f)&&f>=0&&f<c.indices.length/3&&(i===0||f>m.triangleIds[i-1])))throw Error('territory face IDs');
  const used=new Set(m.triangleIds.flatMap(f=>c.indices.slice(f*3,f*3+3))),vertices=new Set<number>();
  for(const [v,w] of m.vertexWeights){if(!used.has(v)||vertices.has(v)||!Number.isFinite(w)||w<0||w>1)throw Error('territory visual weights');vertices.add(v);}
  if(vertices.size!==used.size)throw Error('missing territory weights');
  if(!/^[a-f0-9]{64}$/.test(m.boundaryInputSha256)||await hash(new Uint32Array(m.triangleIds))!==m.faceSetSha256||await maskContentHash(m)!==m.contentSha256)throw Error('territory mask hash');
}
export function territoryEdges(m:Pick<TerritoryMask,'triangleIds'>,c:Carrier) {
  const edges=new Map<string,{pair:[number,number];count:number}>();
  for(const f of m.triangleIds){const t=c.indices.slice(f*3,f*3+3);for(let j=0;j<3;j++){const a=t[j],b=t[(j+1)%3],key=a<b?`${a}:${b}`:`${b}:${a}`,e=edges.get(key);if(e)e.count++;else edges.set(key,{pair:[a,b],count:1});}}
  return [...edges.values()].filter(e=>e.count===1).flatMap(e=>e.pair);
}
/** Only this tiny compact package is lazy fetched. It contains no source geometry/evidence. */
export async function loadTerritoryPackage(carriers:Carrier[],context:AnchorContext,signal:AbortSignal,cancelled:()=>boolean) {
  const {default:url}=await import('../../../../atlas-data/acupoints/territories/lung-r1/masks.json?url');
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  const response=await fetch(url,{signal});if(!response.ok)throw Error('학습 영역을 열 수 없습니다.');
  const bytes=await response.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');
  const d=JSON.parse(new TextDecoder().decode(bytes)) as TerritoryPackage;
  if(d.schemaVersion!==1||d.usage!=='local_learning_areas'||Object.keys(context).some(k=>d[k as keyof AnchorContext]!==context[k as keyof AnchorContext])||new Set(d.masks.map(m=>m.id)).size!==d.masks.length)throw Error('Invalid territory package');
  const masks=d.masks.filter(m=>carriers.some(c=>c.id===m.carrierId));
  for(const m of masks){await validateTerritoryMask(m,carriers.find(c=>c.id===m.carrierId)!,context);if(cancelled())throw new DOMException('Cancelled','AbortError');}
  return {masks,encodedBytes:bytes.byteLength};
}
/** Shared positions/normals, compact index and weight buffers. No anatomical raycast target. */
export class TerritoryMaskLayer {
  readonly group=new THREE.Group();
  private draws:{mask:TerritoryMask;mesh:THREE.Mesh;outline:THREE.LineSegments}[]=[];
  private carriers:Map<string,{carrier:Carrier;geometry:THREE.BufferGeometry}>;
  constructor(masks:TerritoryMask[],carriers:Map<string,{carrier:Carrier;geometry:THREE.BufferGeometry}>) {
    this.carriers=carriers;
    this.group.name='SurfaceLearningTerritories';
    // Stable draw order makes overlap deterministic, independent of request order and camera distance.
    for(const [order,m] of [...masks].sort((a,b)=>a.id.localeCompare(b.id)).entries()) {
      const shared=carriers.get(m.carrierId);if(!shared)throw Error('Missing shared territory geometry');
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',shared.geometry.getAttribute('position'));geometry.setAttribute('normal',shared.geometry.getAttribute('normal'));
      geometry.setIndex(m.triangleIds.flatMap(f=>shared.carrier.indices.slice(f*3,f*3+3)));
      const weights=new Float32Array(shared.carrier.positions.length/3);for(const [v,w] of m.vertexWeights)weights[v]=w;
      geometry.setAttribute('territoryWeight',new THREE.BufferAttribute(weights,1));
      const material=new THREE.MeshBasicMaterial({color:colours[m.channel]??0xb47587,transparent:true,opacity:.27,depthTest:true,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
      material.name='EducationalSurfaceArea';
      material.onBeforeCompile=shader=>{
        shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nattribute float territoryWeight; varying float vTerritoryWeight;').replace('#include <begin_vertex>','#include <begin_vertex>\nvTerritoryWeight = territoryWeight;');
        shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying float vTerritoryWeight;').replace('#include <color_fragment>','#include <color_fragment>\ndiffuseColor.a *= vTerritoryWeight;');
      };
      material.customProgramCacheKey=()=> 'territory-visual-weight-v1';
      const mesh=new THREE.Mesh(geometry,material);mesh.name=m.id;mesh.renderOrder=100+order;mesh.raycast=()=>{};
      const edgeGeometry=new THREE.BufferGeometry();edgeGeometry.setAttribute('position',shared.geometry.getAttribute('position'));edgeGeometry.setIndex(territoryEdges(m,shared.carrier));
      const outline=new THREE.LineSegments(edgeGeometry,new THREE.LineBasicMaterial({color:material.color,transparent:true,opacity:.48,depthTest:true,depthWrite:false}));outline.name=m.id+'-boundary';outline.renderOrder=200+order;outline.raycast=()=>{};
      this.group.add(mesh,outline);this.draws.push({mask:m,mesh,outline});
    }
  }
  show(enabled:boolean,mode:TerritoryMode,channel:string) {
    this.group.visible=enabled;
    for(const [order,{mask,mesh,outline}] of this.draws.entries()){const selected=mask.channel===channel;mesh.visible=outline.visible=mode==='comparison'||selected;mesh.renderOrder=100+order+(selected?50:0);outline.renderOrder=200+order+(selected?50:0);(mesh.material as THREE.MeshBasicMaterial).opacity=selected?.27:.10;(outline.material as THREE.LineBasicMaterial).opacity=selected?.48:.25;}
  }
  diagnostics() {
    const arrays=new Set<ArrayBufferLike>();let triangles=0;
    for(const {mesh,outline} of this.draws){for(const o of [mesh,outline]){for(const [name,a] of Object.entries(o.geometry.attributes))if(name!=='position'&&name!=='normal')arrays.add(a.array.buffer);if(o.geometry.index)arrays.add(o.geometry.index.array.buffer);}triangles+=mesh.geometry.index!.count/3;}
    return {maskCount:this.draws.length,visibleMasks:this.group.visible?this.draws.filter(d=>d.mesh.visible).map(d=>d.mask.id):[],triangles,additionalBufferBytes:[...arrays].reduce((n,b)=>n+b.byteLength,0),sharedPositionBuffers:this.draws.every(d=>d.mesh.geometry.getAttribute('position')===this.carriers.get(d.mask.carrierId)!.geometry.getAttribute('position')),drawCalls:this.group.visible?this.draws.filter(d=>d.mesh.visible).length*2:0,fixtureMasks:this.draws.filter(d=>d.mask.scope==='technical_fixture').length,bindings:this.draws.map(d=>({id:d.mask.id,side:d.mask.side,channel:d.mask.channel,carrierHash:d.mask.carrierHash,boundaryRevision:d.mask.boundaryRevision,contentSha256:d.mask.contentSha256,faces:d.mask.triangleIds.length,weightIsVisualOnly:true})),depthTest:true,depthWrite:false,raycastTargets:0};
  }
  dispose() {
    this.group.removeFromParent();
    for(const {mesh,outline} of this.draws)for(const o of [mesh,outline]){
      o.geometry.dispose();(o.material as THREE.Material).dispose();
    }
    // These attributes belong only to this overlay. Release shared GPU buffers even if the
    // hidden canonical mesh never registered a WebGL dispose listener. Invalidate any base
    // VAO as well; CPU attributes/topology stay intact and can be uploaded on the next ON.
    for(const id of new Set(this.draws.map(d=>d.mask.carrierId)))this.carriers.get(id)!.geometry.dispose();
    this.group.clear();this.draws=[];
  }
}
