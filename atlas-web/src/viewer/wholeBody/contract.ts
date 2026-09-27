export interface BodyAsset {
  id: string; nodeId: string; sourceSha256: string; regions: string[];
  side: string | null; layer: 'bone' | 'muscle'; defaultVisible: boolean; supplement: boolean;
  pickState: string; stableIds: string[]; holdReasons: string[]; humanReviewed: boolean;
  bounds: [number[], number[]];
}
export interface BodyChunk { id: string; url: string; sha256: string; bytes: number; assets: BodyAsset[] }
export interface BodyManifest { version: number; localOnly: boolean; publicRedistribution: string; frame: string; unit: string; lodLevels: number; chunks: BodyChunk[] }
export interface BodyView { region: string | null; bones: boolean; muscles: boolean; supplements: boolean; selectedId: string | null; selectedIds?: string[]; dim: boolean }
export function visible(a: BodyAsset, view: BodyView): boolean {
  return (a.defaultVisible || (a.supplement && view.supplements && a.pickState === 'source_only_unbound'))
    && (a.layer === 'bone' ? view.bones : view.muscles)
    && (!view.region || a.regions.includes(view.region));
}
export function pickable(a: BodyAsset): boolean {
  return ['left', 'right', 'midline'].includes(a.side ?? '') && a.defaultVisible && a.pickState === 'existing_binding_unreviewed' && a.holdReasons.length === 0 && a.stableIds.length > 0;
}
export function validateManifest(m: BodyManifest): void {
  if (m.unit !== 'm' || m.version !== 1 || !m.localOnly || m.publicRedistribution !== 'held' || m.lodLevels !== 1 || m.frame !== 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR') throw new Error('Unsupported body contract');
  const ids = new Set<string>();
  for (const c of m.chunks) {
    if (!/^[a-z0-9-]+$/.test(c.id) || c.url !== `/__atlas/body/${c.id}.glb` || !/^[a-f0-9]{64}$/.test(c.sha256)) throw new Error('Invalid chunk');
    for (const a of c.assets) {
      if (ids.has(a.id) || a.nodeId !== `HA-MESH-BP3D4-${a.id}` || (a.pickState === 'source_only_unbound' && a.stableIds.length)) throw new Error('Invalid identity');
      if (a.humanReviewed !== false || (a.holdReasons.length > 0 && a.defaultVisible) || a.bounds.length !== 2 || a.bounds.some(v => v.length !== 3 || v.some(n => !Number.isFinite(n)))) throw new Error('Invalid source hold or bounds');
      ids.add(a.id);
    }
  }
}
