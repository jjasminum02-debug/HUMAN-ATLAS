import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { projectLegacyRuntime, type V2GeometryFile, type V2Relation, type V2RelationsFile, type V2StructuresFile } from './atlasV2.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const structures = read('runtime/structures.json') as V2StructuresFile;
const relations = read('runtime/relations.json') as V2RelationsFile;
const geometry = read('source-cache/datasets/za-v2/geometry.json') as V2GeometryFile;
const legacy = read('runtime/legacy/runtime-2026-11-03.json');
const { dataset, integration } = projectLegacyRuntime(structures, relations, geometry);

test('v2 projection passes the existing dataset and runtime validators', () => {
  assert.equal(dataset.instances.length, structures.structures.length);
  assert.equal(integration.objects.length, structures.structures.length);
});

test('every pre-v2 visible row projects unchanged apart from the new muscle depth', () => {
  const rows = new Map(integration.objects.map(row => [row.sourceKey, row]));
  for (const before of legacy.rows.filter((row: { kind: string }) => row.kind !== 'accessory')) {
    const { depth, ...after } = rows.get(before.sourceKey)!;
    if (before.names.koModern === null) {
      // C1 fills Korean names only where a row had none (pre-v2 nerves); the English name never changes.
      assert.equal(after.names.en, before.names.en, before.sourceKey);
      assert.ok(after.names.koModern, `${before.sourceKey} still unnamed`);
      assert.ok(before.aliases.every((alias: string) => after.aliases.includes(alias)), `${before.sourceKey} lost an alias`);
      Object.assign(after, { names: before.names, label: before.label, aliases: before.aliases });
    }
    assert.deepEqual(after, before, before.sourceKey);
    assert.equal(depth !== undefined, before.kind === 'muscle', before.sourceKey);
  }
});

test('pre-v2 hidden accessories become layer rows, except cavities', () => {
  const rows = new Map(integration.objects.map(row => [row.sourceKey, row]));
  const shown = new Map<string, number>();
  for (const before of legacy.rows.filter((row: { kind: string }) => row.kind === 'accessory')) {
    const after = rows.get(before.sourceKey)!;
    if (after.localDisplayEligible) shown.set(after.kind, (shown.get(after.kind) ?? 0) + 1);
    else assert.ok(/cells of ethmoid|Sinus of/.test(after.names.en), after.names.en);
  }
  assert.equal(shown.get('accessory'), undefined);
  assert.ok((shown.get('fascia') ?? 0) >= 120 && (shown.get('joint') ?? 0) >= 80 && (shown.get('bone') ?? 0) >= 59);
});

test('every pre-v2 instance keeps key, namespace, matrix and geometry references', () => {
  const instances = new Map(dataset.instances.map(i => [i.sourceKey, i]));
  const hiddenBefore = new Set(legacy.rows.filter((row: { kind: string }) => row.kind === 'accessory').map((row: { sourceKey: string }) => row.sourceKey));
  for (const before of legacy.instances) {
    const after = instances.get(before.sourceKey)!;
    assert.equal(after.sourceName, before.sourceName);
    if (!hiddenBefore.has(before.sourceKey)) assert.equal(after.kind, before.kind);
    assert.equal(after.sourceNamespace, before.sourceNamespace);
    assert.deepEqual(after.matrix, before.matrix);
    for (const level of ['overview', 'detail'] as const)
      for (const field of ['resource', 'chunk', 'triangles', 'vertices', 'geometryBytes'] as const)
        assert.equal(after.lods[level][field], before.lods[level][field], `${before.sourceKey} ${level}.${field}`);
  }
  const chunks = new Map(dataset.chunks.map(c => [c.id, c]));
  for (const before of legacy.chunks) {
    const after = chunks.get(before.id)!;
    assert.equal(after.sha256, before.sha256); assert.equal(after.url, before.url); assert.deepEqual(after.resources, before.resources);
    assert.equal(after.selectionScoped, undefined);
  }
});

test('binding identity matches the pre-v2 runtime', () => {
  assert.equal(dataset.revision, legacy.compat.datasetRevision);
  assert.deepEqual(dataset.frameContract, legacy.compat.frameContract);
  assert.equal(integration.revision, legacy.compat.integrationRevision);
  assert.deepEqual(integration.sourceComponents, legacy.compat.sourceComponents);
});

test('new structures are on-demand, placed in a region, and visible only through a layer', () => {
  const fresh = structures.structures.filter(s => s.geometry.namespace === 'za-v2');
  const systems = new Map<string, number>();
  for (const s of fresh) systems.set(s.system, (systems.get(s.system) ?? 0) + 1);
  assert.ok((systems.get('joint') ?? 0) >= 400 && (systems.get('attachment') ?? 0) >= 700, JSON.stringify([...systems]));
  const onDemand = new Set(dataset.chunks.filter(c => c.selectionScoped).map(c => c.id));
  for (const s of fresh) {
    assert.equal(s.learner.visible, s.layer !== null, s.id);
    if (s.system === 'attachment' || s.kind === 'cns') assert.equal(s.layer, null, s.id);
    assert.ok(s.regions.length > 0, s.id);
    assert.ok(onDemand.has(s.geometry.lods.overview.chunk) && onDemand.has(s.geometry.lods.detail.chunk), s.id);
  }
});

test('knee joint structures are selectable joint-layer rows in the thigh/leg regions', () => {
  const rows = integration.objects;
  for (const name of ['Anterior cruciate ligament', 'Posterior cruciate ligament', 'Medial meniscus', 'Lateral meniscus', 'Articular capsule of knee joint'])
    for (const side of ['left', 'right']) {
      const row = rows.find(r => r.names.en === name && r.side === side);
      assert.ok(row, `${name} ${side}`);
      assert.equal(row.kind, 'joint'); assert.ok(row.localDisplayEligible && row.defaultVisible && row.tissue);
      assert.ok(row.regionIds.some(id => id === 'thigh' || id === 'leg'), `${name} ${row.regionIds}`);
      assert.ok(row.aliases.length > 0, name);
    }
});

test('visible structures carry Korean names except the listed unnamed terms', () => {
  const unnamed = new Set(read('terminology/structure-names-ko.json').unnamed as string[]);
  const missing = integration.objects.filter(r => r.localDisplayEligible && !r.names.koModern);
  for (const row of missing) assert.ok(unnamed.has(row.names.en), `${row.names.en} has no Korean name and is not listed`);
  assert.ok(missing.length <= 2 * unnamed.size);
});

test('muscle depth splits superficial and deep muscles', () => {
  const muscles = integration.objects.filter(r => r.kind === 'muscle');
  const superficial = muscles.filter(r => r.depth === 'superficial').length;
  assert.ok(superficial >= 100 && superficial < muscles.length - 300, String(superficial));
  assert.ok(muscles.every(r => r.depth === 'superficial' || r.depth === 'deep'));
});

test('attachment relations point at real structures', () => {
  const ids = new Set(structures.structures.map(s => s.id));
  const attachments = relations.relations.filter((r): r is Extract<V2Relation, { type: 'origin' | 'insertion' }> => r.type === 'origin' || r.type === 'insertion');
  assert.ok(attachments.length >= 700);
  for (const r of attachments) {
    assert.ok(ids.has(r.from), r.from);
    if (r.bone) assert.ok(ids.has(r.bone), r.bone);
    for (const owner of r.owners) assert.ok(ids.has(owner), owner);
  }
});
