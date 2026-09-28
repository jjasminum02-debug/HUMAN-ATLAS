import assert from "node:assert/strict";
import test from "node:test";
import { type BodyManifest } from "./contract.ts";
import { appendT103SceneExtension, type T103SceneExtension } from "./t103SceneExtension.ts";

const hash = (char: string) => char.repeat(64);
const specs = [
  ["FJ1473", "right"], ["FJ1473M", "left"], ["FJ1474", "right"], ["FJ1474M", "left"], ["FJ1481", "right"],
  ["FJ1481M", "left"], ["FJ1514", "right"], ["FJ1514M", "left"], ["FJ1515", "right"], ["FJ1515M", "left"],
] as const;
const holds = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];

function heldParentAsset(id: string): BodyManifest["chunks"][number]["assets"][number] {
  const h = hash(id === "FJ1469" ? "a" : "b");
  return { id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256: h, regions: ["upper-limb"], side: id === "FJ1469" ? "left" : "right",
    layer: "muscle", defaultVisible: false, supplement: false, pickState: "held", stableIds: [], holdReasons: ["T54_source_label_surface_pair_conflict"],
    humanReviewed: false, bounds: [[-0.31, 0.76, 0.12], [-0.25, 0.80, 0.16]], publicRedistribution: "held", sourcePackage: "T54",
    localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: false, state: "held", sourceSha256: h,
      integrityHolds: ["T54_source_label_surface_pair_conflict"], evidenceIds: [], retainedHoldReasons: ["T54_source_label_surface_pair_conflict"],
      bindingState: "held", publicRedistribution: "held", humanReviewed: false, basis: "preserved_historical_policy" } };
}

function parent(): BodyManifest {
  return { version: 2, localOnly: true, publicRedistribution: "held", frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [
      { id: "parent", url: "/__atlas/body/parent.glb", sha256: hash("c"), bytes: 42, assets: [heldParentAsset("FJ1469"), heldParentAsset("FJ1469M")] },
      { id: "t102-lower-limb-muscle", url: "/__atlas/body/t102-lower-limb-muscle.glb", sha256: hash("d"), bytes: 42, assets: [] },
    ] };
}

function extension(): T103SceneExtension {
  return { revision: "BodyParts3D-R4-T103-SAME-SCENE-EXTENSION-v1", task: "T103", frozenSourceSetSha256: hash("e"),
    parentSourceManifestSha256: hash("f"), parentProductContextOverlaySha256: hash("1"), parentT79SourceManifestSha256: hash("2"),
    parentT79IntegrationExtensionSha256: hash("3"), parentT101SourceManifestSha256: hash("4"), parentT101IntegrationExtensionSha256: hash("5"),
    parentT102SourceManifestSha256: hash("6"), parentT102IntegrationExtensionSha256: hash("7"), sourceManifestSha256: hash("8"),
    sceneContract: { projectFrame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", projectUnit: "m", sourceId: "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
      pose: "bodyparts3d-r4-static-reference", oneAnatomySceneRoot: true, oneRenderer: true, cameraOwner: "existing AnatomySceneController",
      extensionMode: "append T103 exact source-only meshes after the T102 extension in the same scene" },
    chunks: [{ id: "t103-upper-limb-muscle-parts", url: "/__atlas/body/t103-upper-limb-muscle-parts.glb", sha256: hash("9"), bytes: 2048,
      assets: specs.map(([id, side], index) => {
        const sourceHash = hash((index + 1).toString(16));
        return { id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256: sourceHash, regions: ["upper-limb"], primaryOwner: "upper-limb", side,
          layer: "muscle", defaultVisible: true, supplement: false, pickState: "source_only_unbound", stableIds: [], holdReasons: holds,
          humanReviewed: false, bounds: [[-0.31, 0.70, 0.08], [-0.17, 1.08, 0.19]], publicRedistribution: "held", sourcePackage: "T103",
          localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: true, state: "allowed", sourceSha256: sourceHash,
            integrityHolds: [], evidenceIds: ["source-manifest", "browser-validation"], retainedHoldReasons: holds, bindingState: "source_only_unbound",
            publicRedistribution: "held", humanReviewed: false, basis: "verified_local_source_context_only" } };
      }),
    }],
  };
}

test("T103 appends its exact ten source-only nodes once after T102 and retains held T54 parents", () => {
  const base = parent(); const before = structuredClone(base);
  const result = appendT103SceneExtension(base, extension());
  assert.deepEqual(base, before);
  assert.equal(result.revision, "BodyParts3D-R4-T103-SAME-SCENE-EXTENSION-v1");
  assert.equal(result.chunks.length, 3);
  assert.deepEqual(result.chunks[2].assets.map(asset => asset.id), specs.map(([id]) => id));
  assert.equal(result.chunks[2].assets.filter(asset => asset.side === "right").length, 5);
  assert.equal(result.chunks[2].assets.filter(asset => asset.side === "left").length, 5);
  assert.ok(result.chunks[0].assets.every(asset => asset.defaultVisible === false && asset.pickState === "held"));
  assert.ok(result.chunks[2].assets.every(asset => asset.pickState === "source_only_unbound" && !asset.stableIds.length
    && asset.humanReviewed === false && asset.publicRedistribution === "held"));
});

test("T103 rejects changed IDs, duplicates, wrong side/frame/parent, visible whole-FPB parent, binding, review, or rights", () => {
  const reject = (change: (value: T103SceneExtension) => void, source = parent()) => {
    const value = extension(); change(value); assert.throws(() => appendT103SceneExtension(source, value));
  };
  reject(value => { value.chunks[0].assets.pop(); });
  reject(value => { value.chunks[0].assets[0].id = "FJ9999"; });
  reject(value => { value.chunks[0].assets[0].side = "left"; });
  reject(value => { value.sceneContract.projectFrame = "other"; });
  reject(value => { value.parentT102IntegrationExtensionSha256 = "bad"; });
  const visibleParent = parent(); visibleParent.chunks[0].assets[0].defaultVisible = true;
  reject(() => {}, visibleParent);
  const duplicate = parent(); duplicate.chunks[0].assets.push({ ...extension().chunks[0].assets[0] });
  reject(() => {}, duplicate);
  reject(value => { value.chunks[0].assets[0].stableIds = ["invented"] as never; });
  reject(value => { value.chunks[0].assets[0].humanReviewed = true as never; });
  reject(value => { value.chunks[0].assets[0].localDisplay!.publicRedistribution = "allowed" as never; });
});
