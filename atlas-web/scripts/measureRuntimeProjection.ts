import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { buildRuntimeIntegration } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(process.cwd(), '..');
const overlayBytes = await readFile(resolve(root, 'atlas-data/overlays/za-local-integration.json'));
const targetScopeBytes = await readFile(resolve(root, 'atlas-data/catalog/target-scope-t96.json'));
const targetScope = JSON.parse(targetScopeBytes.toString('utf8')) as { targets: Array<{id:string;term:{english:string;latin:string;sourceSynonyms:Record<string,string[]>};semanticKind:string;regionIds:string[]}> };
const semanticBaseline = JSON.parse(await readFile(resolve(root, 'work/evidence/T100/semantic-relations-2026-09-30/start-baseline.json'), 'utf8')) as {
    preservedUnnamedSurfaceState: Array<{ sourceKey: string }>;
};
const targetScopeSha256 = createHash('sha256').update(targetScopeBytes).digest('hex');
const supportContextBytes = await readFile(resolve(root, 'work/evidence/T78/reference/ta2-scope.json'));
const frozenTargetLexicon = { sha256: targetScopeSha256, targets: targetScope.targets, supportContext: { sha256: createHash('sha256').update(supportContextBytes).digest('hex'), terms: JSON.parse(supportContextBytes.toString()) } };
const overlayText = overlayBytes.toString('utf8');
const overlay = JSON.parse(overlayText);
const dataset = validateDataset(JSON.parse(await readFile(resolve(root, 'atlas-data/source-cache/datasets/za/compiled/manifest.json'), 'utf8')));
const rightsBytes = await readFile(resolve(root, overlay.policy.rightsEvidence));
const rightsEvidenceSha256 = createHash('sha256').update(rightsBytes).digest('hex');
const sourceOverlaySha256 = createHash('sha256').update(overlayBytes).digest('hex');
// Warm the same deterministic projection path, then measure several complete
// build+ledger-validation passes over the current T100 inputs. This avoids
// reporting a single cold sample as a stable processing budget.
buildRuntimeIntegration(overlay, dataset, sourceOverlaySha256, rightsEvidenceSha256, frozenTargetLexicon);
const buildValidationSamplesMs: number[] = [];
let projection = buildRuntimeIntegration(overlay, dataset, sourceOverlaySha256, rightsEvidenceSha256, frozenTargetLexicon);
for (let index = 0; index < 9; index++) {
    const started = performance.now();
    projection = buildRuntimeIntegration(overlay, dataset, sourceOverlaySha256, rightsEvidenceSha256, frozenTargetLexicon);
    buildValidationSamplesMs.push(performance.now() - started);
}
const buildAndValidationMs = [...buildValidationSamplesMs].sort((a, b) => a - b)[Math.floor(buildValidationSamplesMs.length / 2)];

const bySourceKey = new Map(overlay.objects.map((row: { sourceKey: string; sourceName: string }) => [row.sourceKey, row]));
const semanticQueryLabels = [...new Set(semanticBaseline.preservedUnnamedSurfaceState.map(item => {
    const row = bySourceKey.get(item.sourceKey);
    if (!row) throw Error(`frozen unnamed surface missing from current overlay: ${item.sourceKey}`);
    return row.sourceName.replace(/\.[lr]$/i, '');
}))].sort();
if (semanticQueryLabels.length !== 113)
    throw Error(`expected 113 side-deduplicated source labels, got ${semanticQueryLabels.length}`);
const targetTerms = targetScope.targets.map(target => ({
    id: target.id,
    values: [...new Set([target.term.english, target.term.latin, ...Object.values(target.term.sourceSynonyms).flat()].filter(Boolean))],
}));
const normalize = (value: string) => Array.from(value.normalize('NFKC').toLocaleLowerCase()).filter(char => /[\p{L}\p{N}]/u.test(char)).join('');
const exactTermIndex = new Map<string, Map<string, Set<string>>>();
for (const target of targetTerms) {
    for (const value of target.values) {
        const normalized = normalize(value);
        const byTarget = exactTermIndex.get(normalized) ?? new Map<string, Set<string>>();
        const values = byTarget.get(target.id) ?? new Set<string>();
        values.add(value);
        byTarget.set(target.id, values);
        exactTermIndex.set(normalized, byTarget);
    }
}
const fullScanQuery = (label: string) => targetTerms.flatMap(target => {
    const matched = target.values.filter(value => normalize(value) === normalize(label));
    return matched.length ? [{ id: target.id, values: matched.sort() }] : [];
});
const indexedQuery = (label: string) => [...(exactTermIndex.get(normalize(label)) ?? new Map())]
    .map(([id, values]) => ({ id, values: [...values].sort() }))
    .sort((left, right) => left.id.localeCompare(right.id));
const signature = (matches: Array<{id:string;values:string[]}>) => JSON.stringify(matches.map(row => ({id:row.id,values:[...row.values].sort()})).sort((a,b) => a.id.localeCompare(b.id)));
for (const label of semanticQueryLabels) {
    if (signature(fullScanQuery(label)) !== signature(indexedQuery(label)))
        throw Error(`indexed semantic lookup differs from full scan for ${label}`);
}
function medianQueryBatchMs(query: (label: string) => unknown): number {
    const samples: number[] = [];
    for (let round = 0; round < 9; round++) {
        const start = performance.now();
        let matchCount = 0;
        for (const label of semanticQueryLabels) {
            const result = query(label);
            if (Array.isArray(result)) matchCount += result.length;
        }
        if (matchCount < 0) throw Error('unreachable semantic lookup count');
        samples.push(performance.now() - start);
    }
    return samples.sort((a, b) => a - b)[Math.floor(samples.length / 2)];
}
const fullScanQueryMedianMs = medianQueryBatchMs(fullScanQuery);
const indexedLookupMedianMs = medianQueryBatchMs(indexedQuery);
const rawCompact = JSON.stringify(overlay);
const runtimeJson = JSON.stringify(projection);
const rawBytes = Buffer.from(rawCompact);
const runtimeBytes = Buffer.from(runtimeJson);

function medianParseMs(serialized: string, rounds = 9): number {
    const samples: number[] = [];
    for (let index = 0; index < rounds; index++) {
        const start = performance.now();
        JSON.parse(serialized);
        samples.push(performance.now() - start);
    }
    return samples.sort((a, b) => a - b)[Math.floor(samples.length / 2)];
}

const result = {
    schema: 't100-runtime-projection-measurement-v1',
    measuredAt: new Date().toISOString(),
    nodeVersion: process.version,
    parseMedianRounds: 9,
    buildValidationRounds: buildValidationSamplesMs.length,
    buildValidationSamplesMs: buildValidationSamplesMs.map(value => Number(value.toFixed(3))),
    sourceOverlaySha256,
    rightsEvidenceSha256,
    frozenTargetScopeSha256: targetScopeSha256,
    datasetRevision: dataset.revision,
    datasetManifestSha256: createHash('sha256').update(await readFile(resolve(root, 'atlas-data/source-cache/datasets/za/compiled/manifest.json'))).digest('hex'),
    records: projection.objects.length,
    locallyDisplayable: projection.objects.filter(row => row.localDisplayEligible).length,
    haBoundRows: projection.objects.filter(row => row.haConceptId !== null).length,
    frozenScope: projection.scope,
    rawOverlayFileBytes: overlayBytes.byteLength,
    rawLedgerCompactResponseBytes: rawBytes.byteLength,
    runtimeProjectionResponseBytes: runtimeBytes.byteLength,
    responseByteReductionPercent: Number(((1 - runtimeBytes.byteLength / rawBytes.byteLength) * 100).toFixed(2)),
    rawLedgerGzipEstimateBytes: gzipSync(rawBytes).byteLength,
    runtimeProjectionGzipEstimateBytes: gzipSync(runtimeBytes).byteLength,
    gzipMeasurement: 'estimate only; local Vite plugin sends uncompressed JSON and does not claim wire compression',
    rawLedgerParseMedianMs: Number(medianParseMs(rawCompact).toFixed(3)),
    runtimeProjectionParseMedianMs: Number(medianParseMs(runtimeJson).toFixed(3)),
    builderAndFullLedgerValidationMedianMs: Number(buildAndValidationMs.toFixed(3)),
    builderAndFullLedgerValidationMs: Number(buildAndValidationMs.toFixed(3)),
    semanticMatchMode: 'precomputed exact normalized T96 term index; no per-surface full-target rescan',
    repeatedSearchBenchmark: {
        sourceConceptLabels: semanticQueryLabels.length,
        frozenTargets: targetTerms.length,
        rounds: 9,
        fullScanQueryMedianMs: Number(fullScanQueryMedianMs.toFixed(3)),
        indexedLookupMedianMs: Number(indexedLookupMedianMs.toFixed(3)),
        relativeSpeedup: Number((fullScanQueryMedianMs / Math.max(indexedLookupMedianMs, 0.000001)).toFixed(2)),
        exactResultsMatch: true,
        method: 'same 113 labels and 542 target terms; one normalized exact index reused vs scanning all target terms for each label; no fuzzy matching',
    },
    evidenceAndTargetCrosswalkFieldsProjected: false,
    publicRedistribution: projection.policy.publicRedistribution,
    humanReview: projection.policy.humanReview,
    sourceOnlyRows: projection.objects.filter(row => row.sourceOnly).length,
};
const evidencePath = resolve(root, 'work/evidence/T100/semantic-relations-2026-09-30/runtime-projection-measurement.json');
await mkdir(resolve(root, 'work/evidence/T100/semantic-relations-2026-09-30'), { recursive: true });
await writeFile(evidencePath, JSON.stringify(result, null, 2) + '\n');
process.stdout.write(JSON.stringify(result, null, 2) + '\n');
