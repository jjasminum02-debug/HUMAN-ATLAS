// Posture patterns (ROADMAP 4-2 step 10; held muscles are in posture-pattern-checks.json).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { patternKeys, patternsFor, type PosturePatternsFile } from './posturePatterns.ts';

const read = (p: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${p}`, import.meta.url), 'utf8'));
const file = read('runtime/posture-patterns.json') as PosturePatternsFile;
const checks = read('anatomy/posture-pattern-checks.json') as { patterns: Record<string, string[]> };
const rows = (read('runtime/structures.json').structures as { key: string; kind: string; side: string; names: { en: string } }[])
  .filter(r => r.kind === 'muscle').map(r => ({ sourceKey: r.key, side: r.side, names: r.names }));

test('posture pattern muscles exist on both sides and never on both lists', () => {
  for (const p of file.patterns) {
    assert.equal(new Set([...p.short, ...p.weak]).size, p.short.length + p.weak.length, p.id);
    const keys = patternKeys(p, rows);
    for (const [role, list] of [['short', p.short], ['weak', p.weak]] as const) for (const en of list) {
      const sides = rows.filter(r => r.names.en === en && keys[role].includes(r.sourceKey)).map(r => r.side).sort();
      assert.ok(sides.includes('left') && sides.includes('right'), `${p.id} ${en}: ${sides}`);
    }
  }
});
test('each posture pattern cites two publishers', () => {
  for (const p of file.patterns) assert.equal(new Set(checks.patterns[p.id].map(s => s.split('-')[0])).size, 2, p.id);
});
test('posture patterns are found per muscle with their side', () => {
  assert.deepEqual(patternsFor(file, 'Pectoralis minor muscle').map(h => [h.pattern.id, h.role]), [['upperCrossed', 'short']]);
  assert.deepEqual(patternsFor(file, 'Gluteus maximus muscle').map(h => [h.pattern.id, h.role]), [['lowerCrossed', 'weak']]);
  assert.deepEqual(patternsFor(file, 'Biceps femoris'), []);
});
