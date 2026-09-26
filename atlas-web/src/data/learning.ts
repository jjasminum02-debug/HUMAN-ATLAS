import summaries from "../../../atlas-data/terminology/learning-structure-summaries.json";
import names from '../../../atlas-data/terminology/learning-names.json';
import { displayTerms, termText, type PilotCatalog } from './catalog';
import { mergeLearningConcepts, searchEntries, type SearchEntry } from '../domain/search';
export const nameSources = names.sources as Record<string, { title: string; url: string | null; locator: string }>;
export const vocabulary = names.entries;
export function nameFor(catalog: PilotCatalog, id: string) {
  const entry = vocabulary.find(row => row.id === id);
  return {
    label: entry?.label ?? termText(catalog, id, 'ko') ?? termText(catalog, id, 'en') ?? '이름 준비 중',
    korean: entry?.korean ?? '', english: entry?.english ?? termText(catalog, id, 'en') ?? '',
    hanja: entry?.hanja ?? '', sources: entry?.sourceIds ?? [],
    hanjaNote: entry?.hanjaNote ?? '',
  };
}
export function learningConcepts(catalog: PilotCatalog) {
  return mergeLearningConcepts(catalog.concepts, vocabulary);
}
export function findMuscles(catalog: PilotCatalog, query: string) {
  const entries: SearchEntry[] = learningConcepts(catalog).map(concept => {
    const n = nameFor(catalog, concept.id);
    const custom = vocabulary.find(row => row.id === concept.id);
    return { id: concept.id, label: n.label, aliases: [n.korean, n.english, n.hanja, ...custom?.aliases ?? [],
      ...displayTerms(catalog, concept.id).flatMap(t => typeof t.text === 'string' ? [t.text] : [])].filter(Boolean) };
  });
  return searchEntries(entries, query);
}

export function structureSummary(conceptId: string, role: string) { return summaries.find(row => row.conceptId === conceptId && row.role === role)?.summary; }
