import learnerCardRuntime from "../../../atlas-data/terminology/learner-card-runtime.json";
import { displayTerms, termText, type PilotCatalog } from "./catalog";
import { learnerNameProjection, learnerSearchEntry, learnerVisibleTerms, mergeLearningConcepts, searchEntries, type SearchEntry } from "../domain/search";
import learnerNerveGraph from "../../../atlas-data/terminology/learner-nerve-graph-t66.json";
import nerveDisplayNames from "../../../atlas-data/terminology/learner-nerve-display-names.json";
import { withNerveDisplayNames } from "../domain/nerveDisplayNames.ts";
import learnerNerveCourse from "../../../atlas-data/terminology/nerve-learning-t66.json";
import type { LearnerFieldProjection } from "../domain/aiEvidence";
import { learnerStructureUnavailability } from "../domain/learnerStructureSourceContent";
import { relationsForNerve } from "../domain/nerveRelations.ts";
import { createLearnerLookupIndex } from "../domain/learnerLookupIndex.ts";

type LearnerCardRuntime = {
  schemaVersion: "learner-card-runtime-v1";
  names: Array<{ id: string; label: string; korean: string; english: string; aliases: string[]; parentId: string | null; entityType: string; lookupOnly: boolean }>;
  structure: {
    byConcept: Record<string, Partial<Record<"origin" | "insertion", string>>>;
    bySource: Record<string, Partial<Record<"origin" | "insertion", string>>>;
  };
  nerveLearning: Record<string, { courseContext: string; compressionContext: string; functionContext: string }>;
  actions: Array<{ conceptId: string; key: string; label: string; explanation: string; sideApplicability: "left" | "right" | null }>;
};

const cardRuntime = learnerCardRuntime as LearnerCardRuntime;
type LearnerNerveConcept = {
  key: string;
  names: { koModern: string; koTraditional: string; en: string; latin: string };
  searchTerms: string[];
  sourceNativeEnglishName: string | null;
  summary?: { course: string; motorRelation: string; variation: string };
  functionEvidenceClass?: "mixed_motor_sensory_evidence_and_motor_relation" | "sensory_course_documented_no_motor_relation" | "motor_relation_documented_sensory_class_not_assessed" | "relationship_not_linked";
};
export type LearnerMotorRelation = {
  relationId: string;
  nerveKey: string;
  basis: "exact_geometry_motor_relation" | "literature_concept_motor_relation";
  targetEnglishConcept?: string;
  targetSourceKeys: string[];
  targetSide: "left" | "right" | null;
  scope: "exact_side_matched_source_instance" | "unsided_named_whole_muscle_concept" | "unsided_named_muscle_part_set" | "unsided_partial_muscle_concept";
  displayNote: string;
};
type LearnerNerveGraph = {
  schemaVersion: "learner-nerve-graph-v1";
  concepts: LearnerNerveConcept[];
  motorRelations: LearnerMotorRelation[];
};
const nativeNerveGraph = learnerNerveGraph as LearnerNerveGraph;
const nerveGraph: LearnerNerveGraph = { ...nativeNerveGraph,
  concepts: withNerveDisplayNames(nativeNerveGraph.concepts, nerveDisplayNames) };
const lookups = createLearnerLookupIndex(cardRuntime.names, cardRuntime.actions, nerveGraph.concepts, nerveGraph.motorRelations);
const nerveSearchEntries = nerveGraph.concepts.map(concept => learnerSearchEntry(
  concept.key, concept.names.koModern,
  [concept.names.koTraditional, concept.names.en, concept.names.latin, ...concept.searchTerms],
));
export const vocabulary = cardRuntime.names;

export function nameFor(catalog: PilotCatalog, id: string) {
  const entry = lookups.namesById.get(id);
  const terms = learnerVisibleTerms(displayTerms(catalog, id));
  return learnerNameProjection(id, entry ?? {}, {
    korean: terms.find((term) => term.language === "ko")?.text,
    english: termText(catalog, id, "en"),
    latin: termText(catalog, id, "la"),
  });
}

export function learningConcepts(catalog: PilotCatalog) {
  return mergeLearningConcepts(catalog.concepts, vocabulary);
}

export function findMuscles(catalog: PilotCatalog, query: string) {
  const entries: SearchEntry[] = learningConcepts(catalog).map((concept) => {
    const names = nameFor(catalog, concept.id);
    const custom = lookups.namesById.get(concept.id);
    const terms = learnerVisibleTerms(displayTerms(catalog, concept.id));
    return learnerSearchEntry(concept.id, names.label, [names.koTraditional, names.koModern, names.en, ...custom?.aliases ?? [],
      ...terms.flatMap((term) => typeof term.text === "string" ? [term.text] : [])]);
  });
  return searchEntries(entries, query);
}

/** Learner-safe field projection; provenance and review detail stay in development evidence. */
export function structureFieldForLearner(conceptId: string, field: string): LearnerFieldProjection | null {
  if (field !== "origin" && field !== "insertion") return null;
  const text = cardRuntime.structure.byConcept[conceptId]?.[field];
  return text ? { text, note: null, alternatives: [], sources: [], quizEligible: false } : null;
}

export function structureTextForLearner(conceptId: string, field: string): string | null {
  return structureFieldForLearner(conceptId, field)?.text ?? null;
}

/** Resolve only the source-scoped learner text frozen from T81 pointers. */
export function structureTextForSource(sourceKey: string, field: "origin" | "insertion"): string | null {
  return cardRuntime.structure.bySource[sourceKey]?.[field] ?? null;
}

export function structureUnavailabilityForLearner(field: "origin" | "insertion" | "motorNerve" | "sensoryProprioception") {
  return learnerStructureUnavailability(field);
}

export function structureSummary(conceptId: string, role: string) {
  return structureFieldForLearner(conceptId, role)?.text ?? undefined;
}

/** Learner-safe text for the supported fibular nerve concepts; source evidence stays internal. */
export function nerveLearningForLearner(englishName: string) {
  return (learnerNerveCourse as Record<string, { courseContext: string; compressionContext: string; variationContext: string; functionContext: string }>)[englishName]
    ?? cardRuntime.nerveLearning[englishName] ?? null;
}

/** Nerve terms are searchable aliases; evidence and review metadata stay in work/evidence. */
export function nerveConceptsForLearner(query = "") {
  return searchEntries(nerveSearchEntries, query).flatMap(match => {
    const concept = lookups.nervesByKey.get(match.entry.id);
    return concept ? [{ concept, approximate: match.approximate }] : [];
  });
}

export function nerveConceptForLearner(key: string) {
  return lookups.nervesByKey.get(key) ?? null;
}

export function nerveConceptForSourceName(englishName: string) {
  return lookups.nerveForExactName(englishName);
}

export function nerveNamesForSource(englishName: string) {
  return nerveConceptForSourceName(englishName)?.names ?? null;
}

/** Both card directions read the same exact relation rows and preserve side/scope. */
export function motorRelationsForSource(sourceKey: string): LearnerMotorRelation[] {
  return [...lookups.relationsBySource.get(sourceKey) ?? []];
}

export function motorRelationsForNerve(nerveKey: string, selectedSide?: string | null): LearnerMotorRelation[] {
  return relationsForNerve(lookups.relationsByNerve.get(nerveKey) ?? [], nerveKey, selectedSide);
}

export function nerveGraphForLearner() {
  return nerveGraph;
}
