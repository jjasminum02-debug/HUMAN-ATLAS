import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import { attachmentBoneKeys, inRegionalScene, regionalAttachmentBoneKeys } from './regionalContext.ts';
export function layerAvailable(row: RuntimeStructureRecord, view: BodyView) {
  return row.kind === 'bone' ? view.bones : row.kind === 'muscle' ? view.muscles
    : row.kind === 'nerve' && Boolean(view.nerves) && row.nerve?.poseId === view.poseId;
}
/** Selection, highlights and restore never override a user layer-off or hidden structure. */
export function observationContextKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const selection = rows.find(r => r.sourceKey === view.selectedId);
  if (!selection) return [];
  const related = new Set([selection.sourceKey, ...attachmentBoneKeys(selection.sourceKey),
    ...(selection.nerve?.muscleKeys ?? []), ...(view.nerveConceptMuscleKeys ?? [])]);
  return rows.filter(r => r.localDisplayEligible && (r.defaultVisible || r.sourceKey === selection.sourceKey)
    && layerAvailable(r, view) && !view.hiddenSourceKeys?.includes(r.sourceKey)
    && (related.has(r.sourceKey) || (r.kind === 'bone' || r.kind === 'muscle')
      && r.regionIds.some(id => selection.regionIds.includes(id)) && (!r.side || r.side === 'midline' || r.side === selection.side))).map(r => r.sourceKey);
}
/** Broad source region memberships need not make a selected nerve's forearm view fit the legs. */
export function observationFrameKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const context = observationContextKeys(rows, view);
  const selection = rows.find(r => r.sourceKey === view.selectedId);
  if (selection?.kind !== 'nerve') return context;
  const related = [selection.sourceKey, ...(selection.nerve?.muscleKeys ?? []), ...(view.nerveConceptMuscleKeys ?? [])];
  const keys = new Set([...related, ...related.flatMap(key => attachmentBoneKeys(key))]);
  return context.filter(key => keys.has(key));
}
export function demandedStructureKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const regions = view.regionIds ?? (view.region ? [view.region] : []);
  const observation = new Set(view.focusObservation ? observationContextKeys(rows, view) : []);
  const contextBones = regionalAttachmentBoneKeys(rows, regions);
  const selectedNerve = rows.find(r => r.sourceKey === view.selectedId && r.kind === 'nerve');
  const nerveVisible = selectedNerve && layerAvailable(selectedNerve, view) && selectedNerve.localDisplayEligible
    && !view.hiddenSourceKeys?.includes(selectedNerve.sourceKey) && inRegionalScene(selectedNerve, regions, view.selectedId);
  // A literature concept link is context only, never a new geometric nerve branch binding.
  const context = new Set(nerveVisible && view.highlightInnervation ? view.nerveConceptMuscleKeys ?? [] : []);
  return rows.filter(r => !view.hiddenSourceKeys?.includes(r.sourceKey) && r.localDisplayEligible
    && (r.defaultVisible || r.sourceKey === view.selectedId) && layerAvailable(r, view)
    && (view.focusObservation ? observation.has(r.sourceKey) : (inRegionalScene(r, regions, view.selectedId) || r.kind === 'bone' && contextBones.has(r.sourceKey)
      || r.kind === 'muscle' && context.has(r.sourceKey) && r.side === selectedNerve?.side))
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
  if (!layerAvailable(selected, view) || view.hiddenSourceKeys?.includes(selected.sourceKey) || !view.muscles) return [];
  const candidates = new Set([...selected.nerve!.muscleKeys, ...(view.nerveConceptMuscleKeys ?? [])]);
  return rows.filter(r => candidates.has(r.sourceKey) && r.kind === 'muscle' && r.localDisplayEligible
    && r.side === selected.side && visibleKeys.has(r.sourceKey) && !view.hiddenSourceKeys?.includes(r.sourceKey)).map(r => r.sourceKey);
}
