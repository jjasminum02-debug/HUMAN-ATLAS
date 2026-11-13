import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { factQuestion, gradeFind, makeRng, quizRows, readQuizRecord, recordAnswer, structureQuestion, writeQuizRecord, type QuizCards, type QuizRow } from './quiz.ts';
import { liveBookmarks, readBookmarks, toggleBookmark, writeBookmarks } from './bookmarks.ts';

const data = (path: string) => JSON.parse(readFileSync(new URL(`../../../atlas-data/${path}`, import.meta.url), 'utf8'));
const structures = data('runtime/structures.json').structures as { key: string; label: string; layer: string | null; kind: string; regions: string[]; side: string; names: QuizRow['names']; learner: { visible: boolean; inspectable: boolean } }[];
const rows: QuizRow[] = structures.filter(s => s.layer).map(s => ({ sourceKey: s.key, label: s.label, kind: s.layer === 'muscle' && s.kind === 'tendon' ? 'tendon' : s.layer!,
  regionIds: s.regions, side: s.side === 'unpaired' ? null : s.side, names: s.names, localDisplayEligible: s.learner.visible, inspectionEligible: s.learner.inspectable }));
const cards = data('runtime/muscle-cards.json') as QuizCards;
const muscles = new Set(rows.filter(r => r.kind === 'muscle').map(r => r.sourceKey));

test('name questions use only drawn structures, with four distinct choices and one right answer', () => {
  const rng = makeRng(7);
  for (let i = 0; i < 200; i++) {
    const q = structureQuestion('name', rows, muscles, rng)!;
    assert.ok(muscles.has(q.targetKey));
    assert.equal(new Set(q.choices).size, 4);
    assert.equal(q.choices.filter(c => c === q.answer).length, 1);
    assert.ok(q.choices.every(c => /[가-힣]/.test(c)));
  }
  assert.equal(structureQuestion('name', rows, new Set(), rng), null, 'nothing drawn, no question');
});

test('fact questions come from agreed muscle-card values; action choices have one muscle that fits', () => {
  const rng = makeRng(11);
  const byLabel = new Map<string, string[]>();
  for (const r of quizRows(rows)) if (r.kind === 'muscle' && cards.cards[r.names.en]?.action) byLabel.set(r.label, [...(byLabel.get(r.label) ?? []), cards.cards[r.names.en].action!]);
  for (const kind of ['nerve', 'artery', 'action'] as const) for (let i = 0; i < 150; i++) {
    const q = factQuestion(kind, rows, cards, rng)!;
    assert.ok(q && q.choices.length === 4 && new Set(q.choices).size === 4, kind);
    if (kind === 'action') for (const c of q.choices.filter(c => c !== q.answer)) {
      assert.ok(!byLabel.get(c)!.includes(q.quote!), `${c} also does "${q.quote}"`);
      const target = rows.find(r => r.sourceKey === q.targetKey)!, wrong = rows.filter(r => r.label === c && r.kind === 'muscle');
      assert.ok(wrong.every(r => !r.regionIds.some(id => target.regionIds.includes(id))), `${c} shares a region with ${target.label}`);
    }
  }
  const rf = rows.find(r => r.names.en === 'Rectus femoris muscle' && r.side === 'right')!;
  const nerve = factQuestion('nerve', [rf, ...rows.filter(r => r.kind === 'muscle')], cards, () => 0)!;
  assert.ok(nerve.answer.length > 0 && nerve.prompt.endsWith('신경지배는?'));
});

test('find accepts the other side of the same structure, not a neighbour', () => {
  const rf = rows.filter(r => r.names.en === 'Rectus femoris muscle');
  const q = structureQuestion('find', rows, new Set([rf[0].sourceKey]), makeRng(1))!;
  assert.equal(q.targetKey, rf[0].sourceKey);
  assert.ok(gradeFind(q, rf[1], rows));
  assert.ok(!gradeFind(q, rows.find(r => r.names.en === 'Vastus lateralis muscle')!, rows));
});

test('score, missed list and bookmarks persist and survive bad storage', () => {
  const store = new Map<string, string>();
  const storage = { getItem: (k: string) => store.get(k) ?? null, setItem: (k: string, v: string) => void store.set(k, v) };
  const q = structureQuestion('name', rows, muscles, makeRng(3))!;
  let record = recordAnswer(readQuizRecord(storage), q, false);
  record = recordAnswer(record, q, true);
  writeQuizRecord(record, storage);
  assert.deepEqual(readQuizRecord(storage), { answered: 2, correct: 1, missed: [] }, 'answering right later clears the miss');
  store.set('atlas.quiz.v1', '{broken'); assert.equal(readQuizRecord(storage).answered, 0);
  let marks = toggleBookmark([], { key: 'A', label: '삼각근', kind: 'muscle' });
  marks = toggleBookmark(marks, { key: 'B', label: '상완골', kind: 'bone' });
  assert.deepEqual(marks.map(b => b.key), ['B', 'A']);
  writeBookmarks(toggleBookmark(marks, { key: 'A', label: '삼각근', kind: 'muscle' }), storage);
  assert.deepEqual(readBookmarks(storage).map(b => b.key), ['B']);
  assert.deepEqual(liveBookmarks(marks, k => k === 'A').map(b => b.key), ['A']);
  assert.deepEqual(readBookmarks(null), []);
});

test('bookmarks keep the saved view and reject a broken one (4-1 step 6)', async () => {
  const { toggleBookmark, validStudyView } = await import('./bookmarks.ts');
  const view = { camera: { position: [0, 1, 2], target: [0, 1, 0], zoom: 1 }, layers: { bone: true, fascia: false }, layerOpacity: { bone: .5 }, section: { axis: 'axial', position: .7, flip: false } };
  const [saved] = toggleBookmark([], { key: 'ZA-x', label: '대퇴직근', kind: 'muscle', view });
  assert.deepEqual(saved.view, view);
  assert.ok(validStudyView(view) && validStudyView({ ...view, section: null }));
  assert.ok(!validStudyView({ ...view, camera: { position: [0, NaN, 0], target: [0, 0, 0], zoom: 1 } }) && !validStudyView(undefined));
});
