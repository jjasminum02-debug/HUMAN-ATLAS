import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { Carrier } from '../acupoints/schema.ts';
import { validateCarrier, verifyCarrierHash } from '../acupoints/anchorAdapter.ts';
import { skinWithinBudget, validateSkinAsset, type SkinAsset, type SkinCost } from './skinContract.ts';
import { skinLayers, skinReservationCost } from './skinRegistry.ts';

const digest = async (b: ArrayBuffer) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', b))].map(n=>n.toString(16).padStart(2,'0')).join('');
const disposeGroup = (group: THREE.Object3D) => {
  const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>();
  group.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));}});
  geometries.forEach(g=>g.dispose()); materials.forEach(m=>m.dispose()); group.removeFromParent();
};
/** One immutable reference topology, no LOD substitution or pose/scale conversion at runtime. */
export async function decodeSkin(bytes: ArrayBuffer, asset: SkinAsset, review = false) {
  if (bytes.byteLength !== asset.bytes || await digest(bytes) !== asset.sha256) throw Error('Skin GLB hash/bytes');
  const view = new DataView(bytes);
  if (view.getUint32(0,true)!==0x46546c67 || view.getUint32(4,true)!==2 || view.getUint32(8,true)!==bytes.byteLength) throw Error('Skin GLB format');
  const doc = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes,20,view.getUint32(12,true))));
  if (doc.buffers?.length!==1 || doc.buffers[0].uri || doc.images?.length || doc.animations?.length || doc.skins?.length
    || doc.extensionsRequired?.length || doc.nodes?.length!==1 || doc.meshes?.length!==1 || doc.meshes[0].primitives.length!==1
    || doc.meshes[0].primitives[0].mode!==4) throw Error('Skin must be embedded static reference geometry');
  const node=doc.nodes[0],identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
  if (node.translation || node.rotation || node.scale || node.matrix && JSON.stringify(node.matrix)!==JSON.stringify(identity)
    || node.extras?.unit!==asset.unit || node.extras?.frame!==asset.frameId || node.extras?.poseId!==asset.poseId
    || !review && (node.extras?.fitAcceptancePassed!==true || node.extras?.learnerEligible!==true)) throw Error('Skin embedded frame/fit acceptance');
  const gltf=await new GLTFLoader().parseAsync(bytes,'');
  try {
    const meshes:THREE.Mesh[]=[];gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh)meshes.push(o);});
    if(meshes.length!==1)throw Error('Skin mesh count');
    const geometry=meshes[0].geometry,p=geometry.getAttribute('position'),index=geometry.index;
    if(!index || index.count/3!==asset.triangles)throw Error('Skin triangle count');
    const carrier:Carrier={id:asset.id,revision:asset.revision,topologySha256:asset.topologySha256,datasetRevision:asset.datasetRevision,
      frameId:asset.frameId,unit:'m',poseId:asset.poseId,side:'midline',coverage:'whole_body',kind:'registered_skin',precision:'landmarks_verified',
      positions:Array.from({length:p.count},(_,i)=>[p.getX(i),p.getY(i),p.getZ(i)]).flat(),indices:Array.from(index.array),
      rights:{source:'MakeHuman core CC0; AI fitted derivative',localObservation:asset.localObservation,publicRedistribution:asset.publicRedistribution,professorReview:asset.professorReview}};
    // The review mesh is only a geometry fixture; it grants no landmarks or point eligibility.
    if(review)carrier.precision='coarse_not_skin';
    validateCarrier(carrier,asset);await verifyCarrierHash(carrier);
    const buffers=new Set<ArrayBufferLike>();for(const a of Object.values(geometry.attributes) as THREE.BufferAttribute[])buffers.add(a.array.buffer);buffers.add(index.array.buffer);
    const geometryBytes=[...buffers].reduce((n,b)=>n+b.byteLength,0);
    if(geometryBytes!==asset.geometryBytes)throw Error('Skin decoded cost mismatch');
    (Array.isArray(meshes[0].material)?meshes[0].material:[meshes[0].material]).forEach(m=>m.dispose());
    const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0xc9a080,roughness:.94,metalness:0,side:THREE.FrontSide}));
    mesh.name=review?'SkinGeometryReviewNotAccepted':'CanonicalSkin';mesh.raycast=()=>{};mesh.renderOrder=0;
    return {mesh,carrier,cost:{encodedBytes:bytes.byteLength,geometryBytes,triangles:index.count/3}};
  } catch(error) {disposeGroup(gltf.scene);throw error;}
}

/** Abortable session cache: OFF releases all geometry/materials; there is no per-frame callback. */
export class SkinLayer {
  private generation=0;
  private request:AbortController|null=null;
  private surface:Awaited<ReturnType<typeof decodeSkin>>|null=null;
  private dead=false;
  private extra:SkinCost={encodedBytes:0,geometryBytes:0,triangles:0};
  private listeners=new Set<()=>void>();
  private removeMotion:()=>void;
  constructor(private adapter:DatasetSceneAdapter,readonly asset:SkinAsset,private review=false) {
    if(skinLayers.has(adapter))throw Error('Only one skin layer per anatomy scene');
    const d=adapter.resources.dataset;validateSkinAsset(asset,{datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??''},review);
    skinLayers.set(adapter,this);this.removeMotion=adapter.onSourceMotionStart(()=>this.off());
    this.extra=skinReservationCost(adapter);
    adapter.scene.renderer.domElement.addEventListener('webglcontextlost',this.off);
    this.inspect('off');
  }
  private baseCost():SkinCost {
    const d=this.adapter.resources.dataset;
    return {encodedBytes:d.chunks.filter(c=>c.level==='overview'&&!c.selectionScoped).reduce((n,c)=>n+c.bytes,0)+Math.max(0,...d.chunks.filter(c=>c.selectionScoped).map(c=>c.bytes)),geometryBytes:this.adapter.resources.queue.bytes,triangles:d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)};
  }
  get sharedSurface(){return this.surface?{carrier:this.surface.carrier,geometry:this.surface.mesh.geometry,mesh:this.surface.mesh}:null;}
  get visible(){return Boolean(this.surface);}
  subscribe(listener:()=>void){this.listeners.add(listener);return()=>{this.listeners.delete(listener);};}
  /** Reserve existing overlay/mask residency too; never relax the shared budget. */
  reserve(extra:SkinCost) {
    this.extra=extra;
    if(this.surface&&!skinWithinBudget(this.baseCost(),this.surface.cost,extra))this.off();
  }
  async on() {
    if(this.dead || this.surface)return;
    this.off();const token=++this.generation,abort=new AbortController();this.request=abort;
    const cancelled=()=>this.dead||abort.signal.aborted||token!==this.generation;
    try {
      if(this.adapter.resources.motionOverrides.size || this.adapter.scene.cameraOwner==='motion')throw Error('피부는 복원된 정지 자세에서만 표시할 수 있습니다.');
      const declared={encodedBytes:this.asset.bytes,geometryBytes:this.asset.geometryBytes,triangles:this.asset.triangles};
      if(!skinWithinBudget(this.baseCost(),declared,this.extra))throw Error('피부가 기존 장면 예산을 초과합니다.');
      this.inspect('loading');const response=await fetch(this.asset.url,{signal:abort.signal});if(!response.ok)throw Error('피부 자료를 읽을 수 없습니다.');
      const bytes=await response.arrayBuffer();if(cancelled())return;
      const decoded=await decodeSkin(bytes,this.asset,this.review);
      if(cancelled() || this.adapter.resources.motionOverrides.size || this.adapter.scene.cameraOwner==='motion'){disposeGroup(decoded.mesh);return;}
      if(!skinWithinBudget(this.baseCost(),decoded.cost,this.extra)){disposeGroup(decoded.mesh);throw Error('피부가 기존 장면 예산을 초과합니다.');}
      this.surface=decoded;this.adapter.scene.root.add(decoded.mesh);this.inspect('on');this.changed();
    } catch(error) {if(!cancelled()){this.inspect('error');throw error;}}
    finally {if(!cancelled())this.request=null;}
  }
  setOpacity(value:number) {
    if(!Number.isFinite(value)||value<.1||value>1)throw Error('Skin opacity');
    const material=this.surface?.mesh.material as THREE.MeshStandardMaterial|undefined;if(!material)return;
    material.opacity=value;material.transparent=value<1;material.depthWrite=value===1;material.needsUpdate=true;this.changed();
  }
  off=()=> {
    ++this.generation;this.request?.abort();this.request=null;
    if(this.surface){disposeGroup(this.surface.mesh);this.surface=null;}
    this.inspect('off');this.changed();
  };
  private changed(){this.adapter.scene.requestRender();for(const listener of this.listeners)listener();}
  private inspect(state:string) {
    this.adapter.scene.renderer.domElement.dataset.skinLayer=JSON.stringify({state,root:this.adapter.scene.root.uuid,review:this.review,learnerEligible:!this.review&&this.asset.learnerEligible,assetHash:this.asset.sha256,topologyHash:this.asset.topologySha256,pose:this.asset.poseId,cost:this.surface?.cost??{encodedBytes:0,geometryBytes:0,triangles:0},extra:this.extra,frameCallbacks:0});
  }
  dispose(){if(this.dead)return;this.off();this.dead=true;this.removeMotion();this.adapter.scene.renderer.domElement.removeEventListener('webglcontextlost',this.off);this.listeners.clear();skinLayers.delete(this.adapter);delete this.adapter.scene.renderer.domElement.dataset.skinLayer;}
}
