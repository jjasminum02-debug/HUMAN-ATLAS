import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import type { AiEvidenceField } from "../domain/aiEvidence.ts";
import { projectLearnerActionCard, type MotionLearningBundle } from "../domain/motionLearning.ts";

const bundle = JSON.parse(readFileSync(new URL("../../../atlas-data/motion/motion-learning.json", import.meta.url), "utf8")) as MotionLearningBundle;
const fields = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/ai-evidence-overlay.json", import.meta.url), "utf8")) as { items: AiEvidenceField[] };
const pilotCalfIds = [
  "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
];

test("the six pilot calf action cards have field-linked citations and no authoring status", () => {
  assert.equal(bundle.muscleActions.length, 6);
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
