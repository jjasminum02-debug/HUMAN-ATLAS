import { type BodyAsset, type BodyChunk, type BodyManifest, validateManifest } from "./contract.ts";

type T103Asset = BodyAsset & { primaryOwner: "upper-limb" };
type T103Chunk = Omit<BodyChunk, "assets"> & { assets: T103Asset[] };

export interface T103SceneExtension {
  revision: string;
  task: "T103";
  frozenSourceSetSha256: string;
  parentSourceManifestSha256: string;
  parentProductContextOverlaySha256: string;
  parentT79SourceManifestSha256: string;
  parentT79IntegrationExtensionSha256: string;
  parentT101SourceManifestSha256: string;
  parentT101IntegrationExtensionSha256: string;
  parentT102SourceManifestSha256: string;
  parentT102IntegrationExtensionSha256: string;
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
  chunks: T103Chunk[];
}

const T103_SIDES: Record<string, "left" | "right"> = {
  FJ1473: "right", FJ1473M: "left", FJ1474: "right", FJ1474M: "left", FJ1481: "right",
  FJ1481M: "left", FJ1514: "right", FJ1514M: "left", FJ1515: "right", FJ1515M: "left",
};
const T103_HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];
const PARENT_FPB_HOLD = "T54_source_label_surface_pair_conflict";
const SHA256 = /^[a-f0-9]{64}$/;

/** Append only T103's verified source-only head surfaces after T102 in the existing one-root scene. */
export function appendT103SceneExtension(parent: BodyManifest, extension: T103SceneExtension): BodyManifest {
  validateManifest(parent);
  if (extension.task !== "T103" || extension.revision !== "BodyParts3D-R4-T103-SAME-SCENE-EXTENSION-v1") throw new Error("Invalid T103 extension identity");
  const hashes = [extension.frozenSourceSetSha256, extension.parentSourceManifestSha256, extension.parentProductContextOverlaySha256,
    extension.parentT79SourceManifestSha256, extension.parentT79IntegrationExtensionSha256, extension.parentT101SourceManifestSha256,
    extension.parentT101IntegrationExtensionSha256, extension.parentT102SourceManifestSha256, extension.parentT102IntegrationExtensionSha256,
    extension.sourceManifestSha256];
  if (!hashes.every(hash => SHA256.test(hash))) throw new Error("Invalid T103 integrity reference");
  const scene = extension.sceneContract;
  const lastParentChunk = parent.chunks[parent.chunks.length - 1];
  if (!parent.localOnly || parent.publicRedistribution !== "held" || scene.projectFrame !== parent.frame || scene.projectUnit !== parent.unit
    || parent.unit !== "m" || parent.frame !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
    || lastParentChunk?.id !== "t102-lower-limb-muscle"
    || scene.sourceId !== "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0" || scene.pose !== "bodyparts3d-r4-static-reference"
    || scene.oneAnatomySceneRoot !== true || scene.oneRenderer !== true || scene.cameraOwner !== "existing AnatomySceneController") {
    throw new Error("T103 frame/pose/root/renderer contract differs from its active T102 parent scene");
  }
  if (extension.chunks.length !== 1 || extension.chunks[0]?.id !== "t103-upper-limb-muscle-parts") throw new Error("T103 must append exactly one upper-limb source chunk");

  const parentAssets = parent.chunks.flatMap(chunk => chunk.assets);
  const existingIds = new Set(parentAssets.map(asset => asset.id));
  const parentWholeFpb = new Map(parentAssets.filter(asset => asset.id === "FJ1469" || asset.id === "FJ1469M").map(asset => [asset.id, asset]));
  if (parentWholeFpb.size !== 2 || [...parentWholeFpb.values()].some(asset => asset.defaultVisible !== false || asset.pickState !== "held"
    || !asset.holdReasons.includes(PARENT_FPB_HOLD))) {
    throw new Error("T103 requires the existing T54 whole-FPB source-label conflict holds to remain hidden");
  }

  const assets = extension.chunks[0].assets;
  const expectedIds = Object.keys(T103_SIDES);
  if (assets.length !== expectedIds.length || new Set(assets.map(asset => asset.id)).size !== assets.length
    || !expectedIds.every(id => assets.some(asset => asset.id === id)) || assets.some(asset => !expectedIds.includes(asset.id))) {
    throw new Error("T103 source FJ set is incomplete, duplicated, or expanded");
  }
  for (const asset of assets) {
    const decision = asset.localDisplay;
    if (existingIds.has(asset.id) || asset.sourcePackage !== "T103" || asset.nodeId !== `HA-MESH-BP3D4-${asset.id}`
      || !SHA256.test(asset.sourceSha256) || asset.layer !== "muscle" || asset.side !== T103_SIDES[asset.id]
      || asset.primaryOwner !== "upper-limb" || asset.regions.length !== 1 || asset.regions[0] !== "upper-limb"
      || asset.defaultVisible !== true || asset.supplement !== false || asset.pickState !== "source_only_unbound"
      || asset.stableIds.length !== 0 || asset.humanReviewed !== false || asset.publicRedistribution !== "held"
      || JSON.stringify(asset.holdReasons) !== JSON.stringify(T103_HOLDS)
      || !decision || decision.state !== "allowed" || decision.beforeDefaultVisible !== false || decision.afterDefaultVisible !== true
      || decision.sourceSha256 !== asset.sourceSha256 || decision.bindingState !== "source_only_unbound"
      || decision.publicRedistribution !== "held" || decision.humanReviewed !== false || decision.integrityHolds.length !== 0
      || JSON.stringify(decision.retainedHoldReasons) !== JSON.stringify(T103_HOLDS)
      || decision.basis !== "verified_local_source_context_only" || decision.evidenceIds.length < 2) {
      throw new Error(`T103 source-only, side, local-display, rights, or review policy invalid for ${asset.id}`);
    }
  }
  const result: BodyManifest = { ...parent, revision: extension.revision, chunks: [...parent.chunks, ...extension.chunks] };
  validateManifest(result);
  return result;
}
