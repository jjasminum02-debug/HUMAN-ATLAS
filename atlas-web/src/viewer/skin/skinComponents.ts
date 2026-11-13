import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DATASET_BUDGET } from '../datasets/schema.ts';
import type { AnchorContext } from '../acupoints/anchorAdapter.ts';

/** Source-derived static surfaces beside the canonical carrier. They carry no skin anchors. */
export interface SkinComponents extends AnchorContext {
  schemaVersion: number; id: string; url: string; sha256: string; bytes: number;
  geometryBytes: number; triangles: number; roles: string[];
  nativeSourceSha256: string; derivedMappingSha256: string;
  localObservation: string; publicRedistribution: string; professorReview: string;
}
export function validateSkinComponents(a: SkinComponents, skin: AnchorContext) {
  if(a.schemaVersion!==1 || !a.id || !a.url || a.frameId!==skin.frameId || a.poseId!==skin.poseId || a.unit!=='m'
    || a.datasetRevision!==skin.datasetRevision || a.localObservation!=='supported'
    || ![a.sha256,a.nativeSourceSha256,a.derivedMappingSha256].every(x=>/^[a-f0-9]{64}$/.test(x))
    || ![a.bytes,a.geometryBytes,a.triangles].every(x=>Number.isSafeInteger(x)&&x>0)
    || a.bytes>DATASET_BUDGET.chunkBytes || !a.roles.length || new Set(a.roles).size!==a.roles.length
    || a.roles.some(x=>!['sclera','iris','cornea','lens'].includes(x)))throw Error('Skin component frame/source/cost');
}
export function validateSkinComponentDocument(doc: any, asset: SkinComponents) {
  if(doc.buffers?.length!==1 || doc.buffers[0].uri || doc.images?.length || doc.animations?.length || doc.skins?.length
    || doc.extensionsUsed?.length || doc.extensionsRequired?.length || !doc.nodes?.length || doc.nodes.length>16
    || doc.meshes?.length!==doc.nodes.length || doc.scenes?.length!==1 || doc.scene!==0
    || doc.scenes[0].nodes?.length!==doc.nodes.length || new Set(doc.scenes[0].nodes).size!==doc.nodes.length
    || doc.scenes[0].nodes.some((x:number)=>!Number.isInteger(x)||x<0||x>=doc.nodes.length)) throw Error('Skin component static document');
  const seen=new Set<string>();
  for(const [i,n] of doc.nodes.entries()) {
    const key=`${n.extras?.role}:${n.extras?.side}`;
    if(n.mesh!==i || n.children?.length || n.translation || n.rotation || n.scale || n.matrix
      || n.extras?.frame!==asset.frameId || n.extras?.poseId!==asset.poseId || n.extras?.unit!=='m'
      || !asset.roles.includes(n.extras?.role) || !['left','right'].includes(n.extras?.side)
      || n.extras?.sourceKey!==`ZA-original:${({sclera:'Sclera',iris:'Iris',cornea:'Cornea',lens:'Lens'} as Record<string,string>)[n.extras?.role]}.${n.extras?.side==='left'?'l':'r'}` || seen.has(key)
      || doc.meshes[i].primitives?.length!==1 || doc.meshes[i].primitives[0].mode!==4
      || doc.meshes[i].primitives[0].targets)throw Error('Skin component role/frame');
    seen.add(key);
  }
}
export function disposeSkinComponents(group: THREE.Object3D) {
  const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>();
  group.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));}});
  geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());group.removeFromParent();
}
export async function decodeSkinComponents(bytes:ArrayBuffer,asset:SkinComponents) {
  const sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(bytes.byteLength!==asset.bytes || sha!==asset.sha256)throw Error('Skin component hash/bytes');
  const view=new DataView(bytes);
  if(bytes.byteLength<28 || view.getUint32(0,true)!==0x46546c67 || view.getUint32(4,true)!==2 || view.getUint32(8,true)!==bytes.byteLength)throw Error('Skin component GLB');
  const doc=JSON.parse(new TextDecoder().decode(new Uint8Array(bytes,20,view.getUint32(12,true))));validateSkinComponentDocument(doc,asset);
  const gltf=await new GLTFLoader().parseAsync(bytes,'');
  try {
    let triangles=0;const buffers=new Set<ArrayBufferLike>();let count=0;
    gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh){
      count++;const p=o.geometry.getAttribute('position'),index=o.geometry.index;if(!index||!p)throw Error('Skin component buffers');
      for(let i=0;i<p.array.length;i++)if(!Number.isFinite(p.array[i]))throw Error('Skin component nonfinite');
      triangles+=index.count/3;for(const a of Object.values(o.geometry.attributes) as THREE.BufferAttribute[])buffers.add(a.array.buffer);buffers.add(index.array.buffer);
      o.raycast=()=>{};o.renderOrder=o.userData.role==='cornea'?1:0;
      for(const m of (Array.isArray(o.material)?o.material:[o.material]) as THREE.MeshStandardMaterial[]){m.side=THREE.FrontSide;if(o.userData.role==='cornea')m.depthWrite=false;}
    }});
    const geometryBytes=[...buffers].reduce((sum,b)=>sum+b.byteLength,0);
    if(count!==doc.nodes.length || triangles!==asset.triangles || geometryBytes!==asset.geometryBytes)throw Error('Skin component decoded cost');
    return gltf.scene;
  }catch(error){disposeSkinComponents(gltf.scene);throw error;}
}
