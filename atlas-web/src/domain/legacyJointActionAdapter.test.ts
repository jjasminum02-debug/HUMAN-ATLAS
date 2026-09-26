import assert from "node:assert/strict";
import test from "node:test";
import { previewLegacyJointActionMigration, type LegacyJointAction } from "./legacyJointActionAdapter.ts";

test("legacy JointAction migration is a non-persistable preview and preserves source review/hash/evidence", () => {
  const source: LegacyJointAction = {
    id: "FX-LEGACY-ACTION", muscleOrPartIds: ["FX-MUSCLE"], jointIds: ["FX-JOINT"], action: "fixture source wording",
    postureConditions: ["fixture posture"], contractionRole: "isometric", taskContext: "fixture task", roleInTask: "fixture role",
    evidenceIds: ["FX-LEGACY-EVIDENCE"], reviewState: "needs_review",
  };
  const snapshot = structuredClone(source);
  const first = previewLegacyJointActionMigration(source);
  const second = previewLegacyJointActionMigration(source);
  assert.deepEqual(first, second);
  assert.deepEqual(source, snapshot);
  assert.equal(first.persistable, false);
  assert.equal(first.source.originalReviewState, "needs_review");
  assert.deepEqual(first.source.originalEvidenceIds, ["FX-LEGACY-EVIDENCE"]);
  assert.match(first.source.snapshotSha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(first.candidate.targetJointIds, ["FX-JOINT"]);
  assert.equal(first.candidate.requiresSourceAndContextReview, true);
  assert.equal("reviewState" in first.candidate, false);
  assert.equal("humanReviewed" in first.candidate, false);
});
// Existing production JointAction collection is empty; this adapter must not invent rows.
