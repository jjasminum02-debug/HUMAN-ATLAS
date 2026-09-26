export type MeshVisibility = "visible" | "transparent" | "hidden";

export interface PickCandidate {
  meshAssetId: string;
}

/** Prefer the nearest solid surface; if every hit is transparent, pass through to the deepest visible candidate. */
export function pickThroughTransparent<T extends PickCandidate>(
  intersections: readonly T[],
  visibilityFor: (meshAssetId: string) => MeshVisibility,
): T | undefined {
  let transparentFallback: T | undefined;
  const seenTransparent = new Set<string>();
  for (const candidate of intersections) {
    const visibility = visibilityFor(candidate.meshAssetId);
    if (visibility === "visible") return candidate;
    if (visibility === "transparent" && !seenTransparent.has(candidate.meshAssetId)) {
      seenTransparent.add(candidate.meshAssetId);
      transparentFallback = candidate;
    }
  }
  return transparentFallback;
}

export function isFocusDimmed(
  meshAssetId: string,
  targetEntityType: string,
  focusIds: ReadonlySet<string>,
  enabled: boolean,
): boolean {
  return enabled && focusIds.size > 0 && targetEntityType !== "structure" && !focusIds.has(meshAssetId);
}

export function visibilityAfterRestore(baseVisibility: MeshVisibility, preserveBaseVisibility: boolean): MeshVisibility {
  return preserveBaseVisibility ? baseVisibility : "visible";
}
