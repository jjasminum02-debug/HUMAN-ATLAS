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

/**
 * Volume preservation (M2 follow-up): a shortened muscle belly thickens, a stretched one thins. Per rest mesh: the
 * main axis (PCA), each vertex's position t along it (0..1), and the vertices of both ends (outer 15 %). After
 * skinning, the posed end centres give the current length; vertices move away from the end-to-end axis by
 * 1 + (k - 1)·sin(πt) with k = √(rest length / current length), so the ends stay on their attachments.
 * Teaching approximation, not muscle mechanics.
 */
export interface VolumeProfile { t: Float32Array; ends: [Uint32Array, Uint32Array]; restLength: number }
export const VOLUME_LIMITS: [number, number] = [.85, 1.25];

export function volumeProfile(p: Float32Array): VolumeProfile | null {
  const count = p.length / 3;
  if (count < 24) return null;
  let cx = 0, cy = 0, cz = 0;
  for (let i = 0; i < p.length; i += 3) { cx += p[i]; cy += p[i + 1]; cz += p[i + 2]; }
  cx /= count; cy /= count; cz /= count;
  const c = [0, 0, 0, 0, 0, 0]; // xx xy xz yy yz zz
  for (let i = 0; i < p.length; i += 3) {
    const x = p[i] - cx, y = p[i + 1] - cy, z = p[i + 2] - cz;
    c[0] += x * x; c[1] += x * y; c[2] += x * z; c[3] += y * y; c[4] += y * z; c[5] += z * z;
  }
  let a = [1, .5, .25];
  for (let k = 0; k < 40; k++) { // power iteration: main axis
    const b = [c[0] * a[0] + c[1] * a[1] + c[2] * a[2], c[1] * a[0] + c[3] * a[1] + c[4] * a[2], c[2] * a[0] + c[4] * a[1] + c[5] * a[2]];
    const l = Math.hypot(b[0], b[1], b[2]) || 1; a = b.map(v => v / l);
  }
  const s = new Float32Array(count);
  let lo = Infinity, hi = -Infinity;
  for (let v = 0, i = 0; v < count; v++, i += 3) { s[v] = (p[i] - cx) * a[0] + (p[i + 1] - cy) * a[1] + (p[i + 2] - cz) * a[2]; lo = Math.min(lo, s[v]); hi = Math.max(hi, s[v]); }
  if (!(hi - lo > 1e-4)) return null;
  const t = new Float32Array(count), start: number[] = [], end: number[] = [];
  for (let v = 0; v < count; v++) { t[v] = (s[v] - lo) / (hi - lo); if (t[v] < .15) start.push(v); else if (t[v] > .85) end.push(v); }
  const profile: VolumeProfile = { t, ends: [Uint32Array.from(start), Uint32Array.from(end)], restLength: 0 };
  profile.restLength = endsLength(profile, p).length;
  return profile.restLength > 1e-4 ? profile : null;
}

function centre(ids: Uint32Array, p: ArrayLike<number>) {
  let x = 0, y = 0, z = 0;
  for (const v of ids) { x += p[3 * v]; y += p[3 * v + 1]; z += p[3 * v + 2]; }
  return [x / ids.length, y / ids.length, z / ids.length];
}
function endsLength(profile: VolumeProfile, p: ArrayLike<number>) {
  const a = centre(profile.ends[0], p), b = centre(profile.ends[1], p);
  return { a, b, length: Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) };
}

/** Thicken/thin the posed muscle in `target` (positions already skinned). Returns the belly scale k applied (1 = none). */
export function preserveVolume(profile: VolumeProfile, target: THREE.BufferGeometry, limits = VOLUME_LIMITS) {
  const attribute = target.getAttribute('position'), p = attribute.array as Float32Array;
  const { a, b, length } = endsLength(profile, p);
  const k = Math.min(limits[1], Math.max(limits[0], Math.sqrt(profile.restLength / Math.max(length, 1e-6))));
  if (Math.abs(k - 1) < .005) return 1;
  const d = [(b[0] - a[0]) / length, (b[1] - a[1]) / length, (b[2] - a[2]) / length];
  for (let v = 0, i = 0; v < profile.t.length; v++, i += 3) {
    const along = (p[i] - a[0]) * d[0] + (p[i + 1] - a[1]) * d[1] + (p[i + 2] - a[2]) * d[2];
    const qx = a[0] + d[0] * along, qy = a[1] + d[1] * along, qz = a[2] + d[2] * along;
    const f = 1 + (k - 1) * Math.sin(Math.PI * profile.t[v]);
    p[i] = qx + (p[i] - qx) * f; p[i + 1] = qy + (p[i + 1] - qy) * f; p[i + 2] = qz + (p[i + 2] - qz) * f;
  }
  attribute.needsUpdate = true;
  target.computeBoundingSphere(); target.computeBoundingBox();
  return k;
}
