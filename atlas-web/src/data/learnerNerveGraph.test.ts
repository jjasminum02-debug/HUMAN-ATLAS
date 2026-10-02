import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { searchEntries } from '../domain/search.ts';

const graph = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/learner-nerve-graph-t25.json', import.meta.url), 'utf8'));
const integration = JSON.parse(readFileSync(new URL('../../../atlas-data/overlays/za-local-integration.json', import.meta.url), 'utf8'));
const nerveSupport = JSON.parse(readFileSync(new URL('../../../atlas-data/overlays/nerve-support-t63.json', import.meta.url), 'utf8'));
const learnerObjects = new Map(integration.objects.filter((row: { localDisplayEligible: boolean }) => row.localDisplayEligible).map((row: { sourceKey: string }) => [row.sourceKey, row]));

test('the five nerve concepts search by modern, Sino-Korean-in-Hangul, English and Latin names', () => {
  assert.equal(graph.concepts.length, 5);
  const entries = graph.concepts.map((concept: { key: string; names: { koModern: string; koTraditional: string; en: string; latin: string }; searchTerms: string[] }) => ({
    id: concept.key,
    label: concept.names.koModern,
    aliases: [concept.names.koTraditional, concept.names.en, concept.names.latin, ...concept.searchTerms],
  }));
  for (const concept of graph.concepts) {
    for (const term of [concept.names.koModern, concept.names.koTraditional, concept.names.en, concept.names.latin, ...concept.searchTerms]) {
      assert.equal(searchEntries(entries, term)[0]?.entry.id, concept.key, `${concept.key}: ${term}`);
    }
  }
  assert.doesNotMatch(JSON.stringify(graph.concepts), /[\u3400-\u9fff]/, 'learner nerve labels do not contain collected Hanja');
});

test('source-named sciatic and text-only dorsal scapular concepts do not manufacture learner geometry', () => {
  const byKey = new Map<string, { key: string; sourceNativeEnglishName: string | null; summary?: unknown }>(graph.concepts.map((concept: { key: string; sourceNativeEnglishName: string | null; summary?: unknown }) => [concept.key, concept]));
  for (const key of ['common-fibular', 'deep-fibular', 'superficial-fibular']) {
    const concept = byKey.get(key) as { sourceNativeEnglishName: string | null };
    assert.ok(concept.sourceNativeEnglishName);
  }
  assert.equal(byKey.get('sciatic')?.sourceNativeEnglishName, 'Sciatic nerve');
  assert.equal(byKey.get('dorsal-scapular')?.sourceNativeEnglishName, null);
  assert.equal(byKey.get('sciatic')?.summary, undefined);
  assert.ok(byKey.get('dorsal-scapular')?.summary);
  const sciaticSourceRows = nerveSupport.instances.filter((row: { names: { en: string } }) => row.names.en === 'Sciatic nerve');
  assert.equal(sciaticSourceRows.length, 2);
  assert.ok(sciaticSourceRows.every((row: { geometry: { assetPath?: string } | null }) => !row.geometry?.assetPath), 'existing context rows are not learner geometry');
});

test('verified deep-fibular relations are exactly side-matched and appear in both directions', () => {
  const rows = graph.motorRelations.filter((row: { nerveKey: string }) => row.nerveKey === 'deep-fibular');
  assert.equal(rows.length, 2);
  assert.deepEqual(new Set(rows.map((row: { targetSide: string }) => row.targetSide)), new Set(['left', 'right']));
  for (const row of rows) {
    assert.equal(row.scope, 'exact_side_matched_source_instance');
    assert.equal(row.targetSourceKeys.length, 1);
    const object = learnerObjects.get(row.targetSourceKeys[0]) as { side: string; names: { en: string } } | undefined;
    assert.ok(object);
    assert.equal(object.names.en, 'Tibialis anterior muscle');
    assert.equal(object.side, row.targetSide);
  }
});

test('dorsal-scapular relations are unsided whole-muscle concepts linked only to existing rhomboid surfaces', () => {
  const rows = graph.motorRelations.filter((row: { nerveKey: string }) => row.nerveKey === 'dorsal-scapular');
  assert.equal(rows.length, 2);
  const names = new Set<string>();
  for (const row of rows) {
    assert.equal(row.targetSide, null);
    assert.equal(row.scope, 'unsided_named_whole_muscle_concept');
    assert.equal(row.targetSourceKeys.length, 2);
    const objects = row.targetSourceKeys.map((key: string) => learnerObjects.get(key) as { side: string; names: { en: string } } | undefined);
    assert.ok(objects.every(Boolean));
    assert.deepEqual(new Set(objects.map((object: { side: string }) => object.side)), new Set(['left', 'right']));
    names.add(objects[0]!.names.en);
    assert.ok(objects.every((object: { names: { en: string } }) => object.names.en === objects[0]!.names.en));
  }
  assert.deepEqual(names, new Set(['Rhomboid major muscle', 'Rhomboid minor muscle']));
});

test('the learner nerve bundle omits provenance, review, rights, task, and canonical-ID metadata', () => {
  assert.doesNotMatch(JSON.stringify(graph), /https?:\/\/|T62-|T25-|sourceNerveInstanceId|HA-[MGP]-|humanReview|publicRedistribution|sourceOnly/);
});
