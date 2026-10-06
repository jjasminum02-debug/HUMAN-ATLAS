export type NerveConceptNameRow = {
  key: string;
  names: { en: string };
  sourceNativeEnglishName: string | null;
};

export type MotorRelationRow = {
  nerveKey: string;
  targetSourceKeys: string[];
  targetSide: "left" | "right" | null;
  scope: string;
};

export const GENERIC_UNLINKED_NERVE_FUNCTION_CONTEXT =
  "확인된 신경 지배 관계가 있는 경우 아래 운동 연결에서 살펴볼 수 있습니다.";

/** Hide only the repeated generic status sentence; keep every specific explanation visible. */
export function shouldDisplayNerveFunctionContext(
  context: string | null | undefined,
  evidenceClass: string | null | undefined,
): boolean {
  if (!context) return false;
  return !(evidenceClass === "relationship_not_linked"
    && context === GENERIC_UNLINKED_NERVE_FUNCTION_CONTEXT);
}

export function nerveActionRouteLabel(hasPlayableCandidate: boolean): string {
  return hasPlayableCandidate ? '이 근육의 움직임 보기' : '이 근육의 작용 설명 보기';
}

/** Resolve only a unique exact native label, with a unique exact display-name fallback. */
export function conceptForExactNerveName<T extends NerveConceptNameRow>(concepts: readonly T[], englishName: string): T | null {
  const sourceMatches = concepts.filter(row => row.sourceNativeEnglishName === englishName);
  if (sourceMatches.length === 1) return sourceMatches[0];
  if (sourceMatches.length > 1) return null;
  const displayMatches = concepts.filter(row => row.names.en === englishName);
  return displayMatches.length === 1 ? displayMatches[0] : null;
}

/** Exact geometry relations follow the selected side; literature concept relations remain unsided. */
export function relationsForNerve<T extends MotorRelationRow>(relations: readonly T[], nerveKey: string, selectedSide?: string | null): T[] {
  return relations.filter(row => row.nerveKey === nerveKey
    && (row.scope !== "exact_side_matched_source_instance" || !selectedSide || row.targetSide === selectedSide));
}

/** Only explanatory action text and true muscle-action bindings belong beside a nerve relation. */
export function isNerveRelatedActionTextIntent(intent: string | undefined): boolean {
  return intent === "muscle_action" || intent === "text_only";
}
