import manifest from "../../../atlas-data/manifests/attachment-context-t13.json";
import canonicalData from "../../../atlas-data/catalog/canonical-catalog.json";
import type { AnnotationAssetContext } from "./annotationDrafts";
import type { SpatialDraftContext, SpatialDraftClaim, SpatialDraftReview, SpatialDraftInstance } from "./spatialDraftLayer";

export interface AttachmentContextRecord {
  attachmentId: string;
  descriptionClaimId: string;
  claimEvidenceIds: string[];
  ownerConceptId: string;
  instanceId: string;
  side: "right";
  role: string;
  targetStructureId: string;
  targetBoneId: string | null;
  sourceBoneFileId: string | null;
  contextMeshAssetId: string | null;
  contextStatus: "whole_bone_search_context_only" | "held_no_matching_target_mesh";
  spatialAnnotationId: null;
  geometry: null;
  precision: null;
  surfaceReviewState: "not_started";
  reason: string;
}

const records = manifest.records as AttachmentContextRecord[];
if (manifest.schemaVersion !== "T13-attachment-context-v2" || records.length !== 41 ||
  manifest.coverage.wholeBoneContexts + manifest.coverage.heldWithoutTargetMesh !== records.length ||
  manifest.coverage.locatedSurfaceAnnotations !== 0 ||
  records.some((row) => row.geometry !== null || row.spatialAnnotationId !== null || row.surfaceReviewState !== "not_started")) {
  throw new Error("T13 부착 검토용 컨텍스트의 coverage 또는 미검토 경계가 맞지 않습니다.");
}

export const attachmentContexts = records;
export const attachmentContextById = new Map(records.map((row) => [row.attachmentId, row]));

export function buildSpatialDraftContext(assets: readonly AnnotationAssetContext[]): SpatialDraftContext {
  const attachmentById = new Map(canonicalData.entities.attachments.map((row) => [row.id, row]));
  const claims = canonicalData.entities.claims as SpatialDraftClaim[];
  const claimById = new Map(claims.map((row) => [row.id, row]));
  const attachments = records.flatMap((contextRow) => {
    const attachment = attachmentById.get(contextRow.attachmentId);
    const claim = claimById.get(contextRow.descriptionClaimId);
    if (!attachment || !claim || attachment.descriptionClaimId !== claim.id || claim.subjectId !== attachment.id) return [];
    const ownerId = attachment.muscleOrPartId;
    const allowedAssetIds = assets.filter((asset) => asset.targetEntityId === ownerId).map((asset) => asset.assetId);
    if (contextRow.contextMeshAssetId) allowedAssetIds.push(contextRow.contextMeshAssetId);
    return [{
      id: attachment.id,
      ownerId,
      descriptionClaimId: claim.id,
      evidenceIds: [...claim.evidenceIds],
      allowedAssetIds: [...new Set(allowedAssetIds)],
    }];
  });
  return {
    assets,
    attachments,
    t13Records: records,
    claims,
    instances: canonicalData.entities.instances as SpatialDraftInstance[],
    reviews: canonicalData.entities.reviews as SpatialDraftReview[],
  };
}
