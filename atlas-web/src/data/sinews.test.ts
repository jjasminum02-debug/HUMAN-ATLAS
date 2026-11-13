// Meridian sinews on the model (ROADMAP 4-1 step 7 ③; the exception list is sinew-checks.json).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import type { SinewFile } from '../viewer/acupointLayer.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const file = read('runtime/sinews.json') as SinewFile;
const checks = read('anatomy/sinew-checks.json').sinews as Record<string, { nodes: { anchor: string; label: string; status: string; unmatched?: string[] }[] }>;
const rig = read('runtime/rig.json');
const structures = new Map((read('runtime/structures.json').structures as { key: string; names: { en: string }; layer: string | null }[]).map(s => [s.key, s]));
const en = (code: string, side: 'right' | 'left' = 'right') => file.sinews[code].muscles[side].map(k => structures.get(k)?.names.en ?? k);

test('twelve sinews; every drawn node agrees with both sources, the rest are listed with the source that disagrees', () => {
  assert.deepEqual(file.order, ['LU', 'LI', 'ST', 'SP', 'HT', 'SI', 'BL', 'KI', 'PC', 'TE', 'GB', 'LR']);
  for (const [code, sinew] of Object.entries(file.sinews)) {
    const agreed = new Set(checks[code].nodes.filter(n => n.status === 'agree').map(n => `${n.anchor}|${n.label}`));
    for (const strand of sinew.strands) for (const n of strand) assert.ok(agreed.has(`${n.anchor}|${n.label}`), `${code} ${n.label}`);
    for (const n of checks[code].nodes) if (n.status === 'conflict') assert.ok(n.unmatched?.length, `${code} ${n.label}`);
  }
  const all = Object.values(checks).flatMap(c => c.nodes);
  assert.ok(all.filter(n => n.status === 'agree').length >= 120, 'most binding regions confirmed');
});

test('paths on both sides ride rig segments, one segment per sample', () => {
  for (const code of file.order) for (const side of ['right', 'left'] as const)
    assert.ok(file.paths.some(p => p.sinew === code && p.side === side), `${code} ${side}`);
  for (const p of file.paths) {
    assert.equal(p.points.length, p.segments.length);
    for (const s of [...p.segments, ...p.nodes.map(n => n.segment)]) assert.ok(rig.segments[s], `${p.sinew} ${s}`);
  }
  // The hand-yangming sinew crosses over the head to the opposite jaw (上左角 絡頭 下右頷).
  assert.ok(file.paths.some(p => p.sinew === 'LI' && p.side === 'right' && p.nodes.some(n => n.anchor === '~ST8' && n.position[0] > 0)));
});

test('muscles under the lines: calf and buttock for the bladder sinew, adductors for the liver sinew, biceps for the lung sinew', () => {
  for (const code of file.order) for (const k of file.sinews[code].muscles.right) assert.equal(structures.get(k)?.layer, 'muscle', `${code} ${k}`);
  assert.ok(en('BL').some(n => /gastrocnemius/.test(n)) && en('BL').includes('Gluteus maximus muscle'), en('BL').join());
  assert.ok(en('LR').includes('Adductor longus') || en('LR').includes('Gracilis muscle'), en('LR').join());
  assert.ok(en('LU').some(n => /biceps brachii/.test(n)), en('LU').join());
  assert.ok(en('BL', 'left').some(n => /gastrocnemius/.test(n)));
});
