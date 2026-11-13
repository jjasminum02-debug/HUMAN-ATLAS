import * as THREE from 'three';
import type { Carrier, PointInstance } from './schema.ts';
import { resolveAnchor } from './anchorAdapter.ts';
export const CONTACT_RADIUS=.0023;
export const CONTACT_OFFSET=.00015;
/** The visual offset/scale never rewrites the source triangle or barycentric address. */
export function placeContactGlyph(mesh:THREE.Mesh,carrier:Carrier,point:PointInstance) {
  const anchor=resolveAnchor(carrier,point);
  mesh.position.copy(anchor.position).addScaledVector(anchor.normal,CONTACT_OFFSET);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),anchor.normal);
  mesh.userData.anchor={position:anchor.position.toArray(),normal:anchor.normal.toArray(),carrierId:point.carrierId,carrierHash:point.carrierHash,triangle:point.triangle,barycentric:[...point.barycentric],side:point.side,poseId:point.poseId};
  return anchor;
}
/** A bounded piece of the actual selected triangle: a depth cue when the full layer is OFF. */
export function localContactTriangle(carrier:Carrier,point:PointInstance) {
  const a=resolveAnchor(carrier,point);
  return carrier.indices.slice(point.triangle*3,point.triangle*3+3).flatMap(v=>{
    const delta=new THREE.Vector3().fromArray(carrier.positions,v*3).sub(a.position);
    return a.position.clone().addScaledVector(delta,Math.min(1,.007/Math.max(delta.length(),1e-9))).addScaledVector(a.normal,CONTACT_OFFSET/2).toArray();
  });
}
