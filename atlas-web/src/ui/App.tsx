import { useEffect, useMemo, useRef, useState } from 'react';
import { WholeBodyViewer } from '../viewer/wholeBody/WholeBodyViewer';
import { validateDataset, type Dataset } from '../viewer/datasets/schema';
import { validateRuntimeIntegration, searchStructures, readDatasetRoute, datasetRouteQuery, type RuntimeIntegration, type DatasetRoute, type RuntimeStructureRecord } from '../viewer/datasets/integration';
import { structureTextForLearner, motionActionOptionsForLearner } from '../data/learning';
import navigation from '../../../atlas-data/navigation/atlas-navigation.json';
import { AtlasLoading } from './AtlasLoading';
import './styles.css';
import './atlasShell.css';
const regionIds = navigation.categories.map(c => c.id);
function NameRows({ row }: {
    row: RuntimeStructureRecord;
}) {
    return <div className="names-card" aria-label="이름">{[['우리말명', row.names.koModern], ['한자어명 (한글 표기)', row.names.koTraditional], ['영어명', row.names.en]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || '이름 정리 중'}</strong></div>)}</div>;
}
/** One data-driven atlas: source observation remains usable independently of optional content bindings. */
export default function App() {
    const [data, setData] = useState<{
        dataset: Dataset;
        integration: RuntimeIntegration;
    } | null>(null);
    const [homeRevision, setHomeRevision] = useState(0);
    const [error, setError] = useState(false);
    const [entered, setEntered] = useState(false);
    const [route, setRoute] = useState<DatasetRoute>({ regions: [], selected: null });
    const [query, setQuery] = useState('');
    const [exploreOpen, setExploreOpen] = useState(false);
    const [detailsOpen, setDetailsOpen] = useState(true);
    const [tab, setTab] = useState<'구조' | '기능'>('구조');
    const [actionId, setActionId] = useState<string | null>(null);
    const info = useRef<HTMLDialogElement>(null);
    useEffect(() => {
        const abort = new AbortController();
        const timer = setTimeout(() => { abort.abort(); setError(true); }, 20000);
        void Promise.all(['/__atlas/datasets/human-atlas-local/manifest.json', '/__atlas/integration.json'].map(async (url) => { const response = await fetch(url, { signal: abort.signal }); if (!response.ok)
            throw Error('자료 연결 실패'); return response.json(); }))
            .then(([raw, overlay]) => { if (abort.signal.aborted)
            return; const dataset = validateDataset(raw); const integration = validateRuntimeIntegration(overlay, dataset); setData({ dataset, integration }); setRoute(readDatasetRoute(location.search, integration.objects, regionIds)); })
            .catch(() => { if (!abort.signal.aborted)
            setError(true); }).finally(() => clearTimeout(timer));
        return () => { clearTimeout(timer); abort.abort(); };
    }, []);
    useEffect(() => { if (!data)
        return; const pop = () => { setRoute(readDatasetRoute(location.search, data.integration.objects, regionIds)); setDetailsOpen(true); }; window.addEventListener('popstate', pop); return () => window.removeEventListener('popstate', pop); }, [data]);
    const rows = useMemo(() => data ? searchStructures(data.integration.objects, query, route.regions) : [], [data, query, route.regions]);
    const selected = data?.integration.objects.find(r => r.sourceKey === route.selected);
    const actions = useMemo(() => selected?.haConceptId ? motionActionOptionsForLearner(selected.haConceptId).filter(a => !a.candidate || !selected.side || a.candidate.definition.side === selected.side) : [], [selected?.haConceptId, selected?.side]);
    const action = actions.find(a => a.id === actionId) ?? actions[0];
    const title = route.regions.length ? navigation.categories.filter(c => route.regions.includes(c.id)).map(c => c.labelKo).join(' · ') : '전신 살펴보기';
    function navigate(next: DatasetRoute, keepExplore = false) {
        const query = datasetRouteQuery(next);
        const url = location.pathname + (query ? '?' + query : '');
        if (url !== location.pathname + location.search)
            history.pushState(null, '', url);
        setRoute(next);
        setDetailsOpen(true);
        setTab('구조');
        setActionId(null);
        if (!keepExplore)
            setExploreOpen(false);
    }
    function toggleRegion(id: string) {
        const regions = route.regions.includes(id) ? route.regions.filter(r => r !== id) : [...route.regions, id];
        setQuery('');
        navigate({ regions, selected: selected && (!regions.length || selected.regionIds.some(r => regions.includes(r))) ? selected.sourceKey : null }, true);
    }
    function select(id: string) {
        const row = data?.integration.objects.find(r => r.sourceKey === id && r.inspectionEligible && r.localDisplayEligible);
        if (!row)
            return;
        // Search can reach outside a regional filter; whole-body selection never narrows the user's scene.
        const regions = route.regions.length && !row.regionIds.some(r => route.regions.includes(r)) ? [] : route.regions;
        navigate({ regions, selected: id });
    }
    if (error)
        return <AtlasLoading failed onRetry={() => location.reload()}/>;
    if (!data)
        return <AtlasLoading />;
    return <div className="study-shell atlas-shell">
  <a className="skip-link" inert={!entered} href={selected ? '#study-details' : '#atlas-stage'}>{selected ? '선택한 구조 설명으로 이동' : '모형으로 이동'}</a>
  <header className="study-header" inert={!entered}>
   <div className="header-brand-group"><button className="brand" aria-label="Human Atlas 전신 홈" onClick={() => { setQuery(''); navigate({ regions: [], selected: null }); setHomeRevision(v => v + 1); }}><span className="brand-dot"/> HUMAN ATLAS</button><button className="app-info-trigger" onClick={() => info.current?.showModal()}>앱 정보</button></div>
   <button className="explore-trigger" aria-expanded={exploreOpen} aria-controls="atlas-explorer" onClick={() => setExploreOpen(!exploreOpen)}>부위 탐색</button>
   <label className="global-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="구조 검색" placeholder="근육·뼈 이름 검색" autoComplete="off" value={query} onChange={e => { setQuery(e.target.value); setExploreOpen(true); }}/>{query && <button aria-label="검색 지우기" onClick={() => setQuery('')}>×</button>}</label>
  </header>
  <dialog className="app-info-dialog" ref={info} aria-labelledby="app-info-title"><div className="app-info-content"><button className="app-info-close" aria-label="앱 정보 닫기" onClick={() => info.current?.close()}>닫기</button><h2 id="app-info-title">모형·자료 정보</h2>
   <p>Z-Anatomy — The libre 3D atlas of anatomy — CC BY-SA 4.0</p><p>BodyParts3D — The Database Center for Life Science — CC BY-SA 2.1 Japan</p><p>고정한 Z-Anatomy 모형을 웹용으로 변환하고 상세 단계를 조정했습니다. 로컬 학습용 시제품이며 일부 구조와 이름·설명은 준비 중입니다. 원본의 별도 출처와 이용 조건을 보존하며 공개 재배포는 보류합니다.</p>
   <a href="https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/c7010a903b75a2fd24a13b1c2c4c3546a9223780/Readme.md" target="_blank" rel="noreferrer">원본·제작자·이용 조건 ↗</a>
  </div></dialog>
  <div className="study-layout">
   <aside id="atlas-explorer" inert={!entered} data-searching={Boolean(query.trim())} className={`study-sidebar ${exploreOpen ? 'is-open' : ''}`} aria-label="부위 탐색" onKeyDown={e => { if (e.key === 'Escape') {
        setExploreOpen(false);
        document.querySelector<HTMLElement>('.explore-trigger')?.focus();
    } }}>
    <button className="explore-close" onClick={() => setExploreOpen(false)}>탐색 닫기</button><div className="sidebar-heading"><span className="eyebrow">EXPLORE ANATOMY</span><h1>부위 탐색</h1><p>어디부터 살펴볼까요?</p></div>
    <button className="region-all-toggle" aria-pressed={!route.regions.length} onClick={() => { setQuery(''); navigate({ regions: [], selected: route.selected }, true); }}>전신</button>
    <nav className="region-grid" aria-label="12개 해부학 부위">{navigation.categories.map(c => <button key={c.id} aria-pressed={route.regions.includes(c.id)} className={route.regions.includes(c.id) ? 'is-current' : ''} onClick={() => toggleRegion(c.id)}>{c.labelKo}</button>)}</nav>
    <div className="region-list-heading"><span className="eyebrow">{query.trim() ? 'SEARCH RESULTS' : 'STRUCTURES'}</span><h2>{query.trim() ? '검색 결과' : title}</h2><p className="result-count" role="status">{rows.length}개 이름 · 좌우 모형 함께 보기</p></div>
    <nav className="study-list region-structure-list" aria-label="구조 목록">{rows.map(r => { const sameSearchConcept = selected && (selected.searchGroupKey ?? selected.sourceKey) === (r.searchGroupKey ?? r.sourceKey); return <button key={r.sourceKey} className={sameSearchConcept ? 'selected' : ''} aria-pressed={Boolean(sameSearchConcept)} onClick={() => select(r.sourceKey)}><span>{r.label}</span>{r.label !== r.names.en && <small>{r.names.en}</small>}{r.searchApproximate && <em>비슷한 이름</em>}</button>; })}{!rows.length && <p className="quiet-note">등록된 이름을 찾지 못했습니다. 다른 이름으로 검색해 보세요.</p>}</nav>
   </aside>
   <section id="atlas-stage" tabIndex={-1} className="study-stage" aria-label={`${title} 학습 장면`}><div className="stage-caption" aria-hidden={!entered}><span className="eyebrow">INTERACTIVE ANATOMY</span><h2>{title}</h2><p>회전하고 확대하며 구조를 살펴보세요.</p></div>
    <WholeBodyViewer homeRevision={homeRevision} datasetSource={data} onEntered={setEntered} regionIds={route.regions} selectedId={route.selected} selectedIds={route.selected ? [route.selected] : []} whole={!route.regions.length} onWholeChange={() => navigate({ regions: [], selected: route.selected })} onSelect={select}/>
   </section>
   {selected && <details inert={!entered} className="study-details" id="study-details" open={detailsOpen} onToggle={e => setDetailsOpen(e.currentTarget.open)}><summary className="mobile-detail-summary">{selected.label}</summary><div className="study-detail-content">
    <button className="bone-related-muscle" onClick={() => navigate({ ...route, selected: null })}>선택 해제</button><h2>{selected.label}</h2><NameRows row={selected}/>
    <div className="names-card"><div><span>{selected.kind === 'bone' ? '뼈' : '근육'}</span><strong>{selected.side === 'left' ? '왼쪽' : selected.side === 'right' ? '오른쪽' : '좌우 구분 없음'}</strong></div></div>
    <div className="part-pills" aria-label="좌우 모형">{data.integration.objects.filter(r => r.localDisplayEligible && r.names.en === selected.names.en && r.side).map(r => <button key={r.sourceKey} aria-pressed={r.sourceKey === selected.sourceKey} onClick={() => select(r.sourceKey)}>{r.side === 'left' ? '왼쪽' : '오른쪽'}</button>)}</div>
    {selected.kind === 'muscle' ? <><div className="movement-cta-block"><button className="movement-cta" disabled aria-describedby="movement-unavailable-note">움직임으로 이해하기</button><p id="movement-unavailable-note" className="quiet-note">움직임 시범 자료는 준비 중입니다.</p></div>
    <div className="study-tabs" role="tablist" aria-label="학습 내용">{(['구조', '기능'] as const).map(t => <button key={t} role="tab" id={`tab-${t}`} aria-controls="study-tab-panel" aria-selected={tab === t} tabIndex={tab === t ? 0 : -1} onClick={() => setTab(t)} onKeyDown={e => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
                e.preventDefault();
                const next = e.key === 'Home' ? '구조' : e.key === 'End' ? '기능' : tab === '구조' ? '기능' : '구조';
                setTab(next);
                document.getElementById(`tab-${next}`)?.focus();
            } }}>{t}</button>)}</div>
    <section id="study-tab-panel" role="tabpanel" aria-labelledby={`tab-${tab}`}>{tab === '구조' ? (['origin', 'insertion'] as const).map(role => <section className="attachment-section attachment-summary-block" key={role}><h3><i className={role}/>{role === 'origin' ? '기시' : '정지'}<span>{role === 'origin' ? 'ORIGIN' : 'INSERTION'}</span></h3><p>{selected.haConceptId && structureTextForLearner(selected.haConceptId, role) || '설명 자료는 준비하고 있습니다.'}</p></section>) : action ? <div className="muscle-action-learning"><h3>이 근육이 하는 일</h3><p>{action.text.label}</p><p>{action.text.explanation}</p><fieldset className="learner-action-picker"><legend>작용 선택</legend>{actions.map(a => <button key={a.id} aria-pressed={action.id === a.id} onClick={() => setActionId(a.id)}>{a.label}</button>)}</fieldset></div> : <p className="quiet-note">작용 정보를 준비하고 있습니다.</p>}</section>
    </> : <section className="attachment-section"><h3>관련 근육</h3>{selected.relatedMuscles?.length ? <ul>{selected.relatedMuscles.map(r => <li key={r.sourceKey}><button className="bone-related-muscle" onClick={() => select(r.sourceKey)}>{r.label}</button><span>{r.roles.map(role => role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '부착').join(' · ')}</span></li>)}</ul> : <p className="quiet-note">주요 표지와 관련 근육 설명을 준비하고 있습니다.</p>}</section>}
   </div></details>}
  </div>
 </div>;
}
