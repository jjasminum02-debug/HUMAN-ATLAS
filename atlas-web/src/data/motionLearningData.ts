import learnerMotionRuntime from "./learnerMotionRuntime.generated.ts";
import learnerCardRuntime from "../../../atlas-data/terminology/learner-card-runtime.json" with { type: "json" };
import { learnerActionAppliesToSide } from "../domain/learnerActionText.ts";
import { resolveLearnerMotionCandidate, type LearnerMotionActionOption, type LearnerActionText } from "../domain/motionLearning.ts";

// Loaded only with the motion feature; names, attachments and the shared scene stay independent.
type CardAction = { conceptId: string; key: string; label: string; explanation: string; sideApplicability: "left" | "right" | null };
const actionsByConcept = new Map<string, CardAction[]>();
for (const action of learnerCardRuntime.actions as CardAction[]) {
  const rows = actionsByConcept.get(action.conceptId) ?? [];
  rows.push(action); actionsByConcept.set(action.conceptId, rows);
}
type LearnerMotionRuntime = {
  schemaVersion: "learner-motion-runtime-v1";
  wave1Actions: Record<string, LearnerMotionActionOption[]>;
  actions: Record<string, Array<{
    actionKey: string;
    learnerActionKey: string | null;
    label: string;
    text: LearnerActionText;
    sideApplicability: "left" | "right" | "bilateral" | "midline" | "not_applicable";
    learningIntent?: LearnerMotionActionOption["learningIntent"];
    candidate: LearnerMotionActionOption["candidate"];
  }>>;
};
const motionRuntime = learnerMotionRuntime as unknown as LearnerMotionRuntime;
/** Learner-only action text is preprojected; source/evidence references stay out of this bundle. */
export function motionActionOptionsForLearner(conceptId: string | null, selectedSide?: string | null, sourceKey?: string | null) {
  const selector = sourceKey && motionRuntime.actions[sourceKey]?.length ? sourceKey : conceptId ?? sourceKey;
  const projected = (selector ? motionRuntime.actions[selector] ?? [] : []).filter(row =>
    !row.candidate || !sourceKey || row.candidate.asset.sourceBinding?.subjectSourceKey === sourceKey);
  const wave1Options = sourceKey
    ? (motionRuntime.wave1Actions[sourceKey] ?? []).filter(row =>
      !selectedSide || row.sideApplicability === "bilateral" || row.sideApplicability === "midline" || row.sideApplicability === selectedSide)
    : [];
  const displayRows = (actionsByConcept.get(conceptId ?? '') ?? []).filter((row) =>
    learnerActionAppliesToSide(row.sideApplicability, selectedSide)).map((row) => {
    return {
      id: row.key,
      label: row.label,
      text: { label: row.label, explanation: row.explanation },
      sideApplicability: row.sideApplicability,
      learningIntent: "muscle_action" as const,
      candidate: resolveLearnerMotionCandidate(row.key, selectedSide, projected),
    };
  });
  if (conceptId && selector === conceptId) return [...displayRows, ...wave1Options];
  if (!sourceKey) return displayRows;
  // A source-only action is reachable by exact sourceKey; no canonical ID or alias is invented.
  const sourceRows = projected.filter((row) => learnerActionAppliesToSide(row.sideApplicability, selectedSide)).map((row) => ({
    id: row.actionKey,
    label: row.label,
    text: { label: row.text.label, explanation: row.text.explanation },
    sideApplicability: row.sideApplicability === "left" || row.sideApplicability === "right" ? row.sideApplicability : null,
    learningIntent: row.learningIntent ?? "posture_observation" as const,
    candidate: row.candidate,
  }));
  const byId = new Map([...sourceRows, ...wave1Options].map(row => [row.id, row]));
  return [...byId.values()];
}
