// Ligament attachment areas (ROADMAP 4-1 step 6).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
test('ligaments carry contact areas on the bones they join (4-1 step 6)', () => {
  const file = JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/attachments.json', import.meta.url), 'utf8'));
  const runtime = JSON.parse(readFileSync(new URL('../../../atlas-data/runtime/structures.json', import.meta.url), 'utf8')).structures as { key: string; names: { en: string } }[];
  const byKey = new Map(runtime.map(s => [s.key, s]));
  const acl = runtime.filter(s => s.names.en === 'Anterior cruciate ligament');
  assert.equal(acl.length, 2);
  for (const ligament of acl) {
    const rows = file.ligaments[ligament.key];
    assert.deepEqual([...new Set(rows.map((r: { bone: string }) => byKey.get(r.bone)!.names.en))].sort(), ['Femur', 'Tibia']);
    for (const r of rows) assert.ok(r.role === 'attachment' && r.source === 'contact' && r.areaMm2 > 20, JSON.stringify(r));
  }
  assert.ok(Object.keys(file.ligaments).length > 300);
});
