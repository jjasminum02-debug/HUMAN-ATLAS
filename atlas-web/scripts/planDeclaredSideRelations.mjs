/** Independent, explicitly sided source evidence can establish one bounded
 * route while its unsided sibling remains unresolved. Defaults to plan-only;
 * --apply is a guarded single-writer update after the previous QA has ended.
 */
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRuntimeIntegration, readDatasetRoute } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const read = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const sideOf = value => ({ l: 'left', r: 'right' })[value?.match(/\.([lr])$/i)?.[1]?.toLowerCase()] ?? null;
const baseline = await read('work/evidence/T100/parallel-resolution-2026-09-30/integration/qa-baseline.json');
const overlayPath = resolve(root, baseline.overlay.path);
const overlayBytes = await readFile(overlayPath);
if (sha(overlayBytes) !== baseline.overlay.sha256) throw Error('QA input changed; rebase the plan explicitly.');
const original = JSON.parse(overlayBytes), proposed = structuredClone(original);
const scopeBytes = await readFile(resolve(root, 'atlas-data/catalog/target-scope-t96.json'));
const scope = JSON.parse(scopeBytes);
const targets = new Map(scope.targets.map(t => [t.id, t]));
const source = await read('work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json');
if (sha(await readFile(resolve(root, 'work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json')))
    !== baseline.relevantInputHashes.frozenInputsFromManifest['work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json']
    || sha(scopeBytes) !== baseline.relevantInputHashes.finalT96ScopeSha256
    || sha(await readFile(resolve(root, 'atlas-data/source-cache/datasets/za/compiled/manifest.json')))
    !== baseline.relevantInputHashes.compiledDatasetManifestSha256) throw Error('Source identity inputs changed');
const sources = new Map(source.objects.map(s => [s.sourceKey, s]));
const dataset = validateDataset(await read('atlas-data/source-cache/datasets/za/compiled/manifest.json'));
const instances = new Map(dataset.instances.map(i => [i.sourceKey, i]));
const additions = [];
for (const row of proposed.objects) {
    const catalog = sources.get(row.sourceKey), instance = instances.get(row.sourceKey);
    const side = sideOf(row.sourceName);
    const dataSide = sideOf(instance?.dataName);
    if (!side || side !== row.side || side !== catalog?.sourceLabelSide || side !== instance?.sourceLabelSide
        || dataSide && dataSide !== side || row.hardHoldReasons.length || !row.localDisplayEligible || !row.inspectionEligible
        || catalog.name !== instance.sourceName || row.sourceName !== instance.sourceName
        || catalog.evaluatedGeometrySha256 !== instance.evaluatedGeometrySha256) continue;
    for (const proof of [...(row.learnerConceptLinks ?? [])]) {
        if (proof.relationKind !== 'normalized_exact_target_term' || proof.identityStatus !== 'side_conflicted'
            || proof.conceptKey !== null || proof.targetIds.length !== 1) continue;
        const target = targets.get(proof.targetIds[0]);
        if (!target || !target.semanticKind.includes(row.kind) || !target.regionIds.some(id => row.regionIds.includes(id))
            || target.sourceCardinality.explicitSourceSide && target.sourceCardinality.explicitSourceSide !== side) continue;
        const conceptKey = 'LC-' + sha(Buffer.from('independent-declared-side|' + target.id + '|' + row.sourceKey)).slice(0, 20);
        const link = { ...structuredClone(proof), conceptKey, identityStatus: 'evidence_backed',
            matchRule: proof.matchRule + '; independent explicit source object side; paired unsided source remains unresolved' };
        row.learnerConceptLinks.push(link);
        additions.push({ targetId: target.id, sourceKey: row.sourceKey, sourceName: row.sourceName, declaredSide: side,
            link, proof: { sourceCatalogObjectName: catalog.name, sourceLabelSide: catalog.sourceLabelSide,
                compiledObjectName: instance.sourceName, compiledSourceLabelSide: instance.sourceLabelSide,
                dataName: instance.dataName, dataNameHasOpposingExplicitSide: false,
                sourceLocator: catalog.sourceLocator, evaluatedGeometrySha256: catalog.evaluatedGeometrySha256,
                parent: catalog.parent, collections: catalog.collections },
            fullBilateralExtent: false, unsidedMateResolved: false, originalConflictLinkPreserved: true });
    }
}
const contextBytes = await readFile(resolve(root, 'work/evidence/T78/reference/ta2-scope.json'));
const rightsBytes = await readFile(resolve(root, original.policy.rightsEvidence));
const runtime = buildRuntimeIntegration(proposed, dataset, sha(Buffer.from(JSON.stringify(proposed))), sha(rightsBytes),
    { sha256: sha(scopeBytes), supportContext: { sha256: sha(contextBytes), terms: JSON.parse(contextBytes) }, targets: scope.targets });
for (const item of additions) {
    const region = targets.get(item.targetId).primaryOwner;
    const params = new URLSearchParams({ regions: region, concept: item.link.conceptKey, side: item.declaredSide });
    const route = readDatasetRoute('?' + params, runtime.objects, scope.regions.map(r => r.regionId));
    if (route.selected !== item.sourceKey || !route.regions.includes(region)) throw Error('new route did not resolve');
    item.validatedRouteQuery = params.toString();
}
let preservedLinks = 0;
for (let n = 0; n < original.objects.length; n++) {
    const before = structuredClone(original.objects[n]), after = structuredClone(proposed.objects[n]);
    const oldLinks = before.learnerConceptLinks ?? [], newLinks = after.learnerConceptLinks ?? [];
    if (JSON.stringify(oldLinks) !== JSON.stringify(newLinks.slice(0, oldLinks.length))) throw Error('preexisting links changed');
    preservedLinks += oldLinks.length;
    delete before.learnerConceptLinks; delete after.learnerConceptLinks;
    if (JSON.stringify(before) !== JSON.stringify(after)) throw Error('non-link object fields changed');
}
const output = { mode: 'validated_plan_only_not_applied', inputOverlaySha256: sha(overlayBytes), additions,
    addedRelationCount: additions.length, existingLinksPreserved: preservedLinks,
    sourceObjects: original.objects.length, existingHaBindings: original.objects.filter(o => o.haConceptId).length,
    newGeometry: 0, changedNonLinkObjectFields: 0, humanReview: 'not_performed', publicRedistribution: 'held',
    commonValidatorPassed: true, commonRouterPassed: true,
    claimBoundary: 'A declared right/left source is independent bounded evidence. The unsided mate remains conflicted and full extent/visual acceptance is not asserted.',
    applicationBoundary: 'Do not apply while the current QA uses the frozen 4a11 overlay. Preserve that evidence, then apply through the single common writer and inspect the added route.' };
const dest = resolve(root, 'work/evidence/T100/closure-audit-2026-09-30');
await mkdir(dest, { recursive: true });
await writeFile(resolve(dest, 'declared-side-plan.json'), JSON.stringify(output, null, 2) + '\n');
if (process.argv.includes('--apply')) {
    const nextBytes = Buffer.from(JSON.stringify(proposed, null, 2) + '\n');
    if (sha(await readFile(overlayPath)) !== sha(overlayBytes)) throw Error('Concurrent overlay change; refuse to write');
    await writeFile(overlayPath, nextBytes);
    await writeFile(resolve(dest, 'declared-side-application.json'), JSON.stringify({
        ...output, mode: 'applied_bounded_independent_declared_side', appliedAt: new Date().toISOString(),
        outputOverlaySha256: sha(nextBytes), originalConflictLinksChanged: 0,
        priorQaBaselinePreserved: true, requiresNewBaselineAndAddedRouteBrowserCheck: true,
        applicationBoundary: 'Only the independently declared source route was added; unresolved mate and full bilateral extent remain unapproved.'
    }, null, 2) + '\n');
}
console.log(JSON.stringify({ mode: process.argv.includes('--apply') ? 'applied_bounded_independent_declared_side' : output.mode, addedRelationCount: additions.length,
    targetIds: additions.map(a => a.targetId), commonValidatorPassed: true, commonRouterPassed: true,
    productionOverlayChanged: process.argv.includes('--apply') }));
