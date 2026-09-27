import { projectAiEvidenceField, type AiEvidenceField } from "./aiEvidence.ts";
import { projectLegacySummary, type LegacyLearningSummary } from "./legacyEvidenceAdapter.ts";

/** Plain learner sentence only. Source, alternative, and review details stay internal. */
export function learnerStructureText(
  aiField: AiEvidenceField | undefined,
  legacy: LegacyLearningSummary | undefined,
): string | null {
  if (aiField?.evidenceState === "conflicted") return "설명 정리 중";
  const projection = aiField ? projectAiEvidenceField(aiField) : projectLegacySummary(legacy);
  if (projection?.text) return projection.text;
  if (aiField && aiField.claims.length > 1) return "설명 정리 중";
  return null;
}
