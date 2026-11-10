import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import type { AiEvidenceField } from "../domain/aiEvidence.ts";
import { learnerStructureText } from "../domain/learnerStructureText.ts";
import { learnerStructureSourceText, learnerStructureUnavailability } from "../domain/learnerStructureSourceContent.ts";
import type { LegacyLearningSummary } from "../domain/legacyEvidenceAdapter.ts";
const evidenceFields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")).items as AiEvidenceField[];
const structureSummaries = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-structure-summaries.json", import.meta.url), "utf8")) as LegacyLearningSummary[];
const sourceStructureContentRows = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learner-structure-source-content.json", import.meta.url), "utf8")).records;


function sourceStructureText(sourceKey: string, field: "origin" | "insertion") {
  const record = sourceStructureContentRows.find((row: { sourceKeys: string[] }) => row.sourceKeys.includes(sourceKey));
  return learnerStructureSourceText(record, field, (subjectId, projectField) => {
    const current = evidenceFields.find((row) => row.subjectId === subjectId && row.field === projectField);
    const legacy = structureSummaries.find((row) => row.conceptId === subjectId && row.role === projectField);
    return learnerStructureText(current, legacy);
  });
}

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
