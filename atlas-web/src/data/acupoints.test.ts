// Acupoints on the rig (ROADMAP 4-1 step 7: 14 channels, 361 points; the exception list is acupoint-checks.json).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { channelPath, channelSegments, type AcupointFile } from '../viewer/acupointLayer.ts';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const file = read('runtime/acupoints.json') as AcupointFile;
const checks = read('anatomy/acupoint-checks.json').points as Record<string, { status: string; missing?: string; unmatched?: string[] }>;
const rig = read('runtime/rig.json'), structures = read('runtime/structures.json').structures as { key: string; names: { en: string }; layer: string | null }[];
const byKey = new Map(structures.map(s => [s.key, s]));
const at = (code: string, side = 'right') => file.points.find(p => p.code === code && p.side === (file.channels[code.replace(/\d+$/, '')]?.midline ? 'midline' : side));
const near = (code: string) => at(code)!.near.map(k => byKey.get(k)?.names.en ?? k);

test('fourteen channels; every runtime point passed the second-source check and sits on a rig segment', () => {
  assert.deepEqual(Object.keys(file.channels), ['LU', 'LI', 'ST', 'SP', 'HT', 'SI', 'BL', 'KI', 'PC', 'TE', 'GB', 'LR', 'GV', 'CV']);
  assert.equal(Object.keys(checks).length, 361);
  for (const c of file.concepts) assert.equal(checks[c.code].status, 'agree', c.code);
  for (const p of file.points) { assert.ok(rig.segments[p.segment], `${p.code} ${p.segment}`); assert.ok(p.position.every(Number.isFinite)); }
  assert.ok(file.concepts.length >= 280, `${file.concepts.length} points kept`);
  // Every other point is in the exception list with its reason.
  for (const [code, c] of Object.entries(checks)) {
    assert.ok(['agree', 'conflict', 'noSource', 'noLandmark', 'geometry'].includes(c.status), code);
    if (c.status === 'noLandmark') assert.ok(c.missing, code);
    if (c.status === 'conflict') assert.ok(c.unmatched?.length, code);
  }
});

test('paired channels mirror left and right; GV and CV run on the midline', () => {
  for (const [code, channel] of Object.entries(file.channels)) {
    if (channel.midline) {
      for (const p of channelPath(file, code, 'midline')) assert.ok(Math.abs(p.position[0]) < .003, p.code);
      continue;
    }
    for (const r of channelPath(file, code, 'right')) {
      const l = file.points.find(p => p.code === r.code && p.side === 'left')!;
      assert.ok(Math.abs(r.position[0] + l.position[0]) < .015 && Math.abs(r.position[1] - l.position[1]) < .015, r.code);
      assert.ok(r.position[0] < 0, `${r.code} right side lies at -x`);
    }
  }
});

test('channel order follows the body: LU descends the arm, GV climbs the spine, CV climbs the front', () => {
  const ys = (ch: string, side: string, from: number, to: number) => channelPath(file, ch, side)
    .filter(p => { const n = Number(p.code.replace(/^\D+/, '')); return n >= from && n <= to; }).map(p => p.position[1]);
  const monotone = (v: number[], dir: 1 | -1, slack = .004) => v.every((y, i) => i === 0 || dir * (y - v[i - 1]) >= -slack);
  assert.ok(monotone(ys('LU', 'right', 2, 11), -1), 'LU2 → LU11 descends');
  assert.ok(monotone(ys('GV', 'midline', 1, 20), 1, .006), 'GV1 → GV20 ascends');
  assert.ok(monotone(ys('CV', 'midline', 2, 22), 1), 'CV2 → CV22 ascends');
  assert.ok(monotone(ys('BL', 'right', 11, 30), -1), 'BL11 → BL30 descends the back');
  // Bladder: the outer back line (3 cun) lies lateral to the inner one (1.5 cun); the line is drawn in two pieces.
  assert.ok(Math.abs(at('BL42')!.position[0]) > Math.abs(at('BL13')!.position[0]) + .015);
  assert.equal(channelSegments(file, 'BL', 'right').length, 2);
});

test('textbook neighbours and segments', () => {
  assert.ok(near('LU9').includes('Radial artery'));
  assert.ok(near('LU7').includes('Radius'));
  assert.ok(near('SP6').includes('Tibia'), near('SP6').join());
  assert.ok(near('KI3').includes('Tibial nerve'), near('KI3').join());
  assert.ok(near('LI11').includes('Humerus') || near('LI11').includes('Brachioradialis muscle'), near('LI11').join());
  assert.equal(at('ST36')!.segment, 'tibia_r');
  assert.equal(at('LI4')!.segment, 'hand_r');
  assert.equal(at('GV20')!.segment, 'head');
  assert.ok(at('GV20')!.position[1] > at('GV24')!.position[1], 'GV20 at the vertex, above GV24');
  // Points the model cannot place (no auricle, hairline, perineum or inside of the mouth) are listed, not drawn.
  for (const code of ['TE20', 'GB8', 'CV1', 'GV28']) { assert.equal(checks[code].status, 'noLandmark'); assert.equal(at(code), undefined); }
});
