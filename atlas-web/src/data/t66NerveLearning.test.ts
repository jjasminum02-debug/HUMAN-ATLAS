import assert from "node:assert/strict";
import { createHash as nodeCreateHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { conceptForExactNerveName, isNerveRelatedActionTextIntent, relationsForNerve } from "../domain/nerveRelations.ts";

const json = (path: string) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const graph = json("../../../atlas-data/terminology/learner-nerve-graph-t66.json");
const support = json("../../../atlas-data/overlays/nerve-support-t66.json");
const integration = json("../../../atlas-data/overlays/za-local-integration.json");
const course = json("../../../atlas-data/terminology/nerve-learning-t66.json");
const ledger = json("../../../work/evidence/T66/nerve-learning-2026-10-05/nerve-relation-ledger.json");
const eligibleMuscles = new Map(integration.objects
  .filter((row: any) => row.kind === "muscle" && row.localDisplayEligible && row.inspectionEligible)
  .map((row: any) => [row.sourceKey, row]));

test("the frozen nerve source inventory remains 195 surfaces and 98 display-label groups", () => {
  const labels = new Set(support.instances.map((row: any) => row.names.en));
  assert.equal(support.instances.length, 195);
  assert.equal(labels.size, 98);
  assert.equal(ledger.denominators.staticSourceSurfaces, 195);
  assert.equal(ledger.denominators.uniqueSourceLabelGroups, 98);
  assert.equal(ledger.denominators.independentAnatomyConceptCount, "not inferred from label groups");
  assert.equal(ledger.labelGroupDisposition.length, 98);
  assert.ok(ledger.labelGroupDisposition.every((row: any) => row.sourceSurfaceCount > 0));
});

test("native nerve labels have explicit evidence states without converting unlinked to absent", () => {
  const accepted = new Set([
    "mixed_motor_sensory_evidence_and_motor_relation",
    "sensory_course_documented_no_motor_relation",
    "motor_relation_documented_sensory_class_not_assessed",
    "relationship_not_linked",
  ]);
  assert.ok(graph.concepts.every((row: any) => accepted.has(row.functionEvidenceClass)));
  assert.equal(ledger.labelGroupDisposition.filter((row: any) => row.functionEvidenceClass === "unmapped_source_label").length, 0);
  for (const name of ["Lateral femoral cutaneous nerve", "Posterior femoral cutaneous nerve"]) {
    const concept = graph.concepts.find((row: any) => row.names.en === name);
    assert.ok(concept);
    assert.equal(concept.functionEvidenceClass, "sensory_course_documented_no_motor_relation");
    assert.equal(graph.motorRelations.some((row: any) => row.nerveKey === concept.key), false);
  }
  assert.notEqual(
    graph.concepts.find((row: any) => row.names.en === "Lateral femoral cutaneous nerve")?.key,
    graph.concepts.find((row: any) => row.names.en === "Posterior femoral cutaneous nerve")?.key,
  );
  assert.ok(graph.concepts.find((row: any) => row.names.en === "Femoral nerve"));
});

test("motor relationship ledger preserves exact geometry and literature concept scope separately", () => {
  assert.equal(graph.motorRelations.length, 18);
  assert.equal(graph.motorRelations.filter((row: any) => row.basis === "exact_geometry_motor_relation").length, 2);
  assert.equal(graph.motorRelations.filter((row: any) => row.basis === "literature_concept_motor_relation").length, 16);
  assert.equal(new Set(graph.motorRelations.map((row: any) => row.relationId)).size, graph.motorRelations.length);
  for (const relation of graph.motorRelations) {
    assert.ok(relation.targetSourceKeys.length > 0, relation.relationId);
    assert.ok(relation.displayNote.length > 0, relation.relationId);
    assert.equal(ledger.relations.find((row: any) => row.relationId === relation.relationId)?.basis, relation.basis);
    assert.ok(ledger.relations.find((row: any) => row.relationId === relation.relationId)?.sourceIds.length > 0, relation.relationId);
    for (const sourceKey of relation.targetSourceKeys) {
      const target = eligibleMuscles.get(sourceKey) as any;
      assert.ok(target, `${relation.relationId} points to an absent/ineligible target ${sourceKey}`);
      assert.equal(target.kind, "muscle");
    }
    if (relation.scope === "exact_side_matched_source_instance") {
      assert.ok(relation.targetSide === "left" || relation.targetSide === "right");
      assert.ok(relation.targetSourceKeys.every((key: string) => (eligibleMuscles.get(key) as any).side === relation.targetSide));
      assert.equal(relation.basis, "exact_geometry_motor_relation");
    } else {
      assert.equal(relation.targetSide, null);
      assert.deepEqual(new Set(relation.targetSourceKeys.map((key: string) => (eligibleMuscles.get(key) as any).side)), new Set(["left", "right"]));
      assert.equal(relation.basis, "literature_concept_motor_relation");
    }
  }
  assert.equal(ledger.relationSummary.exactGeometryMotorRows, 2);
  assert.equal(ledger.relationSummary.literatureConceptRows, 16);
  assert.equal(ledger.relationSummary.totalRows, 18);
  assert.equal(ledger.relationSummary.uniqueNerveConceptKeys, 9);
  assert.equal(new Set(graph.motorRelations.flatMap((row: any) => row.targetSourceKeys)).size, ledger.relationSummary.uniqueTargetSourceKeys);
});

test("same-side exact relation filtering and exact native-name fallback are deterministic", () => {
  const dorsal = graph.concepts.find((row: any) => row.key === "dorsal-scapular");
  assert.ok(dorsal);
  assert.equal(dorsal.sourceNativeEnglishName, "Dorsal scapular nerve");
  assert.equal(conceptForExactNerveName(graph.concepts, "Dorsal scapular nerve")?.key, "dorsal-scapular");
  assert.equal(conceptForExactNerveName([{ ...dorsal, sourceNativeEnglishName: null }], "Dorsal scapular nerve")?.key, "dorsal-scapular");
  const ambiguous = [
    { ...dorsal, key: "first" },
    { ...dorsal, key: "second" },
  ];
  assert.equal(conceptForExactNerveName(ambiguous, "Dorsal scapular nerve"), null);
  const deepFibular = graph.motorRelations.filter((row: any) => row.nerveKey === "deep-fibular");
  assert.deepEqual(relationsForNerve(deepFibular, "deep-fibular", "left").map((row: any) => row.targetSide), ["left"]);
  assert.deepEqual(relationsForNerve(deepFibular, "deep-fibular", "right").map((row: any) => row.targetSide), ["right"]);
  assert.equal(relationsForNerve(deepFibular, "deep-fibular", null).length, 2);
});

test("nerve cards include only action text or true muscle-action options, never posture-only context", () => {
  assert.equal(isNerveRelatedActionTextIntent("muscle_action"), true);
  assert.equal(isNerveRelatedActionTextIntent("text_only"), true);
  assert.equal(isNerveRelatedActionTextIntent("posture_observation"), false);
  assert.equal(isNerveRelatedActionTextIntent("bone_motion"), false);
  assert.equal(isNerveRelatedActionTextIntent(undefined), false);
});

test("learner-facing text carries no internal evidence IDs and preserves held review and rights", () => {
  const learnerText = JSON.stringify({ graph: graph.concepts.map((row: any) => ({ names: row.names, summary: row.summary })), course });
  assert.doesNotMatch(learnerText, /T66_|T61_|PMID|PMCID|https?:\/\/|sourceKey|evidenceHash|humanReview|publicRedistribution/);
  assert.equal(ledger.preservedPolicy.sourceOnly, true);
  assert.equal(ledger.preservedPolicy.localSelection, "verified_geometry_only");
  assert.equal(ledger.preservedPolicy.humanReview, "not_performed");
  assert.equal(ledger.preservedPolicy.publicRedistribution, "held");
  assert.equal(ledger.preservedPolicy.newCanonicalBindings, 0);
  assert.equal(ledger.preservedPolicy.newNerveGeometry, 0);
  assert.equal(ledger.preservedPolicy.newBranchCoordinates, 0);
  for (const [fieldKey, evidence] of Object.entries(ledger.learnerFieldEvidence) as Array<[string, any]>) {
    const [nerveName, field] = fieldKey.split(":");
    assert.ok(course[nerveName][field]);
    assert.equal(createHash(course[nerveName][field]), evidence.valueSha256);
    assert.ok(evidence.sourceIds.length > 0);
  }
});

function createHash(value: string) {
  return nodeCreateHash("sha256").update(value).digest("hex");
}
