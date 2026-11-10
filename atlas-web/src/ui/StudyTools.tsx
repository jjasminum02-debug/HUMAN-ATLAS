// Study tools panel (ROADMAP Q2-3): quiz on what is on screen and on the muscle cards, plus structure bookmarks.
import { useEffect, useMemo, useRef, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import { gradeFind, isQuizHost, makeRng, nextQuestion, QUIZ_KINDS, readQuizRecord, recordAnswer, writeQuizRecord, type QuizCards, type QuizKind, type QuizQuestion } from '../domain/quiz';
import { isStudyViewHost, liveBookmarks, readBookmarks, toggleBookmark, validStudyView, writeBookmarks, type Bookmark } from '../domain/bookmarks';
import { loadMuscleCards } from './MuscleCardFacts';

// One bookmark list shared by the card star and the panel (same tab), persisted in this browser.
const listeners = new Set<(list: Bookmark[]) => void>();
let current: Bookmark[] | null = null;
function useBookmarks(): [Bookmark[], (next: Bookmark[]) => void] {
  const [list, setList] = useState<Bookmark[]>(() => current ??= readBookmarks());
  useEffect(() => { listeners.add(setList); return () => { listeners.delete(setList); }; }, []);
  return [list, next => { current = next; writeBookmarks(next); for (const l of listeners) l(next); }];
}

const KIND_LABEL: Record<string, string> = { muscle: '근육', bone: '뼈', joint: '인대·관절', vessel: '혈관', fascia: '근막', tendon: '힘줄', nerve: '신경' };

export function BookmarkButton({ row, host }: { row: RuntimeStructureRecord; host?: unknown }) {
  const [list, setList] = useBookmarks();
  const saved = list.some(b => b.key === row.sourceKey);
  // The current camera, layers and section are saved with the structure (4-1 step 6).
  const view = () => (isStudyViewHost(host) ? host.captureStudyView() : null) ?? undefined;
  return <button className="bookmark-toggle" aria-pressed={saved} title={saved ? '북마크에서 빼기' : '이 구조를 지금 보는 시점·층과 함께 저장'}
    onClick={() => setList(toggleBookmark(list, { key: row.sourceKey, label: row.label, kind: row.kind, view: view() }))}>{saved ? '★ 저장됨' : '☆ 북마크'}</button>;
}

export function StudyTools({ rows, host, selected, onSelect, onClearSelection, onClose }: {
  rows: RuntimeStructureRecord[]; host: unknown; selected: RuntimeStructureRecord | null;
  onSelect: (key: string) => void; onClearSelection: () => void; onClose: () => void;
}) {
  const [tab, setTab] = useState<'quiz' | 'bookmarks'>('quiz');
  const [kind, setKind] = useState<QuizKind>('name');
  const [cards, setCards] = useState<QuizCards | null>(null);
  const [question, setQuestion] = useState<QuizQuestion | null>(null);
  const [result, setResult] = useState<{ right: boolean; chosen: string } | null>(null);
  const [empty, setEmpty] = useState(false);
  const [record, setRecord] = useState(readQuizRecord);
  const [bookmarks, setBookmarks] = useBookmarks();
  const rng = useRef(makeRng());
  const byKey = useMemo(() => new Map(rows.map(r => [r.sourceKey, r])), [rows]);
  const quizHost = isQuizHost(host) ? host : null;
  useEffect(() => { void loadMuscleCards().then(setCards); }, []);
  useEffect(() => () => quizHost?.setQuizTarget(null), [quizHost]);

  const answer = (right: boolean, chosen: string) => {
    if (!question || result) return;
    setResult({ right, chosen });
    const next = recordAnswer(record, question, right); setRecord(next); writeQuizRecord(next);
  };
  // Find mode: the learner's click on the model (a selection) is the answer.
  const selectedKey = selected?.sourceKey;
  useEffect(() => {
    if (question?.kind === 'find' && !result && selected) answer(gradeFind(question, selected, rows), selected.label);
  }, [selectedKey]); // eslint-disable-line react-hooks/exhaustive-deps

  const ask = (k = kind) => {
    const visible = new Set(quizHost?.visibleQuizKeys() ?? []);
    const q = nextQuestion(k, rows, visible, cards, rng.current);
    setResult(null); setQuestion(q); setEmpty(!q);
    if (q && (k === 'name' || k === 'find')) onClearSelection();
    // The structure is shown for name and fact questions; never for find (that is the task) or action (it is the answer).
    quizHost?.setQuizTarget(q && (k === 'name' || k === 'nerve' || k === 'artery') ? q.targetKey : null);
  };
  const live = liveBookmarks(bookmarks, key => byKey.get(key)?.localDisplayEligible ?? false);

  return <section className="study-tools" id="study-tools" aria-label="학습 도구">
    <div className="study-tools-head">
      <div className="study-tools-tabs" role="tablist">
        <button role="tab" aria-selected={tab === 'quiz'} onClick={() => setTab('quiz')}>퀴즈</button>
        <button role="tab" aria-selected={tab === 'bookmarks'} onClick={() => setTab('bookmarks')}>북마크 {live.length > 0 && <small>{live.length}</small>}</button>
      </div>
      <button className="study-tools-close" aria-label="학습 도구 닫기" onClick={() => { quizHost?.setQuizTarget(null); onClose(); }}>닫기</button>
    </div>
    {tab === 'quiz' ? <div className="quiz" role="tabpanel">
      <div className="quiz-kinds" role="group" aria-label="문제 종류">
        {(Object.keys(QUIZ_KINDS) as QuizKind[]).map(k => <button key={k} aria-pressed={kind === k} onClick={() => { setKind(k); ask(k); }}>{QUIZ_KINDS[k]}</button>)}
      </div>
      {!question ? <>
        <p className="quiet-note">{empty ? '지금 화면에 문제로 낼 구조가 부족합니다. 층을 켜거나 다른 종류를 골라 보세요.'
          : kind === 'name' || kind === 'find' ? '지금 화면에 보이는 구조에서 문제를 냅니다. 층·부위·단면을 바꾸면 범위가 바뀝니다.'
          : '근육 카드에서 두 자료가 일치한 값으로만 문제를 냅니다.'}</p>
        <button className="quiz-start" onClick={() => ask()}>문제 내기</button>
      </> : <>
        <p className="quiz-prompt">{question.prompt}</p>
        {question.quote && <blockquote className="quiz-quote">{question.quote}</blockquote>}
        {question.kind === 'find' ? !result && <p className="quiet-note">모형을 돌리고 층을 바꿔 가며 찾으세요. 누르는 순간 채점합니다.</p>
          : <div className="quiz-choices">{question.choices.map(c => <button key={c} disabled={Boolean(result)}
              className={result ? c === question.answer ? 'is-answer' : c === result.chosen ? 'is-wrong' : '' : ''}
              onClick={() => answer(c === question.answer, c)}>{c}</button>)}</div>}
        {result && <div className={`quiz-result ${result.right ? 'is-right' : 'is-wrong'}`} role="status">
          <strong>{result.right ? '정답' : '오답'}</strong>{!result.right && question.kind === 'find' && <span> — 누른 구조: {result.chosen}</span>}
          <p>{question.explanation}</p>
          <div className="quiz-actions">
            <button onClick={() => ask()}>다음 문제</button>
            {question.kind !== 'find' && <button onClick={() => { quizHost?.setQuizTarget(null); onSelect(question.targetKey); }}>카드 보기</button>}
          </div>
        </div>}
      </>}
      <p className="quiz-score" aria-label="누적 점수">누적 {record.correct}/{record.answered}{record.answered > 0 && ` · ${Math.round(record.correct / record.answered * 100)}%`}</p>
      {record.missed.length > 0 && <details className="quiz-missed"><summary>틀린 문제 {record.missed.length}개</summary>
        <ul>{record.missed.map(m => <li key={m.id}><span>{m.prompt}</span><strong>{m.answer}</strong></li>)}</ul>
        <button className="bone-related-muscle" onClick={() => { const next = { ...record, missed: [] }; setRecord(next); writeQuizRecord(next); }}>목록 비우기</button>
      </details>}
    </div> : <div className="bookmarks" role="tabpanel">
      {live.length ? <ul>{live.map(b => <li key={b.key}>
        <button className="bookmark-open" onClick={() => { onSelect(b.key); if (validStudyView(b.view) && isStudyViewHost(host)) host.restoreStudyView(b.view); }}><span>{byKey.get(b.key)?.label ?? b.label}</span>
          <small>{KIND_LABEL[b.kind] ?? '구조'}{byKey.get(b.key)?.side === 'left' ? ' · 왼쪽' : byKey.get(b.key)?.side === 'right' ? ' · 오른쪽' : ''}{validStudyView(b.view) ? ' · 저장한 시점' : ''}</small></button>
        <button className="bookmark-remove" aria-label={`${b.label} 북마크 빼기`} onClick={() => setBookmarks(bookmarks.filter(x => x.key !== b.key))}>×</button>
      </li>)}</ul> : <p className="quiet-note">구조 카드의 ☆ 북마크를 누르면 그때의 시점·층·단면과 함께 여기에 모입니다. 이 브라우저에만 저장됩니다.</p>}
    </div>}
  </section>;
}
