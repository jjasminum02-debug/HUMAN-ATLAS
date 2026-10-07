type NameRow = { id: string };
type ActionRow = { conceptId: string };
type NerveRow = { key: string; sourceNativeEnglishName: string | null; names: { en: string } };
type RelationRow = { nerveKey: string; targetSourceKeys: string[] };

function append<T>(map: Map<string, T[]>, key: string, row: T) {
  const rows = map.get(key);
  if (rows) rows.push(row); else map.set(key, [row]);
}
function unique<T>(map: Map<string, T | null>, key: string, row: T) {
  map.set(key, map.has(key) ? null : row);
}

/** Index immutable learner data once. Preserve first-match, order and ambiguous-name semantics. */
export function createLearnerLookupIndex<N extends NameRow, A extends ActionRow, C extends NerveRow, R extends RelationRow>(
  names: readonly N[], actions: readonly A[], nerves: readonly C[], relations: readonly R[],
) {
  const namesById = new Map<string, N>(), actionsByConcept = new Map<string, A[]>();
  const nervesByKey = new Map<string, C>();
  const nervesByNativeName = new Map<string, C | null>(), nervesByEnglishName = new Map<string, C | null>();
  const relationsByNerve = new Map<string, R[]>(), relationsBySource = new Map<string, R[]>();
  for (const row of names) if (!namesById.has(row.id)) namesById.set(row.id, row);
  for (const row of actions) append(actionsByConcept, row.conceptId, row);
  for (const row of nerves) {
    if (!nervesByKey.has(row.key)) nervesByKey.set(row.key, row);
    if (row.sourceNativeEnglishName !== null) unique(nervesByNativeName, row.sourceNativeEnglishName, row);
    unique(nervesByEnglishName, row.names.en, row);
  }
  for (const row of relations) {
    append(relationsByNerve, row.nerveKey, row);
    for (const sourceKey of new Set(row.targetSourceKeys)) append(relationsBySource, sourceKey, row);
  }
  return { namesById, actionsByConcept, nervesByKey, relationsByNerve, relationsBySource,
    nerveForExactName: (name: string) => nervesByNativeName.has(name)
      ? nervesByNativeName.get(name) ?? null : nervesByEnglishName.get(name) ?? null };
}
