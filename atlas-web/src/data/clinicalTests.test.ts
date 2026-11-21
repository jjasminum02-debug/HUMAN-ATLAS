// Clinical test names (ROADMAP 4-2 step 9; held items are in clinical-test-checks.json).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { testsFor, type ClinicalTestsFile } from './clinicalTests.ts';

const read = (p: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${p}`, import.meta.url), 'utf8'));
const file = read('runtime/clinical-tests.json') as ClinicalTestsFile;
const checks = read('anatomy/clinical-test-checks.json') as { tests: Record<string, { by: string; url: string }[]>; held: unknown[] };
const names = new Set((read('runtime/structures.json').structures as { names: { en: string } }[]).map(r => r.names.en));

test('every clinical test target is a structure in the model', () => {
  for (const t of file.tests) for (const target of t.targets) assert.ok(names.has(target), `${t.id}: ${target}`);
});
test('every shown clinical test has two independent publishers', () => {
  for (const t of file.tests) assert.ok(new Set(checks.tests[t.id].map(s => s.by)).size >= 2, t.id);
});
test('clinical test runtime keeps learner fields only, one line each', () => {
  for (const t of file.tests) {
    assert.deepEqual(Object.keys(t).sort(), ['en', 'id', 'name', 'targets', 'what']);
    assert.ok(t.what.length < 90, t.id);
  }
});
test('clinical tests are found by English name', () => {
  assert.deepEqual(testsFor(file, 'Subscapularis muscle').map(t => t.id), ['bellyPress', 'liftOff']);
  assert.deepEqual(testsFor(file, 'Medial meniscus').map(t => t.id), ['mcmurray']);
  assert.deepEqual(testsFor(file, 'Sciatic nerve').map(t => t.id), ['slr']);
  assert.deepEqual(testsFor(file, 'Rectus femoris'), []);
});
