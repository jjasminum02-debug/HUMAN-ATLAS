import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { withNerveDisplayNames } from './nerveDisplayNames.ts';
import { conceptForExactNerveName } from './nerveRelations.ts';
import { learnerSearchEntry, searchEntries } from './search.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const graph = read('../../../atlas-data/terminology/learner-nerve-graph-t66.json');
const names = read('../../../atlas-data/terminology/learner-nerve-display-names.json');
const projected = withNerveDisplayNames(graph.concepts, names);

test('all existing nerve label groups have Korean labels, with exact native identity unchanged', () => {
  assert.equal(projected.length, graph.concepts.length);
  for (const [i, row] of projected.entries()) {
    assert.match(row.names.koModern, /[가-힣]/);
    assert.match(row.names.koTraditional, /[가-힣]/);
    assert.equal(row.names.en, graph.concepts[i].names.en);
    assert.equal(row.sourceNativeEnglishName, graph.concepts[i].sourceNativeEnglishName);
    assert.deepEqual({ ...row, names: undefined, searchTerms: undefined },
      { ...graph.concepts[i], names: undefined, searchTerms: undefined });
    assert.equal(conceptForExactNerveName(projected, row.names.en)?.key, row.key);
  }
  assert.deepEqual(graph.motorRelations, read('../../../atlas-data/terminology/learner-nerve-graph-t66.json').motorRelations);
});

test('display overlay covers unique exact native names, without unused or ambiguous mappings', () => {
  for (const [english, display] of Object.entries(names)) {
    const matches = graph.concepts.filter((row: { sourceNativeEnglishName: string }) => row.sourceNativeEnglishName === english);
    assert.equal(matches.length, 1, english);
    assert.match((display as { koModern: string }).koModern, /[가-힣]/);
  }
});

test('plexus level, division, and skin branch remain distinct and searchable in both languages', () => {
  const entries = projected.map(row => learnerSearchEntry(row.key, row.names.koModern,
    [row.names.koTraditional, row.names.en, ...row.searchTerms]));
  for (const [english, korean] of [
    ['Inferior trunk of brachial plexus', '팔신경얼기 아래줄기'],
    ['Anterior division of inferior trunk of brachial plexus', '팔신경얼기 아래줄기 앞갈래'],
    ['Lateral antebrachial cutaneous nerve', '가쪽아래팔피부신경'],
    ['Muscular branches of median nerve', '정중신경 근육가지'],
  ]) {
    const row = conceptForExactNerveName(projected, english)!;
    assert.equal(row.names.koModern, korean);
    for (const term of [english, korean, row.names.koTraditional]) {
      assert.ok(searchEntries(entries, term).some(result => result.entry.id === row.key), term);
    }
  }
});
