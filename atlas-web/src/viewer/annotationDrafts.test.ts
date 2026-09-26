import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import {
  AnnotationValidationError,
  serializeAnnotationDraftExchange,
  validateAnnotationDraftExchange,
  type AnnotationValidationContext,
} from "./annotationDrafts.ts";

const fixtureDir = resolve(process.cwd(), "../work/evidence/T09/fixtures");
function fixture<T>(name: string): T {
  return JSON.parse(readFileSync(resolve(fixtureDir, name), "utf8")) as T;
}
const context = fixture<AnnotationValidationContext>("context.json");
const positive = fixture<unknown>("positive-exchange.json");
const allowSynthetic = { allowSynthetic: true } as const;

function expectCode(payload: unknown, code: string, ctx = context) {
  assert.throws(
    () => validateAnnotationDraftExchange(payload, ctx, allowSynthetic),
    (error: unknown) => error instanceof AnnotationValidationError && error.code === code,
  );
}

test("positive synthetic fixture accepts point, polyline, and surface patch", () => {
  const output = validateAnnotationDraftExchange(positive, context, allowSynthetic);
  assert.deepEqual(output.annotations.map((annotation) => annotation.geometry.kind), ["point", "polyline", "surface_patch"]);
  assert.ok(output.annotations.every((annotation) => annotation.reviewState === "draft" && annotation.synthetic));
});

test("side mismatch is rejected", () => {
  expectCode(fixture("negative-side-mismatch.json"), "annotation_laterality_mismatch");
});

test("asset revision mismatch is rejected", () => {
  expectCode(fixture("negative-asset-revision-mismatch.json"), "asset_revision_mismatch");
});

test("review promotion and duplicate stable IDs are rejected", () => {
  expectCode(fixture("negative-reviewed-state.json"), "annotation_review_state_invalid");
  expectCode(fixture("negative-duplicate-id.json"), "annotation_duplicate_id");
});

test("topology hash change preserves a stale draft without rendering it as current", () => {
  const changedContext = fixture<AnnotationValidationContext>("topology-changed-context.json");
  const output = validateAnnotationDraftExchange(positive, changedContext, allowSynthetic);
  assert.ok(output.annotations.every((annotation) => annotation.reviewState === "stale"));
});

test("current topology rejects triangle IDs outside the indexed mesh", () => {
  const payload = structuredClone(positive) as { annotations: Array<Record<string, unknown>> };
  const patch = payload.annotations[2] as Record<string, unknown>;
  patch.geometry = { kind: "surface_patch", triangleIds: [8], topologyHash: "b".repeat(64) };
  expectCode(payload, "surface_patch_triangle_out_of_range");
});

test("ordinary import rejects fixture mode unless the explicit fixture path is enabled", () => {
  assert.throws(
    () => validateAnnotationDraftExchange(positive, context),
    (error: unknown) => error instanceof AnnotationValidationError && error.code === "synthetic_fixture_blocked",
  );
});

test("JSON export/import round trip keeps coordinates and draft-only state", () => {
  const output = validateAnnotationDraftExchange(positive, context, allowSynthetic);
  const text = serializeAnnotationDraftExchange(output.annotations, true);
  const roundTripped = validateAnnotationDraftExchange(JSON.parse(text), context, allowSynthetic);
  assert.deepEqual(roundTripped, output);
});

test("source-linked manual drafts may remain instance-less until a real instance exists", () => {
  const sourceContext: AnnotationValidationContext = {
    ...context,
    assets: context.assets.map((asset) => ({ ...asset, targetEntityId: "SYN-MUSCLE-01" })),
    attachments: [{ id: "SYN-ATTACHMENT-01", descriptionClaimId: "SYN-CLAIM-01", evidenceIds: ["SYN-EVIDENCE-01"], ownerId: "SYN-MUSCLE-01" }],
    instanceIds: [],
  };
  const payload = structuredClone(positive) as { syntheticFixture: boolean; annotations: Array<Record<string, unknown>> };
  payload.syntheticFixture = false;
  payload.annotations = [payload.annotations[0]];
  Object.assign(payload.annotations[0], {
    attachmentId: "SYN-ATTACHMENT-01",
    descriptionClaimId: "SYN-CLAIM-01",
    instanceId: null,
    evidenceIds: ["SYN-EVIDENCE-01"],
    synthetic: false,
  });
  const output = validateAnnotationDraftExchange(payload, sourceContext);
  assert.equal(output.annotations[0].instanceId, null);
  assert.equal(output.annotations[0].reviewState, "draft");
});

test("asset revision hash mismatch is rejected", () => {
  const payload = fixture<unknown>("negative-asset-hash-mismatch.json");
  expectCode(payload, "asset_revision_mismatch");
});

test("source attachment owner must match a known mesh target", () => {
  const sourceContext: AnnotationValidationContext = {
    ...context,
    assets: context.assets.map((asset) => ({ ...asset, targetEntityId: "SYN-MUSCLE-02" })),
    attachments: [{ id: "SYN-ATTACHMENT-01", descriptionClaimId: "SYN-CLAIM-01", evidenceIds: ["SYN-EVIDENCE-01"], ownerId: "SYN-MUSCLE-01" }],
  };
  const payload = structuredClone(fixture<Record<string, unknown>>("positive-exchange.json"));
  payload.syntheticFixture = false;
  const rows = payload.annotations as Array<Record<string, unknown>>;
  rows.splice(1);
  Object.assign(rows[0], {
    attachmentId: "SYN-ATTACHMENT-01",
    descriptionClaimId: "SYN-CLAIM-01",
    instanceId: null,
    evidenceIds: ["SYN-EVIDENCE-01"],
    synthetic: false,
  });
  expectCode(payload, "attachment_asset_target_mismatch", sourceContext);
});

test("T13 permits only a provenance-linked target-bone review draft", () => {
  const sourceContext: AnnotationValidationContext = {
    ...context,
    assets: context.assets.map((asset) => ({ ...asset, targetEntityId: "SYN-BONE-01" })),
    attachments: [{ id: "SYN-ATTACHMENT-01", descriptionClaimId: "SYN-CLAIM-01", evidenceIds: ["SYN-EVIDENCE-01"],
      ownerId: "SYN-MUSCLE-01", allowedAssetIds: [context.assets[0].assetId] }],
  };
  const payload = structuredClone(fixture<Record<string, unknown>>("positive-exchange.json"));
  payload.syntheticFixture = false;
  const rows = payload.annotations as Array<Record<string, unknown>>;
  rows.splice(1);
  Object.assign(rows[0], { attachmentId: "SYN-ATTACHMENT-01", descriptionClaimId: "SYN-CLAIM-01",
    instanceId: null, evidenceIds: ["SYN-EVIDENCE-01"], synthetic: false });
  assert.equal(validateAnnotationDraftExchange(payload, sourceContext).annotations[0].reviewState, "draft");
  sourceContext.attachments[0].allowedAssetIds = ["SYN-UNRELATED-BONE"];
  expectCode(payload, "attachment_asset_target_mismatch", sourceContext);
});
