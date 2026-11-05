// Muscle card innervation, blood supply and action summary (ROADMAP C2). Data: /__atlas/v2/muscle-cards.json —
// only values two independent sources agree on (atlas-data/pipeline/build_muscle_cards.py).
import { useEffect, useState, type ReactNode } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';

type Term = { ko: string; koTraditional: string; en: string; structure?: string; structures?: string[] };
type Card = { concept?: string; tendonOf?: string | null; nerve?: string[]; roots?: string; artery?: string[]; action?: string };
export type MuscleCardsFile = { nerves: Record<string, Term>; arteries: Record<string, Term>; cards: Record<string, Card> };
let file: Promise<MuscleCardsFile | null> | undefined;
export const loadMuscleCards = () => file ??= fetch('/__atlas/v2/muscle-cards.json').then(r => r.ok ? r.json() : null).catch(() => { file = undefined; return null; });

function useMuscleCards() {
  const [cards, setCards] = useState<MuscleCardsFile | null>(null);
  useEffect(() => { let live = true; void loadMuscleCards().then(f => { if (live) setCards(f); }); return () => { live = false; }; }, []);
  return cards;
}

const termName = (t: Term) => t.ko === t.koTraditional ? t.ko : `${t.ko} (${t.koTraditional})`;
/** The drawn structure with this English name, on the given side when the model has both sides. */
const rowNamed = (rows: Map<string, RuntimeStructureRecord>, kind: RuntimeStructureRecord['kind'], en: string, side: string | null) =>
  [...rows.values()].find(r => r.kind === kind && r.names.en === en && r.side === side) ?? [...rows.values()].find(r => r.kind === kind && r.names.en === en);

/** Innervation from the C2 table; renders `fallback` when the muscle has none. */
export function MuscleNerves({ muscle, rows, onSelect, fallback }: {
  muscle: RuntimeStructureRecord; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void; fallback: ReactNode;
}) {
  const data = useMuscleCards(), card = data?.cards[muscle.names.en];
  if (!data || !card?.nerve?.length) return <>{card?.tendonOf !== undefined ? <p>힘줄이라 따로 신경지배를 표시하지 않습니다.</p> : fallback}</>;
  const nerveRow = (en: string) => rowNamed(rows, 'nerve', en, muscle.side);
  return <>
    <ul className="muscle-facts">{card.nerve.map(key => {
      const t = data.nerves[key], row = t.structure ? nerveRow(t.structure) : undefined;
      return <li key={key}>{row ? <button className="bone-related-muscle" onClick={() => onSelect(row.sourceKey)}>{termName(t)}</button> : <span>{termName(t)}</span>}<small>{t.en}</small></li>;
    })}</ul>
    {card.roots && <p className="muscle-facts-roots">척수 분절 <b>{card.roots}</b></p>}
  </>;
}

export function MuscleBloodSupply({ muscle, rows, onSelect }: { muscle: RuntimeStructureRecord; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void }) {
  const data = useMuscleCards(), card = data?.cards[muscle.names.en];
  if (!data || card?.tendonOf !== undefined) return null;
  return <section className="attachment-section attachment-summary-block">
    <h3>혈액공급</h3>
    {card?.artery?.length ? <ul className="muscle-facts">{card.artery.map(key => {
      const t = data.arteries[key], vessel = t.structures?.map(en => rowNamed(rows, 'vessel', en, muscle.side)).find(Boolean);
      return <li key={key}>{vessel ? <button className="bone-related-muscle" onClick={() => onSelect(vessel.sourceKey)}>{termName(t)}</button> : <span>{termName(t)}</span>}<small>{t.en}</small></li>;
    })}</ul>
      : <p>두 자료가 일치하는 혈관 정보가 아직 없습니다.</p>}
    <p className="quiet-note">신경 분지와 혈관 분포에는 개인차가 있습니다.</p>
  </section>;
}

export function MuscleActionSummary({ muscle }: { muscle: RuntimeStructureRecord }) {
  const data = useMuscleCards(), card = data?.cards[muscle.names.en];
  if (!card?.action) return null;
  return <section className="attachment-section attachment-summary-block muscle-action-summary">
    <h3>작용 요약</h3>
    <p>{card.action}</p>
  </section>;
}

/** Q2-1 vessel card: what the vessel is and, for arteries, the muscles whose C2 blood supply names it. */
export function VesselCard({ vessel, rows, onSelect }: { vessel: RuntimeStructureRecord; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void }) {
  const data = useMuscleCards();
  const keys = data ? Object.entries(data.arteries).filter(([, t]) => t.structures?.includes(vessel.names.en)).map(([key]) => key) : [];
  const supplied = data ? Object.entries(data.cards).filter(([, c]) => c.artery?.some(k => keys.includes(k)))
    .map(([en]) => rowNamed(rows, 'muscle', en, vessel.side)).filter((r): r is RuntimeStructureRecord => Boolean(r?.localDisplayEligible)) : [];
  const unique = [...new Map(supplied.map(r => [r.label, r])).values()];
  return <>
    <section className="attachment-section attachment-summary-block vessel-card" aria-label="혈관">
      <h3>{vessel.tissue === 'vein' ? '정맥' : vessel.tissue === 'heart' ? '심장' : '동맥'}</h3>
      <p>{vessel.tissue === 'vein' ? '조직의 혈액을 모아 심장 쪽으로 돌려보내는 혈관입니다.'
        : vessel.tissue === 'heart' ? '혈액을 온몸과 허파로 내보내는 심장의 한 부분입니다.' : '심장에서 나온 혈액을 조직으로 보내는 혈관입니다.'}</p>
    </section>
    {vessel.tissue === 'artery' && <section className="attachment-section attachment-summary-block vessel-supplied">
      <h3>혈액을 받는 근육</h3>
      {unique.length ? <div className="attachment-bone-links">{unique.map(r => <button key={r.sourceKey} className="bone-related-muscle" onClick={() => onSelect(r.sourceKey)}>{r.label}</button>)}</div>
        : <p>근육 카드의 혈액공급 자료에 이 동맥이 아직 없습니다.</p>}
    </section>}
    <p className="quiet-note">혈관은 Z-Anatomy 모형의 중심선을 따라 그린 관이며, 가지와 주행에는 개인차가 큽니다.</p>
  </>;
}
