// Acupoint panel (ROADMAP 4-1 step 7): channel points on the model, their location and the structures around them.
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../datasets/integration';
import { acupointId, channelPath, channelSide, isBinding, landmarkId, LOCATION_BASIS_LABEL, locationBasis, sixChannelOf, type AcupointInstance, type Landmark, type AcupointFile, type AcupointHost, type AcupointTarget, type SinewFile } from '../acupointLayer';

const SIDE = { right: '오른쪽', left: '왼쪽', midline: '정중선' } as const;
let file: Promise<AcupointFile | null> | undefined;
let sinewFile: Promise<SinewFile | null> | undefined;
export const loadSinews = () => sinewFile ??= fetch('/__atlas/v2/sinews.json').then(r => r.ok ? r.json() : null).catch(() => { sinewFile = undefined; return null; });
export const loadAcupoints = () => file ??= fetch('/__atlas/v2/acupoints.json').then(r => r.ok ? r.json() : null).catch(() => { file = undefined; return null; });

export function AcupointPanel({ host, rows, request = null, onSelectStructure, onClose }: {
  host: AcupointHost; rows: Map<string, RuntimeStructureRecord>; request?: (AcupointTarget & { revision: number }) | null;
  onSelectStructure: (key: string, side: string | null) => void; onClose: () => void;
}) {
  const [data, setData] = useState<AcupointFile | null>(null);
  const [failed, setFailed] = useState(false);
  const [side, setSide] = useState<'right' | 'left'>('right');
  const [selected, setSelected] = useState<string | null>(null);
  const [channel, setChannel] = useState('LU');
  const [mode, setMode] = useState<'points' | 'sinews' | 'landmarks'>('points');
  useEffect(() => { let live = true; void loadAcupoints().then(f => { if (!live) return; if (f) setData(f); else setFailed(true); }); return () => { live = false; }; }, []);
  useEffect(() => {
    if (!data) return;
    host.showAcupoints(data, id => { setSelected(id); if (!id.endsWith(':midline')) setSide(id.endsWith(':left') ? 'left' : 'right'); host.selectAcupoint(id, false); });
    return () => host.showAcupoints(null);
  }, [host, data]);
  useEffect(() => { if (data) host.showAcupointChannel(mode === 'points' ? channel : ''); }, [host, data, channel, mode]);
  // 2026-11-20: next to a channel's points, its sinew in faint teal (the 12 regular channels have one; 督·任 do not).
  const [sinews, setSinews] = useState<SinewFile | null>(null);
  useEffect(() => { let live = true; void loadSinews().then(f => { if (live) setSinews(f); }); return () => { live = false; }; }, []);
  const [withSinew, setWithSinew] = useState(true);
  const [others, setOthers] = useState(false);
  useEffect(() => { host.showOtherChannels?.(mode === 'points' && others); }, [host, others, mode, data]);
  useEffect(() => {
    if (mode !== 'points' || !sinews || !withSinew || !sinews.sinews[channel]) return;
    host.showSinew(sinews, channel, 'companion'); return () => host.showSinew(null, null);
  }, [host, sinews, channel, mode, withSinew]);
  // Opened from a muscle card: go to that point (its channel) or that sinew.
  const [sinewRequest, setSinewRequest] = useState<{ sinew: string; side: 'right' | 'left'; revision: number } | null>(null);
  const [landmarkRequest, setLandmarkRequest] = useState<{ id: string; revision: number } | null>(null);
  useEffect(() => {
    if (!request || !data) return;
    if ('sinew' in request) { setMode('sinews'); setSelected(null); host.selectAcupoint(null, false); setSinewRequest(request); return; }
    if ('landmark' in request) { setMode('landmarks'); setSelected(null); host.selectAcupoint(null, false); setLandmarkRequest({ id: request.landmark, revision: request.revision }); return; }
    goToPoint(request.point);
  }, [request?.revision, data]); // eslint-disable-line react-hooks/exhaustive-deps
  /** Show one point ("BL60:right") in its channel; used by a muscle card and by the sinew view's binding places. */
  function goToPoint(id: string) {
    const concept = data?.concepts.find(c => c.code === id.split(':')[0]);
    if (!concept || !data?.points.some(p => acupointId(p) === id)) return;
    setMode('points'); setChannel(concept.channel); setSelected(id);
    if (!id.endsWith(':midline')) setSide(id.endsWith(':left') ? 'left' : 'right');
    host.selectAcupoint(id);
  }
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
      <button aria-pressed={mode === 'landmarks'} onClick={() => { setMode('landmarks'); setSelected(null); host.selectAcupoint(null, false); }}>기준점</button>
    </div>
    {mode === 'landmarks' ? <LandmarkView host={host} file={data} rows={rows} onSelectStructure={onSelectStructure} request={landmarkRequest}/>
    : mode === 'sinews' ? <SinewView host={host} rows={rows} request={sinewRequest} acupoints={data} onPoint={goToPoint} onSelectStructure={onSelectStructure}/> : <>
    <Picker label="경맥" current={current ? `${current.nameKo} ${channel}` : channel} items={Object.entries(data.channels).map(([code, c]) => ({ code, title: `${c.nameKo} ${c.nameHanja}`,
      short: c.nameKo.replace(/^[수족]/, '').replace(/^(태음|양명|소음|태양|궐음|소양)/, '') }))} value={channel}
      onPick={code => { setChannel(code); setSelected(null); host.selectAcupoint(null, false); }}/>
    {current && !current.midline && <div className="movement-side" role="group" aria-label="몸의 쪽">
      {(['right', 'left'] as const).map(s => <button key={s} aria-pressed={side === s} onClick={() => { setSide(s); if (point && point.side !== 'midline') choose(acupointId({ code: point.code, side: s })); }}>{s === 'right' ? '오른쪽' : '왼쪽'}</button>)}
    </div>}
    {sinews?.sinews[channel] && <label className="acupoint-sinew-toggle"><input type="checkbox" checked={withSinew} onChange={e => setWithSinew(e.target.checked)}/>
      <i aria-hidden="true"/>{sinews.sinews[channel].nameKo} 함께 보기</label>}
    <label className="acupoint-sinew-toggle is-others"><input type="checkbox" checked={others} onChange={e => setOthers(e.target.checked)}/><i aria-hidden="true"/>다른 경맥도 옅게</label>
    {/* 4-3 U10: the answer first (name, where, how it is found), the structures around it in folds. */}
    {point && concept && <section className="acupoint-detail" aria-label="선택한 경혈">
      <h4>{concept.nameKo} <span>{concept.hanja} · {concept.code} · {SIDE[point.side]}</span></h4>
      <p>{concept.location}</p>
      <PointBasis location={concept.location}/>
      <Beneath point={point} rows={rows} onSelectStructure={onSelectStructure}/>
      {point.near.length > 0 && <details className="point-fold"><summary>주변 구조 <small>{point.near.length}</small></summary><div className="attachment-bone-links">{point.near.map(key => rows.get(key)).filter((r): r is RuntimeStructureRecord => Boolean(r))
        .map(r => <button key={r.sourceKey} className="bone-related-muscle" onClick={() => onSelectStructure(r.sourceKey, r.side)}>{r.label}</button>)}</div></details>}
    </section>}
    {current && <section className="acupoint-channel">
      <h4>{current.nameKo}<span>{current.nameHanja} · {current.codes.length}혈</span></h4>
      <ol>{channelPath(data, channel, channelSide(data, channel, side)).map(p => { const c = data.concepts.find(x => x.code === p.code)!;
        return <li key={acupointId(p)}><button aria-pressed={selected === acupointId(p)} onClick={() => choose(acupointId(p))}>
          <span>{c.nameKo}</span><small>{c.hanja} · {c.code}</small></button></li>; })}</ol>
    </section>}
    <PanelLimits items={['경혈은 뼈 표지와 골도분촌(비례촌)으로 이 모형 위에 계산한 교육용 위치이며, 실제 취혈·시술 안내가 아닙니다. 관절을 움직이면 함께 따라갑니다.',
      '아래 지나는 혈관·신경은 혈 자리에서 곧게 안쪽으로 6cm까지, 1cm 반경 안을 이 모형에서 잰 값입니다. 사람·체형·자세에 따라 다르며 자침 깊이 기준이 아닙니다.']}/>
    </>}
  </aside>;
}

/** Meridian sinews: course through the binding regions (『영추·경근』) and the muscles the line lies on in this model. */
function SinewView({ host, rows, request, acupoints, onPoint, onSelectStructure }: {
  host: AcupointHost; rows: Map<string, RuntimeStructureRecord>; request: { sinew: string; side: 'right' | 'left'; revision: number } | null;
  acupoints: AcupointFile; onPoint: (id: string) => void; onSelectStructure: (key: string, side: string | null) => void;
}) {
  const [region, setRegion] = useState(true);
  // Hand and foot sinews of the same name (태양 = 수태양 + 족태양) drawn and coloured together.
  const [paired, setPaired] = useState(false);
  const [data, setData] = useState<SinewFile | null>(null);
  const [failed, setFailed] = useState(false);
  const [sinew, setSinew] = useState(request?.sinew ?? 'BL');
  const [side, setSide] = useState<'right' | 'left'>(request?.side ?? 'right');
  useEffect(() => { if (request) { setSinew(request.sinew); setSide(request.side); } }, [request]);
  useEffect(() => { let live = true; void loadSinews().then(f => { if (!live) return; if (f) setData(f); else setFailed(true); }); return () => { live = false; }; }, []);
  const six = sixChannelOf(sinew), shown = paired && six ? [six.hand, six.foot] : [sinew];
  useEffect(() => { if (data) host.showSinew(data, shown); return () => host.showSinew(null, null); }, [host, data, shown.join()]); // eslint-disable-line react-hooks/exhaustive-deps
  // The sinew's region: every muscle its course lies on, coloured on the model (on by default).
  useEffect(() => { host.setSinewRegion(data && region ? [...new Set(shown.flatMap(code => data.sinews[code].muscles[side]))] : null); return () => host.setSinewRegion(null); }, [host, data, shown.join(), side, region]); // eslint-disable-line react-hooks/exhaustive-deps
  if (failed) return <p className="quiet-note">경근 자료를 불러오지 못했습니다.</p>;
  if (!data) return <p className="quiet-note">경근 자료를 불러오는 중…</p>;
  const current = data.sinews[sinew];
  const muscles = [...new Map(current.muscles[side].map(key => rows.get(key)).filter((r): r is RuntimeStructureRecord => Boolean(r)).map(r => [r.label, r])).values()];
  return <>
    <Picker label="경근" current={`${current.nameKo} ${sinew}`} value={sinew} onPick={setSinew}
      items={data.order.map(code => ({ code, title: `${data.sinews[code].nameKo} ${data.sinews[code].hanja}`, short: data.sinews[code].nameKo.replace(/경근$/, '') }))}/>
    <section className="acupoint-detail sinew-detail" aria-label="선택한 경근">
      <h4>{current.nameKo} <span>{current.hanja}</span></h4>
      {current.strands.map((strand, i) => <ol key={i} className="sinew-strand">{strand.map((n, j) => {
        const concept = acupoints.concepts.find(c => c.code === n.anchor), id = acupointId({ code: n.anchor, side: acupoints.points.some(p => p.code === n.anchor && p.side === 'midline') ? 'midline' : side });
        return <li key={j} className={isBinding(n) ? 'sinew-binding' : undefined}>{isBinding(n) && <b className="binding-mark">結</b>}{n.label}
          {concept && <button className="sinew-anchor" onClick={() => onPoint(id)} title="이 자리를 경혈 보기로">{concept.nameKo}<small>{concept.code}</small></button>}</li>; })}</ol>)}
      <p className="card-hint"><b className="binding-mark">結</b> 경근이 뼈·관절에 맺히는 곳(모형 위 큰 호박색 점) — 그 자리의 혈은 매번 같은 곳을 짚기 쉽습니다.</p>
      {current.internal.length > 0 && <p className="quiet-note">몸속 경로(선으로 그리지 않음): {current.internal.join(' · ')}</p>}
      <div className="movement-side" role="group" aria-label="몸의 쪽">
        {(['right', 'left'] as const).map(s => <button key={s} aria-pressed={side === s} onClick={() => setSide(s)}>{s === 'right' ? '오른쪽' : '왼쪽'}</button>)}
      </div>
      <label className="sinew-region-toggle"><input type="checkbox" checked={region} onChange={e => setRegion(e.target.checked)}/> 영역 칠하기 <small>경로가 지나는 근육을 호박색으로</small></label>
      {six && <label className="sinew-region-toggle"><input type="checkbox" checked={paired} onChange={e => setPaired(e.target.checked)}/> 같은 이름 함께 · {six.name}({six.hanja})
        <small>{data.sinews[six.hand].nameKo} + {data.sinews[six.foot].nameKo}</small></label>}
      {muscles.length > 0 && <><h5>경로가 지나는 근육</h5><div className="attachment-bone-links">{muscles
        .map(r => <button key={r.sourceKey} className="bone-related-muscle" onClick={() => onSelectStructure(r.sourceKey, r.side)}>{r.label}</button>)}</div></>}
    </section>
    <PanelLimits items={['『영추·경근』의 맺히는 곳(結)을 이 모형의 해당 부위에 이어 그린 교육용 경로입니다. 근육 목록은 선 아래 근육을 모형에서 잰 것이며, 시술 안내가 아닙니다.']}/>
  </>;
}

/** 4-3 U10: the channel (or sinew) choice folded to one button; the 14-button grid opens under it. */
function Picker({ label, current, items, value, onPick }: {
  label: string; current: string; value: string; onPick: (code: string) => void; items: { code: string; title: string; short: string }[];
}) {
  const [open, setOpen] = useState(false);
  return <div className="channel-picker">
    <button className="channel-picker-toggle" aria-expanded={open} onClick={() => setOpen(o => !o)}><small>{label}</small>{current}</button>
    {open && <div className="acupoint-channels" role="group" aria-label={label}>
      {items.map(i => <button key={i.code} aria-pressed={value === i.code} title={i.title} onClick={() => { onPick(i.code); setOpen(false); }}>{i.short}<small>{i.code}</small></button>)}
    </div>}
  </div>;
}

/** One "자료와 한계" fold at the panel's bottom (same rule as the cards, U1). */
function PanelLimits({ items }: { items: string[] }) {
  return <details className="card-limits"><summary>자료와 한계</summary><ul>{items.map(t => <li key={t}>{t}</li>)}</ul></details>;
}

/** How the point is found (from its standard location text): on a landmark is the easiest to find the same way every time. */
function PointBasis({ location }: { location: string }) {
  const basis = locationBasis(location);
  return <p className={`point-basis basis-${basis.kind}`}><b>취혈 기준</b> {LOCATION_BASIS_LABEL[basis.kind]}{basis.cun ? ` ${basis.cun}촌` : ''}
    {basis.marks.length > 0 && <small> · 표지: {basis.marks.join('·')}</small>}</p>;
}

/** Vessels and nerves under the point, nearest first, with the depth measured on this model. */
function Beneath({ point, rows, onSelectStructure }: { point: AcupointInstance; rows: Map<string, RuntimeStructureRecord>; onSelectStructure: (key: string, side: string | null) => void }) {
  const list = (point.beneath ?? []).map(b => ({ ...b, row: rows.get(b.key) })).filter((b): b is { key: string; depth: number; row: RuntimeStructureRecord } => Boolean(b.row));
  if (!list.length) return null;
  const tone = (r: RuntimeStructureRecord) => r.kind === 'nerve' ? 'nerve' : r.tissue === 'artery' ? 'artery' : 'vein';
  return <details className="point-fold" open><summary>아래 지나는 혈관·신경 <small>{list.length}</small></summary>
    <ul className="point-beneath">{list.map(({ key, depth, row }) => <li key={key}>
      <i className={`beneath-${tone(row)}`}/><button className="bone-related-muscle" onClick={() => onSelectStructure(row.sourceKey, row.side)}>{row.label}</button>
      <small>{depth < 3 ? '바로 아래' : `약 ${Math.round(depth / 5) * 5 || depth}mm`}</small></li>)}</ul></details>;
}

const LANDMARK_GROUPS: { name: string; ids: string[] }[] = [
  { name: '머리·목', ids: ['eop', 'suboccipital'] },
  { name: '가슴·어깨·팔', ids: ['jugularNotch', 'scj', 'coracoid', 'greaterTubercle', 'lateralEpicondyle', 'snuffbox'] },
  { name: '배·골반', ids: ['navel', 'rib12', 'iliacCrest', 'asis', 'psis', 'greaterTrochanter'] },
  { name: '다리', ids: ['fibularHead', 'lateralMalleolus', 'medialMalleolus'] }];

/**
 * Bony reference points of the diagnosis practicum and the two-point distances compared left and right to find the
 * short side. Lengths follow the current pose (bend the trunk sideways in 관절 움직임 and one side shortens).
 */
function LandmarkView({ host, file, rows, onSelectStructure, request = null }: {
  host: AcupointHost; file: AcupointFile; rows: Map<string, RuntimeStructureRecord>; onSelectStructure: (key: string, side: string | null) => void;
  /** Opened from a muscle card (4-3 U4): start with this landmark chosen. */
  request?: { id: string; revision: number } | null;
}) {
  const [selected, setSelected] = useState<string | null>(request?.id ?? null);
  useEffect(() => { if (request) setSelected(request.id); }, [request?.revision]); // eslint-disable-line react-hooks/exhaustive-deps
  const [lengths, setLengths] = useState<Record<string, { right: number; left: number }>>({});
  useEffect(() => {
    host.showLandmarks(file); setLengths(host.measureLengths());
    const off = host.onRigPoseChange?.(() => setLengths(host.measureLengths()));
    return () => { off?.(); host.showLandmarks(null); };
  }, [host, file]);
  useEffect(() => { host.selectLandmark(selected); }, [host, selected]);
  const marks = file.landmarks ?? [];
  const pick = (m: Landmark) => { const id = landmarkId(m); setSelected(selected === id ? null : id); const bone = m.bone && rows.get(m.bone); if (bone && selected !== id) onSelectStructure(bone.sourceKey, bone.side); };
  const cm = (v?: number) => v === undefined ? '–' : `${(v * 100).toFixed(1)}cm`;
  return <section className="acupoint-detail landmark-view" aria-label="기준점">
    <p className="quiet-note">진단학 실습에서 좌우를 비교하는 뼈 기준점입니다(모형 위 보라색 점). 누르면 그 뼈를 고르고 점을 크게 표시합니다.</p>
    {LANDMARK_GROUPS.map(group => <div key={group.name} className="landmark-group"><h5>{group.name}</h5>
      <ul>{group.ids.map(id => { const sides = marks.filter(m => m.id === id); if (!sides.length) return null;
        return <li key={id}><span>{sides[0].nameKo}</span>{sides.map(m => <button key={m.side} aria-pressed={selected === landmarkId(m)} onClick={() => pick(m)}>
          {m.side === 'right' ? '오른쪽' : m.side === 'left' ? '왼쪽' : '보기'}</button>)}</li>; })}</ul></div>)}
    {(file.measures?.length ?? 0) > 0 && <><h5>좌우 비교 거리</h5>
      <table className="measure-table"><thead><tr><th>두 점</th><th>오른쪽</th><th>왼쪽</th><th>짧은 쪽</th></tr></thead><tbody>
        {file.measures!.map(m => { const l = lengths[m.id], diff = l ? l.right - l.left : 0;
          return <tr key={m.id}><td>{m.nameKo}<small>{m.reads}</small></td><td>{cm(l?.right)}</td><td>{cm(l?.left)}</td>
            <td>{!l || Math.abs(diff) < .002 ? '같음' : `${diff < 0 ? '오른쪽' : '왼쪽'} ${(Math.abs(diff) * 1000).toFixed(0)}mm`}</td></tr>; })}
      </tbody></table>
      <p className="quiet-note">모형이 좌우 대칭이라 서 있는 자세에서는 같습니다. 관절 움직임에서 허리를 옆으로 굽히거나 돌리면 짧아지는 쪽이 숫자로 보입니다. 실제 촉진에서는 두 뼈 사이를 손으로 잡아 비교합니다.</p></>}
  </section>;
}
