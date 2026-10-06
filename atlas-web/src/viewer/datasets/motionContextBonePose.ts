import { Matrix4 } from 'three';
import type { MotionAsset } from '../../domain/motionLearning.ts';
import type { RuntimeStructureRecord } from './integration.ts';

const teachingFamily = (asset: MotionAsset) => /^T66-FAMILY-(?:elbow-flexion|shoulder-flexion)-(?:left|right)-/.test(asset.id);
const distalBone = (row: RuntimeStructureRecord) => /^(?:Radius|Ulna|Scaphoid bone|Lunate bone|Triquetrum bone|Pisiform bone|Trapezium bone|Trapezoid bone|Capitate bone|Hamate bone|(?:First|Second|Third|Fourth|Fifth) metacarpal bone|(?:Proximal|Middle|Distal) phalanx of .* of hand)$/.test(row.names.en);

/** Complete the existing native distal chain; do not rigidly carry muscles crossing the fixed humerus. */
export function limbMotionContextKeys(asset: MotionAsset, rows: readonly RuntimeStructureRecord[], attachments: (key: string) => readonly string[]) {
  if (!teachingFamily(asset) || !asset.sourceBinding) return [];
  const eligible = rows.filter(row => row.side === asset.staticBinding.side && row.localDisplayEligible && row.defaultVisible
    && !row.hardHoldReasons.length && !row.sourceHiddenStatePreserved.hideViewport);
  const boneKeys = new Set(eligible.filter(row => row.kind === 'bone' && distalBone(row)).map(row => row.sourceKey));
  const anchors = asset.sourceBinding.members.filter(member => member.role === 'moving_structure'
    && eligible.some(row => row.sourceKey === member.sourceKey && row.names.en === 'Ulna'));
  if (anchors.length !== 1) return [];
  const members = new Set(asset.sourceBinding.members.map(member => member.sourceKey));
  return eligible.filter(row => !members.has(row.sourceKey) && (boneKeys.has(row.sourceKey)
    || row.kind === 'muscle' && attachments(row.sourceKey).length > 0 && attachments(row.sourceKey).every(key => boneKeys.has(key))))
    .map(row => row.sourceKey);
}

/** Authored educational co-motion, not a measured joint axis or a new asset binding. */
export function contextBoneFollowers(asset: MotionAsset, contextKeys: readonly string[], rowFor: (key: string) => RuntimeStructureRecord | undefined) {
  const binding = asset.sourceBinding;
  if (!binding || !teachingFamily(asset)) return [];
  const anchors = binding.members.filter(member => member.role === 'moving_structure' && rowFor(member.sourceKey)?.names.en === 'Ulna'
    && rowFor(member.sourceKey)?.side === asset.staticBinding.side);
  if (anchors.length !== 1) return [];
  return contextKeys.filter(key => !binding.members.some(member => member.sourceKey === key)
    && rowFor(key)?.side === asset.staticBinding.side)
    .map(sourceKey => ({ sourceKey, anchorSourceKey: anchors[0].sourceKey }));
}

/** Preserve the native radius/ulna relationship under the existing rigid teaching trajectory. */
export function followContextBone(rest: Matrix4, anchorRestInverse: Matrix4, anchorPose: Matrix4, target: Matrix4) {
  return target.copy(anchorPose).multiply(anchorRestInverse).multiply(rest);
}
