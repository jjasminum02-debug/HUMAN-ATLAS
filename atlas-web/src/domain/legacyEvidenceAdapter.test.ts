import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { projectLegacySummary, type LegacyLearningSummary } from "./legacyEvidenceAdapter.ts";

const legacyRows = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-structure-summaries.json", import.meta.url), "utf8")) as LegacyLearningSummary[];

test("legacy summary fallback preserves exact learner text without changing its approval or source contract", () => {
  const original = legacyRows.find((row) => row.conceptId === "HA-M-000001" && row.role === "origin");
  assert.ok(original);
  const before = JSON.stringify(original);
  const projection = projectLegacySummary(original);
  assert.ok(projection);
  assert.equal(projection.text, original.summary);
  assert.equal(projection.quizEligible, false);
  assert.equal(projection.note, null);
  assert.equal(JSON.stringify(original), before);
  assert.doesNotMatch(JSON.stringify(projection), /sourceClaimHash|sourceClaimIds|humanReviewed|reviewState|cross_checked/);
});

test("empty legacy summaries remain unavailable", () => {
  assert.equal(projectLegacySummary(undefined), null);
  assert.equal(projectLegacySummary({ conceptId: "HA-M-000001", role: "origin", summary: " " }), null);
});
