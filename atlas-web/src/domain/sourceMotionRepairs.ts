import type { MotionAsset } from './motionLearning.ts';
import { motionRepairBytesEligible } from './motionAssetBudget.ts';

export interface SourceMotionRepair {
  assetId: string;
  baseUri: string;
  baseSha256: string;
  bindingSignature: string;
  uri: string;
  sha256: string;
  revision: string;
  bytes: number;
}

/** Pin the complete frame, pose, side, topology and camera/playback contract. */
export function motionRepairBindingSignature(asset: MotionAsset): string {
  return JSON.stringify([asset.staticBinding, asset.clip, asset.poseControl, asset.sourceBinding]);
}

/** A repair replaces only a verified emitted stream. It grants no anatomy/review rights. */
export function applySourceMotionRepair<T extends { definition: unknown; asset: MotionAsset }>(
  candidate: T | null, rows: readonly SourceMotionRepair[],
): T | null {
  if (!candidate) return null;
  const row = rows.find(row => row.assetId === candidate.asset.id);
  if (!row) return candidate;
  const asset = candidate.asset;
  if (asset.uri !== row.baseUri || asset.sha256 !== row.baseSha256
      || motionRepairBindingSignature(asset) !== row.bindingSignature
      || !/^[a-f0-9]{64}$/.test(row.sha256)
      || !row.uri.startsWith('atlas-data/assets/motion/') || row.uri.includes('..')
      || !motionRepairBytesEligible(row)) return null;
  return { ...candidate, asset: { ...asset, uri: row.uri, sha256: row.sha256, revision: row.revision } };
}
