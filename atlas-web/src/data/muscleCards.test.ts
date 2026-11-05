import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const data = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
type Term = { ko: string; koTraditional: string; en: string; structure?: string };
type Card = { concept?: string; tendonOf?: string | null; nerve?: string[]; roots?: string; artery?: string[]; action?: string };
const file = data('runtime/muscle-cards.json') as { nerves: Record<string, Term>; arteries: Record<string, Term>; cards: Record<string, Card> };
const checks = data('anatomy/muscle-card-checks.json') as { muscles: Record<string, Record<string, { status: string }>> };
const structures = data('runtime/structures.json').structures as { kind: string; layer: string | null; names: { en: string }; learner: { visible: boolean } }[];
const muscles = [...new Set(structures.filter(s => s.learner.visible && s.layer === 'muscle').map(s => s.names.en))];
const nerveNames = new Set(structures.filter(s => s.learner.visible && s.layer === 'nerve').map(s => s.names.en));

test('every visible muscle name has a card; tendons point at their muscle', () => {
  for (const name of muscles) assert.ok(file.cards[name], name);
  const cards = Object.values(file.cards).filter(c => c.tendonOf === undefined);
  assert.ok(cards.filter(c => c.nerve?.length).length >= 220, 'innervation coverage');
  assert.ok(cards.filter(c => c.action).length >= 210, 'action coverage');
  assert.ok(cards.filter(c => c.artery?.length).length >= 160, 'blood supply coverage');
});

test('shown values are vocabulary terms both sources agreed on', () => {
  for (const [name, card] of Object.entries(file.cards)) {
    if (card.tendonOf !== undefined) continue;
    for (const key of card.nerve ?? []) assert.ok(file.nerves[key]?.ko, `${name} nerve ${key}`);
    for (const key of card.artery ?? []) assert.ok(file.arteries[key]?.ko, `${name} artery ${key}`);
    for (const field of ['nerve', 'artery', 'roots', 'action'] as const)
      if (card[field]?.length) assert.ok(['agree', 'partial'].includes(checks.muscles[name][field].status), `${name} ${field}`);
    if (card.roots) assert.match(card.roots, /^[CTLS]\d{1,2}(–[CTLS]\d{1,2})?(, [CTLS]\d{1,2}(–[CTLS]\d{1,2})?)*$/);
  }
  for (const t of Object.values(file.nerves)) if (t.structure) assert.ok(nerveNames.has(t.structure), t.structure);
});

test('textbook examples', () => {
  const nerves = (name: string) => file.cards[name].nerve!.map(k => file.nerves[k].en);
  assert.deepEqual(nerves('Acromial part of deltoid muscle'), ['Axillary nerve']);
  assert.deepEqual(nerves('Rectus femoris muscle'), ['Femoral nerve']);
  assert.deepEqual(nerves('Short head of biceps brachii'), ['Musculocutaneous nerve']);
  assert.deepEqual(nerves('Tibialis anterior muscle'), ['Deep fibular nerve']);
  assert.deepEqual(nerves('Lateral rectus muscle'), ['Abducens nerve']);
  assert.deepEqual(nerves('Long head of biceps femoris'), ['Tibial nerve']);
  assert.deepEqual(nerves('Short head of biceps femoris'), ['Common fibular nerve']);
  assert.equal(file.cards['Gluteus medius muscle'].roots, 'L4–S1');
  assert.equal(file.cards['Diaphragm'].roots, undefined); // the infobox names no segments: not shown
  assert.deepEqual(file.cards['Rectus femoris muscle'].artery!.map(k => file.arteries[k].en), ['Lateral circumflex femoral artery']);
  assert.equal(file.cards['Calcaneal tendon'].tendonOf, 'Gastrocnemius');
});
