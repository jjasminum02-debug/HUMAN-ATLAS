import assert from "node:assert/strict";
import test from "node:test";
import { type BodyManifest } from "./contract.ts";
import { appendT101SceneExtension, type T101SceneExtension } from "./t101SceneExtension.ts";

const hash = (char: string) => char.repeat(64);
const specs = [
  ["FJ1393", "right", "foot"], ["FJ1393M", "left", "foot"], ["FJ1394M", "left", "leg"],
  ["FJ1395", "right", "thigh"], ["FJ1395M", "left", "thigh"], ["FJ1396", "right", "foot"],
  ["FJ1396M", "left", "foot"], ["FJ1397M", "left", "leg"], ["FJ1398", "right", "foot"], ["FJ1398M", "left", "foot"],
] as const;
const holds = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];

function parent(): BodyManifest {
  return { version: 2, localOnly: true, publicRedistribution: "held", frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [{ id: "parent", url: "/__atlas/body/parent.glb", sha256: hash("a"), bytes: 42, assets: [] }] };
}

function extension(): T101SceneExtension {
  return { revision: "BodyParts3D-R4-T101-SAME-SCENE-EXTENSION-v1", task: "T101", frozenSourceSetSha256: hash("b"),
    parentSourceManifestSha256: hash("c"), parentProductContextOverlaySha256: hash("d"), parentT79SourceManifestSha256: hash("e"),
    parentT79IntegrationExtensionSha256: hash("f"), sourceManifestSha256: hash("1"),
    sceneContract: { projectFrame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", projectUnit: "m", sourceId: "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
      pose: "bodyparts3d-r4-static-reference", oneAnatomySceneRoot: true, oneRenderer: true, cameraOwner: "existing AnatomySceneController",
      extensionMode: "append source-only nodes into the existing scene" },
    chunks: [{ id: "t101-lower-limb-muscle", url: "/__atlas/body/t101-lower-limb-muscle.glb", sha256: hash("2"), bytes: 1024,
      assets: specs.map(([id, side, owner], index) => ({
        id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256: hash((index + 3).toString(16)), regions: [owner], primaryOwner: owner, side,
        layer: "muscle", defaultVisible: true, supplement: false, pickState: "source_only_unbound", stableIds: [], holdReasons: holds,
        humanReviewed: false, bounds: [[0, 0, 0], [1, 1, 1]], publicRedistribution: "held", sourcePackage: "T101",
        localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: true, state: "allowed", sourceSha256: hash((index + 3).toString(16)),
          integrityHolds: [], evidenceIds: ["source-manifest", "validation"], retainedHoldReasons: holds, bindingState: "source_only_unbound",
          publicRedistribution: "held", humanReviewed: false, basis: "verified_local_source_context_only" },
      })),
    }],
  };
}

test("T101 appends its exact ten source-only surfaces into the existing scene", () => {
  const base = parent();
  const before = structuredClone(base);
  const result = appendT101SceneExtension(base, extension());
  assert.deepEqual(base, before);
  assert.equal(result.revision, "BodyParts3D-R4-T101-SAME-SCENE-EXTENSION-v1");
  assert.equal(result.chunks.length, 2);
  assert.deepEqual(result.chunks[1].assets.map((asset) => asset.id), specs.map(([id]) => id));
  assert.equal(result.chunks[1].assets.filter((asset) => asset.side === "left").length, 6);
  assert.equal(result.chunks[1].assets.filter((asset) => asset.side === "right").length, 4);
  assert.ok(result.chunks[1].assets.every((asset) => asset.pickState === "source_only_unbound" && !asset.stableIds.length
    && asset.humanReviewed === false && asset.publicRedistribution === "held"));
});

test("T101 extension rejects changed IDs, collisions, frame, side, owner, binding, review, or rights", () => {
  const reject = (change: (value: T101SceneExtension) => void, source = parent()) => {
    const value = extension(); change(value); assert.throws(() => appendT101SceneExtension(source, value));
  };
  reject((value) => { value.chunks[0].assets.pop(); });
  reject((value) => { value.chunks[0].assets[0].id = "FJ9999"; });
  reject((value) => { value.sceneContract.projectFrame = "other"; });
  reject((value) => { value.chunks[0].assets[0].side = "left"; });
  reject((value) => { value.chunks[0].assets[0].regions = ["thigh"]; });
  reject((value) => { value.chunks[0].assets[0].stableIds = ["invented"] as never; });
  reject((value) => { value.chunks[0].assets[0].humanReviewed = true as never; });
  reject((value) => { value.chunks[0].assets[0].localDisplay!.publicRedistribution = "allowed" as never; });
  const duplicate = parent();
  duplicate.chunks[0].assets.push({ ...extension().chunks[0].assets[0] });
  reject(() => {}, duplicate);
});
