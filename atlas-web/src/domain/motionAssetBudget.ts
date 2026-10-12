/** The measured native trunk budget follows this exact immutable base only. */
export const DEFAULT_MOTION_ASSET_BYTES = 8 * 1024 * 1024;
export const NATIVE_TRUNK_BASE = {
  uri: 'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb',
  sha256: 'fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf',
  bytes: 31_306_820,
} as const;

export function motionAssetByteBudget(entry: { uri: string; sha256: string }): number {
  return entry.uri === NATIVE_TRUNK_BASE.uri && entry.sha256 === NATIVE_TRUNK_BASE.sha256
    ? NATIVE_TRUNK_BASE.bytes : DEFAULT_MOTION_ASSET_BYTES;
}

/** A direct replacement inherits its original's ceiling; it cannot expand it. */
export function motionRepairByteBudget(row: { baseUri: string; baseSha256: string }): number {
  return motionAssetByteBudget({ uri: row.baseUri, sha256: row.baseSha256 });
}

export function motionRepairBytesEligible(row: { baseUri: string; baseSha256: string; bytes: number }): boolean {
  return Number.isSafeInteger(row.bytes) && row.bytes > 0 && row.bytes <= motionRepairByteBudget(row);
}
