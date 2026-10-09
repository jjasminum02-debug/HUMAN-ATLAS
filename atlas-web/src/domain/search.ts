export interface SearchEntry { id: string; label: string; aliases: string[] }
export interface LearningConceptRecord { id: string; entityType?: string; lookupOnly?: boolean }
export interface SearchMatch { entry: SearchEntry; approximate: boolean; score: number }

const hanScript = /\p{Script=Han}/u;

export function hasHanScript(value: string): boolean {
  return hanScript.test(value);
}

export function withoutHanScript(value: unknown): string {
  return typeof value === 'string' ? value.replace(/\p{Script=Han}+/gu, '[출처 한자 생략]') : '';
}

export function learnerVisibleTerms<T extends Record<string, unknown>>(terms: T[]): T[] {
  return terms.filter((term) => term.script !== 'Hani' &&
    !(typeof term.text === 'string' && hasHanScript(term.text)));
}

function hangulName(value: unknown): string | null {
  return typeof value === 'string' && /[\uac00-\ud7af]/u.test(value) && !hasHanScript(value)
    ? value : null;
}

export function learnerNameProjection(
  id: string,
  fields: { label?: unknown; korean?: unknown; english?: unknown },
  fallback: { korean?: unknown; english?: unknown; latin?: unknown } = {},
) {
  const koTraditional = hangulName(fields.label);
  const koModern = hangulName(fields.korean);
  const en = typeof fields.english === 'string' && fields.english.length > 0 && !hasHanScript(fields.english)
    ? fields.english
    : typeof fallback.english === 'string' && !hasHanScript(fallback.english) ? fallback.english : '';
  const fallbackKorean = hangulName(fallback.korean);
  const latin = typeof fallback.latin === 'string' && fallback.latin.length > 0 && !hasHanScript(fallback.latin)
    ? fallback.latin : '';
  const label = koTraditional ?? koModern ?? fallbackKorean ?? (en || latin || id);
  return { label, koTraditional, koModern, en };
}

export function learnerSearchEntry(id: string, label: string, candidates: unknown[]): SearchEntry {
  const safeLabel = hasHanScript(label) ? id : label;
  const aliases = candidates.filter((value): value is string =>
    typeof value === 'string' && value.trim().length > 0 && !hasHanScript(value));
  return { id, label: safeLabel, aliases };
}

export function mergeLearningConcepts<T extends { id: string }, O extends LearningConceptRecord>(
  canonical: T[], overlay: O[],
): (T | O)[] {
  const ids = new Set(canonical.map((row) => row.id));
  return [...canonical, ...overlay.filter((row) =>
    !ids.has(row.id) && (row.lookupOnly === true || row.entityType === 'muscle_part'),
  )];
}
export function normalize(value: string): string {
  return value.normalize('NFC').toLocaleLowerCase().replace(/[\s·_\-().]/g, '');
}
// Restricted Latin typo tolerance; Korean short queries never use fuzzy matching.
export function distance(a: string, b: string): number {
  // Optimal-string-alignment distance needs only two prior rows, including
  // adjacent transpositions. Keep the shorter term on the allocated axis.
  if (a.length < b.length) [a, b] = [b, a];
  let older = new Uint32Array(b.length + 1);
  let previous = Uint32Array.from({ length: b.length + 1 }, (_, i) => i);
  let current = new Uint32Array(b.length + 1);
  for (let i = 1; i <= a.length; i++) {
    current[0] = i;
    for (let j = 1; j <= b.length; j++) {
      current[j] = Math.min(previous[j] + 1, current[j - 1] + 1,
        previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1])
        current[j] = Math.min(current[j], older[j - 2] + 1);
    }
    [older, previous, current] = [previous, current, older];
  }
  return previous[b.length];
}
export function searchEntries(entries: SearchEntry[], query: string): SearchMatch[] {
  const q = normalize(query);
  if (!q) return entries.map(entry => ({ entry, approximate: false, score: 0 }));
  return entries.flatMap(entry => {
    const terms = [entry.label, ...entry.aliases].map(normalize);
    const score = terms.some(t => t === q) ? 0 : terms.some(t => t.startsWith(q)) ? 1 : terms.some(t => t.includes(q)) ? 2 :
      /^[a-z]{5,}$/.test(q) && terms.some(t => {
        const candidate = t.replace(/muscle$/, ''), tolerance = q.length >= 9 ? 2 : 1;
        return Math.abs(candidate.length - q.length) <= tolerance && distance(candidate, q) <= tolerance;
      }) ? 3 : 99;
    return score === 99 ? [] : [{ entry, approximate: score === 3, score }];
  }).sort((a,b) => a.score - b.score || a.entry.label.localeCompare(b.entry.label, 'ko'));
}
