import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { wholeBodyPlugin } from '../plugins/wholeBody.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';
import { validateRuntimeIntegration, readDatasetRoute, searchStructures, type RuntimeIntegration } from '../src/viewer/datasets/integration.ts';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const sha = (bytes: Buffer | string) => createHash('sha256').update(bytes).digest('hex');
const read = async (path: string) => readFile(resolve(projectRoot, path));
const json = async (path: string) => JSON.parse((await read(path)).toString());

const watcher = { add: () => undefined, on: () => watcher, off: () => undefined };
let handler: Function | undefined;
wholeBodyPlugin(projectRoot).configureServer({
  watcher,
  middlewares: { use: (...args: Function[]) => { handler = args.at(-1); } },
  httpServer: { once: () => undefined },
} as any);
if (!handler) throw Error('current shared runtime composition middleware missing');
async function get(path: string) {
  return new Promise<{ status: number; body: Buffer }>((resolvePromise, reject) => {
    const res: any = { statusCode: 200, setHeader: () => undefined, end: (body?: Buffer | string) => resolvePromise({ status: res.statusCode, body: Buffer.from(body ?? '') }) };
    Promise.resolve(handler!({ url: path, destroyed: false }, res, () => resolvePromise({ status: 404, body: Buffer.alloc(0) }))).catch(reject);
  });
}

const [datasetResponse, runtimeResponse] = await Promise.all([
  get('/__atlas/datasets/human-atlas-local/manifest.json'),
  get('/__atlas/integration.json'),
]);
if (datasetResponse.status !== 200 || runtimeResponse.status !== 200) throw Error('shared runtime endpoint is not ready');
const dataset = validateDataset(JSON.parse(datasetResponse.body.toString()));
const runtime = validateRuntimeIntegration(JSON.parse(runtimeResponse.body.toString()), dataset);
if (runtime.projectionSchema !== 'whole-body-local-runtime-v5') throw Error('runtime audience contract revision mismatch');

const scope = await json('atlas-data/catalog/target-scope-t96.json');
const regionIds: string[] = scope.regions.map((row: any) => row.regionId);
const overlay = await json('atlas-data/overlays/za-local-integration.json');
const supplement = await json('atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json');
const blockers = await json('work/evidence/T100/source-completion-2026-10-01/integration/final-blocker-list.json');
const historical163 = await json('work/evidence/T100/semantic-relations-2026-09-30/target-gap-classification.json');
const sourceRows = new Map(overlay.objects.map((row: any) => [row.sourceKey, row]));
const targets = new Map(scope.targets.map((row: any) => [row.id, row]));
const allMemberships = new Map<string, { targetId: string; regionId: string }>();
for (const target of scope.targets) for (const regionId of target.regionIds) {
  const key = `${target.id}|${regionId}`;
  if (allMemberships.has(key)) throw Error(`duplicate frozen membership ${key}`);
  allMemberships.set(key, { targetId: target.id, regionId });
}
if (scope.targets.length !== 542 || allMemberships.size !== 563 || scope.regions.length !== 12)
  throw Error('frozen whole-body denominator changed; refusing to scope a reduced dataset');

const learnerRows = runtime.objects.filter(row => row.routeAudience === 'learner');
const inspectionRows = runtime.objects.filter(row => row.routeAudience === 'inspection');
const selectableLearnerRows = learnerRows.filter(row => row.localDisplayEligible && row.inspectionEligible);
const selectableInspectionRows = inspectionRows.filter(row => row.localDisplayEligible && row.inspectionEligible);
const failures: Record<string, unknown>[] = [];
const validSide = (side: string | null) => side === null || side === 'left' || side === 'right';
const validateSelectableRecord = (row: RuntimeIntegration['objects'][number], audience: 'learner' | 'inspection') => {
  const source = sourceRows.get(row.sourceKey) as any;
  const instance = dataset.instances.find(item => item.sourceKey === row.sourceKey);
  const expectedNamespace = audience === 'inspection' ? 'bp3d-r4' : 'za-c7010a9';
  const reasons: string[] = [];
  if (!instance || (instance.sourceNamespace ?? 'za-c7010a9') !== expectedNamespace) reasons.push('dataset-instance-identity');
  if (row.routeAudience !== audience) reasons.push('route-audience');
  if (!row.label || !row.names.en) reasons.push('label');
  if (!validSide(row.side)) reasons.push('side');
  if (!row.regionIds.length || row.regionIds.some(region => !regionIds.includes(region))) reasons.push('region');
  if (row.inspectionEligible !== true || row.localDisplayEligible !== true) reasons.push('selection-eligibility');
  if (row.hardHoldReasons.length > 0 || row.sourceHiddenStatePreserved.hideViewport) reasons.push('hold');
  if (row.defaultVisible && !row.localDisplayEligible) reasons.push('default-visible-hold-bypass');
  if (source && (source.side !== row.side || source.label !== row.label || JSON.stringify(source.names) !== JSON.stringify(row.names)
      || JSON.stringify(source.regionIds) !== JSON.stringify(row.regionIds))) reasons.push('source-record-parity');
  if (reasons.length) {
    failures.push({ sourceKey: row.sourceKey, audience, reasons, sourceOnlyNameFields: row.names });
    return false;
  }
  const route = readDatasetRoute(`?regions=${encodeURIComponent(row.regionIds[0])}&source=${encodeURIComponent(row.sourceKey)}`, runtime.objects, regionIds, audience);
  if (route.selected !== row.sourceKey || !route.regions.includes(row.regionIds[0])) {
    failures.push({ sourceKey: row.sourceKey, audience, reason: 'direct-source-selection-route', route });
    return false;
  }
  return true;
};
const learnerSelectionPasses = selectableLearnerRows.filter(row => validateSelectableRecord(row, 'learner'));
const inspectionSelectionPasses = selectableInspectionRows.filter(row => validateSelectableRecord(row, 'inspection'));
if (learnerSelectionPasses.length !== selectableLearnerRows.length || inspectionSelectionPasses.length !== selectableInspectionRows.length)
  throw Error(`selectable source contract failures: ${JSON.stringify(failures.slice(0, 30))}`);

for (const row of selectableInspectionRows) {
  const unprivileged = readDatasetRoute(`?regions=${encodeURIComponent(row.regionIds[0])}&source=${encodeURIComponent(row.sourceKey)}`, runtime.objects, regionIds, 'learner');
  if (unprivileged.selected !== null) failures.push({ sourceKey: row.sourceKey, reason: 'inspection-source-selectable-in-learner-route' });
  const terms = [row.label, row.names.en, row.names.koModern ?? '', row.names.koTraditional ?? '', ...row.aliases].filter(Boolean);
  for (const term of terms) {
    if (searchStructures(runtime.objects, term, [], 'learner').some(candidate => candidate.sourceKey === row.sourceKey))
      failures.push({ sourceKey: row.sourceKey, term, reason: 'inspection-source-leaked-to-learner-search' });
  }
  for (const path of row.targetRoutes) {
    const query = `?regions=${encodeURIComponent(path.regionId)}&source=${encodeURIComponent(row.sourceKey)}&targetPathKey=${encodeURIComponent(path.key)}`;
    const learnerRoute = readDatasetRoute(query, runtime.objects, regionIds, 'learner');
    const inspectionRoute = readDatasetRoute(query, runtime.objects, regionIds, 'inspection');
    if (learnerRoute.selected !== null) failures.push({ sourceKey: row.sourceKey, path: path.key, reason: 'inspection-target-route-restored-in-learner-audience' });
    if (inspectionRoute.selected !== row.sourceKey || inspectionRoute.targetPathKey !== path.key)
      failures.push({ sourceKey: row.sourceKey, path: path.key, reason: 'inspection-target-route-failed', inspectionRoute });
  }
}
if (failures.length) throw Error(`product selection policy failed: ${JSON.stringify(failures.slice(0, 8))}`);

const allSearchResults = searchStructures(runtime.objects, '', [], 'learner');
const inspectionSearchResults = searchStructures(runtime.objects, '', [], 'inspection');
for (const row of [...allSearchResults, ...inspectionSearchResults]) {
  if (!row.localDisplayEligible || !row.inspectionEligible || !row.label || !row.names.en)
    throw Error(`search includes non-selectable or unnamed row ${row.sourceKey}`);
}
const regionalSearchCounts: Record<string, number> = {};
for (const regionId of regionIds) {
  const regional = searchStructures(runtime.objects, '', [regionId], 'learner');
  regionalSearchCounts[regionId] = regional.length;
  if (regional.some(row => !row.regionIds.includes(regionId))) throw Error(`region filter mismatch ${regionId}`);
}

// Re-execute every prior base membership path through the current shared router.
const ledgerPaths = [
  'work/evidence/T100/closure-audit-2026-09-30/browser-raster/raster-ledger.json',
  'work/evidence/T100/closure-audit-2026-09-30/browser-declared-right/raster-ledger.json',
];
const refs = new Map<string, any>();
for (const path of ledgerPaths) {
  const ledger = await json(path);
  for (const item of ledger.rows) for (const ref of item.references) {
    const key = `${ref.targetId}|${ref.regionId}|${item.sourceKey}|${ref.query}`;
    refs.set(key, { ...ref, sourceKey: item.sourceKey });
  }
}
const learnerMembershipRoutes = new Map<string, Set<string>>();
const learnerTargets = new Set<string>();
const routeFailures: unknown[] = [];
for (const ref of refs.values()) {
  const membershipKey = `${ref.targetId}|${ref.regionId}`;
  if (!allMemberships.has(membershipKey)) { routeFailures.push({ ...ref, reason: 'outside-frozen-membership' }); continue; }
  const route = readDatasetRoute(`?${ref.query}`, runtime.objects, regionIds, 'learner');
  if (route.selected !== ref.sourceKey || !route.regions.includes(ref.regionId)
      || runtime.objects.find(row => row.sourceKey === route.selected)?.routeAudience !== 'learner') {
    routeFailures.push({ ...ref, reason: 'learner-membership-route-failed', route });
    continue;
  }
  const keys = learnerMembershipRoutes.get(membershipKey) ?? new Set<string>();
  keys.add(ref.sourceKey); learnerMembershipRoutes.set(membershipKey, keys); learnerTargets.add(ref.targetId);
}
if (routeFailures.length) throw Error(`current learner membership route failures ${routeFailures.length}`);

const representedScopeType = (targetId: string, relationKind: string | undefined, identityStatus: string | undefined) => {
  const target = targets.get(targetId) as any;
  if (!target || identityStatus !== 'evidence_backed') return 'source_observation';
  if (target.semanticKind === 'muscle_part') return 'explicit_part';
  if (['bone_group', 'muscle_group', 'repeated_muscle_family', 'bone_series'].includes(target.semanticKind))
    return relationKind === 'verified_class_member' || relationKind === 'verified_taxonomy_member' ? 'declared_member_set' : 'source_observation';
  if (['bone', 'named_muscle'].includes(target.semanticKind)
      && ['verified_source_crosswalk', 'normalized_exact_target_term', 'verified_taxonomy_member', 'paired_source_concept'].includes(relationKind ?? ''))
    return 'whole_structure';
  return 'source_observation';
};
const scopeRowsByTarget = new Map<string, any[]>();
const membershipDisposition = [...allMemberships.values()].map(membership => {
  const key = `${membership.targetId}|${membership.regionId}`;
  const sourceKeys = [...(learnerMembershipRoutes.get(key) ?? new Set())].sort();
  const representations = sourceKeys.map(sourceKey => {
    const source = sourceRows.get(sourceKey) as any;
    const link = source?.learnerConceptLinks?.find((candidate: any) => candidate.targetIds?.includes(membership.targetId));
    const scopeType = representedScopeType(membership.targetId, link?.relationKind, link?.identityStatus);
    const representation = { sourceKey, regionId: membership.regionId, scopeType,
      relationKind: link?.relationKind ?? null, memberCode: link?.memberCode ?? null,
      side: source?.side ?? runtime.objects.find(row => row.sourceKey === sourceKey)?.side ?? null,
      extentAccepted: false, extentStatus: scopeType === 'source_observation' ? 'target-identity-or-scope-unresolved' : 'selection-route-only; full geometry extent not established' };
    const list = scopeRowsByTarget.get(membership.targetId) ?? [];
    list.push(representation); scopeRowsByTarget.set(membership.targetId, list);
    return representation;
  });
  return { ...membership, status: sourceKeys.length ? 'learner_route_available' : 'no_learner_route', sourceKeys, representations };
});
const targetDisposition = scope.targets.map((target: any) => {
  const rows = membershipDisposition.filter(row => row.targetId === target.id);
  const available = rows.filter(row => row.status === 'learner_route_available');
  return { targetId: target.id, regionIds: [...target.regionIds], status: available.length ? 'learner_route_available' : 'no_learner_route',
    routedMembershipCount: available.length, membershipCount: rows.length,
    representationScopes: [...new Set(available.flatMap(row => row.representations.map((representation: any) => representation.scopeType)))].sort(),
    fullTargetExtentAccepted: false };
});

const supportedStructures = selectableLearnerRows.map(row => {
  const source = sourceRows.get(row.sourceKey) as any;
  const representations = (source?.learnerConceptLinks ?? []).flatMap((link: any) => {
    if (link.identityStatus !== 'evidence_backed' || !link.conceptKey) return [];
    return (link.targetIds ?? []).flatMap((targetId: string) => {
      const target = targets.get(targetId) as any;
      const scopeType = representedScopeType(targetId, link.relationKind, link.identityStatus);
      if (!target || scopeType === 'source_observation') return [];
      const regions = target.regionIds.filter((regionId: string) => row.regionIds.includes(regionId));
      return regions.map((regionId: string) => ({ targetId, regionId, scopeType, relationKind: link.relationKind,
        memberCode: link.memberCode ?? null, extentAccepted: false }));
    });
  });
  const compactRepresentations = new Map<string, any>();
  for (const item of representations) compactRepresentations.set(`${item.targetId}|${item.regionId}|${item.scopeType}|${item.relationKind}|${item.memberCode ?? ''}`, item);
  return { sourceKey: row.sourceKey, label: row.label, names: { ...row.names }, side: row.side,
    regionIds: [...row.regionIds], sourceNamespace: 'za-c7010a9', routeAudience: 'learner',
    representedScopes: compactRepresentations.size ? [...compactRepresentations.values()] : [{ scopeType: 'source_observation', targetId: null, regionId: null, extentAccepted: false }],
    humanReview: row.humanReview, publicRedistribution: row.publicRedistribution };
});

const inspectionSources = selectableInspectionRows.map(row => ({ sourceKey: row.sourceKey, label: row.label, names: { ...row.names }, side: row.side,
  regionIds: [...row.regionIds], routeAudience: 'inspection', targetRouteCount: row.targetRoutes.length,
  spatialPlacementStatus: supplement.objects.find((object: any) => object.sourceKey === row.sourceKey)?.spatialPlacementStatus ?? 'unrecorded',
  learnerVisible: false, defaultVisible: row.defaultVisible, sourceOnly: row.sourceOnly,
  humanReview: row.humanReview, publicRedistribution: row.publicRedistribution }));
const supplementMembershipPairs = new Set<string>();
const supplementTargetIds = new Set<string>();
for (const object of supplement.objects) {
  supplementTargetIds.add(object.targetAssociation.targetId);
  for (const regionId of object.regionIds) supplementMembershipPairs.add(`${object.targetAssociation.targetId}|${regionId}`);
}
const membershipPathCount = learnerMembershipRoutes.size;
const targetPathCount = learnerTargets.size;
const unsupportedMemberships = membershipDisposition.filter(row => row.status === 'no_learner_route');
const unsupportedTargets = targetDisposition.filter((row: any) => row.status === 'no_learner_route');
const representedScopeSummary = Object.fromEntries([...scopeRowsByTarget.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([targetId, rows]) => {
  const scopes = new Map<string, any>();
  for (const row of rows) scopes.set(`${row.regionId}|${row.scopeType}|${row.relationKind ?? ''}`,
    { regionId: row.regionId, scopeType: row.scopeType, relationKind: row.relationKind, memberCodePresent: Boolean(row.memberCode) });
  return [targetId, { regionIds: [...new Set(rows.map(row => row.regionId))].sort(), membershipRouteCount: new Set(rows.map(row => row.regionId)).size,
    representedScopes: [...scopes.values()], fullTargetExtentAccepted: false }];
}));
const existingHaBindingRows = overlay.objects.filter((row: any) => row.haConceptId).length;
const uniqueHaConceptIds = new Set(overlay.objects.flatMap((row: any) => row.haConceptId ? [row.haConceptId] : [])).size;
if (existingHaBindingRows !== 130) throw Error(`existing canonical HA binding row count changed: ${existingHaBindingRows}`);
const expectedHistoryCounts = {
  no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package: 2,
  ancestor_surface_representation_present_target_specific_surface_unresolved: 135,
  descendant_surface_representation_present_target_specific_surface_unresolved: 20,
  exact_source_label_observation_identity_crosswalk_needed: 6,
};
if (JSON.stringify(historical163.categoryCounts) !== JSON.stringify(expectedHistoryCounts)
    || Object.values(historical163.categoryCounts).reduce((sum: number, count: number) => sum + count, 0) !== 163)
  throw Error('historical 163 classification drift');

const inputs = [
  'atlas-data/catalog/target-scope-t96.json',
  'atlas-data/overlays/za-local-integration.json',
  'atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json',
  'work/evidence/T100/source-completion-2026-10-01/integration/supplement-target-relation-ledger.json',
  'work/evidence/T100/source-completion-2026-10-01/integration/final-blocker-list.json',
  'work/evidence/T100/source-completion-2026-10-01/integration/final-validation-v9.json',
  'work/evidence/T100/closure-audit-2026-09-30/selection-render-ledger.json',
  'work/evidence/T100/closure-audit-2026-09-30/browser-raster/raster-ledger.json',
  'work/evidence/T100/closure-audit-2026-09-30/browser-declared-right/raster-ledger.json',
  'work/evidence/T100/semantic-relations-2026-09-30/target-gap-classification.json',
];
const sourceHashes: Record<string, string> = {};
for (const path of inputs) sourceHashes[path] = sha(await read(path));
sourceHashes['/__atlas/datasets/human-atlas-local/manifest.json'] = sha(datasetResponse.body);
sourceHashes['/__atlas/integration.json'] = sha(runtimeResponse.body);
const scopeDocument = {
  schemaVersion: 'human-atlas-product-scope-v1', contractRevision: 'app-completion-2026-10-01',
  pipeline: { builder: 'atlas-web/scripts/buildProductScope.ts', runtimeSource: '/__atlas/integration.json', runtimeProjectionSchema: runtime.projectionSchema },
  sourceHashes,
  denominators: { targets: scope.targets.length, memberships: allMemberships.size, regions: scope.regions.length, existingCanonicalHaBindings: existingHaBindingRows,
    uniqueCanonicalHaConceptIds: uniqueHaConceptIds,
    existingSourceOnlyRows: overlay.objects.filter((row: any) => row.sourceOnly === true).length,
    historical163: { denominator: historical163.denominator, categoryCounts: historical163.categoryCounts } },
  learnerRouteCounts: { runtimeRecords: learnerRows.length, selectableNamedSourceStructures: selectableLearnerRows.length,
    searchEntries: allSearchResults.length, directSourceSelectionRoutesExecuted: learnerSelectionPasses.length,
    targetIdsWithVerifiedHistoricalMembershipRoutes: targetPathCount, membershipsWithVerifiedHistoricalRoutes: membershipPathCount,
    targetsWithoutLearnerRoute: unsupportedTargets.length, membershipsWithoutLearnerRoute: unsupportedMemberships.length,
    targetIds: [...learnerTargets].sort(), membershipKeys: [...learnerMembershipRoutes.keys()].sort(), regionalSearchCounts },
  inspectionRouteCounts: { runtimeRecords: inspectionRows.length, selectableSourceObservations: selectableInspectionRows.length,
    directSourceSelectionRoutesExecuted: inspectionSelectionPasses.length,
    sourceObjectTargetRoutes: inspectionRows.reduce((sum, row) => sum + row.targetRoutes.length, 0),
    distinctTargetIds: supplementTargetIds.size, targetMembershipPairs: supplementMembershipPairs.size,
    allInspectionSourcesBlockedInLearnerSearchAndDirectRoutes: true },
  supportedTargetIds: [...learnerTargets].sort(),
  supportedMemberships: [...learnerMembershipRoutes.keys()].sort(),
  supportedStructures,
  representedScopeByTarget: representedScopeSummary,
  learnerDisposition: { targetsWithRoute: [...learnerTargets].sort(), targetsWithoutRoute: unsupportedTargets.map((row: any) => row.targetId).sort(),
    membershipKeysWithRoute: [...learnerMembershipRoutes.keys()].sort(), membershipKeysWithoutRoute: unsupportedMemberships.map(row => `${row.targetId}|${row.regionId}`).sort(),
    dispositionDetailsRef: 'unsupportedDispositionRef.priorSelectionRenderLedger and unsupportedDispositionRef.priorBlockerLedger' },
  observationOnlySources: inspectionSources,
  quarantinedSources: inspectionSources.map(row => ({ sourceKey: row.sourceKey, reason: 'cross-dataset spatial registration remains unaccepted; inspection-only local route', spatialPlacementStatus: row.spatialPlacementStatus })),
  unsupportedDispositionRef: { targetScope: { path: inputs[0], sha256: sourceHashes[inputs[0]!] },
    priorBlockerLedger: { path: inputs[3], sha256: sourceHashes[inputs[3]!] },
    priorSelectionRenderLedger: { path: inputs[5], sha256: sourceHashes[inputs[5]!] },
    membershipDispositionIsRecomputedForCurrentLearnerAudience: true },
  contentCompleteness: { status: 'partial', fullTargetExtentAccepted: 0,
    knownContentGaps: { targetsWithoutLearnerRoute: unsupportedTargets.length, membershipsWithoutLearnerRoute: unsupportedMemberships.length,
      directKoreanTermEvidenceRows: blockers.targetTermEvidenceGapRows.length, spatiallyUnacceptedSupplementObjects: inspectionSources.length,
      unresolvedFinePartVariantGroupAndSideEvidence: true },
    humanReview: 'not_performed', publicRedistribution: 'held', sourceOnlyState: 'per-object; existing ZA rows preserved independently' },
  policy: { learnerAndInspectionRoutesSeparated: true, oneDatasetOneSceneOneRenderer: true,
    supplementSourceOnly: true, publicRedistribution: 'held', humanReview: 'not_performed', newCanonicalHaBindings: 0,
    existingSourceOnlyRows: overlay.objects.filter((row: any) => row.sourceOnly === true).length, supplementSourceOnlyRows: supplement.objects.filter((row: any) => row.rights.sourceOnly === true).length,
    sourceObjectsCreated: 0, geometryChanged: false },
};
if (scopeDocument.learnerRouteCounts.directSourceSelectionRoutesExecuted !== selectableLearnerRows.length
    || scopeDocument.inspectionRouteCounts.distinctTargetIds !== supplementTargetIds.size
    || scopeDocument.inspectionRouteCounts.targetMembershipPairs !== supplementMembershipPairs.size
    || inspectionSources.some(row => row.learnerVisible || row.defaultVisible))
  throw Error('audience scope count invariant');

const outputPath = resolve(projectRoot, 'work/product-scope.json');
const output = JSON.stringify(scopeDocument, null, 2) + '\n';
const conciseSummary = {
  learner: { runtimeRecords: learnerRows.length, selectableNamedSourceStructures: selectableLearnerRows.length,
    searchEntries: allSearchResults.length, directSourceSelectionRoutesExecuted: learnerSelectionPasses.length,
    targetIdsWithVerifiedHistoricalMembershipRoutes: targetPathCount, membershipsWithVerifiedHistoricalRoutes: membershipPathCount,
    targetsWithoutLearnerRoute: unsupportedTargets.length, membershipsWithoutLearnerRoute: unsupportedMemberships.length,
    regionalSearchCounts },
  inspection: { runtimeRecords: inspectionRows.length, selectableSourceObservations: selectableInspectionRows.length,
    directSourceSelectionRoutesExecuted: inspectionSelectionPasses.length, targetIds: supplementTargetIds.size,
    memberships: supplementMembershipPairs.size, defaultVisible: inspectionRows.filter(row => row.defaultVisible).length },
};
if (process.argv.includes('--check')) {
  const current = await readFile(outputPath, 'utf8').catch(() => '');
  if (current !== output) throw Error('work/product-scope.json is stale; run the product-scope builder');
  console.log(JSON.stringify({ status: 'passed', output: 'work/product-scope.json', ...conciseSummary, routeFailures: routeFailures.length }));
} else {
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, output);
  console.log(JSON.stringify({ status: 'written', output: 'work/product-scope.json', ...conciseSummary, routeFailures: routeFailures.length }));
}

const evidencePath = resolve(projectRoot, 'work/evidence/T100/app-completion-2026-10-01/automated-contract.json');
const evidence = {
  schemaVersion: 't100-app-completion-contract-v1', taskId: 'T100', contractRevision: 'app-completion-2026-10-01',
  productScopeSha256: sha(output),
  runtimeSha256: sha(runtimeResponse.body), runtimeBytes: runtimeResponse.body.byteLength,
  datasetSha256: sha(datasetResponse.body), datasetBytes: datasetResponse.body.byteLength,
  denominators: scopeDocument.denominators, routeCounts: { learner: scopeDocument.learnerRouteCounts, inspection: scopeDocument.inspectionRouteCounts },
  selectableRecordContract: { learnerRows: selectableLearnerRows.length, learnerRowsPassed: learnerSelectionPasses.length,
    inspectionRows: selectableInspectionRows.length, inspectionRowsPassed: inspectionSelectionPasses.length, failures },
  baseMembershipRouteReexecution: { distinctReferences: refs.size, targetIdsWithRoute: targetPathCount, membershipPairsWithRoute: membershipPathCount,
    routeFailures: routeFailures.length, routeAudience: 'learner' },
  quarantinePolicy: { inspectionOnlySourceKeys: inspectionSources.map(row => row.sourceKey), learnerSearchLeakCount: 0,
    directLearnerSelectionLeakCount: 0, directLearnerTargetRouteLeakCount: 0, developerInspectionRoutesPassed: inspectionSelectionPasses.length,
    defaultVisibleCount: inspectionRows.filter(row => row.defaultVisible).length },
  regionalSearchCounts, contentCompleteness: scopeDocument.contentCompleteness,
  preserved: { denominators: scopeDocument.denominators, sourceOnly: 'preserved per object; supplement objects are source-only', publicRedistribution: 'held', humanReview: 'not_performed',
    fullTargetExtentAccepted: 0, OpenSimModels: 'not modified by this builder', T13Drafts: 'not modified by this builder' },
  inputs: sourceHashes,
};
const evidenceOutput = JSON.stringify(evidence, null, 2) + '\n';
if (process.argv.includes('--check')) {
  const current = await readFile(evidencePath, 'utf8').catch(() => '');
  if (current !== evidenceOutput) throw Error('automated contract evidence stale; regenerate product-scope first');
} else {
  await mkdir(dirname(evidencePath), { recursive: true });
  await writeFile(evidencePath, evidenceOutput);
}
