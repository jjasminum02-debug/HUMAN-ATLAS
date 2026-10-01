import learnerCardRuntime from "../../../atlas-data/terminology/learner-card-runtime.json";
import { displayTerms, termText, type PilotCatalog } from "./catalog";
import { learnerNameProjection, learnerSearchEntry, learnerVisibleTerms, mergeLearningConcepts, searchEntries, type SearchEntry } from "../domain/search";
import type { LearnerFieldProjection } from "../domain/aiEvidence";
import { learnerStructureUnavailability } from "../domain/learnerStructureSourceContent";

type LearnerCardRuntime = {
  schemaVersion: "learner-card-runtime-v1";
  names: Array<{ id: string; label: string; korean: string; english: string; aliases: string[]; parentId: string | null; entityType: string; lookupOnly: boolean }>;
  structure: {
    byConcept: Record<string, Partial<Record<"origin" | "insertion", string>>>;
    bySource: Record<string, Partial<Record<"origin" | "insertion", string>>>;
  };
  actions: Array<{ conceptId: string; key: string; label: string; explanation: string; candidateSide: string | null }>;
};

const cardRuntime = learnerCardRuntime as LearnerCardRuntime;
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
export function motionActionOptionsForLearner(conceptId: string) {
  return cardRuntime.actions.filter((row) => row.conceptId === conceptId).map((row) => ({
    id: row.key,
    label: row.label,
    text: { label: row.label, explanation: row.explanation },
    candidateSide: row.candidateSide,
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
