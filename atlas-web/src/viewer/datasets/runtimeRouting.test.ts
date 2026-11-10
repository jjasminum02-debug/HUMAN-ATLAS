// Search, deep links and the runtime contract on the data the app actually loads (ROADMAP D3).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { projectLegacyRuntime, type V2GeometryFile, type V2RelationsFile, type V2StructuresFile } from '../../data/atlasV2.ts';
import { datasetRouteQuery, readDatasetRoute, searchStructures, validateRuntimeIntegration } from './integration.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const { dataset, integration } = projectLegacyRuntime(read('runtime/structures.json') as V2StructuresFile,
  read('runtime/relations.json') as V2RelationsFile, read('source-cache/datasets/za-v2/geometry.json') as V2GeometryFile);
const rows = integration.objects;
const regionIds = [...new Set(rows.flatMap(row => row.regionIds))];
const rectus = rows.filter(row => row.names.koModern === '넙다리곧은근');

test('all three names find one entry for a left/right pair', () => {
  assert.equal(rectus.length, 2);
  for (const query of [rectus[0].names.koModern!, rectus[0].names.koTraditional!, rectus[0].names.en]) {
    const hits = searchStructures(rows, query, []).filter(hit => hit.names.en === rectus[0].names.en);
    assert.equal(hits.length, 1, query);
  }
});

test('titles lead with the Sino-Korean term, and a modern-term search still finds it', () => {
  assert.equal(rectus[0].label, '대퇴직근');
  for (const query of ['넙다리곧은근', '넙다리곧', '대퇴직근']) {
    const [hit] = searchStructures(rows, query, []);
    assert.equal(hit?.label, '대퇴직근', query);
  }
  const named = rows.filter(row => row.names.koTraditional && row.names.koModern && row.localDisplayEligible);
  assert.ok(named.length > 2000);
  assert.deepEqual(named.filter(row => row.label !== row.names.koTraditional).map(row => row.label), []);
});

test('region filters use the union of the chosen regions', () => {
  const [a, b] = regionIds, one = searchStructures(rows, '', [a]).length, other = searchStructures(rows, '', [b]).length;
  const both = searchStructures(rows, '', [a, b]).length;
  assert.ok(both >= Math.max(one, other) && both > 0);
});

test('a source link round-trips, picks the side, and ignores unknown keys', () => {
  const [row] = rectus, regions = [row.regionIds[0]];
  const query = String(datasetRouteQuery({ regions, selected: row.sourceKey }));
  assert.deepEqual(readDatasetRoute(query, rows, regionIds), { regions, selected: row.sourceKey });
  const sided = rectus.find(r => r.side === 'left')!;
  assert.equal(readDatasetRoute(`?source=${sided.sourceKey}&side=right`, rows, regionIds).selected, null);
  assert.equal(readDatasetRoute(`?source=${sided.sourceKey}&side=left`, rows, regionIds).selected, sided.sourceKey);
  assert.equal(readDatasetRoute('?source=ZA-not-a-structure', rows, regionIds).selected, null);
});

test('the runtime contract rejects stale revisions, extra fields and broken rows', () => {
  assert.doesNotThrow(() => validateRuntimeIntegration(integration, dataset));
  assert.throws(() => validateRuntimeIntegration({ ...integration, datasetRevision: 'other' }, dataset));
  assert.throws(() => validateRuntimeIntegration({ ...integration, sourceLedger: [] }, dataset));
  assert.throws(() => validateRuntimeIntegration({ ...integration, objects: rows.slice(1) }, dataset));
});
