/** Field-level AI evidence types and learner-safe projection.
 * Internal evidence/review codes deliberately do not appear in the projection type.
 */
export type EvidenceState = "unresearched" | "single_source" | "cross_checked" | "conflicted" | "unavailable";
export type GeometryState = "absent" | "context" | "illustrative" | "model_validated";
export type MotionState = "absent" | "text_ready" | "clip_draft" | "educational_ready";
export type EvidenceAccessMethod = "publisher_full_text" | "repository_full_text" | "secondary_full_text" | "abstract" | "metadata" | "search_index" | "legacy_record" | "synthetic_fixture";
export type EvidenceTextAccess = "full_text_opened" | "partial_text_opened" | "abstract_only" | "metadata_only" | "index_only" | "legacy_record" | "fixture_only" | "unavailable";

export interface AiEvidenceSource {
  id: string;
  underlyingWorkId: string;
  title: string;
  url: string;
  editionStatus: "verified" | "not_exposed" | "unknown";
  edition: string | null;
  accessedOn: string;
  accessMethod: EvidenceAccessMethod;
  textAccess: EvidenceTextAccess;
  sourceHash: string;
  fixtureOnly?: boolean;
}

export interface AiEvidenceRecord {
  id: string;
  sourceId: string;
  locator: string;
  accessedOn: string;
  accessMethod: EvidenceAccessMethod;
  textAccess: EvidenceTextAccess;
  excerptHash?: string | null;
  supportsClaimIds: string[];
  evidenceHash: string;
}

export interface AiFieldClaim {
  id: string;
  value: unknown;
  valueHash: string;
  evidenceIds: string[];
  attribution: "ai_structured" | "ai_source_summary" | "source_paraphrase" | "source_quote" | "legacy_summary_migration";
}

export interface AiEvidenceField {
  id: string;
  subjectId: string;
  field: string;
  evidenceState: EvidenceState;
  claims: AiFieldClaim[];
  sources: AiEvidenceSource[];
  evidence: AiEvidenceRecord[];
  unavailableReason?: string;
  geometryState: GeometryState;
  motionState: MotionState;
}

export interface LearnerEvidenceCitation {
  title: string;
  url: string;
  edition: string | null;
  locator: string;
}

export interface LearnerFieldAlternative {
  text: string;
  sources: LearnerEvidenceCitation[];
}

/**
 * This is the only field-evidence shape intended for learner components.
 * It contains no evidenceState, geometryState, motionState, claim ID, or JSON blob.
 */
export interface LearnerFieldProjection {
  text: string | null;
  note: string | null;
  alternatives: LearnerFieldAlternative[];
  sources: LearnerEvidenceCitation[];
  quizEligible: boolean;
}

function claimText(claim: AiFieldClaim): string | null {
  return typeof claim.value === "string" && claim.value.trim().length > 0 ? claim.value : null;
}

function citationsForClaims(item: AiEvidenceField, claims: readonly AiFieldClaim[]): LearnerEvidenceCitation[] {
  const evidenceIds = new Set(claims.flatMap((claim) => claim.evidenceIds));
  const sourceById = new Map(item.sources.map((source) => [source.id, source]));
  const citations: LearnerEvidenceCitation[] = [];
  for (const evidence of item.evidence) {
    if (!evidenceIds.has(evidence.id)) continue;
    const source = sourceById.get(evidence.sourceId);
    if (!source) continue;
    citations.push({ title: source.title, url: source.url, edition: source.edition, locator: evidence.locator });
  }
  return citations.filter((citation, index) => citations.findIndex((candidate) =>
    candidate.url === citation.url && candidate.locator === citation.locator,
  ) === index);
}

function uniqueClaims(claims: readonly AiFieldClaim[]): AiFieldClaim[] {
  const seen = new Set<string>();
  return claims.filter((claim) => {
    if (seen.has(claim.valueHash)) return false;
    seen.add(claim.valueHash);
    return true;
  });
}

export function projectAiEvidenceField(item: AiEvidenceField): LearnerFieldProjection {
  const claims = uniqueClaims(item.claims);
  const sourceRows = citationsForClaims(item, item.claims);
  const empty = (note: string): LearnerFieldProjection => ({ text: null, note, alternatives: [], sources: sourceRows, quizEligible: false });

  switch (item.evidenceState) {
    case "cross_checked": {
      const text = claims.length === 1 ? claimText(claims[0]) : null;
      return text
        ? { text, note: "여러 독립 자료에서 대조한 설명입니다. 사람의 해부학 검토와 3D 위치 검토는 별도입니다.", alternatives: [], sources: sourceRows, quizEligible: true }
        : empty("확인한 문장을 학습 화면에 표시할 수 없습니다.");
    }
    case "single_source": {
      const text = claims.length === 1 ? claimText(claims[0]) : null;
      return text
        ? { text, note: "한 자료를 바탕으로 한 설명입니다. 다른 자료와의 대조 범위는 출처를 열어 확인해 주세요.", alternatives: [], sources: sourceRows, quizEligible: false }
        : empty("확인한 문장을 학습 화면에 표시할 수 없습니다.");
    }
    case "conflicted": {
      const alternatives = claims.flatMap((claim) => {
        const text = claimText(claim);
        return text ? [{ text, sources: citationsForClaims(item, [claim]) }] : [];
      });
      return { text: null, note: "자료에 차이가 있어 하나의 답으로 정리하지 않았습니다.", alternatives, sources: sourceRows, quizEligible: false };
    }
    case "unavailable":
      return empty("이 내용을 확인할 수 있는 원문 근거를 확보하지 못했습니다.");
    case "unresearched":
      return empty("이 설명은 아직 자료를 대조하지 않았습니다.");
  }
}

export function emptyLearnerProjection(text: string): LearnerFieldProjection {
  return { text, note: null, alternatives: [], sources: [], quizEligible: false };
}
