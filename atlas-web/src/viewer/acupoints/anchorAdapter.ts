import * as THREE from 'three';
import type { Carrier, PointInstance } from './schema.ts';
import { DATASET_BUDGET } from '../datasets/schema.ts';
export interface AnchorContext { datasetRevision: string; frameId: string; unit: string; poseId: string }
export type AnchorTopology = Pick<Carrier,'id'|'revision'|'topologySha256'|'datasetRevision'|'frameId'|'unit'|'poseId'|'side'|'positions'|'indices'>;
export type TopologyAnchor = Pick<PointInstance,'carrierId'|'carrierRevision'|'carrierHash'|'frameId'|'unit'|'poseId'|'side'|'triangle'|'barycentric'>;
export function validateTopology(c: AnchorTopology, context: AnchorContext) {
  if (c.datasetRevision !== context.datasetRevision || c.frameId !== context.frameId || c.unit !== 'm' || context.unit !== 'm' || c.poseId !== context.poseId) throw Error('stale carrier frame/unit/pose/dataset');
  if (!/^[a-f0-9]{64}$/.test(c.topologySha256) || c.positions.length % 3 || c.indices.length % 3 || !c.positions.length || !c.indices.length || !c.positions.every(Number.isFinite)) throw Error('carrier topology');
  if (!c.indices.every(i => Number.isInteger(i) && i >= 0 && i < c.positions.length / 3)) throw Error('carrier index');
  for (let i = 0; i < c.positions.length; i += 3) if (c.side === 'right' && c.positions[i] >= 0 || c.side === 'left' && c.positions[i] <= 0) throw Error('carrier subject side');
}
export function validateCarrier(c: Carrier, context: AnchorContext) {
  validateTopology(c,context);
  if (c.rights.localObservation !== 'supported') throw Error('carrier local rights');
}
export async function verifyCarrierHash(c: Pick<Carrier,'positions'|'indices'|'topologySha256'>) {
  const p = new Float32Array(c.positions), i = new Uint32Array(c.indices);
  const bytes = new Uint8Array(p.byteLength + i.byteLength); bytes.set(new Uint8Array(p.buffer)); bytes.set(new Uint8Array(i.buffer), p.byteLength);
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n => n.toString(16).padStart(2, '0')).join('');
  if (hash !== c.topologySha256) throw Error('carrier topology hash mismatch');
}
/** Frozen world-frame topology, never a nearest-muscle search and never mirrored implicitly. */
export function resolveAnchor(c: AnchorTopology, i: TopologyAnchor) {
  if (i.carrierId !== c.id || i.carrierRevision !== c.revision || i.carrierHash !== c.topologySha256 || i.frameId !== c.frameId || i.unit !== c.unit || i.poseId !== c.poseId || (i.side !== c.side && c.side !== 'midline')) throw Error('stale anchor binding');
  if (!Number.isInteger(i.triangle) || i.triangle < 0 || i.triangle >= c.indices.length / 3 || i.barycentric.length !== 3 || !i.barycentric.every(n => Number.isFinite(n) && n >= 0 && n <= 1) || Math.abs(i.barycentric.reduce((a,b) => a+b,0) - 1) > 1e-6) throw Error('anchor triangle/barycentric');
  const vertices = c.indices.slice(i.triangle * 3, i.triangle * 3 + 3).map(index => new THREE.Vector3().fromArray(c.positions, index * 3));
  const normal = vertices[1].clone().sub(vertices[0]).cross(vertices[2].clone().sub(vertices[0]));
  if (normal.lengthSq() < 1e-16) throw Error('degenerate anchor triangle');
  const position = new THREE.Vector3(); vertices.forEach((v,k) => position.addScaledVector(v,i.barycentric[k]));
  if(i.side==='right'&&position.x>=0||i.side==='left'&&position.x<=0)throw Error('anchor subject side');
  return { position, normal: normal.normalize() };
}
export function withinOverlayBudget(base: { overviewBytes: number; geometryBytes: number; triangles: number }, extra: { bytes: number; triangles: number; overviewBytes?: number }) {
  return base.overviewBytes + (extra.overviewBytes ?? extra.bytes) <= DATASET_BUDGET.overviewBytes && base.geometryBytes + extra.bytes <= DATASET_BUDGET.geometryBytes && base.triangles + extra.triangles <= DATASET_BUDGET.triangles;
}
