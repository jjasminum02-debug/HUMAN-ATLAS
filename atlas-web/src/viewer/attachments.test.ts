import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const data = (path: string) => new URL(`../../../atlas-data/${path}`, import.meta.url);
type Lod = { resource: string; chunk: string; triangles: number };
const structures = JSON.parse(readFileSync(data('runtime/structures.json'), 'utf8')).structures as
  { key: string; kind: string; system: string; layer: string | null; side: string; names: { en: string }; learner: { visible: boolean }; geometry: { lods: Record<'overview' | 'detail', Lod> } }[];
const file = JSON.parse(readFileSync(data('runtime/attachments.json'), 'utf8')) as
  { muscles: Record<string, { key?: string; role: string; bone: string | null; source: string }[]>; missing: string[] };
const byKey = new Map(structures.map(s => [s.key, s]));
const muscles = structures.filter(s => s.learner.visible && s.layer === 'muscle');
const contactsDir = 'source-cache/datasets/za-v2/attachments';

test('every visible muscle has drawn attachment areas or is listed as missing', () => {
  for (const m of muscles) assert.ok(file.muscles[m.key]?.length || file.missing.includes(m.key), m.names.en);
  assert.ok(file.missing.length <= 10, `missing ${file.missing.length}`);
});

test('Z-Anatomy rows point at patch structures on visible bones; contact rows have triangles for both bone LODs', () => {
  for (const [muscle, rows] of Object.entries(file.muscles)) {
    const contact = rows.filter(r => r.source === 'contact');
    const tris = contact.length ? JSON.parse(readFileSync(data(`${contactsDir}/${muscle}.json`), 'utf8')).rows as Record<string, string>[] : [];
    assert.equal(tris.length, contact.length, muscle);
    for (const r of rows) {
      assert.ok(['origin', 'insertion', 'attachment'].includes(r.role));
      if (r.bone) assert.equal(byKey.get(r.bone)?.layer, 'bone', `${muscle} bone`);
      if (r.source === 'za') assert.ok(r.key && byKey.get(r.key)?.system === 'attachment', `${muscle} patch`);
    }
    contact.forEach((r, i) => {
      const bone = byKey.get(r.bone!)!;
      for (const level of ['overview', 'detail'] as const) {
        const lod = bone.geometry.lods[level], packed = tris[i][lod.resource];
        assert.ok(packed, `${muscle} ${level}`);
        const ids = new Uint32Array(Uint8Array.from(Buffer.from(packed, 'base64')).buffer);
        assert.ok(ids.every(t => t < lod.triangles), `${muscle} ${level} index range`);
      }
    });
  }
});

test('textbook examples: deltoid scapula -> humerus; rectus femoris hip bone -> patella', () => {
  const rows = (en: string) => {
    const m = muscles.find(s => s.names.en === en && s.side === 'right')!;
    return file.muscles[m.key].map(r => `${r.role}:${byKey.get(r.bone!)?.names.en}`);
  };
  assert.deepEqual(rows('Acromial part of deltoid muscle'), ['origin:Scapula', 'insertion:Humerus']);
  assert.deepEqual(rows('Rectus femoris muscle'), ['origin:Hip bone', 'insertion:Patella']);
});

test('contact triangle files exist only for muscles with contact rows', () => {
  for (const [muscle, rows] of Object.entries(file.muscles))
    assert.equal(existsSync(data(`${contactsDir}/${muscle}.json`)), rows.some(r => r.source === 'contact'), muscle);
});
