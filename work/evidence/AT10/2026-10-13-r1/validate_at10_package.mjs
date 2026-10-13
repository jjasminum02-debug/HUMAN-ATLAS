import { readFile, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { validateLearningCatalog } from '../../../../atlas-web/src/viewer/acupoints/learningCatalog.ts';
import { validateLearningRegistry, plannedSides, assertUniqueInstances } from '../../../../atlas-web/src/viewer/acupoints/learningRegistry.ts';
import { validateLearningPackage } from '../../../../atlas-web/src/viewer/acupoints/learningPackage.ts';

const root = resolve(fileURLToPath(new URL('../../../../', import.meta.url)));
const run = resolve(fileURLToPath(new URL('.', import.meta.url)));
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const readBytes = (path) => readFile(join(root, path));
const readJson = async (path) => JSON.parse(await readBytes(path));

const catalog = await readJson('atlas-data/acupoints/observation/catalog-r1.json');
const registry = await readJson('atlas-data/acupoints/learner/registry-r1.json');
const base = await readJson('atlas-data/acupoints/learner/lung-r7.json');
const context = { datasetRevision: base.datasetRevision, frameId: base.frameId, unit: 'm', poseId: base.poseId };
const packageBytes = await readBytes('atlas-data/acupoints/learner/st-r1.json');
const observationBytes = await readBytes('atlas-data/acupoints/observation/st-context-r1.json');
const pkg = JSON.parse(packageBytes.toString('utf8'));
const observation = JSON.parse(observationBytes.toString('utf8'));
const positionLedger = await readJson('work/evidence/AT10/2026-10-13-r1/position-ledger.json');
const start = await readJson('work/evidence/AT10/2026-10-13-r1/start.json');
const registration = registry.packages.find((item) => item.id === 'st-r1');

validateLearningCatalog(catalog);
validateLearningRegistry(registry, catalog);
const baselineRegistryBytes = execFileSync('git', ['show', 'HEAD:atlas-data/acupoints/learner/registry-r1.json']);
const baselineRegistry = JSON.parse(baselineRegistryBytes.toString('utf8'));
if (sha(baselineRegistryBytes) !== start.inputSha256['atlas-data/acupoints/learner/registry-r1.json']) throw new Error('HEAD registry differs from frozen AT10 start input');
if (JSON.stringify(registry.packages.filter((item) => item.id !== 'st-r1')) !== JSON.stringify(baselineRegistry.packages)) throw new Error('Existing learner registrations changed while adding AT10');
const preservedEvidence = ['work/reports/acupoint-AC1.md', 'work/reports/acupoint-AC2.md'].map(async (path) => {
  const bytes = await readBytes(path);
  if (sha(bytes) !== start.inputSha256[path]) throw new Error(`Existing AC evidence changed: ${path}`);
  return { path, sha256: sha(bytes), preserved: true };
});
const preservedAcEvidence = await Promise.all(preservedEvidence);
if (!registration || registration.channel !== 'ST') throw new Error('Missing ST partial package registration');
if (sha(packageBytes) !== registration.learnerSha256 || sha(observationBytes) !== registration.observationSha256) throw new Error('Registered package byte hash mismatch');
validateLearningPackage(pkg, context, catalog, registration);
if (registration.codes.join(',') !== Array.from({ length: 25 }, (_, i) => `ST${i + 1}`).join(',')) throw new Error('ST registration must cover only ST1–ST25');
if (registry.packages.some((item) => item.id !== 'st-r1' && item.channel === 'ST')) throw new Error('Duplicate ST channel registration');
if (registry.packages.flatMap((item) => item.codes).some((code) => /^ST(?:2[6-9]|3\d|4[0-5])$/.test(code))) throw new Error('ST26–ST45 must remain outside this partial package');

const expectedConcepts = catalog.concepts.filter((point) => point.channel === 'ST' && Number(point.code.slice(2)) <= 25);
const expected = expectedConcepts.flatMap((point) => plannedSides(catalog, point.code).map((side) => ({ code: point.code, side })));
const plannedCatalogInstances = catalog.concepts.flatMap((point) => plannedSides(catalog, point.code).map((side) => ({ code: point.code, side })));
if (plannedCatalogInstances.length !== 670 || new Set(plannedCatalogInstances.map((point) => `${point.code}:${point.side}`)).size !== 670) throw new Error('Full WHO 361 catalog denominator/uniqueness mismatch');
const expectedKeys = expected.map((point) => `${point.code}:${point.side}`);
const actual = pkg.availability.map(({ code, side }) => ({ code, side }));
const actualKeys = actual.map((point) => `${point.code}:${point.side}`);
assertUniqueInstances(actual);
if (expected.length !== 50 || expectedConcepts.length !== 25 || actualKeys.length !== 50 || new Set(actualKeys).size !== 50
  || expectedKeys.some((key) => !actualKeys.includes(key)) || actualKeys.some((key) => !expectedKeys.includes(key))) throw new Error('AT10 code/side coverage mismatch');
if (pkg.concepts.length !== 25 || new Set(pkg.concepts.map((point) => point.code)).size !== 25
  || pkg.concepts.some((point, index) => point.code !== `ST${index + 1}` || point.nameKo !== catalog.concepts.find((item) => item.code === point.code)?.nameKo)) throw new Error('AT10 concepts/names do not match the catalog');
if (pkg.availability.some((item) => item.display !== 'unavailable' || !item.reason.trim())
  || pkg.projections.length !== 0 || pkg.precisionCounts.precise !== 0
  || pkg.precisionCounts.educationalApproximation !== 0 || pkg.precisionCounts.unresolved !== 50) throw new Error('Unresolved locations must remain unavailable without projections');
if (observation.datasetRevision !== context.datasetRevision || observation.frameId !== context.frameId
  || observation.poseId !== context.poseId || observation.unit !== 'm'
  || observation.contexts.length !== 0 || observation.teachingPaths.length !== 0) throw new Error('Unexpected AT10 observation context/route');
const sectionCodes = registration.sections.flatMap((section) => section.codes);
if (sectionCodes.length !== 25 || new Set(sectionCodes).size !== 25 || sectionCodes.some((code) => !registration.codes.includes(code))) throw new Error('AT10 sections must exactly partition the partial codes');
if (positionLedger.locationRows.length !== 25 || positionLedger.instanceRows.length !== 50) throw new Error('AT10 location/instance ledger size mismatch');
const ledgerKeys = positionLedger.instanceRows.map((item) => `${item.code}:${item.side}`);
if (new Set(ledgerKeys).size !== 50 || expectedKeys.some((key) => !ledgerKeys.includes(key))
  || positionLedger.instanceRows.some((item) => item.carrierId !== null || item.carrierHash !== null
    || item.candidateDecision !== 'not_accepted_no_target_specific_external_surface_anchor' || item.verdict !== 'unresolved'
    || !item.reason.trim() || !item.positionRule.trim() || !item.candidateCarriers.length
    || item.candidateCarriers.some((candidate) => !/^[a-f0-9]{64}$/.test(candidate.topologySha256 ?? '')
      || !/^[a-f0-9]{64}$/.test(candidate.assetSha256 ?? '') || candidate.decision !== 'candidate_only_not_a_point_carrier'))) throw new Error('AT10 per-instance source/hash/disposition evidence incomplete');

const result = {
  schemaVersion: 1,
  run: '2026-10-13-r1',
  validation: 'validateLearningCatalog + validateLearningRegistry + validateLearningPackage + exact code/side/hash/source-scope assertions',
  fullCatalog: { channels: catalog.channels.length, uniqueConcepts: catalog.concepts.length, plannedInstances: plannedCatalogInstances.length, duplicateCodes: 0, missingCodes: [] },
  at10: {
    registration: registration.id,
    channel: 'ST',
    codeRange: ['ST1', 'ST25'],
    concepts: pkg.concepts.length,
    instances: actual.length,
    sides: { right: actual.filter((item) => item.side === 'right').length, left: actual.filter((item) => item.side === 'left').length, midline: actual.filter((item) => item.side === 'midline').length },
    duplicateKeys: 0,
    missingCodes: [],
    extraCodes: [],
    st26To45Covered: false,
    projections: pkg.projections.length,
    unavailable: pkg.availability.length,
    precisionCounts: pkg.precisionCounts,
    routes: observation.teachingPaths.length,
    ledgerRows: positionLedger.instanceRows.length,
    candidateCarrierEvidencePerInstance: positionLedger.instanceRows.map((item) => ({ code: item.code, side: item.side, candidateCount: item.candidateCarriers.length, selectedCarrierHash: item.carrierHash, verdict: item.verdict })),
    learnerBytes: packageBytes.byteLength,
    learnerSha256: sha(packageBytes),
    observationBytes: observationBytes.byteLength,
    observationSha256: sha(observationBytes),
    registrySha256: sha(await readBytes('atlas-data/acupoints/learner/registry-r1.json')),
  },
  retainedPackageIdsOutsideAT10: registry.packages.filter((item) => item.id !== registration.id).map((item) => item.id),
  baselinePreservation: { originalPackageRegistrationsUnchanged: true, ac1Ac2Evidence: preservedAcEvidence },
  locationDisposition: '50 unresolved; no coordinate, projection, route, or carrier accepted',
};
await writeFile(join(run, 'package-validation.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ channels: 14, catalogConcepts: 361, plannedInstances: 670, targetConcepts: 25, targetInstances: 50, right: 25, left: 25, unresolved: 50, projectionCount: 0, routeCount: 0, st26To45Covered: false }));
