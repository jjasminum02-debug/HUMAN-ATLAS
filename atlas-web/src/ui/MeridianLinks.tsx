// Muscle card 경락 tab: from a muscle to the meridian sinews whose course lies on it and the acupoints over and around it,
// so a learner can go from the anatomy (대흉근) to the channel picture (족양명위경 · 응창) and back. Data: the same
// acupoints.json / sinews.json the acupoint panel uses (positions computed on this model; 『영추·경근』 courses).
import { useEffect, useMemo, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import { acupointId, locationBasis, sixChannelOf, type AcupointFile, type AcupointInstance, type AcupointTarget, type SinewFile } from '../viewer/acupointLayer';
import { loadAcupoints, loadSinews } from '../viewer/wholeBody/AcupointPanel';

export function meridianLinks(muscleKey: string, side: string | null, acupoints: AcupointFile, sinews: SinewFile) {
  const sides = side === 'left' || side === 'right' ? [side] : ['right', 'left'] as const;
  const passing = sinews.order.filter(code => sides.some(s => sinews.sinews[code].muscles[s as 'right' | 'left'].includes(muscleKey)));
  const byChannel = (points: AcupointInstance[]) => {
    const groups = new Map<string, AcupointInstance[]>();
    for (const p of points) { const channel = acupoints.concepts.find(c => c.code === p.code)?.channel ?? ''; groups.set(channel, [...(groups.get(channel) ?? []), p]); }
    const order = Object.keys(acupoints.channels);
    return [...groups].sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
  };
  const over = acupoints.points.filter(p => p.surfaceOf === muscleKey);
  const near = acupoints.points.filter(p => p.surfaceOf !== muscleKey && p.near.includes(muscleKey));
  return { passing, over: byChannel(over), near: byChannel(near) };
}

type BoundaryHost = { setSinewRegion(keys: string[] | null): void; structureHeight?(key: string): [number, number] | null;
  showHandFootBoundary?(on: boolean): Promise<void>; loadRig?(): Promise<{ landmarks?: { handFootBoundary?: { y: number } } }> };

export function MeridianLinks({ muscle, host, onOpen }: { muscle: RuntimeStructureRecord; host?: BoundaryHost | null; onOpen?: (target: AcupointTarget) => void }) {
  const [data, setData] = useState<{ acupoints: AcupointFile; sinews: SinewFile } | null | 'failed'>(null);
  const side = muscle.side === 'left' ? 'left' : 'right';
  // Sinew regions coloured on the model from the card: one sinew, or a hand and foot sinew of the same name together.
  const [region, setRegion] = useState<string[] | null>(null);
  const regionKeys = useMemo(() => data && data !== 'failed' && region ? [...new Set(region.flatMap(code => data.sinews.sinews[code]?.muscles[side] ?? []))] : null, [data, region, side]);
  useEffect(() => { if (!host) return; host.setSinewRegion(regionKeys); return () => host.setSinewRegion(null); }, [host, regionKeys]);
  useEffect(() => setRegion(null), [muscle.sourceKey]);
  // Hand/foot boundary (『영추·종시』): where this muscle lies against the thoracolumbar level.
  const [boundaryY, setBoundaryY] = useState<number | null>(null);
  const [showBoundary, setShowBoundary] = useState(false);
  useEffect(() => { let live = true; void host?.loadRig?.().then(rig => { if (live) setBoundaryY(rig.landmarks?.handFootBoundary?.y ?? null); }).catch(() => {}); return () => { live = false; }; }, [host]);
  useEffect(() => { if (!host?.showHandFootBoundary) return; void host.showHandFootBoundary(showBoundary); return () => { void host.showHandFootBoundary?.(false); }; }, [host, showBoundary]);
  useEffect(() => {
    let live = true;
    void Promise.all([loadAcupoints(), loadSinews()]).then(([acupoints, sinews]) => { if (live) setData(acupoints && sinews ? { acupoints, sinews } : 'failed'); });
    return () => { live = false; };
  }, []);
  if (data === 'failed') return <p className="quiet-note">경혈·경근 자료를 불러오지 못했습니다.</p>;
  if (!data) return <p className="quiet-note">경혈·경근 자료를 불러오는 중…</p>;
  const { acupoints, sinews } = data, links = meridianLinks(muscle.sourceKey, muscle.side, acupoints, sinews);
  const channels = [...new Set([...links.over, ...links.near].map(([channel]) => channel))];
  const height = host?.structureHeight?.(muscle.sourceKey) ?? null;
  const above = height && boundaryY !== null ? Math.min(1, Math.max(0, (height[1] - boundaryY) / Math.max(height[1] - height[0], 1e-6))) : null;
  const same = (key: string[] | null, codes: string[]) => Boolean(key && key.length === codes.length && codes.every(c => key.includes(c)));
  const regionButton = (codes: string[], label: string) => host && <button className="meridian-region" aria-pressed={same(region, codes)}
    onClick={() => setRegion(same(region, codes) ? null : codes)}>{same(region, codes) ? '영역 끄기' : label}</button>;
  const names = [...new Map(links.passing.map(code => [sixChannelOf(code)?.name, sixChannelOf(code)])).values()].filter((c): c is NonNullable<typeof c> => Boolean(c));
  const points = (groups: [string, AcupointInstance[]][]) => groups.map(([channel, list]) => {
    const c = acupoints.channels[channel];
    return <div className="meridian-group" key={channel}>
      <h5>{c ? <>{c.nameKo} <span>{c.nameHanja}</span></> : channel}</h5>
      <div className="attachment-bone-links">{list.map(p => { const concept = acupoints.concepts.find(x => x.code === p.code)!;
        return <button key={acupointId(p)} className="bone-related-muscle meridian-point" disabled={!onOpen} onClick={() => onOpen?.({ point: acupointId(p) })}>
          {concept.nameKo}<small>{concept.hanja} · {concept.code}</small>{locationBasis(concept.location).kind === 'landmark' && <i className="landmark-mark" title="표지에서 바로 잡는 혈">표지</i>}</button>; })}</div>
    </div>;
  });
  return <div className="meridian-links">
    {channels.length > 0 && <p className="meridian-summary">이 근육 위의 경맥 · <strong>{channels.map(ch => acupoints.channels[ch]?.nameKo ?? ch).join(' · ')}</strong></p>}
    {above !== null && <section className="attachment-section attachment-summary-block hand-foot">
      <h3>손·발 경계</h3>
      <p><strong>{above >= .85 ? '경계 위' : above <= .15 ? '경계 아래' : `경계에 걸침 · 위 ${Math.round(above * 100)}% · 아래 ${Math.round((1 - above) * 100)}%`}</strong>
        {above >= .85 ? ' — 손의 경맥이 맡는 높이' : above <= .15 ? ' — 발의 경맥이 맡는 높이' : ' — 손과 발의 경맥을 함께 본다'}</p>
      <p className="classic-quote">從腰以上者，手太陰陽明皆主之；從腰以下者，足太陰陽明皆主之。… 病在腰者，取之膕。<small>『영추·종시』</small></p>
      <p className="quiet-note">원문은 허리(腰)를 기준으로 손·발의 태음·양명을 말합니다. 수업에서는 이를 손·발 경맥 전체로 넓혀 횡격막 높이에서 가르며, 이 모형은 흉요 이행부(T12–L1 추간판 중심)를 경계로 씁니다.</p>
      {host?.showHandFootBoundary && <label className="sinew-region-toggle"><input type="checkbox" checked={showBoundary} onChange={e => setShowBoundary(e.target.checked)}/> 경계 높이 보기 <small>모형 위 보라색 면</small></label>}
    </section>}
    <section className="attachment-section attachment-summary-block">
      <h3>지나가는 경근</h3>
      {links.passing.length ? <ul className="meridian-sinews">{links.passing.map(code => { const s = sinews.sinews[code], six = sixChannelOf(code);
        return <li key={code}>
          {six && <b className="six-channel" title={six.hanja}>{six.name}</b>}
          <button className="bone-related-muscle meridian-point" disabled={!onOpen} onClick={() => { setRegion(null); onOpen?.({ sinew: code, side }); }}>{s.nameKo}<small>{s.hanja}</small></button>
          {regionButton([code], `영역 보기 · 근육 ${s.muscles[side].length}`)}
        </li>; })}</ul>
        : <p className="empty-answer">이 모형에서 경근 경로가 이 근육 위를 지나지 않습니다.</p>}
    </section>
    {names.length > 0 && <section className="attachment-section attachment-summary-block">
      <h3>같은 이름으로 묶기</h3>
      <ul className="meridian-sinews">{names.map(six => { const partner = links.passing.includes(six.hand) ? six.foot : six.hand;
        return <li key={six.name}><b className="six-channel">{six.name}</b>
          <span className="six-pair">{sinews.sinews[six.hand].nameKo} + {sinews.sinews[six.foot].nameKo}</span>
          {regionButton([six.hand, six.foot], '손발 함께 칠하기')}
          {onOpen && <button className="sinew-anchor" onClick={() => { setRegion(null); onOpen({ sinew: partner, side }); }}>{sinews.sinews[partner].nameKo} 보기</button>}
        </li>; })}</ul>
      <p className="quiet-note">같은 이름의 양경은 얼굴에서 손에서 발로 이어집니다(수태양 → 족태양은 눈 안쪽, 수양명 → 족양명은 코 옆, 수소양 → 족소양은 눈 바깥쪽).
        음경은 경맥 흐름으로 직접 잇지 않고 육경의 같은 이름으로 함께 묶어 봅니다. 여러 부위가 함께 긴장했을 때 공통된 이름을 찾는 출발점입니다.</p>
    </section>}
    <section className="attachment-section attachment-summary-block">
      <h3>바로 위의 경혈</h3>
      {links.over.length ? points(links.over) : <p className="empty-answer">이 근육 표면에 놓인 경혈이 없습니다.</p>}
    </section>
    {links.near.length > 0 && <section className="attachment-section attachment-summary-block">
      <h3>주변 경혈</h3>
      {points(links.near)}
    </section>}
    <p className="card-hint">경혈·경근 이름을 누르면 경혈·경근 창에서 위치를 보여 줍니다.</p>
  </div>;
}
