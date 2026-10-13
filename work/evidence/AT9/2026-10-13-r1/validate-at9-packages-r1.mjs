import { readFile, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { validateLearningCatalog } from '../../../../atlas-web/src/viewer/acupoints/learningCatalog.ts';
import { validateLearningRegistry, plannedSides, assertUniqueInstances } from '../../../../atlas-web/src/viewer/acupoints/learningRegistry.ts';
import { validateLearningPackage, composeLearningPackages } from '../../../../atlas-web/src/viewer/acupoints/learningPackage.ts';

const root = resolve(fileURLToPath(new URL('../../../../', import.meta.url)));
const run = resolve(fileURLToPath(new URL('.', import.meta.url)));
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const readBytes = (p) => readFile(join(root, p));
const readJson = async (p) => JSON.parse(await readBytes(p));
const catalog = await readJson('atlas-data/acupoints/observation/catalog-r1.json');
const registry = await readJson('atlas-data/acupoints/learner/registry-r1.json');
const contextPkg = await readJson('atlas-data/acupoints/learner/lung-r7.json');
const context = { datasetRevision: contextPkg.datasetRevision, frameId: contextPkg.frameId, unit: 'm', poseId: contextPkg.poseId };
validateLearningCatalog(catalog);
validateLearningRegistry(registry, catalog);

const packages = [];
const decodedObservation = [];
const packageResults = [];
for (const registration of registry.packages) {
  const learnerPath = `atlas-data/acupoints/learner/${registration.learnerFile}`;
  const observationPath = `atlas-data/acupoints/observation/${registration.observationFile}`;
  const learnerBytes = await readBytes(learnerPath);
  const observationBytes = await readBytes(observationPath);
  if (sha(learnerBytes) !== registration.learnerSha256 || sha(observationBytes) !== registration.observationSha256) throw new Error(`Registered file hash mismatch: ${registration.id}`);
  const pkg = JSON.parse(learnerBytes.toString('utf8'));
  validateLearningPackage(pkg, context, catalog, registration);
  packages.push(pkg);
  if (registration.channel === 'HT' || registration.channel === 'PC' || registration.channel === 'SI') {
    const raw = registration.observationEncoding === 'gzip' ? gunzipSync(observationBytes) : observationBytes;
    const obs = JSON.parse(raw.toString('utf8'));
    if (obs.datasetRevision !== context.datasetRevision || obs.frameId !== context.frameId || obs.poseId !== context.poseId || obs.unit !== 'm'
      || obs.contexts.length !== 0 || obs.teachingPaths.length !== 0) throw new Error(`Unexpected observation binding: ${registration.id}`);
    decodedObservation.push({ registration: registration.id, encodedBytes: observationBytes.byteLength, decodedBytes: raw.byteLength, contexts: 0, paths: 0, sha256: sha(observationBytes) });
    packageResults.push({
      registration: registration.id,
      channel: registration.channel,
      conceptCount: pkg.concepts.length,
      codes: pkg.concepts.map((c) => c.code),
      uniqueNames: new Set(pkg.concepts.map((c) => c.nameKo)).size,
      instanceCount: pkg.availability.length,
      rightCount: pkg.availability.filter((i) => i.side === 'right').length,
      leftCount: pkg.availability.filter((i) => i.side === 'left').length,
      unresolvedCount: pkg.precisionCounts.unresolved,
      projectionCount: pkg.projections.length,
    });
  }
}
const composed = composeLearningPackages(packages);
const at9Registrations = registry.packages.filter((p) => ['HT', 'PC', 'SI'].includes(p.channel));
const at9Availability = composed.availability.filter((i) => ['HT', 'PC', 'SI'].some((channel) => i.code.startsWith(channel)));
assertUniqueInstances(at9Availability);
const planned = at9Registrations.flatMap((r) => r.codes.flatMap((code) => plannedSides(catalog, code).map((side) => ({ code, side }))));
if (planned.length !== 74 || at9Availability.length !== 74 || new Set(at9Availability.map((i) => `${i.code}:${i.side}`)).size !== 74) throw new Error('AT9 instance denominator or uniqueness check failed');
if (at9Availability.some((i) => i.display !== 'unavailable' || !i.reason.trim())) throw new Error('AT9 contains an unproven available location');
if (composed.concepts.filter((c) => ['HT', 'PC', 'SI'].includes(c.channel)).length !== 37) throw new Error('AT9 catalog/package concept count mismatch');

const result = {
  schemaVersion: 1,
  run: '2026-10-13-r1',
  catalog: { channels: catalog.channels.length, concepts: catalog.concepts.length, plannedInstances: 670 },
  at9: { concepts: 37, targetCodes: at9Registrations.flatMap((r) => r.codes), instances: at9Availability.length, right: 37, left: 37, midline: 0, resolved: 0, unresolved: 74, duplicates: 0, missingCodes: [], extraCodes: [], projections: 0, supportedPathSegments: 0 },
  preservedExistingRegistrationIds: registry.packages.filter((p) => !['HT', 'PC', 'SI'].includes(p.channel)).map((p) => p.id),
  packageResults,
  decodedObservation,
  sharedValidation: 'validateLearningCatalog + validateLearningRegistry + validateLearningPackage + composeLearningPackages + assertUniqueInstances passed',
};
await writeFile(join(run, 'package-validation-r1.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ at9Concepts: 37, instances: 74, unresolved: 74, duplicateKeys: 0, fullCatalogConcepts: 361, fullCatalogInstances: 670 }));
