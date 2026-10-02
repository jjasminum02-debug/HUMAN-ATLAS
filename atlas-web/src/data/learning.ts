import learnerCardRuntime from "../../../atlas-data/terminology/learner-card-runtime.json";
import learnerMotionRuntime from "./learnerMotionRuntime.generated.ts";
import { displayTerms, termText, type PilotCatalog } from "./catalog";
import { learnerNameProjection, learnerSearchEntry, learnerVisibleTerms, mergeLearningConcepts, searchEntries, type SearchEntry } from "../domain/search";
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
  const selector = conceptId ?? sourceKey;
  const projected = selector ? motionRuntime.actions[selector] ?? [] : [];
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
  if (conceptId || !sourceKey) return displayRows;
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
  return cardRuntime.nerveLearning[englishName] ?? null;
}
