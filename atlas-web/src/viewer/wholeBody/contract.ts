export interface LocalDisplayDecision {
  beforeDefaultVisible: boolean; afterDefaultVisible: boolean; state: 'allowed' | 'held';
  sourceSha256: string; integrityHolds: string[]; evidenceIds: string[];
  retainedHoldReasons: string[]; bindingState: string; publicRedistribution: 'held'; humanReviewed: false;
  basis: string;
}
export interface BodyAsset {
  localDisplay?: LocalDisplayDecision; publicRedistribution?: 'held'; sourcePackage?: string;
  id: string; nodeId: string; sourceSha256: string; regions: string[];
  side: string | null; layer: 'bone' | 'muscle'; defaultVisible: boolean; supplement: boolean;
  pickState: string; stableIds: string[]; holdReasons: string[]; humanReviewed: boolean;
  bounds: [number[], number[]];
}
export interface BodyChunk { id: string; url: string; sha256: string; bytes: number; assets: BodyAsset[] }
export interface BodyManifest { version: number; revision?: string; localOnly: boolean; publicRedistribution: string; frame: string; unit: string; lodLevels: number; chunks: BodyChunk[] }
export interface BodyView { attachmentObservation?: { sourceKey: string; role: 'origin' | 'insertion' } | null; focusObservation?: boolean; nerveConceptMuscleKeys?: string[]; nerves?: boolean; poseId?: string; highlightInnervation?: boolean; observeNerves?: boolean; region: string | null; regionIds?: string[]; bones: boolean; muscles: boolean; supplements: boolean; selectedId: string | null; selectedIds?: string[]; dim: boolean; isolate?: boolean; selectedPresentation?: 'normal' | 'translucent' | 'hidden'; hiddenSourceKeys?: string[]; translucentSourceKeys?: string[];
  /** V1 layers: fascia/joint layers, muscle depth split, and per-layer opacity (0.1-1). */
  fascia?: boolean; joints?: boolean; superficialMuscles?: boolean; deepMuscles?: boolean; layerOpacity?: Partial<Record<LayerId, number>>;
  /** Q2-1: arteries, veins and heart. */
  vessels?: boolean }
export type LayerId = 'fascia' | 'superficialMuscle' | 'deepMuscle' | 'joint' | 'bone' | 'nerve' | 'vessel';
export function visible(a: BodyAsset, view: BodyView): boolean {
  const regionIds = view.regionIds ?? (view.region ? [view.region] : []);
  return (a.localDisplay ? a.localDisplay.state === 'allowed' && a.defaultVisible : (a.defaultVisible || (a.supplement && view.supplements && a.pickState === 'source_only_unbound')))
    && !view.hiddenSourceKeys?.some(key => key === a.id || key === a.nodeId || a.stableIds.includes(key))
    && !(view.selectedPresentation === 'hidden' && selected(a, view))
    && (!view.isolate || !view.selectedId || selected(a, view))
    && (a.layer === 'bone' ? view.bones : view.muscles)
    && (regionIds.length === 0 || regionIds.some((regionId) => a.regions.includes(regionId)));
}
export function pickable(a: BodyAsset): boolean {
  return ['left', 'right', 'midline'].includes(a.side ?? '') && a.defaultVisible && a.pickState === 'existing_binding_unreviewed' && a.holdReasons.length === 0 && a.stableIds.length > 0;
}

/** Presentation isolation cannot grant a source-only/held asset a learner binding. */
export function selected(a: BodyAsset, view: BodyView): boolean {
  return pickable(a) && a.stableIds.some(id => (view.selectedIds ?? [view.selectedId]).includes(id));
}
