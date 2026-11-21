// 4-3 U1: learner text ends in 합니다체; a plain "~한다." sentence in card data is a regression.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const read = (p: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/runtime/${p}`, import.meta.url), 'utf8'));
function plainSentences(value: unknown, out: string[] = []): string[] {
  if (typeof value === 'string') { for (const s of value.split(/(?<=\.)\s+/)) if (/[가-힣]다\.?$/.test(s.trim()) && !/니다\.?$/.test(s.trim())) out.push(s.trim()); }
  else if (Array.isArray(value)) value.forEach(v => plainSentences(v, out));
  else if (value && typeof value === 'object') Object.values(value).forEach(v => plainSentences(v, out));
  return out;
}
for (const file of ['muscle-cards.json', 'structure-cards.json', 'clinical-tests.json', 'posture-patterns.json']) {
  test(`${file} learner sentences end in 합니다체`, () => {
    const plain = plainSentences(file === 'muscle-cards.json' ? read(file).cards : read(file));
    assert.deepEqual(plain.slice(0, 5), [], `${plain.length} plain sentences`);
  });
}
