import { validateNerveRegistry, nerveCard, type NerveRegistry } from '../../domain/nerveContract.ts';
import { validateDataset, type Dataset } from './schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from './integration.ts';

export interface NerveSceneManifest {
  schemaVersion: 1; revision: string; registryPath: string; datasetPath: string; rightsPath: string;
  inputSha256: Record<string, string>;
  objects: { instanceId: string; sourceKey: string; bounds: number[][]; name: string;
    path: string; sha256: string; topologySha256: string }[];
}
export interface NerveLocalRights {
  id: string; allowedSourceKeys: string[]; localUseRights: string; sourceOnly: true;
  humanReview: 'not_performed'; publicRedistribution: 'held';
}
/** The server verifies all pinned bytes before calling this common composition port. */
export function composeNerveScene(base: Dataset, runtime: RuntimeIntegration, input: NerveSceneManifest,
  rawRegistry: unknown, rawDataset: unknown, rights: NerveLocalRights, combinedHash: string, rightsHash: string) {
  validateRuntimeIntegration(runtime, base);
  const registry: NerveRegistry = validateNerveRegistry(rawRegistry);
  const nerves = validateDataset(rawDataset);
  const supported = registry.instances.filter(n => n.localSelection === 'verified_geometry');
  if (input.schemaVersion !== 1 || input.objects.length !== supported.length || nerves.instances.length !== supported.length
    || rights.localUseRights !== 'supported_local_prototype' || !rights.sourceOnly
    || rights.humanReview !== 'not_performed' || rights.publicRedistribution !== 'held'
    || new Set(input.objects.map(o => o.instanceId)).size !== supported.length
    || new Set(input.objects.map(o => o.sourceKey)).size !== supported.length
    || new Set(rights.allowedSourceKeys).size !== supported.length) throw Error('nerve scene scope/rights');
  const keyById = new Map(input.objects.map(o => [o.instanceId, o.sourceKey]));
  const policy = { ...runtime.policy, rightsDecisionId: runtime.policy.rightsDecisionId + '+' + rights.id };
  const rows: RuntimeStructureRecord[] = input.objects.map(o => {
    const n = supported.find(n => n.id === o.instanceId);
    const instance = nerves.instances.find(i => i.sourceKey === o.sourceKey);
    if (!n?.geometry || !instance || !rights.allowedSourceKeys.includes(o.sourceKey)
      || n.hardHolds.length || n.sourceNamespace !== 'za-c7010a9' || !['left', 'right'].includes(n.side)
      || n.geometry.geometrySpace !== 'source_world' || n.geometry.transformKind !== 'same_source_axis_conversion'
      || o.path !== n.geometry.assetPath || o.sha256 !== n.geometry.assetSha256 || o.topologySha256 !== n.geometry.topologySha256
      || instance.kind !== 'nerve_surface' || instance.sourceName !== o.name
      || instance.sourceHiddenStatePreserved.hideViewport
      || instance.matrix.some((v, idx) => v !== n.geometry!.sourceToAtlas[idx % 4 * 4 + Math.floor(idx / 4)])
      || o.bounds.length !== 2 || o.bounds.some(b => b.length !== 3 || b.some(v => !Number.isFinite(v)))
      || (n.side === 'left' ? o.bounds[0][0] <= 0 : o.bounds[1][0] >= 0)) throw Error('nerve scene identity/frame');
    const card = nerveCard(registry, n)!;
    const muscleKeys = card.muscleIds.filter(id => runtime.objects.some(r => r.sourceKey === id && r.kind === 'muscle'
      && r.side === n.side && r.localDisplayEligible));
    if (muscleKeys.length !== card.muscleIds.length) throw Error('nerve motor target policy/side');
    return {
      sourceKey: o.sourceKey, routeAudience: 'learner', searchGroupKey: n.names.en!, kind: 'nerve',
      regionIds: [...n.regionIds], side: n.side, label: n.names.koTraditional ?? n.names.en!,
      names: { ...n.names, en: n.names.en! }, aliases: [], haConceptId: null, learnerConceptKeys: [], targetRoutes: [],
      localDisplayEligible: true, inspectionEligible: true, defaultVisible: true, sourceOnly: true,
      humanReview: 'not_performed', publicRedistribution: 'held', sourceHiddenStatePreserved: { ...instance.sourceHiddenStatePreserved },
      localUseRights: 'supported_local_prototype', displayDecisionBasis: policy.rightsDecisionId, hardHoldReasons: [],
      bounds: o.bounds as RuntimeStructureRecord['bounds'], relatedMuscles: [],
      nerve: { poseId: n.geometry.sourcePoseId, branchKeys: card.branchIds.map(id => keyById.get(id)!), muscleKeys },
    };
  });
  const dataset = validateDataset({ ...base, revision: base.revision + '+' + input.revision,
    instances: [...base.instances, ...nerves.instances], chunks: [...base.chunks, ...nerves.chunks.map(c => ({ ...c, sourceNamespace: nerves.namespace }))],
    resources: { ...base.resources, ...nerves.resources },
    metrics: { instances: base.instances.length + nerves.instances.length,
      uniqueResources: Object.keys({ ...base.resources, ...nerves.resources }).length,
      totalBytes: [...base.chunks, ...nerves.chunks].reduce((sum, c) => sum + c.bytes, 0),
      overviewBytes: [...base.chunks, ...nerves.chunks].filter(c => c.level === 'overview' && !c.selectionScoped).reduce((sum, c) => sum + c.bytes, 0),
      overviewTriangles: [...base.instances, ...nerves.instances].reduce((sum, i) => sum + i.lods.overview.triangles, 0),
      overviewGeometryBytes: [...base.chunks, ...nerves.chunks].filter(c => c.level === 'overview').reduce((sum, c) => sum + c.geometryBytes, 0) } });
  const integration = validateRuntimeIntegration({ ...runtime, datasetRevision: dataset.revision,
    sourceOverlaySha256: combinedHash, rightsEvidenceSha256: rightsHash, policy,
    objects: [...runtime.objects.map(r => ({ ...r, displayDecisionBasis: policy.rightsDecisionId })), ...rows] }, dataset);
  return { dataset, integration };
}
