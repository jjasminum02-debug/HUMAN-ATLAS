import contexts from '../../../../atlas-data/terminology/learner-attachment-context.json' with { type: 'json' };
import type { AttachmentContexts } from '../../domain/sourceAttachments.ts';
import cards from '../../../../atlas-data/terminology/learner-card-runtime.json' with { type: 'json' };
import { namedAttachmentBones } from '../../domain/attachmentTextContext.ts';
import type { RuntimeStructureRecord } from './integration.ts';
type RegionalRow = Pick<RuntimeStructureRecord, 'sourceKey' | 'names' | 'regionIds' | 'localDisplayEligible'> & Partial<Pick<RuntimeStructureRecord, 'kind' | 'defaultVisible'>>;

const resolved = new WeakMap<RuntimeStructureRecord[], Map<string, string[]>>();
export function attachmentBoneKeys(sourceKey: string, role?: 'origin' | 'insertion', rows?: RuntimeStructureRecord[]): string[] {
  const cacheKey = `${sourceKey}:${role ?? 'both'}`;
  const cached = rows && resolved.get(rows)?.get(cacheKey);
  if (cached) return [...cached];
  const entry = (contexts as AttachmentContexts)[sourceKey];
  const source = rows?.find(r => r.sourceKey === sourceKey && r.kind === 'muscle' && r.localDisplayEligible);
  const keys = new Set<string>();
  for (const field of role ? [role] : ['origin', 'insertion'] as const) {
    for (const key of entry?.[field] ?? []) keys.add(key);
    // Reuse exact source text (or its existing canonical card), without inheriting another part's prose.
    const text = source ? attachmentText(source, field) : null;
    if (text && source && rows) for (const key of namedAttachmentBones(text, source.side,
      rows.filter(r => r.sourceKey.split('-')[1] === source.sourceKey.split('-')[1]), { wholeBoneContext: true }).keys) keys.add(key);
  }
  const result = [...keys];
  if (rows) { let cache = resolved.get(rows); if (!cache) { cache = new Map(); resolved.set(rows, cache); } cache.set(cacheKey, result); }
  return result;
}
export function attachmentText(source: RuntimeStructureRecord, role: 'origin' | 'insertion'): string | null {
  const structure = cards.structure as { bySource: Record<string, Partial<Record<'origin' | 'insertion', string>>>;
    byConcept: Record<string, Partial<Record<'origin' | 'insertion', string>>> };
  const text = structure.bySource[source.sourceKey]?.[role] ?? structure.byConcept[source.haConceptId ?? '']?.[role];
  return text && !/^(?:설명 정리 중|자료 없음)$/.test(text) ? text : null;
}

/** Regional default scenes do not present the frozen full-spine Rotatores group as a neck-only surface. */
export function inRegionalScene(row: RegionalRow, regions: string[], selectedId: string | null) {
  return (!regions.length || row.regionIds.some(id => regions.includes(id)))
    && (row.names.en !== 'Rotatores' || !regions.length || regions.includes('back') || row.sourceKey === selectedId);
}

/** Explicit source-scoped principal attachments supply existing whole bones, without promoting a held asset. */
export function regionalAttachmentBoneKeys(rows: RegionalRow[], regions: string[]) {
  if (!regions.length) return new Set<string>();
  return new Set(rows.filter(r => r.kind === 'muscle' && r.localDisplayEligible && r.defaultVisible
    && inRegionalScene(r, regions, null)).flatMap(r => attachmentBoneKeys(r.sourceKey)));
}
export function inRegionalRoute(row: RegionalRow, rows: RegionalRow[], regions: string[]) {
  return inRegionalScene(row, regions, row.sourceKey) || row.kind === 'bone' && regionalAttachmentBoneKeys(rows, regions).has(row.sourceKey);
}
