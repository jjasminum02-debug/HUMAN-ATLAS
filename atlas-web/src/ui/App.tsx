import { useEffect, useMemo, useState } from 'react';
import { loadPilotCatalog, linkedEvidence, recordLabel, sourceForEvidence, type PilotCatalog } from '../data/catalog';
import { findMuscles, learningConcepts, nameFor, nameSources, structureFieldForLearner } from '../data/learning';
import { attachmentCrosscheckFor } from '../domain/attachmentCrosschecks';
import { GLBViewer } from '../viewer/GLBViewer';
import { sceneRevision } from '../viewer/scenePlan';
import { attachmentContextById } from '../viewer/attachmentContext';
import { boneSourceLabel, buildBoneCardData } from '../domain/boneCard';
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

type TabName = '구조' | '기능' | '평가';
type StandardReference = { uri: string; edition: string; identifier: string };
type LearnerConcept = ReturnType<typeof learningConcepts>[number];
type UnmappedMeshNotice = { meshAssetId: string; sourceName: string };
const navigation = rawNavigation as NavigationContract;

function standardReferences(value: unknown): StandardReference[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((candidate) => {
    if (typeof candidate !== 'object' || candidate === null || Array.isArray(candidate)) return [];
    const reference = candidate as Record<string, unknown>;
    if (typeof reference.uri !== 'string') return [];
    return [{
      uri: reference.uri,
      edition: typeof reference.edition === 'string' ? reference.edition : '',
      identifier: typeof reference.identifier === 'string' ? reference.identifier : '',
    }];
  });
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
  const [routeNotice, setRouteNotice] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [tab, setTab] = useState<TabName>('구조');
  const [activeAttachmentId, setActiveAttachmentId] = useState<string | null>(null);
  const [unmappedMeshNotice, setUnmappedMeshNotice] = useState<UnmappedMeshNotice | null>(null);
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
      setActiveAttachmentId(null);
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
  const standardRefs = standardReferences(selected && 'standardRefs' in selected ? selected.standardRefs : undefined);
  const parentId = selected?.entityType === 'muscle_part' && typeof selected.parentId === 'string' ? selected.parentId : selectedId;
  const parts = concepts.filter((concept) => concept.entityType === 'muscle_part' && concept.parentId === parentId);
  const owners = new Set([selectedId, ...concepts.filter((concept) => concept.parentId === selectedId).map((concept) => concept.id)]);
  const attachments = catalog ? catalog.attachments.filter((attachment) => owners.has(String(attachment.muscleOrPartId))) : [];
  const regionRows = region ? categoryMemberships(navigation, region.id) : [];
  const regionMuscles = regionRows.flatMap((row) => {
    const concept = concepts.find((candidate) => candidate.id === row.entityId);
    return concept ? [concept] : [];
  });
  const searchResults = catalog && query.trim() ? findMuscles(catalog, query) : [];
  const listItems = query.trim()
    ? searchResults.map(({ entry, approximate }) => ({ id: entry.id, label: entry.label, approximate }))
    : regionMuscles.map((concept) => ({ id: concept.id, label: nameFor(catalog!, concept.id).label, approximate: false }));
  const regionScenes = navigation.sceneManifests.filter((scene) => scene.categoryId === route.regionId);
  const activeScenes = regionScenes.filter((scene) => scene.availability !== 'unavailable' && scene.assetRefs.length > 0 &&
    (!route.side || scene.defaultView.side === route.side));
  const sceneAvailable = activeScenes.length > 0;

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
    setActiveAttachmentId(null);
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

  function chooseUnmappedMesh(mesh: UnmappedMeshNotice) {
    commitRoute({ regionId: route.regionId, side: route.side, selection: null, legacyRoute: false });
    setUnmappedMeshNotice(mesh);
  }

  function clearSelection() {
    commitRoute({ regionId: route.regionId, side: route.side, selection: null, legacyRoute: false });
  }

  if (error) return <main className="load-state"><h1>자료를 불러오지 못했습니다</h1><p>{error}</p><button onClick={() => location.reload()}>다시 시도</button></main>;
  if (!catalog || !routeReady) return <main className="load-state" role="status">Human Atlas를 준비하고 있습니다…</main>;

  const stageTitle = region?.labelKo ?? (selected ? '구조 사전' : '부위 선택');
  const selectedSideLabel = route.side === 'left' ? '왼쪽' : route.side === 'right' ? '오른쪽' : null;
  const sideScenePending = Boolean(selectedSideLabel) && regionScenes.length > 0 && activeScenes.length === 0;
  const stageDescription = sceneAvailable
    ? '현재 확보된 부위 장면입니다. 출처 연결이 확인된 근육과 뼈를 선택할 수 있습니다.'
    : sideScenePending
      ? `${selectedSideLabel} ${region?.labelKo ?? '해당 부위'} 장면은 준비 중입니다. 다른 좌우의 모형을 대신 표시하지 않습니다.`
    : region
      ? `${region.labelKo} 자료를 준비하고 있습니다. 현재 종아리 장면을 다른 부위 자료처럼 표시하지 않습니다.`
      : '아직 부위 연결이 확인되지 않은 구조입니다. 3D 장면은 표시하지 않습니다.';
  const sceneMembershipSources = new Set(regionRows.map((row) => row.entityId));

  return <div className="study-shell">
    <a className="skip-link" href="#study-details">선택한 구조 설명으로 이동</a>
    <header className="study-header">
      <a className="brand" href="/"><span className="brand-dot"/> HUMAN ATLAS <small>구조를 보고, 움직임을 이해하다</small></a>
      <label className="global-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="구조 검색" placeholder="구조 이름 · 한글, English" value={query} onChange={(event) => setQuery(event.target.value)} autoComplete="off"/>{query && <button aria-label="검색 지우기" onClick={() => setQuery('')}>×</button>}</label>
    </header>
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
            const itemRegions = categoriesForMuscleConcept(navigation, baseId)
              .map((id) => navigation.categories.find((category) => category.id === id)?.labelKo)
              .filter((value): value is string => Boolean(value));
            return <button key={item.id} type="button" className={item.id === selectedId ? 'selected' : ''} aria-pressed={item.id === selectedId} onClick={() => chooseEntity(item.id)}>
              <span>{item.label}</span>
              <small>{nameFor(catalog, item.id).en || '영어 이름 확인 중'}</small>
              {query.trim() && <em>{itemRegions.length ? itemRegions.join(' · ') : '부위 연결 준비 중'}</em>}
              {item.approximate && <em>비슷한 이름</em>}
            </button>;
          })}
          {listItems.length === 0 && <p className="quiet-note">{query.trim() ? '찾는 이름이 아직 등록되지 않았습니다. 다른 언어 이름으로도 검색해 보세요.' : '이 부위의 구조 연결은 준비 중입니다. 미확인 구조를 추정해 채우지 않았습니다.'}</p>}
        </nav>
        {region?.id === 'leg' && !query.trim() && <div className="region-source-note">
          <strong>현재 확인된 종아리 파일럿</strong>
          <span>오른쪽 종아리의 여섯 근육만 목록에 연결되어 있습니다.</span>
          <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html" target="_blank" rel="noreferrer">BodyParts3D Release 4.0 · CC BY 4.0 ↗</a>
          <small>모형 연결 출처이며, 해부학 검토·부착 위치 승인을 뜻하지 않습니다.</small>
        </div>}
      </aside>
      <section className={`study-stage ${sceneAvailable ? '' : 'is-unavailable'}`} aria-label={`${stageTitle} 학습 장면`}>
        <div className="stage-caption"><span className="eyebrow">INTERACTIVE ANATOMY</span><h2>{stageTitle}</h2><p>{stageDescription}</p></div>
        {sceneAvailable
          ? <GLBViewer key={`${route.regionId}:${route.side}:${sceneRevision(activeScenes)}`} selectedEntityId={route.selection?.kind === 'muscle' ? routeEntityId(route.selection) : null} selectedSelection={route.selection} unmappedMeshId={unmappedMeshNotice?.meshAssetId ?? null} navigation={navigation} scenes={activeScenes} activeAttachmentId={activeAttachmentId} concepts={[...concepts.map((concept) => ({ id: concept.id, entityType: concept.entityType, parentId: concept.parentId ?? null, displayLabel: nameFor(catalog, concept.id).label })), ...catalog.structures.filter((structure) => structure.kind === 'bone').map((structure) => ({ id: structure.id, entityType: 'bone', parentId: null, displayLabel: recordLabel(catalog, structure.id) }))]} attachments={catalog.attachments} claims={catalog.claims} onSelectEntity={chooseEntity} onSelectBone={chooseBone} onSelectUnmappedMesh={chooseUnmappedMesh} onClearSelection={clearSelection} onClearAttachment={() => setActiveAttachmentId(null)} studyMode/>
          : <div className="region-empty-scene" role="status">
              <span className="empty-scene-mark" aria-hidden="true">◎</span>
              <h3>{region ? `${region.labelKo} 장면은 준비 중입니다` : selected ? '이 구조의 부위 연결은 준비 중입니다' : '부위를 선택해 주세요'}</h3>
              <p>{routeNotice ?? (sideScenePending ? '선택한 좌우의 장면은 준비 중입니다.' : region && sceneMembershipSources.size === 0 ? '아직 확인된 구조 목록이 없습니다. 다른 부위 자료를 대신 보여주지 않습니다.' : '이 화면에서는 확인된 자료가 있는 장면만 표시합니다.')}</p>
            </div>}
      </section>
      <details className="study-details" id="study-details" open={detailsOpen} onToggle={(event) => setDetailsOpen(event.currentTarget.open)}>
        <summary className="mobile-detail-summary">{selected && name ? `${name.label} 설명` : '선택한 구조 설명'}</summary>
        <div className="study-detail-content">
          {selectedBoneCard ? <>
            <div className="detail-top"><span className="eyebrow">BONE STRUCTURE</span><span className="status-dot">출처 요약 · 사람 검토 전</span></div>
            <h2>{selectedBoneCard.label ?? '이 뼈의 이름은 확인 중입니다'}</h2>
            <p className="english-name"><span>뼈 표기</span> {selectedBoneCard.label ?? '이름 자료 준비 중'}</p>
            <div className="names-card bone-side-card"><div><span>좌우</span><strong>{selectedBoneCard.side === 'right' ? '오른쪽' : selectedBoneCard.side === 'left' ? '왼쪽' : selectedBoneCard.side === 'midline' ? '정중' : '좌우 구분 없음'}</strong></div></div>
            <section className="attachment-section bone-card-section"><h3>근거가 연결된 주요 표지</h3>
              {selectedBoneCard.landmarks.length > 0 ? <ul>{selectedBoneCard.landmarks.map((landmark) => <li key={landmark.id}><span>{landmark.label}</span>{landmark.sources.map((source) => <small key={source.id}>{boneSourceLabel(source.id)}</small>)}</li>)}</ul> : <p className="quiet-note">이 뼈에 연결된 주요 표지는 아직 표시할 근거가 없습니다.</p>}
            </section>
            <section className="attachment-section bone-card-section"><h3>근거가 연결된 근육</h3>
              {selectedBoneCard.relations.length > 0 ? <ul>{selectedBoneCard.relations.map((relation) => <li key={relation.muscleOrPartId}>
                <button type="button" className="bone-related-muscle" onClick={() => chooseEntity(relation.muscleOrPartId)}>{nameFor(catalog, relation.muscleOrPartId).label}</button>
                <span>{relation.roles.map((role) => role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '그 외 부착').join(' · ')}</span>
                {relation.landmarks.length > 0 && <small>{relation.landmarks.map((id) => selectedBoneCard.landmarks.find((landmark) => landmark.id === id)?.label).filter(Boolean).join(' · ')}</small>}
                {relation.sources.map((source) => <small key={source.id}>{boneSourceLabel(source.id)}</small>)}
              </li>)}</ul> : <p className="quiet-note">이 뼈와 근육을 연결하는 출처 근거가 아직 없습니다.</p>}
            </section>
            <details className="study-sources"><summary>이름과 연결의 출처</summary>
              {[...selectedBoneCard.nameSources, ...selectedBoneCard.assetSources].filter((source, index, rows) => rows.findIndex((other) => other.id === source.id) === index).map((source) => <p key={source.id}>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{boneSourceLabel(source.id)} ↗</a> : boneSourceLabel(source.id)}{source.edition && <small>{source.edition}</small>}</p>)}
              <p>표시한 이름과 부착 관계는 기존 출처 요약을 연결한 것입니다. mesh의 선택 상태나 표시가 사람 해부학 검토, 정확한 부착 위치 승인 또는 `reviewed` 상태를 뜻하지 않습니다.</p>
            </details>
          </> : unmappedMeshNotice ? <>
            <div className="detail-top"><span className="eyebrow">STRUCTURE INFORMATION</span><span className="status-dot">자료 연결 준비 중</span></div>
            <h2>이 메시의 뼈 연결은 확인되지 않았습니다</h2>
            <p>{unmappedMeshNotice.sourceName}에 대한 안정된 전체 뼈 ID와 출처 crosswalk를 확인하지 못했습니다. 이전에 선택한 근육 설명은 닫았습니다.</p>
          </> : route.selection?.kind === 'bone' ? <>
            <div className="detail-top"><span className="eyebrow">BONE STRUCTURE</span><span className="status-dot">자료 연결 준비 중</span></div>
            <h2>뼈 정보를 불러올 수 없습니다</h2><p>선택된 뼈의 이름 또는 근거 자료를 확인할 수 없습니다.</p>
          </> : selected && name ? <>
            <div className="detail-top"><span className="eyebrow">MUSCLE ATLAS</span><span className="status-dot">학습 초안</span></div>
            <h2>{name.label}</h2><p className="english-name"><span>영어명</span> {name.en || '—'}</p>
            <div className="names-card" aria-label="이름"><div><span>우리말명</span><strong>{name.koModern || '—'}</strong></div><div><span>한자어명 (한글 표기)</span><strong>{name.koTraditional || '—'}</strong></div></div>
            <div className="study-tabs" role="tablist" aria-label="학습 내용">{(['구조','기능','평가'] as TabName[]).map((entry) => <button key={entry} role="tab" id={`tab-${entry}`} aria-controls="study-tab-panel" aria-selected={tab === entry} onClick={() => setTab(entry)}>{entry}</button>)}</div>
            <section id="study-tab-panel" key={selectedId} role="tabpanel" aria-labelledby={`tab-${tab}`}>
              {tab === '구조' ? <>
                {parts.length > 0 && <div className="part-pills" aria-label="근육 부분"><button aria-pressed={selectedId === parentId} onClick={() => chooseEntity(parentId!)}>전체</button>{parts.map((part) => <button key={part.id} aria-pressed={part.id === selectedId} onClick={() => chooseEntity(part.id)}>{nameFor(catalog, part.id).label.split(' · ').at(-1)}</button>)}</div>}
                {(['origin','insertion'] as const).map((role) => <section className="attachment-section attachment-summary-block" key={role}>
                  <h3><i className={role}/>{role === 'origin' ? '기시' : '정지'}<span>{role === 'origin' ? 'ORIGIN' : 'INSERTION'}</span></h3>
                  {(() => {
                    const fieldView = structureFieldForLearner(selectedId!, role);
                    if (!fieldView) return <p className="quiet-note">이 근육의 {role === 'origin' ? '기시' : '정지'} 설명은 준비 중입니다.</p>;
                    return <>
                      {fieldView.text && <p>{fieldView.text}</p>}
                      {fieldView.note && <p className="quiet-note">{fieldView.note}</p>}
                      {fieldView.alternatives.length > 0 && <ul className="field-evidence-alternatives">{fieldView.alternatives.map((alternative, index) => <li key={`${role}-alternative-${index}`}><p>{alternative.text}</p></li>)}</ul>}
                      {fieldView.sources.length > 0 && <details className="field-evidence-sources"><summary>이 문장의 근거</summary><ul>{fieldView.sources.map((source, index) => <li key={`${source.url}-${source.locator}-${index}`}>
                        <a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a>
                        {source.edition && <small>{source.edition}</small>}
                        <small>{source.locator}</small>
                      </li>)}</ul></details>}
                    </>;
                  })()}
                  {attachmentCrosscheckFor(selectedId!, role) && <details className="attachment-crosscheck">
                    <summary>현대 연구와 비교하기</summary>
                    <p>{attachmentCrosscheckFor(selectedId!, role)!.item.comparison}</p>
                    <ul>{attachmentCrosscheckFor(selectedId!, role)!.sources.map((source) => <li key={source.id}>
                      <a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a>
                      <small>{source.citation}</small>
                      <small>{source.edition} · {source.locator}</small>
                      <small>접근: {source.accessMethod}</small>
                    </li>)}</ul>
                    <p className="quiet-note">문헌 대조와 사람 해부학 검토는 별도입니다. 이 비교는 메시 표면 좌표나 승인 상태를 만들지 않습니다.</p>
                  </details>}
                </section>)}
                {attachments.length > 0 && <details className="attachment-context-disclosure">
                  <summary>부착별 관련 뼈와 영문 근거 보기</summary>
                  {(['origin','insertion','other_attachment'] as const).filter((role) => attachments.some((attachment) => attachment.role === role)).map((role) => {
                    const roleAttachments = attachments.filter((attachment) => attachment.role === role);
                    return <section className="attachment-section" key={role}>
                      <h3><i className={role}/>{role === 'origin' ? '기시 문맥' : role === 'insertion' ? '정지 문맥' : '그 외 부착'}</h3>
                      <div className="attachment-candidates">{roleAttachments.map((attachment) => {
                        const context = attachmentContextById.get(attachment.id);
                        return <button key={attachment.id} type="button" aria-pressed={activeAttachmentId === attachment.id} aria-label={`${role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '부착'} 설명 선택`} onClick={() => setActiveAttachmentId(attachment.id)}>
                          <span>{context?.contextMeshAssetId ? '관련 뼈 강조' : '3D 위치 표시 보류'}</span>
                          <small>{context?.contextMeshAssetId ? '정확한 부착면은 미지정' : '표적 구조 3D 미확보 · 위치 표시 보류'}</small>
                        </button>;
                      })}</div>
                      <details className="attachment-source-detail">
                        <summary>영문 상세 설명과 판본 펼치기</summary>
                        {roleAttachments.map((attachment) => {
                          const claim = catalog.claims.find((item) => item.id === attachment.descriptionClaimId);
                          const value = claim?.value as { summary?: string; edition?: string } | undefined;
                          return <div className="attachment-source-item" key={attachment.id}>
                            {value?.summary && <p lang="en">{value.summary}</p>}
                            {value?.edition && <small>{value.edition}</small>}
                          </div>;
                        })}
                      </details>
                    </section>;
                  })}
                  <p className="quiet-note">부착 설명은 Gray 1918년판에 근거한 검토 전 요약입니다. 강조된 뼈 전체는 표면 검토 대상이며 정확한 부착 영역은 아직 연결되지 않았습니다.</p>
                </details>}
              </> : <div className="upcoming"><span>{tab === '기능' ? '↗' : '◎'}</span><h3>{tab} 자료를 준비하고 있습니다</h3><p>{tab === '기능' ? '관절의 움직임, 자세에 따른 역할과 안정화 작용을 연결할 예정입니다.' : '검사 목적, 시행 방법과 결과를 해석하는 순서를 연결할 예정입니다.'}</p></div>}
            </section>
            <details className="study-sources"><summary>출처와 자료 상태</summary><p>용어 출처와 Gray 1918년판의 역사적 부착 설명을 구분했습니다. 현대 연구 대조는 각 기시·정지 문장 옆에서 열 수 있으며, 직접 측정·배경 설명·미측정 범위를 구별합니다. 사람 해부학 검토와 3D 부착면 승인은 별도입니다.</p>{name.sources.map((id) => { const source = nameSources[id]; return source && <p key={id}>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a> : source.title}<small>{source.locator}</small></p>; })}{standardRefs.map((reference, index) => <p key={`standard-reference-${index}`}><a href={reference.uri} target="_blank" rel="noreferrer">FIPAT · Terminologia Anatomica, Part 2 ↗</a><small>{reference.edition}{reference.identifier ? ` · ${reference.identifier}` : ''}</small></p>)}{Array.from(new Set(attachments.flatMap((attachment) => { const claim = catalog.claims.find((item) => item.id === attachment.descriptionClaimId); return linkedEvidence(catalog, claim?.evidenceIds).map((evidence) => evidence.sourceId); }))).map((id) => { const evidence = catalog.evidence.find((item) => item.sourceId === id); const source = evidence && sourceForEvidence(catalog, evidence); return source && <p key={String(id)}><a href={String(source.urlOrLocalRef)} target="_blank" rel="noreferrer">{String(source.title)} ↗</a></p>; })}</details>
          </> : <div className="upcoming"><h2>{routeNotice ? '주소의 구조 연결을 확인해 주세요' : '구조를 선택해 주세요'}</h2><p>{routeNotice ?? (region ? `${region.labelKo}의 구조 자료는 준비 중입니다.` : '검색하거나 부위를 선택해 학습할 구조를 찾을 수 있습니다.')}</p></div>}
        </div>
      </details>
    </div>
  </div>;
}
