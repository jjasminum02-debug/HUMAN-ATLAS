import contexts from '../../../../atlas-data/terminology/learner-attachment-context.json' with { type: 'json' };
import type { AttachmentContexts } from '../../domain/sourceAttachments.ts';
import type { RuntimeStructureRecord } from './integration.ts';
type RegionalRow = Pick<RuntimeStructureRecord, 'sourceKey' | 'names' | 'regionIds' | 'localDisplayEligible'> & Partial<Pick<RuntimeStructureRecord, 'kind' | 'defaultVisible'>>;

export function attachmentBoneKeys(sourceKey: string, role?: 'origin' | 'insertion'): string[] {
  const entry = (contexts as AttachmentContexts)[sourceKey];
  return entry ? [...new Set(role ? entry[role] : [...entry.origin, ...entry.insertion])] : [];
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
