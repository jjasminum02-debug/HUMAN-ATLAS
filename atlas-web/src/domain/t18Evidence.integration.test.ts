import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { projectAiEvidenceField, type AiEvidenceField } from "./aiEvidence.ts";

const overlay = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")) as {
  denominatorFrozen: boolean;
  wholeBodyIndividualMuscleCount: number | null;
  coveragePercent: number | null;
  items: AiEvidenceField[];
};
const targetIds = [
  "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
  "HA-P-000001", "HA-P-000002",
];

test("T18 adds only origin/insertion fields for the six calf muscles and two existing gastrocnemius heads", () => {
  const rows = overlay.items.filter((row) => targetIds.includes(row.subjectId));
  assert.equal(rows.length, 16);
  assert.deepEqual(new Set(rows.map((row) => row.field)), new Set(["origin", "insertion"]));
  for (const id of targetIds) {
    for (const field of ["origin", "insertion"]) {
      const row = rows.find((candidate) => candidate.subjectId === id && candidate.field === field);
      assert.ok(row, `missing ${id} ${field}`);
      assert.equal(row.geometryState, "absent");
      assert.equal(row.motionState, "absent");
      assert.equal("humanReviewed" in row, false);
      assert.equal("reviewState" in row, false);
      const learner = projectAiEvidenceField(row);
      assert.doesNotMatch(JSON.stringify(learner), /cross_checked|reviewed|geometryState|motionState|HA-M-|HA-P-/);
    }
  }
  assert.equal(overlay.denominatorFrozen, false);
  assert.equal(overlay.wholeBodyIndividualMuscleCount, null);
  assert.equal(overlay.coveragePercent, null);
});

test("T18 source field projections distinguish cross-check, single-source head mapping, and the fibularis-longus extent conflict", () => {
  const row = (id: string, field: string) => {
    const found = overlay.items.find((candidate) => candidate.subjectId === id && candidate.field === field);
    assert.ok(found, `missing ${id} ${field}`);
    return found;
  };
  const gastroc = projectAiEvidenceField(row("HA-M-000001", "origin"));
  assert.ok(gastroc.text);
  assert.equal(gastroc.sources.length, 2);
  const lateralHead = projectAiEvidenceField(row("HA-P-000001", "origin"));
  assert.ok(lateralHead.text);
  assert.equal(lateralHead.sources.length, 1);
  assert.match(lateralHead.note ?? "", /한 자료/);
  const medialHead = projectAiEvidenceField(row("HA-P-000002", "origin"));
  assert.ok(medialHead.text);
  assert.equal(medialHead.sources.length, 1);
  const conflict = projectAiEvidenceField(row("HA-M-000005", "origin"));
  assert.equal(conflict.text, null);
  assert.equal(conflict.alternatives.length, 2);
  assert.equal(conflict.alternatives.every((alternative) => alternative.sources.length === 1), true);
  const urls = conflict.alternatives.map((alternative) => alternative.sources[0].url);
  assert.notEqual(urls[0], urls[1]);
  assert.match(conflict.alternatives[0].text, /3분의 2/);
  assert.match(conflict.alternatives[1].text, /절반/);
});
