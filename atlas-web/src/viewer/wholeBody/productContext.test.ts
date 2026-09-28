import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { applyProductContextOverlay, type ProductContextOverlay } from "./productContext.ts";
import type { BodyAsset, BodyManifest } from "./contract.ts";

const overlay = JSON.parse(readFileSync(new URL("../../../../atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json", import.meta.url), "utf8")) as ProductContextOverlay;
const sourceRows: Array<[string, string, string, string[], string]> = [
  ["FJ3237", "2491009d53eaed99ccb2a802b29402eec715eb8d207fb819fad67b0720195cf2", "left", ["shoulder-scapular", "thorax"], "source-only"],
  ["FJ3279", "e63a5675c6cdbe942322305920241b4a63762d7a65879572400f444fa3d42739", "left", ["shoulder-scapular", "thorax"], "source-only"],
  ["FJ3362", "9a111cac8351e79dd1315aea90108fe56f78e4bf0159473e6ad727ba91b60e6d", "right", ["shoulder-scapular", "upper-limb"], "source-only"],
  ["FJ3384", "1641b04e55f9d75bdd6f1f4f07ea596e5dea0a8cb6b348bff47281b8a0bc6e5d", "right", ["shoulder-scapular", "upper-limb"], "source-only"],
];

function makeAsset([id, sourceSha256, side, regions]: typeof sourceRows[number]): BodyAsset {
  return {
    id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256, regions: [...regions], side,
    layer: "bone", defaultVisible: true, supplement: false, pickState: "source_only_unbound",
    stableIds: [], holdReasons: [], humanReviewed: false,
    localDisplay: {
      beforeDefaultVisible: true, afterDefaultVisible: true, state: "allowed", sourceSha256,
      integrityHolds: [], evidenceIds: [], retainedHoldReasons: [], bindingState: "source_only_unbound",
      publicRedistribution: "held", humanReviewed: false, basis: "preserved_historical_policy",
    },
    publicRedistribution: "held", bounds: [[0, 0, 0], [1, 1, 1]],
  };
}

function fixture(): BodyManifest {
  return {
    version: 2, localOnly: true, publicRedistribution: "held",
    frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [{ id: "shoulder", url: "/__atlas/body/shoulder.glb", sha256: "a".repeat(64), bytes: 10, assets: sourceRows.map(makeAsset) }],
  };
}

test("T95 product context adds left scapula membership without editing source or duplicating nodes", () => {
  const source = fixture();
  const before = structuredClone(source);
  const result = applyProductContextOverlay(source, overlay);
  assert.deepEqual(source, before, "source manifest must remain immutable");
  const byId = new Map(result.chunks.flatMap((chunk) => chunk.assets.map((asset) => [asset.id, asset] as const)));
  assert.deepEqual(byId.get("FJ3279")?.regions, ["shoulder-scapular", "thorax", "upper-limb"]);
  assert.deepEqual(byId.get("FJ3384")?.regions, ["shoulder-scapular", "upper-limb"]);
  assert.deepEqual(byId.get("FJ3237")?.regions, ["shoulder-scapular", "thorax"]);
  assert.deepEqual(byId.get("FJ3362")?.regions, ["shoulder-scapular", "upper-limb"]);
  assert.equal(new Set(result.chunks.flatMap((chunk) => chunk.assets.map((asset) => asset.nodeId))).size, 4);
  for (const asset of byId.values()) {
    assert.equal(asset.pickState, "source_only_unbound");
    assert.deepEqual(asset.stableIds, []);
    assert.equal(asset.humanReviewed, false);
    assert.equal(asset.publicRedistribution, "held");
    assert.equal(asset.defaultVisible, true);
  }
});

test("T95 context overlay rejects source identity, laterality, region, policy, and duplicate drift", () => {
  const reject = (asset: BodyAsset, changedOverlay: ProductContextOverlay = overlay) => {
    const source = fixture();
    source.chunks[0].assets[source.chunks[0].assets.findIndex((row) => row.id === asset.id)] = asset;
    assert.throws(() => applyProductContextOverlay(source, changedOverlay));
  };
  reject({ ...makeAsset(sourceRows[1]), sourceSha256: "b".repeat(64) });
  reject({ ...makeAsset(sourceRows[1]), side: "right" });
  const reviewedAsset = makeAsset(sourceRows[1]);
  const promoted = { ...reviewedAsset, localDisplay: { ...reviewedAsset.localDisplay!, humanReviewed: true } } as unknown as BodyAsset;
  reject(promoted);
  const wrongRegions = structuredClone(overlay);
  wrongRegions.entries.find((entry) => entry.sourceId === "FJ3279")!.sourceRegions = ["upper-limb"];
  reject(makeAsset(sourceRows[1]), wrongRegions);
  const duplicate = structuredClone(overlay);
  duplicate.entries.push(structuredClone(duplicate.entries[0]));
  assert.throws(() => applyProductContextOverlay(fixture(), duplicate));
});
