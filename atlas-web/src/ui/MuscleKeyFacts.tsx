// 4-3 U2: four lines under a muscle card's title, always in view: where it attaches, its nerve, what it does, which sinew lies on it.
// Each line opens the section that holds the detail. Values come from the same checked data as the tabs (no new content).
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import type { AcupointFile, SinewFile } from '../viewer/acupointLayer';
import { loadAcupoints, loadSinews } from '../viewer/wholeBody/AcupointPanel';
import { loadMuscleCards, type MuscleCardsFile } from './MuscleCardFacts';
import { meridianLinks } from './MeridianLinks';

export type KeyFactTab = '구조' | '기능' | '경락';

/** First sentence only: the tab keeps the rest. */
const firstSentence = (text: string) => text.split(/(?<=[.。])\s+/)[0];

export function keyFactLines(muscle: RuntimeStructureRecord, cards: MuscleCardsFile | null, attach: { origin: string[]; insertion: string[]; text: { origin?: string; insertion?: string } },
  meridian: { acupoints: AcupointFile; sinews: SinewFile } | null) {
  const card = cards?.cards[muscle.names.en];
  const lines: { fact: string; label: string; value: string; tab: KeyFactTab }[] = [];
  const end = (bones: string[], text?: string) => bones.length ? bones.slice(0, 2).join('·') : text ? firstSentence(text).replace(/(에서 시작합니다|에 붙습니다|에 이어집니다|에 닿습니다)\.$/, '') : '';
  const origin = end(attach.origin, attach.text.origin), insertion = end(attach.insertion, attach.text.insertion);
  if (origin || insertion) lines.push({ fact: 'attach', label: '붙는 곳', value: `${origin || '—'} → ${insertion || '—'}`, tab: '구조' });
  const nerves = (card?.nerve ?? []).map(k => cards!.nerves[k]).filter(Boolean).map(t => t.koTraditional || t.ko);
  if (nerves.length) lines.push({ fact: 'nerve', label: '신경', value: [nerves.join('·'), card?.roots].filter(Boolean).join(' · '), tab: '구조' });
  if (card?.action) lines.push({ fact: 'action', label: '작용', value: firstSentence(card.action), tab: '기능' });
  if (meridian) {
    const links = meridianLinks(muscle.sourceKey, muscle.side, meridian.acupoints, meridian.sinews);
    const over = links.over.map(([channel]) => meridian.acupoints.channels[channel]?.nameKo ?? channel);
    const value = links.passing.length ? links.passing.map(code => meridian.sinews.sinews[code].nameKo).join('·')
      : over.length ? `지나는 경근 없음 · 위 경혈 ${over.join('·')}` : '이 모형에서 지나는 경근 없음';
    lines.push({ fact: 'meridian', label: '경락', value, tab: '경락' });
  }
  return lines;
}

export function MuscleKeyFacts({ muscle, attach, onOpen }: {
  muscle: RuntimeStructureRecord; attach: Parameters<typeof keyFactLines>[2]; onOpen: (tab: KeyFactTab) => void;
}) {
  const [cards, setCards] = useState<MuscleCardsFile | null>(null);
  const [meridian, setMeridian] = useState<{ acupoints: AcupointFile; sinews: SinewFile } | null>(null);
  useEffect(() => {
    let live = true;
    void loadMuscleCards().then(f => { if (live) setCards(f); });
    void Promise.all([loadAcupoints(), loadSinews()]).then(([acupoints, sinews]) => { if (live && acupoints && sinews) setMeridian({ acupoints, sinews }); });
    return () => { live = false; };
  }, []);
  const lines = keyFactLines(muscle, cards, attach, meridian);
  if (!lines.length) return null;
  return <dl className="key-facts" aria-label="핵심">
    {lines.map(l => <div key={l.fact} data-fact={l.fact} role="button" tabIndex={0} title={`${l.tab === '경락' ? '한의학적 접근' : l.tab} 칸에서 자세히`}
      onClick={() => onOpen(l.tab)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(l.tab); } }}>
      <dt>{l.label}</dt><dd>{l.value}</dd></div>)}
  </dl>;
}
