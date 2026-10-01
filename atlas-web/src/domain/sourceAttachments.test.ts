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
