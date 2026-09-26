import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import type { AnnotationDraft } from "./annotationDrafts.ts";
import {
  SPATIAL_DRAFT_LAYER_VERSION,
  SpatialDraftValidationError,
  canonicalClaimHash,
  contextStatusRecords,
  makeDraftSurfaceRecord,
  makePendingLegacyRecord,
  parseSpatialDraftLayerText,
  readSyntheticTestSpatialDraftLayer,
  saveSpatialDraftLayer,
  saveSyntheticTestSpatialDraftLayer,
  serializeSpatialDraftLayer,
  validateSpatialDraftLayer,
  type SpatialDraftContext,
  type SpatialDraftLayer,
  type SpatialDraftRecord,
} from "./spatialDraftLayer.ts";

const fixtureDir = resolve(process.cwd(), "../work/evidence/T13b/fixtures");
function fixture<T>(name: string): T {
  return JSON.parse(readFileSync(resolve(fixtureDir, name), "utf8")) as T;
}
const context = fixture<SpatialDraftContext>("context.json");
const positiveTemplate = fixture<SpatialDraftLayer>("positive-spatial-layer.json");
const allowFixture = { allowSyntheticFixture: true } as const;

async function positive(): Promise<SpatialDraftLayer> {
  const claim = context.claims[0];
  const sourceClaimHash = await canonicalClaimHash(claim);
  return structuredClone({
    ...positiveTemplate,
    records: positiveTemplate.records.map((row) => ({ ...row, sourceClaimHash })),
  });
}

async function expectCode(
  payload: unknown,
  code: string,
  ctx = context,
  opts: { allowSyntheticFixture?: boolean } = allowFixture,
) {
  await assert.rejects(
    validateSpatialDraftLayer(payload, ctx, opts),
    (error: unknown) => error instanceof SpatialDraftValidationError && error.code === code,
  );
}

test("positive synthetic layer validates a source-linked surface while remaining fixture-only", async () => {
  const output = await validateSpatialDraftLayer(await positive(), context, allowFixture);
  assert.equal(output.schemaVersion, SPATIAL_DRAFT_LAYER_VERSION);
  assert.equal(output.records[0].status, "draft_surface");
  assert.equal(output.records[0].sourceClaimHash, await canonicalClaimHash(context.claims[0]));
  await expectCode(await positive(), "synthetic_fixture_blocked", context, {});
});

test("context-only and pending states never contain geometry", async () => {
  const contextOnly = await contextStatusRecords(context);
  assert.equal(contextOnly.length, 1);
  assert.equal(contextOnly[0].status, "context_only");
  assert.equal(contextOnly[0].geometry, null);
  const pending = { ...contextOnly[0], id: "CTX-PENDING", status: "pending" as const, assetId: null,
    assetRevision: null, assetRevisionHash: null, topologyHash: null, frameId: null, units: null, poseId: null };
  const result = await validateSpatialDraftLayer({
    schemaVersion: SPATIAL_DRAFT_LAYER_VERSION,
    syntheticFixture: false,
    sourceContextVersion: "T13-attachment-context-v2",
    records: [pending],
  }, context);
  assert.equal(result.records[0].status, "pending");
  const invalid = structuredClone(await positive());
  invalid.records[0] = { ...invalid.records[0], status: "context_only" };
  await expectCode(invalid, "context_geometry_blocked");
});

test("source, instance, mesh, laterality, claim, revision, frame, unit, and pose mismatches are rejected", async () => {
  const base = await positive();
  const invalids: Array<[string, (row: SpatialDraftRecord) => void, string]> = [
    ["orphan source", (row) => { row.attachmentId = "UNKNOWN-ATTACHMENT"; }, "source_attachment_unknown"],
    ["orphan claim", (row) => { row.descriptionClaimId = "UNKNOWN-CLAIM"; }, "source_claim_unknown"],
    ["orphan instance", (row) => { row.instanceId = "UNKNOWN-INSTANCE"; }, "instance_reference_invalid"],
    ["wrong side", (row) => { row.side = "left"; }, "instance_side_mismatch"],
    ["changed claim hash", (row) => { row.sourceClaimHash = "c".repeat(64); }, "source_claim_hash_mismatch"],
    ["unknown mesh", (row) => { row.assetId = "UNKNOWN-MESH"; }, "mesh_reference_invalid"],
    ["changed asset hash", (row) => { row.assetRevisionHash = "c".repeat(64); }, "asset_revision_hash_mismatch"],
    ["wrong frame", (row) => { row.frameId = "OTHER-FRAME"; }, "frame_mismatch"],
    ["wrong units", (row) => { row.units = "mm"; }, "units_mismatch"],
    ["wrong pose", (row) => { row.poseId = "OTHER-POSE"; }, "pose_mismatch"],
  ];
  for (const [label, change, code] of invalids) {
    const payload = structuredClone(base);
    change(payload.records[0]);
    await expectCode(payload, code);
    assert.ok(label.length > 0);
  }
});

test("a changed topology retains the record as stale and does not mark it reviewed", async () => {
  const changedContext: SpatialDraftContext = {
    ...context,
    assets: context.assets.map((asset) => ({ ...asset, topologyHash: "c".repeat(64) })),
  };
  const output = await validateSpatialDraftLayer(await positive(), changedContext, allowFixture);
  assert.equal(output.records[0].status, "stale");
  assert.equal(output.records[0].staleReason, "topology_hash_changed");
  assert.equal(output.records[0].reviewId, null);
});

test("reviewed state requires a current approved human review for the exact content hash", async () => {
  const invalid = await positive();
  invalid.records[0] = { ...invalid.records[0], status: "reviewed" };
  await expectCode(invalid, "human_review_required");
  const wrongProof = structuredClone(invalid);
  wrongProof.records[0] = { ...wrongProof.records[0], reviewId: "FAKE-REVIEW" };
  await expectCode(wrongProof, "human_review_hash_mismatch");
});

test("new review drafts bind current source claim hash and canonical instance", async () => {
  const draft: AnnotationDraft = {
    id: "SYN-ANNOTATION-NEW",
    attachmentId: "SYN-ATTACHMENT-1",
    descriptionClaimId: "SYN-CLAIM-1",
    instanceId: null,
    side: "right",
    assetId: "SYN-MESH-R1",
    assetRevision: "SYN-REV-1",
    assetRevisionHash: "a".repeat(64),
    topologyHash: "b".repeat(64),
    geometry: { kind: "point", position: [0, 0, 0] },
    frameId: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
    units: "m",
    poseId: "SYN-POSE-1",
    precision: "representative",
    method: "manual_mapping",
    transformChain: [],
    landmarkChecks: [],
    evidenceIds: ["SYN-EVIDENCE-1"],
    reviewState: "draft",
    synthetic: false,
  };
  const record = await makeDraftSurfaceRecord(draft, context);
  assert.equal(record.status, "draft_surface");
  assert.equal(record.instanceId, "SYN-INSTANCE-R-1");
  assert.equal(record.sourceClaimHash, await canonicalClaimHash(context.claims[0]));
});

test("serialization reloads and a failed import leaves the prior stored document unchanged", async () => {
  const valid = await positive();
  const storage = new Map<string, string>();
  const adapter = {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => { storage.set(key, value); },
  };
  const checked = await validateSpatialDraftLayer(valid, context, allowFixture);
  const serialized = serializeSpatialDraftLayer(checked);
  await assert.rejects(parseSpatialDraftLayerText(serialized, context), (error: unknown) =>
    error instanceof SpatialDraftValidationError && error.code === "synthetic_fixture_blocked");
  storage.set("human-atlas:t13b:spatial-drafts:v1", "preexisting-production-value");
  const before = storage.get("human-atlas:t13b:spatial-drafts:v1");
  await assert.rejects(saveSpatialDraftLayer(adapter, { ...valid, syntheticFixture: true }, context));
  assert.equal(storage.get("human-atlas:t13b:spatial-drafts:v1"), before);
  await saveSyntheticTestSpatialDraftLayer(adapter, checked, context);
  const reloaded = await readSyntheticTestSpatialDraftLayer(adapter, context);
  assert.equal(reloaded.records[0].id, "SYN-ANNOTATION-1");
  assert.equal(reloaded.syntheticFixture, true);
  assert.equal(storage.get("human-atlas:t13b:spatial-drafts:v1"), before);
});

test("legacy drafts are copied to pending without adding a source claim hash or altering the source record", () => {
  const legacy: AnnotationDraft = {
    id: "HA-ANN-DRAFT-OLD",
    attachmentId: "SYN-ATTACHMENT-1",
    descriptionClaimId: "SYN-CLAIM-1",
    instanceId: null,
    side: "right",
    assetId: "SYN-MESH-R1",
    assetRevision: "SYN-REV-1",
    assetRevisionHash: "a".repeat(64),
    topologyHash: "b".repeat(64),
    geometry: { kind: "point", position: [0.1, 0.2, 0.3] },
    frameId: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
    units: "m",
    poseId: "SYN-POSE-1",
    precision: "representative",
    method: "manual_mapping",
    transformChain: [],
    landmarkChecks: [],
    evidenceIds: ["SYN-EVIDENCE-1"],
    reviewState: "draft",
    synthetic: false,
  };
  const snapshot = structuredClone(legacy);
  const migrated = makePendingLegacyRecord(legacy);
  assert.deepEqual(legacy, snapshot);
  assert.equal(migrated.status, "pending");
  assert.equal(migrated.sourceClaimHash, null);
  assert.equal(migrated.instanceId, null);
  assert.deepEqual(migrated.geometry, legacy.geometry);
});
