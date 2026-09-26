import summaries from "../../../atlas-data/terminology/learning-structure-summaries.json";
import names from '../../../atlas-data/terminology/learning-names.json';
import { displayTerms, termText, type PilotCatalog } from './catalog';
import { learnerNameProjection, learnerSearchEntry, learnerVisibleTerms, mergeLearningConcepts, searchEntries, withoutHanScript, type SearchEntry } from '../domain/search';
const rawNameSources = names.sources as Record<string, { title: string; url: string | null; locator: string }>;
export const nameSources = Object.fromEntries(Object.entries(rawNameSources).map(([id, source]) => [id, {
  ...source, title: withoutHanScript(source.title), locator: withoutHanScript(source.locator),
}])) as Record<string, { title: string; url: string | null; locator: string }>;
export const vocabulary = names.entries;

export function nameFor(catalog: PilotCatalog, id: string) {
  const entry = vocabulary.find(row => row.id === id);
  const terms = learnerVisibleTerms(displayTerms(catalog, id));
  const projected = learnerNameProjection(id, entry ?? {}, {
    korean: terms.find(term => term.language === 'ko')?.text,
    english: termText(catalog, id, 'en'),
    latin: termText(catalog, id, 'la'),
  });
  return {
    ...projected, sources: entry?.sourceIds ?? [],
  };
}
export function learningConcepts(catalog: PilotCatalog) {
  return mergeLearningConcepts(catalog.concepts, vocabulary);
}
export function findMuscles(catalog: PilotCatalog, query: string) {
  const entries: SearchEntry[] = learningConcepts(catalog).map(concept => {
    const n = nameFor(catalog, concept.id);
    const custom = vocabulary.find(row => row.id === concept.id);
    const terms = learnerVisibleTerms(displayTerms(catalog, concept.id));
    return learnerSearchEntry(concept.id, n.label, [n.koTraditional, n.koModern, n.en, ...custom?.aliases ?? [],
      ...terms.flatMap(t => typeof t.text === 'string' ? [t.text] : [])]);
  });
  return searchEntries(entries, query);
}

export function structureSummary(conceptId: string, role: string) { return summaries.find(row => row.conceptId === conceptId && row.role === role)?.summary; }
