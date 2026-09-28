import assert from "node:assert/strict";
import test from "node:test";
import { type BodyManifest } from "./contract.ts";
import { appendT102SceneExtension, type T102SceneExtension } from "./t102SceneExtension.ts";

const hash = (char: string) => char.repeat(64);
const specs = [
  ["FJ1441", "right", "thigh"], ["FJ1441M", "left", "thigh"], ["FJ1442", "right", "thigh"], ["FJ1442M", "left", "thigh"],
  ["FJ1443", "right", "thigh"], ["FJ1443M", "left", "thigh"], ["FJ1444", "right", "thigh"], ["FJ1444M", "left", "thigh"],
  ["FJ1445", "right", "foot"], ["FJ1445M", "left", "foot"],
] as const;
const holds = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];

function parent(): BodyManifest {
  return { version: 2, localOnly: true, publicRedistribution: "held", frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [
      { id: "parent", url: "/__atlas/body/parent.glb", sha256: hash("a"), bytes: 42, assets: [] },
      { id: "t101-lower-limb-muscle", url: "/__atlas/body/t101-lower-limb-muscle.glb", sha256: hash("b"), bytes: 42, assets: [] },
    ] };
}

function extension(): T102SceneExtension {
  return { revision: "BodyParts3D-R4-T102-SAME-SCENE-EXTENSION-v1", task: "T102", frozenSourceSetSha256: hash("c"),
    parentSourceManifestSha256: hash("d"), parentProductContextOverlaySha256: hash("e"), parentT79SourceManifestSha256: hash("f"),
    parentT79IntegrationExtensionSha256: hash("1"), parentT101SourceManifestSha256: hash("2"), parentT101IntegrationExtensionSha256: hash("3"),
    sourceManifestSha256: hash("4"),
    sceneContract: { projectFrame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", projectUnit: "m", sourceId: "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
      pose: "bodyparts3d-r4-static-reference", oneAnatomySceneRoot: true, oneRenderer: true, cameraOwner: "existing AnatomySceneController",
      extensionMode: "append source-only nodes into the existing T77+T95+T79+T101 scene" },
    chunks: [{ id: "t102-lower-limb-muscle", url: "/__atlas/body/t102-lower-limb-muscle.glb", sha256: hash("5"), bytes: 1024,
      assets: specs.map(([id, side, owner], index) => ({
        id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256: hash((index + 6).toString(16)), regions: [owner], primaryOwner: owner, side,
        layer: "muscle", defaultVisible: true, supplement: false, pickState: "source_only_unbound", stableIds: [], holdReasons: holds,
        humanReviewed: false, bounds: [[0, 0, 0], [1, 1, 1]], publicRedistribution: "held", sourcePackage: "T102",
        localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: true, state: "allowed", sourceSha256: hash((index + 6).toString(16)),
          integrityHolds: [], evidenceIds: ["source-manifest", "validation"], retainedHoldReasons: holds, bindingState: "source_only_unbound",
          publicRedistribution: "held", humanReviewed: false, basis: "verified_local_source_context_only" },
      })),
    }],
  };
}

test("T102 appends its exact ten source-only surfaces once into the existing scene", () => {
  const base = parent();
  const before = structuredClone(base);
  const result = appendT102SceneExtension(base, extension());
  assert.deepEqual(base, before);
  assert.equal(result.chunks.length, 3);
  const assets = result.chunks[2].assets as T102SceneExtension["chunks"][number]["assets"];
  assert.deepEqual(assets.map((asset) => asset.id), specs.map(([id]) => id));
  assert.equal(assets.filter((asset) => asset.primaryOwner === "thigh").length, 8);
  assert.equal(assets.filter((asset) => asset.primaryOwner === "foot").length, 2);
  assert.equal(assets.filter((asset) => asset.side === "left").length, 5);
  assert.equal(assets.filter((asset) => asset.side === "right").length, 5);
  assert.ok(assets.every((asset) => asset.pickState === "source_only_unbound" && !asset.stableIds.length
    && asset.humanReviewed === false && asset.publicRedistribution === "held"));
});

test("T102 extension rejects changed IDs, collisions, frame, parent order, side, owner, binding, review, or rights", () => {
  const reject = (change: (value: T102SceneExtension) => void, source = parent()) => {
    const value = extension(); change(value); assert.throws(() => appendT102SceneExtension(source, value));
  };
  reject((value) => { value.chunks[0].assets.pop(); });
  reject((value) => { value.chunks[0].assets[0].id = "FJ9999"; });
  reject((value) => { value.sceneContract.projectFrame = "other"; });
  reject((value) => { value.chunks[0].assets[0].side = "left"; });
  reject((value) => { value.chunks[0].assets[0].regions = ["foot"]; });
  reject((value) => { value.chunks[0].assets[0].stableIds = ["invented"] as never; });
  reject((value) => { value.chunks[0].assets[0].humanReviewed = true as never; });
  reject((value) => { value.chunks[0].assets[0].localDisplay!.publicRedistribution = "allowed" as never; });
  const collision = parent();
  collision.chunks[0].assets.push({ ...extension().chunks[0].assets[0] });
  reject(() => {}, collision);
  const wrongParent = parent();
  wrongParent.chunks[1].id = "unrelated-scene";
  wrongParent.chunks[1].url = "/__atlas/body/unrelated-scene.glb";
  reject(() => {}, wrongParent);
});
