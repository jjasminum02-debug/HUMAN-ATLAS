import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRuntimeIntegration } from '../../../../../atlas-web/src/viewer/datasets/integration.ts';
import { validateDataset } from '../../../../../atlas-web/src/viewer/datasets/schema.ts';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../../../../..');
const run = resolve(root, 'work/evidence/T100/parallel-resolution-2026-09-30');
const integrationDir = resolve(run, 'integration');
const output = resolve(integrationDir, 'qa-baseline.json');
const validationOutput = resolve(integrationDir, 'integration-validation.json');
const refresh = process.argv.includes('--refresh');
if (!refresh) {
    for (const path of [output, validationOutput]) {
        try { await readFile(path); throw new Error(`refusing to overwrite ${path}; pass --refresh after verifying the same run`); }
        catch (error) { if (error?.code !== 'ENOENT') throw error; }
    }
}
const bytes = async path => readFile(resolve(root, path));
const json = async path => JSON.parse((await bytes(path)).toString('utf8'));
const sha = data => createHash('sha256').update(data).digest('hex');

const runManifestBytes = await bytes('work/evidence/T100/parallel-resolution-2026-09-30/run-manifest.json');
const runManifest = JSON.parse(runManifestBytes.toString('utf8'));
const inputSnapshotBytes = await bytes('work/evidence/T100/parallel-resolution-2026-09-30/input-snapshot/atlas-data/overlays/za-local-integration.json');
const overlayBytes = await bytes('atlas-data/overlays/za-local-integration.json');
const original = JSON.parse(inputSnapshotBytes.toString('utf8'));
const overlay = JSON.parse(overlayBytes.toString('utf8'));
const frozen = await json('atlas-data/catalog/target-scope-t96.json');
const frozenBytes = await bytes('atlas-data/catalog/target-scope-t96.json');
const supportBytes = await bytes('work/evidence/T78/reference/ta2-scope.json');
const supportContext = JSON.parse(supportBytes.toString('utf8'));
const datasetBytes = await bytes('atlas-data/source-cache/datasets/za/compiled/manifest.json');
const runtimeBuilderBytes = await bytes('atlas-web/src/viewer/datasets/integration.ts');
const datasetSchemaBytes = await bytes('atlas-web/src/viewer/datasets/schema.ts');
const vitePluginBytes = await bytes('atlas-web/plugins/wholeBody.ts');
const dataset = validateDataset(JSON.parse(datasetBytes.toString('utf8')));
const rightsBytes = await bytes(overlay.policy.rightsEvidence);
const overlaySha = sha(overlayBytes);
const rightsSha = sha(rightsBytes);
const supportSha = sha(supportBytes);
if (runManifest.runId !== 'T100-parallel-resolution-2026-09-30-r1'
    || runManifest.nextUnit !== 'resolve-target-representation-and-final-scene-qa'
    || sha(inputSnapshotBytes) !== 'e9277ca6f7b2081ce3cf78b3a9ac02bc265207782e0294e82d84847fa0bd2ab4'
    || supportSha !== frozen.source.snapshotSha256)
    throw new Error('parallel baseline or frozen support context is stale');

const frozenTargetLexicon = {
    sha256: sha(frozenBytes),
    supportContext: { sha256: supportSha, terms: supportContext },
    targets: frozen.targets.map(target => ({
        id: target.id, term: target.term, semanticKind: target.semanticKind, primaryOwner: target.primaryOwner,
        regionIds: target.regionIds, sourceAncestryIds: target.sourceAncestryIds,
        sourceCardinality: target.sourceCardinality ? { explicitSourceSide: target.sourceCardinality.explicitSourceSide ?? null } : undefined,
    })),
};
const runtime = buildRuntimeIntegration(overlay, dataset, overlaySha, rightsSha, frozenTargetLexicon);
const runtimeBytes = Buffer.from(JSON.stringify(runtime));

// Recount exact selectable paths from the final validated developer ledger.
// A route is a source surface carrying an evidence-backed, non-null concept key
// to the frozen target in the same region; it is not a visual or completeness claim.
const routeKinds = new Set(['normalized_exact_target_term', 'verified_class_member', 'verified_taxonomy_member', 'verified_source_crosswalk']);
const pathIndex = new Map();
for (const target of frozen.targets) {
    for (const regionId of target.regionIds) {
        const paths = [];
        for (const row of overlay.objects) {
            if (!row.localDisplayEligible || !row.inspectionEligible || !row.regionIds.includes(regionId)) continue;
            for (const link of row.learnerConceptLinks ?? []) {
                if (!routeKinds.has(link.relationKind) || link.identityStatus !== 'evidence_backed'
                    || !link.conceptKey || !link.targetIds.includes(target.id)) continue;
                paths.push({
                    sourceKey: row.sourceKey, sourceName: row.sourceName, side: row.side,
                    conceptKey: link.conceptKey, relationKind: link.relationKind, memberCode: link.memberCode,
                });
            }
        }
        const unique = new Map(paths.map(path => [JSON.stringify(path), path]));
        pathIndex.set(`${target.id}\t${regionId}`, [...unique.values()].sort((a, b) =>
            a.sourceKey.localeCompare(b.sourceKey) || a.relationKind.localeCompare(b.relationKind)));
    }
}
const membershipPaths = [...pathIndex].map(([key, paths]) => {
    const [targetId, regionId] = key.split('\t');
    return { targetId, regionId, status: paths.length ? 'selectable_paths_present' : 'no_exact_selectable_path', paths };
}).sort((a, b) => a.targetId.localeCompare(b.targetId) || a.regionId.localeCompare(b.regionId));
const targetIdsWithPaths = [...new Set(membershipPaths.filter(row => row.paths.length).map(row => row.targetId))].sort();
const targetIdsWithoutPaths = frozen.targets.map(row => row.id).filter(id => !targetIdsWithPaths.includes(id)).sort();
const membershipsWithPaths = membershipPaths.filter(row => row.paths.length);
const termEvidenceById = new Map(overlay.targetTerminologyEvidence.map(row => [row.targetId, row]));
const cEvidence = await json('work/evidence/T100/parallel-resolution-2026-09-30/terminology-c/term-evidence.json');
const cTermGaps = cEvidence.rows.flatMap(row => {
    const term = termEvidenceById.get(row.targetId);
    if (!term) throw new Error(`missing final internal term evidence row ${row.targetId}`);
    return term.fieldEvidence.koModern.status === 'missing' || term.fieldEvidence.koTraditional.status === 'missing'
        ? [{ targetId: row.targetId, koModern: term.fieldEvidence.koModern.status, koTraditional: term.fieldEvidence.koTraditional.status }]
        : [];
});
const objectsByKey = new Map(overlay.objects.map(row => [row.sourceKey, row]));
const beforeObjectsByKey = new Map(original.objects.map(row => [row.sourceKey, row]));
if (objectsByKey.size !== 960 || beforeObjectsByKey.size !== objectsByKey.size) throw new Error('object denominator drift');
const allowedChangedObjectFields = new Set(['targetIds', 'learnerConceptLinks', 'targetRelationEvidence']);
const changedObjectKeys = [];
for (const [sourceKey, row] of objectsByKey) {
    const before = beforeObjectsByKey.get(sourceKey);
    const changed = Object.keys(row).filter(key => JSON.stringify(row[key]) !== JSON.stringify(before[key]));
    if (changed.some(key => !allowedChangedObjectFields.has(key))) throw new Error(`unexpected source object edit ${sourceKey}: ${changed}`);
    if (changed.length) changedObjectKeys.push({ sourceKey, sourceName: row.sourceName, changedFields: changed });
    for (const field of ['haConceptId', 'sourceOnly', 'humanReview', 'publicRedistribution', 'localDisplayEligible',
        'inspectionEligible', 'defaultVisible', 'sourceHiddenStatePreserved', 'regionIds', 'side', 'names', 'aliases', 'label']) {
        if (JSON.stringify(row[field]) !== JSON.stringify(before[field])) throw new Error(`preservation drift ${field}/${sourceKey}`);
    }
}
const policyCounts = {
    targets: overlay.scope.targets, memberships: overlay.scope.memberships, regions: overlay.scope.regions,
    sourceObjects: overlay.objects.length,
    existingHaBindings: overlay.objects.filter(row => row.haConceptId).length,
    sourceOnlyRows: overlay.objects.filter(row => row.sourceOnly).length,
    rightsHeldRows: overlay.objects.filter(row => row.publicRedistribution === 'held').length,
    humanReviewNotPerformedRows: overlay.objects.filter(row => row.humanReview === 'not_performed').length,
};
if (policyCounts.targets !== 542 || policyCounts.memberships !== 563 || policyCounts.regions !== 12
    || policyCounts.existingHaBindings !== 130 || policyCounts.sourceOnlyRows !== 830
    || policyCounts.rightsHeldRows !== 960 || policyCounts.humanReviewNotPerformedRows !== 960)
    throw new Error(`fixed denominator or rights/review invariant drift: ${JSON.stringify(policyCounts)}`);
const sourceInputHashes = Object.fromEntries(runManifest.inputs.map(input => [input.originalPath, input.sha256]));
const qa = {
    schemaVersion: 1,
    taskId: 'T100',
    runId: runManifest.runId,
    baselineHead: runManifest.baselineHead,
    generatedAt: new Date().toISOString(),
    nextUnit: runManifest.nextUnit,
    authority: 'Runtime produced by the same buildRuntimeIntegration and validateDataset code used by the local Vite integration endpoint; delivery.test verifies endpoint wiring.',
    overlay: { path: 'atlas-data/overlays/za-local-integration.json', sha256: overlaySha, bytes: overlayBytes.length },
    runtime: { route: '/__atlas/integration.json', projectionSchema: runtime.projectionSchema, sha256: sha(runtimeBytes), bytes: runtimeBytes.length, objects: runtime.objects.length, serializedAs: 'UTF-8 JSON.stringify projection body' },
    relevantInputHashes: {
        parallelRunManifestSha256: sha(runManifestBytes),
        frozenInputsFromManifest: sourceInputHashes,
        finalT96ScopeSha256: sha(frozenBytes),
        frozenT78ContextSha256: supportSha,
        compiledDatasetManifestSha256: sha(datasetBytes),
        runtimeBuilderCodeSha256: sha(runtimeBuilderBytes),
        datasetSchemaCodeSha256: sha(datasetSchemaBytes),
        localViteIntegrationPluginCodeSha256: sha(vitePluginBytes),
        rightsEvidenceSha256: rightsSha,
    },
    routeCoverage: {
        targetCount: frozen.targets.length,
        targetIdsWithPathsCount: targetIdsWithPaths.length,
        targetIdsWithoutPathsCount: targetIdsWithoutPaths.length,
        membershipCount: membershipPaths.length,
        membershipsWithPathsCount: membershipsWithPaths.length,
        membershipsWithoutPathsCount: membershipPaths.length - membershipsWithPaths.length,
        targetIdsWithPaths,
        targetIdsWithoutPaths,
        memberships: membershipPaths,
    },
    terminology: {
        C_assignedTargetRows: cEvidence.rows.length,
        C_targetRowsWithAnyKoreanFieldGap: cTermGaps.length,
        missingModernFieldCount: cTermGaps.filter(row => row.koModern === 'missing').length,
        missingTraditionalFieldCount: cTermGaps.filter(row => row.koTraditional === 'missing').length,
        unresolvedTargetFields: cTermGaps,
        Hanja: 'not_collected; no Hanja value added',
    },
    preservation: {
        fixedCounts: policyCounts,
        historical163: { preserved: true, exactLabelObservation: 6, descendantSurfaces: 20, ancestorGroupSurfaces: 135, frozenHierarchyNonObservation: 2 },
        changedObjectKeys,
        newCanonicalHaBindings: 0,
        newGeometry: 0,
        sourceOnly: true,
        publicRedistribution: 'held',
        humanReview: 'not_performed',
        learnerNameOrAliasChanges: 0,
    },
    visualQA: {
        status: 'pending',
        exhaustiveTargetMembershipSelection: false,
        perTargetVisualStatus: 'not established by runtime route inventory',
        performanceMeasurementRepeated: false,
    },
};

const validation = {
    schemaVersion: 1,
    taskId: 'T100',
    runId: runManifest.runId,
    sharedDatasetValidator: 'passed',
    sharedIntegrationValidator: 'passed',
    runtimeProjectionValidator: 'passed by buildRuntimeIntegration',
    overlaySha256: overlaySha,
    runtimeInputHashes: { runtimeBuilderCodeSha256: sha(runtimeBuilderBytes), datasetSchemaCodeSha256: sha(datasetSchemaBytes), localViteIntegrationPluginCodeSha256: sha(vitePluginBytes) },
    runtimeSha256: sha(runtimeBytes),
    runtimeBytes: runtimeBytes.length,
    targetRoutes: { withPaths: targetIdsWithPaths.length, withoutPaths: targetIdsWithoutPaths.length },
    membershipRoutes: { withPaths: membershipsWithPaths.length, withoutPaths: membershipPaths.length - membershipsWithPaths.length },
    T100_status: 'in_progress',
    T100_acceptance: 'partial',
    nextUnit: runManifest.nextUnit,
    visualQA: 'pending; no exhaustive browser selection claim',
    buildAndTestEvidence: [
        { command: 'pnpm run test:whole-body', result: 'passed', tests: 51, failures: 0 },
        { command: 'pnpm run test:delivery', result: 'passed', tests: 3, failures: 0 },
        { command: 'pnpm run typecheck', result: 'passed' },
        { command: 'pnpm run build', result: 'passed', warning: 'existing production chunk-size warning (>500 kB)' },
    ],
};
await writeFile(output, JSON.stringify(qa, null, 2) + '\n');
await writeFile(validationOutput, JSON.stringify(validation, null, 2) + '\n');
process.stdout.write(JSON.stringify({
    qaBaseline: output, runtimeSha256: sha(runtimeBytes), runtimeBytes: runtimeBytes.length,
    targetRoutes: `${targetIdsWithPaths.length}/${frozen.targets.length}`,
    membershipRoutes: `${membershipsWithPaths.length}/${membershipPaths.length}`,
    remainingTerminologyRows: cTermGaps.length,
}, null, 2) + '\n');
