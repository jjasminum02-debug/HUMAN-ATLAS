import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import type { AiEvidenceField } from "../domain/aiEvidence.ts";
import { projectLearnerActionCard, projectLearnerMotionActionOptions, type MotionLearningBundle } from "../domain/motionLearning.ts";
import { learnerStructureText } from "../domain/learnerStructureText.ts";
import { learnerActionExplanation } from "../domain/learnerActionText.ts";
import type { LegacyLearningSummary } from "../domain/legacyEvidenceAdapter.ts";
const evidenceFields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")).items as AiEvidenceField[];
const structureSummaries = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-structure-summaries.json", import.meta.url), "utf8")) as LegacyLearningSummary[];

const bundle = JSON.parse(readFileSync(new URL("../../../atlas-data/motion/motion-learning.json", import.meta.url), "utf8")) as MotionLearningBundle;
const fields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")) as { items: AiEvidenceField[] };
const pilotCalfIds = [
  "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
];

test("the six pilot calf action cards have field-linked citations and no authoring status", () => {
  assert.equal(bundle.muscleActions.length, 7);
  assert.equal(bundle.muscleActions.filter((row) => row.id.startsWith("T21-ACTION-")).length, 6);
  for (const id of pilotCalfIds) {
    const action = bundle.muscleActions.find((row) => row.subjectIds.includes(id));
    const card = projectLearnerActionCard(action, fields.items);
    assert.ok(card, `${id} should have an action card`);
    assert.ok(card.label.length > 0 && card.explanation.length > 0);
    assert.ok(card.postureConditions.length > 0);
    assert.ok(card.citations.some((row) => row.section === "action"));
    assert.ok(card.citations.some((row) => row.section === "posture"));
    assert.ok(card.citations.every((row) => row.url.startsWith("https://") && row.locator && row.accessedOn));
    const text = JSON.stringify(card);
    assert.doesNotMatch(text, /HA-M-|T21-|cross_checked|single_source|unavailable|reviewed|needs_review|JSON/);
  }
});

test("unassigned concepts do not receive inferred action cards", () => {
  assert.equal(projectLearnerActionCard(undefined, fields.items), null);
});

test("learner motion options retain six authored rows and keep the T24 candidate unplayable", () => {
  for (const id of pilotCalfIds) {
    const options = projectLearnerMotionActionOptions(id, bundle, fields.items);
    assert.equal(options.length, id === "HA-M-000003" ? 2 : 1);
    assert.ok(options.every((option) => option.label.length > 0 && option.candidate === null));
    assert.ok(options.every((option) => JSON.stringify(option.subjectIds) === JSON.stringify([id])));
  }
  assert.deepEqual(projectLearnerMotionActionOptions("HA-M-NOT-ASSIGNED", bundle, fields.items), []);
});

test("learner action copy omits source-scope disclosure while preserving underlying source claim", () => {
  const action = bundle.muscleActions.find((row) => row.subjectIds.includes("HA-M-000003"));
  assert.ok(action);
  assert.match(action.explanation, /출처에 한정되며/);
  assert.equal(learnerActionExplanation(action.explanation), "해당 근육은 발목 등쪽굽힘과 발 안쪽번짐에 관여합니다. 이 근육 하나가 움직임 전체를 단독으로 만든다는 뜻은 아닙니다.");
  assert.doesNotMatch(learnerActionExplanation(action.explanation), /출처|https?:\/\/|\[\d+\]|\b(?:19|20)\d{2}\b|현대 연구|사람 검토|AI 대조/);
});

test("origin and insertion learner text hides source disclosures while retaining the original evidence projection", () => {
  const original = evidenceFields.find((row) => row.subjectId === "HA-M-000001" && row.field === "origin");
  assert.ok(original);
  assert.equal(learnerStructureText(original, undefined), "비복근은 대퇴골 안쪽관절융기와 가쪽관절융기에서 시작합니다.");
  const insertion = evidenceFields.find((row) => row.subjectId === "HA-M-000001" && row.field === "insertion");
  assert.equal(learnerStructureText(insertion, undefined), "비복근은 발꿈치뼈(종골)에 정지합니다.");
});

test("conflicted attachment claims project only the short learner notice", () => {
  const original = evidenceFields.find((row) => row.subjectId === "HA-M-000005" && row.field === "origin");
  assert.ok(original);
  assert.equal(original.claims.length, 2);
  assert.equal(learnerStructureText(original, undefined), "설명 정리 중");
});

test("legacy structure summaries remain visible without adding evidence disclosures", () => {
  const summary = structureSummaries.find((row) => row.summary.trim());
  if (!summary) return;
  assert.equal(learnerStructureText(undefined, summary), summary.summary);
});
