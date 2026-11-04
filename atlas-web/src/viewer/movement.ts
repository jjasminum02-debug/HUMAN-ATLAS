// Movement UI data (ROADMAP M3): joint groups for the sliders, which muscles drive a movement, and the
// action playback curve. Data: /__atlas/v2/actions.json (atlas-data/pipeline/build_actions.py), /__atlas/v2/rig.json.
import type { RigDof, RigFile, RigPose } from './rig.ts';

export interface MuscleAction { dof: string; sign: 1 | -1; role: 'primary' | 'assist' }
export interface MuscleActionsFile { schemaVersion: 1; muscles: Record<string, { actions: MuscleAction[]; outside?: string[] }> }
export type ActionHighlight = { agonists: string[]; antagonists: string[] } | null;

/** What the movement panel and the muscle card need from the scene (implemented by DatasetSceneAdapter). */
export interface RigHost {
  loadRig(): Promise<RigFile>;
  loadMuscleActions(): Promise<MuscleActionsFile>;
  setRigPose(rig: RigFile, pose: RigPose | null): void;
  readonly rigPose: RigPose | null;
  onRigPoseChange(listener: (pose: RigPose | null) => void): () => void;
  setActionHighlight(highlight: ActionHighlight): void;
  /** Ask the movement panel to open on a rig joint (e.g. from a joint card). */
  openMovement(jointId: string): void;
  onOpenMovement(listener: (jointId: string) => void): () => void;
}
export const isRigHost = (host: unknown): host is RigHost => Boolean(host && typeof (host as RigHost).loadRig === 'function');

/** The seven joint groups of the roadmap's completion criterion, in body order. Joint ids are side-free. */
export const MOVEMENT_GROUPS: { id: string; label: string; joints: string[] }[] = [
  { id: 'back', label: '허리', joints: ['back'] },
  { id: 'shoulder', label: '어깨', joints: ['shoulder'] },
  { id: 'elbow', label: '팔꿉·아래팔', joints: ['elbow', 'radioulnar'] },
  { id: 'wrist', label: '손목', joints: ['wrist'] },
  { id: 'hip', label: '엉덩', joints: ['hip'] },
  { id: 'knee', label: '무릎', joints: ['knee'] },
  { id: 'ankle', label: '발목·발', joints: ['ankle', 'subtalar', 'mtp'] },
];

export const rigJointId = (joint: string, side: 'l' | 'r') => joint === 'back' ? 'back' : `${joint}_${side}`;

/** Settable dofs of a group on one side, with their joint. */
export function groupDofs(rig: RigFile, groupId: string, side: 'l' | 'r') {
  const group = MOVEMENT_GROUPS.find(g => g.id === groupId);
  return (group?.joints ?? []).flatMap(joint => {
    const id = rigJointId(joint, side), rigJoint = rig.joints[id];
    return rigJoint ? rigJoint.dofs.filter(dof => !dof.coupledTo).map(dof => ({ joint: id, jointName: rigJoint.name, dof })) : [];
  });
}

/** Group and side of a rig joint id ("knee_r" -> knee, r). */
export function groupOfJoint(jointId: string) {
  const [joint, side] = jointId === 'back' ? ['back', 'r'] : [jointId.replace(/_[lr]$/, ''), jointId.endsWith('_l') ? 'l' : 'r'];
  const group = MOVEMENT_GROUPS.find(g => g.joints.includes(joint));
  return group ? { group: group.id, side: side as 'l' | 'r' } : null;
}

/** Muscles that produce the movement (agonists) and those that produce the opposite one (antagonists). */
export function movementRoles(actions: MuscleActionsFile, dofId: string, direction: 1 | -1, visible?: (key: string) => boolean) {
  const agonists: { key: string; role: MuscleAction['role'] }[] = [], antagonists: { key: string; role: MuscleAction['role'] }[] = [];
  for (const [key, row] of Object.entries(actions.muscles)) {
    if (visible && !visible(key)) continue;
    for (const action of row.actions) if (action.dof === dofId) (action.sign === direction ? agonists : antagonists).push({ key, role: action.role });
  }
  const order = (a: { role: string }, b: { role: string }) => (a.role === 'primary' ? 0 : 1) - (b.role === 'primary' ? 0 : 1);
  return { agonists: agonists.sort(order), antagonists: antagonists.sort(order) };
}

/** Learner label of a movement: "무릎관절 (오른쪽) 굽힘". */
export function movementLabel(rig: RigFile, dofId: string, sign: 1 | -1) {
  const joint = rig.joints[dofId.split(':')[0]], dof = joint?.dofs.find(d => d.id === dofId);
  return dof ? `${joint.name} ${sign > 0 ? dof.positive : dof.negative}` : dofId;
}

export type Keyframe = { to: number; active: boolean };
/**
 * Playback of a movement, from rest: go 70 % of the way to the range end in that direction, hold, return. When rest is
 * already the end of that direction (knee or elbow extension, supination) first bend the other way, then show the
 * movement back to rest. `active` marks the frames that are the movement itself (coloured).
 */
export function actionKeyframes(dof: RigDof, sign: 1 | -1): Keyframe[] {
  const end = sign > 0 ? dof.range[1] : dof.range[0], other = sign > 0 ? dof.range[0] : dof.range[1];
  if (Math.abs(end) >= 10) { const target = Math.round(end * .7); return [{ to: target, active: true }, { to: target, active: true }, { to: 0, active: false }]; }
  const prep = Math.round(other * .7);
  return [{ to: prep, active: false }, { to: prep, active: false }, { to: end, active: true }, { to: end, active: true }];
}

/** Angle and phase at `t` in [0, 1]; frames are evenly spaced and eased in and out, starting from 0. */
export function sampleKeyframes(frames: Keyframe[], t: number) {
  const ease = (x: number) => x * x * (3 - 2 * x);
  const position = Math.min(frames.length - 1e-9, Math.max(0, t) * frames.length), i = Math.floor(position);
  const from = i === 0 ? 0 : frames[i - 1].to;
  return { value: from + (frames[i].to - from) * ease(position - i), active: frames[i].active };
}

/** The rig joint between two segments that the given bones belong to (parent-child), preferring settable ones. */
export function rigJointForBones(rig: RigFile, boneKeys: string[]) {
  const segmentOf = new Map<string, string>();
  for (const [id, segment] of Object.entries(rig.segments)) for (const bone of segment.bones) segmentOf.set(bone, id);
  const segments = new Set(boneKeys.map(key => segmentOf.get(key)).filter((s): s is string => Boolean(s)));
  const joints = [...segments].map(id => rig.segments[id]).filter(s => s.parent && segments.has(s.parent) && s.joint).map(s => s.joint!);
  return joints.find(id => rig.joints[id]?.dofs.some(dof => !dof.coupledTo)) ?? null;
}
