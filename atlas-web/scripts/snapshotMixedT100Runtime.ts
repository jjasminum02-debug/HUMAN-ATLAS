import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { wholeBodyPlugin } from '../plugins/wholeBody.ts';
import { readDatasetRoute } from '../src/viewer/datasets/integration.ts';
import { resolveSupplementTargetRelations } from '../src/viewer/datasets/supplementRelations.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const args = process.argv.slice(2);
const outArg = args.indexOf('--out');
const outDir = resolve(root, outArg < 0 ? 'work/evidence/T100/source-completion-2026-10-01/integration'
    : args[outArg + 1]);
const evidenceRoot = resolve(root, 'work/evidence/T100/source-completion-2026-10-01/integration');
if ((outArg >= 0 && !args[outArg + 1]) || !outDir.startsWith(evidenceRoot + '/'))
    throw Error('mixed runtime snapshots must use a new T100 integration evidence subdirectory');
const sha = (value: Buffer | string) => createHash('sha256').update(value).digest('hex');
const read = async (path: string) => readFile(resolve(root, path));
const json = async (path: string) => JSON.parse((await read(path)).toString());

let handler: ((req: any, res: any, next: () => void) => unknown) | undefined;
const listeners = new Map<string, Function[]>();
const watcher = {
    add: () => undefined,
    on: (name: string, callback: Function) => { listeners.set(name, [...(listeners.get(name) ?? []), callback]); return watcher; },
    off: () => undefined,
};
wholeBodyPlugin(root).configureServer({
    watcher: watcher as any,
    middlewares: { use: (...args: any[]) => { handler = args.at(-1); } },
    httpServer: { once: () => undefined },
} as any);
if (!handler) throw Error('whole-body plugin integration endpoint was not installed');

async function get(path: string): Promise<{ status: number; body: Buffer; headers: Record<string, string> }> {
    return new Promise((resolvePromise, reject) => {
        const headers: Record<string, string> = {};
        const res: any = {
            statusCode: 200,
            setHeader: (name: string, value: string) => { headers[name.toLowerCase()] = value; },
            end: (body?: Buffer | string) => resolvePromise({ status: res.statusCode, body: Buffer.from(body ?? ''), headers }),
        };
        Promise.resolve(handler!({ url: path, destroyed: false }, res, () => resolvePromise({ status: 404, body: Buffer.alloc(0), headers }))).catch(reject);
    });
}

const endpoint = await get('/__atlas/integration.json');
if (endpoint.status !== 200 || endpoint.headers['content-type'] !== 'application/json'
    || endpoint.headers['cache-control'] !== 'no-store'
    || endpoint.headers['content-length'] !== String(endpoint.body.byteLength))
    throw Error(`mixed runtime endpoint failed: ${endpoint.status}`);
const runtime = JSON.parse(endpoint.body.toString());
const scope = await json('atlas-data/catalog/target-scope-t96.json');
const supplement = await json('atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json');
const sourceElements = await json('work/evidence/T78/source-elements.json');
const partofPath = 'atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt';
const partofBytes = await read(partofPath);
const relationEvidence = resolveSupplementTargetRelations(supplement, {
    targets: scope.targets,
    sourceElements,
    evidenceHashes: { ...supplement.inputSha256, [partofPath]: sha(partofBytes) },
});
const zaOverlayBytes = await read('atlas-data/overlays/za-local-integration.json');
const supplementBytes = await read('atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json');
const scopeBytes = await read('atlas-data/catalog/target-scope-t96.json');
const targetMemberships = new Map<string, { targetId: string; regionId: string }>();
for (const target of scope.targets) for (const regionId of target.regionIds) {
    const key = `${target.id}|${regionId}`;
    targetMemberships.set(key, { targetId: target.id, regionId });
}
const regionIds = scope.regions.map((row: any) => row.regionId);
const observedRefs = new Map<string, any>();
const sourceLedgerPaths = [
    'work/evidence/T100/closure-audit-2026-09-30/browser-raster/raster-ledger.json',
    'work/evidence/T100/closure-audit-2026-09-30/browser-declared-right/raster-ledger.json',
];
const sourceLedgerHashes: Record<string, string> = {};
for (const path of sourceLedgerPaths) {
    const bytes = await read(path);
    sourceLedgerHashes[path] = sha(bytes);
    const ledger = JSON.parse(bytes.toString());
    for (const item of ledger.rows) for (const ref of item.references) {
        const key = `${ref.targetId}|${ref.regionId}|${item.sourceKey}|${ref.conceptKey}`;
        observedRefs.set(key, { ...ref, sourceKey: item.sourceKey, sourceName: item.sourceName, side: item.side });
    }
}

const selectionLedger = await json('work/evidence/T100/closure-audit-2026-09-30/selection-render-ledger.json');
const membershipLedger = new Map(selectionLedger.memberships.map((row: any) => [`${row.targetId}|${row.regionId}`, row]));
const routeFailures: any[] = [];
const routedMemberships = new Set<string>();
const routedTargets = new Set<string>();
let routeOccurrences = 0;
for (const ref of observedRefs.values()) {
    const key = `${ref.targetId}|${ref.regionId}`;
    const expectedMembership = targetMemberships.get(key);
    if (!expectedMembership) { routeFailures.push({ ...ref, reason: 'reference-not-in-frozen-target-scope' }); continue; }
    const route = readDatasetRoute(`?${ref.query}`, runtime.objects, regionIds);
    routeOccurrences++;
    if (route.selected !== ref.sourceKey || !route.regions.includes(ref.regionId)) {
        routeFailures.push({ ...ref, reason: 'mixed-runtime-base-route-mismatch', selected: route.selected, regions: route.regions });
    } else {
        routedMemberships.add(key);
        routedTargets.add(ref.targetId);
    }
}
const oldPathMemberships = selectionLedger.memberships.filter((row: any) => row.availablePathCount > 0).length;
const oldPathTargets = new Set(selectionLedger.memberships.filter((row: any) => row.availablePathCount > 0).map((row: any) => row.targetId)).size;
if (oldPathMemberships !== 427 || oldPathTargets !== 409 || observedRefs.size !== selectionLedger.summary.currentAliasesChecked
    || routeOccurrences !== observedRefs.size)
    throw Error(`historical route input disagrees with frozen summary: refs=${observedRefs.size}, memberships=${oldPathMemberships}, targets=${oldPathTargets}`);

const supplementRelationFailures: any[] = [];
const supplementObjectRoutes = new Set<string>();
const supplementMembershipPairs = new Set<string>();
for (const relation of relationEvidence) {
    const scopeKey = `${relation.targetId}|${relation.regionId}`;
    if (!targetMemberships.has(scopeKey)) {
        supplementRelationFailures.push({ targetId: relation.targetId, regionId: relation.regionId, reason: 'not-in-frozen-scope' });
        continue;
    }
    const route = readDatasetRoute(`?regions=${encodeURIComponent(relation.regionId)}&targetPathKey=${encodeURIComponent(relation.targetRouteKey)}`, runtime.objects, regionIds, 'inspection');
    if (route.selected !== relation.sourceKey || route.targetPathKey !== relation.targetRouteKey || route.regions.join(',') !== relation.regionId) {
        supplementRelationFailures.push({ ...relation, reason: 'mixed-runtime-supplement-route-mismatch', selected: route.selected, regions: route.regions });
        continue;
    }
    supplementObjectRoutes.add(`${scopeKey}|${relation.sourceKey}`);
    supplementMembershipPairs.add(scopeKey);
    routedMemberships.add(scopeKey);
    routedTargets.add(relation.targetId);
}
if (routeFailures.length || supplementRelationFailures.length) throw Error(`mixed runtime route verification failures: ${routeFailures.length}/${supplementRelationFailures.length}`);

const missingMemberships = [...targetMemberships.values()].filter(({ targetId, regionId }) => !routedMemberships.has(`${targetId}|${regionId}`));
const routeBodySha256 = sha(endpoint.body);
const routeSummary = {
    schemaVersion: 't100-mixed-runtime-route-validation-v2',
    taskId: 'T100',
    nextUnit: 'resolve-target-representation-and-final-scene-qa',
    baselineHead: '3a04aa4049f1d0948c760eb1962fcf9cc215953b',
    generatedAt: new Date().toISOString(),
    runtimeEndpoint: { path: '/__atlas/integration.json', status: endpoint.status, sha256: routeBodySha256, bytes: endpoint.body.byteLength },
    denominators: { targets: scope.targets.length, memberships: targetMemberships.size, regions: scope.regions.length },
    baseRevisionCoverage: { targetsWithRoutedMemberships: oldPathTargets, membershipRowsWithRoutes: oldPathMemberships, routeOccurrencesValidated: routeOccurrences, distinctCapturedReferences: observedRefs.size },
    supplementDelta: {
        targetsWithRoutes: new Set(relationEvidence.map((row: any) => row.targetId)).size,
        membershipPairsWithRoutes: supplementMembershipPairs.size,
        sourceObjectRoutes: supplementObjectRoutes.size,
    },
    combinedCoverage: { targetsWithRoutedMemberships: routedTargets.size, membershipRowsWithRoutes: routedMemberships.size, targetsWithoutAnyRoutedMembership: scope.targets.length - routedTargets.size, membershipsWithoutAnyRoute: missingMemberships.length },
    routeFailures: [],
    missingMemberships,
    fullExtentAcceptance: false,
    anatomicalHumanReview: 'not_performed',
    rights: { sourceOnly: true, publicRedistribution: 'held' },
    provenance: {
        overlaySha256: sha(zaOverlayBytes), supplementManifestSha256: sha(supplementBytes), targetScopeSha256: sha(scopeBytes),
        sourceElementsSha256: sha(await read('work/evidence/T78/source-elements.json')),
        partOfSha256: sha(partofBytes), historicalRasterLedgerHashes: sourceLedgerHashes,
        historicalMembershipLedgerSha256: sha(await read('work/evidence/T100/closure-audit-2026-09-30/selection-render-ledger.json')),
    },
    claimBoundary: 'Base route aliases are re-executed through the current v5 mixed-runtime router in the learner audience. The 13 supplement member routes are developer-only source-observation selections. Neither establishes full target/group extent, anatomical approval, or visual acceptance.',
};
const targetRelationLedger = {
    schemaVersion: 't100-supplement-target-relation-ledger-v1', taskId: 'T100', generatedAt: new Date().toISOString(),
    sourceOnly: true, canonicalHaBindingCreated: false, publicRedistribution: 'held', humanReview: 'not_performed',
    relations: relationEvidence,
    provenance: routeSummary.provenance,
};
await mkdir(outDir, { recursive: true });
await writeFile(resolve(outDir, 'mixed-runtime-route-validation.json'), JSON.stringify(routeSummary, null, 2) + '\n');
await writeFile(resolve(outDir, 'supplement-target-relation-ledger.json'), JSON.stringify(targetRelationLedger, null, 2) + '\n');
console.log(JSON.stringify({ runtimeSha256: routeBodySha256, runtimeBytes: endpoint.body.byteLength, baseRoutes: routeOccurrences,
    supplementMembershipPairs: supplementMembershipPairs.size, supplementObjectRoutes: supplementObjectRoutes.size,
    combinedTargetsWithRoutes: routedTargets.size, combinedMembershipsWithRoutes: routedMemberships.size,
    targetsWithoutRoutes: routeSummary.combinedCoverage.targetsWithoutAnyRoutedMembership, membershipsWithoutRoutes: missingMemberships.length }));
