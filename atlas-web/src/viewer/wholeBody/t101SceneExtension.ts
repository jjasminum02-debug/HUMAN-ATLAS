import { type BodyAsset, type BodyChunk, type BodyManifest, validateManifest } from "./contract.ts";

type T101Asset = BodyAsset & { primaryOwner: "foot" | "leg" | "thigh" };
type T101Chunk = Omit<BodyChunk, "assets"> & { assets: T101Asset[] };

export interface T101SceneExtension {
  revision: string;
  task: "T101";
  frozenSourceSetSha256: string;
  parentSourceManifestSha256: string;
  parentProductContextOverlaySha256: string;
  parentT79SourceManifestSha256: string;
  parentT79IntegrationExtensionSha256: string;
  sourceManifestSha256: string;
  sceneContract: {
    projectFrame: string;
    projectUnit: string;
    sourceId: string;
    pose: string;
    oneAnatomySceneRoot: boolean;
    oneRenderer: boolean;
    cameraOwner: string;
    extensionMode: string;
  };
  chunks: T101Chunk[];
}

const T101_SOURCE_REGIONS: Record<string, { side: "left" | "right"; owner: "foot" | "leg" | "thigh" }> = {
  FJ1393: { side: "right", owner: "foot" }, FJ1393M: { side: "left", owner: "foot" },
  FJ1394M: { side: "left", owner: "leg" }, FJ1395: { side: "right", owner: "thigh" }, FJ1395M: { side: "left", owner: "thigh" },
  FJ1396: { side: "right", owner: "foot" }, FJ1396M: { side: "left", owner: "foot" },
  FJ1397M: { side: "left", owner: "leg" }, FJ1398: { side: "right", owner: "foot" }, FJ1398M: { side: "left", owner: "foot" },
};
const T101_HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];
const SHA256 = /^[a-f0-9]{64}$/;

/** Append the frozen T101 static source-only surfaces into the existing one-root scene. */
export function appendT101SceneExtension(parent: BodyManifest, extension: T101SceneExtension): BodyManifest {
  validateManifest(parent);
  if (extension.task !== "T101" || extension.revision !== "BodyParts3D-R4-T101-SAME-SCENE-EXTENSION-v1") throw new Error("Invalid T101 extension identity");
  const hashes = [extension.frozenSourceSetSha256, extension.parentSourceManifestSha256, extension.parentProductContextOverlaySha256,
    extension.parentT79SourceManifestSha256, extension.parentT79IntegrationExtensionSha256, extension.sourceManifestSha256];
  if (!hashes.every((hash) => SHA256.test(hash))) throw new Error("Invalid T101 integrity reference");
  const scene = extension.sceneContract;
  if (!parent.localOnly || parent.publicRedistribution !== "held" || scene.projectFrame !== parent.frame || scene.projectUnit !== parent.unit
    || parent.unit !== "m" || parent.frame !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
    || scene.sourceId !== "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0" || scene.pose !== "bodyparts3d-r4-static-reference"
    || scene.oneAnatomySceneRoot !== true || scene.oneRenderer !== true || scene.cameraOwner !== "existing AnatomySceneController") {
    throw new Error("T101 frame/pose/root/renderer contract differs from its active parent scene");
  }
  if (extension.chunks.length !== 1 || extension.chunks[0]?.id !== "t101-lower-limb-muscle") throw new Error("T101 must append exactly one frozen lower-limb chunk");

  const existingIds = new Set(parent.chunks.flatMap((chunk) => chunk.assets.map((asset) => asset.id)));
  const assets = extension.chunks[0].assets;
  const expectedIds = Object.keys(T101_SOURCE_REGIONS);
  if (assets.length !== expectedIds.length || new Set(assets.map((asset) => asset.id)).size !== assets.length
    || !expectedIds.every((id) => assets.some((asset) => asset.id === id)) || assets.some((asset) => !expectedIds.includes(asset.id))) {
    throw new Error("T101 source FJ set is incomplete, duplicated, or expanded");
  }
  for (const asset of assets) {
    const expected = T101_SOURCE_REGIONS[asset.id];
    const decision = asset.localDisplay;
    if (existingIds.has(asset.id) || asset.sourcePackage !== "T101" || asset.nodeId !== `HA-MESH-BP3D4-${asset.id}`
      || !SHA256.test(asset.sourceSha256) || asset.layer !== "muscle" || asset.side !== expected.side
      || asset.primaryOwner !== expected.owner || asset.regions.length !== 1 || asset.regions[0] !== expected.owner
      || asset.defaultVisible !== true || asset.supplement !== false || asset.pickState !== "source_only_unbound"
      || asset.stableIds.length !== 0 || asset.humanReviewed !== false || asset.publicRedistribution !== "held"
      || JSON.stringify(asset.holdReasons) !== JSON.stringify(T101_HOLDS)
      || !decision || decision.state !== "allowed" || decision.beforeDefaultVisible !== false || decision.afterDefaultVisible !== true
      || decision.sourceSha256 !== asset.sourceSha256 || decision.bindingState !== "source_only_unbound"
      || decision.publicRedistribution !== "held" || decision.humanReviewed !== false || decision.integrityHolds.length !== 0
      || JSON.stringify(decision.retainedHoldReasons) !== JSON.stringify(T101_HOLDS)
      || decision.basis !== "verified_local_source_context_only" || decision.evidenceIds.length < 2) {
      throw new Error(`T101 source-only, side, local-display, rights, or review policy invalid for ${asset.id}`);
    }
  }
  const result: BodyManifest = { ...parent, revision: extension.revision, chunks: [...parent.chunks, ...extension.chunks] };
  validateManifest(result);
  return result;
}
