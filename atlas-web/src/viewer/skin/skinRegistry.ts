import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { SkinLayer } from './SkinLayer.ts';
import type { SkinCost } from './skinContract.ts';
// Small registry shared by the lazy layer and overlay; importing it loads no GLB/loader.
export const skinLayers = new WeakMap<DatasetSceneAdapter, SkinLayer>();
const reservations = new WeakMap<DatasetSceneAdapter, Map<object,SkinCost>>();
export function skinReservationCost(adapter:DatasetSceneAdapter):SkinCost {
  return [...reservations.get(adapter)?.values()??[]].reduce((a,b)=>({encodedBytes:a.encodedBytes+b.encodedBytes,geometryBytes:a.geometryBytes+b.geometryBytes,triangles:a.triangles+b.triangles,textureBytes:(a.textureBytes??0)+(b.textureBytes??0)}),{encodedBytes:0,geometryBytes:0,triangles:0});
}
export function reserveSkinResidency(adapter:DatasetSceneAdapter,owner:object,cost:SkinCost|null) {
  let values=reservations.get(adapter);if(!values){values=new Map();reservations.set(adapter,values);}
  if(cost)values.set(owner,cost);else values.delete(owner);
  skinLayers.get(adapter)?.reserve(skinReservationCost(adapter));
}
