import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { createLearnerLookupIndex } from './learnerLookupIndex.ts';
import { conceptForExactNerveName, relationsForNerve, type MotorRelationRow, type NerveConceptNameRow } from './nerveRelations.ts';

test('ambiguous native names stay unresolved and never fall through to another display identity', () => {
  const nerves = [
    { key: 'a', sourceNativeEnglishName: 'shared', names: { en: 'A' } },
    { key: 'b', sourceNativeEnglishName: 'shared', names: { en: 'B' } },
    { key: 'c', sourceNativeEnglishName: null, names: { en: 'shared' } },
  ];
  const index = createLearnerLookupIndex([], [], nerves, []);
  for (const name of ['shared', 'A', 'B', 'missing', ''])
    assert.equal(index.nerveForExactName(name), conceptForExactNerveName(nerves, name));
  assert.equal(index.nerveForExactName('shared'), null);
});

test('the full current learner data retains names, action order and both directions of side-scoped nerve relations', () => {
  const load = (file: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/terminology/${file}`, import.meta.url), 'utf8'));
  const card = load('learner-card-runtime.json');
  const graph = load('learner-nerve-graph-t66.json') as { concepts: NerveConceptNameRow[]; motorRelations: MotorRelationRow[] };
  const index = createLearnerLookupIndex(card.names, card.actions, graph.concepts, graph.motorRelations);
  for (const row of card.names) assert.equal(index.namesById.get(row.id), card.names.find((r: typeof row) => r.id === row.id));
  for (const id of new Set(card.actions.map((row: { conceptId: string }) => row.conceptId)))
    assert.deepEqual(index.actionsByConcept.get(id as string), card.actions.filter((row: { conceptId: string }) => row.conceptId === id));
  for (const name of new Set(graph.concepts.flatMap((row: { sourceNativeEnglishName: string | null; names: { en: string } }) => [row.sourceNativeEnglishName, row.names.en])))
    if (name !== null) assert.equal(index.nerveForExactName(name as string), conceptForExactNerveName(graph.concepts, name as string));
  for (const nerve of graph.concepts) for (const side of [null, 'left', 'right'])
    assert.deepEqual(relationsForNerve(index.relationsByNerve.get(nerve.key) ?? [], nerve.key, side), relationsForNerve(graph.motorRelations, nerve.key, side));
  for (const key of new Set(graph.motorRelations.flatMap((row: { targetSourceKeys: string[] }) => row.targetSourceKeys)))
    assert.deepEqual(index.relationsBySource.get(key as string), graph.motorRelations.filter((row: { targetSourceKeys: string[] }) => row.targetSourceKeys.includes(key as string)));
});

test('repeated source keys retain one relation and duplicate IDs retain their first match', () => {
  const relation = { nerveKey: 'nerve', targetSourceKeys: ['source', 'source'] };
  const names = [{ id: 'a', label: 'first' }, { id: 'a', label: 'second' }];
  const index = createLearnerLookupIndex(names, [], [], [relation]);
  assert.equal(index.namesById.get('a'), names[0]);
  assert.deepEqual(index.relationsBySource.get('source'), [relation]);
});
