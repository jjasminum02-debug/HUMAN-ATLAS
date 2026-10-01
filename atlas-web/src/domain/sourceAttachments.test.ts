import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { projectSourceAttachments } from './sourceAttachments.ts';
const content = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/muscle-attachment-content-t90.json', import.meta.url), 'utf8'));
const overlayBytes = readFileSync(new URL('../../../atlas-data/overlays/za-local-integration.json', import.meta.url));
const rows = JSON.parse(overlayBytes.toString()).objects;
test('all principal-attachment descriptions map to exact whole named source muscles and same-side existing bones; original binding/review authority stays unchanged', () => {
  assert.equal(createHash('sha256').update(overlayBytes).digest('hex'), content.sourceOverlaySha256);
  const result = projectSourceAttachments(content, rows);
  assert.equal(content.records.length, 15); assert.equal(Object.keys(result.text).length, 30);
  assert.equal(rows.filter((r: any) => r.haConceptId).length, 130);
  assert.ok(content.records.every((r: any) => r.summaryExtent === 'principal_attachments_only_not_exhaustive'));
  for (const muscle of rows.filter((r: any) => result.text[r.sourceKey])) for (const boneKey of Object.values(result.contexts[muscle.sourceKey]).flat()) {
    const bone = rows.find((r: any) => r.sourceKey === boneKey); assert.equal(bone.kind, 'bone'); assert.ok(bone.side === muscle.side || bone.side === null);
  }
  assert.doesNotMatch(JSON.stringify(result.text), /https?:\/\/|not_performed|single_source|T90|sourceHash/);
  assert.equal(content.records.some((r: any) => /(?:head|part) of (?:pectoralis|trapezius)/i.test(r.sourceName)), false);
});
test('reject renamed/part-expanded muscle, held/wrong-side context, missing source hashes and invented human approval', () => {
  for (const mutate of [(c: any) => c.records[0].sourceName = 'Clavicular head of sternocleidomastoid', (c: any) => c.records[0].scopeType = 'entire_group', (c: any) => c.sources[0].originalHtmlSha256 = '', (c: any) => c.records[0].humanReview = 'performed']) {
    const c = structuredClone(content); mutate(c); assert.throws(() => projectSourceAttachments(c, rows));
  }
  const keys = projectSourceAttachments(content, rows).contexts[content.records[0].sourceKeys[0]].origin;
  const pairedKey = keys.find(key => rows.find((r: any) => r.sourceKey === key).side !== null)!;
  for (const mutate of [(r: any) => r.localDisplayEligible = false, (r: any) => r.side = 'unknown']) {
    const changed = structuredClone(rows); mutate(changed.find((r: any) => r.sourceKey === pairedKey)); assert.throws(() => projectSourceAttachments(content, changed));
  }
});

test('T65 adds only exact part-scoped or whole-source summaries with pinned web-reader notes and existing same-side bones', () => {
  const t65 = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/muscle-attachment-content-t65.json', import.meta.url), 'utf8'));
  const notes = readFileSync(new URL('../../../work/evidence/T65/source-review-notes.md', import.meta.url));
  assert.equal(createHash('sha256').update(notes).digest('hex'), t65.reviewNotesSha256);
  assert.equal(t65.sources.every((s: any) => s.originalHtmlRetrieved === false && s.originalHtmlSha256 === null), true);
  const verified = new Set<string>(t65.sources.map((s: any) => s.id));
  const result = projectSourceAttachments(t65, rows, { verifiedWebReaderSourceIds: verified });
  assert.equal(t65.records.length, 9); assert.equal(Object.keys(result.text).length, 18);
  assert.equal(t65.records.filter((r: any) => r.scopeType === 'named_source_part').length, 6);
  assert.equal(t65.records.filter((r: any) => r.scopeType === 'named_source_muscle').length, 3);
  assert.ok(t65.records.every((r: any) => r.sourceKeys.length === 2 && r.sourceKeys.every((key: string) => rows.find((row: any) => row.sourceKey === key)?.names.en === r.sourceName)));
  assert.equal(Object.keys(result.text).some((key) => /^HA-/.test(key)), false);
  assert.equal(t65.contract.humanReview, 'not_performed'); assert.equal(t65.contract.publicRedistribution, 'held');
  assert.equal(createHash('sha256').update(t65.records[0].origin).digest('hex'), t65.records[0].fieldEvidence.origin.learnerValueSha256);
  assert.notEqual(createHash('sha256').update(t65.records[0].origin + '변경').digest('hex'), t65.records[0].fieldEvidence.origin.learnerValueSha256);
  assert.throws(() => projectSourceAttachments(t65, rows), /Attachment field source/);
  for (const mutate of [(c: any) => c.records[0].sourceName = 'Deltoid muscle', (c: any) => c.records[0].scopeType = 'named_source_muscle',
    (c: any) => c.sources[0].originalHtmlRetrieved = true,
    (c: any) => c.contract.humanReview = 'reviewed']) {
    const changed = structuredClone(t65); mutate(changed); assert.throws(() => projectSourceAttachments(changed, rows, { verifiedWebReaderSourceIds: verified }));
  }
});
