export interface LocalDisplayDecision {
  beforeDefaultVisible: boolean; afterDefaultVisible: boolean; state: 'allowed' | 'held';
  sourceSha256: string; integrityHolds: string[]; evidenceIds: string[];
  retainedHoldReasons: string[]; bindingState: string; publicRedistribution: 'held'; humanReviewed: false;
  basis: string;
}
const contextHolds = new Set(['not_canonical_learner_binding', 'no_canonical_learner_binding', 'human_anatomy_review_not_performed', 'public_redistribution_held']);
export interface BodyAsset {
  localDisplay?: LocalDisplayDecision; publicRedistribution?: 'held'; sourcePackage?: string;
  id: string; nodeId: string; sourceSha256: string; regions: string[];
  side: string | null; layer: 'bone' | 'muscle'; defaultVisible: boolean; supplement: boolean;
  pickState: string; stableIds: string[]; holdReasons: string[]; humanReviewed: boolean;
  bounds: [number[], number[]];
}
export interface BodyChunk { id: string; url: string; sha256: string; bytes: number; assets: BodyAsset[] }
export interface BodyManifest { version: number; revision?: string; localOnly: boolean; publicRedistribution: string; frame: string; unit: string; lodLevels: number; chunks: BodyChunk[] }
export interface BodyView { nerves?: boolean; poseId?: string; highlightInnervation?: boolean; observeNerves?: boolean; region: string | null; regionIds?: string[]; bones: boolean; muscles: boolean; supplements: boolean; selectedId: string | null; selectedIds?: string[]; dim: boolean; isolate?: boolean; selectedPresentation?: 'normal' | 'translucent' | 'hidden'; hiddenSourceKeys?: string[]; translucentSourceKeys?: string[] }
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
export function validateManifest(m: BodyManifest): void {
  if (m.unit !== 'm' || ![1, 2].includes(m.version) || !m.localOnly || m.publicRedistribution !== 'held' || m.lodLevels !== 1 || m.frame !== 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR') throw new Error('Unsupported body contract');
  const ids = new Set<string>();
  for (const c of m.chunks) {
    if (!/^[a-z0-9-]+$/.test(c.id) || c.url !== `/__atlas/body/${c.id}.glb` || !/^[a-f0-9]{64}$/.test(c.sha256)) throw new Error('Invalid chunk');
    for (const a of c.assets) {
      if (ids.has(a.id) || a.nodeId !== `HA-MESH-BP3D4-${a.id}` || (a.pickState === 'source_only_unbound' && a.stableIds.length)) throw new Error('Invalid identity');
      if (a.humanReviewed !== false || (a.holdReasons.some(h => m.version === 1 || !contextHolds.has(h)) && a.defaultVisible) || a.bounds.length !== 2 || a.bounds.some(v => v.length !== 3 || v.some(n => !Number.isFinite(n)))) throw new Error('Invalid source hold or bounds');
      if (m.version === 2) {
        const d = a.localDisplay;
        if (!d || d.sourceSha256 !== a.sourceSha256 || d.afterDefaultVisible !== a.defaultVisible
          || !['allowed', 'held'].includes(d.state) || (d.state === 'allowed') !== a.defaultVisible
          || d.bindingState !== a.pickState || JSON.stringify(d.retainedHoldReasons) !== JSON.stringify(a.holdReasons)
          || d.publicRedistribution !== 'held' || a.publicRedistribution !== 'held' || d.humanReviewed !== false
          || (d.state === 'allowed' && (d.integrityHolds.length > 0 || a.pickState === 'held'))
          || (!d.beforeDefaultVisible && d.afterDefaultVisible && (d.evidenceIds.length < 2 || d.basis !== 'verified_local_source_context_only'))) {
          throw new Error('Invalid local display decision');
        }
      }
      ids.add(a.id);
    }
  }
}

/** Presentation isolation cannot grant a source-only/held asset a learner binding. */
export function selected(a: BodyAsset, view: BodyView): boolean {
  return pickable(a) && a.stableIds.some(id => (view.selectedIds ?? [view.selectedId]).includes(id));
}
