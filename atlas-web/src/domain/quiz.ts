// Study quiz (ROADMAP Q2-3). Questions come only from data the app already shows: structure names on screen, and the
// muscle-card nerve / blood supply / action values that two sources agree on (C2). No new anatomy is written here.
export interface QuizRow {
  sourceKey: string; label: string; kind: string; regionIds: string[]; side: string | null; searchGroupKey?: string;
  names: { en: string; koModern?: string | null; koTraditional?: string | null };
  inspectionEligible?: boolean; localDisplayEligible?: boolean;
}
type Term = { ko: string; koTraditional: string };
export interface QuizCards {
  nerves: Record<string, Term>; arteries: Record<string, Term>;
  cards: Record<string, { tendonOf?: string | null; nerve?: string[]; roots?: string; artery?: string[]; action?: string }>;
}
export type QuizKind = 'name' | 'find' | 'nerve' | 'artery' | 'action';
export const QUIZ_KINDS: Record<QuizKind, string> = {
  name: '이름 맞히기', find: '모형에서 찾기', nerve: '신경지배', artery: '혈액공급', action: '작용',
};
export interface QuizQuestion {
  id: string; kind: QuizKind; prompt: string; quote?: string;
  /** Structure shown (name) or to be found (find), or the muscle the fact is about. */
  targetKey: string; answer: string; choices: string[]; explanation: string;
}

/** Small deterministic generator (mulberry32) so tests can fix the sequence. */
export function makeRng(seed = Date.now()) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
type Rng = () => number;
const pick = <T,>(list: T[], rng: Rng) => list[Math.floor(rng() * list.length)];
function shuffle<T>(list: T[], rng: Rng) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [out[i], out[j]] = [out[j], out[i]]; }
  return out;
}
const HANGUL = /[가-힣]/;
const QUIZ_KINDS_ROW = new Set(['muscle', 'bone', 'joint', 'vessel', 'fascia', 'tendon']);
const sharesRegion = (a: QuizRow, b: QuizRow) => a.regionIds.some(r => b.regionIds.includes(r));
const termName = (t: Term) => t.koTraditional || t.ko;

/** Rows a learner can be asked about: displayable, selectable and named in Korean. */
export function quizRows(rows: QuizRow[]) {
  return rows.filter(r => r.localDisplayEligible !== false && r.inspectionEligible !== false && QUIZ_KINDS_ROW.has(r.kind) && HANGUL.test(r.label));
}

/** Up to `n` distinct wrong labels: same tissue first, then sharing a body region, then anything. */
function distractors(target: QuizRow, pool: QuizRow[], n: number, rng: Rng) {
  const out: string[] = [];
  const tiers = [pool.filter(r => r.kind === target.kind && sharesRegion(r, target)), pool.filter(r => r.kind === target.kind), pool];
  for (const tier of tiers) for (const r of shuffle(tier, rng)) {
    if (out.length >= n) return out;
    if (r.label !== target.label && !out.includes(r.label)) out.push(r.label);
  }
  return out;
}

function choiceSet(answer: string, wrong: string[], rng: Rng) { return wrong.length >= 2 ? shuffle([answer, ...wrong], rng) : null; }

/** "What is this?" for a structure currently drawn, or "Find X" for the click-on-the-model mode. */
export function structureQuestion(kind: 'name' | 'find', rows: QuizRow[], visibleKeys: Set<string>, rng: Rng): QuizQuestion | null {
  const pool = quizRows(rows);
  const shown = pool.filter(r => visibleKeys.has(r.sourceKey));
  if (!shown.length) return null;
  const target = pick(shown, rng);
  const side = target.side === 'left' ? '왼쪽 ' : target.side === 'right' ? '오른쪽 ' : '';
  if (kind === 'find') return { id: `find:${target.sourceKey}`, kind, targetKey: target.sourceKey, answer: target.label, choices: [],
    prompt: `모형에서 ${side}${target.label}을(를) 찾아 누르세요.`, explanation: `${target.label} (${target.names.en})` };
  const choices = choiceSet(target.label, distractors(target, shown.length > 8 ? shown : pool, 3, rng), rng);
  return choices && { id: `name:${target.sourceKey}`, kind, targetKey: target.sourceKey, answer: target.label, choices,
    prompt: '모형에서 강조한 구조의 이름은?', explanation: `${side}${target.label} (${target.names.en})` };
}

/** Muscle fact questions from the two-source muscle cards. */
export function factQuestion(kind: 'nerve' | 'artery' | 'action', rows: QuizRow[], cards: QuizCards, rng: Rng): QuizQuestion | null {
  const muscles = quizRows(rows).filter(r => r.kind === 'muscle');
  const byName = new Map<string, QuizRow>();
  for (const r of muscles) if (!byName.has(r.names.en) || r.side === 'right') byName.set(r.names.en, r);
  const value = (en: string) => {
    const c = cards.cards[en];
    if (kind === 'action') return c?.action ?? null;
    const keys = kind === 'nerve' ? c?.nerve : c?.artery;
    return keys?.length ? keys.map(k => termName((kind === 'nerve' ? cards.nerves : cards.arteries)[k])).join(' · ') : null;
  };
  const candidates = [...byName.entries()].map(([en, row]) => ({ row, value: value(en) })).filter((c): c is { row: QuizRow; value: string } => Boolean(c.value));
  if (candidates.length < 4) return null;
  const target = pick(candidates, rng);
  if (kind === 'action') {
    // Only one choice may fit the quoted action. Different wording can still mean the same movement (quadratus lumborum
    // and intertransversarii both bend the trunk sideways), so wrong muscles come from other body regions only.
    const others = candidates.filter(c => c.value !== target.value && c.row.label !== target.row.label && !sharesRegion(c.row, target.row));
    const wrong = nearFirst([], others, c => c.row.label, rng);
    const choices = choiceSet(target.row.label, wrong, rng);
    return choices && { id: `action:${target.row.names.en}`, kind, targetKey: target.row.sourceKey, answer: target.row.label, choices,
      prompt: '다음 작용을 하는 근육은?', quote: target.value, explanation: `${target.row.label}: ${target.value}` };
  }
  const others = candidates.filter(c => c.value !== target.value);
  const wrong = nearFirst(others.filter(c => sharesRegion(c.row, target.row)), others, c => c.value, rng);
  const choices = choiceSet(target.value, wrong, rng);
  const card = cards.cards[target.row.names.en];
  return choices && { id: `${kind}:${target.row.names.en}`, kind, targetKey: target.row.sourceKey, answer: target.value, choices,
    prompt: `${target.row.label}의 ${kind === 'nerve' ? '신경지배' : '혈액공급'}는?`,
    explanation: `${target.row.label}: ${target.value}${kind === 'nerve' && card?.roots ? ` (척수 분절 ${card.roots})` : ''}` };
}

/** Three distinct wrong answers, from neighbours of the target first, then from the whole body. */
function nearFirst<T>(near: T[], all: T[], text: (item: T) => string, rng: Rng) {
  const out: string[] = [];
  for (const item of [...shuffle(near, rng), ...shuffle(all, rng)]) { const t = text(item); if (!out.includes(t)) out.push(t); if (out.length === 3) break; }
  return out;
}

export function nextQuestion(kind: QuizKind, rows: QuizRow[], visibleKeys: Set<string>, cards: QuizCards | null, rng: Rng) {
  return kind === 'name' || kind === 'find' ? structureQuestion(kind, rows, visibleKeys, rng) : cards ? factQuestion(kind, rows, cards, rng) : null;
}

/** A find answer is right when the clicked structure is the target or its other side / same-named part. */
export function gradeFind(question: QuizQuestion, picked: QuizRow, rows: QuizRow[]) {
  const target = rows.find(r => r.sourceKey === question.targetKey);
  return Boolean(target) && (picked.sourceKey === target!.sourceKey || picked.label === target!.label);
}

// Score and missed questions persist per browser (local study aid; nothing leaves the device).
export interface QuizRecord { answered: number; correct: number; missed: { id: string; kind: QuizKind; prompt: string; answer: string }[] }
const KEY = 'atlas.quiz.v1';
export function readQuizRecord(storage: Pick<Storage, 'getItem'> | null = safeStorage()): QuizRecord {
  try { const v = JSON.parse(storage?.getItem(KEY) ?? 'null'); if (v && Array.isArray(v.missed)) return v; } catch { /* unreadable: start over */ }
  return { answered: 0, correct: 0, missed: [] };
}
export function recordAnswer(record: QuizRecord, question: QuizQuestion, right: boolean): QuizRecord {
  const missed = record.missed.filter(m => m.id !== question.id);
  if (!right) missed.unshift({ id: question.id, kind: question.kind, prompt: question.quote ? `${question.prompt} “${question.quote}”` : question.prompt, answer: question.answer });
  return { answered: record.answered + 1, correct: record.correct + (right ? 1 : 0), missed: missed.slice(0, 20) };
}
export function writeQuizRecord(record: QuizRecord, storage: Pick<Storage, 'setItem'> | null = safeStorage()) {
  try { storage?.setItem(KEY, JSON.stringify(record)); } catch { /* storage full or blocked: keep the session only */ }
}
export function safeStorage(): Storage | null { try { return globalThis.localStorage ?? null; } catch { return null; } }

/** Viewer side of the quiz: highlight one structure without selecting it (no card, no name), and list what is drawn. */
export interface QuizHost { setQuizTarget(key: string | null): void; visibleQuizKeys(): string[] }
export const isQuizHost = (host: unknown): host is QuizHost => typeof (host as QuizHost | null)?.setQuizTarget === 'function';
