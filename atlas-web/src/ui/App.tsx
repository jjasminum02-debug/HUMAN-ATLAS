import { useEffect, useMemo, useRef, useState } from 'react';
import { WholeBodyViewer } from '../viewer/wholeBody/WholeBodyViewer';
import { validateDataset, type Dataset } from '../viewer/datasets/schema';
import { validateRuntimeIntegration, searchStructures, readDatasetRoute, datasetRouteQuery, type RuntimeIntegration, type DatasetRoute, type RuntimeStructureRecord } from '../viewer/datasets/integration';
import { structureTextForLearner, structureTextForSource, structureUnavailabilityForLearner, motionActionOptionsForLearner, nerveLearningForLearner, nerveConceptsForLearner, nerveConceptForLearner, nerveConceptForSourceName, nerveNamesForSource, motorRelationsForSource, motorRelationsForNerve } from '../data/learning';
import navigation from '../../../atlas-data/navigation/atlas-navigation.json';
import { learnerFunctionUnavailableText } from '../domain/learnerActionText';
import { AtlasLoading } from './AtlasLoading';
import { anatomicalPartSubtitle } from '../domain/displayNames';
import { attachmentBoneKeys, inRegionalRoute } from '../viewer/datasets/regionalContext';
import { MotionLearningPanel } from './MotionLearningPanel';
import type { LearnerMotionActionOption } from '../domain/motionLearning';
import type { SourceMotionHost } from '../viewer/datasets/sourceMotionHost';
import { motionActionLabel, motionLearningIntent, preferredMotionAction, buildMotionActionLibrary } from '../domain/atlasMotionExperience';
import { isNerveRelatedActionTextIntent } from '../domain/nerveRelations';
import './styles.css';
import './atlasShell.css';
const regionIds = navigation.categories.map(c => c.id);
function routeAudienceFor(search: string): 'learner' | 'inspection' {
    return import.meta.env.DEV && new URLSearchParams(search).get('view') === 'source-observation' ? 'inspection' : 'learner';
}
function resolveRoute(search: string, rows: RuntimeStructureRecord[]): DatasetRoute {
    return readDatasetRoute(search, rows, regionIds, routeAudienceFor(search));
}
function NameRows({ row }: {
    row: RuntimeStructureRecord;
}) {
    const nerveNames = row.kind === 'nerve' ? nerveNamesForSource(row.names.en) : null;
    const names = nerveNames ? { koModern: nerveNames.koModern, koTraditional: nerveNames.koTraditional, en: nerveNames.en }
        : row.names;
    return <div className="names-card" aria-label="이름">{[['우리말명', names.koModern], ['한자어명 (한글 표기)', names.koTraditional], ['영어명', names.en]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || '이름 정리 중'}</strong></div>)}</div>;
}
function learnerRowTitle(row: RuntimeStructureRecord) {
    return row.kind === 'nerve' ? nerveNamesForSource(row.names.en)?.koModern ?? row.label : row.label;
}
function motionPanelOptions(actions: ReturnType<typeof motionActionOptionsForLearner>, sourceKey: string): LearnerMotionActionOption[] {
    return actions.map(action => ({
        id: action.id, label: action.label, subjectIds: [sourceKey], sideApplicability: action.sideApplicability,
        text: { label: action.text.label, explanation: action.text.explanation, postureConditions: [],
            stabilizationConditions: [], stabilizationNote: null, contextNotes: [], contractionNote: '', citations: [] },
        candidate: action.candidate ?? null, learningIntent: action.learningIntent,
    }));
}
/** One data-driven atlas: source observation remains usable independently of optional content bindings. */
export default function App() {
    const [data, setData] = useState<{
        dataset: Dataset;
        integration: RuntimeIntegration;
    } | null>(null);
    const [homeRevision, setHomeRevision] = useState(0);
    const [viewResetRevision, setViewResetRevision] = useState(0);
    const [error, setError] = useState(false);
    const [entered, setEntered] = useState(false);
    const [route, setRoute] = useState<DatasetRoute>({ regions: [], selected: null });
    const [textNerveKey, setTextNerveKey] = useState<string | null>(null);
    const [query, setQuery] = useState('');
    const [exploreOpen, setExploreOpen] = useState(false);
    const [regionMenuOpen, setRegionMenuOpen] = useState(false);
    const [detailsOpen, setDetailsOpen] = useState(true);
    const [tab, setTab] = useState<'구조' | '기능'>('구조');
    const [explorerMode, setExplorerMode] = useState<'structures' | 'actions'>('structures');
    const [actionId, setActionId] = useState<string | null>(null);
    const [motionHost, setMotionHost] = useState<SourceMotionHost | null>(null);
    const [muscleLayerEnabled, setMuscleLayerEnabled] = useState(true);
    const [boneLayerEnabled, setBoneLayerEnabled] = useState(true);
    const [selectedSourceHidden, setSelectedSourceHidden] = useState(false);
    const info = useRef<HTMLDialogElement>(null);
    const regionPicker = useRef<HTMLDivElement>(null);
    const regionPickerTrigger = useRef<HTMLButtonElement>(null);
    useEffect(() => {
        // Desktop has no collapse control; restore its card when leaving the
        // narrow layout after the learner has collapsed the mobile card.
        const desktop = window.matchMedia('(min-width: 761px)');
        const reopen = () => { if (desktop.matches) setDetailsOpen(true); };
        desktop.addEventListener('change', reopen);
        return () => desktop.removeEventListener('change', reopen);
    }, []);
    useEffect(() => {
        const abort = new AbortController();
        const timer = setTimeout(() => { abort.abort(); setError(true); }, 20000);
        void Promise.all(['/__atlas/datasets/human-atlas-local/manifest.json', '/__atlas/integration.json'].map(async (url) => { const response = await fetch(url, { signal: abort.signal }); if (!response.ok)
            throw Error('자료 연결 실패'); return response.json(); }))
            .then(([raw, overlay]) => { if (abort.signal.aborted)
            return; const dataset = validateDataset(raw); const integration = validateRuntimeIntegration(overlay, dataset); setData({ dataset, integration }); setRoute(resolveRoute(location.search, integration.objects)); setTextNerveKey(nerveConceptForLearner(new URLSearchParams(location.search).get('nerveConcept') ?? '')?.key ?? null); setQuery(history.state?.atlasSearchQuery ?? ''); })
            .catch(() => { if (!abort.signal.aborted)
            setError(true); }).finally(() => clearTimeout(timer));
        return () => { clearTimeout(timer); abort.abort(); };
    }, []);
    useEffect(() => { if (!data)
        return; const pop = () => { setRoute(resolveRoute(location.search, data.integration.objects)); setTextNerveKey(nerveConceptForLearner(new URLSearchParams(location.search).get('nerveConcept') ?? '')?.key ?? null); setQuery(history.state?.atlasSearchQuery ?? ''); setDetailsOpen(true); setTab('구조'); setActionId(null); setRegionMenuOpen(false); }; window.addEventListener('popstate', pop); return () => window.removeEventListener('popstate', pop); }, [data]);
    useEffect(() => {
        if (!regionMenuOpen) return;
        const closeOutside = (event: PointerEvent) => {
            if (!regionPicker.current?.contains(event.target as Node)) setRegionMenuOpen(false);
        };
        document.addEventListener('pointerdown', closeOutside);
        return () => document.removeEventListener('pointerdown', closeOutside);
    }, [regionMenuOpen]);
    const rows = useMemo(() => data ? searchStructures(data.integration.objects, query, route.regions, route.audience ?? 'learner')
        .filter(row => !query.trim() || row.kind !== 'nerve' || !nerveConceptForSourceName(row.names.en)) : [], [data, query, route.regions, route.audience]);
    const nerveSearchResults = useMemo(() => query.trim() && route.audience !== 'inspection'
        ? nerveConceptsForLearner(query).map(match => ({ ...match, nativeRows: match.concept.sourceNativeEnglishName
            ? (data?.integration.objects ?? []).filter(row => row.kind === 'nerve' && row.names.en === match.concept.sourceNativeEnglishName
                && row.localDisplayEligible && row.inspectionEligible && row.routeAudience === 'learner')
            : [] })) : [], [data, query, route.audience]);
    const selected = data?.integration.objects.find(r => r.sourceKey === route.selected);
    const selectedTextNerve = textNerveKey ? nerveConceptForLearner(textNerveKey) : null;
    const runtimeObjects = data?.integration.objects ?? [];
    const selectedNerveConcept = selected?.kind === 'nerve' ? nerveConceptForSourceName(selected.names.en) : null;
    const relatedMuscles = useMemo(() => {
        const result = new Map((selected?.relatedMuscles ?? []).map(row => [row.sourceKey, { ...row, roles: [...row.roles] }]));
        if (selected?.kind === 'bone') for (const muscle of data?.integration.objects ?? []) {
            const roles = (['origin', 'insertion'] as const).filter(role => attachmentBoneKeys(muscle.sourceKey, role).includes(selected.sourceKey));
            if (!roles.length) continue;
            const previous = result.get(muscle.sourceKey);
            result.set(muscle.sourceKey, { sourceKey: muscle.sourceKey, label: muscle.label, roles: [...new Set([...previous?.roles ?? [], ...roles])] });
        }
        return [...result.values()];
    }, [selected, data]);
    const actions = useMemo(() => (selected?.kind === 'muscle' || selected?.kind === 'bone')
        ? motionActionOptionsForLearner(selected.haConceptId, selected.side, selected.sourceKey) : [],
        [selected?.kind, selected?.haConceptId, selected?.side, selected?.sourceKey]);
    const motionActions = useMemo(() => (selected?.kind === 'muscle' || selected?.kind === 'bone') ? motionPanelOptions(actions, selected.sourceKey) : [], [actions, selected?.kind, selected?.sourceKey]);
    // Build once from the whole supported set, rather than choosing an initial muscle shortlist.
    const actionLibrary = useMemo(() => buildMotionActionLibrary((data?.integration.objects ?? [])
        .filter(row => row.kind === 'muscle' && row.localDisplayEligible && row.inspectionEligible && row.routeAudience === 'learner')
        .flatMap(row => motionPanelOptions(motionActionOptionsForLearner(row.haConceptId, row.side, row.sourceKey), row.sourceKey)
            .map(action => ({ sourceKey: row.sourceKey, name: learnerRowTitle(row), side: row.side, regionIds: row.regionIds, action })))), [data]);
    const visibleActionLibrary = useMemo(() => actionLibrary.map(entry => ({ ...entry,
        subjects: entry.subjects.filter(subject => (!route.regions.length || subject.regionIds.some(id => route.regions.includes(id)))
          && (!query.trim() || `${entry.label} ${subject.name}`.includes(query.trim()))) })).filter(entry => entry.subjects.length),
        [actionLibrary, route.regions, query]);
    const postureActions = actions.filter(a => motionLearningIntent(a) === 'posture_observation');
    const functionActions = actions.filter(a => motionLearningIntent(a) !== 'posture_observation');
    const action = actions.find(a => a.id === actionId) ?? preferredMotionAction(functionActions);
    const regionLabel = route.regions.length === 0 ? '전신'
        : route.regions.length === 1 ? navigation.categories.find(c => c.id === route.regions[0])?.labelKo ?? '선택한 부위'
        : `${route.regions.length}개 부위`;
    const nerveLearning = selected?.kind === 'nerve' ? nerveLearningForLearner(selected.names.en) : null;
    const textNerveLearning = selectedTextNerve ? nerveLearningForLearner(selectedTextNerve.sourceNativeEnglishName ?? selectedTextNerve.names.en) : null;
    const selectedNerveRelations = selectedNerveConcept ? motorRelationsForNerve(selectedNerveConcept.key, selected?.side) : [];
    const selectedTextNerveRelations = selectedTextNerve ? motorRelationsForNerve(selectedTextNerve.key) : [];
    const selectedMuscleNerveRelations = selected?.kind === 'muscle' ? motorRelationsForSource(selected.sourceKey) : [];
    const title = route.regions.length ? navigation.categories.filter(c => route.regions.includes(c.id)).map(c => c.labelKo).join(' · ') : '전신 살펴보기';
    function navigate(next: DatasetRoute, keepExplore = false, searchQuery = query) {
        const nextRoute = route.audience === 'inspection' ? { ...next, audience: 'inspection' as const } : next;
        const routeQuery = datasetRouteQuery(nextRoute);
        const url = location.pathname + (routeQuery ? '?' + routeQuery : '');
        if (url !== location.pathname + location.search)
            history.pushState({ atlasSearchQuery: searchQuery }, '', url);
        else history.replaceState({ ...history.state, atlasSearchQuery: searchQuery }, '', url);
        setTextNerveKey(null);
        setRoute(nextRoute);
        setRegionMenuOpen(false);
        setDetailsOpen(true);
        setTab('구조');
        setActionId(null);
        if (!keepExplore)
            setExploreOpen(false);
    }
    function updateQuery(value: string) {
        setQuery(value);
        // Retain the search that led to a selected history entry. A new search is saved
        // on the next navigation, so Back restores the previous card and its search.
        if (!route.selected) history.replaceState({ ...history.state, atlasSearchQuery: value }, '', location.href);
    }
    function resetPresentation() { setViewResetRevision(value => value + 1); }
    function toggleRegion(id: string, combine = false) {
        const regions = combine ? route.regions.includes(id) ? route.regions.filter(r => r !== id) : [...route.regions, id] : [id];
        setQuery('');
        resetPresentation();
        navigate({ regions, selected: selected && inRegionalRoute(selected, data!.integration.objects, regions) ? selected.sourceKey : null }, true, '');
    }
    function chooseRegion(id: string | null, combine = false) {
        if (id) toggleRegion(id, combine);
        else {
            setQuery('');
            resetPresentation();
            navigate({ regions: [], selected: route.selected }, true, '');
        }
        setRegionMenuOpen(false);
        requestAnimationFrame(() => regionPickerTrigger.current?.focus());
    }
    function select(id: string) {
        const row = data?.integration.objects.find(r => r.sourceKey === id && r.inspectionEligible && r.localDisplayEligible
            && r.routeAudience === (route.audience ?? 'learner'));
        if (!row)
            return;
        // Search can reach outside a regional filter; whole-body selection never narrows the user's scene.
        const regions = inRegionalRoute(row, data!.integration.objects, route.regions) ? route.regions : [];
        navigate({ regions, selected: id });
    }
    function selectMuscleAction(sourceKey: string, selectedActionId: string) {
        const row = data?.integration.objects.find(r => r.sourceKey === sourceKey && r.kind === 'muscle'
            && r.inspectionEligible && r.localDisplayEligible && r.routeAudience === (route.audience ?? 'learner'));
        const exactAction = row && motionActionOptionsForLearner(row.haConceptId, row.side, row.sourceKey)
            .some(option => option.id === selectedActionId);
        if (!row || !exactAction) return;
        const regions = inRegionalRoute(row, data!.integration.objects, route.regions) ? route.regions : [];
        navigate({ regions, selected: sourceKey });
        // This is an explicit action link; it intentionally wins over navigate's normal structure default.
        setActionId(selectedActionId);
        setTab('기능');
    }
    function selectTextNerve(key: string) {
        if (!nerveConceptForLearner(key)) return;
        const nextRoute = route.audience === 'inspection' ? { regions: [], selected: null, audience: 'inspection' as const }
            : { regions: [], selected: null };
        const base = datasetRouteQuery(nextRoute);
        const params = new URLSearchParams(base);
        params.set('nerveConcept', key);
        const nextSearch = `?${params.toString()}`;
        const url = location.pathname + nextSearch;
        if (url !== location.pathname + location.search) history.pushState({ atlasSearchQuery: query }, '', url);
        else history.replaceState({ ...history.state, atlasSearchQuery: query }, '', url);
        setRoute(nextRoute);
        setTextNerveKey(key);
        setDetailsOpen(true);
        setTab('구조');
        setActionId(null);
        setExploreOpen(false);
    }
    function openNerveConcept(key: string, preferredSide?: string | null) {
        const concept = nerveConceptForLearner(key);
        if (!concept) return;
        const native = (data?.integration.objects ?? []).find(row => row.kind === 'nerve'
            && row.names.en === concept.sourceNativeEnglishName && row.localDisplayEligible && row.inspectionEligible
            && row.routeAudience === (route.audience ?? 'learner')
            && (!preferredSide || row.side === preferredSide));
        if (native) select(native.sourceKey);
        else selectTextNerve(key);
    }
    function nerveFunctionStatus(concept: NonNullable<typeof selectedNerveConcept>) {
        switch (concept.functionEvidenceClass) {
            case 'mixed_motor_sensory_evidence_and_motor_relation':
                return '문헌에서 운동 가지와 감각 가지가 모두 기술됩니다. 아래는 확인된 운동근 관계입니다.';
            case 'sensory_course_documented_no_motor_relation':
                return '확인된 자료는 피부 감각 주행을 설명합니다. 현재 연결된 운동근 관계는 없습니다.';
            case 'motor_relation_documented_sensory_class_not_assessed':
                return '문헌에서 아래 운동근 관계가 확인되었습니다. 이 관계만으로 신경의 감각 기능까지 분류하지 않습니다.';
            default:
                return '현재 학습 자료에는 연결된 운동근 관계가 없습니다. 이는 해부학적 지배가 없다는 뜻이 아닙니다.';
        }
    }
    function renderNerveRelations(relations: ReturnType<typeof motorRelationsForNerve>, selectedSide: string | null | undefined) {
        const relationItems = relations.map(relation => {
            const targets = relation.targetSourceKeys.map(key => runtimeObjects.find(row => row.sourceKey === key))
                .filter((row): row is RuntimeStructureRecord => Boolean(row && row.kind === 'muscle' && row.localDisplayEligible && row.inspectionEligible
                    && row.routeAudience === (route.audience ?? 'learner') && (!selectedSide || row.side === selectedSide)));
            if (!targets.length) return null;
            return <li key={relation.relationId}>
                <p>{relation.displayNote}</p>
                {targets.map(row => {
                    const actionsForTarget = motionActionOptionsForLearner(row.haConceptId, row.side, row.sourceKey)
                        .filter(option => isNerveRelatedActionTextIntent(option.learningIntent));
                    return <div className="nerve-related-muscle" key={row.sourceKey}>
                        <button className="bone-related-muscle" onClick={() => select(row.sourceKey)}>
                            {learnerRowTitle(row)} · {row.side === 'left' ? '왼쪽' : row.side === 'right' ? '오른쪽' : '좌우 구분 없음'}
                        </button>
                        <div className="nerve-related-actions" aria-label={`${learnerRowTitle(row)}의 작용 설명`}>
                            <span>관련 작용</span>
                            {actionsForTarget.length > 0 ? actionsForTarget.map(option => <div key={option.id}>
                                <p><strong>{motionActionLabel(option.label)}</strong> · {option.text.explanation}</p>
                                <button className="bone-related-muscle" onClick={() => {
                                    selectMuscleAction(row.sourceKey, option.id);
                                }}>{option.learningIntent === 'muscle_action' ? '이 근육의 움직임 보기' : '이 근육의 작용 설명 보기'}</button>
                            </div>) : <p className="quiet-note">현재 연결된 작용 설명이 없습니다.</p>}
                        </div>
                    </div>;
                })}
            </li>;
        }).filter(Boolean);
        return relationItems.length ? <ul>{relationItems}</ul> : <p className="quiet-note">현재 학습 자료에는 연결된 운동근 관계가 없습니다. 이는 해부학적 지배가 없다는 뜻이 아닙니다.</p>;
    }
    if (error)
        return <AtlasLoading failed onRetry={() => location.reload()}/>;
    if (!data)
        return <AtlasLoading />;
    return <div className="study-shell atlas-shell">
  <a className="skip-link" inert={!entered} href={selected || selectedTextNerve ? '#study-details' : '#atlas-stage'}>{selected || selectedTextNerve ? '선택한 구조 설명으로 이동' : '모형으로 이동'}</a>
  <header className="study-header" inert={!entered}>
   <div className="header-brand-group"><button className="brand" aria-label="Human Atlas 전신 홈" onClick={() => { setQuery(''); resetPresentation(); navigate({ regions: [], selected: null }, false, ''); setHomeRevision(v => v + 1); }}><span className="brand-dot"/> HUMAN ATLAS</button></div>
   <button className="explore-trigger" aria-expanded={exploreOpen} aria-controls="atlas-explorer" onClick={() => setExploreOpen(!exploreOpen)}>부위 탐색 · {regionLabel} ▾</button>
   <label className="global-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="구조 검색" placeholder={explorerMode === "actions" ? "움직임·근육 이름 검색" : "근육·뼈·신경 이름 검색"} autoComplete="off" value={query} onChange={e => { updateQuery(e.target.value); setExploreOpen(true); }}/>{query && <button aria-label="검색 지우기" onClick={() => updateQuery('')}>×</button>}</label>
  </header>
  <button inert={!entered} className="app-info-trigger" onClick={() => info.current?.showModal()}>앱 정보</button>
  <dialog className="app-info-dialog" ref={info} aria-labelledby="app-info-title"><div className="app-info-content"><button className="app-info-close" aria-label="앱 정보 닫기" onClick={() => info.current?.close()}>닫기</button><h2 id="app-info-title">모형·자료 정보</h2>
   <p>Z-Anatomy — The libre 3D atlas of anatomy — CC BY-SA 4.0</p><p>BodyParts3D — The Database Center for Life Science — CC BY-SA 2.1 Japan</p><p>고정한 Z-Anatomy 모형을 웹용으로 변환하고 상세 단계를 조정했습니다. 로컬 학습용 시제품이며 일부 구조와 이름·설명은 준비 중입니다. 원본의 별도 출처와 이용 조건을 보존하며 공개 재배포는 보류합니다.</p>
   <a href="https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/c7010a903b75a2fd24a13b1c2c4c3546a9223780/Readme.md" target="_blank" rel="noreferrer">원본·제작자·이용 조건 ↗</a>
   <p>근육 부착 설명은 NCBI Bookshelf의 StatPearls 해부학 자료를 대조한 한국어 요약입니다. 자세한 기시·정지 범위에는 개인차가 있습니다.</p><a href="https://www.ncbi.nlm.nih.gov/books/NBK459392/" target="_blank" rel="noreferrer">해부학 설명 참고 자료 ↗</a>
  </div></dialog>
  <div className="study-layout">
   <aside id="atlas-explorer" inert={!entered} data-searching={Boolean(query.trim())} className={`study-sidebar ${exploreOpen ? 'is-open' : ''}`} aria-label="부위 탐색" onKeyDown={e => { if (e.key === 'Escape') {
        if (regionMenuOpen) { setRegionMenuOpen(false); regionPickerTrigger.current?.focus(); }
        else { setExploreOpen(false); document.querySelector<HTMLElement>('.explore-trigger')?.focus(); }
    } }}>
    <button className="explore-close" onClick={() => setExploreOpen(false)}>탐색 닫기</button>
    <div className="region-picker" ref={regionPicker}>
      <button ref={regionPickerTrigger} type="button" className="region-picker-trigger" aria-expanded={regionMenuOpen}
        aria-controls="atlas-region-menu" onClick={() => setRegionMenuOpen(open => !open)}>
        부위 탐색 · {regionLabel} <span aria-hidden="true">▾</span>
      </button>
      {regionMenuOpen && <div id="atlas-region-menu" className="region-picker-menu" aria-label="전신 및 12개 부위">
        <button type="button" aria-pressed={!route.regions.length} onClick={() => chooseRegion(null)}>전신</button>
        {navigation.categories.map(c => <button type="button" key={c.id} aria-pressed={route.regions.includes(c.id)}
          onClick={event => chooseRegion(c.id, event.shiftKey)}>{c.labelKo}</button>)}
        <p className="region-combine-hint">한 부위씩 보기 · Shift + 부위 선택으로 함께 보기</p>
      </div>}
    </div>
    <div className="explorer-mode" role="group" aria-label="탐색 방법"><button aria-pressed={explorerMode === 'structures'} onClick={() => setExplorerMode('structures')}>구조 찾기</button><button aria-pressed={explorerMode === 'actions'} onClick={() => { setExplorerMode('actions'); updateQuery(''); }}>근육 작용 찾기</button></div>

    {explorerMode === 'actions' ? <>
      <div className="region-list-heading"><span className="eyebrow">MUSCLE ACTIONS</span><h2>근육 작용 찾기</h2><p className="result-count">{visibleActionLibrary.length}개 동작 범주 · 글 설명/3D 시범 상태 표시</p></div>
      <section className="motion-library explorer-results-body" aria-label="근육 작용 목록">
        {visibleActionLibrary.map(entry => <details key={entry.label}><summary>{entry.label}</summary><div>{entry.subjects.map(subject => <button key={`${subject.sourceKey}:${subject.action.id}`} onClick={() => { selectMuscleAction(subject.sourceKey, subject.action.id); setQuery(''); }}><span>{subject.name}</span><small>{subject.side === 'left' ? '왼쪽' : subject.side === 'right' ? '오른쪽' : ''}</small></button>)}</div></details>)}
        {!visibleActionLibrary.length && <p className="quiet-note">이 범위의 근육 작용 시범은 준비 중입니다. 구조 찾기에서 모형과 설명을 볼 수 있습니다.</p>}
      </section>
    </> : <>
    <div className="region-list-heading"><span className="eyebrow">{query.trim() ? 'SEARCH RESULTS' : 'STRUCTURES'}</span><h2>{query.trim() ? '검색 결과' : title}</h2><p className="result-count" role="status">{rows.length + nerveSearchResults.reduce((n, row) => n + Math.max(1, row.nativeRows.length), 0)}개 이름 · 좌우 모형 함께 보기</p></div>
    <div className="explorer-results-body">
    <nav className="study-list region-structure-list" aria-label="구조 목록">{rows.map(r => { const sameSearchConcept = selected && (selected.searchGroupKey ?? selected.sourceKey) === (r.searchGroupKey ?? r.sourceKey); return <button key={r.sourceKey} className={sameSearchConcept ? 'selected' : ''} aria-pressed={Boolean(sameSearchConcept)} onClick={() => select(r.sourceKey)}><span>{learnerRowTitle(r)}</span>{learnerRowTitle(r) !== r.names.en && <small>{r.names.en}</small>}{r.searchApproximate && <em>비슷한 이름</em>}</button>; })}{!rows.length && !nerveSearchResults.length && <p className="quiet-note">등록된 이름을 찾지 못했습니다. 다른 이름으로 검색해 보세요.</p>}</nav>
    {nerveSearchResults.length > 0 && <section className="nerve-search-results" aria-label="신경 검색 결과"><h2>신경 설명</h2>
      {nerveSearchResults.map(({ concept, nativeRows, approximate }) => <div className="nerve-search-result" key={concept.key}>
        <strong>{concept.names.koModern}</strong><small>{concept.names.en}</small>
        {nativeRows.length ? <div>{nativeRows.map(row => <button key={row.sourceKey} onClick={() => select(row.sourceKey)}>{row.side === 'left' ? '왼쪽' : row.side === 'right' ? '오른쪽' : '선택'} 모형</button>)}</div>
          : <button onClick={() => selectTextNerve(concept.key)}>설명 보기</button>}
        {approximate && <em>비슷한 이름</em>}
      </div>)}
    </section>}</div></>}

   </aside>
   <section id="atlas-stage" tabIndex={-1} className="study-stage" aria-label={`${title} 학습 장면`}><div className="stage-caption" aria-hidden={!entered}><span className="eyebrow">INTERACTIVE ANATOMY</span><h2>{title}</h2><p>회전하고 확대하며 구조를 살펴보세요.</p></div>
    <WholeBodyViewer homeRevision={homeRevision} viewResetRevision={viewResetRevision} datasetSource={data} onEntered={setEntered} onMotionHostChange={setMotionHost} onMuscleLayerChange={setMuscleLayerEnabled} onBoneLayerChange={setBoneLayerEnabled} onSelectionHiddenChange={setSelectedSourceHidden} regionIds={route.regions} selectedId={route.selected} selectedIds={route.selected ? [route.selected] : []} whole={!route.regions.length} onWholeChange={() => { resetPresentation(); navigate({ regions: [], selected: route.selected }); }} onSelect={select}/>
   </section>
   {(selected || selectedTextNerve) && <details inert={!entered} className="study-details" id="study-details" open={detailsOpen} onToggle={e => setDetailsOpen(e.currentTarget.open)}><summary className="mobile-detail-summary">{selected ? learnerRowTitle(selected) : selectedTextNerve!.names.koModern}</summary><div className="study-detail-content">
    <button className="bone-related-muscle" onClick={() => navigate({ regions: [], selected: null })}>선택 해제</button><h2>{selected ? learnerRowTitle(selected) : selectedTextNerve!.names.koModern}</h2>{selected && anatomicalPartSubtitle(selected.names.en) && <p className="anatomical-part-subtitle">{anatomicalPartSubtitle(selected.names.en)}</p>}{selected ? <NameRows row={selected}/> : <div className="names-card" aria-label="이름"><div><span>우리말명</span><strong>{selectedTextNerve!.names.koModern}</strong></div><div><span>한자어명 (한글 표기)</span><strong>{selectedTextNerve!.names.koTraditional}</strong></div><div><span>영어명</span><strong>{selectedTextNerve!.names.en}</strong></div></div>}
    {selected?.names.en === 'Rotatores' && route.regions.length > 0 && !route.regions.includes('back') && <p className="quiet-note">선택한 돌림근 모형은 목에만 한정되지 않고 척추를 따라 이어지는 전체 묶음입니다.</p>}
    {selected && <><div className="names-card"><div><span>{selected.kind === 'bone' ? '뼈' : selected.kind === 'nerve' ? '신경' : '근육'}</span><strong>{selected.side === 'left' ? '왼쪽' : selected.side === 'right' ? '오른쪽' : '좌우 구분 없음'}</strong></div></div>
    <div className="part-pills" aria-label="좌우 모형">{data.integration.objects.filter(r => r.routeAudience === (route.audience ?? 'learner') && r.localDisplayEligible && r.inspectionEligible && r.names.en === selected.names.en && r.side).map(r => <button key={r.sourceKey} aria-pressed={r.sourceKey === selected.sourceKey} onClick={() => select(r.sourceKey)}>{r.side === 'left' ? '왼쪽' : '오른쪽'}</button>)}</div></>}
    {!selected && selectedTextNerve && <section className="attachment-section nerve-card text-nerve-card" aria-label="신경 개념 설명">
      <h3>신경 설명</h3>
      {selectedTextNerve.summary ? <>
        <section><h4>해부학적 주행</h4><p>{selectedTextNerve.summary.course}</p></section>
        <section><h4>운동 연결</h4><p>{selectedTextNerve.summary.motorRelation}</p></section>
        <section><h4>변이와 범위</h4><p>{selectedTextNerve.summary.variation}</p></section>
      </> : textNerveLearning ? <>
        <section><h4>정적 모형의 주행 맥락</h4><p>{textNerveLearning.courseContext}</p></section>
        <p className="quiet-note">개념 설명 화면입니다. 개별 좌우의 선택 가능한 신경 표면은 제공되지 않습니다.</p>
      </> : <p className="quiet-note">이 신경의 주행 설명 자료는 아직 연결되지 않았습니다.</p>}
      <h4>운동·감각 관계 상태</h4><p>{nerveFunctionStatus(selectedTextNerve)}</p>
      <h4>확인된 운동근 관계</h4>
      {renderNerveRelations(selectedTextNerveRelations, null)}
      <p className="quiet-note">선택 가능한 신경 모형이 없는 개념은 설명 카드로만 표시합니다.</p>
    </section>}
    {selected?.kind === 'nerve' ? <section className="attachment-section nerve-card" aria-label="신경 설명"><h3>신경 주행</h3>
      {nerveLearning && <section><h4>정적 모형에서 관찰하는 주행</h4><p>{nerveLearning.courseContext}</p></section>}
      <p className="quiet-note">표시된 주행은 정적 모형 관찰입니다. 움직임에 따른 신경 변형은 제공하지 않으며, 개인별 분지와 경로에는 차이가 있습니다.</p>
      <p className="nerve-legend"><span><i className="nerve-swatch"/>선택 신경</span><span><i className="motor-swatch"/>관련 근육</span></p>
      <h3>분지</h3>{selected.nerve!.branchKeys.length ? selected.nerve!.branchKeys.map(key => { const row = data.integration.objects.find(r => r.sourceKey === key); return row ? <button className="bone-related-muscle" key={key} onClick={() => select(key)}>{learnerRowTitle(row)}</button> : null; }) : <p className="quiet-note">표시할 하위 분지가 준비되지 않았습니다.</p>}
      <h3>운동·감각 관계 상태</h3><p>{selectedNerveConcept ? nerveFunctionStatus(selectedNerveConcept) : '이 모형 이름은 설명 개념과 아직 연결되지 않았습니다.'}</p>
      <h3>확인된 운동근 관계</h3>{renderNerveRelations(selectedNerveRelations, selected.side)}<p className="quiet-note">강조는 확인된 관계를 설명하기 위한 표시입니다. 실제 힘이나 활성도를 측정하지 않으며, 목록은 전체 지배 범위를 뜻하지 않습니다.</p>
      {nerveLearning && <details key={selected.sourceKey} className="nerve-learning-context"><summary>주행·포착 맥락</summary><section><h4>기능 연결</h4><p>{nerveLearning.functionContext}</p></section><section><h4>해부학적 주행과 변이</h4><p>{nerveLearning.courseContext}</p></section><section><h4>포착 가능 구간과 주변 조직</h4><p>{nerveLearning.compressionContext}</p></section>{"variationContext" in nerveLearning && <section><h4>변이와 자세 범위</h4><p>{String(nerveLearning.variationContext)}</p></section>}</details>}
    </section> : selected?.kind === 'muscle' ? <>
    <div className="study-tabs" role="tablist" aria-label="학습 내용">{(['구조', '기능'] as const).map(t => <button key={t} role="tab" id={`tab-${t}`} aria-controls={t === '구조' ? 'study-structure-panel' : 'study-function-panel'} aria-selected={tab === t} tabIndex={tab === t ? 0 : -1} onClick={() => setTab(t)} onKeyDown={e => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
                e.preventDefault();
                const next = e.key === 'Home' ? '구조' : e.key === 'End' ? '기능' : tab === '구조' ? '기능' : '구조';
                setTab(next);
                document.getElementById(`tab-${next}`)?.focus();
            } }}>{t}</button>)}</div>
    <div className="study-tab-panels">
    <section id="study-structure-panel" className="study-tab-panel" role="tabpanel" aria-labelledby="tab-구조" hidden={tab !== '구조'}>
      {(['origin', 'insertion'] as const).map(role => {
        const text = structureTextForSource(selected.sourceKey, role) || (selected.haConceptId && structureTextForLearner(selected.haConceptId, role));
        const bones = attachmentBoneKeys(selected.sourceKey, role).map(key => data.integration.objects.find(r => r.sourceKey === key)!).filter(Boolean);
        return <section className="attachment-section attachment-summary-block" key={role}>
          <h3><i className={role}/>{role === 'origin' ? '기시' : '정지'}<span>{role === 'origin' ? 'ORIGIN' : 'INSERTION'}</span></h3>
          <p>{text || structureUnavailabilityForLearner(role)}</p>
          {bones.length > 0 && <div className="attachment-bone-links" aria-label={`${role === 'origin' ? '기시' : '정지'} 관련 뼈`}>{bones.map(bone => <button key={bone.sourceKey} onClick={() => select(bone.sourceKey)}>{bone.label}</button>)}</div>}
        </section>;
      })}
      {attachmentBoneKeys(selected.sourceKey).length > 0 && <p className="quiet-note">주요 부착 부위를 요약했습니다. 관련 뼈는 전체 모형으로 함께 표시하며, 정확한 부착점 표시는 제공하지 않습니다.</p>}
      <section className="attachment-section attachment-summary-block">
        <h3>운동신경</h3>
        {selectedMuscleNerveRelations.length ? <ul>{selectedMuscleNerveRelations.map(relation => {
          const concept = nerveConceptForLearner(relation.nerveKey);
          return <li key={`${relation.nerveKey}:${relation.targetEnglishConcept}:${relation.targetSide}`}>
            <button className="bone-related-muscle" onClick={() => openNerveConcept(relation.nerveKey, relation.targetSide ?? selected.side)}>{concept?.names.koModern ?? '신경 설명'}</button>
            <p>{relation.displayNote}</p>
          </li>;
        })}</ul> : <p>{structureUnavailabilityForLearner('motorNerve')}</p>}
      </section>
      <section className="attachment-section attachment-summary-block">
        <h3>감각·고유감각</h3>
        <p>{structureUnavailabilityForLearner('sensoryProprioception')}</p>
      </section>
    </section>
    <section id="study-function-panel" className="study-tab-panel function-tab-panel" role="tabpanel" aria-labelledby="tab-기능" hidden={tab !== '기능'}>
      {functionActions.length > 0 && <fieldset className="learner-action-picker" aria-label="근육 작용 선택">
        <legend>근육 작용</legend>
        {functionActions.map(option => <button type="button" key={option.id} className="action-choice-row"
          aria-pressed={action?.id === option.id} onClick={() => setActionId(option.id)}>
          <span className="action-choice-heading"><strong>{motionActionLabel(option.label)}</strong><small>{option.candidate ? '3D 시범 연결' : '글 설명 제공'}</small></span>
          <span className="action-choice-description">{option.text.explanation || option.text.label}</span>
        </button>)}
      </fieldset>}
      {functionActions.length === 0 && <p className="quiet-note">{learnerFunctionUnavailableText()}</p>}
      <MotionLearningPanel active={tab === '기능'} subjectHidden={selectedSourceHidden} actions={motionActions}
        selectedActionId={action?.id ?? null} onSelectAction={setActionId} host={motionHost} sourceContextKey={selected.sourceKey}
        showActionPicker={false} muscleLayerEnabled={muscleLayerEnabled} boneLayerEnabled={boneLayerEnabled}/>
      {postureActions.length > 0 && <details className="posture-observation-disclosure">
        <summary>자세에서 관찰하기</summary>
        <p>근육 자체의 작용 시범이 아니라, 주변 구조가 움직일 때의 자세를 관찰합니다.</p>
        <div className="posture-observation-list">{postureActions.map(option => <button type="button" key={option.id}
          aria-pressed={action?.id === option.id} onClick={() => setActionId(option.id)}>
          <span className="action-choice-heading"><strong>{motionActionLabel(option.label)}</strong><small>자세 관찰 자료</small></span>
          <span className="action-choice-description">{option.text.explanation || option.text.label}</span>
        </button>)}</div>
      </details>}
    </section>
    </div>
    </> : selected?.kind === 'bone' ? <><MotionLearningPanel subjectHidden={selectedSourceHidden} actions={motionActions} selectedActionId={actionId ?? preferredMotionAction(motionActions)?.id ?? null} onSelectAction={setActionId} host={motionHost} sourceContextKey={selected.sourceKey} showActionPicker={true} muscleLayerEnabled={boneLayerEnabled} subjectKind="bone"/><section className="attachment-section"><h3>관련 근육</h3>{relatedMuscles.length ? <ul>{relatedMuscles.map(r => <li key={r.sourceKey}><button className="bone-related-muscle" onClick={() => select(r.sourceKey)}>{r.label}</button><span>{r.roles.map(role => role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '부착').join(' · ')}</span></li>)}</ul> : <p className="quiet-note">주요 표지와 관련 근육 설명을 준비하고 있습니다.</p>}</section></> : null}
   </div></details>}
  </div>
 </div>;
}
