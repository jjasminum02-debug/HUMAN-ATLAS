/** Carry physical raster evidence forward only when the selected source,
 * shared geometry and source-specific runtime projection remain identical.
 * All current aliases are revalidated by the shared router. No anatomy or
 * complete target/group acceptance follows from these checks.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildRuntimeIntegration, readDatasetRoute } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const out = 'work/evidence/T100/closure-audit-2026-09-30';
const sha = b => createHash('sha256').update(b).digest('hex');
const bytes = path => readFile(resolve(root,path));
const json = async path => JSON.parse(await bytes(path));
const previousBaselinePath = 'work/evidence/T100/parallel-resolution-2026-09-30/integration/qa-baseline.json';
const current = await json(out + '/qa-baseline.json'), previous = await json(previousBaselinePath);
const previousOverlayRef = process.argv[2];
if (!previousOverlayRef || !/^[a-f0-9]{40}$/.test(previousOverlayRef)) throw Error('Pass the committed integration overlay ref, not a mutable branch');
const oldBytes = execFileSync('git',['show',previousOverlayRef + ':' + previous.overlay.path], { cwd: root, maxBuffer: 16*1024*1024 });
if (sha(oldBytes) !== previous.overlay.sha256) throw Error('Previous overlay ref/hash mismatch');
const nowBytes = await bytes(current.overlay.path);
if (sha(nowBytes) !== current.overlay.sha256) throw Error('Current overlay changed');
for (const key of ['finalT96ScopeSha256','frozenT78ContextSha256','compiledDatasetManifestSha256',
    'rightsEvidenceSha256','runtimeBuilderCodeSha256','datasetSchemaCodeSha256','localViteIntegrationPluginCodeSha256']) {
    if (current.relevantInputHashes[key] !== previous.relevantInputHashes[key]) throw Error('Input requiring new QA: ' + key);
}
// Product renderer/UI cannot silently change while reusing images. Tests and
// offline inspection/capture tools are not product renderer inputs.
const productFiles = execFileSync('git',['ls-tree','-r','--name-only',previousOverlayRef,'atlas-web/src','atlas-web/plugins'], { cwd: root }).toString().trim().split('\n')
    .filter(p => !/\.test\./.test(p));
for (const path of productFiles) {
    const old = execFileSync('git',['show',previousOverlayRef + ':' + path], { cwd: root, maxBuffer: 16*1024*1024 });
    if (sha(old) !== sha(await bytes(path))) throw Error('Renderer/UI input changed: ' + path);
}
const scopeBytes = await bytes('atlas-data/catalog/target-scope-t96.json'), scope = JSON.parse(scopeBytes);
const contextBytes = await bytes('work/evidence/T78/reference/ta2-scope.json');
const dataset = validateDataset(await json('atlas-data/source-cache/datasets/za/compiled/manifest.json'));
const oldOverlay = JSON.parse(oldBytes), newOverlay = JSON.parse(nowBytes);
const rights = sha(await bytes(newOverlay.policy.rightsEvidence));
const lexicon = { sha256: sha(scopeBytes), supportContext: { sha256: sha(contextBytes), terms: JSON.parse(contextBytes) }, targets: scope.targets };
const oldRuntime = buildRuntimeIntegration(oldOverlay,dataset,sha(oldBytes),rights,lexicon);
const newRuntime = buildRuntimeIntegration(newOverlay,dataset,sha(nowBytes),rights,lexicon);
if (sha(Buffer.from(JSON.stringify(oldRuntime))) !== previous.runtime.sha256
    || sha(Buffer.from(JSON.stringify(newRuntime))) !== current.runtime.sha256) throw Error('Runtime projection no longer reproduces either baseline');
const oldObjects = new Map(oldRuntime.objects.map(o => [o.sourceKey,o]));
const newObjects = new Map(newRuntime.objects.map(o => [o.sourceKey,o]));
const inputs = [out + '/browser-raster/raster-ledger.json', out + '/browser-declared-right/raster-ledger.json'];
const cases = new Map(), evidence = [];
for (const path of inputs) {
    const ledger = await json(path);
    if (!ledger.summary.browserRuntime?.verified || ledger.summary.failedOrUnverified || ledger.summary.routeFailures.length || ledger.summary.consoleErrors.length) throw Error('Incomplete/failed raster evidence');
    const old = ledger.summary.overlaySha256 === previous.overlay.sha256;
    if (!old && ledger.summary.overlaySha256 !== current.overlay.sha256) throw Error('Unknown capture revision');
    const expected = old ? previous : current;
    if (ledger.summary.browserRuntime.sha256 !== expected.runtime.sha256) throw Error('Capture response mismatch');
    for (const row of ledger.rows) {
        if (row.status !== 'render_observed' || row.anatomicalVisualQA !== 'pending'
            || row.targetExtent !== 'not_asserted' || !row.uiPixelMaskApplied) throw Error('Raster claim boundary drift');
        if (old && JSON.stringify(oldObjects.get(row.sourceKey)) !== JSON.stringify(newObjects.get(row.sourceKey))) throw Error('Changed selected-source projection requires new capture');
        if (sha(await bytes(row.screenshotLocator)) !== row.screenshotSha256) throw Error('Screenshot missing or changed');
        cases.set(row.caseKey, { row, ledgerPath: path, carriedForward: old });
    }
    if (!ledger.rows.some(r => r.hiddenControlPassed && r.hiddenControlPixelCount <= 20)) throw Error('Missing UI-only negative control');
    evidence.push({ path, sha256: sha(await bytes(path)), overlaySha256: ledger.summary.overlaySha256,
        browserRuntime: ledger.summary.browserRuntime, caseCount: ledger.rows.length });
}
const memberships = [], regions = scope.regions.map(r => r.regionId);
let aliasCount = 0;
for (const membership of current.routeCoverage.memberships) {
    const refs = [];
    for (const path of membership.paths) {
        const query = new URLSearchParams({ regions: membership.regionId, concept: path.conceptKey });
        if (path.side) query.set('side',path.side);
        if (readDatasetRoute('?' + query,newRuntime.objects,regions).selected !== path.sourceKey) throw Error('Current route mismatch');
        const key = membership.regionId + '|' + path.sourceKey, capture = cases.get(key);
        if (!capture || !capture.row.references.some(r => r.targetId === membership.targetId && r.conceptKey === path.conceptKey && r.regionId === membership.regionId)
            || capture.row.routeAliasesChecked !== capture.row.references.length) throw Error('Alias never exercised in browser');
        refs.push({ caseKey: key, evidenceLedger: capture.ledgerPath });
        aliasCount++;
    }
    memberships.push({ targetId: membership.targetId, regionId: membership.regionId,
        availablePathCount: membership.paths.length,
        boundedSelectionRender: refs.length ? 'all_available_paths_exercised_and_render_observed' : 'pending_no_selectable_path',
        caseReferences: [...new Map(refs.map(r => [r.caseKey,r])).values()],
        fullTargetExtent: 'pending; not established by available-path capture', anatomicalSideReview: 'pending',
        geometryAbsenceClaim: false, humanReview: 'not_performed' });
}
const summary = { taskId: 'T100', executionStatus: 'in_progress', acceptance: 'partial',
    nextUnit: current.nextUnit, generatedAt: new Date().toISOString(),
    denominators: { targets: 542, memberships: 563, regions: 12 },
    targetIdsWithPaths: current.routeCoverage.targetIdsWithPathsCount,
    membershipsWithPaths: current.routeCoverage.membershipsWithPathsCount,
    membershipsWithoutPaths: current.routeCoverage.membershipsWithoutPathsCount,
    currentAliasesChecked: aliasCount, actualPhysicalCaptures: cases.size,
    carriedForwardUnchangedCases: [...cases.values()].filter(c => c.carriedForward).length,
    newlyCapturedCases: [...cases.values()].filter(c => !c.carriedForward).length,
    routeFailures: 0, missingOrChangedScreenshots: 0, runtimeErrorsObserved: 0,
    browserRuntimeResponseHashVerified: true, availablePathCaptureComplete: true,
    full542Target563MembershipVisualAcceptance: false, fullTargetExtentPassesClaimed: 0,
    previousOverlayRef, previousOverlaySha256: previous.overlay.sha256, currentOverlaySha256: current.overlay.sha256,
    rendererUiFilesComparedToIntegrationCommit: productFiles.length,
    reuseProof: 'Same compiled geometry/resources, rights, source-specific runtime projections and renderer/UI code; every current alias resolves in the common router. Original images and revision hashes remain unchanged.',
    performance: 'No benchmark repeated. Geometry, renderer, buffer budgets and physical scene unchanged; runtime JSON increased by 25 bytes. GPU/VRAM/total-process memory remain unmeasured limitations, not newly invented acceptance gates.',
    evidence, humanReview: 'not_performed', publicRedistribution: 'held' };
await writeFile(resolve(root,out,'selection-render-ledger.json'),JSON.stringify({ summary, memberships },null,2) + '\n');
console.log(JSON.stringify(summary));
