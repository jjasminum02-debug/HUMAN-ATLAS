// Whole-body skeleton rig (ROADMAP M1). Data: atlas-data/runtime/rig.json (atlas-data/pipeline/build_rig.py).
// posed(segment) = posed(parent) · T(centre) · R(dof₁) · R(dof₂) … · T(−centre), every centre/axis in the rest frame.
import * as THREE from 'three';

export interface RigDof { id: string; axis: [number, number, number]; range: [number, number]; positive: string; negative: string; rangeSource: string;
  /** Driven by another dof (patella follows knee flexion); never set directly. */
  coupledTo?: string; ratio?: number }
export interface RigJoint { name: string; centre: [number, number, number]; estimate: string; dofs: RigDof[];
  /** A control without a segment of its own (neck, fingers 2–5, toes 2–5): its dofs drive coupled joints. */
  control?: boolean }
export interface RigSegment { parent: string | null; joint: string | null; side: string; bones: string[] }
export interface RigFile { schemaVersion: 1; revision: string; segments: Record<string, RigSegment>; joints: Record<string, RigJoint> }
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

/** Segment id -> world transform for the pose (identity at rest). Parents are always resolved first. */
export function segmentTransforms(rig: RigFile, pose: RigPose): Map<string, THREE.Matrix4> {
  const done = new Map<string, THREE.Matrix4>();
  const rotation = new THREE.Matrix4(), axis = new THREE.Vector3();
  const resolve = (id: string): THREE.Matrix4 => {
    const cached = done.get(id); if (cached) return cached;
    const segment = rig.segments[id];
    const matrix = segment.parent ? resolve(segment.parent).clone() : new THREE.Matrix4();
    const joint = segment.joint ? rig.joints[segment.joint] : undefined;
    if (joint) {
      const [x, y, z] = joint.centre;
      matrix.multiply(new THREE.Matrix4().makeTranslation(x, y, z));
      for (const dof of joint.dofs) {
        const degrees = dof.coupledTo ? (pose[dof.coupledTo] ?? 0) * (dof.ratio ?? 1) : pose[dof.id] ?? 0;
        if (degrees) matrix.multiply(rotation.makeRotationAxis(axis.set(...dof.axis).normalize(), THREE.MathUtils.degToRad(degrees)));
      }
      matrix.multiply(new THREE.Matrix4().makeTranslation(-x, -y, -z));
    }
    done.set(id, matrix);
    return matrix;
  };
  for (const id of Object.keys(rig.segments)) resolve(id);
  return done;
}

/** Bone key -> segment id. */
export function boneSegments(rig: RigFile): Map<string, string> {
  const out = new Map<string, string>();
  for (const [id, segment] of Object.entries(rig.segments)) for (const bone of segment.bones) out.set(bone, id);
  return out;
}
