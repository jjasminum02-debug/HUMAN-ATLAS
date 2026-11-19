// How a point is found (2026-11-19): on a landmark, between two, by finger breadth, or by proportional cun.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { locationBasis, type AcupointFile } from './acupointLayer.ts';

const file = JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/acupoints.json', import.meta.url), 'utf8')) as AcupointFile;
const basis = (code: string) => locationBasis(file.concepts.find(c => c.code === code)!.location);

test('location basis reads the standard location text', () => {
  assert.equal(basis('PC7').kind, 'landmark', '대릉: between two tendons on the crease');
  assert.deepEqual(basis('PC6'), { kind: 'cun', cun: 2, marks: ['힘줄', '주름'] });
  assert.equal(basis('BL40').kind, 'landmark');
  assert.equal(basis('LI11').kind, 'between', '곡지: midpoint of a line');
  assert.equal(basis('ST6').kind, 'finger');
  assert.equal(basis('BL67').kind, 'landmark', '0.1 cun beside the nail corner counts as the landmark');
  assert.equal(basis('ST36').kind, 'cun');
  assert.ok(basis('LI5').marks.includes('힘줄'), '양계: between tendons');
  const kinds = file.concepts.map(c => locationBasis(c.location).kind);
  assert.ok(kinds.filter(k => k === 'landmark').length > 80 && kinds.filter(k => k === 'cun').length > 150, JSON.stringify(Object.fromEntries(['landmark', 'between', 'finger', 'cun'].map(k => [k, kinds.filter(x => x === k).length]))));
});

test('vessels and nerves beneath points: popliteal artery under 위중, vertebral artery deep to 풍지', () => {
  const structures = new Map((JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/structures.json', import.meta.url), 'utf8')).structures as { key: string; names: { en: string } }[]).map(s => [s.key, s.names.en]));
  const under = (code: string) => file.points.find(p => p.code === code && p.side !== 'left')!.beneath!.map(b => [structures.get(b.key), b.depth] as const);
  assert.ok(under('BL40').some(([n, d]) => n === 'Popliteal artery' && d <= 20) && under('BL40').some(([n]) => n === 'Tibial nerve'));
  assert.ok(under('GB20').some(([n, d]) => n === 'Vertebral artery' && d > 15));
  assert.ok(under('LU9').some(([n]) => n === 'Radial artery'));
  assert.ok(under('PC6').some(([n]) => n === 'Median nerve'));
  for (const p of file.points) for (let i = 1; i < (p.beneath?.length ?? 0); i++) assert.ok(p.beneath![i].depth >= p.beneath![i - 1].depth, `${p.code} sorted by depth`);
});

test('중부 lies on pectoralis major, not on a deep muscle across the empty axilla', () => {
  const structures = new Map((JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/structures.json', import.meta.url), 'utf8')).structures as { key: string; names: { en: string } }[]).map(s => [s.key, s.names.en]));
  assert.match(structures.get(file.points.find(p => p.code === 'LU1')!.surfaceOf!) ?? '', /pectoralis major/);
  assert.match(structures.get(file.points.find(p => p.code === 'GB30')!.surfaceOf!) ?? '', /Gluteus maximus/);
});

test('teaching landmarks sit where palpation finds them, and every measure has both ends on both sides', () => {
  const at = (id: string, side = 'right') => file.landmarks!.find(m => m.id === id && (m.side === side || m.side === 'midline'))!.position;
  assert.equal(new Set(file.landmarks!.map(m => m.id)).size, 17);
  assert.ok(at('psis')[2] < at('asis')[2] - .1 && Math.abs(at('psis')[0]) < Math.abs(at('asis')[0]), 'PSIS behind and medial to ASIS');
  assert.ok(at('rib12')[1] > at('iliacCrest')[1] && at('iliacCrest')[1] > at('asis')[1], '12th rib above the crest, crest above ASIS');
  assert.ok(at('coracoid')[2] > at('greaterTubercle')[2] && Math.abs(at('scj')[0]) < .03, 'coracoid in front of the greater tubercle; SC joint beside the midline');
  assert.ok(at('eop')[1] > at('suboccipital')[1], 'suboccipital below the external occipital protuberance');
  for (const m of file.landmarks!) if (m.side === 'right') { const l = at(m.id, 'left'); assert.ok(Math.abs(l[0] + m.position[0]) < .002 && Math.abs(l[1] - m.position[1]) < .002, `${m.id} mirrors`); }
  for (const measure of file.measures!) for (const side of ['right', 'left']) assert.ok(at(measure.from, side) && at(measure.to, side), `${measure.id} ${side}`);
});
