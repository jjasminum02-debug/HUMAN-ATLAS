import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
export function layerAvailable(row: RuntimeStructureRecord, view: BodyView) {
  return row.kind === 'bone' ? view.bones : row.kind === 'muscle' ? view.muscles
    : row.kind === 'nerve' && Boolean(view.nerves) && row.nerve?.poseId === view.poseId;
}
/** Selection, highlights and restore never override a user layer-off or hidden structure. */
export function demandedStructureKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const regions = view.regionIds ?? (view.region ? [view.region] : []);
  return rows.filter(r => !view.hiddenSourceKeys?.includes(r.sourceKey) && r.localDisplayEligible
    && (r.defaultVisible || r.sourceKey === view.selectedId) && layerAvailable(r, view)
    && (!regions.length || r.regionIds.some(id => regions.includes(id)))
    && (!view.isolate || !view.selectedId || r.sourceKey === view.selectedId)).map(r => r.sourceKey);
}
export function innervationHighlightKeys(rows: RuntimeStructureRecord[], view: BodyView, visibleKeys: ReadonlySet<string>) {
  const selected = rows.find(r => r.sourceKey === view.selectedId);
  if (!view.highlightInnervation || selected?.kind !== 'nerve' || !visibleKeys.has(selected.sourceKey)) return [];
  return selected.nerve!.muscleKeys.filter(key => visibleKeys.has(key));
}
