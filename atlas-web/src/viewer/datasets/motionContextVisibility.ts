import type { BodyView } from '../wholeBody/contract.ts';
import type { RuntimeStructureRecord } from './integration.ts';
import type { MotionFrameMember } from './motionFrameContext.ts';
import { layerAvailable } from './presentation.ts';

/** One visibility contract for all motion packages, including posture observations. */
export function motionContextVisibility(
  members: readonly MotionFrameMember[], frameKeys: readonly string[],
  rowFor: (key: string) => RuntimeStructureRecord | undefined, view: BodyView,
) {
  const packageKeys = new Set(members.map(member => member.sourceKey));
  const candidates = [...new Set([...packageKeys, ...frameKeys.filter(key => rowFor(key)?.kind === 'bone')])];
  return candidates.filter(key => {
    const row = rowFor(key);
    return Boolean(row && (row.kind === 'bone' || row.kind === 'muscle') && row.localDisplayEligible
      && !row.hardHoldReasons.length && !row.sourceHiddenStatePreserved.hideViewport
      && (row.defaultVisible || key === view.selectedId) && layerAvailable(row, view)
      && !view.hiddenSourceKeys?.includes(key) && !(key === view.selectedId && view.selectedPresentation === 'hidden')
      && (!view.isolate || key === view.selectedId));
  });
}
