import { useEffect, useMemo, useRef, useState } from 'react';
import { loadPilotCatalog, type PilotCatalog } from '../data/catalog';
import { findMuscles, learningConcepts, motionActionOptionsForLearner, nameFor, structureTextForLearner } from '../data/learning';
import { boneNameForLearner, searchSelectableBones } from '../data/boneNames';
import { WholeBodyViewer } from '../viewer/wholeBody/WholeBodyViewer';
import { buildBoneCardData } from '../domain/boneCard';
import {
  serializeAtlasRoute,
  type AtlasRouteState,
  type NavigationContract,
  type Selection,
  type SelectionReferences,
} from '../domain/navigation';
import {
  categoriesForMuscleConcept,
  categoryMemberships,
  defaultLearnerRoute,
  resolveLearnerRoute,
  routeForCategory,
  routeForBoneSelection,
  routeForMuscleSelection,
} from '../domain/regionNavigation';
import rawNavigation from '../../../atlas-data/navigation/atlas-navigation.json';
import './styles.css';

type TabName = '구조' | '기능';
type LearnerConcept = ReturnType<typeof learningConcepts>[number];
type UnmappedMeshNotice = { meshAssetId: string; sourceName: string };
type LearnerName = { label: string; koTraditional: string | null; koModern: string | null; en: string };
type SearchListItem =
  | { id: string; label: string; approximate: boolean; kind: 'muscle' }
  | { id: string; label: string; approximate: boolean; kind: 'bone'; selection: Extract<Selection, { kind: 'bone' }> };
const navigation = rawNavigation as NavigationContract;

function LearnerNameRows({ name }: { name: LearnerName }) {
  return <div className="names-card" aria-label="이름">
    <div><span>우리말명</span><strong>{name.koModern || '설명 정리 중'}</strong></div>
    <div><span>한자어명 (한글 표기)</span><strong>{name.koTraditional || '설명 정리 중'}</strong></div>
    <div><span>영어명</span><strong>{name.en || '설명 정리 중'}</strong></div>
  </div>;
}

function routeUrl(route: AtlasRouteState) {
  const query = serializeAtlasRoute(location.search, route);
  return `${location.pathname}${query ? `?${query}` : ''}${location.hash}`;
}

function routeEntityId(selection: Selection | null): string | null {
  if (!selection) return null;
  return selection.kind === 'muscle' ? selection.partId ?? selection.conceptId : selection.conceptId;
}

function muscleConceptId(concept: LearnerConcept | undefined, fallbackId: string): string {
  return concept?.entityType === 'muscle_part' && typeof concept.parentId === 'string'
    ? concept.parentId
    : fallbackId;
}

export default function App() {
  const [catalog, setCatalog] = useState<PilotCatalog | null>(null);
  const [error, setError] = useState('');
  const [route, setRoute] = useState<AtlasRouteState>(() => defaultLearnerRoute(navigation));
  const [routeReady, setRouteReady] = useState(false);
  const [wholeView, setWholeView] = useState(false);
  const [routeNotice, setRouteNotice] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [tab, setTab] = useState<TabName>('구조');
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [unmappedMeshNotice, setUnmappedMeshNotice] = useState<UnmappedMeshNotice | null>(null);
  const appInfoDialog = useRef<HTMLDialogElement>(null);
  const [detailsOpen, setDetailsOpen] = useState(() => typeof window === 'undefined' || window.matchMedia('(min-width: 761px)').matches);

  useEffect(() => {
    let active = true;
    loadPilotCatalog().then((loaded) => { if (active) setCatalog(loaded); })
      .catch((loadError: unknown) => { if (active) setError(String(loadError)); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const media = window.matchMedia('(min-width: 761px)');
    const sync = () => setDetailsOpen(media.matches);
    media.addEventListener('change', sync);
    return () => media.removeEventListener('change', sync);
  }, []);

  const concepts = useMemo(() => catalog ? learningConcepts(catalog) : [], [catalog]);
  const routeRefs = useMemo<SelectionReferences>(() => {
    const muscles = new Map<string, { entityType: string }>();
    const muscleParts = new Map<string, { parentId: string }>();
    const structures = new Map<string, { kind: string; parentId?: string }>();
    for (const concept of concepts) {
      if (concept.entityType === 'individual_muscle' || concept.entityType === 'muscle_group') {
        muscles.set(concept.id, { entityType: String(concept.entityType) });
      }
      if (concept.entityType === 'muscle_part' && typeof concept.parentId === 'string') {
        muscleParts.set(concept.id, { parentId: concept.parentId });
      }
    }
    for (const structure of catalog?.structures ?? []) {
      if (typeof structure.kind !== 'string') continue;
      structures.set(structure.id, { kind: structure.kind, ...(typeof structure.parentId === 'string' ? { parentId: structure.parentId } : {}) });
    }
    const structureInstances = new Map(navigation.structureInstances.map((row) => [row.id, { structureId: row.structureId, side: row.side }]));
    const structureMeshMappings = new Map(navigation.structureMeshMappings.map((row) => [row.id, { structureInstanceId: row.structureInstanceId, meshIds: row.meshIds }]));
    const meshAssets = new Map<string, { laterality?: string }>();
    for (const mapping of navigation.structureMeshMappings) {
      const instance = structureInstances.get(mapping.structureInstanceId);
      for (const meshId of mapping.meshIds) meshAssets.set(meshId, { laterality: instance?.side });
    }
    return {
      muscles,
      muscleInstances: new Map(),
      muscleParts,
      structures,
      structureInstances,
      meshAssets,
      muscleMeshMappings: new Map(),
      structureMeshMappings,
    };
  }, [catalog, concepts]);

  useEffect(() => {
    if (!catalog) return;
    const sync = () => {
      const resolved = resolveLearnerRoute(location.search, navigation, routeRefs);
      setRoute(resolved.route);
      setRouteReady(true);
      setRouteNotice(resolved.notice);
      setUnmappedMeshNotice(null);
      setTab('구조');
      setSelectedActionId(null);
      if (resolved.canonicalize) {
        const nextUrl = routeUrl(resolved.route);
        if (nextUrl !== `${location.pathname}${location.search}${location.hash}`) {
          history.replaceState(null, '', nextUrl);
        }
      }
    };
    sync();
    window.addEventListener('popstate', sync);
    return () => window.removeEventListener('popstate', sync);
  }, [catalog, routeRefs]);

  const region = navigation.categories.find((candidate) => candidate.id === route.regionId) ?? null;
  const selectedId = routeEntityId(route.selection);
  const selected = selectedId ? concepts.find((concept) => concept.id === selectedId) : undefined;
  const name = catalog && selectedId ? nameFor(catalog, selectedId) : null;
  const selectedBoneCard = catalog && route.selection?.kind === 'bone'
    ? buildBoneCardData(catalog, navigation, route.selection)
    : null;
  const selectedBoneName = selectedBoneCard ? boneNameForLearner(selectedBoneCard.conceptId) : null;
  const parentId = selected?.entityType === 'muscle_part' && typeof selected.parentId === 'string' ? selected.parentId : selectedId;
  const actionOptions = useMemo(() => selectedId && parentId ? motionActionOptionsForLearner(parentId) : [], [selectedId, parentId]);
  const activeAction = actionOptions.find((action) => action.id === selectedActionId) ?? actionOptions[0] ?? null;
  const actionCard = activeAction?.text ?? null;
  const parts = concepts.filter((concept) => concept.entityType === 'muscle_part' && concept.parentId === parentId);
  const regionRows = region ? categoryMemberships(navigation, region.id) : [];
  const regionMuscles = regionRows.flatMap((row) => {
    const concept = concepts.find((candidate) => candidate.id === row.entityId);
    return concept ? [concept] : [];
  });
  const searchResults = catalog && query.trim()
    ? [
      ...findMuscles(catalog, query).map((row) => ({ ...row, kind: 'muscle' as const })),
      ...searchSelectableBones(catalog, navigation, query).map((row) => ({ ...row, kind: 'bone' as const })),
    ].sort((a, b) => a.score - b.score || a.entry.label.localeCompare(b.entry.label, 'ko'))
    : [];
  const listItems: SearchListItem[] = query.trim()
    ? searchResults.reduce<SearchListItem[]>((items, result) => {
      if (result.kind === 'bone') items.push({ id: result.entry.id, label: result.entry.label, approximate: result.approximate, kind: 'bone', selection: result.selection });
      else items.push({ id: result.entry.id, label: result.entry.label, approximate: result.approximate, kind: 'muscle' });
      return items;
    }, [])
    : regionMuscles.map((concept) => ({ id: concept.id, label: nameFor(catalog!, concept.id).label, approximate: false, kind: 'muscle' as const }));
  function commitRoute(nextRoute: AtlasRouteState, replace = false) {
    const nextUrl = routeUrl(nextRoute);
    const currentUrl = `${location.pathname}${location.search}${location.hash}`;
    if (nextUrl !== currentUrl) {
      if (replace) history.replaceState(null, '', nextUrl);
      else history.pushState(null, '', nextUrl);
    }
    setRoute(nextRoute);
    setRouteNotice(null);
    setUnmappedMeshNotice(null);
    setTab('구조');
    setSelectedActionId(null);
    setDetailsOpen(true);
  }

  function chooseRegion(categoryId: string) {
    setQuery('');
    commitRoute(routeForCategory(navigation, categoryId, route.selection));
  }

  function chooseEntity(entityId: string) {
    const concept = concepts.find((candidate) => candidate.id === entityId);
    if (!concept) return;
    const conceptId = muscleConceptId(concept, entityId);
    const partId = concept.entityType === 'muscle_part' ? entityId : undefined;
    commitRoute(routeForMuscleSelection(navigation, conceptId, partId, route.regionId));
  }

  function chooseBone(selection: Extract<Selection, { kind: 'bone' }>) {
    commitRoute(routeForBoneSelection(navigation, selection));
  }

  function chooseSearchItem(item: SearchListItem) {
    if (item.kind === 'bone') chooseBone(item.selection);
    else chooseEntity(item.id);
  }


  function clearSelection() {
    commitRoute({ regionId: route.regionId, side: route.side, selection: null, legacyRoute: false });
  }

  if (error) return <main className="load-state"><h1>자료를 불러오지 못했습니다</h1><p>{error}</p><button onClick={() => location.reload()}>다시 시도</button></main>;
  if (!catalog || !routeReady) return <main className="load-state" role="status">Human Atlas를 준비하고 있습니다…</main>;

  const stageTitle = wholeView ? '전체 모형' : region?.labelKo ?? (selected ? '구조 사전' : '부위 선택');
  const stageDescription = '회전하고 확대하며 구조를 살펴보세요.';

  return <div className="study-shell">
    <a className="skip-link" href="#study-details">선택한 구조 설명으로 이동</a>
    <header className="study-header">
      <div className="header-brand-group">
        <a className="brand" href="/"><span className="brand-dot"/> HUMAN ATLAS <small>구조를 보고, 움직임을 이해하다</small></a>
        <button type="button" className="app-info-trigger" onClick={() => appInfoDialog.current?.showModal()}>앱 정보</button>
      </div>
      <label className="global-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="구조 검색" placeholder="구조 이름 · 한글, English" value={query} onChange={(event) => setQuery(event.target.value)} autoComplete="off"/>{query && <button aria-label="검색 지우기" onClick={() => setQuery('')}>×</button>}</label>
    </header>
    <dialog className="app-info-dialog" ref={appInfoDialog} aria-labelledby="app-info-title">
      <div className="app-info-content">
        <button type="button" className="app-info-close" aria-label="앱 정보 닫기" onClick={() => appInfoDialog.current?.close()}>닫기</button>
        <h2 id="app-info-title">모형·자료 정보</h2>
        <p>3D 모형 자료: BodyParts3D Release 4.0.</p>
        <p className="model-attribution">BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International</p>
        <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html" target="_blank" rel="noreferrer">이용 조건 보기 ↗</a>
      </div>
    </dialog>
    <div className="study-layout">
      <aside className="study-sidebar">
        <div className="sidebar-heading"><span className="eyebrow">EXPLORE ANATOMY</span><h1>부위 탐색</h1><p>12개 부위와 확인된 구조 연결을 살펴봅니다.</p></div>
        <label className="mobile-region-picker">부위 선택
          <select aria-label="부위 선택" value={region?.id ?? ''} onChange={(event) => event.target.value && chooseRegion(event.target.value)}>
            <option value="" disabled>부위를 선택해 주세요</option>
            {navigation.categories.map((category) => <option key={category.id} value={category.id}>{category.labelKo}</option>)}
          </select>
        </label>
        <nav className="region-grid" aria-label="12개 해부학 부위">
          {navigation.categories.map((category) => <button key={category.id} type="button" className={category.id === route.regionId ? 'is-current' : ''} aria-pressed={category.id === route.regionId} onClick={() => chooseRegion(category.id)}>{category.labelKo}</button>)}
        </nav>
        <div className="region-list-heading">
          <span className="eyebrow">{query.trim() ? 'SEARCH RESULTS' : 'STRUCTURES'}</span>
          <h2>{query.trim() ? '검색 결과' : region?.labelKo ?? '연결된 부위 없음'}</h2>
          <p className="result-count" role="status">{query.trim() ? `검색 결과 ${listItems.length}` : region ? `${listItems.length}개 연결된 근육` : '부위를 선택해 주세요'}</p>
        </div>
        <nav className="study-list region-structure-list" aria-label={query.trim() ? '검색 구조 목록' : `${region?.labelKo ?? '선택한 부위'} 구조 목록`}>
          {listItems.map((item) => {
            const itemConcept = concepts.find((concept) => concept.id === item.id);
            const baseId = muscleConceptId(itemConcept, item.id);
            const itemRegions = item.kind === 'muscle' ? categoriesForMuscleConcept(navigation, baseId)
              .map((id) => navigation.categories.find((category) => category.id === id)?.labelKo)
              .filter((value): value is string => Boolean(value)) : [];
            const itemSelected = item.kind === 'bone'
              ? route.selection?.kind === 'bone' && route.selection.conceptId === item.id
              : item.id === selectedId;
            const itemName = item.kind === 'bone' ? boneNameForLearner(item.id) : catalog && nameFor(catalog, item.id);
            return <button key={item.id} type="button" className={itemSelected ? 'selected' : ''} aria-pressed={itemSelected} onClick={() => chooseSearchItem(item)}>
              <span>{item.label}</span>
              <small>{itemName?.en || '영어 이름 확인 중'}</small>
              {query.trim() && <em>{item.kind === 'bone' ? '뼈 정보' : itemRegions.length ? itemRegions.join(' · ') : '부위 연결 준비 중'}</em>}
              {item.approximate && <em>비슷한 이름</em>}
            </button>;
          })}
          {listItems.length === 0 && <p className="quiet-note">{query.trim() ? '찾는 이름이 아직 등록되지 않았습니다. 다른 언어 이름으로도 검색해 보세요.' : '이 부위의 구조 연결은 준비 중입니다. 미확인 구조를 추정해 채우지 않았습니다.'}</p>}
        </nav>
      </aside>
      <section className="study-stage" aria-label={`${stageTitle} 학습 장면`}>
        <div className="stage-caption"><span className="eyebrow">INTERACTIVE ANATOMY</span><h2>{stageTitle}</h2><p>{stageDescription}</p></div>
        <WholeBodyViewer whole={wholeView} onWholeChange={setWholeView} region={route.regionId} selectedId={selectedId} selectedIds={route.side === 'left' ? [] : [...(selectedId ? [selectedId] : []), ...(!route.selection || route.selection.kind !== 'muscle' || route.selection.partId ? [] : parts.map(part => part.id))]} onSelect={(id, side) => {
          if (id.startsWith('HA-S-')) {
            const instance = navigation.structureInstances.find(row => row.structureId === id && row.side === side);
            if (instance) chooseBone({ kind: 'bone', conceptId: id, instanceId: instance.id });
          } else chooseEntity(id);
        }}/>

      </section>
      <details className="study-details" id="study-details" open={detailsOpen} onToggle={(event) => setDetailsOpen(event.currentTarget.open)}>
        <summary className="mobile-detail-summary">{selectedBoneName?.label ?? (selected && name ? name.label : '선택한 구조 설명')}</summary>
        <div className="study-detail-content">
          {route.selection && <button type="button" className="bone-related-muscle" onClick={clearSelection}>선택 해제</button>}
          {selectedBoneCard && selectedBoneName ? <>
            <h2>{selectedBoneName.label || '설명 정리 중'}</h2>
            <LearnerNameRows name={selectedBoneName}/>
            <div className="names-card bone-side-card"><div><span>좌우</span><strong>{selectedBoneCard.side === 'right' ? '오른쪽' : selectedBoneCard.side === 'left' ? '왼쪽' : selectedBoneCard.side === 'midline' ? '정중' : '좌우 구분 없음'}</strong></div></div>
            <section className="attachment-section bone-card-section"><h3>주요 표지</h3>
              <p className="quiet-note">표지 정보는 준비하고 있습니다.</p>
            </section>
            <section className="attachment-section bone-card-section"><h3>관련 근육</h3>
              {selectedBoneCard.relations.length > 0 ? <ul>{selectedBoneCard.relations.map((relation) => <li key={relation.muscleOrPartId}>
                <button type="button" className="bone-related-muscle" onClick={() => chooseEntity(relation.muscleOrPartId)}>{nameFor(catalog, relation.muscleOrPartId).label}</button>
                <span>{relation.roles.map((role) => role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '그 외 부착').join(' · ')}</span>
              </li>)}</ul> : <p className="quiet-note">연결된 근육 정보는 준비하고 있습니다.</p>}
            </section>
          </> : unmappedMeshNotice ? <>
            <h2>이 구조 정보는 준비하고 있습니다</h2>
            <p>선택한 구조에 연결된 설명을 준비하고 있습니다.</p>
          </> : route.selection?.kind === 'bone' ? <>
            <h2>뼈 정보 준비 중</h2><p>선택한 뼈의 이름과 설명을 준비하고 있습니다.</p>
          </> : selected && name ? <>
            <h2>{name.label}</h2>
            <LearnerNameRows name={name}/>
            <div className="movement-cta-block">
              <button type="button" className="movement-cta" disabled aria-describedby="movement-unavailable-note">움직임으로 이해하기</button>
              <p id="movement-unavailable-note" className="quiet-note">움직임 시범 자료는 준비 중입니다.</p>
            </div>
            <div className="study-tabs" role="tablist" aria-label="학습 내용">{(['구조','기능'] as TabName[]).map((entry) => <button key={entry} role="tab" id={`tab-${entry}`} aria-controls="study-tab-panel" aria-selected={tab === entry} onClick={() => setTab(entry)}>{entry}</button>)}</div>
            <section id="study-tab-panel" key={selectedId} role="tabpanel" aria-labelledby={`tab-${tab}`}>
              {tab === '구조' ? <>
                {parts.length > 0 && <div className="part-pills" aria-label="근육 부분"><button aria-pressed={selectedId === parentId} onClick={() => chooseEntity(parentId!)}>전체</button>{parts.map((part) => <button key={part.id} aria-pressed={part.id === selectedId} onClick={() => chooseEntity(part.id)}>{nameFor(catalog, part.id).label.split(' · ').at(-1)}</button>)}</div>}
                {(['origin','insertion'] as const).map((role) => <section className="attachment-section attachment-summary-block" key={role}>
                  <h3><i className={role}/>{role === 'origin' ? '기시' : '정지'}<span>{role === 'origin' ? 'ORIGIN' : 'INSERTION'}</span></h3>
                  {structureTextForLearner(selectedId!, role)
                    ? <p>{structureTextForLearner(selectedId!, role)}</p>
                    : <p className="quiet-note">설명 자료는 준비하고 있습니다.</p>}
                </section>)}
              </> : actionCard ? <div className="muscle-action-learning">
                <section className="muscle-action-summary" aria-labelledby="action-summary-title">
                  <h3 id="action-summary-title">이 근육이 하는 일</h3>
                  <p className="action-label">{actionCard.label}</p>
                  <p>{actionCard.explanation}</p>
                </section>
                <fieldset className="learner-action-picker" aria-label="작용 선택">
                  <legend>작용 선택</legend>
                  {actionOptions.length ? actionOptions.map((action) => <button key={action.id} type="button" aria-pressed={action.id === activeAction?.id} onClick={() => setSelectedActionId(action.id)}>{action.label}</button>)
                    : <p className="quiet-note">작용 정보를 준비하고 있습니다.</p>}
                </fieldset>
              </div> : <div className="upcoming"><h3>작용 정보를 준비하고 있습니다</h3></div>}
            </section>
          </> : <div className="upcoming"><h2>{routeNotice ? '주소의 구조 연결을 확인해 주세요' : '구조를 선택해 주세요'}</h2><p>{routeNotice ?? (region ? `${region.labelKo} 목록 또는 설명이 연결된 모형을 선택해 주세요.` : '검색하거나 부위를 선택해 학습할 구조를 찾을 수 있습니다.')}</p></div>}
        </div>
      </details>
    </div>
  </div>;
}
