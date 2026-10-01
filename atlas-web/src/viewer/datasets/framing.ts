import { layerAvailable } from './presentation.ts';
import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
/** Camera framing does not make an inspection-only, held or hidden source part of the learner scene. */
export function framingRecords(rows: RuntimeStructureRecord[], view: BodyView, regions: string[]): RuntimeStructureRecord[] {
  return rows.filter(r => r.localDisplayEligible && (r.defaultVisible || r.sourceKey === view.selectedId)
    && !view.hiddenSourceKeys?.includes(r.sourceKey)
    && layerAvailable(r, view)
    && (!regions.length || r.regionIds.some(region => regions.includes(region)))
    // This frozen source is the entire neck/back muscle group. Keep its geometry/route intact,
    // but do not frame the whole spine when the learner explicitly asks to see the neck.
    // Explicit "selection fit" still uses the complete source bounds.
    && !(regions.length === 1 && regions[0] === 'neck' && r.names.en === 'Rotatores'));
}
