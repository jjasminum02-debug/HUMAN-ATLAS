export type NerveDisplayName = { koModern: string; koTraditional: string };
type NameableNerve = {
  key: string;
  sourceNativeEnglishName: string | null;
  names: { en: string; koModern: string; koTraditional: string };
  searchTerms: string[];
};

/** Learner labels overlay native identity; it grants no new branch, supply or geometry. */
export function withNerveDisplayNames<T extends NameableNerve>(
  concepts: readonly T[], displayNames: Record<string, NerveDisplayName>,
): T[] {
  return concepts.map(concept => {
    const display = concept.sourceNativeEnglishName && displayNames[concept.sourceNativeEnglishName];
    if (!display) return concept;
    return {
      ...concept,
      names: { ...concept.names, ...display },
      searchTerms: [...new Set([...concept.searchTerms, display.koModern, display.koTraditional])],
    };
  });
}
