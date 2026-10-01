import { readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolve, relative } from 'node:path';
import { validateNerveRegistry } from '../src/domain/nerveContract.ts';

const root = fileURLToPath(new URL('../../', import.meta.url));
const hashFile = (path: string) => createHash('sha256').update(readFileSync(resolve(root, path))).digest('hex');
const inventory = JSON.parse(readFileSync(resolve(root, 'atlas-data/manifests/nerve-support-t61.json'), 'utf8'));
function check(value: unknown, label: string): asserts value { if (!value) throw Error(label); }
check(inventory.schemaVersion === 't61-source-inventory-v1', 'inventory schema');
check(inventory.contractRevision === 'app-completion-2026-10-01', 'contract revision');
for (const [path, hash] of Object.entries(inventory.inputs)) {
  check(!relative(root, resolve(root, path)).startsWith('..'), 'path outside workspace');
  check(existsSync(resolve(root, path)) && hashFile(path) === hash, `input hash: ${path}`);
}
const registry = validateNerveRegistry(inventory.registry);
for (const e of registry.evidence) check(hashFile(e.sourcePath) === e.sourceSha256, `evidence source: ${e.id}`);
for (const n of registry.instances) if (n.geometry) check(hashFile(n.geometry.assetPath) === n.geometry.assetSha256, `asset hash: ${n.id}`);
const ledgers = new Map<string, Record<string, unknown>>();
for (const ref of inventory.fullLedgerReferences) {
  const value = JSON.parse(readFileSync(resolve(root, ref.path), 'utf8'));
  check(hashFile(ref.path) === ref.sha256, 'full ledger hash');
  if (ref.rows) check((value.allObjects ?? value.records).length === ref.rows, 'ledger rows');
  if (ref.conceptRows) check(value.sourceConcepts.length === ref.conceptRows && value.sourceElementFiles.length === ref.elementRows, 'BP3D full ledger');
  ledgers.set(ref.path, value);
}
const candidateIds = new Set<string>();
for (const c of inventory.candidates) {
  check(!candidateIds.has(c.id), 'duplicate candidate'); candidateIds.add(c.id);
  let source: any = ledgers.get(c.ledgerPath);
  for (const part of c.ledgerPointer.split('/').slice(1)) source = source?.[part];
  check(source, `missing ledger row ${c.id}`);
  const expected = c.sourceNamespace === 'za-c7010a9' ? source.sourceObjectLocator.objectDataBlockPointer : source.sourceFmaConceptId;
  check(expected === c.sourceObjectId, 'source namespace/locator mismatch');
  check(c.sourceOnly === true && c.humanReview === 'not_performed' && c.publicRedistribution === 'held'
    && c.localSelection === 'unsupported' && c.side === 'unknown' && c.geometry === null && c.missing.length > 0, 'candidate promotion');
  for (const e of c.elementAvailability ?? []) for (const f of e.localFiles) check(hashFile(f.path) === f.sha256, 'element hash');
}
check(candidateIds.size === inventory.counts.sourceCandidateRows, 'candidate count');
for (const n of registry.instances) check(inventory.candidates.some((c: { sourceNamespace: string; sourceObjectId: string }) =>
  c.sourceNamespace === n.sourceNamespace && c.sourceObjectId === n.sourceObjectId), `source identity not inventoried: ${n.id}`);
check(registry.instances.filter(n => n.localSelection === 'verified_geometry').length === inventory.counts.supportedNerve3D, '3D support count');
check(registry.instances.filter(n => n.localSelection !== 'unsupported').length === inventory.counts.supportedNerveCards, 'card support count');
check(inventory.support.supportedNerveIds.length === registry.instances.filter(n => n.localSelection !== 'unsupported').length, 'support list');
check(JSON.stringify([...inventory.support.supportedNerveIds].sort()) === JSON.stringify(registry.instances.filter(n => n.localSelection !== 'unsupported').map(n => n.id).sort()), 'support identity');
check(inventory.denominators.targets === 542 && inventory.denominators.memberships === 563 && inventory.denominators.regions === 12
  && inventory.preserved.existingHaConnections === 130 && JSON.stringify(inventory.preserved.historical163) === '[6,20,135,2]', 'preserved denominators');
process.stdout.write(JSON.stringify({ status: 'passed', validatedInputs: Object.keys(inventory.inputs).length,
  fullLedgerReferences: inventory.fullLedgerReferences.length, counts: inventory.counts,
  fixtureEvidenceIsProductionEvidence: false, newNerve3D: false, contentCompleteness: inventory.contentCompleteness }, null, 2) + '\n');
