import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import type { StructureCardsFile } from '../ui/StructureCard.tsx';

const read = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/runtime/${path}`, import.meta.url), 'utf8'));
const cards = read('structure-cards.json') as StructureCardsFile;
const structures = new Map((read('structures.json').structures as { key: string; names: { en: string }; side: string; layer: string | null; learner: { visible: boolean } }[])
  .map(s => [s.key, s]));
const keyOf = (en: string, side: string) => [...structures.values()].find(s => s.names.en === en && s.side === side)!.key;
const names = (keys: string[]) => keys.map(key => structures.get(key)!.names.en);

test('every card and link points at a visible structure', () => {
  for (const [key, card] of Object.entries(cards.cards)) {
    assert.ok(structures.get(key)?.learner.visible, key);
    for (const link of [...card.bones, ...card.muscles]) assert.ok(structures.get(link)?.learner.visible, `${key} -> ${link}`);
    if (card.joint) assert.ok(cards.joints[card.joint]?.members.includes(key), `${key} not listed in ${card.joint}`);
  }
});

test('knee ligaments join femur and tibia and belong to the knee joint', () => {
  for (const side of ['left', 'right']) {
    for (const ligament of ['Anterior cruciate ligament', 'Posterior cruciate ligament']) {
      const card = cards.cards[keyOf(ligament, side)];
      assert.deepEqual(new Set(names(card.bones)), new Set(['Femur', 'Tibia']), `${ligament} ${side}`);
      assert.equal(card.joint, `joint:knee-joint:${side}`);
      assert.ok(card.text);
    }
    assert.deepEqual(new Set(names(cards.cards[keyOf('Fibular collateral ligament', side)].bones)), new Set(['Femur', 'Fibula']));
    const knee = cards.joints[`joint:knee-joint:${side}`];
    assert.equal(knee.type, 'synovial');
    assert.ok(['Femur', 'Tibia', 'Patella'].every(bone => names(knee.bones).includes(bone)), names(knee.bones).join());
    assert.ok(knee.summary && knee.names.koTraditional);
  }
});

test('fascia lata links the thigh muscles it wraps', () => {
  const muscles = names(cards.cards[keyOf('Fascia lata', 'right')].muscles);
  assert.ok(muscles.some(m => /Sartorius|Vastus lateralis|Rectus femoris/.test(m)), muscles.join());
});
