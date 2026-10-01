import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import { inRegionalScene, regionalAttachmentBoneKeys } from './regionalContext.ts';
export function layerAvailable(row: RuntimeStructureRecord, view: BodyView) {
  return row.kind === 'bone' ? view.bones : row.kind === 'muscle' ? view.muscles
    : row.kind === 'nerve' && Boolean(view.nerves) && row.nerve?.poseId === view.poseId;
}
/** Selection, highlights and restore never override a user layer-off or hidden structure. */
export function demandedStructureKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const regions = view.regionIds ?? (view.region ? [view.region] : []);
  const contextBones = regionalAttachmentBoneKeys(rows, regions);
  return rows.filter(r => !view.hiddenSourceKeys?.includes(r.sourceKey) && r.localDisplayEligible
    && (r.defaultVisible || r.sourceKey === view.selectedId) && layerAvailable(r, view)
    && (inRegionalScene(r, regions, view.selectedId) || r.kind === 'bone' && contextBones.has(r.sourceKey))
    && (!view.isolate || !view.selectedId || r.sourceKey === view.selectedId)).map(r => r.sourceKey);
}
export function observingNerves(rows: RuntimeStructureRecord[], view: BodyView, visibleKeys: ReadonlySet<string>) {
  const selection = rows.find(r => r.sourceKey === view.selectedId);
  return Boolean(view.observeNerves && (!selection || selection.kind === 'nerve' && visibleKeys.has(selection.sourceKey))
    && rows.some(r => r.kind === 'nerve' && visibleKeys.has(r.sourceKey) && layerAvailable(r, view)));
}
export function innervationHighlightKeys(rows: RuntimeStructureRecord[], view: BodyView, visibleKeys: ReadonlySet<string>) {
  const selected = rows.find(r => r.sourceKey === view.selectedId);
  if (!view.highlightInnervation || selected?.kind !== 'nerve' || !visibleKeys.has(selected.sourceKey)) return [];
  return selected.nerve!.muscleKeys.filter(key => visibleKeys.has(key));
}
