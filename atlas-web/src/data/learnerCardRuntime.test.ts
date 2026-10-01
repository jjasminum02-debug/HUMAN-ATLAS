import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../../../", import.meta.url);
const runtime = JSON.parse(readFileSync(new URL("atlas-data/terminology/learner-card-runtime.json", root), "utf8"));
const sourceContent = JSON.parse(readFileSync(new URL("atlas-data/terminology/learner-structure-source-content.json", root), "utf8"));
const originalNames = JSON.parse(readFileSync(new URL("atlas-data/terminology/learning-names.json", root), "utf8"));

test("learner card runtime is a minimal text projection with no source or review ledger fields", () => {
  assert.deepEqual(Object.keys(runtime).sort(), ["actions", "names", "schemaVersion", "structure"]);
  assert.deepEqual(Object.keys(runtime.structure).sort(), ["byConcept", "bySource"]);
  assert.equal(runtime.names.length, originalNames.entries.length);
  for (const [index, row] of runtime.names.entries()) {
    assert.deepEqual(Object.keys(row).sort(), ["aliases", "english", "entityType", "id", "korean", "label", "lookupOnly", "parentId"]);
    assert.deepEqual(row.id, originalNames.entries[index].id);
    for (const value of [row.label, row.korean, row.english, ...row.aliases]) {
      assert.doesNotMatch(value ?? "", /\p{Script=Han}/u);
    }
  }
  assert.equal(Object.keys(runtime.structure.bySource).length, 14);
  assert.equal(Object.keys(runtime.structure.byConcept).length, 8);
  assert.equal(runtime.actions.length, 7);
  const encoded = JSON.stringify(runtime);
  assert.doesNotMatch(encoded, /https?:\/\/|cross_checked|single_source|evidenceHash|fieldEvidenceId|T18-|T21-|sourceIds|humanReviewed|not_performed|publicRedistribution|locator|accessedOn/);
});

test("supported structure cards preserve exact claim text, conflict copy, and field separation", () => {
  assert.equal(runtime.structure.byConcept["HA-M-000001"].origin, "비복근은 대퇴골 안쪽관절융기와 가쪽관절융기에서 시작합니다.");
  assert.equal(runtime.structure.byConcept["HA-M-000001"].insertion, "비복근은 발꿈치뼈(종골)에 정지합니다.");
  assert.equal(runtime.structure.byConcept["HA-M-000005"].origin, "설명 정리 중");
  assert.equal(runtime.structure.byConcept["HA-M-000001"].motorNerve, undefined);
  assert.equal(runtime.structure.byConcept["HA-M-000001"].sensoryProprioception, undefined);

  const lateralHead = sourceContent.records.find((row: { targetId: string | null; sourceKeys: string[] }) => row.targetId === "TA2:2658");
  assert.ok(lateralHead);
  const sourceKey = lateralHead.sourceKeys[0];
  assert.equal(runtime.structure.bySource[sourceKey].origin, "비복근 외측두는 대퇴골 외측관절융기에서 시작합니다.");
  assert.equal(runtime.structure.bySource[sourceKey].insertion, "자료에는 비복근의 공통 정지가 종골로 기록되어 있고, 외측두만의 별도 원위 부착면은 나뉘어 제시되지 않습니다.");
});

test("action tab receives only learner strings and retains the current no-clip state", () => {
  const rows = runtime.actions.filter((row: { conceptId: string }) => row.conceptId === "HA-M-000003");
  assert.equal(rows.length, 2);
  assert.equal(rows[0].sideApplicability, null);
  assert.equal(rows[1].sideApplicability, "right");
  for (const row of rows) {
    assert.deepEqual(Object.keys(row).sort(), ["conceptId", "explanation", "key", "label", "sideApplicability"]);
    assert.doesNotMatch(JSON.stringify(row), /https?:\/\/|evidence|claim|source|T21-|T18-/i);
    assert.doesNotMatch(`${row.label} ${row.explanation}`, /\p{Script=Han}/u);
  }
  assert.match(rows[1].explanation, /오른쪽 발목/);
  assert.doesNotMatch(rows[1].explanation, /이 시범은/);
});
