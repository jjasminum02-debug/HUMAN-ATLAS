import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import { attachmentBoneKeys, inRegionalScene, regionalAttachmentBoneKeys } from './regionalContext.ts';
/** Exact selected muscle/side and existing same-source bones only; no footprint or new binding. */
export function attachmentObservationKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const focus = view.attachmentObservation;
  const muscle = rows.find(r => r.sourceKey === focus?.sourceKey && r.sourceKey === view.selectedId
    && r.kind === 'muscle' && r.localDisplayEligible && r.defaultVisible && !r.hardHoldReasons.length);
  if (!muscle || !focus) return [];
  const keys = new Set(attachmentBoneKeys(muscle.sourceKey, focus.role, rows));
  return rows.filter(r => keys.has(r.sourceKey) && r.kind === 'bone' && r.localDisplayEligible && r.defaultVisible
    && !r.hardHoldReasons.length && !r.sourceHiddenStatePreserved.hideViewport
    && (r.side === muscle.side || r.side === null || r.side === 'midline')
    && r.sourceKey.split('-')[1] === muscle.sourceKey.split('-')[1]
    && layerAvailable(r, view) && !view.hiddenSourceKeys?.includes(r.sourceKey)).map(r => r.sourceKey);
}
const nerveIndexes = new WeakMap<RuntimeStructureRecord[], Map<string, RuntimeStructureRecord>>();
/** Follow only registered same-side static branch links; never infer branches by name/proximity. */
export function nerveCourseKeys(rows: RuntimeStructureRecord[], view: BodyView): string[] {
  let byKey=nerveIndexes.get(rows);
  if(!byKey){byKey=new Map(rows.map(row=>[row.sourceKey,row]));nerveIndexes.set(rows,byKey);}
  const selected=byKey.get(view.selectedId??'');
  if(selected?.kind!=='nerve'||!layerAvailable(selected,view)||view.hiddenSourceKeys?.includes(selected.sourceKey)
    || view.selectedPresentation==='hidden')return [];
  const visited=new Set<string>(),pending=[selected.sourceKey];
  while(pending.length){const key=pending.pop()!;if(visited.has(key))continue;const row=byKey.get(key);
    if(!row||row.kind!=='nerve'||row.side!==selected.side||row.nerve?.poseId!==selected.nerve?.poseId
      || !row.localDisplayEligible||row.hardHoldReasons?.length||row.sourceHiddenStatePreserved?.hideViewport
      || !layerAvailable(row,view)||view.hiddenSourceKeys?.includes(key))continue;
    visited.add(key);pending.push(...row.nerve?.branchKeys??[]);
  }
  return [...visited];
}
export function layerAvailable(row: RuntimeStructureRecord, view: BodyView) {
  return row.kind === 'bone' ? view.bones : row.kind === 'muscle' ? view.muscles
    : row.kind === 'nerve' && Boolean(view.nerves) && row.nerve?.poseId === view.poseId;
}
/** Selection, highlights and restore never override a user layer-off or hidden structure. */
export function observationContextKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const selection = rows.find(r => r.sourceKey === view.selectedId);
  if (!selection) return [];
  if (view.attachmentObservation) {
    const bones = new Set(attachmentObservationKeys(rows, view));
    return rows.filter(r => (r.sourceKey === selection.sourceKey || bones.has(r.sourceKey))
      && layerAvailable(r, view) && !view.hiddenSourceKeys?.includes(r.sourceKey)).map(r => r.sourceKey);
  }
  const related = new Set([...nerveCourseKeys(rows, view), selection.sourceKey, ...attachmentBoneKeys(selection.sourceKey, undefined, rows),
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
  const related = [...nerveCourseKeys(rows, view), selection.sourceKey, ...(selection.nerve?.muscleKeys ?? []), ...(view.nerveConceptMuscleKeys ?? [])];
  const keys = new Set([...related, ...related.flatMap(key => attachmentBoneKeys(key, undefined, rows))]);
  return context.filter(key => keys.has(key));
}
export function demandedStructureKeys(rows: RuntimeStructureRecord[], view: BodyView) {
  const regions = view.regionIds ?? (view.region ? [view.region] : []);
  const observation = new Set(view.focusObservation || view.attachmentObservation ? observationContextKeys(rows, view) : []);
  const contextBones = regionalAttachmentBoneKeys(rows, regions);
  const selectedNerve = rows.find(r => r.sourceKey === view.selectedId && r.kind === 'nerve');
  const nerveVisible = selectedNerve && layerAvailable(selectedNerve, view) && selectedNerve.localDisplayEligible
    && !view.hiddenSourceKeys?.includes(selectedNerve.sourceKey) && inRegionalScene(selectedNerve, regions, view.selectedId);
  // A literature concept link is context only, never a new geometric nerve branch binding.
  const course = new Set(nerveCourseKeys(rows, view));
  const context = new Set(nerveVisible && view.highlightInnervation ? view.nerveConceptMuscleKeys ?? [] : []);
  return rows.filter(r => !view.hiddenSourceKeys?.includes(r.sourceKey) && r.localDisplayEligible
    && (r.defaultVisible || r.sourceKey === view.selectedId) && layerAvailable(r, view)
    && (view.focusObservation || view.attachmentObservation ? observation.has(r.sourceKey) : (course.has(r.sourceKey) || inRegionalScene(r, regions, view.selectedId) || r.kind === 'bone' && contextBones.has(r.sourceKey)
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

/** Focus once when a supported nerve becomes selected/visible; never on orbit or highlight updates. */
export function shouldFocusNerveSelection(rows: RuntimeStructureRecord[], previous: BodyView, next: BodyView) {
  const nerve=rows.find(row=>row.sourceKey===next.selectedId&&row.kind==='nerve');
  return Boolean(nerve && nerve.localDisplayEligible && !nerve.hardHoldReasons?.length
    && !nerve.sourceHiddenStatePreserved?.hideViewport && layerAvailable(nerve,next)
    && !next.hiddenSourceKeys?.includes(nerve.sourceKey) && next.selectedPresentation!=='hidden'
    && (previous.selectedId!==next.selectedId || !previous.nerves || previous.poseId!==next.poseId));
}
