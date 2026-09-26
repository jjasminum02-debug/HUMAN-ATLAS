import type { AnnotationDraft, AnnotationGeometry, AnnotationAssetContext, AnnotationAttachmentContext } from "./annotationDrafts";
import type { ViewerMesh } from "./glb";
import type { ThreeViewer } from "./ThreeViewer";

export const SPATIAL_DRAFT_LAYER_VERSION = "HA-spatial-draft-layer-v1" as const;
export const SPATIAL_DRAFT_LAYER_STORAGE_KEY = "human-atlas:t13b:spatial-drafts:v1";
export const SPATIAL_DRAFT_TEST_STORAGE_KEY = "human-atlas:t13b:test-only:spatial-drafts";
export const T13_CONTEXT_VERSION = "T13-attachment-context-v2" as const;

export type SpatialDraftStatus = "pending" | "context_only" | "draft_surface" | "reviewed" | "stale";
export type DraftSide = "left" | "right";

export interface SpatialDraftRecord {
  id: string;
  status: SpatialDraftStatus;
  attachmentId: string | null;
  descriptionClaimId: string | null;
  sourceClaimHash: string | null;
  instanceId: string | null;
  side: DraftSide;
  assetId: string | null;
  assetRevision: string | null;
  assetRevisionHash: string | null;
  topologyHash: string | null;
  geometry: AnnotationGeometry | null;
  frameId: string | null;
  units: "m" | "mm" | "cm" | null;
  poseId: string | null;
  precision: "representative" | "approximate_extent" | "reviewed_extent" | null;
  method: "source_annotation" | "manual_mapping" | "model_derived" | null;
  evidenceIds: string[];
  reviewId: string | null;
  staleReason: string | null;
  migrationSource: string | null;
}

export interface SpatialDraftLayer {
  schemaVersion: typeof SPATIAL_DRAFT_LAYER_VERSION;
  syntheticFixture: boolean;
  sourceContextVersion: typeof T13_CONTEXT_VERSION;
  records: SpatialDraftRecord[];
}

export interface SpatialDraftContextRecord {
  attachmentId: string;
  descriptionClaimId: string;
  claimEvidenceIds: string[];
  ownerConceptId: string;
  instanceId: string;
  side: DraftSide;
  role: string;
  contextMeshAssetId: string | null;
  contextStatus: "whole_bone_search_context_only" | "held_no_matching_target_mesh";
  reason: string;
}

export interface SpatialDraftClaim extends Record<string, unknown> {
  id: string;
  subjectId: string;
  evidenceIds: string[];
}

export interface SpatialDraftInstance {
  id: string;
  conceptId: string;
  side: string;
}

export interface SpatialDraftReview {
  id: string;
  targetId: string;
  targetRevisionHash: string;
  reviewerKind: "human" | "ai";
  reviewerId: string;
  decision: "approved" | "rejected" | "needs_revision" | "held";
  reviewedAt: string;
}

export interface SpatialDraftContext {
  assets: readonly AnnotationAssetContext[];
  attachments: readonly AnnotationAttachmentContext[];
  t13Records: readonly SpatialDraftContextRecord[];
  claims: readonly SpatialDraftClaim[];
  instances: readonly SpatialDraftInstance[];
  reviews: readonly SpatialDraftReview[];
}

export class SpatialDraftValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = "SpatialDraftValidationError";
    this.code = code;
  }
}

const HASH_RE = /^[a-f0-9]{64}$/;
const ID_RE = /^[A-Za-z0-9][A-Za-z0-9._:/-]*$/;
const RECORD_KEYS = new Set([
  "id", "status", "attachmentId", "descriptionClaimId", "sourceClaimHash", "instanceId", "side",
  "assetId", "assetRevision", "assetRevisionHash", "topologyHash", "geometry", "frameId", "units",
  "poseId", "precision", "method", "evidenceIds", "reviewId", "staleReason", "migrationSource",
]);

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);
const isId = (value: unknown): value is string => typeof value === "string" && ID_RE.test(value);
const isHash = (value: unknown): value is string => typeof value === "string" && HASH_RE.test(value);
const isPosition = (value: unknown): value is [number, number, number] =>
  Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item));

function fail(code: string, message: string): never {
  throw new SpatialDraftValidationError(code, message);
}

function stableValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stableValue);
  if (!isRecord(value)) return value;
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
}

export function stableJson(value: unknown): string {
  return JSON.stringify(stableValue(value));
}

export async function sha256Text(text: string): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new Error("브라우저 Web Crypto API를 사용할 수 없어 SHA-256 검증을 진행하지 못했습니다.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((part) => part.toString(16).padStart(2, "0")).join("");
}

export function canonicalClaimHash(claim: SpatialDraftClaim): Promise<string> {
  return sha256Text(stableJson(claim));
}

export async function spatialDraftRevisionHash(record: SpatialDraftRecord): Promise<string> {
  const { status: _status, reviewId: _reviewId, staleReason: _staleReason, migrationSource: _migrationSource, ...content } = record;
  return sha256Text(stableJson(content));
}

function normalizeGeometry(value: unknown, asset: AnnotationAssetContext, topologyChanged: boolean): AnnotationGeometry {
  if (!isRecord(value) || typeof value.kind !== "string") return fail("geometry_invalid", "draft_surface requires point, polyline, or surface_patch geometry.");
  if (value.kind === "point") {
    if (!isPosition(value.position)) return fail("point_invalid", "point.position must contain three finite asset-frame coordinates.");
    return { kind: "point", position: [...value.position] as [number, number, number] };
  }
  if (value.kind === "polyline") {
    if (!Array.isArray(value.vertices) || value.vertices.length < 2 || !value.vertices.every(isPosition)) {
      return fail("polyline_invalid", "polyline.vertices must contain at least two finite coordinates.");
    }
    return { kind: "polyline", vertices: value.vertices.map((part) => [...part] as [number, number, number]) };
  }
  if (value.kind === "surface_patch") {
    if (!Array.isArray(value.triangleIds) || value.triangleIds.length < 1 ||
      !value.triangleIds.every((id) => Number.isInteger(id) && id >= 0) || new Set(value.triangleIds).size !== value.triangleIds.length ||
      !isHash(value.topologyHash)) {
      return fail("surface_patch_invalid", "surface_patch requires unique non-negative triangle IDs and a SHA-256 topology hash.");
    }
    if (value.topologyHash !== asset.topologyHash && !topologyChanged) {
      return fail("surface_patch_topology_mismatch", "surface_patch and asset topology hashes differ.");
    }
    if (!topologyChanged && value.triangleIds.some((id) => id >= asset.triangleCount)) {
      return fail("surface_patch_triangle_out_of_range", "surface_patch references a triangle outside the current mesh.");
    }
    return { kind: "surface_patch", triangleIds: [...value.triangleIds] as number[], topologyHash: value.topologyHash };
  }
  return fail("geometry_kind_unsupported", `Unsupported geometry kind: ${value.kind}.`);
}

function assertDocument(value: unknown): asserts value is SpatialDraftLayer {
  if (!isRecord(value) || value.schemaVersion !== SPATIAL_DRAFT_LAYER_VERSION ||
    value.sourceContextVersion !== T13_CONTEXT_VERSION || typeof value.syntheticFixture !== "boolean" || !Array.isArray(value.records)) {
    fail("layer_schema_invalid", `JSON must be ${SPATIAL_DRAFT_LAYER_VERSION} with a records array and the preserved T13 context version.`);
  }
  for (const [index, row] of value.records.entries()) {
    if (!isRecord(row)) fail("record_invalid", `records[${index}] must be an object.`);
    for (const key of Object.keys(row)) if (!RECORD_KEYS.has(key)) fail("record_unknown_field", `records[${index}] has unknown field ${key}.`);
    for (const key of RECORD_KEYS) if (!(key in row)) fail("record_field_missing", `records[${index}] is missing ${key}.`);
  }
}

export async function validateSpatialDraftLayer(
  value: unknown,
  context: SpatialDraftContext,
  options: { allowSyntheticFixture?: boolean } = {},
): Promise<SpatialDraftLayer> {
  assertDocument(value);
  if (value.syntheticFixture && options.allowSyntheticFixture !== true) {
    fail("synthetic_fixture_blocked", "Synthetic spatial fixtures are accepted only by the isolated test workflow.");
  }
  const assets = new Map(context.assets.map((row) => [row.assetId, row]));
  const attachments = new Map(context.attachments.map((row) => [row.id, row]));
  const t13Records = new Map(context.t13Records.map((row) => [row.attachmentId, row]));
  const claims = new Map(context.claims.map((row) => [row.id, row]));
  const instances = new Map(context.instances.map((row) => [row.id, row]));
  const reviews = new Map(context.reviews.map((row) => [row.id, row]));
  const ids = new Set<string>();

  const records: SpatialDraftRecord[] = [];
  for (const [index, original] of value.records.entries()) {
    if (!isRecord(original)) fail("record_invalid", `records[${index}] must be an object.`);
    const row = original as unknown as SpatialDraftRecord;
    if (!isId(row.id) || ids.has(row.id)) fail("record_id_invalid", `records[${index}] has an invalid or duplicate ID.`);
    ids.add(row.id);
    if (!["pending", "context_only", "draft_surface", "reviewed", "stale"].includes(row.status)) {
      fail("record_status_invalid", `Record ${row.id} has an unknown status.`);
    }
    if (row.side !== "left" && row.side !== "right") fail("record_side_invalid", `Record ${row.id} side must be left or right.`);
    if (!Array.isArray(row.evidenceIds) || row.evidenceIds.some((id) => !isId(id)) || new Set(row.evidenceIds).size !== row.evidenceIds.length) {
      fail("record_evidence_invalid", `Record ${row.id} evidence IDs must be unique strings.`);
    }

    const source = row.attachmentId === null ? undefined : t13Records.get(row.attachmentId);
    const attachment = row.attachmentId === null ? undefined : attachments.get(row.attachmentId);
    const claim = row.descriptionClaimId === null ? undefined : claims.get(row.descriptionClaimId);
    if (row.attachmentId !== null && (!source || !attachment)) fail("source_attachment_unknown", `Record ${row.id} does not resolve to a T13 source attachment.`);
    if (row.descriptionClaimId !== null && !claim) fail("source_claim_unknown", `Record ${row.id} has an unknown source claim.`);
    if (source && attachment && (source.descriptionClaimId !== attachment.descriptionClaimId || row.descriptionClaimId !== attachment.descriptionClaimId)) {
      fail("source_claim_attachment_mismatch", `Record ${row.id} claim does not belong to its attachment.`);
    }
    if (claim && attachment && claim.subjectId !== attachment.id) fail("source_claim_subject_mismatch", `Record ${row.id} claim subject is not its selected attachment.`);
    if (source && claim && !row.evidenceIds.every((evidenceId) => source.claimEvidenceIds.includes(evidenceId) && claim.evidenceIds.includes(evidenceId))) {
      fail("source_evidence_mismatch", `Record ${row.id} cites evidence outside the linked source claim.`);
    }
    if (row.sourceClaimHash !== null && !isHash(row.sourceClaimHash)) fail("source_claim_hash_invalid", `Record ${row.id} source claim hash is not SHA-256.`);
    if (row.sourceClaimHash !== null && claim && row.sourceClaimHash !== await canonicalClaimHash(claim)) {
      fail("source_claim_hash_mismatch", `Record ${row.id} source claim has changed since this draft was created.`);
    }

    const instance = row.instanceId === null ? undefined : instances.get(row.instanceId);
    if (row.instanceId !== null && (!instance || !source || source.instanceId !== row.instanceId)) {
      fail("instance_reference_invalid", `Record ${row.id} does not resolve to its T13 attachment instance.`);
    }
    if (instance && (instance.side !== row.side || !source || source.side !== row.side)) {
      fail("instance_side_mismatch", `Record ${row.id} side differs from its attachment instance.`);
    }
    if (row.status === "draft_surface" || row.status === "reviewed") {
      if (!attachment || !claim || !source || !isHash(row.sourceClaimHash) || !instance) {
        fail("draft_provenance_required", `Record ${row.id} requires current source, claim hash, and canonical instance references.`);
      }
      if (row.geometry === null) fail("draft_geometry_required", `Record ${row.id} surface status requires geometry.`);
    }
    if (row.status === "context_only" && row.geometry !== null) fail("context_geometry_blocked", `Context-only record ${row.id} cannot contain a surface.`);
    if (row.status === "pending" && row.geometry === null && row.assetId !== null) {
      // Pending references are allowed while source material is being re-linked; validate every reference that is present below.
    }

    let currentStatus: SpatialDraftStatus = row.status;
    let currentStaleReason = row.staleReason;
    let asset: AnnotationAssetContext | undefined;
    if (row.assetId !== null) {
      asset = assets.get(row.assetId);
      if (!asset) fail("mesh_reference_invalid", `Record ${row.id} refers to a mesh absent from the current T12/T13 asset set.`);
      if (row.assetRevision !== asset.assetRevision || row.assetRevisionHash !== asset.assetRevisionHash) {
        fail("asset_revision_hash_mismatch", `Record ${row.id} asset revision or GLB hash differs from the current manifest.`);
      }
      const sourceAssetAllowed = !!source && (
        source.contextMeshAssetId === asset.assetId || attachments.get(source.attachmentId)?.allowedAssetIds?.includes(asset.assetId) === true
      );
      if (source && !sourceAssetAllowed) fail("mesh_attachment_mismatch", `Record ${row.id} mesh is not an allowed context or owner mesh for this attachment.`);
      if (source && asset.laterality !== "bilateral" && asset.laterality !== "unknown" && asset.laterality !== row.side) {
        fail("mesh_side_mismatch", `Record ${row.id} side differs from mesh ${asset.assetId}.`);
      }
      if (row.frameId !== null && row.frameId !== asset.frameId) fail("frame_mismatch", `Record ${row.id} frame differs from its mesh.`);
      if (row.units !== null && row.units !== asset.units) fail("units_mismatch", `Record ${row.id} units differ from its mesh.`);
      if (row.poseId !== null && row.poseId !== asset.poseId) fail("pose_mismatch", `Record ${row.id} pose differs from its mesh.`);
      if (row.topologyHash !== null && !isHash(row.topologyHash)) fail("topology_hash_invalid", `Record ${row.id} topology hash is invalid.`);
      if (row.topologyHash !== null && row.topologyHash !== asset.topologyHash && row.status !== "stale") {
        currentStatus = "stale";
        currentStaleReason = "topology_hash_changed";
      }
    } else if (row.status === "draft_surface" || row.status === "reviewed" || row.geometry !== null) {
      fail("mesh_reference_required", `Record ${row.id} with geometry requires a current mesh reference.`);
    }

    let geometry = row.geometry;
    if (geometry !== null) {
      if (!asset) fail("geometry_asset_required", `Record ${row.id} geometry has no referenced mesh.`);
      const topologyChanged = row.topologyHash !== asset.topologyHash;
      geometry = normalizeGeometry(geometry, asset, topologyChanged);
      if (geometry.kind === "surface_patch" && geometry.topologyHash !== row.topologyHash) {
        fail("surface_patch_hash_disagreement", `Record ${row.id} surface patch and record topology hashes disagree.`);
      }
    }

    if (currentStatus === "reviewed") {
      if (!row.reviewId) fail("human_review_required", `Record ${row.id} cannot be reviewed without a linked T03 human review.`);
      const review = reviews.get(row.reviewId);
      const revisionHash = await spatialDraftRevisionHash({ ...row, status: "draft_surface", staleReason: null });
      if (!review || review.targetId !== row.id || review.targetRevisionHash !== revisionHash || review.reviewerKind !== "human" ||
        !review.reviewerId.trim() || review.decision !== "approved" || Number.isNaN(Date.parse(review.reviewedAt))) {
        fail("human_review_hash_mismatch", `Record ${row.id} lacks an approved human review for this exact content hash.`);
      }
    } else if (row.reviewId !== null) {
      fail("unexpected_review_link", `Record ${row.id} links a review but is not in reviewed state.`);
    }

    records.push({
      ...row,
      status: currentStatus,
      geometry,
      staleReason: currentStatus === "stale" ? currentStaleReason ?? "stale_reference" : null,
    });
  }
  return { schemaVersion: SPATIAL_DRAFT_LAYER_VERSION, syntheticFixture: value.syntheticFixture, sourceContextVersion: T13_CONTEXT_VERSION, records };
}

export function serializeSpatialDraftLayer(layer: SpatialDraftLayer): string {
  return JSON.stringify(layer, null, 2);
}

export async function parseSpatialDraftLayerText(
  text: string,
  context: SpatialDraftContext,
  options: { allowSyntheticFixture?: boolean } = {},
): Promise<SpatialDraftLayer> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    fail("json_invalid", "Spatial draft JSON 형식을 읽을 수 없습니다.");
  }
  return validateSpatialDraftLayer(parsed, context, options);
}

export async function saveSpatialDraftLayer(
  storage: Pick<Storage, "setItem">,
  layer: unknown,
  context: SpatialDraftContext,
): Promise<SpatialDraftLayer> {
  const checked = await validateSpatialDraftLayer(layer, context);
  storage.setItem(SPATIAL_DRAFT_LAYER_STORAGE_KEY, serializeSpatialDraftLayer(checked));
  return checked;
}

export async function readSpatialDraftLayer(
  storage: Pick<Storage, "getItem">,
  context: SpatialDraftContext,
): Promise<SpatialDraftLayer> {
  const text = storage.getItem(SPATIAL_DRAFT_LAYER_STORAGE_KEY);
  return text === null ? emptySpatialDraftLayer() : parseSpatialDraftLayerText(text, context);
}

export async function saveSyntheticTestSpatialDraftLayer(
  storage: Pick<Storage, "setItem">,
  layer: unknown,
  context: SpatialDraftContext,
): Promise<SpatialDraftLayer> {
  const checked = await validateSpatialDraftLayer(layer, context, { allowSyntheticFixture: true });
  if (!checked.syntheticFixture) fail("test_fixture_required", "The isolated preview store accepts synthetic fixtures only.");
  storage.setItem(SPATIAL_DRAFT_TEST_STORAGE_KEY, serializeSpatialDraftLayer(checked));
  return checked;
}

export async function readSyntheticTestSpatialDraftLayer(
  storage: Pick<Storage, "getItem">,
  context: SpatialDraftContext,
): Promise<SpatialDraftLayer> {
  const text = storage.getItem(SPATIAL_DRAFT_TEST_STORAGE_KEY);
  if (text === null) return { ...emptySpatialDraftLayer(), syntheticFixture: true };
  return parseSpatialDraftLayerText(text, context, { allowSyntheticFixture: true });
}

export function emptySpatialDraftLayer(): SpatialDraftLayer {
  return { schemaVersion: SPATIAL_DRAFT_LAYER_VERSION, syntheticFixture: false, sourceContextVersion: T13_CONTEXT_VERSION, records: [] };
}

export function makePendingLegacyRecord(draft: AnnotationDraft): SpatialDraftRecord {
  return {
    id: draft.id,
    status: "pending",
    attachmentId: draft.attachmentId,
    descriptionClaimId: draft.descriptionClaimId,
    sourceClaimHash: null,
    instanceId: null,
    side: draft.side,
    assetId: draft.assetId,
    assetRevision: draft.assetRevision,
    assetRevisionHash: draft.assetRevisionHash,
    topologyHash: draft.topologyHash,
    geometry: structuredClone(draft.geometry),
    frameId: draft.frameId,
    units: draft.units,
    poseId: draft.poseId,
    precision: draft.precision,
    method: draft.method,
    evidenceIds: [...draft.evidenceIds],
    reviewId: null,
    staleReason: null,
    migrationSource: "HA-annotation-draft-exchange-v1_without_source_claim_hash",
  };
}

export async function makeDraftSurfaceRecord(
  draft: AnnotationDraft,
  context: SpatialDraftContext,
): Promise<SpatialDraftRecord> {
  if (!draft.attachmentId || !draft.descriptionClaimId) fail("draft_source_required", "New spatial drafts require an attachment and description claim.");
  const source = context.t13Records.find((row) => row.attachmentId === draft.attachmentId);
  const claim = context.claims.find((row) => row.id === draft.descriptionClaimId);
  const attachment = context.attachments.find((row) => row.id === draft.attachmentId);
  const asset = context.assets.find((row) => row.assetId === draft.assetId);
  if (!source || !claim || !attachment || !asset) fail("draft_source_context_missing", "New draft source, claim, or mesh could not be verified against the current manifests.");
  if (source.descriptionClaimId !== draft.descriptionClaimId || claim.subjectId !== attachment.id) fail("draft_claim_mismatch", "Selected claim is not the source attachment claim.");
  if (!source.claimEvidenceIds.every((id) => draft.evidenceIds.includes(id))) fail("draft_evidence_mismatch", "Draft does not retain the T13 source claim evidence.");
  const instance = context.instances.find((row) => row.id === source.instanceId);
  if (!instance || instance.side !== source.side || draft.side !== source.side) fail("draft_instance_mismatch", "Source attachment instance or laterality is not current.");
  const bound: AnnotationDraft = { ...draft, instanceId: source.instanceId };
  const sourceClaimHash = await canonicalClaimHash(claim);
  const record: SpatialDraftRecord = {
    id: bound.id,
    status: "draft_surface",
    attachmentId: bound.attachmentId,
    descriptionClaimId: bound.descriptionClaimId,
    sourceClaimHash,
    instanceId: source.instanceId,
    side: bound.side,
    assetId: bound.assetId,
    assetRevision: bound.assetRevision,
    assetRevisionHash: bound.assetRevisionHash,
    topologyHash: bound.topologyHash,
    geometry: structuredClone(bound.geometry),
    frameId: bound.frameId,
    units: bound.units,
    poseId: bound.poseId,
    precision: bound.precision,
    method: bound.method,
    evidenceIds: [...bound.evidenceIds],
    reviewId: null,
    staleReason: null,
    migrationSource: null,
  };
  const checked = await validateSpatialDraftLayer({
    schemaVersion: SPATIAL_DRAFT_LAYER_VERSION,
    syntheticFixture: false,
    sourceContextVersion: T13_CONTEXT_VERSION,
    records: [record],
  }, context);
  return checked.records[0];
}

export async function contextStatusRecords(
  context: SpatialDraftContext,
): Promise<SpatialDraftRecord[]> {
  const records: SpatialDraftRecord[] = [];
  for (const source of context.t13Records) {
    const claim = context.claims.find((row) => row.id === source.descriptionClaimId);
    const attachment = context.attachments.find((row) => row.id === source.attachmentId);
    const asset = source.contextMeshAssetId ? context.assets.find((row) => row.assetId === source.contextMeshAssetId) : undefined;
    const instance = context.instances.find((row) => row.id === source.instanceId);
    const status: SpatialDraftStatus = asset ? "context_only" : "pending";
    if (!claim || !attachment || !instance) fail("context_manifest_reference_invalid", `T13 context row ${source.attachmentId} no longer resolves to catalog source/instance records.`);
    records.push({
      id: `CTX-${source.attachmentId}`,
      status,
      attachmentId: source.attachmentId,
      descriptionClaimId: source.descriptionClaimId,
      sourceClaimHash: await canonicalClaimHash(claim),
      instanceId: source.instanceId,
      side: source.side,
      assetId: asset?.assetId ?? null,
      assetRevision: asset?.assetRevision ?? null,
      assetRevisionHash: asset?.assetRevisionHash ?? null,
      topologyHash: asset?.topologyHash ?? null,
      geometry: null,
      frameId: asset?.frameId ?? null,
      units: asset?.units ?? null,
      poseId: asset?.poseId ?? null,
      precision: null,
      method: null,
      evidenceIds: [...source.claimEvidenceIds],
      reviewId: null,
      staleReason: null,
      migrationSource: T13_CONTEXT_VERSION,
    });
  }
  return records;
}

export function mergeSpatialDraftLayers(current: SpatialDraftLayer, incoming: SpatialDraftLayer): SpatialDraftLayer {
  if (current.syntheticFixture !== incoming.syntheticFixture) fail("fixture_mode_mismatch", "Production and synthetic test records cannot be merged into one layer.");
  const byId = new Map(current.records.map((row) => [row.id, row]));
  for (const row of incoming.records) {
    const existing = byId.get(row.id);
    if (existing && stableJson(existing) !== stableJson(row)) fail("record_id_conflict", `Import ID ${row.id} conflicts with an existing record; current data was left unchanged.`);
    byId.set(row.id, row);
  }
  return { ...current, records: [...byId.values()] };
}

export function drawReadOnlySpatialOverlay(
  canvas: HTMLCanvasElement,
  viewer: ThreeViewer,
  records: readonly SpatialDraftRecord[],
  t13Records: readonly SpatialDraftContextRecord[],
  visibleOwnerIds: ReadonlySet<string>,
): number {
  const rect = canvas.getBoundingClientRect();
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, Math.round(rect.width * ratio));
  const height = Math.max(1, Math.round(rect.height * ratio));
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;
  const context = canvas.getContext("2d");
  if (!context) return 0;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, rect.width, rect.height);
  let drawn = 0;
  const drawMarker = (x: number, y: number, color: string, label: string) => {
    context.beginPath();
    context.arc(x, y, 6, 0, Math.PI * 2);
    context.fillStyle = "#ffffff";
    context.fill();
    context.lineWidth = 3;
    context.strokeStyle = color;
    context.stroke();
    context.font = "700 10px ui-sans-serif, sans-serif";
    context.lineWidth = 3;
    context.strokeStyle = "rgba(255,255,255,.96)";
    context.strokeText(label, x + 8, y - 8);
    context.fillStyle = color;
    context.fillText(label, x + 8, y - 8);
  };

  for (const record of records) {
    if ((record.status !== "draft_surface" && record.status !== "reviewed") || !record.geometry || !record.attachmentId || !record.assetId) continue;
    const source = t13Records.find((row) => row.attachmentId === record.attachmentId);
    if (!source || !visibleOwnerIds.has(source.ownerConceptId) || viewer.getVisibility(record.assetId) === "hidden") continue;
    const mesh: ViewerMesh | undefined = viewer.getMesh(record.assetId);
    if (!mesh) continue;
    const color = source.role === "origin" ? "#07876d" : source.role === "insertion" ? "#c88412" : "#496f9b";
    const stateLabel = record.status === "reviewed" ? "사람 검토" : "미검토";
    const label = `${source.role === "origin" ? "기시" : source.role === "insertion" ? "정지" : "부착"} · ${stateLabel}`;
    context.save();
    context.globalAlpha = viewer.getVisibility(record.assetId) === "transparent" ? 0.65 : 1;
    context.setLineDash(record.status === "draft_surface" ? [6, 4] : []);
    context.lineWidth = 3;
    context.strokeStyle = color;
    context.fillStyle = `${color}35`;
    if (record.geometry.kind === "point") {
      const point = viewer.projectPoint(record.geometry.position);
      if (point.visible) { drawMarker(point.x, point.y, color, label); drawn += 1; }
    } else if (record.geometry.kind === "polyline") {
      const points = record.geometry.vertices.map((point) => viewer.projectPoint(point));
      if (points.length >= 2 && points.every((point) => point.visible)) {
        context.beginPath();
        points.forEach((point, index) => index === 0 ? context.moveTo(point.x, point.y) : context.lineTo(point.x, point.y));
        context.stroke();
        points.forEach((point, index) => drawMarker(point.x, point.y, color, index === 0 ? label : ""));
        drawn += 1;
      }
    } else {
      for (const triangleId of record.geometry.triangleIds) {
        const base = triangleId * 3;
        if (base + 2 >= mesh.indices.length) continue;
        const vertices = [mesh.indices[base], mesh.indices[base + 1], mesh.indices[base + 2]].map((vertexId) => {
          const offset = vertexId * 3;
          return viewer.projectPoint([mesh.positions[offset], mesh.positions[offset + 1], mesh.positions[offset + 2]]);
        });
        if (vertices.some((point) => !point.visible)) continue;
        context.beginPath();
        context.moveTo(vertices[0].x, vertices[0].y);
        context.lineTo(vertices[1].x, vertices[1].y);
        context.lineTo(vertices[2].x, vertices[2].y);
        context.closePath();
        context.fill();
        context.stroke();
      }
      drawn += 1;
    }
    context.restore();
  }
  return drawn;
}
