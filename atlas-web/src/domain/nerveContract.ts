/** G3 registration port. Source observations never become learner anatomy by name matching. */
export const NERVE_CONTRACT = 'nerve-support-v1' as const;
export type NerveSide = 'left' | 'right' | 'midline' | 'unpaired' | 'unknown';
export type NerveSelection = { kind: 'nerve'; instanceId: string };
export type AnatomicalSelection = NerveSelection | { kind: 'muscle' | 'bone'; sourceKey: string };
export interface NerveEvidence {
  id: string; sourcePath: string; sourceSha256: string; locator: string;
  subjectId: string; predicate: 'identity' | 'side' | 'scope' | 'branch' | 'frame' | 'pose' | 'placement' | 'motor_innervation' | 'cutaneous_territory' | 'root_dermatome' | 'muscle_proprioception' | 'traditional_meridian';
  objectId: string | null; status: 'verified_local' | 'candidate' | 'conflicted';
  fixtureOnly?: true;
  /** Exact serialized frame contract for frame/registration facts. */
  value?: string;
}
export interface NerveGeometry {
  kind: 'curve' | 'mesh'; assetPath: string; assetSha256: string;
  topologySha256: string; sourceNamespace: string; sourceFrameId: string;
  sourcePoseId: string; sourceUnit: 'm' | 'mm'; targetFrameId: string;
  geometrySpace: 'source_local' | 'source_world'; sourceObjectToWorld: number[];
  /** Row-major, applied once after the source object/world transform. */
  sourceToAtlas: number[]; transformKind: 'same_source_axis_conversion' | 'inter_model_registration';
  evidenceIds: string[];
  registrationEvidenceIds: string[];
  /** Static only until a separately validated pose binding is supplied. */
  validatedPoseIds: string[];
}
export interface NerveInstance {
  id: string; sourceNamespace: string; sourceObjectId: string; conceptId: string | null;
  side: NerveSide; scope: 'trunk' | 'branch' | 'root' | 'plexus' | 'ganglion' | 'neural_context' | 'unresolved';
  names: { koTraditional: string | null; koModern: string | null; en: string | null };
  regionIds: string[]; identity: 'candidate' | 'verified_local' | 'conflicted';
  evidenceIds: string[]; geometry: NerveGeometry | null;
  localSelection: 'unsupported' | 'text_only' | 'verified_geometry';
  hardHolds: string[]; sourceOnly: true; humanReview: 'not_performed'; publicRedistribution: 'held';
}
export type NerveRelation = {
  id: string; fromId: string; toId: string; evidenceIds: string[]; status: 'candidate' | 'verified_local';
} & (
  { kind: 'branch_of'; targetKind: 'nerve' } |
  { kind: 'motor_innervation' | 'muscle_proprioception'; targetKind: 'muscle' | 'muscle_part'; targetSide: NerveSide } |
  { kind: 'cutaneous_territory'; targetKind: 'cutaneous_area' } |
  { kind: 'root_dermatome'; targetKind: 'root_area' } |
  { kind: 'traditional_meridian'; targetKind: 'traditional_area' }
);
export interface NerveRegistry {
  schemaVersion: typeof NERVE_CONTRACT; instances: NerveInstance[];
  evidence: NerveEvidence[]; relations: NerveRelation[];
  targets: { id: string; kind: 'muscle' | 'muscle_part' | 'cutaneous_area' | 'root_area' | 'traditional_area';
    side: NerveSide; evidenceIds: string[] }[];
  /** Region context is separate from the nerve's full course/extent. */
  regionalBindings?: { instanceId: string; regionIds: string[]; evidenceIds: string[];
    extentMeaning: 'display_context_only' }[];
}
const hash = (s: string) => /^[a-f0-9]{64}$/.test(s);
const localPath = (s: string) => /^(atlas-data|work)\//.test(s) && !s.split('/').includes('..');
const sides: NerveSide[] = ['left', 'right', 'midline', 'unpaired', 'unknown'];
const regions = ['head', 'neck', 'back', 'shoulder-scapular', 'thorax', 'abdomen-lumbar', 'pelvis-perineum', 'gluteal-hip', 'thigh', 'leg', 'foot', 'upper-limb'];
const predicates = ['identity', 'side', 'scope', 'branch', 'frame', 'pose', 'placement', 'motor_innervation', 'cutaneous_territory', 'root_dermatome', 'muscle_proprioception', 'traditional_meridian'];
function check(ok: unknown, reason: string): asserts ok { if (!ok) throw new Error(`nerve contract: ${reason}`); }
export function nerveFrameSignature(g: NerveGeometry): string {
  return JSON.stringify([g.assetSha256, g.topologySha256, g.sourceNamespace, g.sourceFrameId, g.sourcePoseId, g.sourceUnit,
    g.targetFrameId, g.geometrySpace, g.sourceObjectToWorld, g.sourceToAtlas, g.transformKind]);
}

/** Runtime validation as well as TS typing: rejects mixed systems and incomplete promotions. */
export function validateNerveRegistry(value: unknown, options: { allowFixtures?: boolean } = {}): NerveRegistry {
  const r = value as NerveRegistry;
  check(r?.schemaVersion === NERVE_CONTRACT && Array.isArray(r.instances) && Array.isArray(r.evidence) && Array.isArray(r.relations) && Array.isArray(r.targets), 'registry');
  const nodes = new Map(r.instances.map(n => [n.id, n]));
  const ev = new Map(r.evidence.map(e => [e.id, e]));
  const targets = new Map(r.targets.map(t => [t.id, t]));
  check(nodes.size === r.instances.length && ev.size === r.evidence.length && targets.size === r.targets.length
    && r.targets.every(t => !nodes.has(t.id))
    && new Set(r.instances.map(n => `${n.sourceNamespace}:${n.sourceObjectId}`)).size === r.instances.length, 'duplicate identity');
  for (const e of r.evidence) check(e.id && e.subjectId && e.locator?.trim() && localPath(e.sourcePath) && hash(e.sourceSha256)
    && predicates.includes(e.predicate) && ['verified_local', 'candidate', 'conflicted'].includes(e.status)
    && (e.fixtureOnly !== true || options.allowFixtures === true), 'evidence locator/hash/type or fixture promotion');
  const refs = (ids: string[]) => Array.isArray(ids) && ids.every(id => ev.has(id));
  const has = (ids: string[], subject: string, predicate: string, object: string | null = null, value?: string) => ids.some(id => {
    const e = ev.get(id); return e?.status === 'verified_local' && e.subjectId === subject && e.predicate === predicate && e.objectId === object
      && (value === undefined || e.value === value);
  });
  for (const t of r.targets) check(t.id && ['muscle', 'muscle_part', 'cutaneous_area', 'root_area', 'traditional_area'].includes(t.kind)
    && sides.includes(t.side) && refs(t.evidenceIds) && ['identity', 'side', 'scope'].every(p => has(t.evidenceIds, t.id, p)), 'target identity/scope');
  const regionalBindings = r.regionalBindings ?? [];
  check(Array.isArray(regionalBindings), 'regional bindings');
  const regionalKeys = new Set<string>();
  for (const binding of regionalBindings) {
    const instance = nodes.get(binding.instanceId);
    check(instance && binding.extentMeaning === 'display_context_only'
      && Array.isArray(binding.regionIds) && binding.regionIds.length > 0
      && binding.regionIds.every(id => regions.includes(id) && instance.regionIds.includes(id))
      && refs(binding.evidenceIds) && has(binding.evidenceIds, binding.instanceId, 'scope'),
    'regional context evidence/extent');
    for (const regionId of binding.regionIds) {
      const key = `${binding.instanceId}:${regionId}`;
      check(!regionalKeys.has(key), 'duplicate regional binding');
      regionalKeys.add(key);
    }
  }
  for (const n of r.instances) {
    check(n.id?.startsWith(`${n.sourceNamespace}:`) && n.sourceNamespace && n.sourceObjectId && sides.includes(n.side)
      && ['trunk', 'branch', 'root', 'plexus', 'ganglion', 'neural_context', 'unresolved'].includes(n.scope)
      && ['candidate', 'verified_local', 'conflicted'].includes(n.identity)
      && ['unsupported', 'text_only', 'verified_geometry'].includes(n.localSelection)
      && refs(n.evidenceIds) && Array.isArray(n.hardHolds) && Array.isArray(n.regionIds) && n.regionIds.every(id => regions.includes(id)) && n.names
      && ['koTraditional', 'koModern', 'en'].every(k => { const s = n.names[k as keyof typeof n.names]; return s === null || typeof s === 'string' && s.trim().length > 0; })
      && !/[\u3400-\u9fff\uf900-\ufaff]/.test(`${n.names.koTraditional ?? ''}${n.names.koModern ?? ''}`)
      && n.sourceOnly === true && n.humanReview === 'not_performed' && n.publicRedistribution === 'held', 'identity/policy');
    if (n.localSelection !== 'unsupported') {
      check(n.identity === 'verified_local' && n.side !== 'unknown' && n.scope !== 'unresolved'
        && n.hardHolds.length === 0 && n.names.en && n.regionIds.length > 0
        && ['identity', 'side', 'scope'].every(p => has(n.evidenceIds, n.id, p)), 'selection promotion');
    }
    if (n.geometry) {
      const g = n.geometry;
      check(['curve', 'mesh'].includes(g.kind) && localPath(g.assetPath) && hash(g.assetSha256) && hash(g.topologySha256)
        && g.sourceNamespace === n.sourceNamespace && g.sourceFrameId && g.sourcePoseId && ['m', 'mm'].includes(g.sourceUnit)
        && g.targetFrameId === 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR'
        && ['source_local', 'source_world'].includes(g.geometrySpace)
        && Array.isArray(g.sourceObjectToWorld) && g.sourceObjectToWorld.length === 16 && g.sourceObjectToWorld.every(Number.isFinite)
        && g.sourceObjectToWorld.slice(12).join(',') === '0,0,0,1'
        && Array.isArray(g.sourceToAtlas) && g.sourceToAtlas.length === 16 && g.sourceToAtlas.every(Number.isFinite)
        && g.sourceToAtlas.slice(12).join(',') === '0,0,0,1'
        && ['same_source_axis_conversion', 'inter_model_registration'].includes(g.transformKind)
        && refs(g.evidenceIds) && refs(g.registrationEvidenceIds)
        && Array.isArray(g.validatedPoseIds) && g.validatedPoseIds.length === 1 && g.validatedPoseIds[0] === g.sourcePoseId, 'geometry/frame');
      if (g.geometrySpace === 'source_world') check(g.sourceObjectToWorld.join(',') === '1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1', 'double world transform');
      const m = g.sourceToAtlas;
      const det = m[0]*(m[5]*m[10]-m[6]*m[9])-m[1]*(m[4]*m[10]-m[6]*m[8])+m[2]*(m[4]*m[9]-m[5]*m[8]);
      check(det > 0, 'reflection/singular transform');
      if (g.transformKind === 'same_source_axis_conversion') {
        const scale = g.sourceUnit === 'mm' ? 0.001 : 1;
        check([0, 1, 2].every(col => Math.abs(Math.hypot(m[col], m[col+4], m[col+8]) - scale) < 1e-8)
          && Math.abs(det - scale**3) < scale**3 * 1e-6 && [3, 7, 11].every(i => m[i] === 0), 'unit/axis-only scale');
      }
      if (g.transformKind === 'inter_model_registration') check(has(g.registrationEvidenceIds, n.id, 'placement', g.assetSha256, nerveFrameSignature(g)), 'registration evidence');
      if (n.localSelection === 'verified_geometry') check(['frame', 'placement'].every(p => has(g.evidenceIds, n.id, p, g.assetSha256))
        && has(g.evidenceIds, n.id, 'frame', g.assetSha256, nerveFrameSignature(g))
        && g.validatedPoseIds.every(p => has(g.evidenceIds, n.id, 'pose', p)), 'geometry evidence');
    } else check(n.localSelection !== 'verified_geometry', 'missing geometry');
  }
  const relationIds = new Set<string>();
  const parents = new Map<string, string[]>();
  for (const edge of r.relations) {
    check(edge.id && !relationIds.has(edge.id) && nodes.has(edge.fromId) && refs(edge.evidenceIds)
      && ['candidate', 'verified_local'].includes(edge.status), 'relation identity'); relationIds.add(edge.id);
    const kindTargets: Record<string, string[]> = { branch_of: ['nerve'], motor_innervation: ['muscle', 'muscle_part'],
      muscle_proprioception: ['muscle', 'muscle_part'], cutaneous_territory: ['cutaneous_area'], root_dermatome: ['root_area'], traditional_meridian: ['traditional_area'] };
    check(kindTargets[edge.kind]?.includes(edge.targetKind) && edge.toId, 'mixed relation systems');
    if (edge.status === 'verified_local') check(has(edge.evidenceIds, edge.fromId, edge.kind === 'branch_of' ? 'branch' : edge.kind, edge.toId)
      && nodes.get(edge.fromId)!.identity === 'verified_local', 'relation evidence');
    if (edge.status === 'verified_local' && edge.kind !== 'branch_of') check(targets.get(edge.toId)?.kind === edge.targetKind
      && targets.get(edge.toId)?.side === nodes.get(edge.fromId)!.side, 'unregistered target or scope/side substitution');
    if (edge.kind === 'branch_of') {
      const parent = nodes.get(edge.toId); const child = nodes.get(edge.fromId)!;
      check(parent && child.id !== parent.id, 'branch reference');
      if (edge.status === 'verified_local') check(parent.identity === 'verified_local'
        && child.side === parent.side && child.side !== 'unknown', 'branch side');
      parents.set(child.id, [...parents.get(child.id) ?? [], parent.id]);
    } else if (edge.kind === 'motor_innervation' || edge.kind === 'muscle_proprioception') {
      check(sides.includes(edge.targetSide), 'target side');
      if (edge.status === 'verified_local') check(edge.targetSide === nodes.get(edge.fromId)!.side && edge.targetSide !== 'unknown', 'innervation side');
    }
  }
  const visited = new Set<string>(); const active = new Set<string>();
  function visit(id: string) { check(!active.has(id), 'branch cycle'); if (visited.has(id)) return;
    active.add(id); for (const p of parents.get(id) ?? []) visit(p); active.delete(id); visited.add(id); }
  for (const id of nodes.keys()) visit(id);
  return r;
}
export interface NerveViewContext {
  nerves: boolean; poseId: string; frameId: string; regionIds: string[]; hiddenIds: string[];
}
/** A selected/ restored nerve still obeys layer-off, holds, frame and pose. */
export function nerveVisible(n: NerveInstance, v: NerveViewContext): boolean {
  return n.identity === 'verified_local' && n.localSelection === 'verified_geometry' && n.hardHolds.length === 0
    && !!n.geometry && n.geometry.validatedPoseIds.includes(v.poseId) && n.geometry.targetFrameId === v.frameId
    && v.nerves && !v.hiddenIds.includes(n.id) && (!v.regionIds.length || v.regionIds.some(id => n.regionIds.includes(id)));
}
/** Lets the shared player/UI request return-to-rest rather than silently changing the layer toggle. */
export function nervePoseDecision(n: NerveInstance, v: NerveViewContext): 'available' | 'return_to_validated_pose' | 'unsupported' {
  if (!n.geometry || n.localSelection !== 'verified_geometry' || n.identity !== 'verified_local' || n.hardHolds.length) return 'unsupported';
  if (n.geometry.targetFrameId !== v.frameId) return 'unsupported';
  return n.geometry.validatedPoseIds.includes(v.poseId) ? 'available' : 'return_to_validated_pose';
}
export function selectNerve(r: NerveRegistry, selection: AnatomicalSelection, view: NerveViewContext): NerveInstance | null {
  if (selection.kind !== 'nerve') return null;
  const n = r.instances.find(n => n.id === selection.instanceId);
  return n && nerveVisible(n, view) ? n : null;
}
export function innervatedMuscleIds(r: NerveRegistry, n: NerveInstance): string[] {
  if (n.identity !== 'verified_local' || n.hardHolds.length || n.localSelection === 'unsupported') return [];
  return [...new Set(r.relations.filter(e => e.fromId === n.id && e.kind === 'motor_innervation' && e.status === 'verified_local').map(e => e.toId))];
}
/** The common scene supplies its already policy-filtered muscle IDs; this cannot turn layers back on. */
export function nerveMuscleHighlights(r: NerveRegistry, selection: AnatomicalSelection, v: NerveViewContext, visibleMuscleIds: ReadonlySet<string>): string[] {
  const n = selectNerve(r, selection, v);
  return n ? innervatedMuscleIds(r, n).filter(id => visibleMuscleIds.has(id)) : [];
}
/** Learner DTO deliberately omits source/task/evidence/review metadata. */
export function nerveCard(r: NerveRegistry, n: NerveInstance) {
  if (n.identity !== 'verified_local' || n.localSelection === 'unsupported' || n.hardHolds.length) return null;
  return { kind: 'nerve' as const, names: n.names, side: n.side, scope: n.scope,
    courseAvailable: n.localSelection === 'verified_geometry', muscleIds: innervatedMuscleIds(r, n),
    branchIds: r.relations.filter(e => e.kind === 'branch_of' && e.toId === n.id && e.status === 'verified_local'
      && r.instances.some(child => child.id === e.fromId && child.localSelection !== 'unsupported' && child.hardHolds.length === 0)).map(e => e.fromId) };
}
