import assert from "node:assert/strict";
import test from "node:test";
import { type BodyManifest } from "./contract.ts";
import { appendT79SceneExtension, type SourceOnlySceneExtension } from "./taskExtension.ts";

const hash = (char: string) => char.repeat(64);
const ids = ["FJ1512", "FJ1512M", "FJ1478", "FJ1478M", "FJ1479", "FJ1479M", "FJ1480", "FJ1480M", "FJ1477", "FJ1477M"];
const holds = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];

function parent(): BodyManifest {
  return { version: 2, localOnly: true, publicRedistribution: "held", frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", unit: "m", lodLevels: 1,
    chunks: [{ id: "parent", url: "/__atlas/body/parent.glb", sha256: hash("a"), bytes: 42, assets: [] }] };
}

function extension(): SourceOnlySceneExtension {
  return {
    revision: "BodyParts3D-R4-T79-SAME-SCENE-EXTENSION-v1", task: "T79", frozenSourceSetSha256: hash("b"),
    parentSourceManifestSha256: hash("c"), parentProductContextOverlaySha256: hash("d"), sourceManifestSha256: hash("e"),
    sceneContract: { projectFrame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", projectUnit: "m", sourceId: "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
      pose: "bodyparts3d-r4-static-reference", oneAnatomySceneRoot: true, oneRenderer: true, cameraOwner: "existing AnatomySceneController",
      extensionMode: "append source-only nodes to T77 + T95 runtime manifest; do not replace renderer/root/camera" },
    chunks: [{ id: "t79-upper-limb-muscle", url: "/__atlas/body/t79-upper-limb-muscle.glb", sha256: hash("f"), bytes: 1024,
      assets: ids.map((id, index) => ({
        id, nodeId: `HA-MESH-BP3D4-${id}`, sourceSha256: hash((index + 1).toString(16).slice(-1)), regions: ["upper-limb"],
        side: id.endsWith("M") ? "left" : "right", layer: "muscle", defaultVisible: true, supplement: false,
        pickState: "source_only_unbound", stableIds: [], holdReasons: holds, humanReviewed: false,
        bounds: [[-0.24, 1.0, -0.11], [0.24, 1.3, -0.02]], publicRedistribution: "held", sourcePackage: "T79",
        localDisplay: { beforeDefaultVisible: false, afterDefaultVisible: true, state: "allowed", sourceSha256: hash((index + 1).toString(16).slice(-1)),
          integrityHolds: [], evidenceIds: ["source-manifest", "validation"], retainedHoldReasons: holds, bindingState: "source_only_unbound",
          publicRedistribution: "held", humanReviewed: false, basis: "verified_local_source_context_only" },
      } as const)),
    }],
  };
}

test("T79 appends ten source-only nodes to the same manifest without mutating parent", () => {
  const base = parent();
  const before = structuredClone(base);
  const result = appendT79SceneExtension(base, extension());
  assert.deepEqual(base, before);
  assert.equal(result.revision, "BodyParts3D-R4-T79-SAME-SCENE-EXTENSION-v1");
  assert.equal(result.chunks.length, 2);
  assert.deepEqual(result.chunks.flatMap((chunk) => chunk.assets.map((asset) => asset.id)).slice(-10), ids);
  assert.ok(result.chunks[1].assets.every((asset) => asset.pickState === "source_only_unbound" && !asset.stableIds.length && asset.humanReviewed === false));
});

test("T79 extension rejects missing/extra IDs, source collisions, frame drift, binding and review promotion", () => {
  const base = parent();
  const reject = (change: (value: SourceOnlySceneExtension) => void, source = base) => {
    const value = extension(); change(value); assert.throws(() => appendT79SceneExtension(source, value));
  };
  reject((value) => { value.chunks[0].assets.pop(); });
  reject((value) => { value.chunks[0].assets[0].id = "FJ9999"; });
  reject((value) => { value.sceneContract.projectFrame = "other"; });
  reject((value) => { value.chunks[0].assets[0].stableIds = ["invented"] as never; });
  reject((value) => { value.chunks[0].assets[0].humanReviewed = true as never; });
  reject((value) => { value.chunks[0].assets[0].localDisplay!.publicRedistribution = "allowed" as never; });
  const duplicate = parent();
  duplicate.chunks[0].assets.push({
    ...extension().chunks[0].assets[0], id: "FJ1512",
  });
  reject(() => {}, duplicate);
});
