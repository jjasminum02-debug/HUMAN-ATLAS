import { emptyLearnerProjection, type LearnerFieldProjection } from "./aiEvidence.ts";

export interface LegacyLearningSummary {
  conceptId: string;
  role: string;
  summary: string;
  attribution?: string;
  humanReviewed?: boolean;
  sourceClaimIds?: string[];
  sourceClaimHash?: string;
}

/** Preserve the old display text when no migrated field overlay exists.
 * This path does not upgrade its evidence or human-review state.
 */
export function projectLegacySummary(summary: LegacyLearningSummary | undefined): LearnerFieldProjection | null {
  if (!summary || typeof summary.summary !== "string" || summary.summary.trim().length === 0) return null;
  return emptyLearnerProjection(summary.summary);
}
