import { type BodyAsset, type BodyChunk, type BodyManifest, validateManifest } from "./contract.ts";

type T104Owner = "upper-limb" | "neck";
type T104Asset = BodyAsset & { primaryOwner: T104Owner; sourcePackage: "T104" };
type T104Chunk = Omit<BodyChunk, "assets"> & { assets: T104Asset[] };

export interface T104SceneExtension {
  revision: string;
  task: "T104";
  frozenSourceSetSha256: string;
  parentSourceManifestSha256: string;
  parentProductContextOverlaySha256: string;
  parentT79SourceManifestSha256: string;
  parentT79IntegrationExtensionSha256: string;
  parentT101SourceManifestSha256: string;
  parentT101IntegrationExtensionSha256: string;
  parentT102SourceManifestSha256: string;
  parentT102IntegrationExtensionSha256: string;
  parentT103SourceManifestSha256: string;
  parentT103IntegrationExtensionSha256: string;
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
  chunks: T104Chunk[];
}

const T104_SOURCE_REGIONS: Record<string, { side: "left" | "right"; owner: T104Owner }> = {
  FJ1516: { side: "right", owner: "upper-limb" }, FJ1516M: { side: "left", owner: "upper-limb" },
  FJ1518: { side: "right", owner: "upper-limb" }, FJ1518M: { side: "left", owner: "upper-limb" },
  FJ1557: { side: "left", owner: "neck" }, FJ1600: { side: "left", owner: "neck" }, FJ1601: { side: "left", owner: "neck" },
  FJ2774: { side: "left", owner: "neck" }, FJ2781: { side: "left", owner: "neck" }, FJ2783: { side: "left", owner: "neck" },
};
const T104_HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];
const SHA256 = /^[a-f0-9]{64}$/;

/** Append only T104's exact, source-only limb/neck surfaces after T103 in the existing scene. */
export function appendT104SceneExtension(parent: BodyManifest, extension: T104SceneExtension): BodyManifest {
  validateManifest(parent);
  if (extension.task !== "T104" || extension.revision !== "BodyParts3D-R4-T104-SAME-SCENE-EXTENSION-v1") {
    throw new Error("Invalid T104 extension identity");
  }
  const hashes = [extension.frozenSourceSetSha256, extension.parentSourceManifestSha256, extension.parentProductContextOverlaySha256,
    extension.parentT79SourceManifestSha256, extension.parentT79IntegrationExtensionSha256, extension.parentT101SourceManifestSha256,
    extension.parentT101IntegrationExtensionSha256, extension.parentT102SourceManifestSha256, extension.parentT102IntegrationExtensionSha256,
    extension.parentT103SourceManifestSha256, extension.parentT103IntegrationExtensionSha256, extension.sourceManifestSha256];
  if (!hashes.every((hash) => SHA256.test(hash))) throw new Error("Invalid T104 integrity reference");
  const scene = extension.sceneContract;
  const lastParentChunk = parent.chunks[parent.chunks.length - 1];
  if (!parent.localOnly || parent.publicRedistribution !== "held" || scene.projectFrame !== parent.frame || scene.projectUnit !== parent.unit
    || parent.unit !== "m" || parent.frame !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
    || lastParentChunk?.id !== "t103-upper-limb-muscle-parts"
    || scene.sourceId !== "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0" || scene.pose !== "bodyparts3d-r4-static-reference"
    || scene.oneAnatomySceneRoot !== true || scene.oneRenderer !== true || scene.cameraOwner !== "existing AnatomySceneController") {
    throw new Error("T104 frame/pose/root/renderer contract differs from its active T103 parent scene");
  }
  if (extension.chunks.length !== 2 || extension.chunks[0]?.id !== "t104-upper-limb-muscle-parts"
    || extension.chunks[1]?.id !== "t104-neck-muscle-parts") {
    throw new Error("T104 must append the exact upper-limb then neck chunks");
  }
  const parentAssets = parent.chunks.flatMap((chunk) => chunk.assets);
  const existingIds = new Set(parentAssets.map((asset) => asset.id));
  const assets = extension.chunks.flatMap((chunk) => chunk.assets);
  const expectedIds = Object.keys(T104_SOURCE_REGIONS);
  if (assets.length !== expectedIds.length || new Set(assets.map((asset) => asset.id)).size !== assets.length
    || !expectedIds.every((id) => assets.some((asset) => asset.id === id)) || assets.some((asset) => !expectedIds.includes(asset.id))) {
    throw new Error("T104 source FJ set is incomplete, duplicated, or expanded");
  }
  for (const chunk of extension.chunks) {
    const owner = chunk.id === "t104-upper-limb-muscle-parts" ? "upper-limb" : "neck";
    const expectedInChunk = expectedIds.filter((id) => T104_SOURCE_REGIONS[id].owner === owner);
    if (chunk.assets.length !== expectedInChunk.length || chunk.assets.some((asset) => T104_SOURCE_REGIONS[asset.id]?.owner !== owner)) {
      throw new Error(`T104 ${owner} chunk has wrong members`);
    }
  }
  for (const asset of assets) {
    const expected = T104_SOURCE_REGIONS[asset.id];
    const decision = asset.localDisplay;
    if (existingIds.has(asset.id) || asset.sourcePackage !== "T104" || asset.nodeId !== `HA-MESH-BP3D4-${asset.id}`
      || !SHA256.test(asset.sourceSha256) || asset.layer !== "muscle" || asset.side !== expected.side
      || asset.primaryOwner !== expected.owner || asset.regions.length !== 1 || asset.regions[0] !== expected.owner
      || asset.defaultVisible !== true || asset.supplement !== false || asset.pickState !== "source_only_unbound"
      || asset.stableIds.length !== 0 || asset.humanReviewed !== false || asset.publicRedistribution !== "held"
      || JSON.stringify(asset.holdReasons) !== JSON.stringify(T104_HOLDS)
      || !decision || decision.state !== "allowed" || decision.beforeDefaultVisible !== false || decision.afterDefaultVisible !== true
      || decision.sourceSha256 !== asset.sourceSha256 || decision.bindingState !== "source_only_unbound"
      || decision.publicRedistribution !== "held" || decision.humanReviewed !== false || decision.integrityHolds.length !== 0
      || JSON.stringify(decision.retainedHoldReasons) !== JSON.stringify(T104_HOLDS)
      || decision.basis !== "verified_local_source_context_only" || decision.evidenceIds.length < 2) {
      throw new Error(`T104 source-only, side, region, local-display, rights, or review policy invalid for ${asset.id}`);
    }
  }
  const result: BodyManifest = { ...parent, revision: extension.revision, chunks: [...parent.chunks, ...extension.chunks] };
  validateManifest(result);
  return result;
}
