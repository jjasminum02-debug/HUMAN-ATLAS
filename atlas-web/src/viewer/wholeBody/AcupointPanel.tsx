// Acupoint panel (ROADMAP 4-1 step 7): channel points on the model, their location and the structures around them.
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../datasets/integration';
import { acupointId, channelPath, channelSide, type AcupointFile, type AcupointHost, type SinewFile } from '../acupointLayer';

const SIDE = { right: '오른쪽', left: '왼쪽', midline: '정중선' } as const;
let file: Promise<AcupointFile | null> | undefined;
let sinewFile: Promise<SinewFile | null> | undefined;
const loadSinews = () => sinewFile ??= fetch('/__atlas/v2/sinews.json').then(r => r.ok ? r.json() : null).catch(() => { sinewFile = undefined; return null; });
const load = () => file ??= fetch('/__atlas/v2/acupoints.json').then(r => r.ok ? r.json() : null).catch(() => { file = undefined; return null; });

export function AcupointPanel({ host, rows, onSelectStructure, onClose }: {
  host: AcupointHost; rows: Map<string, RuntimeStructureRecord>; onSelectStructure: (key: string, side: string | null) => void; onClose: () => void;
}) {
  const [data, setData] = useState<AcupointFile | null>(null);
  const [failed, setFailed] = useState(false);
  const [side, setSide] = useState<'right' | 'left'>('right');
  const [selected, setSelected] = useState<string | null>(null);
  const [channel, setChannel] = useState('LU');
  const [mode, setMode] = useState<'points' | 'sinews'>('points');
  useEffect(() => { let live = true; void load().then(f => { if (!live) return; if (f) setData(f); else setFailed(true); }); return () => { live = false; }; }, []);
  useEffect(() => {
    if (!data) return;
    host.showAcupoints(data, id => { setSelected(id); if (!id.endsWith(':midline')) setSide(id.endsWith(':left') ? 'left' : 'right'); host.selectAcupoint(id, false); });
    return () => host.showAcupoints(null);
  }, [host, data]);
  useEffect(() => { if (data) host.showAcupointChannel(mode === 'points' ? channel : ''); }, [host, data, channel, mode]);
  const choose = (id: string) => { setSelected(id); host.selectAcupoint(id); };
  if (failed) return <aside className="acupoint-panel" aria-label="경혈"><p className="quiet-note">경혈 자료를 불러오지 못했습니다.</p></aside>;
  if (!data) return <aside className="acupoint-panel" aria-label="경혈"><p className="quiet-note">경혈 자료를 불러오는 중…</p></aside>;
  const point = data.points.find(p => acupointId(p) === selected), concept = point && data.concepts.find(c => c.code === point.code);
  const current = data.channels[channel];
  return <aside className="acupoint-panel" aria-label="경혈">
    <div className="acupoint-panel-head"><strong>경혈·경근</strong><button aria-label="경혈 닫기" onClick={onClose}>닫기</button></div>
    <div className="movement-side acupoint-mode" role="group" aria-label="보기">
      <button aria-pressed={mode === 'points'} onClick={() => setMode('points')}>경혈</button>
      <button aria-pressed={mode === 'sinews'} onClick={() => { setMode('sinews'); setSelected(null); host.selectAcupoint(null, false); }}>경근</button>
    </div>
    {mode === 'sinews' ? <SinewView host={host} rows={rows} onSelectStructure={onSelectStructure}/> : <>
    <div className="acupoint-channels" role="group" aria-label="경맥">
      {Object.entries(data.channels).map(([code, c]) => <button key={code} aria-pressed={channel === code} title={`${c.nameKo} ${c.nameHanja}`}
        onClick={() => { setChannel(code); setSelected(null); host.selectAcupoint(null, false); }}>{c.nameKo.replace(/^[수족]/, '').replace(/^(태음|양명|소음|태양|궐음|소양)/, '')}<small>{code}</small></button>)}
    </div>
    {current && !current.midline && <div className="movement-side" role="group" aria-label="몸의 쪽">
      {(['right', 'left'] as const).map(s => <button key={s} aria-pressed={side === s} onClick={() => { setSide(s); if (point && point.side !== 'midline') choose(acupointId({ code: point.code, side: s })); }}>{s === 'right' ? '오른쪽' : '왼쪽'}</button>)}
    </div>}
    {point && concept && <section className="acupoint-detail" aria-label="선택한 경혈">
      <h4>{concept.nameKo} <span>{concept.hanja} · {concept.code} · {SIDE[point.side]}</span></h4>
      <p>{concept.location}</p>
      {point.near.length > 0 && <><h5>주변 구조</h5><div className="attachment-bone-links">{point.near.map(key => rows.get(key)).filter((r): r is RuntimeStructureRecord => Boolean(r))
        .map(r => <button key={r.sourceKey} className="bone-related-muscle" onClick={() => onSelectStructure(r.sourceKey, r.side)}>{r.label}</button>)}</div></>}
    </section>}
    {current && <section className="acupoint-channel">
      <h4>{current.nameKo}<span>{current.nameHanja} · {current.codes.length}혈</span></h4>
      <ol>{channelPath(data, channel, channelSide(data, channel, side)).map(p => { const c = data.concepts.find(x => x.code === p.code)!;
        return <li key={acupointId(p)}><button aria-pressed={selected === acupointId(p)} onClick={() => choose(acupointId(p))}>
          <span>{c.nameKo}</span><small>{c.hanja} · {c.code}</small></button></li>; })}</ol>
    </section>}
    <p className="quiet-note">뼈 표지와 골도분촌(비례촌)으로 이 모형 위에 계산한 교육용 위치이며, 실제 취혈·시술 안내가 아닙니다. 관절을 움직이면 함께 따라갑니다.</p>
    </>}
  </aside>;
}

/** Meridian sinews: course through the binding regions (『영추·경근』) and the muscles the line lies on in this model. */
function SinewView({ host, rows, onSelectStructure }: {
  host: AcupointHost; rows: Map<string, RuntimeStructureRecord>; onSelectStructure: (key: string, side: string | null) => void;
}) {
  const [data, setData] = useState<SinewFile | null>(null);
  const [failed, setFailed] = useState(false);
  const [sinew, setSinew] = useState('BL');
  const [side, setSide] = useState<'right' | 'left'>('right');
  useEffect(() => { let live = true; void loadSinews().then(f => { if (!live) return; if (f) setData(f); else setFailed(true); }); return () => { live = false; }; }, []);
  useEffect(() => { if (data) host.showSinew(data, sinew); return () => host.showSinew(null, null); }, [host, data, sinew]);
  if (failed) return <p className="quiet-note">경근 자료를 불러오지 못했습니다.</p>;
  if (!data) return <p className="quiet-note">경근 자료를 불러오는 중…</p>;
  const current = data.sinews[sinew];
  const muscles = [...new Map(current.muscles[side].map(key => rows.get(key)).filter((r): r is RuntimeStructureRecord => Boolean(r)).map(r => [r.label, r])).values()];
  return <>
    <div className="acupoint-channels" role="group" aria-label="경근">
      {data.order.map(code => { const s = data.sinews[code]; return <button key={code} aria-pressed={sinew === code} title={`${s.nameKo} ${s.hanja}`}
        onClick={() => setSinew(code)}>{s.nameKo.replace(/경근$/, '')}<small>{code}</small></button>; })}
    </div>
    <section className="acupoint-detail sinew-detail" aria-label="선택한 경근">
      <h4>{current.nameKo} <span>{current.hanja}</span></h4>
      {current.strands.map((strand, i) => <ol key={i} className="sinew-strand">{strand.map((n, j) => <li key={j}>{n.label}</li>)}</ol>)}
      {current.internal.length > 0 && <p className="quiet-note">몸속 경로(선으로 그리지 않음): {current.internal.join(' · ')}</p>}
      <div className="movement-side" role="group" aria-label="몸의 쪽">
        {(['right', 'left'] as const).map(s => <button key={s} aria-pressed={side === s} onClick={() => setSide(s)}>{s === 'right' ? '오른쪽' : '왼쪽'}</button>)}
      </div>
      {muscles.length > 0 && <><h5>경로가 지나는 근육</h5><div className="attachment-bone-links">{muscles
        .map(r => <button key={r.sourceKey} className="bone-related-muscle" onClick={() => onSelectStructure(r.sourceKey, r.side)}>{r.label}</button>)}</div></>}
    </section>
    <p className="quiet-note">『영추·경근』의 맺히는 곳(結)을 이 모형의 해당 부위에 이어 그린 교육용 경로입니다. 근육 목록은 선 아래 근육을 모형에서 잰 것이며, 시술 안내가 아닙니다.</p>
  </>;
}
