import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { buildRuntimeIntegration } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

const root = resolve(process.cwd(), '..');
const overlayBytes = await readFile(resolve(root, 'atlas-data/overlays/za-local-integration.json'));
const overlayText = overlayBytes.toString('utf8');
const overlay = JSON.parse(overlayText);
const dataset = validateDataset(JSON.parse(await readFile(resolve(root, 'atlas-data/source-cache/datasets/za/compiled/manifest.json'), 'utf8')));
const rightsBytes = await readFile(resolve(root, overlay.policy.rightsEvidence));
const rightsEvidenceSha256 = createHash('sha256').update(rightsBytes).digest('hex');
const sourceOverlaySha256 = createHash('sha256').update(overlayBytes).digest('hex');
const started = performance.now();
const projection = buildRuntimeIntegration(overlay, dataset, sourceOverlaySha256, rightsEvidenceSha256);
const buildAndValidationMs = performance.now() - started;
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
    sourceOverlaySha256,
    rightsEvidenceSha256,
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
    builderAndFullLedgerValidationMs: Number(buildAndValidationMs.toFixed(3)),
    evidenceAndTargetCrosswalkFieldsProjected: false,
    publicRedistribution: projection.policy.publicRedistribution,
    humanReview: projection.policy.humanReview,
    sourceOnlyRows: projection.objects.filter(row => row.sourceOnly).length,
};
process.stdout.write(JSON.stringify(result, null, 2) + '\n');
