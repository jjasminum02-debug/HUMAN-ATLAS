// Soft-tissue skinning (ROADMAP M2): linear blend of two rig segments per vertex, on the CPU, only when the pose
// changes. Weights: atlas-data/pipeline/build_skin.py -> /__atlas/v2/skin/<chunk>.bin (layout documented there).
import * as THREE from 'three';

export interface SkinWeights { roles: string[]; data: Uint16Array }
export type SkinChunk = Map<string, SkinWeights>;

export function parseSkinChunk(buffer: ArrayBuffer): SkinChunk {
  const headerBytes = new DataView(buffer).getUint32(0, true);
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 4, headerBytes))) as
    { resources: Record<string, { offset: number; vertices: number; roles: string[] }> };
  const base = 4 + headerBytes, out: SkinChunk = new Map();
  for (const [key, r] of Object.entries(header.resources))
    out.set(key, { roles: r.roles, data: new Uint16Array(buffer.slice(base + r.offset, base + r.offset + r.vertices * 2)) });
  return out;
}

/** Rig segment id for a role on a given body side ("femur" + right -> "femur_r"). */
export function segmentForRole(role: string, side: string | null) {
  return role === 'pelvis' || role === 'torso' ? role : `${role}_${side === 'left' ? 'l' : 'r'}`;
}

/**
 * Write the posed positions/normals of `rest` into `target` (same vertex count). `slotMatrices[i]` maps rest
 * object space to posed object space for role slot i (instance⁻¹ · segment pose · instance).
 */
export function skinGeometry(rest: THREE.BufferGeometry, weights: Uint16Array, slotMatrices: THREE.Matrix4[], target: THREE.BufferGeometry) {
  const p = rest.getAttribute('position').array as Float32Array, n = rest.getAttribute('normal')?.array as Float32Array | undefined;
  const tp = target.getAttribute('position').array as Float32Array, tn = target.getAttribute('normal')?.array as Float32Array | undefined;
  const m = slotMatrices.map(matrix => matrix.elements);
  for (let v = 0, i = 0; v < weights.length; v++, i += 3) {
    const packed = weights[v], a = m[packed >> 12], b = m[(packed >> 8) & 15], wa = (packed & 255) / 255, wb = 1 - wa;
    const x = p[i], y = p[i + 1], z = p[i + 2];
    tp[i] = wa * (a[0] * x + a[4] * y + a[8] * z + a[12]) + wb * (b[0] * x + b[4] * y + b[8] * z + b[12]);
    tp[i + 1] = wa * (a[1] * x + a[5] * y + a[9] * z + a[13]) + wb * (b[1] * x + b[5] * y + b[9] * z + b[13]);
    tp[i + 2] = wa * (a[2] * x + a[6] * y + a[10] * z + a[14]) + wb * (b[2] * x + b[6] * y + b[10] * z + b[14]);
    if (n && tn) {
      const nx = n[i], ny = n[i + 1], nz = n[i + 2];
      const ox = wa * (a[0] * nx + a[4] * ny + a[8] * nz) + wb * (b[0] * nx + b[4] * ny + b[8] * nz);
      const oy = wa * (a[1] * nx + a[5] * ny + a[9] * nz) + wb * (b[1] * nx + b[5] * ny + b[9] * nz);
      const oz = wa * (a[2] * nx + a[6] * ny + a[10] * nz) + wb * (b[2] * nx + b[6] * ny + b[10] * nz);
      const length = Math.hypot(ox, oy, oz) || 1;
      tn[i] = ox / length; tn[i + 1] = oy / length; tn[i + 2] = oz / length;
    }
  }
  target.getAttribute('position').needsUpdate = true;
  if (tn) target.getAttribute('normal').needsUpdate = true;
  target.computeBoundingSphere(); target.computeBoundingBox();
}

/** A writable copy of `rest` (own index too: disposing a geometry frees every GPU buffer it references). */
export function posedCopy(rest: THREE.BufferGeometry) {
  const target = new THREE.BufferGeometry();
  const index = rest.getIndex();
  if (index) target.setIndex(new THREE.BufferAttribute(index.array.slice(), 1));
  target.setAttribute('position', new THREE.BufferAttribute(new Float32Array(rest.getAttribute('position').array), 3));
  const normal = rest.getAttribute('normal');
  if (normal) target.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(normal.array), 3));
  target.userData.skinRest = rest;
  return target;
}
