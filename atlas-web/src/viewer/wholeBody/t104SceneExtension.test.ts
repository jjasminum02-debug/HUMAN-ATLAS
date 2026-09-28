import assert from "node:assert/strict";
import test from "node:test";
import { type BodyManifest } from "./contract.ts";
import { appendT104SceneExtension, type T104SceneExtension } from "./t104SceneExtension.ts";

const hash = (char: string) => char.repeat(64);
const specs = [
  ["FJ1516", "right", "upper-limb"], ["FJ1516M", "left", "upper-limb"], ["FJ1518", "right", "upper-limb"],
  ["FJ1518M", "left", "upper-limb"], ["FJ1557", "left", "neck"], ["FJ1600", "left", "neck"],
  ["FJ1601", "left", "neck"], ["FJ2774", "left", "neck"], ["FJ2781", "left", "neck"], ["FJ2783", "left", "neck"],
] as const;
const holds = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];

function parent(): BodyManifest {
  return { version: 2, localOnly: true, publicRedistribution: "held", frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [
      { id: "base", url: "/__atlas/body/base.glb", sha256: hash("a"), bytes: 42, assets: [] },
      { id: "t103-upper-limb-muscle-parts", url: "/__atlas/body/t103-upper-limb-muscle-parts.glb", sha256: hash("b"), bytes: 42, assets: [] },
    ] };
}

function extension(): T104SceneExtension {
  const references = { frozenSourceSetSha256: hash("c"), parentSourceManifestSha256: hash("d"), parentProductContextOverlaySha256: hash("e"),
    parentT79SourceManifestSha256: hash("f"), parentT79IntegrationExtensionSha256: hash("1"), parentT101SourceManifestSha256: hash("2"),
    parentT101IntegrationExtensionSha256: hash("3"), parentT102SourceManifestSha256: hash("4"), parentT102IntegrationExtensionSha256: hash("5"),
    parentT103SourceManifestSha256: hash("6"), parentT103IntegrationExtensionSha256: hash("7"), sourceManifestSha256: hash("8") };
  const assets = specs.map(([id, side, owner], index) => {
    const sourceSha256 = hash(((index + 1) % 16).toString(16).slice(-1));
    return { id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256, regions: [owner], primaryOwner: owner, sourcePackage: "T104" as const, side,
      layer: "muscle" as const, defaultVisible: true, supplement: false, pickState: "source_only_unbound", stableIds: [], holdReasons: holds,
      humanReviewed: false, bounds: [[0, 0, 0], [1, 1, 1]] as [number[], number[]], publicRedistribution: "held" as const,
      localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: true, state: "allowed" as const, sourceSha256,
        integrityHolds: [], evidenceIds: ["source-manifest", "browser-validation"], retainedHoldReasons: holds,
        bindingState: "source_only_unbound", publicRedistribution: "held" as const, humanReviewed: false as const,
        basis: "verified_local_source_context_only" },
    };
  });
  return { revision: "BodyParts3D-R4-T104-SAME-SCENE-EXTENSION-v1", task: "T104", ...references,
    sceneContract: { projectFrame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", projectUnit: "m", sourceId: "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
      pose: "bodyparts3d-r4-static-reference", oneAnatomySceneRoot: true, oneRenderer: true, cameraOwner: "existing AnatomySceneController",
      extensionMode: "append the T104 exact source-only limb and neck chunks after T103 in the same scene" },
    chunks: [
      { id: "t104-upper-limb-muscle-parts", url: "/__atlas/body/t104-upper-limb-muscle-parts.glb", sha256: hash("a"), bytes: 1024,
        assets: assets.filter((asset) => asset.primaryOwner === "upper-limb") },
      { id: "t104-neck-muscle-parts", url: "/__atlas/body/t104-neck-muscle-parts.glb", sha256: hash("b"), bytes: 2048,
        assets: assets.filter((asset) => asset.primaryOwner === "neck") },
    ],
  };
}

test("T104 appends its exact ten source-only meshes after T103 in the same scene", () => {
  const base = parent(); const before = structuredClone(base); const value = extension();
  const result = appendT104SceneExtension(base, value);
  assert.deepEqual(base, before);
  assert.equal(result.revision, "BodyParts3D-R4-T104-SAME-SCENE-EXTENSION-v1");
  assert.equal(result.chunks.length, 4);
  assert.deepEqual(result.chunks.slice(-2).map((chunk) => chunk.id), ["t104-upper-limb-muscle-parts", "t104-neck-muscle-parts"]);
  const assets = value.chunks.flatMap((chunk) => chunk.assets);
  assert.deepEqual(assets.map((asset) => asset.id), specs.map(([id]) => id));
  assert.equal(assets.filter((asset) => asset.primaryOwner === "upper-limb").length, 4);
  assert.equal(assets.filter((asset) => asset.primaryOwner === "neck").length, 6);
  assert.equal(assets.filter((asset) => asset.side === "right").length, 2);
  assert.equal(assets.filter((asset) => asset.side === "left").length, 8);
  assert.ok(assets.every((asset) => asset.pickState === "source_only_unbound" && !asset.stableIds.length
    && asset.humanReviewed === false && asset.publicRedistribution === "held"));
});

test("T104 rejects changed membership, duplicate IDs, wrong side/region/frame/parent, binding, review, or rights", () => {
  const reject = (change: (value: T104SceneExtension) => void, source = parent()) => {
    const value = extension(); change(value); assert.throws(() => appendT104SceneExtension(source, value));
  };
  reject((value) => { value.chunks[0].assets.pop(); });
  reject((value) => { value.chunks[0].assets[0].id = "FJ9999"; });
  reject((value) => { value.chunks[0].assets[0].side = "left"; });
  reject((value) => { value.sceneContract.projectFrame = "other"; });
  reject((value) => { value.parentT103IntegrationExtensionSha256 = "bad"; });
  reject((value) => { value.chunks[0].assets[0].regions = ["neck"]; });
  reject((value) => { value.chunks[0].assets[0].stableIds = ["invented"] as never; });
  reject((value) => { value.chunks[0].assets[0].humanReviewed = true as never; });
  reject((value) => { value.chunks[0].assets[0].localDisplay!.publicRedistribution = "allowed" as never; });
  const collision = parent(); collision.chunks[0].assets.push({ ...extension().chunks[0].assets[0] });
  reject(() => {}, collision);
  const wrongParent = parent(); wrongParent.chunks[1].id = "unrelated-scene"; wrongParent.chunks[1].url = "/__atlas/body/unrelated-scene.glb";
  reject(() => {}, wrongParent);
});
