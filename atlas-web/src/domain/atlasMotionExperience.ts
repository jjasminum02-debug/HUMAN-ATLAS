import type { LearnerMotionActionOption } from "./motionLearning.ts";

export type MotionLearningIntent = NonNullable<LearnerMotionActionOption["learningIntent"]>;

export function motionLearningIntent(option: Pick<LearnerMotionActionOption, "candidate" | "learningIntent"> | null | undefined): MotionLearningIntent {
  if (!option) return "text_only";
  if (option.learningIntent) return option.learningIntent;
  // An unclassified source pose never becomes muscle function just because it can play.
  return option.candidate ? "posture_observation" : "text_only";
}

/** Prefer a verified action, then its text, before offering unrelated joint context. */
export function preferredMotionAction<T extends { candidate: LearnerMotionActionOption["candidate"]; learningIntent?: MotionLearningIntent }>(options: readonly T[]): T | undefined {
  return options.find(option => option.candidate && motionLearningIntent(option) === "muscle_action")
    ?? options.find(option => motionLearningIntent(option) === "muscle_action")
    ?? options.find(option => option.candidate && motionLearningIntent(option) === "bone_motion")
    ?? options.find(option => option.candidate) ?? options[0];
}

/** Remove editorial observation wording, retaining anatomical part/start-range qualifications. */
export function motionActionLabel(label: string): string {
  return label.replace(/\s*자세에서\s*(?:관찰|살펴보기)/g, "")
    .replace(/\s*자세\s*관찰/g, "").replace(/\s+관찰(?=\s|$)/g, "")
    .replace(/\s+/g, " ").trim();
}

export function motionLearningTitle(intent: MotionLearningIntent): string {
  return intent === "muscle_action" ? "근육의 작용" : intent === "bone_motion" ? "뼈와 관절의 움직임"
    : intent === "posture_observation" ? "관절 움직임과 주변 구조" : "작용 설명";
}

export function motionPhaseLabel(phase: "action" | "return" | "rest" | "held", label: string): string {
  return phase === "action" ? label : phase === "return" ? "처음 자세로 복귀"
    : phase === "held" ? "선택한 자세" : "처음 자세";
}

export interface MotionLibrarySubject {
  sourceKey: string;
  name: string;
  side: string | null;
  regionIds: readonly string[];
  action: LearnerMotionActionOption;
}
export interface MotionLibraryEntry { label: string; subjects: MotionLibrarySubject[] }

/** A region's action library contains playable muscle actions, never passive poses or candidates. */
export function buildMotionActionLibrary(subjects: readonly MotionLibrarySubject[]): MotionLibraryEntry[] {
  const entries = new Map<string, MotionLibraryEntry>();
  for (const subject of subjects) {
    if (!subject.action.candidate || motionLearningIntent(subject.action) !== "muscle_action") continue;
    const label = motionActionLabel(subject.action.label);
    const entry = entries.get(label) ?? { label, subjects: [] };
    if (!entry.subjects.some(row => row.sourceKey === subject.sourceKey && row.action.id === subject.action.id)) entry.subjects.push(subject);
    entries.set(label, entry);
  }
  return [...entries.values()].sort((a, b) => a.label.localeCompare(b.label, "ko"));
}

/** Colour emphasis teaches the action/reset phases; it is not physiological activation. */
export function muscleActionEmphasis(phase: "action" | "return" | "rest" | "held", poseFraction: number): number | null {
  if (phase !== "action" && phase !== "return") return null;
  const fraction = Math.max(0, Math.min(1, Number.isFinite(poseFraction) ? poseFraction : 0));
  const x = phase === "action" ? Math.min(1, fraction / 0.15) : fraction;
  return x * x * (3 - 2 * x);
}
