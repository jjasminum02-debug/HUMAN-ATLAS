/** Snapshot current, validated selectable paths without rewriting historical QA.
 * No anatomy/extent acceptance or inherited test results are generated here.
 */
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRuntimeIntegration, readDatasetRoute } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const args = process.argv.slice(2);
const arg = (key, fallback) => { const n = args.indexOf(key); return n < 0 ? fallback : args[n + 1]; };
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const bytes = path => readFile(resolve(root, path));
const json = async path => JSON.parse(await bytes(path));
const overlayPath = 'atlas-data/overlays/za-local-integration.json';
const overlayBytes = await bytes(overlayPath), overlay = JSON.parse(overlayBytes);
const scopeBytes = await bytes('atlas-data/catalog/target-scope-t96.json'), scope = JSON.parse(scopeBytes);
const contextBytes = await bytes('work/evidence/T78/reference/ta2-scope.json');
const datasetBytes = await bytes('atlas-data/source-cache/datasets/za/compiled/manifest.json');
const rightsBytes = await bytes(overlay.policy.rightsEvidence);
const dataset = validateDataset(JSON.parse(datasetBytes));
const runtime = buildRuntimeIntegration(overlay, dataset, sha(overlayBytes), sha(rightsBytes),
    { sha256: sha(scopeBytes), supportContext: { sha256: sha(contextBytes), terms: JSON.parse(contextBytes) }, targets: scope.targets });
const counts = { targets: scope.targets.length, memberships: scope.targets.reduce((n,t) => n + t.regionIds.length, 0),
    regions: scope.regions.length, sourceObjects: overlay.objects.length,
    existingHaBindings: overlay.objects.filter(o => o.haConceptId).length,
    sourceOnlyRows: overlay.objects.filter(o => o.sourceOnly).length,
    rightsHeldRows: overlay.objects.filter(o => o.publicRedistribution === 'held').length,
    humanReviewNotPerformedRows: overlay.objects.filter(o => o.humanReview === 'not_performed').length };
if (JSON.stringify(Object.values(counts)) !== JSON.stringify([542,563,12,960,130,830,960,960])) throw Error('Preservation invariant drift');
const kinds = new Set(['normalized_exact_target_term','verified_class_member','verified_taxonomy_member','verified_source_crosswalk']);
const memberships = [], regionIds = scope.regions.map(r => r.regionId);
for (const target of scope.targets) for (const regionId of target.regionIds) {
    const paths = [];
    for (const row of overlay.objects) {
        if (!row.localDisplayEligible || !row.inspectionEligible || !row.regionIds.includes(regionId)) continue;
        for (const link of row.learnerConceptLinks ?? []) {
            if (!kinds.has(link.relationKind) || link.identityStatus !== 'evidence_backed' || !link.conceptKey || !link.targetIds.includes(target.id)) continue;
            const query = new URLSearchParams({ regions: regionId, concept: link.conceptKey });
            if (row.side) query.set('side', row.side);
            if (readDatasetRoute('?' + query, runtime.objects, regionIds).selected !== row.sourceKey) throw Error('Route mismatch');
            paths.push({ sourceKey: row.sourceKey, sourceName: row.sourceName, side: row.side,
                conceptKey: link.conceptKey, relationKind: link.relationKind, memberCode: link.memberCode });
        }
    }
    const unique = [...new Map(paths.map(p => [JSON.stringify(p),p])).values()]
        .sort((a,b) => a.sourceKey.localeCompare(b.sourceKey) || a.relationKind.localeCompare(b.relationKind));
    memberships.push({ targetId: target.id, regionId, status: unique.length ? 'selectable_paths_present' : 'no_exact_selectable_path', paths: unique });
}
memberships.sort((a,b) => a.targetId.localeCompare(b.targetId) || a.regionId.localeCompare(b.regionId));
const withPaths = [...new Set(memberships.filter(r => r.paths.length).map(r => r.targetId))].sort();
const c = await json('work/evidence/T100/parallel-resolution-2026-09-30/terminology-c/term-evidence.json');
const terms = new Map(overlay.targetTerminologyEvidence.map(t => [t.targetId,t]));
const gaps = c.rows.flatMap(r => {
    const t = terms.get(r.targetId);
    return t.fieldEvidence.koModern.status === 'missing' || t.fieldEvidence.koTraditional.status === 'missing'
        ? [{ targetId: r.targetId, koModern: t.fieldEvidence.koModern.status, koTraditional: t.fieldEvidence.koTraditional.status }] : [];
});
const current = { schemaVersion: 1, taskId: 'T100', runId: 'T100-closure-audit-2026-09-30',
    generatedAt: new Date().toISOString(), nextUnit: 'resolve-target-representation-and-final-scene-qa',
    overlay: { path: overlayPath, sha256: sha(overlayBytes), bytes: overlayBytes.length },
    runtime: { route: '/__atlas/integration.json', sha256: sha(Buffer.from(JSON.stringify(runtime))),
        bytes: Buffer.byteLength(JSON.stringify(runtime)), objects: runtime.objects.length },
    relevantInputHashes: { finalT96ScopeSha256: sha(scopeBytes), frozenT78ContextSha256: sha(contextBytes),
        compiledDatasetManifestSha256: sha(datasetBytes), rightsEvidenceSha256: sha(rightsBytes),
        runtimeBuilderCodeSha256: sha(await bytes('atlas-web/src/viewer/datasets/integration.ts')),
        datasetSchemaCodeSha256: sha(await bytes('atlas-web/src/viewer/datasets/schema.ts')),
        localViteIntegrationPluginCodeSha256: sha(await bytes('atlas-web/plugins/wholeBody.ts')) },
    routeCoverage: { targetCount: counts.targets, targetIdsWithPathsCount: withPaths.length,
        targetIdsWithoutPathsCount: counts.targets - withPaths.length,
        membershipCount: memberships.length, membershipsWithPathsCount: memberships.filter(r => r.paths.length).length,
        membershipsWithoutPathsCount: memberships.filter(r => !r.paths.length).length,
        targetIdsWithPaths: withPaths, targetIdsWithoutPaths: scope.targets.map(t => t.id).filter(id => !withPaths.includes(id)).sort(), memberships },
    terminology: { C_assignedTargetRows: c.rows.length, C_targetRowsWithAnyKoreanFieldGap: gaps.length,
        missingModernFieldCount: gaps.filter(r => r.koModern === 'missing').length,
        missingTraditionalFieldCount: gaps.filter(r => r.koTraditional === 'missing').length, unresolvedTargetFields: gaps,
        Hanja: 'not_collected; no Hanja value added' },
    preservation: { fixedCounts: counts, newCanonicalHaBindings: 0, newGeometry: 0,
        historical163: { preserved: true, exactLabelObservation: 6, descendantSurfaces: 20, ancestorGroupSurfaces: 135, frozenHierarchyNonObservation: 2 } },
    visualQA: { status: 'pending; link snapshots never establish visual/extent acceptance', exhaustiveTargetMembershipSelection: false } };
const out = resolve(root, arg('--out', 'work/evidence/T100/closure-audit-2026-09-30/qa-baseline.json'));
try { await readFile(out); throw Error('Refuse to overwrite an existing baseline'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(current,null,2) + '\n');
console.log(JSON.stringify({ overlaySha256: current.overlay.sha256, runtime: current.runtime,
    targetRoutes: withPaths.length, membershipRoutes: current.routeCoverage.membershipsWithPathsCount }));
