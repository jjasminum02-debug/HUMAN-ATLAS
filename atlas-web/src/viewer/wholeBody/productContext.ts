import type { BodyManifest } from "./contract.ts";

export interface ProductContextEntry {
  sourceId: string;
  nodeId: string;
  sourceSha256: string;
  sourceRegions: string[];
  side: string;
  productRegions: string[];
  comparisonOnly?: boolean;
}

export interface ProductContextOverlay {
  schemaVersion: 1;
  overlayId: string;
  sourceManifestSha256: string;
  sourceFrame: string;
  sourceUnit: string;
  sourcePublicRedistribution: "held";
  humanReview: "not_performed";
  entries: ProductContextEntry[];
}

const EXPECTED_IDS = ["FJ3237", "FJ3279", "FJ3362", "FJ3384"];
const ALLOWED_PRODUCT_REGIONS = new Set(["upper-limb"]);

function sameJson(a: unknown, b: unknown): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

/**
 * Add product-only region context to a cloned manifest. Source labels, bytes,
 * bindings, visibility, review state, and redistribution policy stay intact.
 */
export function applyProductContextOverlay(
  source: BodyManifest,
  overlay: ProductContextOverlay,
): BodyManifest {
  if (overlay.schemaVersion !== 1 || overlay.overlayId !== "T95-SHOULDER-GIRDLE-CONTEXT") {
    throw new Error("Unsupported T95 product-context overlay");
  }
  if (overlay.sourceFrame !== source.frame || overlay.sourceUnit !== source.unit
      || overlay.sourcePublicRedistribution !== "held" || source.publicRedistribution !== "held"
      || overlay.humanReview !== "not_performed" || source.localOnly !== true) {
    throw new Error("T95 source contract or hold mismatch");
  }
  const entries = new Map<string, ProductContextEntry>();
  for (const entry of overlay.entries) {
    if (entries.has(entry.sourceId)) throw new Error(`Duplicate T95 source entry: ${entry.sourceId}`);
    if (entry.productRegions.some((region) => !ALLOWED_PRODUCT_REGIONS.has(region))) {
      throw new Error(`Unsupported product region for ${entry.sourceId}`);
    }
    if (new Set(entry.productRegions).size !== entry.productRegions.length) {
      throw new Error(`Duplicate product region for ${entry.sourceId}`);
    }
    entries.set(entry.sourceId, entry);
  }
  if (!sameJson([...entries.keys()].sort(), [...EXPECTED_IDS].sort())) {
    throw new Error("T95 overlay must compare exactly the four frozen shoulder-girdle source IDs");
  }

  const assets = source.chunks.flatMap((chunk) => chunk.assets);
  const assetIds = new Set(assets.map((asset) => asset.id));
  if (assetIds.size !== assets.length) throw new Error("Duplicate source asset identity");
  for (const entry of entries.values()) {
    const matches = assets.filter((asset) => asset.id === entry.sourceId);
    if (matches.length !== 1) throw new Error(`T95 source asset missing or duplicated: ${entry.sourceId}`);
    const asset = matches[0];
    if (asset.nodeId !== entry.nodeId || asset.sourceSha256 !== entry.sourceSha256
      || asset.side !== entry.side || asset.layer !== "bone"
      || !sameJson(asset.regions, entry.sourceRegions)
      || asset.defaultVisible !== true || asset.supplement !== false
      || asset.pickState !== "source_only_unbound" || asset.stableIds.length !== 0
      || asset.holdReasons.length !== 0 || asset.humanReviewed !== false
      || asset.publicRedistribution !== "held"
      || asset.localDisplay?.state !== "allowed"
      || asset.localDisplay?.humanReviewed !== false
      || asset.localDisplay?.publicRedistribution !== "held"
      || asset.localDisplay?.sourceSha256 !== entry.sourceSha256) {
      throw new Error(`T95 source identity or hold changed: ${entry.sourceId}`);
    }
  }

  const result = structuredClone(source);
  for (const chunk of result.chunks) {
    for (const asset of chunk.assets) {
      const entry = entries.get(asset.id);
      if (!entry) continue;
      asset.regions = [...new Set([...asset.regions, ...entry.productRegions])];
    }
  }
  return result;
}
