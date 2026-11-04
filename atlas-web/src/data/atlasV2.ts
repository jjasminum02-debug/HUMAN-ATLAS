// v2 runtime data (ROADMAP D2): atlas-data/runtime/structures.json + relations.json, geometry chunks.
// projectLegacyRuntime() turns it into the Dataset/RuntimeIntegration shapes the current viewer and UI
// consume. Pre-v2 structures keep their keys, geometry bytes and binding identity, so motion, acupoint and
// skin bindings stay valid. `layer` decides the row kind (bone/muscle/tendon/fascia/joint/nerve); structures
// without a layer (CNS, sense organs, attachment patches, cavities) project as hidden accessories.
import { validateDataset, type Dataset, type Instance, type Level } from '../viewer/datasets/schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from '../viewer/datasets/integration.ts';

export type V2System = 'skeletal' | 'attachment' | 'joint' | 'muscular' | 'nervous';
export type V2Layer = 'bone' | 'muscle' | 'fascia' | 'joint' | 'nerve';
export interface V2Lod { resource: string; chunk: string; triangles: number; vertices: number; geometryBytes: number }
export interface V2Structure {
  id: string; key: string; sourceName: string; system: V2System; kind: string | null;
  side: 'left' | 'right' | 'unpaired'; bodyRegions: string[]; regions: string[];
  layer: V2Layer | null; depth: 'superficial' | 'deep' | null;
  names: RuntimeStructureRecord['names']; label: string; aliases: string[]; searchGroup: string;
  learner: { visible: boolean; defaultVisible: boolean; inspectable: boolean; sourceOnly: boolean };
  content: { haConceptId: string | null; learnerConceptKeys: string[] };
  nerve?: { poseId: string };
  geometry: { namespace: string; instanceKind: string; matrix: number[]; bounds: RuntimeStructureRecord['bounds']; hideRender: boolean; lods: Record<Level, V2Lod> };
}
export interface V2Compat {
  datasetRevision: string; frameContract: Dataset['frameContract']; sourceRevisions: Record<string, string>;
  integrationRevision: string; sourceComponents: NonNullable<RuntimeIntegration['sourceComponents']>;
  sourceOverlaySha256: string; rightsEvidenceSha256: string; rightsDecisionId: string;
}
export interface V2StructuresFile { schemaVersion: 2; revision: string; frame: string; source: string; regions: string[]; compat: V2Compat; structures: V2Structure[] }
export type V2Relation =
  | { type: 'origin' | 'insertion'; from: string; owners: string[]; bone: string | null }
  | { type: 'nerve_branch' | 'innervates'; from: string; to: string }
  | { type: 'related_muscle'; from: string; to: string; label: string; roles: string[] };
export interface V2RelationsFile { schemaVersion: 2; revision: string; relations: V2Relation[] }
export interface V2Chunk { id: string; sha256: string; bytes: number; geometryBytes: number; level: Level; resources: string[]; namespace: string; onDemand: boolean }
export interface V2GeometryFile { schemaVersion: 2; revision: string; chunks: V2Chunk[]; resources: Dataset['resources'] }

const HIDDEN_REASON = 'accessory-or-original-hidden-or-exception';
const INSTANCE_KIND: Record<string, string> = { bone: 'skeletal_surface', muscle: 'muscle_surface_or_part', tendon: 'tendon_surface',
  fascia: 'fascia_surface', joint: 'joint_surface', nerve: 'nerve_surface' };
function rowKind(s: V2Structure): RuntimeStructureRecord['kind'] {
  return s.layer === null ? 'accessory' : s.layer === 'muscle' && s.kind === 'tendon' ? 'tendon' : s.layer;
}

export function projectLegacyRuntime(file: V2StructuresFile, relationsFile: V2RelationsFile, geometry: V2GeometryFile): { dataset: Dataset; integration: RuntimeIntegration } {
  if (file.schemaVersion !== 2 || relationsFile.revision !== file.revision || geometry.revision !== file.revision)
    throw Error('atlas v2 files are from different builds');
  const { compat } = file;
  const byId = new Map(file.structures.map(s => [s.id, s]));
  const keyOf = (id: string) => { const s = byId.get(id); if (!s) throw Error(`atlas v2 relation to unknown structure ${id}`); return s.key; };

  const instances: Instance[] = file.structures.map(s => ({
    sourceKey: s.key, sourceName: s.sourceName, kind: INSTANCE_KIND[rowKind(s)] ?? s.geometry.instanceKind, matrix: s.geometry.matrix,
    lods: { overview: s.geometry.lods.overview, detail: s.geometry.lods.detail },
    sourceNamespace: s.geometry.namespace, geometrySpace: 'source_local',
    canonicalConceptId: null, learnerBinding: 'source_only_unbound', defaultLearnerVisible: false,
    appDisplayRights: 'held_not_approved_by_this_task', publicRedistribution: 'held', humanReview: 'not_performed',
    sourceHiddenStatePreserved: { hideRender: s.geometry.hideRender, hideViewport: false },
  }));
  const dataset = validateDataset({
    schemaVersion: 1, namespace: 'human-atlas-local', revision: compat.datasetRevision, unit: 'm', geometrySpace: 'source_local',
    localOnly: true, publicRedistribution: 'held', sourceRevisions: compat.sourceRevisions, frameContract: compat.frameContract,
    instances,
    chunks: geometry.chunks.map(c => ({
      id: c.id, url: `/__atlas/datasets/${c.namespace}/${c.id}.glb`, sha256: c.sha256, bytes: c.bytes, geometryBytes: c.geometryBytes,
      resources: c.resources, level: c.level, sourceNamespace: c.namespace, ...(c.onDemand ? { selectionScoped: true } : {}),
    })),
    resources: geometry.resources, budgetPass: true,
  });

  const nerveLinks = new Map<string, { branchKeys: string[]; muscleKeys: string[] }>();
  const related = new Map<string, RuntimeStructureRecord['relatedMuscles']>();
  for (const r of relationsFile.relations) {
    if (r.type === 'nerve_branch' || r.type === 'innervates') {
      const links = nerveLinks.get(r.from) ?? { branchKeys: [], muscleKeys: [] };
      (r.type === 'nerve_branch' ? links.branchKeys : links.muscleKeys).push(keyOf(r.to));
      nerveLinks.set(r.from, links);
    } else if (r.type === 'related_muscle') {
      related.set(r.from, [...(related.get(r.from) ?? []), { sourceKey: keyOf(r.to), label: r.label, roles: r.roles }]);
    }
  }
  const objects: RuntimeStructureRecord[] = file.structures.map(s => {
    const kind = rowKind(s);
    const row: RuntimeStructureRecord = {
      sourceKey: s.key, routeAudience: 'learner', searchGroupKey: s.searchGroup, kind, regionIds: s.regions,
      side: s.side === 'unpaired' ? null : s.side, label: s.label, names: s.names, aliases: s.aliases,
      haConceptId: s.content.haConceptId, learnerConceptKeys: s.content.learnerConceptKeys, targetRoutes: [],
      localDisplayEligible: s.learner.visible, inspectionEligible: s.learner.inspectable, defaultVisible: s.learner.defaultVisible,
      sourceOnly: s.learner.sourceOnly, humanReview: 'not_performed', publicRedistribution: 'held',
      sourceHiddenStatePreserved: { hideRender: s.geometry.hideRender, hideViewport: false },
      localUseRights: s.learner.visible ? 'supported_local_prototype' : 'not_eligible',
      displayDecisionBasis: compat.rightsDecisionId, hardHoldReasons: s.learner.visible ? [] : [HIDDEN_REASON],
      bounds: s.geometry.bounds, relatedMuscles: related.get(s.id) ?? [],
    };
    if (kind === 'nerve') row.nerve = { poseId: s.nerve!.poseId, ...(nerveLinks.get(s.id) ?? { branchKeys: [], muscleKeys: [] }) };
    if (s.depth) row.depth = s.depth;
    if (kind === 'fascia' || kind === 'joint' || kind === 'tendon' || kind === 'bone' && s.kind !== 'bone') row.tissue = s.kind!;
    return row;
  });
  const integration = validateRuntimeIntegration({
    schemaVersion: 1, projectionSchema: 'whole-body-local-runtime-v5', revision: compat.integrationRevision,
    datasetRevision: dataset.revision, sourceOverlaySha256: compat.sourceOverlaySha256, rightsEvidenceSha256: compat.rightsEvidenceSha256,
    sourceComponents: compat.sourceComponents, scope: { targets: 542, memberships: 563, regions: 12 },
    policy: { localOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', localUseRights: 'supported_local_prototype', rightsDecisionId: compat.rightsDecisionId },
    objects,
  }, dataset);
  return { dataset, integration };
}
