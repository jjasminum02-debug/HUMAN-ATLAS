// Whole-body skeleton rig (ROADMAP M1). Data: atlas-data/runtime/rig.json (atlas-data/pipeline/build_rig.py).
// posed(segment) = posed(parent) · T(centre) · R(dof₁) · R(dof₂) … · T(−centre), every centre/axis in the rest frame.
// Two shoulder refinements: the scapula keeps its medial border on the chest wall (it takes only the acromioclavicular
// point from the clavicle and turns about it), and the shoulder sliders give the arm's angle to the trunk, shared 2 : 1
// between the shoulder joint and the scapula beyond 30° (scapulohumeral rhythm).
import * as THREE from 'three';

export interface RigDof { id: string; axis: [number, number, number]; range: [number, number]; positive: string; negative: string; rangeSource: string;
  /** Driven by another dof (patella follows knee flexion); never set directly. */
  coupledTo?: string; ratio?: number }
export interface RigJoint { name: string; centre: [number, number, number]; estimate: string; dofs: RigDof[];
  /** A control without a segment of its own (neck, fingers 2–5, toes 2–5): its dofs drive coupled joints. */
  control?: boolean;
  /** Medial border points that stay on the chest wall (acromioclavicular joints). */
  scapulothoracic?: { contacts: [number, number, number][] };
  /** Arm elevation beyond `start` degrees is shared with the scapula's upward rotation (shoulder joints). */
  rhythm?: { dofs: string[]; scapula: string; start: number; share: number } }
/** Outer rib cage surface: radius by height row and angle column about the vertical line x = 0, z = z0. */
export interface RigThorax { z0: number; y0: number; step: number; angles: number; radius: number[][] }
export interface RigSegment { parent: string | null; joint: string | null; side: string; bones: string[] }
/** Teaching landmarks: the hand/foot channel boundary height (『영추·종시』 腰 / the class's diaphragm), on its segment. */
export interface RigLandmarks { handFootBoundary?: { y: number; segment: string } }
export interface RigFile { schemaVersion: 1; revision: string; segments: Record<string, RigSegment>; joints: Record<string, RigJoint>; thorax?: RigThorax; landmarks?: RigLandmarks }
/** Degrees per dof id (e.g. "knee_r:flexion"); missing dofs are 0. */
export type RigPose = Record<string, number>;

export function clampPose(rig: RigFile, pose: RigPose): RigPose {
  const out: RigPose = {};
  for (const joint of Object.values(rig.joints)) for (const dof of joint.dofs) {
    if (dof.coupledTo) continue;
    const value = pose[dof.id];
    if (value !== undefined && Number.isFinite(value)) out[dof.id] = Math.min(dof.range[1], Math.max(dof.range[0], value));
  }
  return out;
}

const dofOf = (rig: RigFile, id: string) => rig.joints[id.split(':')[0]]?.dofs.find(d => d.id === id);

/**
 * Joint angles actually applied: the shoulder sliders are the arm's elevation to the trunk; beyond `start` the scapula
 * takes `share` of it as upward rotation (added to its own slider, within its range) and the shoulder joint the rest.
 */
export function rhythmPose(rig: RigFile, pose: RigPose): RigPose {
  const out = { ...pose };
  for (const joint of Object.values(rig.joints)) {
    const rhythm = joint.rhythm, scapula = rhythm && dofOf(rig, rhythm.scapula);
    if (!rhythm || !scapula) continue;
    const raised = rhythm.dofs.map(id => Math.max(0, pose[id] ?? 0)), elevation = Math.hypot(...raised);
    if (elevation <= rhythm.start) continue;
    const own = pose[rhythm.scapula] ?? 0;
    const turned = Math.min(scapula.range[1], own + (elevation - rhythm.start) * rhythm.share) - own;
    if (turned <= 0) continue;
    const keep = (elevation - turned) / elevation;
    rhythm.dofs.forEach((id, i) => { if (raised[i] > 0) out[id] = raised[i] * keep; });
    out[rhythm.scapula] = own + turned;
  }
  return out;
}

/** Signed distance (m) of a rest-frame point outside the rib cage surface, along the radius about the thorax axis. */
export function thoraxGap(thorax: RigThorax, point: THREE.Vector3) {
  const dz = point.z - thorax.z0, n = thorax.angles, rows = thorax.radius.length;
  const fj = (Math.atan2(point.x, -dz) + Math.PI) / (2 * Math.PI) * n - .5, j0 = Math.floor(fj), wj = fj - j0;
  const fi = Math.min(rows - 1.0001, Math.max(0, (point.y - thorax.y0) / thorax.step)), i0 = Math.floor(fi), wi = fi - i0;
  const at = (i: number, j: number) => thorax.radius[i][((j % n) + n) % n];
  const r = (at(i0, j0) * (1 - wj) + at(i0, j0 + 1) * wj) * (1 - wi) + (at(i0 + 1, j0) * (1 - wj) + at(i0 + 1, j0 + 1) * wj) * wi;
  return Math.hypot(point.x, dz) - r;
}

const restGaps = new WeakMap<RigJoint, number[]>();
/**
 * Rotation about the acromioclavicular point that brings the medial border contacts back to their rest distance from the
 * chest wall (least squares, 2 dof: about axes across the upward rotation axis, so it never undoes upward rotation).
 * `place(w)` gives the contacts in the thorax frame for a correction rotation vector `w` (radians).
 */
function scapulaCorrection(thorax: RigThorax, joint: RigJoint, place: (w: THREE.Vector3) => THREE.Vector3[]) {
  let rest = restGaps.get(joint);
  if (!rest) { rest = joint.scapulothoracic!.contacts.map(p => thoraxGap(thorax, new THREE.Vector3(...p))); restGaps.set(joint, rest); }
  const restGap = rest;
  const n = new THREE.Vector3(...joint.dofs[0].axis).normalize();
  const b1 = new THREE.Vector3().crossVectors(n, new THREE.Vector3(0, 1, 0)).normalize(), b2 = new THREE.Vector3().crossVectors(n, b1);
  const residual = (w: THREE.Vector3) => place(w).map((p, i) => thoraxGap(thorax, p) - restGap[i]);
  const w = new THREE.Vector3(), h = 1e-3, step = new THREE.Vector3();
  for (let iteration = 0; iteration < 8; iteration++) {
    const r = residual(w);
    if (Math.max(...r.map(Math.abs)) < 5e-4) break;
    const columns = [b1, b2].map(b => residual(w.clone().addScaledVector(b, h)).map((v, i) => (v - r[i]) / h));
    // Normal equations of the 2 × 2 least squares with a little damping.
    const a = columns[0].reduce((s, v) => s + v * v, 0) + 1e-4, c = columns[1].reduce((s, v) => s + v * v, 0) + 1e-4;
    const b = columns[0].reduce((s, v, i) => s + v * columns[1][i], 0);
    const g0 = -columns[0].reduce((s, v, i) => s + v * r[i], 0), g1 = -columns[1].reduce((s, v, i) => s + v * r[i], 0);
    const det = a * c - b * b; if (Math.abs(det) < 1e-12) break;
    step.copy(b1).multiplyScalar((c * g0 - b * g1) / det).addScaledVector(b2, (a * g1 - b * g0) / det);
    if (step.length() > .17) step.setLength(.17);   // at most ~10° per iteration
    w.add(step);
    if (w.length() > .8) { w.setLength(.8); break; }  // at most ~45° in all
  }
  return w;
}

/** Segment id -> world transform for the pose (identity at rest). Parents are always resolved first. */
export function segmentTransforms(rig: RigFile, pose: RigPose, options: { rhythm?: boolean } = {}): Map<string, THREE.Matrix4> {
  const applied = options.rhythm === false ? pose : rhythmPose(rig, pose);
  const done = new Map<string, THREE.Matrix4>();
  const rotation = new THREE.Matrix4(), axis = new THREE.Vector3();
  const turn = (joint: RigJoint) => {
    const out = new THREE.Matrix4();
    for (const dof of joint.dofs) {
      const degrees = dof.coupledTo ? (applied[dof.coupledTo] ?? 0) * (dof.ratio ?? 1) : applied[dof.id] ?? 0;
      if (degrees) out.multiply(rotation.makeRotationAxis(axis.set(...dof.axis).normalize(), THREE.MathUtils.degToRad(degrees)));
    }
    return out;
  };
  const translate = (v: THREE.Vector3, sign = 1) => new THREE.Matrix4().makeTranslation(sign * v.x, sign * v.y, sign * v.z);
  const resolve = (id: string): THREE.Matrix4 => {
    const cached = done.get(id); if (cached) return cached;
    const segment = rig.segments[id];
    const parent = segment.parent ? resolve(segment.parent) : new THREE.Matrix4();
    const joint = segment.joint ? rig.joints[segment.joint] : undefined;
    const thoraxId = segment.parent ? rig.segments[segment.parent].parent : null;
    let matrix: THREE.Matrix4;
    if (joint?.scapulothoracic && rig.thorax && thoraxId) {
      // Scapula: placed in the thorax (torso) frame at the point the clavicle carries, turned by its own dofs, then
      // about that point so the medial border stays on the chest wall.
      const torso = resolve(thoraxId);
      const centre = new THREE.Vector3(...joint.centre), carried = centre.clone().applyMatrix4(torso.clone().invert().multiply(parent));
      const local = translate(carried).multiply(turn(joint)).multiply(translate(centre, -1));
      const corrected = (w: THREE.Vector3) => w.lengthSq() < 1e-18 ? local.clone()
        : translate(carried).multiply(new THREE.Matrix4().makeRotationAxis(w.clone().normalize(), w.length())).multiply(translate(carried, -1)).multiply(local);
      const contacts = joint.scapulothoracic.contacts.map(p => new THREE.Vector3(...p));
      const w = scapulaCorrection(rig.thorax, joint, v => { const m = corrected(v); return contacts.map(p => p.clone().applyMatrix4(m)); });
      matrix = torso.clone().multiply(corrected(w));
    } else {
      matrix = parent.clone();
      if (joint) { const centre = new THREE.Vector3(...joint.centre); matrix.multiply(translate(centre)).multiply(turn(joint)).multiply(translate(centre, -1)); }
    }
    done.set(id, matrix);
    return matrix;
  };
  for (const id of Object.keys(rig.segments)) resolve(id);
  return done;
}

/**
 * Soft-tissue contact at a bent hinge (elbow, knee): tissue of the two segments meets on the inside of the bend
 * instead of passing through. The contact plane goes through the joint centre and bisects the angle between the
 * proximal and distal long axes; `normal` points to the proximal side, `inside` to the concave side of the bend.
 * `strength` ramps in between 25° and 60° of bend so small movements are untouched. World frame, posed.
 * Not the hip: a flexed thigh meets the belly well in front of the joint, so a plane through the joint centre would
 * push the abdominal wall inward.
 */
export interface ContactPlane { proximal: string; distal: Set<string>; centre: THREE.Vector3; normal: THREE.Vector3; inside: THREE.Vector3;
  restCentre: THREE.Vector3; restNormal: THREE.Vector3; radius: number; strength: number }
const CONTACTS = [{ joint: 'elbow', from: 'shoulder', to: 'wrist', radius: .12 }, { joint: 'knee', from: 'hip', to: 'ankle', radius: .16 }];
export function contactPlanes(rig: RigFile, transforms: Map<string, THREE.Matrix4>): ContactPlane[] {
  const out: ContactPlane[] = [];
  const children = new Map<string, string[]>();
  for (const [id, s] of Object.entries(rig.segments)) if (s.parent) children.set(s.parent, [...(children.get(s.parent) ?? []), id]);
  const below = (id: string): string[] => [id, ...(children.get(id) ?? []).flatMap(below)];
  const direction = (m: THREE.Matrix4, v: THREE.Vector3) => v.clone().transformDirection(m);
  for (const contact of CONTACTS) for (const side of ['l', 'r']) {
    const jointId = `${contact.joint}_${side}`, joint = rig.joints[jointId];
    const child = Object.entries(rig.segments).find(([, s]) => s.joint === jointId)?.[0], parent = child && rig.segments[child].parent;
    const from = rig.joints[contact.from] ?? rig.joints[`${contact.from}_${side}`], to = rig.joints[`${contact.to}_${side}`];
    if (!joint || !child || !parent || !from || !to) continue;
    const c = new THREE.Vector3(...joint.centre), up = new THREE.Vector3(...from.centre).sub(c).normalize(), down = new THREE.Vector3(...to.centre).sub(c).normalize();
    const P = transforms.get(parent) ?? new THREE.Matrix4(), D = transforms.get(child) ?? new THREE.Matrix4();
    const upNow = direction(P, up), downNow = direction(D, down);
    const bend = THREE.MathUtils.radToDeg(up.angleTo(down) - upNow.angleTo(downNow));
    const strength = THREE.MathUtils.clamp((bend - 25) / 35, 0, 1);
    if (!strength) continue;
    out.push({ proximal: parent, distal: new Set(below(child)), centre: c.clone().applyMatrix4(P), normal: upNow.clone().sub(downNow).normalize(),
      inside: upNow.clone().add(downNow).normalize(), restCentre: c, restNormal: up.clone().sub(down).normalize(), radius: contact.radius, strength });
  }
  return out;
}

/** Bone key -> segment id. */
export function boneSegments(rig: RigFile): Map<string, string> {
  const out = new Map<string, string>();
  for (const [id, segment] of Object.entries(rig.segments)) for (const bone of segment.bones) out.set(bone, id);
  return out;
}
