import assert from "node:assert/strict";
import test from "node:test";
import { projectAiEvidenceField, type AiEvidenceField } from "./aiEvidence.ts";

function item(state: AiEvidenceField["evidenceState"], values: string[]): AiEvidenceField {
  const sources = values.map((_value, index) => ({
    id: `source-${index}`,
    underlyingWorkId: `work-${index}`,
    title: `Synthetic source ${index}`,
    url: `https://example.invalid/source-${index}`,
    editionStatus: "verified" as const,
    edition: "Synthetic fixture",
    accessedOn: "2026-09-27",
    accessMethod: "publisher_full_text" as const,
    textAccess: "full_text_opened" as const,
    sourceHash: "a".repeat(64),
    fixtureOnly: true,
  }));
  const claims = values.map((value, index) => ({
    id: `claim-${index}`,
    value,
    valueHash: `hash-${value}`,
    evidenceIds: [`evidence-${index}`],
    attribution: "ai_structured" as const,
  }));
  const evidence = values.map((_value, index) => ({
    id: `evidence-${index}`,
    sourceId: `source-${index}`,
    locator: `Synthetic locator ${index}`,
    accessedOn: "2026-09-27",
    accessMethod: "publisher_full_text" as const,
    textAccess: "full_text_opened" as const,
    supportsClaimIds: [`claim-${index}`],
    evidenceHash: "b".repeat(64),
  }));
  return {
    id: "fixture-field",
    subjectId: "HA-M-000001",
    field: "origin",
    evidenceState: state,
    claims,
    sources,
    evidence,
    geometryState: "absent",
    motionState: "absent",
  };
}

test("cross-check display allows a basic quiz without implying human approval", () => {
  const projection = projectAiEvidenceField(item("cross_checked", ["Synthetic statement"]));
  assert.equal(projection.text, "Synthetic statement");
  assert.equal(projection.quizEligible, true);
  assert.match(projection.note ?? "", /사람의 해부학 검토.*별도/);
  assert.equal("evidenceState" in projection, false);
  assert.equal("humanReview" in projection, false);
  assert.equal("reviewState" in projection, false);
  assert.doesNotMatch(JSON.stringify(projection), /cross_checked|reviewed|reviewState|geometryState|motionState/);
});

test("single-source display carries a caveat and is not quiz eligible", () => {
  const projection = projectAiEvidenceField(item("single_source", ["Historical source summary"]));
  assert.equal(projection.text, "Historical source summary");
  assert.match(projection.note ?? "", /한 자료/);
  assert.equal(projection.quizEligible, false);
});

test("conflicted fields render alternatives without a single answer", () => {
  const projection = projectAiEvidenceField(item("conflicted", ["Synthetic value A", "Synthetic value B"]));
  assert.equal(projection.text, null);
  assert.equal(projection.alternatives.length, 2);
  assert.match(projection.note ?? "", /차이/);
  assert.equal(projection.quizEligible, false);
});

test("unavailable and unresearched fields have distinct learner messages", () => {
  const unavailable = projectAiEvidenceField(item("unavailable", []));
  const unresearched = projectAiEvidenceField(item("unresearched", []));
  assert.notEqual(unavailable.note, unresearched.note);
  assert.equal(unavailable.quizEligible, false);
  assert.equal(unresearched.quizEligible, false);
});

test("geometry and motion values do not alter evidence projection", () => {
  const row = item("single_source", ["Synthetic statement"]);
  const before = projectAiEvidenceField(row);
  row.geometryState = "context";
  row.motionState = "educational_ready";
  assert.deepEqual(projectAiEvidenceField(row), before);
});
