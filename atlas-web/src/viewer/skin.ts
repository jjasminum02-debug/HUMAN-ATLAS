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
export function segmentForRole(role: string, side: string | null, segments?: { has(id: string): boolean }) {
  // Segments without a side (pelvis, torso, neck vertebrae, head) are their own role.
  if (segments ? segments.has(role) : role === 'pelvis' || role === 'torso') return role;
  return `${role}_${side === 'left' ? 'l' : 'r'}`;
}

/** Rigid transform as a unit dual quaternion [rx, ry, rz, rw, dx, dy, dz, dw]. Slot matrices are rigid (a segment pose
 * conjugated by the instance matrix, whose mirror and scale cancel), so rotation and translation are all there is. */
const scratch = { position: new THREE.Vector3(), rotation: new THREE.Quaternion(), scale: new THREE.Vector3() };
export function dualQuaternion(matrix: THREE.Matrix4) {
  matrix.decompose(scratch.position, scratch.rotation, scratch.scale);
  const { x: rx, y: ry, z: rz, w: rw } = scratch.rotation, { x: tx, y: ty, z: tz } = scratch.position;
  // d = ½ · (t, 0) ⊗ r
  return Float64Array.of(rx, ry, rz, rw, .5 * (tx * rw + ty * rz - tz * ry), .5 * (-tx * rz + ty * rw + tz * rx), .5 * (tx * ry - ty * rx + tz * rw), -.5 * (tx * rx + ty * ry + tz * rz));
}

/**
 * Write the posed positions/normals of `rest` into `target` (same vertex count). `slotMatrices[i]` maps rest
 * object space to posed object space for role slot i (instance⁻¹ · segment pose · instance).
 * Dual-quaternion blending (4-1 step 4): a linear blend of two rotations shrinks tissue on the inside of a bent joint
 * (the elbow crease collapses, a twisted forearm pinches); blending the rotations themselves keeps the cross-section.
 */
export function skinGeometry(rest: THREE.BufferGeometry, weights: Uint16Array, slotMatrices: THREE.Matrix4[], target: THREE.BufferGeometry) {
  const p = rest.getAttribute('position').array as Float32Array, n = rest.getAttribute('normal')?.array as Float32Array | undefined;
  const tp = target.getAttribute('position').array as Float32Array, tn = target.getAttribute('normal')?.array as Float32Array | undefined;
  const q = slotMatrices.map(dualQuaternion), m = slotMatrices.map(matrix => matrix.elements);
  for (let v = 0, i = 0; v < weights.length; v++, i += 3) {
    const packed = weights[v], sa = packed >> 12, sb = (packed >> 8) & 15, share = packed & 255;
    if (sa === sb || share === 255 || share === 0) {
      // One segment only (most vertices away from joints): the rigid matrix is exact and cheaper.
      const e = m[share === 0 ? sb : sa], x = p[i], y = p[i + 1], z = p[i + 2];
      tp[i] = e[0] * x + e[4] * y + e[8] * z + e[12]; tp[i + 1] = e[1] * x + e[5] * y + e[9] * z + e[13]; tp[i + 2] = e[2] * x + e[6] * y + e[10] * z + e[14];
      if (n && tn) {
        const nx = n[i], ny = n[i + 1], nz = n[i + 2];
        tn[i] = e[0] * nx + e[4] * ny + e[8] * nz; tn[i + 1] = e[1] * nx + e[5] * ny + e[9] * nz; tn[i + 2] = e[2] * nx + e[6] * ny + e[10] * nz;
      }
      continue;
    }
    const a = q[sa], b = q[sb], wa = share / 255;
    const wb = (1 - wa) * (a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] < 0 ? -1 : 1); // shortest arc
    let rx = wa * a[0] + wb * b[0], ry = wa * a[1] + wb * b[1], rz = wa * a[2] + wb * b[2], rw = wa * a[3] + wb * b[3];
    let dx = wa * a[4] + wb * b[4], dy = wa * a[5] + wb * b[5], dz = wa * a[6] + wb * b[6], dw = wa * a[7] + wb * b[7];
    const length = Math.hypot(rx, ry, rz, rw) || 1;
    rx /= length; ry /= length; rz /= length; rw /= length; dx /= length; dy /= length; dz /= length; dw /= length;
    // translation t = 2 · (rw·d − dw·r + r × d)
    const tx = 2 * (rw * dx - dw * rx + ry * dz - rz * dy), ty = 2 * (rw * dy - dw * ry + rz * dx - rx * dz), tz = 2 * (rw * dz - dw * rz + rx * dy - ry * dx);
    const x = p[i], y = p[i + 1], z = p[i + 2];
    // rotate: v + 2·r × (r × v + rw·v)
    let cx = ry * z - rz * y + rw * x, cy = rz * x - rx * z + rw * y, cz = rx * y - ry * x + rw * z;
    tp[i] = x + 2 * (ry * cz - rz * cy) + tx; tp[i + 1] = y + 2 * (rz * cx - rx * cz) + ty; tp[i + 2] = z + 2 * (rx * cy - ry * cx) + tz;
    if (n && tn) {
      const nx = n[i], ny = n[i + 1], nz = n[i + 2];
      cx = ry * nz - rz * ny + rw * nx; cy = rz * nx - rx * nz + rw * ny; cz = rx * ny - ry * nx + rw * nz;
      tn[i] = nx + 2 * (ry * cz - rz * cy); tn[i + 1] = ny + 2 * (rz * cx - rx * cz); tn[i + 2] = nz + 2 * (rx * cy - ry * cx);
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
