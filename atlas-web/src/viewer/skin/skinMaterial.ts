import * as THREE from 'three';

export interface SkinTextureSpec {
  url: string; sha256: string; bytes: number; width: number; height: number;
  gpuBytes: number; colorSpace: string; flipY: boolean;
}
export interface SkinMaterialPackage {
  schemaVersion: number; id: string; geometrySha256: string; uvSha256: string;
  encodedBytes: number; textureBytes: number; normalScale: number;
  maps: Record<'color'|'normal'|'roughness', SkinTextureSpec>;
}
const hash = async (bytes: ArrayBuffer) => [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
export function textureMipBytes(width:number,height:number) {
  let bytes=0;
  do {bytes+=width*height*4;if(width===1&&height===1)break;width=Math.max(1,Math.floor(width/2));height=Math.max(1,Math.floor(height/2));} while(true);
  return bytes;
}
export function validateSkinMaterial(p:SkinMaterialPackage,geometryHash:string) {
  if(p.schemaVersion!==1 || !p.id || p.geometrySha256!==geometryHash || !/^[a-f0-9]{64}$/.test(p.uvSha256)
    || !Number.isFinite(p.normalScale) || p.normalScale<0 || p.normalScale>.5)throw Error('Skin material binding');
  for(const [kind,m] of Object.entries(p.maps)) {
    if(!m.url || !/^[a-f0-9]{64}$/.test(m.sha256) || !Number.isSafeInteger(m.bytes) || m.bytes<=0
      || ![m.width,m.height].every(n=>Number.isSafeInteger(n)&&n>0&&n<=2048)
      || m.gpuBytes!==textureMipBytes(m.width,m.height) || m.flipY!==true
      || m.colorSpace!==(kind==='color'?'srgb':'linear'))throw Error('Skin texture contract');
  }
  if(!p.maps.color||!p.maps.normal||!p.maps.roughness || Object.keys(p.maps).length!==3
    || p.encodedBytes!==Object.values(p.maps).reduce((n,m)=>n+m.bytes,0)
    || p.textureBytes!==Object.values(p.maps).reduce((n,m)=>n+m.gpuBytes,0))throw Error('Skin texture cost');
}
/** Only textures created here are owned here. No global/shared texture disposal. */
export function disposeSkinMaterial(material:THREE.Material) {
  const textures=material.userData.skinTextures as THREE.Texture[]|undefined;
  for(const texture of textures??[]){texture.dispose();(texture.image as ImageBitmap)?.close?.();}
  material.userData.skinTextures=[];material.dispose();
}
export async function loadSkinMaterial(p:SkinMaterialPackage,geometryHash:string,uv:THREE.BufferAttribute,signal:AbortSignal) {
  validateSkinMaterial(p,geometryHash);
  const uvBytes=new Uint8Array(uv.array.buffer,uv.array.byteOffset,uv.array.byteLength).slice().buffer;
  if(uv.itemSize!==2 || await hash(uvBytes)!==p.uvSha256)throw Error('Skin material UV layout');
  const material=new THREE.MeshStandardMaterial({color:0xffffff,roughness:1,metalness:0,side:THREE.FrontSide});
  const owned:THREE.Texture[]=[];material.userData.skinTextures=owned;
  try {
    for(const kind of ['color','normal','roughness'] as const) {
      signal.throwIfAborted();const spec=p.maps[kind];
      const response=await fetch(spec.url,{signal});if(!response.ok)throw Error('Skin texture HTTP');
      const bytes=await response.arrayBuffer();signal.throwIfAborted();
      if(bytes.byteLength!==spec.bytes || await hash(bytes)!==spec.sha256)throw Error('Skin texture hash/bytes');
      // Source is OBJ V-up. ImageBitmap ignores Texture.flipY, so flip at decode.
      const bitmap=await createImageBitmap(new Blob([bytes],{type:'image/webp'}),{imageOrientation:'flipY',premultiplyAlpha:'none',colorSpaceConversion:'none'});
      if(signal.aborted || bitmap.width!==spec.width || bitmap.height!==spec.height){bitmap.close();signal.throwIfAborted();throw Error('Skin texture dimensions');}
      const texture=new THREE.Texture(bitmap);owned.push(texture);texture.flipY=false;
      texture.colorSpace=kind==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;
      texture.minFilter=THREE.LinearMipmapLinearFilter;texture.magFilter=THREE.LinearFilter;
      texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;texture.needsUpdate=true;
      if(kind==='color')material.map=texture;
      else if(kind==='normal')material.normalMap=texture;
      else material.roughnessMap=texture;
    }
    signal.throwIfAborted();material.normalScale.setScalar(p.normalScale);return material;
  } catch(error){disposeSkinMaterial(material);throw error;}
}
