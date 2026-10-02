import learnerCardRuntime from "../../../atlas-data/terminology/learner-card-runtime.json";
import learnerMotionRuntime from "./learnerMotionRuntime.generated.ts";
import { displayTerms, termText, type PilotCatalog } from "./catalog";
import { learnerNameProjection, learnerSearchEntry, learnerVisibleTerms, mergeLearningConcepts, searchEntries, type SearchEntry } from "../domain/search";
import learnerNerveGraph from "../../../atlas-data/terminology/learner-nerve-graph-t66.json";
import learnerNerveCourse from "../../../atlas-data/terminology/nerve-learning-t66.json";
import type { LearnerFieldProjection } from "../domain/aiEvidence";
import { learnerStructureUnavailability } from "../domain/learnerStructureSourceContent";
import { learnerActionAppliesToSide } from "../domain/learnerActionText";
import { resolveLearnerMotionCandidate, type LearnerMotionActionOption, type LearnerActionText } from "../domain/motionLearning.ts";

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
};
export type LearnerMotorRelation = {
  nerveKey: string;
  targetEnglishConcept?: string;
  targetSourceKeys: string[];
  targetSide: "left" | "right" | null;
  scope: "exact_side_matched_source_instance" | "unsided_named_whole_muscle_concept";
  displayNote: string;
};
type LearnerNerveGraph = {
  schemaVersion: "learner-nerve-graph-v1";
  concepts: LearnerNerveConcept[];
  motorRelations: LearnerMotorRelation[];
};
const nerveGraph = learnerNerveGraph as LearnerNerveGraph;
type LearnerMotionRuntime = {
  schemaVersion: "learner-motion-runtime-v1";
  actions: Record<string, Array<{
    actionKey: string;
    learnerActionKey: string | null;
    label: string;
    text: LearnerActionText;
    sideApplicability: "left" | "right" | "bilateral" | "midline" | "not_applicable";
    candidate: LearnerMotionActionOption["candidate"];
  }>>;
};
const motionRuntime = learnerMotionRuntime as unknown as LearnerMotionRuntime;
export const vocabulary = cardRuntime.names;

export function nameFor(catalog: PilotCatalog, id: string) {
  const entry = vocabulary.find((row) => row.id === id);
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
    const custom = vocabulary.find((row) => row.id === concept.id);
    const terms = learnerVisibleTerms(displayTerms(catalog, concept.id));
    return learnerSearchEntry(concept.id, names.label, [names.koTraditional, names.koModern, names.en, ...custom?.aliases ?? [],
      ...terms.flatMap((term) => typeof term.text === "string" ? [term.text] : [])]);
  });
  return searchEntries(entries, query);
}

/** Learner-only action text is preprojected; source/evidence references stay out of this bundle. */
export function motionActionOptionsForLearner(conceptId: string | null, selectedSide?: string | null, sourceKey?: string | null) {
  const selector = sourceKey && motionRuntime.actions[sourceKey]?.length ? sourceKey : conceptId ?? sourceKey;
  const projected = (selector ? motionRuntime.actions[selector] ?? [] : []).filter(row =>
    !row.candidate || !sourceKey || row.candidate.asset.sourceBinding?.subjectSourceKey === sourceKey);
  const displayRows = cardRuntime.actions.filter((row) => row.conceptId === conceptId
    && learnerActionAppliesToSide(row.sideApplicability, selectedSide)).map((row) => {
    return {
      id: row.key,
      label: row.label,
      text: { label: row.label, explanation: row.explanation },
      sideApplicability: row.sideApplicability,
      candidate: resolveLearnerMotionCandidate(row.key, selectedSide, projected),
    };
  });
  if ((conceptId && selector === conceptId) || !sourceKey) return displayRows;
  // A source-only action is reachable by exact sourceKey; no canonical ID or alias is invented.
  return projected.filter((row) => learnerActionAppliesToSide(row.sideApplicability, selectedSide)).map((row) => ({
    id: row.actionKey,
    label: row.label,
    text: { label: row.text.label, explanation: row.text.explanation },
    sideApplicability: row.sideApplicability === "left" || row.sideApplicability === "right" ? row.sideApplicability : null,
    candidate: row.candidate,
  }));
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
  const entries: SearchEntry[] = nerveGraph.concepts.map(concept => learnerSearchEntry(
    concept.key,
    concept.names.koModern,
    [concept.names.koTraditional, concept.names.en, concept.names.latin, ...concept.searchTerms],
  ));
  return searchEntries(entries, query).flatMap(match => {
    const concept = nerveGraph.concepts.find(row => row.key === match.entry.id);
    return concept ? [{ concept, approximate: match.approximate }] : [];
  });
}

export function nerveConceptForLearner(key: string) {
  return nerveGraph.concepts.find(row => row.key === key) ?? null;
}

export function nerveConceptForSourceName(englishName: string) {
  return nerveGraph.concepts.find(row => row.sourceNativeEnglishName === englishName) ?? null;
}

export function nerveNamesForSource(englishName: string) {
  return nerveConceptForSourceName(englishName)?.names ?? null;
}

/** Both card directions read the same exact relation rows and preserve side/scope. */
export function motorRelationsForSource(sourceKey: string): LearnerMotorRelation[] {
  return nerveGraph.motorRelations.filter(row => row.targetSourceKeys.includes(sourceKey));
}

export function motorRelationsForNerve(nerveKey: string, selectedSide?: string | null): LearnerMotorRelation[] {
  return nerveGraph.motorRelations.filter(row => row.nerveKey === nerveKey
    && (row.scope !== "exact_side_matched_source_instance" || !selectedSide || row.targetSide === selectedSide));
}

export function nerveGraphForLearner() {
  return nerveGraph;
}
