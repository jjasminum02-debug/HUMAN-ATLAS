import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import type { AiEvidenceField } from "../domain/aiEvidence.ts";
import { projectLearnerActionCard, projectLearnerMotionActionOptions, type MotionLearningBundle } from "../domain/motionLearning.ts";
import { learnerStructureText } from "../domain/learnerStructureText.ts";
import { learnerStructureSourceText, learnerStructureUnavailability } from "../domain/learnerStructureSourceContent.ts";
import { learnerActionExplanation } from "../domain/learnerActionText.ts";
import { learnerActionAppliesToSide, learnerFunctionUnavailableText } from "../domain/learnerActionText.ts";
import type { LegacyLearningSummary } from "../domain/legacyEvidenceAdapter.ts";
import safeMotionRuntime from "./learnerMotionRuntime.generated.ts";
const evidenceFields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")).items as AiEvidenceField[];
const structureSummaries = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-structure-summaries.json", import.meta.url), "utf8")) as LegacyLearningSummary[];
const sourceStructureContentRows = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learner-structure-source-content.json", import.meta.url), "utf8")).records;

const bundle = JSON.parse(readFileSync(new URL("../../../atlas-data/motion/motion-learning.json", import.meta.url), "utf8")) as MotionLearningBundle;
const fields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")) as { items: AiEvidenceField[] };
const learnerRuntime = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learner-card-runtime.json", import.meta.url), "utf8"));
const pilotCalfIds = [
  "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
];

function sourceStructureText(sourceKey: string, field: "origin" | "insertion") {
  const record = sourceStructureContentRows.find((row: { sourceKeys: string[] }) => row.sourceKeys.includes(sourceKey));
  return learnerStructureSourceText(record, field, (subjectId, projectField) => {
    const current = evidenceFields.find((row) => row.subjectId === subjectId && row.field === projectField);
    const legacy = structureSummaries.find((row) => row.conceptId === subjectId && row.role === projectField);
    return learnerStructureText(current, legacy);
  });
}

test("the six pilot calf action cards have field-linked citations and no authoring status", () => {
  assert.equal(bundle.muscleActions.filter(a => a.subjectKind !== "bone" && !a.sourceFamilyId).length, 8);
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
    assert.equal(options.length, id === "HA-M-000003" ? 3 : 1);
    assert.ok(options.every((option) => option.label.length > 0));
    assert.equal(options.filter(option => option.candidate !== null).length, id === "HA-M-000003" ? 1 : 0);
    assert.ok(options.filter(option => option.candidate !== null).every(option => option.candidate?.asset.sourceBinding?.subjectSourceKey === "ZA-c7010a9-54ae5266082b61f48ed8e83e"));
    assert.ok(options.every((option) => JSON.stringify(option.subjectIds) === JSON.stringify([id])));
  }
  assert.deepEqual(projectLearnerMotionActionOptions("HA-M-NOT-ASSIGNED", bundle, fields.items), []);
});

test("learner motion runtime excludes raw evidence and exposes no unavailable production clip", () => {
  const serialized = JSON.stringify(safeMotionRuntime);
  assert.equal(safeMotionRuntime.schemaVersion, "learner-motion-runtime-v1");
  assert.equal(Object.values(safeMotionRuntime.actions).reduce((count, rows) => count + rows.length, 0), 281);
  assert.equal(Object.values(safeMotionRuntime.actions).flat().filter((row) => row.candidate !== null).length, 274);
  const renderedText = JSON.stringify(Object.values(safeMotionRuntime.actions).flat().map(row => ({ label: row.label, text: row.text })));
  assert.doesNotMatch(renderedText, /T21-|T24-|T59-|sourceKey|evidenceHash|https?:\/\//);
  assert.doesNotMatch(serialized, /evidenceHash|fieldEvidenceId|sourceRefs|poseSourceRefs|https?:\/\//);
});

test("the T24 text candidate keeps its right-side scope while its clip remains unavailable", () => {
  const tibialisActions = projectLearnerMotionActionOptions("HA-M-000003", bundle, fields.items);
  const rightCandidate = tibialisActions.find((option) => option.sideApplicability === "right");
  assert.ok(rightCandidate);
  assert.equal(rightCandidate.candidate, null);
  assert.equal(learnerActionAppliesToSide(rightCandidate.sideApplicability, "left"), false);
  assert.equal(learnerActionAppliesToSide(rightCandidate.sideApplicability, "right"), true);
  assert.equal(learnerActionAppliesToSide(rightCandidate.sideApplicability, null), false, "unilateral text needs a matching selected side");
  assert.equal(learnerActionAppliesToSide(rightCandidate.sideApplicability, undefined), false, "unilateral text stays hidden when side is unknown");
  assert.equal(learnerActionAppliesToSide(null, "left"), true, "bilateral action text remains available on both sides");
  assert.equal(learnerActionAppliesToSide(null, null), true, "bilateral action text remains available when side is unspecified");
  const projected = learnerRuntime.actions.filter((option: { conceptId: string }) => option.conceptId === "HA-M-000003");
  const forLeft = projected.filter((option: { sideApplicability: string | null }) => learnerActionAppliesToSide(option.sideApplicability, "left"));
  const forRight = projected.filter((option: { sideApplicability: string | null }) => learnerActionAppliesToSide(option.sideApplicability, "right"));
  assert.deepEqual(forLeft.map((option: { label: string }) => option.label), ["발목 등쪽굽힘과 발 안쪽번짐"]);
  assert.deepEqual(forRight.map((option: { label: string }) => option.label), ["발목 등쪽굽힘과 발 안쪽번짐", "오른쪽 발목 등쪽굽힘"]);
  assert.deepEqual(projectLearnerMotionActionOptions("HA-P-000001", bundle, fields.items), [], "a whole-muscle action must not be inherited by the lateral head");
  assert.deepEqual(projectLearnerMotionActionOptions("HA-P-000002", bundle, fields.items), [], "a whole-muscle action must not be inherited by the medial head");
});

test("unsupported function content has a clear learner message and stays separate from clip state", () => {
  assert.equal(learnerFunctionUnavailableText(), "현재 확인 가능한 기능 설명이 없습니다.");
  assert.equal(bundle.motionAssets.filter((asset) => asset.technicalStatus === "binding_verified").length, 274);
  assert.equal(bundle.motionAssets.find(asset => asset.id.includes("T24-"))?.technicalStatus, "candidate");
});

test("learner action copy omits source-scope disclosure while preserving underlying source claim", () => {
  const action = bundle.muscleActions.find((row) => row.subjectIds.includes("HA-M-000003"));
  assert.ok(action);
  assert.match(action.explanation, /출처에 한정되며/);
  assert.equal(learnerActionExplanation(action.explanation), "해당 근육은 발목 등쪽굽힘과 발 안쪽번짐에 관여합니다. 이 근육 하나가 움직임 전체를 단독으로 만든다는 뜻은 아닙니다.");
  assert.doesNotMatch(learnerActionExplanation(action.explanation), /출처|https?:\/\/|\[\d+\]|\b(?:19|20)\d{2}\b|현대 연구|사람 검토|AI 대조/);
  const rightCandidate = bundle.muscleActions.find((row) => row.id.startsWith("T24-"));
  assert.ok(rightCandidate);
  assert.doesNotMatch(learnerActionExplanation(rightCandidate.explanation), /시범|재생/);
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

test("T81 projects existing attachment evidence only to exact source surfaces and keeps conflicts short", () => {
  const projection = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learner-structure-source-content.json", import.meta.url), "utf8"));
  const lateralHead = projection.records.find((row: { targetId: string | null }) => row.targetId === "TA2:2658");
  const medialHead = projection.records.find((row: { targetId: string | null }) => row.targetId === "TA2:2659");
  const tibialisAnterior = projection.records.find((row: { targetId: string | null }) => row.targetId === "TA2:2644");
  const fibularisLongus = projection.records.find((row: { targetId: string | null }) => row.targetId === "TA2:2652");
  assert.ok(lateralHead && medialHead && tibialisAnterior && fibularisLongus);
  assert.equal(lateralHead.scopeType, "explicit_part");
  assert.equal(medialHead.scopeType, "explicit_part");
  assert.equal(lateralHead.subjectId, "HA-P-000001");
  assert.equal(medialHead.subjectId, "HA-P-000002");
  assert.notEqual(lateralHead.subjectId, medialHead.subjectId);
  assert.ok(lateralHead.sourceKeys.every((key: string) => sourceStructureText(key, "origin")));
  assert.ok(medialHead.sourceKeys.every((key: string) => sourceStructureText(key, "origin")));
  assert.match(sourceStructureText(tibialisAnterior.sourceKeys[0], "origin") ?? "", /앞정강근/);
  assert.equal(sourceStructureText(fibularisLongus.sourceKeys[0], "origin"), "설명 정리 중");
  assert.ok(sourceStructureText(fibularisLongus.sourceKeys[0], "insertion"));
  assert.equal(projection.records.some((row: { targetId: string | null }) => row.targetId === "TA2:2657"), false,
    "head surfaces must not inherit the entire gastrocnemius claim");
});

test("T81 covers every supported source muscle while keeping workbook and nerve fields non-claim data separate", () => {
  const projection = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learner-structure-source-content.json", import.meta.url), "utf8"));
  const keys = projection.records.flatMap((row: { sourceKeys: string[] }) => row.sourceKeys);
  assert.equal(projection.records.length, 232);
  assert.equal(keys.length, 462);
  assert.equal(new Set(keys).size, 462);
  assert.ok(projection.records.every((row: { sourceOnly: boolean; canonicalBindingCreated: boolean; humanReview: string; publicRedistribution: string }) =>
    row.sourceOnly && !row.canonicalBindingCreated && row.humanReview === "not_performed" && row.publicRedistribution === "held"));
  assert.ok(projection.records.every((row: { fieldDisposition: Record<string, { status: string }> }) =>
    row.fieldDisposition.motorNerve.status === "no_verified_field_claim"
    && row.fieldDisposition.sensoryProprioception.status === "no_verified_field_claim"));
  const hand = projection.records.find((row: { sourceDataName: string }) => row.sourceDataName === "Abductor digiti minimi of hand");
  const foot = projection.records.find((row: { sourceDataName: string }) => row.sourceDataName === "Abductor digiti minimi of foot");
  if (hand && foot) {
    assert.equal(hand.subjectId, null);
    assert.equal(foot.subjectId, null);
    assert.equal(sourceStructureText(hand.sourceKeys[0], "origin"), null);
    assert.equal(sourceStructureText(foot.sourceKeys[0], "origin"), null);
  }
  assert.equal(learnerStructureUnavailability("motorNerve"), "확인된 운동신경 설명이 없습니다.");
  assert.equal(learnerStructureUnavailability("sensoryProprioception"), "별도로 확인된 감각·고유감각 설명이 없습니다.");
  assert.doesNotMatch(JSON.stringify(projection), /근육-기시정지-신경-작용-정리\.xlsx|originCandidate|sensoryProprioceptionCandidate|https?:\/\//);
  const learnerText = projection.records.filter((row: { subjectId: string | null }) => row.subjectId)
    .flatMap((row: { sourceKeys: string[] }) => row.sourceKeys.map((key: string) => sourceStructureText(key, "origin") ?? ""))
    .join(" ");
  assert.doesNotMatch(learnerText, /HA-M-|HA-P-|cross_checked|single_source|conflicted|T18-|https?:\/\/|사람 검토|AI 대조/,
    "learner-facing text must not expose evidence or review metadata");
});
