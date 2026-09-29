import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { ResourceQueue } from '../wholeBody/resources.ts';
import { DATASET_BUDGET, planLods, type Dataset } from './schema.ts';
type Resource = {meshes:Map<string,THREE.BufferGeometry>;bytes:number};
/** Adds resource instances to an existing scene root. Owns no renderer, camera, or learner bindings. */
export class DatasetResources {
  readonly dataset:Dataset;readonly root:THREE.Group;readonly queue:ResourceQueue<Resource>;
  readonly nodes=new Map<string,THREE.Mesh>(); readonly materials=new Map<string,THREE.MeshStandardMaterial>();
  readonly inspection:boolean;readonly invalidate:()=>void;private visible=new Set<string>();private detail=new Set<string>();
  private disposed=false;
  constructor(dataset:Dataset,root:THREE.Group,inspection=false,invalidate:()=>void=()=>{}) {
    this.dataset=dataset;this.root=root;this.inspection=inspection;this.invalidate=invalidate;
    this.queue=new ResourceQueue((id,signal)=>this.load(id,signal),r=>{for(const g of new Set(r.meshes.values()))g.dispose();},()=>this.sync(),2,
      {maxBytes:DATASET_BUDGET.geometryBytes,measure:r=>r.bytes});
  }
  demand(sourceKeys:string[],details:string[]=[]) {
    if(this.disposed)return;
    // Local engineering inspection is explicit and never modifies catalog policy.
    this.visible=new Set(this.dataset.instances.filter(i=>sourceKeys.includes(i.sourceKey)&&(this.inspection||i.defaultLearnerVisible&&i.appDisplayRights==='approved')).map(i=>i.sourceKey));
    this.detail=new Set(details);
    this.sync(); // Remove obsolete meshes before queue eviction can dispose their geometries.
    const plan=planLods(this.dataset,this.visible,this.detail);
    const overview=this.dataset.instances.filter(i=>this.visible.has(i.sourceKey)).map(i=>i.lods.overview.chunk);
    this.queue.demand(plan.chunks,overview);
  }
  private async load(id:string,signal:AbortSignal):Promise<Resource> {
    const chunk=this.dataset.chunks.find(c=>c.id===id);if(!chunk)throw Error('unknown chunk');
    const response=await fetch(chunk.url,{signal});if(!response.ok)throw Error('chunk unavailable');
    const bytes=await response.arrayBuffer();
    const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    if(hash!==chunk.sha256||bytes.byteLength!==chunk.bytes)throw Error('chunk hash');
    if(signal.aborted)throw new DOMException('Aborted','AbortError');
    const view=new DataView(bytes);const size=view.getUint32(12,true);
    const doc=JSON.parse(new TextDecoder().decode(new Uint8Array(bytes,20,size)));
    if(doc.images?.length||doc.animations?.length||doc.skins?.length||doc.buffers?.some((b:{uri?:string})=>b.uri))throw Error('unexpected external/animated resource');
    const gltf=await new GLTFLoader().parseAsync(bytes,'');const meshes=new Map<string,THREE.BufferGeometry>();
    const materials=new Set<THREE.Material>();const buffers=new Set<ArrayBufferLike>();
    try {
      gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh){
        const key=o.userData.resourceKey as string;
        if(!chunk.resources.includes(key)||meshes.has(key)||!o.geometry.index)throw Error('resource identity/index');
        meshes.set(key,o.geometry);
        for(const a of Object.values(o.geometry.attributes) as THREE.BufferAttribute[])buffers.add(a.array.buffer);
        buffers.add(o.geometry.index.array.buffer);
        for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);
      }});
      if(meshes.size!==chunk.resources.length)throw Error('missing resource');
      const size=[...buffers].reduce((n,b)=>n+b.byteLength,0);
      // GLTFLoader may share the entire BIN buffer; measure real retained arrays, not estimates.
      return {meshes,bytes:size};
    }catch(e){gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.dispose();});throw e;}
    finally {for(const m of materials)m.dispose();}
  }
  private sync() {
    if(this.disposed)return;
    const plan=planLods(this.dataset,this.visible,this.detail);
    for(const [key,node] of this.nodes)if(!this.visible.has(key)){node.removeFromParent();this.nodes.delete(key);}
    for(const instance of this.dataset.instances) {
      if(!this.visible.has(instance.sourceKey))continue;
      const choice=plan.choices.get(instance.sourceKey)!;
      const wanted=this.queue.loaded.get(choice.chunk)?.meshes.get(choice.resource);
      const geometry=wanted??this.queue.loaded.get(instance.lods.overview.chunk)?.meshes.get(instance.lods.overview.resource);
      if(!geometry)continue;
      let node=this.nodes.get(instance.sourceKey);
      if(!node) {
        let material=this.materials.get(instance.kind);
        if(!material){material=new THREE.MeshStandardMaterial({color:instance.kind==='skeletal_surface'?0xd8cfae:instance.kind==='musculoskeletal_accessory'?0xc2a89b:0xa65448,roughness:.78});this.materials.set(instance.kind,material);}
        node=new THREE.Mesh(geometry,material);node.name=instance.sourceKey;node.matrixAutoUpdate=false;node.matrix.fromArray(instance.matrix);
        node.userData={sourceKey:instance.sourceKey,sourceName:instance.sourceName,learnerBinding:instance.learnerBinding,engineeringInspection:this.inspection};
        this.nodes.set(instance.sourceKey,node);this.root.add(node);
      }else node.geometry=geometry;
      node.userData.level=wanted?'requested':'overview-fallback';
    }
    this.invalidate();
  }
  dispose(){if(this.disposed)return;this.disposed=true;for(const n of this.nodes.values())n.removeFromParent();this.nodes.clear();this.queue.dispose();for(const m of this.materials.values())m.dispose();this.materials.clear();}
}
