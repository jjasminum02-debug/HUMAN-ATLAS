import { type BodyAsset, type BodyManifest, type BodyChunk, validateManifest } from "./contract.ts";

export interface SourceOnlySceneExtension {
  revision: string;
  task: "T79";
  frozenSourceSetSha256: string;
  parentSourceManifestSha256: string;
  parentProductContextOverlaySha256: string;
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
  chunks: BodyChunk[];
}

const T79_IDS = new Set([
  "FJ1512", "FJ1512M", "FJ1478", "FJ1478M", "FJ1479", "FJ1479M",
  "FJ1480", "FJ1480M", "FJ1477", "FJ1477M",
]);
const T79_HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"];
const SHA256 = /^[a-f0-9]{64}$/;

/** Append a bounded static source-only package to the one existing learner scene manifest. */
export function appendT79SceneExtension(parent: BodyManifest, extension: SourceOnlySceneExtension): BodyManifest {
  validateManifest(parent);
  if (extension.task !== "T79" || !extension.revision.startsWith("BodyParts3D-R4-T79-")) throw new Error("Invalid source extension identity");
  if (![extension.frozenSourceSetSha256, extension.parentSourceManifestSha256, extension.parentProductContextOverlaySha256, extension.sourceManifestSha256].every((hash) => SHA256.test(hash))) throw new Error("Invalid source extension integrity reference");
  if (!parent.localOnly || parent.publicRedistribution !== "held" || extension.sceneContract.projectFrame !== parent.frame
    || extension.sceneContract.projectUnit !== parent.unit || parent.unit !== "m" || parent.frame !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
    || extension.sceneContract.sourceId !== "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
    || extension.sceneContract.pose !== "bodyparts3d-r4-static-reference"
    || extension.sceneContract.oneAnatomySceneRoot !== true || extension.sceneContract.oneRenderer !== true
    || extension.sceneContract.cameraOwner !== "existing AnatomySceneController") {
    throw new Error("T79 scene frame/pose/root/renderer contract differs from the parent scene");
  }
  if (extension.chunks.length !== 1 || extension.chunks[0]?.id !== "t79-upper-limb-muscle") throw new Error("T79 must append its single frozen chunk");
  const existing = new Set(parent.chunks.flatMap((chunk) => chunk.assets.map((asset) => asset.id)));
  const assets: BodyAsset[] = extension.chunks.flatMap((chunk) => chunk.assets);
  if (assets.length !== T79_IDS.size || new Set(assets.map((asset) => asset.id)).size !== assets.length
    || !assets.every((asset) => T79_IDS.has(asset.id)) || !T79_IDS.size || [...T79_IDS].some((id) => !assets.some((asset) => asset.id === id))) {
    throw new Error("T79 source ID set is incomplete, duplicated, or expanded");
  }
  for (const asset of assets) {
    const decision = asset.localDisplay;
    if (existing.has(asset.id) || asset.sourcePackage !== "T79" || asset.nodeId !== `HA-MESH-BP3D4-${asset.id}`
      || !SHA256.test(asset.sourceSha256) || asset.layer !== "muscle" || asset.regions.length !== 1 || asset.regions[0] !== "upper-limb"
      || !["left", "right"].includes(asset.side ?? "") || asset.defaultVisible !== true || asset.supplement !== false
      || asset.pickState !== "source_only_unbound" || asset.stableIds.length !== 0 || asset.humanReviewed !== false
      || asset.publicRedistribution !== "held" || JSON.stringify(asset.holdReasons) !== JSON.stringify(T79_HOLDS)
      || !decision || decision.state !== "allowed" || decision.beforeDefaultVisible !== false || decision.afterDefaultVisible !== true
      || decision.sourceSha256 !== asset.sourceSha256 || decision.bindingState !== "source_only_unbound"
      || decision.publicRedistribution !== "held" || decision.humanReviewed !== false || decision.integrityHolds.length !== 0
      || JSON.stringify(decision.retainedHoldReasons) !== JSON.stringify(T79_HOLDS)
      || decision.basis !== "verified_local_source_context_only" || decision.evidenceIds.length < 2) {
      throw new Error(`T79 local display, identity, review, or redistribution hold invalid for ${asset.id}`);
    }
  }
  const result: BodyManifest = { ...parent, revision: extension.revision, chunks: [...parent.chunks, ...extension.chunks] };
  validateManifest(result);
  return result;
}
