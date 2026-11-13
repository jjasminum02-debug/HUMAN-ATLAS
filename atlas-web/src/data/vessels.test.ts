import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';
import { projectLegacyRuntime, type V2GeometryFile, type V2RelationsFile, type V2StructuresFile } from './atlasV2.ts';

const data = (path: string) => new URL(`../../../atlas-data/${path}`, import.meta.url);
const file = JSON.parse(readFileSync(data('runtime/structures.json'), 'utf8')) as V2StructuresFile;
const vessels = file.structures.filter(s => s.layer === 'vessel');
const geometryPath = data('source-cache/datasets/za-v2/geometry.json');

test('Q2-1: Z-Anatomy arteries, veins and heart are one on-demand vessel layer', () => {
  const kinds = new Map<string, number>();
  for (const s of vessels) kinds.set(s.kind!, (kinds.get(s.kind!) ?? 0) + 1);
  assert.ok((kinds.get('artery') ?? 0) >= 400 && (kinds.get('vein') ?? 0) >= 200 && (kinds.get('heart') ?? 0) >= 15, JSON.stringify([...kinds]));
  for (const s of vessels) {
    assert.equal(s.system, 'cardiovascular');
    assert.ok(s.learner.visible && s.regions.length, s.sourceName);
  }
  for (const name of ['Aortic arch', 'Femoral artery', 'Great saphenous vein', 'Left ventricle', 'Superior sagittal sinus'])
    assert.ok(vessels.some(s => s.names.en === name), name);
  // Paired vessels sit on their own side of the body (x = subject left).
  const femoral = vessels.filter(s => s.names.en === 'Femoral artery');
  for (const s of femoral) assert.equal(Math.sign((s.geometry.bounds[0][0] + s.geometry.bounds[1][0]) / 2), s.side === 'left' ? 1 : -1);
});

test('vessel rows project as kind vessel with artery/vein/heart tissue, from on-demand chunks only', { skip: !existsSync(geometryPath) }, () => {
  const relations = JSON.parse(readFileSync(data('runtime/relations.json'), 'utf8')) as V2RelationsFile;
  const geometry = JSON.parse(readFileSync(geometryPath, 'utf8')) as V2GeometryFile;
  const { integration } = projectLegacyRuntime(file, relations, geometry);
  const rows = integration.objects.filter(r => r.kind === 'vessel');
  assert.equal(rows.length, vessels.length);
  assert.ok(rows.every(r => ['artery', 'vein', 'heart'].includes(r.tissue!)));
  const onDemand = new Set(geometry.chunks.filter(c => c.onDemand).map(c => c.id));
  for (const s of vessels) for (const lod of Object.values(s.geometry.lods)) assert.ok(onDemand.has(lod.chunk), s.sourceName);
  const overview = vessels.reduce((n, s) => n + s.geometry.lods.overview.triangles, 0);
  assert.ok(overview < 300_000, `vessel overview triangles ${overview}`);
});

test('muscle blood supply terms link to drawn vessels', () => {
  const cards = JSON.parse(readFileSync(data('runtime/muscle-cards.json'), 'utf8')) as { arteries: Record<string, { en: string; structures?: string[] }> };
  const names = new Set(vessels.map(s => s.names.en));
  const linked = Object.values(cards.arteries).filter(a => a.structures?.length);
  assert.ok(linked.length >= 45, `linked ${linked.length}`);
  for (const a of linked) for (const n of a.structures!) assert.ok(names.has(n), n);
  assert.deepEqual(cards.arteries.lateral_circumflex_femoral.structures, ['Lateral circumflex femoral artery']);
});

test('vessel branch links (4-1 step 6) point at vessels in the model, follow textbook examples and never loop', () => {
  const branches = JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/vessel-branches.json', import.meta.url), 'utf8')).parents as Record<string, string>;
  const all = JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/structures.json', import.meta.url), 'utf8')).structures as { layer: string | null; names: { en: string } }[];
  const names = new Set(all.filter(s => s.layer === 'vessel').map(s => s.names.en));
  for (const [child, parent] of Object.entries(branches)) {
    assert.ok(names.has(child), child);
    assert.ok(parent.includes('{S}') ? names.has(parent.replace('{S}', 'Left')) && names.has(parent.replace('{S}', 'Right')) : names.has(parent), `${child} -> ${parent}`);
  }
  assert.equal(branches['Brachial artery'], 'Axillary artery');
  assert.equal(branches['Femoral vein'], 'External iliac vein');
  assert.equal(branches['Lateral circumflex femoral artery'], 'Deep femoral artery');
  assert.equal(branches['Descending branch of lateral circumflex femoral artery'], 'Lateral circumflex femoral artery'); // from the name
  assert.equal(branches['Thoracic aorta'], undefined); // draft and Wikipedia disagree: not shown
  for (const start of Object.keys(branches)) {
    const seen = new Set<string>(); let at: string | undefined = start;
    while (at && branches[at]) { assert.ok(!seen.has(at), `loop at ${start}`); seen.add(at); at = branches[at].replace('{S}', 'Left'); }
  }
});
