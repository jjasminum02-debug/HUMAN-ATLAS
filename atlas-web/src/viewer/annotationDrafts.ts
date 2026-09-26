export const ANNOTATION_EXCHANGE_VERSION = "HA-annotation-draft-exchange-v1" as const;

export type AnnotationGeometry =
  | { kind: "point"; position: [number, number, number] }
  | { kind: "polyline"; vertices: [number, number, number][] }
  | { kind: "surface_patch"; triangleIds: number[]; topologyHash: string };

export interface AnnotationDraft {
  id: string;
  attachmentId: string | null;
  descriptionClaimId: string | null;
  instanceId: string | null;
  side: "left" | "right";
  assetId: string;
  assetRevision: string;
  assetRevisionHash: string;
  topologyHash: string;
  geometry: AnnotationGeometry;
  frameId: string;
  units: "m";
  poseId: string;
  precision: "representative" | "approximate_extent";
  method: "manual_mapping";
  transformChain: [];
  landmarkChecks: [];
  evidenceIds: string[];
  reviewState: "draft" | "stale";
  synthetic: boolean;
}

export interface AnnotationDraftExchange {
  schemaVersion: typeof ANNOTATION_EXCHANGE_VERSION;
  syntheticFixture: boolean;
  annotations: AnnotationDraft[];
}

export interface AnnotationAssetContext {
  assetId: string;
  assetRevision: string;
  assetRevisionHash: string;
  topologyHash: string;
  laterality: "left" | "right" | "midline" | "unpaired" | "bilateral" | "unknown";
  frameId: string;
  units: "m" | "mm" | "cm";
  poseId: string;
  triangleCount: number;
  targetEntityId: string | null;
}

export interface AnnotationAttachmentContext {
  id: string;
  ownerId: string;
  descriptionClaimId: string;
  evidenceIds: string[];
  allowedAssetIds?: string[];
}

export interface AnnotationValidationContext {
  assets: readonly AnnotationAssetContext[];
  attachments: readonly AnnotationAttachmentContext[];
  instanceIds?: readonly string[];
}

export class AnnotationValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = "AnnotationValidationError";
    this.code = code;
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const isId = (value: unknown): value is string =>
  typeof value === "string" && /^[A-Za-z0-9][A-Za-z0-9._:/-]*$/.test(value);

const isHash = (value: unknown): value is string =>
  typeof value === "string" && /^[a-f0-9]{64}$/.test(value);

const isPosition = (value: unknown): value is [number, number, number] =>
  Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item));

const EXACT_ANNOTATION_KEYS = new Set([
  "id", "attachmentId", "descriptionClaimId", "instanceId", "side", "assetId", "assetRevision",
  "assetRevisionHash", "topologyHash", "geometry", "frameId", "units", "poseId", "precision",
  "method", "transformChain", "landmarkChecks", "evidenceIds", "reviewState", "synthetic",
]);

function fail(code: string, message: string): never {
  throw new AnnotationValidationError(code, message);
}

function validateGeometry(value: unknown, context: AnnotationAssetContext, topologyChanged: boolean): AnnotationGeometry {
  if (!isRecord(value) || typeof value.kind !== "string") return fail("geometry_invalid", "annotation geometry must be a point, polyline, or surface_patch object.");
  if (value.kind === "point") {
    if (!isPosition(value.position)) return fail("point_invalid", "point.position must be three finite asset-frame coordinates in meters.");
    return { kind: "point", position: [...value.position] as [number, number, number] };
  }
  if (value.kind === "polyline") {
    if (!Array.isArray(value.vertices) || value.vertices.length < 2 || !value.vertices.every(isPosition)) {
      return fail("polyline_invalid", "polyline.vertices must contain at least two finite 3D coordinates.");
    }
    return { kind: "polyline", vertices: value.vertices.map((point) => [...point] as [number, number, number]) };
  }
  if (value.kind === "surface_patch") {
    if (!Array.isArray(value.triangleIds) || value.triangleIds.length < 1 || !value.triangleIds.every((id) => Number.isInteger(id) && id >= 0)) {
      return fail("surface_patch_invalid", "surface_patch.triangleIds must contain one or more non-negative integer triangle IDs.");
    }
    if (new Set(value.triangleIds).size !== value.triangleIds.length || !isHash(value.topologyHash)) {
      return fail("surface_patch_topology_invalid", "surface_patch triangle IDs must be unique and use a SHA-256 topology hash.");
    }
    if (!topologyChanged && (value.topologyHash !== context.topologyHash || value.triangleIds.some((id) => id >= context.triangleCount))) {
      return fail("surface_patch_triangle_out_of_range", "surface_patch references a triangle outside the current mesh topology.");
    }
    return { kind: "surface_patch", triangleIds: [...value.triangleIds] as number[], topologyHash: value.topologyHash };
  }
  return fail("geometry_kind_unsupported", `unsupported annotation geometry kind: ${value.kind}`);
}

export function validateAnnotationDraftExchange(
  value: unknown,
  context: AnnotationValidationContext,
  options: { allowSynthetic?: boolean; changedAssetPolicy?: "reject" | "mark_stale" } = {},
): AnnotationDraftExchange {
  if (!isRecord(value) || value.schemaVersion !== ANNOTATION_EXCHANGE_VERSION || typeof value.syntheticFixture !== "boolean" || !Array.isArray(value.annotations)) {
    return fail("exchange_schema_invalid", `JSON must use ${ANNOTATION_EXCHANGE_VERSION} with an annotations array.`);
  }
  if (value.syntheticFixture && options.allowSynthetic !== true) {
    return fail("synthetic_fixture_blocked", "Synthetic fixture imports are allowed only from the isolated fixture workflow.");
  }
  const assets = new Map(context.assets.map((asset) => [asset.assetId, asset]));
  const attachments = new Map(context.attachments.map((attachment) => [attachment.id, attachment]));
  const instanceIds = new Set(context.instanceIds ?? []);
  const ids = new Set<string>();
  const annotations: AnnotationDraft[] = value.annotations.map((row, index) => {
    if (!isRecord(row)) return fail("annotation_invalid", `annotations[${index}] must be an object.`);
    for (const key of Object.keys(row)) if (!EXACT_ANNOTATION_KEYS.has(key)) fail("annotation_unknown_field", `annotations[${index}] has unsupported field ${key}.`);
    const requiredStrings = ["id", "assetId", "assetRevision", "frameId", "poseId"] as const;
    for (const key of requiredStrings) if (!isId(row[key])) fail("annotation_id_invalid", `annotations[${index}].${key} is missing or invalid.`);
    if (ids.has(row.id as string)) fail("annotation_duplicate_id", `duplicate annotation ID ${row.id}.`);
    ids.add(row.id as string);
    if ((row.attachmentId !== null && !isId(row.attachmentId)) || (row.descriptionClaimId !== null && !isId(row.descriptionClaimId)) || (row.instanceId !== null && !isId(row.instanceId))) {
      fail("annotation_reference_invalid", `annotations[${index}] has an invalid nullable reference.`);
    }
    if (row.side !== "left" && row.side !== "right") fail("annotation_side_invalid", `annotations[${index}].side must be left or right.`);
    if (!isHash(row.assetRevisionHash) || !isHash(row.topologyHash)) fail("annotation_hash_invalid", `annotations[${index}] must carry asset and topology SHA-256 hashes.`);
    if (row.frameId !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR" || row.units !== "m") fail("annotation_frame_invalid", `annotations[${index}] is not in the fixed T07 Atlas right-handed meter frame.`);
    if (row.precision !== "representative" && row.precision !== "approximate_extent") fail("annotation_precision_invalid", `annotations[${index}].precision is not supported for a draft.`);
    if (row.method !== "manual_mapping" || !Array.isArray(row.transformChain) || row.transformChain.length !== 0 || !Array.isArray(row.landmarkChecks) || row.landmarkChecks.length !== 0) {
      fail("annotation_method_invalid", `annotations[${index}] must remain an untransformed manual draft without landmark review.`);
    }
    if (!Array.isArray(row.evidenceIds) || !row.evidenceIds.every(isId) || new Set(row.evidenceIds).size !== row.evidenceIds.length) {
      fail("annotation_evidence_invalid", `annotations[${index}].evidenceIds must be unique source IDs.`);
    }
    if (row.reviewState !== "draft" && row.reviewState !== "stale") fail("annotation_review_state_invalid", "Draft exchange cannot import a reviewed or needs_review annotation state.");
    if (row.synthetic !== value.syntheticFixture) fail("synthetic_flag_mismatch", "Every annotation's synthetic flag must match the exchange document mode.");
    if (value.syntheticFixture && row.attachmentId !== null && row.descriptionClaimId !== null) {
      fail("synthetic_claim_link_blocked", "Synthetic fixtures cannot claim association with real T05 attachment text.");
    }

    const asset = assets.get(row.assetId as string);
    if (!asset) fail("asset_unknown", `asset ${row.assetId} is not present in the current T07 manifest.`);
    const changedAsset = row.assetRevision !== asset.assetRevision || row.assetRevisionHash !== asset.assetRevisionHash;
    if (changedAsset && options.changedAssetPolicy !== "mark_stale") {
      fail("asset_revision_mismatch", `asset revision/hash mismatch for ${row.assetId}; import was rejected.`);
    }
    if (row.side !== asset.laterality && asset.laterality !== "bilateral" && asset.laterality !== "unknown") {
      fail("annotation_laterality_mismatch", `annotation side ${row.side} does not match ${asset.laterality} asset ${asset.assetId}.`);
    }
    if (row.frameId !== asset.frameId || row.units !== asset.units || row.poseId !== asset.poseId) {
      fail("annotation_asset_frame_mismatch", `annotation frame/units/pose do not match asset ${asset.assetId}.`);
    }
    const topologyChanged = row.topologyHash !== asset.topologyHash;
    const geometry = validateGeometry(row.geometry, asset, topologyChanged);
    if (geometry.kind === "surface_patch" && geometry.topologyHash !== row.topologyHash) {
      fail("surface_patch_hash_disagreement", `surface patch and annotation topology hashes disagree for ${row.id}.`);
    }

    if (value.syntheticFixture) {
      if (row.attachmentId !== null || row.descriptionClaimId !== null || row.instanceId === null) {
        fail("synthetic_context_invalid", "Synthetic fixture annotations require an isolated synthetic instance and no source-claim link.");
      }
    } else {
      if (row.instanceId !== null && !instanceIds.has(row.instanceId as string)) fail("instance_unknown", `instance ${row.instanceId} is not in the current catalog.`);
      if (row.attachmentId === null || row.descriptionClaimId === null) fail("source_attachment_required", `draft ${row.id} must link an existing T05 attachment and description claim.`);
      const attachment = attachments.get(row.attachmentId as string);
      if (!attachment || attachment.descriptionClaimId !== row.descriptionClaimId) fail("attachment_claim_mismatch", `draft ${row.id} does not resolve to the selected T05 attachment/claim pair.`);
      if (attachment.allowedAssetIds) {
        if (!attachment.allowedAssetIds.includes(asset.assetId)) fail("attachment_asset_target_mismatch", `draft ${row.id} asset is not a recorded muscle or target-bone review context for its attachment.`);
      } else if (!asset.targetEntityId || attachment.ownerId !== asset.targetEntityId) {
        fail("attachment_asset_target_mismatch", `draft ${row.id} attachment owner does not match a known mesh target.`);
      }
      if (row.evidenceIds.some((id) => !attachment.evidenceIds.includes(id))) fail("annotation_evidence_mismatch", `draft ${row.id} includes evidence not linked to its T05 attachment claim.`);
      if (row.instanceId === null) {
        // An instance-less local draft remains distinct from canonical SpatialAnnotation even after T12b added instances.
      } else if (!instanceIds.has(row.instanceId)) {
        fail("instance_unknown", `instance ${row.instanceId} is not in the current catalog.`);
      }
    }

    return {
      id: row.id as string,
      attachmentId: row.attachmentId as string | null,
      descriptionClaimId: row.descriptionClaimId as string | null,
      instanceId: row.instanceId as string | null,
      side: row.side,
      assetId: row.assetId as string,
      assetRevision: row.assetRevision as string,
      assetRevisionHash: row.assetRevisionHash as string,
      topologyHash: row.topologyHash as string,
      geometry,
      frameId: row.frameId as string,
      units: "m",
      poseId: row.poseId as string,
      precision: row.precision,
      method: "manual_mapping",
      transformChain: [],
      landmarkChecks: [],
      evidenceIds: [...row.evidenceIds] as string[],
      reviewState: changedAsset || topologyChanged ? "stale" : row.reviewState,
      synthetic: row.synthetic as boolean,
    };
  });
  return { schemaVersion: ANNOTATION_EXCHANGE_VERSION, syntheticFixture: value.syntheticFixture, annotations };
}

export function serializeAnnotationDraftExchange(annotations: readonly AnnotationDraft[], syntheticFixture = false): string {
  const exchange: AnnotationDraftExchange = { schemaVersion: ANNOTATION_EXCHANGE_VERSION, syntheticFixture, annotations: annotations.map((row) => ({ ...row })) };
  return JSON.stringify(exchange, null, 2);
}
