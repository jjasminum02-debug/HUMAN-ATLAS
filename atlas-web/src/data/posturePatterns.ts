// 4-2 step 10: posture patterns (Janda's crossed syndromes). Data: atlas-data/runtime/posture-patterns.json
// (built by atlas-data/pipeline/posture_patterns.py; sources and held muscles in atlas-data/anatomy/posture-pattern-checks.json).
export interface PosturePattern { id: string; name: string; en: string; signs: string; short: string[]; weak: string[]; note?: string }
export interface PosturePatternsFile { schemaVersion: 1; patterns: PosturePattern[] }

/** Source keys (both sides) of the pattern's short and weak muscles among the shown rows. */
export function patternKeys(pattern: PosturePattern, rows: Iterable<{ sourceKey: string; names: { en: string }; localDisplayEligible?: boolean }>) {
  const short = new Set(pattern.short), weak = new Set(pattern.weak), out = { short: [] as string[], weak: [] as string[] };
  for (const row of rows) if (row.localDisplayEligible !== false) {
    if (short.has(row.names.en)) out.short.push(row.sourceKey);
    else if (weak.has(row.names.en)) out.weak.push(row.sourceKey);
  }
  return out;
}

/** Patterns naming this muscle, with the side it is on. */
export type PatternHit = { pattern: PosturePattern; role: 'short' | 'weak' };
export function patternsFor(file: PosturePatternsFile | null, englishName: string) {
  const hits: PatternHit[] = [];
  for (const p of file?.patterns ?? []) {
    if (p.short.includes(englishName)) hits.push({ pattern: p, role: 'short' });
    else if (p.weak.includes(englishName)) hits.push({ pattern: p, role: 'weak' });
  }
  return hits;
}
