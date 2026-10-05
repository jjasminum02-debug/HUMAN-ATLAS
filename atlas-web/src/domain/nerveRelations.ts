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
