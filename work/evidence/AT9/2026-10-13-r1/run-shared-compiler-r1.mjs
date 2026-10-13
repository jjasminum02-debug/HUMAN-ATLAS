import { readFile, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { createHash } from 'node:crypto';
import { webcrypto } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { compilePlacementBatch, projectCompiledBatch, ANCHOR_COMPILER_VERSION } from '../../../../atlas-web/src/viewer/acupoints/anchorCompiler.ts';
import { decodeCarrierChunk, validateCarrierManifest } from '../../../../atlas-web/src/viewer/acupoints/carrierSample.ts';

const root = resolve(fileURLToPath(new URL('../../../../', import.meta.url)));
const run = resolve(fileURLToPath(new URL('.', import.meta.url)));
const readJson = async (p) => JSON.parse(await readFile(join(root, p), 'utf8'));
const ledgerDoc = JSON.parse(await readFile(join(run, 'point-ledger-r1.json'), 'utf8'));
const priorAT8 = await readJson('work/evidence/AT8/2026-10-13-r1/rules-r19.json');
const context = priorAT8.context;
const inputs = priorAT8.inputs;
globalThis.crypto ??= webcrypto;
const decodedCandidates = [];
const manifestCache = new Map();
for (const row of ledgerDoc.instances) for (const candidate of row.candidateCarriers) {
  const current = inputs.carriers[candidate.carrierId];
  if (current) {
    if (current.topologySha256 !== candidate.carrierHash) throw new Error(`Frozen compiler/carrier hash mismatch: ${candidate.carrierId}`);
    continue;
  }
  let manifest = manifestCache.get(candidate.edition);
  if (!manifest) {
    manifest = await readJson(`atlas-data/acupoints/carriers/${candidate.edition}/manifest.json`);
    validateCarrierManifest(manifest, context);
    manifestCache.set(candidate.edition, manifest);
  }
  const chunk = manifest.chunks.find((entry) => entry.id === candidate.carrierId);
  if (!chunk) throw new Error(`Candidate missing from manifest: ${candidate.carrierId}`);
  const raw = await readFile(join(root, 'atlas-data/acupoints/carriers', candidate.edition, chunk.file));
  const view = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
  const sample = await decodeCarrierChunk(manifest, chunk, view);
  if (sample.carrier.topologySha256 !== candidate.carrierHash) throw new Error(`Candidate topology hash mismatch: ${candidate.carrierId}`);
  inputs.carriers[candidate.carrierId] = sample.carrier;
  decodedCandidates.push({
    carrierId: candidate.carrierId,
    edition: candidate.edition,
    carrierHash: candidate.carrierHash,
    binarySha256: candidate.binarySha256,
    bytes: raw.byteLength,
  });
}
const units = ledgerDoc.instances.map((r) => ({
  id: `AT9-${r.code}-${r.side}`,
  scope: 'real_input',
  code: r.code,
  side: r.side,
  revision: 'AT9-unresolved-r1',
  context,
  carrierId: r.candidateCarrierId,
  originalText: r.sourceRuleKo,
  originalSources: [{
    id: r.source.id,
    title: r.source.standard,
    edition: '2008/2009',
    url: r.source.whoUrl,
    locator: r.source.kmcricUrl,
    rights: r.source.rights,
  }],
  author: 'ai',
  professorReview: 'not_performed',
  landmarks: [],
  observedReferences: [],
  rule: { kind: 'unresolved' },
  relationEvidenceId: `${r.code}-${r.side}-location-relation-not-annotated`,
  surfaceEvidenceId: `${r.code}-${r.side}-surface-registration-not-annotated`,
}));

const missing = units.filter((u) => !inputs.carriers[u.carrierId]);
if (units.length !== 74 || missing.length) throw new Error(`Compiler input has ${units.length} units; missing candidate carrier: ${missing.map((u) => u.carrierId).join(',')}`);

const compiled = await compilePlacementBatch(units, inputs);
const projection = await projectCompiledBatch(compiled.ledger, inputs, { ...context, motionActive: false });
const unitResults = Object.values(compiled.ledger.units).map((u) => ({
  id: u.id,
  code: u.instance?.code ?? u.id.replace(/^AT9-/, '').replace(/-(right|left)$/, ''),
  side: u.id.endsWith('-right') ? 'right' : 'left',
  status: u.status,
  errors: u.errors,
  inputSha256: u.inputSha256,
}));
const failures = unitResults.filter((u) => u.status !== 'failed' || !u.errors.some((e) => e.includes('ineligible rule: unresolved')));
if (failures.length || projection.length || projection.some((p) => p.instances.length)) throw new Error('Fail-closed compiler disposition did not match the expected unresolved result.');

const report = {
  schemaVersion: 1,
  run: '2026-10-13-r1',
  compilerVersion: ANCHOR_COMPILER_VERSION,
  reusedInput: 'work/evidence/AT8/2026-10-13-r1/rules-r19.json',
  reusedInputSha256: createHash('sha256').update(await readFile(join(root, 'work/evidence/AT8/2026-10-13-r1/rules-r19.json'))).digest('hex'),
  at9LedgerSha256: createHash('sha256').update(await readFile(join(run, 'point-ledger-r1.json'))).digest('hex'),
  exactCandidateCarriersDecodedAndHashChecked: decodedCandidates,
  attempted: units.length,
  passed: 0,
  failed: unitResults.length,
  failedUnits: unitResults,
  eligibleProjectionGroups: projection.length,
  eligibleInstances: projection.reduce((n, p) => n + p.instances.length, 0),
  fixtureExports: 0,
  disposition: 'All 74 fail closed because no point-specific confirmed landmark/surface registration was supplied; no learner anchor was emitted.',
};
await writeFile(join(run, 'compiler-disposition-r1.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ compilerVersion: report.compilerVersion, attempted: report.attempted, failed: report.failed, eligibleInstances: report.eligibleInstances }));
