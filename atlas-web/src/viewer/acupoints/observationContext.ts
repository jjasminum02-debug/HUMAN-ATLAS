import * as THREE from 'three';
import type { CameraState } from '../wholeBody/cameraObservation.ts';
import type { Vec3, Side } from './schema.ts';
export interface Rect {left:number;top:number;right:number;bottom:number;width:number;height:number}
export interface ObservationStructure {sourceKey:string;name:string;bounds:[Vec3,Vec3];samplePositions:Vec3[];sourceSha256:string;role:'bone'|'muscle_tendon'|'native_probe'}
export interface ObservationContext {code:string;side:Side;point?:Vec3;mode:'point_and_structures'|'structures_only';region:string;structures:ObservationStructure[];preferredNormal:Vec3;minimumSpan:number;
  placementBinding?:{carrierId:string;carrierHash:string;triangle:number;barycentric:Vec3};limitations:string[]}
export const rect=(left:number,top:number,right:number,bottom:number):Rect=>({left,top,right,bottom,width:Math.max(0,right-left),height:Math.max(0,bottom-top)});
/** Maximum usable rectangle after actual DOM intersections; reserved CSS space is not subtracted twice. */
export function visibleRect(canvas:Rect,panels:Rect[],margin=14):Rect {
 const clipped=panels.map(p=>rect(Math.max(canvas.left,p.left),Math.max(canvas.top,p.top),Math.min(canvas.right,p.right),Math.min(canvas.bottom,p.bottom))).filter(p=>p.width>0&&p.height>0);
 const xs=[canvas.left,canvas.right,...clipped.flatMap(p=>[p.left,p.right])],ys=[canvas.top,canvas.bottom,...clipped.flatMap(p=>[p.top,p.bottom])];let best=canvas,area=0;
 for(const l of xs)for(const r of xs)for(const t of ys)for(const b of ys){if(r<=l||b<=t)continue;const q=rect(l,t,r,b);if(clipped.some(p=>Math.min(q.right,p.right)>Math.max(q.left,p.left)&&Math.min(q.bottom,p.bottom)>Math.max(q.top,p.top)))continue;
  if(q.width*q.height>area){best=q;area=q.width*q.height;}}
 return rect(best.left+margin,best.top+margin,best.right-margin,best.bottom-margin);
}
export function contextBounds(contexts:ObservationContext[],visibleKeys?:Set<string>) {
 const box=new THREE.Box3();for(const c of contexts){if(c.point)box.expandByPoint(new THREE.Vector3().fromArray(c.point));
  for(const s of c.structures)if(!visibleKeys||visibleKeys.has(s.sourceKey)){box.expandByPoint(new THREE.Vector3().fromArray(s.bounds[0]));box.expandByPoint(new THREE.Vector3().fromArray(s.bounds[1]));}}
 return box;
}
export function projectContext(box:THREE.Box3,state:CameraState,fov:number,canvas:Rect,safe:Rect,point?:Vec3) {
 const camera=new THREE.PerspectiveCamera(fov,canvas.width/canvas.height,.005,50);camera.position.fromArray(state.position);camera.lookAt(new THREE.Vector3().fromArray(state.target));camera.zoom=state.zoom;camera.updateProjectionMatrix();camera.updateMatrixWorld();
 const project=(p:THREE.Vector3)=>{const q=p.clone().project(camera);return {x:canvas.left+(q.x+1)*canvas.width/2,y:canvas.top+(1-q.y)*canvas.height/2,z:q.z};};
 const corners=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])corners.push(project(new THREE.Vector3(x,y,z)));
 const bounds=rect(Math.min(...corners.map(p=>p.x)),Math.min(...corners.map(p=>p.y)),Math.max(...corners.map(p=>p.x)),Math.max(...corners.map(p=>p.y)));
 const p=point?project(new THREE.Vector3().fromArray(point)):null;
 const inside=(q:{x:number;y:number;z:number})=>q.x>=safe.left&&q.x<=safe.right&&q.y>=safe.top&&q.y<=safe.bottom&&Math.abs(q.z)<=1;
 return {bounds,point:p,inside:corners.every(inside)&&(!p||inside(p)),occupancy:Math.max(bounds.width/safe.width,bounds.height/safe.height)};
}
/** Shared region geometry input; no point-code camera distance and no whole-bone bounds. */
export function observationCamera(box:THREE.Box3,state:CameraState,fov:number,canvas:Rect,safe:Rect,normal:Vec3,point?:Vec3,force=false,allowCurrent=true) {
 if(box.isEmpty())throw Error('No verified observation structures');
 const preferred=new THREE.Vector3().fromArray(normal).normalize(),current=new THREE.Vector3().fromArray(state.position).sub(new THREE.Vector3().fromArray(state.target)).normalize();
 const before=projectContext(box,state,fov,canvas,safe,point);
 if(!force&&current.dot(preferred)>.55&&before.inside&&before.occupancy>=.46&&before.occupancy<=.78)return {state,retained:true,before,after:before};
 const direction=allowCurrent&&current.dot(preferred)>.65?current:preferred;
 const right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),direction).normalize(),up=new THREE.Vector3().crossVectors(direction,right).normalize();
 const center=box.getCenter(new THREE.Vector3()),tan=Math.tan(THREE.MathUtils.degToRad(fov/2)),aspect=canvas.width/canvas.height,occupancy=.62;let distance=.06;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(center);distance=Math.max(distance,p.dot(direction)+Math.max(Math.abs(p.dot(right))/(tan*aspect*safe.width/canvas.width*occupancy),Math.abs(p.dot(up))/(tan*safe.height/canvas.height*occupancy)));}
 const ndcX=((safe.left+safe.right)/2-canvas.left)/canvas.width*2-1,ndcY=1-((safe.top+safe.bottom)/2-canvas.top)/canvas.height*2;
 const target=center.clone().addScaledVector(right,-ndcX*distance*tan*aspect).addScaledVector(up,-ndcY*distance*tan);
 const next={position:target.clone().addScaledVector(direction,distance).toArray(),target:target.toArray(),zoom:1};
 return {state:next,retained:false,before,after:projectContext(box,next,fov,canvas,safe,point)};
}
